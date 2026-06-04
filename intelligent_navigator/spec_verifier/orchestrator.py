"""
Traversal Orchestrator (replaces the old SpecVerifier).

Drives a two-phase agentic traversal to verify all sections of a functional
description against a live web application — with zero hardcoded URLs.

Phase 1 — Public traversal
  Starting from base_url, the orchestrator uses:
    - LinkDiscoveryAgent  → find which page links match unvisited spec sections
    - Navigator           → navigate to those pages
    - PageIdentifierAgent → confirm which spec section the landed page is
    - SpecCheckerAgent    → verify the page against its spec section
  It repeats until no more public-accessible spec sections are reachable.

Phase 2 — Per-role authenticated traversal
  For each set of credentials, the orchestrator logs in and repeats the
  same BFS loop for sections that were not reachable as a public user.
  Each role gets a completely fresh traversal from base_url.

No URL hints, no keyword tables, no guessing.
"""

import os
from collections import deque
from datetime import datetime
from typing import Any, Deque, Dict, List, Optional, Set

from intelligent_navigator.core.llm import LLMClient
from intelligent_navigator.core.logging import DebugLogger
from intelligent_navigator.core.models import (
    NavigatorCommand,
    RoleCredentials,
    SectionVerificationResult,
    SpecSection,
    VerificationReport,
)
from intelligent_navigator.core.utils import (
    get_current_title,
    get_current_url,
    log,
    wait_for_page,
)
from intelligent_navigator.browser.controller import BrowserController
from intelligent_navigator.browser.dom_helper import DOMHelper
from intelligent_navigator.browser.selector_filter import SelectorMapFilter
from intelligent_navigator.exploration.credentials import CredentialParser
from intelligent_navigator.agents.navigator import Navigator
from intelligent_navigator.agents.page_identifier import PageIdentifierAgent
from intelligent_navigator.agents.link_discovery import LinkDiscoveryAgent, CandidateLink
from intelligent_navigator.spec_verifier.description_parser import DescriptionParser
from intelligent_navigator.spec_verifier.checker import SpecCheckerAgent
from intelligent_navigator.spec_verifier import report as report_module

# ---- Traversal constants ----
_MAX_FRONTIER_RETRIES = 2    # times to go back to base_url when frontier is empty
_MAX_VISITED_URLS = 200      # circuit-breaker to prevent infinite loops


class TraversalOrchestrator:
    """
    Orchestrates a zero-hardcoding, agentic traversal-based spec verification.

    Parameters
    ----------
    config : dict
        - base_url             (str) : target application URL
        - functional_desc_file (str) : path to the markdown spec file
        - credentials_file     (str) : path to credentials markdown (optional)
        - output_dir           (str) : where to write reports
        - api_key              (str) : LLM API key
        - model_name           (str) : LiteLLM model string
        - debug                (bool): enable debug logging
        - skip_sections        (list): section names to skip (optional)
    """

    def __init__(self, config: Dict[str, Any]):
        self.base_url = config["base_url"]
        self.functional_desc_file = config.get("functional_desc_file", "")
        self.credentials_file = config.get("credentials_file", "")
        self.output_dir = config.get("output_dir", "output")
        self.debug = config.get("debug", False)
        self.skip_sections = config.get("skip_sections", None)

        # ---- Debug logging ----
        self.debug_logger = DebugLogger()
        self.debug_file: Optional[str] = None
        if self.debug:
            self.debug_file = self.debug_logger.get_debug_file_path("traversal")
            print(f"\n[DEBUG] Log file: {self.debug_file}\n")

        # ---- LLM ----
        api_key = config["api_key"]
        model_name = config.get("model_name", "openai/gpt-4o-mini")
        self._base_llm = LLMClient(
            api_key=api_key,
            model_name=model_name,
            system_prompt="",
            debug_file=self.debug_file,
        )

        # ---- Browser ----
        self.browser_controller = BrowserController(llm_client=self._base_llm)
        self.browser_session = self.browser_controller.browser_context
        self.dom_helper = DOMHelper(self.browser_session)
        self.selector_filter = SelectorMapFilter()

        # ---- Agents ----
        self.navigator = Navigator(
            llm_client=self._base_llm,
            browser_controller=self.browser_controller,
            browser_session=self.browser_session,
            debug=self.debug,
            debug_file=self.debug_file,
            selector_filter=self.selector_filter,
        )
        self.page_identifier = PageIdentifierAgent(
            llm_client=self._base_llm,
            debug=self.debug,
            debug_file=self.debug_file,
        )
        self.link_discovery = LinkDiscoveryAgent(
            llm_client=self._base_llm,
            browser_controller=self.browser_controller,
            browser_session=self.browser_session,
            dom_helper=self.dom_helper,
            debug=self.debug,
            debug_file=self.debug_file,
        )
        self.checker = SpecCheckerAgent(
            llm_client=self._base_llm,
            debug=self.debug,
            debug_file=self.debug_file,
        )

        # ---- Spec components ----
        self.parser = DescriptionParser()
        self.credential_parser = CredentialParser(self._base_llm)
        self.credentials: List[RoleCredentials] = []

        # ---- LLM call tracking ----
        self.llm_call_count = 0

    # ================================================================
    # Public API
    # ================================================================

    def run(self) -> VerificationReport:
        """Main entry point. Returns a VerificationReport."""
        self._log("=" * 60)
        self._log("TRAVERSAL ORCHESTRATOR STARTED")
        self._log(f"Base URL : {self.base_url}")
        self._log(f"Spec file: {self.functional_desc_file}")
        self._log("=" * 60)

        # 1. Parse spec → sections
        all_sections = self._load_sections()
        if not all_sections:
            self._log("ERROR: No sections found in functional description.")
            return self._empty_report()

        self._log(
            f"Parsed {len(all_sections)} sections: "
            + ", ".join(s.name for s in all_sections)
        )

        # 2. Parse credentials
        self._load_credentials()

        # 3. Navigate to base URL
        self.browser_controller.execute_command("navigate_to", self.base_url)
        wait_for_page(self.browser_session)

        # 4. Phase 1 — Public traversal
        self._log("\n" + "=" * 40)
        self._log("PHASE 1 — PUBLIC TRAVERSAL")
        self._log("=" * 40)

        public_results: Dict[str, SectionVerificationResult] = {}
        self._run_traversal_loop(
            pending=list(all_sections),
            all_sections=all_sections,
            results=public_results,
            auth_state="public",
            role_label="public",
        )

        # 5. Phase 2 — Per-role authenticated traversal
        role_results: Dict[str, Dict[str, SectionVerificationResult]] = {
            "public": public_results
        }

        for creds in self.credentials:
            self._log("\n" + "=" * 40)
            self._log(f"PHASE 2 — AUTHENTICATED TRAVERSAL (role: {creds.role})")
            self._log("=" * 40)

            # Navigate back to base, log in fresh for this role
            self.browser_controller.execute_command("navigate_to", self.base_url)
            wait_for_page(self.browser_session)
            self._do_login(creds)

            auth_results: Dict[str, SectionVerificationResult] = {}
            self._run_traversal_loop(
                pending=list(all_sections),
                all_sections=all_sections,
                results=auth_results,
                auth_state="logged_in",
                role_label=creds.role,
            )
            role_results[creds.role] = auth_results

            self._do_logout()

        # 6. Merge results: prefer authenticated results over public for sections
        #    that were skipped or failed as public
        merged = self._merge_results(all_sections, role_results)

        # 7. Build and write report
        total_llm = (
            self.llm_call_count
            + self.navigator.llm_call_count
            + self.page_identifier.llm_call_count
            + self.link_discovery.llm_call_count
            + self.checker.llm_call_count
        )
        report = report_module.build_report(
            project_url=self.base_url,
            functional_desc_file=self.functional_desc_file,
            section_results=merged,
            llm_calls_total=total_llm,
            extra_stats={
                "llm_calls_orchestrator": self.llm_call_count,
                "llm_calls_navigator": self.navigator.llm_call_count,
                "llm_calls_page_identifier": self.page_identifier.llm_call_count,
                "llm_calls_link_discovery": self.link_discovery.llm_call_count,
                "llm_calls_checker": self.checker.llm_call_count,
                "roles_verified": list(role_results.keys()),
            },
        )
        paths = report_module.write_report(report, self.output_dir)

        self._log("=" * 60)
        self._log("VERIFICATION COMPLETE")
        self._log(
            f"Sections: {report.sections_checked} | "
            f"Pass: {report.passed} | Partial: {report.partial} | "
            f"Fail: {report.failed} | Skipped: {report.skipped}"
        )
        self._log(f"Overall score: {report.overall_score:.0f}/100")
        self._log(f"JSON   → {paths['json']}")
        self._log(f"Report → {paths['markdown']}")
        self._log(f"LLM calls: {total_llm}")
        self._log("=" * 60)

        return report

    # ================================================================
    # Core BFS Traversal Loop
    # ================================================================

    def _run_traversal_loop(
        self,
        pending: List[SpecSection],
        all_sections: List[SpecSection],
        results: Dict[str, SectionVerificationResult],
        auth_state: str,
        role_label: str,
    ) -> None:
        """
        BFS-based traversal loop.

        Maintains a frontier (queue of CandidateLink) populated by
        LinkDiscoveryAgent. Pops candidates by confidence, navigates,
        identifies, verifies, then re-runs discovery on the new page.
        Falls back to base_url when frontier is empty.
        """
        pending_names: Set[str] = {s.name for s in pending}
        pending_map: Dict[str, SpecSection] = {s.name: s for s in pending}
        frontier: Deque[CandidateLink] = deque()
        visited_urls: Set[str] = set()
        empty_retries = 0

        # Seed: run discovery from the current page (base_url landing)
        current_url = get_current_url(self.browser_session)
        current_title = get_current_title(self.browser_session)

        # First check if the landing page itself matches a section
        self._identify_and_verify_current_page(
            current_url, current_title, pending_names, pending_map,
            results, all_sections,
        )

        # Discover links from landing page
        unvisited = [pending_map[n] for n in pending_names if n not in results]
        self._extend_frontier(frontier, current_url, current_title, unvisited)
        visited_urls.add(current_url)

        while pending_names - set(results.keys()):
            # Sort frontier by confidence (highest first)
            sorted_frontier = sorted(frontier, key=lambda c: c.confidence, reverse=True)
            frontier = deque(sorted_frontier)

            if not frontier:
                empty_retries += 1
                if empty_retries > _MAX_FRONTIER_RETRIES:
                    self._log(
                        f"  [Traversal] Frontier empty after {_MAX_FRONTIER_RETRIES} "
                        f"retries. Marking remaining sections as skipped."
                    )
                    break

                self._log(
                    f"  [Traversal] Frontier empty (retry {empty_retries}/"
                    f"{_MAX_FRONTIER_RETRIES}). Returning to base URL..."
                )
                self.browser_controller.execute_command("navigate_to", self.base_url)
                wait_for_page(self.browser_session)
                current_url = get_current_url(self.browser_session)
                current_title = get_current_title(self.browser_session)

                unvisited = [pending_map[n] for n in pending_names if n not in results]
                self._extend_frontier(frontier, current_url, current_title, unvisited)
                continue

            # Pop next candidate
            candidate = frontier.popleft()

            # Skip if section already verified
            if candidate.section in results:
                continue

            # Skip if URL already visited
            candidate_url = candidate.href
            if candidate_url in visited_urls:
                continue

            if len(visited_urls) >= _MAX_VISITED_URLS:
                self._log("  [Traversal] Visited URL limit reached — stopping.")
                break

            self._log(
                f"\n  [Traversal] → '{candidate.section}' via "
                f"[{candidate.link_text}]({candidate.href}) [{candidate.confidence}%]"
            )

            # Navigate using the Navigator agent (click-based if needed)
            nav_success = self._navigate_to(candidate.href, candidate.section)
            current_url = get_current_url(self.browser_session)
            current_title = get_current_title(self.browser_session)
            visited_urls.add(current_url)

            if not nav_success:
                self._log(f"  [Traversal] Navigation failed for '{candidate.section}'.")
                results[candidate.section] = self._skipped_result(
                    candidate.section, current_url, current_title,
                    reason=f"Navigation to {candidate.href} failed.",
                )
                continue

            # Identify the page
            self._identify_and_verify_current_page(
                current_url, current_title, pending_names, pending_map,
                results, all_sections,
            )

            # Discover links from this new page
            unvisited = [pending_map[n] for n in pending_names if n not in results]
            if unvisited:
                self._extend_frontier(frontier, current_url, current_title, unvisited)

        # Mark any still-pending sections as skipped
        for name in pending_names:
            if name not in results:
                self._log(f"  [Traversal] Section '{name}' unreachable — skipped.")
                results[name] = self._skipped_result(
                    name, self.base_url, "",
                    reason="Section not reachable via traversal.",
                )

    # ================================================================
    # Identify + Verify Current Page
    # ================================================================

    def _identify_and_verify_current_page(
        self,
        current_url: str,
        current_title: str,
        pending_names: Set[str],
        pending_map: Dict[str, SpecSection],
        results: Dict[str, SectionVerificationResult],
        all_sections: List[SpecSection],
    ) -> None:
        """
        Run PageIdentifierAgent on the current page.
        If a pending section is matched, run SpecCheckerAgent and store result.
        """
        # Capture page content
        page_content = self._get_combined_page_content()

        matched_section, confidence = self.page_identifier.identify(
            current_url=current_url,
            current_title=current_title,
            page_content=page_content,
            all_sections=all_sections,
        )

        if not matched_section:
            self._log(
                f"  [Traversal] No spec match for '{current_title}' ({current_url})"
            )
            return

        if matched_section not in pending_names:
            self._log(
                f"  [Traversal] '{matched_section}' already visited — skipping verify."
            )
            return

        self._log(
            f"  [Traversal] ✓ Matched '{matched_section}' [{confidence}%] "
            f"→ running spec check..."
        )

        section = pending_map[matched_section]

        # Optional screenshot for vision-capable models
        screenshot_b64 = None
        if self._base_llm.is_vision:
            from intelligent_navigator.browser.screenshot import capture_screenshot_b64
            screenshot_b64 = capture_screenshot_b64(self.browser_session)

        result = self.checker.check(
            section=section,
            page_title=current_title,
            page_url=current_url,
            selector_map_string=page_content,
            actual_url=current_url,
            actual_title=current_title,
            screenshot_b64=screenshot_b64,
        )
        result.navigation_success = True
        results[matched_section] = result

    # ================================================================
    # Frontier Management
    # ================================================================

    def _extend_frontier(
        self,
        frontier: Deque[CandidateLink],
        current_url: str,
        current_title: str,
        unvisited_sections: List[SpecSection],
    ) -> None:
        """Run LinkDiscoveryAgent and add candidates to the frontier."""
        candidates = self.link_discovery.discover(
            current_url=current_url,
            current_title=current_title,
            unvisited_sections=unvisited_sections,
        )
        # Only add if section not already in frontier
        frontier_sections = {c.section for c in frontier}
        for c in candidates:
            if c.section not in frontier_sections:
                frontier.append(c)

    # ================================================================
    # Navigation Helpers
    # ================================================================

    def _navigate_to(self, url: str, label: str) -> bool:
        command = NavigatorCommand(
            command_type="explore_page",
            target_url=url,
            target_label=label,
            reasoning=f"Navigate to verify spec section: {label}",
        )
        result = self.navigator.navigate(command)
        return result.success

    def _do_login(self, creds: RoleCredentials) -> None:
        login_url = self._build_url("/login")
        command = NavigatorCommand(
            command_type="login",
            target_url=login_url,
            target_label="Login",
            credentials=creds,
        )
        result = self.navigator.navigate(command)
        if result.success:
            self._log(f"  Logged in as: {creds.role}")
        else:
            self._log(f"  Login failed: {result.failure_reason}")

    def _do_logout(self) -> None:
        command = NavigatorCommand(
            command_type="logout",
            target_url=self._build_url("/logout"),
            target_label="Logout",
        )
        self.navigator.navigate(command)
        self._log("  Logged out.")

    def _build_url(self, path: str) -> str:
        base = self.base_url.rstrip("/")
        path = path if path.startswith("/") else f"/{path}"
        return f"{base}{path}"

    # ================================================================
    # Page Content Capture
    # ================================================================

    def _get_combined_page_content(self) -> str:
        """
        Combine visible page body text + DOM selector map into a single
        string for use by PageIdentifierAgent and SpecCheckerAgent.
        """
        body_text = self._get_page_body_text()
        _, selector_map_string = self.dom_helper.scroll_and_capture()

        if body_text and selector_map_string:
            return (
                f"=== VISIBLE PAGE TEXT ===\n{body_text}\n\n"
                f"=== DOM ELEMENTS ===\n{selector_map_string}"
            )
        return body_text or selector_map_string or ""

    def _get_page_body_text(self) -> str:
        """Extract visible plain text from the page body (max 4000 chars)."""
        try:
            page = self.browser_session.get_current_page()
            if page is None:
                return ""
            text = page.evaluate("""
                () => {
                    const clone = document.body.cloneNode(true);
                    clone.querySelectorAll(
                        'script, style, [aria-hidden="true"], noscript'
                    ).forEach(el => el.remove());
                    return (clone.innerText || clone.textContent || '')
                        .replace(/\\n{3,}/g, '\\n\\n')
                        .trim();
                }
            """)
            if len(text) > 4000:
                text = text[:4000] + "\n... (truncated)"
            return text
        except Exception:
            return ""

    # ================================================================
    # Result Merging (public + per-role)
    # ================================================================

    def _merge_results(
        self,
        all_sections: List[SpecSection],
        role_results: Dict[str, Dict[str, SectionVerificationResult]],
    ) -> List[SectionVerificationResult]:
        """
        Merge per-role results into a single list.
        Prefer non-skipped, higher-scoring results over public-phase results.
        """
        merged: Dict[str, SectionVerificationResult] = {}

        # Start with public results as baseline
        for name, result in role_results.get("public", {}).items():
            merged[name] = result

        # Override with authenticated results if they are better
        for role, results in role_results.items():
            if role == "public":
                continue
            for name, result in results.items():
                existing = merged.get(name)
                if existing is None:
                    merged[name] = result
                elif (
                    existing.verdict == "skipped"
                    or result.compliance_score > existing.compliance_score
                ):
                    merged[name] = result

        # Ensure every section has an entry (fill in any gaps as skipped)
        for section in all_sections:
            if section.name not in merged:
                merged[section.name] = self._skipped_result(
                    section.name, self.base_url, "",
                    reason="Section was not reached during traversal.",
                )

        return [merged[s.name] for s in all_sections]

    # ================================================================
    # Startup
    # ================================================================

    def _load_sections(self) -> List[SpecSection]:
        if not self.functional_desc_file:
            self._log("ERROR: --functional-desc is required.")
            return []
        if not os.path.isfile(self.functional_desc_file):
            self._log(f"ERROR: File not found: {self.functional_desc_file}")
            return []
        with open(self.functional_desc_file, "r", encoding="utf-8") as f:
            text = f.read()
        kwargs = {}
        if self.skip_sections is not None:
            kwargs["skip_sections"] = self.skip_sections
        return self.parser.parse(text, **kwargs)

    def _load_credentials(self) -> None:
        self._log("\n--- Credentials ---")
        if self.credentials_file and os.path.isfile(self.credentials_file):
            self.credentials = self.credential_parser.parse_credentials(
                self.credentials_file
            )
            self.llm_call_count += 1
            self.credentials = self.credential_parser.deduplicate_roles(self.credentials)
            self.credentials = self.credential_parser.sort_by_privilege(self.credentials)
            self._log(
                f"  Found {len(self.credentials)} role(s): "
                + ", ".join(c.role for c in self.credentials)
            )
        else:
            self._log("  No credentials file — verifying as public user only.")

    # ================================================================
    # Helpers
    # ================================================================

    def _skipped_result(
        self,
        section_name: str,
        url: str,
        title: str,
        reason: str = "",
    ) -> SectionVerificationResult:
        return SectionVerificationResult(
            section_name=section_name,
            actual_url=url,
            actual_title=title,
            verdict="skipped",
            compliance_score=0,
            notes=reason,
            navigation_success=False,
            navigation_failure_reason=reason,
        )

    def _empty_report(self) -> VerificationReport:
        return VerificationReport(
            project_url=self.base_url,
            functional_desc_file=self.functional_desc_file,
            captured_at=datetime.now().isoformat(),
            sections_checked=0,
            passed=0,
            partial=0,
            failed=0,
            skipped=0,
            overall_score=0.0,
        )

    def _log(self, message: str) -> None:
        log(message, debug=self.debug, debug_file=self.debug_file)


# ---- Backward-compatible alias so __main__.py doesn't need changing ----
SpecVerifier = TraversalOrchestrator
