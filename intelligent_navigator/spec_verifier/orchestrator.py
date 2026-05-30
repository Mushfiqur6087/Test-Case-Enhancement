"""
Spec Verifier Orchestrator.

Drives the description-driven compliance verification loop:

  1. Parse the functional description into SpecSections
  2. Start a browser session
  3. (Optional) Log in if credentials are provided
  4. For each SpecSection:
       a. Use the Navigator to navigate to the section's inferred URL
       b. Capture the full page DOM via DOMHelper
       c. Run the SpecCheckerAgent → get a SectionVerificationResult
  5. Build and write the VerificationReport (JSON + Markdown)
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

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
from intelligent_navigator.spec_verifier.description_parser import DescriptionParser
from intelligent_navigator.spec_verifier.checker import SpecCheckerAgent
from intelligent_navigator.spec_verifier import report as report_module


class SpecVerifier:
    """
    Orchestrates a description-driven spec verification run.

    Parameters
    ----------
    config : dict
        Same keys as the Orchestrator config, plus:
          - ``functional_desc_file`` (str): path to the markdown spec file
          - ``skip_sections`` (list[str]): section names to skip (optional)
    """

    def __init__(self, config: Dict[str, Any]):
        # ---- Config ----
        self.base_url = config["base_url"]
        self.functional_desc_file = config.get("functional_desc_file", "")
        self.credentials_file = config.get("credentials_file", "")
        self.output_dir = config.get("output_dir", "output")
        self.debug = config.get("debug", False)
        self.skip_sections = config.get("skip_sections", None)  # None → use parser defaults

        # ---- Tracking ----
        self.llm_call_count = 0          # orchestrator-level LLM calls
        self.debug_logger = DebugLogger()
        self.debug_file: Optional[str] = None
        if self.debug:
            self.debug_file = self.debug_logger.get_debug_file_path("verification")
            print(f"\n[DEBUG] Log file: {self.debug_file}\n")

        # ---- LLM clients ----
        api_key = config["api_key"]
        model_name = config.get("model_name", "gpt-4o-mini")

        self._base_llm = LLMClient(
            api_key=api_key,
            model_name=model_name,
            system_prompt="",
            debug_file=self.debug_file,
        )

        # ---- Browser ----
        self.browser_controller = BrowserController(llm_client=self._base_llm)
        self.browser_session = self.browser_controller.browser_context

        # ---- DOM helpers ----
        self.dom_helper = DOMHelper(self.browser_session)
        self.selector_filter = SelectorMapFilter()

        # ---- Credential parser ----
        self.credential_parser = CredentialParser(self._base_llm)
        self.credentials: List[RoleCredentials] = []
        self.current_role = "public"

        # ---- Navigator (reused from existing system) ----
        self.navigator = Navigator(
            llm_client=self._base_llm,
            browser_controller=self.browser_controller,
            browser_session=self.browser_session,
            debug=self.debug,
            debug_file=self.debug_file,
            selector_filter=self.selector_filter,
        )

        # ---- Spec components ----
        self.parser = DescriptionParser()
        self.checker = SpecCheckerAgent(
            llm_client=self._base_llm,
            debug=self.debug,
            debug_file=self.debug_file,
        )

    # ================================================================
    # Public API
    # ================================================================

    def run(self) -> VerificationReport:
        """Main entry point. Returns a VerificationReport."""
        self._log("=" * 60)
        self._log("SPEC VERIFIER STARTED")
        self._log(f"Base URL : {self.base_url}")
        self._log(f"Spec file: {self.functional_desc_file}")
        self._log("=" * 60)

        # 1. Parse description → sections
        sections = self._load_sections()
        if not sections:
            self._log("ERROR: No sections found in the functional description.")
            return self._empty_report()

        self._log(f"Parsed {len(sections)} sections: {', '.join(s.name for s in sections)}")

        # 2. Parse credentials
        self._startup()

        # 3. Navigate to base URL to start
        self.browser_controller.execute_command("navigate_to", self.base_url)
        wait_for_page(self.browser_session)

        # 4. Log in if any section requires auth
        auth_sections = [s for s in sections if s.requires_auth]
        if auth_sections and self.credentials:
            self._do_login(self.credentials[0])

        # 5. Verify each section
        section_results: List[SectionVerificationResult] = []
        for section in sections:
            result = self._verify_section(section)
            section_results.append(result)

        # 6. Build and write report
        total_llm = (
            self.llm_call_count
            + self.navigator.llm_call_count
            + self.checker.llm_call_count
        )
        report = report_module.build_report(
            project_url=self.base_url,
            functional_desc_file=self.functional_desc_file,
            section_results=section_results,
            llm_calls_total=total_llm,
            extra_stats={
                "llm_calls_orchestrator": self.llm_call_count,
                "llm_calls_navigator": self.navigator.llm_call_count,
                "llm_calls_checker": self.checker.llm_call_count,
            },
        )
        paths = report_module.write_report(report, self.output_dir)

        self._log("=" * 60)
        self._log("VERIFICATION COMPLETE")
        self._log(f"Sections: {report.sections_checked} | "
                  f"Pass: {report.passed} | Partial: {report.partial} | "
                  f"Fail: {report.failed} | Skipped: {report.skipped}")
        self._log(f"Overall score: {report.overall_score:.0f}/100")
        self._log(f"JSON   → {paths['json']}")
        self._log(f"Report → {paths['markdown']}")
        self._log(f"LLM calls used: {total_llm}")
        self._log("=" * 60)

        return report

    # ================================================================
    # Startup
    # ================================================================

    def _startup(self) -> None:
        """Parse credentials if a credentials file was provided."""
        self._log("\n--- Startup ---")
        if self.credentials_file and os.path.isfile(self.credentials_file):
            self._log("Parsing credentials...")
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
            self._log("  No credentials file provided — verifying as public user only.")

    # ================================================================
    # Section Loading
    # ================================================================

    def _load_sections(self) -> List[SpecSection]:
        """Read and parse the functional description file."""
        if not self.functional_desc_file:
            self._log("ERROR: --functional-desc is required in verify mode.")
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

    # ================================================================
    # Per-Section Verification
    # ================================================================

    def _verify_section(self, section: SpecSection) -> SectionVerificationResult:
        """Navigate to a section's page and run the spec check."""
        self._log(f"\n--- Section: {section.name} ---")
        self._log(f"  URL hint : {section.url_hint}")
        self._log(f"  Auth req : {section.requires_auth}")

        # Build the target URL from the hint
        target_url = self._build_target_url(section.url_hint)

        # Handle auth state transitions
        if section.requires_auth and self.current_role == "public" and self.credentials:
            self._log("  Section requires auth — logging in...")
            self._do_login(self.credentials[0])

        # Navigate to the section's page
        nav_result = self._navigate_to(target_url, section.name)

        current_url = get_current_url(self.browser_session, fallback=target_url)
        current_title = get_current_title(self.browser_session)

        if not nav_result:
            self._log(f"  Navigation failed for section '{section.name}'")
            return SectionVerificationResult(
                section_name=section.name,
                url_hint=section.url_hint,
                actual_url=current_url,
                actual_title=current_title,
                verdict="skipped",
                compliance_score=0,
                notes="Navigation to this page failed — section skipped.",
                navigation_success=False,
                navigation_failure_reason=f"Could not reach {target_url}",
            )

        self._log(f"  Landed on: {current_title} ({current_url})")

        # Capture the full DOM
        selector_map_json, selector_map_string = self.dom_helper.scroll_and_capture()
        page_body_text = self._get_page_body_text()

        # ---- 404 / error-page detection ----
        # If the page body is short and contains error keywords, the URL hint
        # was wrong and we landed on an error page — skip this section.
        body_lower = page_body_text.lower()
        is_error_page = (
            len(page_body_text) < 200
            and any(kw in body_lower for kw in ("404", "not found", "page not found", "oops"))
        )
        if is_error_page:
            self._log(f"  ⚠️  404/error page detected at {current_url} — section skipped.")
            self._log(f"     Body text: {page_body_text[:100]!r}")
            return SectionVerificationResult(
                section_name=section.name,
                url_hint=section.url_hint,
                actual_url=current_url,
                actual_title=current_title,
                verdict="skipped",
                compliance_score=0,
                notes=(
                    f"Navigation landed on a 404/error page at {current_url}. "
                    f"The URL hint '{section.url_hint}' may be incorrect for this application. "
                    f"Page body: {page_body_text[:100]!r}"
                ),
                navigation_success=False,
                navigation_failure_reason=f"404 error page at {current_url}",
            )

        # Log the captured content (debug)
        if self.debug and self.debug_file:
            with open(self.debug_file, "a", encoding="utf-8") as _f:
                _f.write(f"\n{'='*60}\n")
                _f.write(f"SECTION: {section.name} | URL: {current_url}\n")
                _f.write(f"{'='*60}\n")
                _f.write(f"\n--- PAGE BODY TEXT ({len(page_body_text)} chars) ---\n")
                _f.write(page_body_text or "(empty)")
                _f.write(f"\n\n--- DOM SELECTOR MAP ({len(selector_map_string)} chars, showing first 3000) ---\n")
                _f.write(selector_map_string[:3000] or "(empty)")
                _f.write("\n")

        # Build the combined DOM context for the checker
        dom_context = selector_map_string
        if page_body_text:
            dom_context = (
                f"=== PAGE BODY TEXT (visible text content) ===\n"
                f"{page_body_text}\n\n"
                f"=== DOM ELEMENTS (interactive + structural) ===\n"
                f"{selector_map_string}"
            )

        # Run the spec checker
        result = self.checker.check(
            section=section,
            page_title=current_title,
            page_url=current_url,
            selector_map_string=dom_context,
            actual_url=current_url,
            actual_title=current_title,
        )
        result.navigation_success = True
        return result

    # ================================================================
    # Navigation Helpers
    # ================================================================

    def _navigate_to(self, url: str, label: str) -> bool:
        """
        Navigate to `url` using the Navigator agent (tries direct URL first,
        then falls back to LLM-guided navigation).

        Returns True on success.
        """
        command = NavigatorCommand(
            command_type="explore_page",
            target_url=url,
            target_label=label,
            reasoning=f"Navigate to verify spec section: {label}",
        )
        nav_result = self.navigator.navigate(command)
        return nav_result.success

    def _do_login(self, creds: RoleCredentials) -> None:
        """Log in using the given credentials."""
        login_url = self._build_target_url("/login")
        command = NavigatorCommand(
            command_type="login",
            target_url=login_url,
            target_label="Login",
            credentials=creds,
        )
        nav_result = self.navigator.navigate(command)
        if nav_result.success:
            self.current_role = creds.role
            self._log(f"  Logged in as: {creds.role}")
        else:
            self._log(f"  Login failed: {nav_result.failure_reason}")

    def _build_target_url(self, path: str) -> str:
        """Combine base_url and a path fragment into a full URL."""
        base = self.base_url.rstrip("/")
        path = path if path.startswith("/") else f"/{path}"
        return f"{base}{path}"

    def _get_page_body_text(self) -> str:
        """
        Extract the visible plain text of the page body via JavaScript.
        Strips scripts, styles, and aria-hidden elements so only what the
        user actually sees is included.
        Returns a truncated string (max 4000 chars) for the LLM context.
        """
        try:
            page = self.browser_session.get_current_page()
            if page is None:
                return ""
            text = page.evaluate("""
                () => {
                    // Remove script/style/hidden elements
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
    # Fallback report
    # ================================================================

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

    # ================================================================
    # Logging
    # ================================================================

    def _log(self, message: str) -> None:
        log(message, debug=self.debug, debug_file=self.debug_file)
