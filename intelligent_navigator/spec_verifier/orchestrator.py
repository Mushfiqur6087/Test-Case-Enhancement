"""
Traversal Orchestrator — Plan-based spec verification.

Drives a two-phase, spec-aware traversal to verify all sections of a functional
description against a live web application.

Architecture:
  1. TraversalPlannerAgent reads the full spec → generates ordered traversal plan
  2. For each step in the plan:
     a. ActionEngine navigates to the target page (goal-oriented actions)
     b. PageIdentifierAgent confirms which spec section the page matches
     c. SpecCheckerAgent verifies the page against its spec section
  3. Failed steps trigger replanning via the TraversalPlannerAgent

No URL hints, no keyword tables, no guessing. The plan is derived entirely
from the functional specification.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from intelligent_navigator.core.llm import LLMClient
from intelligent_navigator.core.logging import DebugLogger
from intelligent_navigator.core.models import (
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
from intelligent_navigator.agents.page_identifier import PageIdentifierAgent
from intelligent_navigator.agents.traversal_planner import (
    TraversalPlannerAgent,
    TraversalStep,
)
from intelligent_navigator.agents.action_engine import ActionEngine
from intelligent_navigator.spec_verifier.description_parser import DescriptionParser
from intelligent_navigator.spec_verifier.checker import SpecCheckerAgent
from intelligent_navigator.spec_verifier import report as report_module


# ---- Constants ----
_MAX_REPLAN_ATTEMPTS = 2   # max times to replan a single failed step
_ACTION_SECTION_KEYWORDS = ["logout", "reset", "sign out", "log out"]


class TraversalOrchestrator:
    """
    Orchestrates a plan-based, agentic traversal for spec verification.

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
        self.planner = TraversalPlannerAgent(
            llm_client=self._base_llm,
            debug=self.debug,
            debug_file=self.debug_file,
        )
        self.action_engine = ActionEngine(
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

        # 4. Generate traversal plan
        self._log("\n" + "=" * 40)
        self._log("GENERATING TRAVERSAL PLAN")
        self._log("=" * 40)

        credentials_info = self._format_credentials_for_planner()
        plan = self.planner.generate_plan(
            all_sections=all_sections,
            base_url=self.base_url,
            credentials_info=credentials_info,
        )
        self._log(f"\nPlan reasoning: {plan.reasoning}")
        self._log(f"Total steps: {len(plan.steps)}")
        for i, step in enumerate(plan.steps, 1):
            self._log(
                f"  {i}. [{step.phase}] {step.target_section} "
                f"({step.page_type}) — {step.how_to_reach[:80]}"
            )

        # 5. Execute the plan
        results: Dict[str, SectionVerificationResult] = {}
        section_map = {s.name: s for s in all_sections}
        current_phase = None
        logged_in = False

        for step_idx, step in enumerate(plan.steps):
            section_name = step.target_section

            # Skip if already verified
            if section_name in results:
                self._log(f"\n  [Step {step_idx+1}] '{section_name}' already verified — skipping.")
                continue

            # Handle phase transitions
            if step.phase != current_phase:
                current_phase = step.phase
                self._log(f"\n{'=' * 40}")
                self._log(f"PHASE: {current_phase.upper()}")
                self._log("=" * 40)

                if step.phase == "authenticated" and not logged_in:
                    self._do_login()
                    logged_in = True

            self._log(
                f"\n  [Step {step_idx+1}/{len(plan.steps)}] "
                f"Target: '{section_name}' ({step.page_type})"
            )
            self._log(f"    How: {step.how_to_reach}")
            if step.prerequisites:
                self._log(f"    Prerequisites: {', '.join(step.prerequisites)}")

            # Execute the step
            result = self._execute_step(
                step=step,
                section_map=section_map,
                results=results,
                all_sections=all_sections,
            )

            if result:
                results[section_name] = result
                self._log(
                    f"    Result: {result.verdict.upper()} "
                    f"({result.compliance_score}/100)"
                )
            else:
                self._log(f"    Result: Navigation failed — will try replanning.")

                # Replan the failed step
                replan_result = self._replan_and_retry(
                    step=step,
                    section_map=section_map,
                    results=results,
                    all_sections=all_sections,
                )
                if replan_result:
                    results[section_name] = replan_result
                    self._log(
                        f"    Replan result: {replan_result.verdict.upper()} "
                        f"({replan_result.compliance_score}/100)"
                    )
                else:
                    results[section_name] = self._skipped_result(
                        section_name,
                        get_current_url(self.browser_session),
                        get_current_title(self.browser_session),
                        reason="Could not navigate to this section after replanning.",
                    )

            # Progress summary
            self._log_progress(results, all_sections)

        # 6. Handle any sections not in the plan
        for section in all_sections:
            if section.name not in results:
                self._log(f"  Section '{section.name}' not reached — skipped.")
                results[section.name] = self._skipped_result(
                    section.name, self.base_url, "",
                    reason="Section was not reached during traversal.",
                )

        # 7. Build and write report
        merged = [results[s.name] for s in all_sections]
        total_llm = (
            self.llm_call_count
            + self.planner.llm_call_count
            + self.action_engine.llm_call_count
            + self.page_identifier.llm_call_count
            + self.checker.llm_call_count
        )
        report = report_module.build_report(
            project_url=self.base_url,
            functional_desc_file=self.functional_desc_file,
            section_results=merged,
            llm_calls_total=total_llm,
            extra_stats={
                "llm_calls_orchestrator": self.llm_call_count,
                "llm_calls_planner": self.planner.llm_call_count,
                "llm_calls_action_engine": self.action_engine.llm_call_count,
                "llm_calls_page_identifier": self.page_identifier.llm_call_count,
                "llm_calls_checker": self.checker.llm_call_count,
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
    # Step Execution
    # ================================================================

    def _execute_step(
        self,
        step: TraversalStep,
        section_map: Dict[str, SpecSection],
        results: Dict[str, SectionVerificationResult],
        all_sections: List[SpecSection],
    ) -> Optional[SectionVerificationResult]:
        """
        Execute a single traversal step:
          1. Check if we're already on the target page (skip nav if so)
          2. For form_gateway: use two-phase approach (verify form, then submit)
          3. For normal pages: navigate → identify → verify → run interactions
        """
        section = section_map.get(step.target_section)
        if not section:
            return None

        # ---- CHECK: Are we already on the target page? ----
        current_url = get_current_url(self.browser_session)
        current_title = get_current_title(self.browser_session)
        page_content = self._get_combined_page_content()

        unvisited = [
            section_map[n] for n in section_map
            if n not in results
        ]

        matched_section, confidence = self.page_identifier.identify(
            current_url=current_url,
            current_title=current_title,
            page_content=page_content,
            all_sections=unvisited,
        )

        if matched_section == step.target_section and confidence >= 70:
            self._log(
                f"    Already on target page '{step.target_section}' "
                f"[{confidence}%] — skipping navigation."
            )
            result = self._verify_section(
                section=section,
                current_url=current_url,
                current_title=current_title,
                page_content=page_content,
            )
            # Run post-verification interactions even when we skipped nav
            self._run_post_verify_interactions(step)
            return result

        # ---- FORM GATEWAY: Two-phase approach ----
        if step.page_type == "form_gateway":
            return self._execute_form_gateway_step(
                step=step,
                section_map=section_map,
                results=results,
                all_sections=all_sections,
            )

        # ---- NORMAL STEP: Navigate → Identify → Verify → Interact ----
        goal = self._build_goal(step, section_map, results)
        extra_context = self._build_extra_context(step)

        pre_nav_url = get_current_url(self.browser_session)
        action_result = self.action_engine.execute_goal(
            goal=goal,
            extra_context=extra_context,
        )

        if not action_result.success:
            self._log(
                f"    Navigation failed: {action_result.failure_reason[:120]}"
            )
            return None

        # Sanity check: if the URL didn't change, the LLM may have declared
        # goal_achieved prematurely (saw filled form fields, assumed the next
        # click would navigate, but didn't wait for the actual page transition).
        # Retry once so the ActionEngine can observe the true page state.
        post_nav_url = get_current_url(self.browser_session)
        if post_nav_url == pre_nav_url:
            self._log(
                f"    [Nav] URL unchanged after action — retrying navigation"
            )
            retry_result = self.action_engine.execute_goal(
                goal=goal,
                extra_context=extra_context,
            )
            if not retry_result.success:
                self._log(
                    f"    Navigation retry failed: {retry_result.failure_reason[:120]}"
                )
                return None

        # Identify the page we landed on and verify it
        result = self._identify_and_verify(
            step=step,
            section_map=section_map,
            results=results,
        )

        # ---- POST-VERIFY: Execute interactions_needed as side-effect setup ----
        # This runs AFTER verification so we can't overshoot the target page,
        # but BEFORE the next step so prerequisites (e.g., "items in cart")
        # are satisfied. The planner already specified what to do on each page.
        if result:
            self._run_post_verify_interactions(step)

        return result

    def _execute_form_gateway_step(
        self,
        step: TraversalStep,
        section_map: Dict[str, SpecSection],
        results: Dict[str, SectionVerificationResult],
        all_sections: List[SpecSection],
    ) -> Optional[SectionVerificationResult]:
        """
        Two-phase form_gateway execution:
          Phase A: Navigate to the form page, identify + verify it (before submit)
          Phase B: Fill and submit the form to proceed to the next step

        This ensures form pages (Login, Checkout Info) get verified BEFORE
        the form submission navigates us away.
        """
        section = section_map.get(step.target_section)
        if not section:
            return None

        # --- Phase A: Navigate to the form page ---
        nav_goal = self._build_goal(step, section_map, results)
        extra_context = self._build_extra_context(step)

        action_result = self.action_engine.execute_goal(
            goal=nav_goal,
            extra_context=extra_context,
        )

        if not action_result.success:
            self._log(
                f"    [FormGateway] Navigation failed: "
                f"{action_result.failure_reason[:120]}"
            )
            return None

        # --- Phase A: Verify the form page ---
        current_url = get_current_url(self.browser_session)
        current_title = get_current_title(self.browser_session)
        page_content = self._get_combined_page_content()

        self._log(
            f"    [FormGateway] Arrived at form page: "
            f"{current_title} ({current_url})"
        )

        result = self._verify_section(
            section=section,
            current_url=current_url,
            current_title=current_title,
            page_content=page_content,
        )

        # --- Phase B: Fill and submit the form to proceed ---
        if step.interactions_needed:
            self._log(
                f"    [FormGateway] Submitting form: "
                f"{step.interactions_needed[:100]}"
            )
            submit_goal = step.interactions_needed
            submit_result = self.action_engine.execute_goal(
                goal=submit_goal,
                extra_context=extra_context,
            )
            if submit_result.success:
                self._log(
                    f"    [FormGateway] Form submitted → "
                    f"{submit_result.current_title} ({submit_result.current_url})"
                )
            else:
                self._log(
                    f"    [FormGateway] Form submission failed: "
                    f"{submit_result.failure_reason[:120]}"
                )

        return result

    def _identify_and_verify(
        self,
        step: TraversalStep,
        section_map: Dict[str, SpecSection],
        results: Dict[str, SectionVerificationResult],
    ) -> Optional[SectionVerificationResult]:
        """
        After navigation, identify the current page and verify it.
        If the page matches a different unvisited section, verify that instead.
        """
        current_url = get_current_url(self.browser_session)
        current_title = get_current_title(self.browser_session)
        page_content = self._get_combined_page_content()

        unvisited = [
            section_map[n] for n in section_map
            if n not in results
        ]

        matched_section, confidence = self.page_identifier.identify(
            current_url=current_url,
            current_title=current_title,
            page_content=page_content,
            all_sections=unvisited,
        )

        # Determine which section to verify
        target_to_verify = step.target_section
        if matched_section and matched_section != step.target_section:
            self._log(
                f"    Page matched '{matched_section}' instead of "
                f"'{step.target_section}' [{confidence}%]"
            )
            if matched_section not in results:
                target_to_verify = matched_section

        if not matched_section:
            # For overlay and action types, verify in-place
            if step.page_type in ("overlay", "action"):
                target_to_verify = step.target_section
                self._log(
                    f"    No page match (expected for {step.page_type} type) — "
                    f"verifying '{target_to_verify}' in-place."
                )
            else:
                self._log(
                    f"    No spec section matched at {current_url}"
                )
                return None

        section_to_verify = section_map.get(target_to_verify)
        if not section_to_verify:
            return None

        return self._verify_section(
            section=section_to_verify,
            current_url=current_url,
            current_title=current_title,
            page_content=page_content,
        )

    def _run_post_verify_interactions(self, step: TraversalStep) -> None:
        """
        Execute a step's interactions_needed AFTER the page has been verified.

        This is the post-verification side-effect phase. It satisfies prerequisites
        for subsequent steps without any app-specific logic:
          - Verification already happened → no risk of overshooting the target page
          - Interactions run now → next step's prerequisites are met
          - The planner specified what to do on each page — we just execute it

        Examples of what this executes:
          - Product Inventory / Detail: "Click 'Add to cart' for one product"
            → satisfies "items in cart" prerequisite for Shopping Cart step
          - Navigation Menu (overlay): "Click 'All Items' or close the X button"
            → cleans up overlay state before next step

        Skipped for form_gateway steps — those use the Phase B submission instead.
        """
        if not step.interactions_needed:
            return
        if step.page_type == "form_gateway":
            return  # form_gateway uses Phase B (explicit submit)

        self._log(
            f"    [PostVerify] Executing interactions: "
            f"{step.interactions_needed[:100]}"
        )
        extra_context = self._build_extra_context(step)
        interact_result = self.action_engine.execute_goal(
            goal=step.interactions_needed,
            extra_context=extra_context,
        )
        if interact_result.success:
            self._log(
                f"    [PostVerify] Done → "
                f"{interact_result.current_title} ({interact_result.current_url})"
            )
        else:
            self._log(
                f"    [PostVerify] Failed (non-fatal): "
                f"{interact_result.failure_reason[:100]}"
            )

    def _replan_and_retry(
        self,
        step: TraversalStep,
        section_map: Dict[str, SpecSection],
        results: Dict[str, SectionVerificationResult],
        all_sections: List[SpecSection],
    ) -> Optional[SectionVerificationResult]:
        """Try to replan a failed step and execute the alternative approach."""
        for attempt in range(_MAX_REPLAN_ATTEMPTS):
            self._log(
                f"    [Replan] Attempt {attempt + 1}/{_MAX_REPLAN_ATTEMPTS}..."
            )

            current_url = get_current_url(self.browser_session)
            current_title = get_current_title(self.browser_session)
            page_content = self._get_combined_page_content()

            remaining = [
                section_map[n] for n in section_map
                if n not in results
            ]

            replan_data = self.planner.replan_step(
                failed_step=step,
                failure_reason="Navigation actions did not reach the target page.",
                current_url=current_url,
                current_title=current_title,
                page_content=page_content,
                remaining_sections=remaining,
            )

            if not replan_data or not replan_data.get("can_reach", False):
                self._log(f"    [Replan] Cannot reach '{step.target_section}'.")
                continue

            new_approach = replan_data.get("new_approach", "")
            self._log(f"    [Replan] New approach: {new_approach[:120]}")

            # Create a modified step with the new approach
            new_step = TraversalStep(
                target_section=step.target_section,
                page_type=step.page_type,
                how_to_reach=new_approach,
                prerequisites=step.prerequisites,
                interactions_needed=replan_data.get("actions_needed", ""),
                phase=step.phase,
            )

            result = self._execute_step(
                step=new_step,
                section_map=section_map,
                results=results,
                all_sections=all_sections,
            )

            if result:
                return result

            # Go back to base (or inventory) to try again from a known state
            self._log("    [Replan] Returning to base URL for next attempt...")
            self.action_engine.navigate_to_url(self.base_url)

        return None

    # ================================================================
    # Goal Building
    # ================================================================

    def _build_goal(
        self,
        step: TraversalStep,
        section_map: Dict[str, SpecSection],
        results: Dict[str, SectionVerificationResult],
    ) -> str:
        """
        Build a NAVIGATION-ONLY goal for the ActionEngine from a plan step.

        CRITICAL: The goal must ONLY be about reaching the target page.
        It must NOT include interactions_needed (like clicking Checkout,
        filling forms, or clicking Back). Those cause the ActionEngine to
        overshoot past the target page before we can verify it.
        """
        section = section_map.get(step.target_section)
        section_desc = section.raw_text[:200] if section else ""

        # ONLY navigation — no interactions on the target page
        goal = step.how_to_reach

        # Add a stop instruction so the LLM doesn't keep interacting
        goal += (
            f"\n\nIMPORTANT: STOP as soon as you arrive at a page that matches "
            f"this description: {section_desc}"
            f"\nDo NOT interact with the page after arriving. "
            f"Do NOT click any buttons or fill any forms on the destination page. "
            f"Do NOT navigate away from the destination page."
        )

        return goal

    def _build_extra_context(self, step: TraversalStep) -> str:
        """Build extra context for the ActionEngine (e.g., credentials)."""
        parts = []

        # Add credential info for login steps
        if "login" in step.how_to_reach.lower() or step.page_type == "form_gateway":
            if self.credentials:
                creds = self.credentials[0]
                parts.append(
                    f"Credentials available: username='{creds.username}', "
                    f"password='{creds.password}'"
                )

        # Add prerequisite context
        if step.prerequisites:
            parts.append(f"Prerequisites: {', '.join(step.prerequisites)}")

        return "\n".join(parts)

    # ================================================================
    # Verification
    # ================================================================

    def _verify_section(
        self,
        section: SpecSection,
        current_url: str,
        current_title: str,
        page_content: str,
    ) -> SectionVerificationResult:
        """Run SpecCheckerAgent on the current page for a section."""
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
        return result

    # ================================================================
    # Login / Logout
    # ================================================================

    def _do_login(self) -> None:
        """Log in using the first available credential set."""
        if not self.credentials:
            self._log("  No credentials — skipping login.")
            return

        creds = self.credentials[0]
        self._log(f"  Logging in as: {creds.role} ({creds.username})")

        # Navigate to base URL first (login page is often the landing page)
        self.action_engine.navigate_to_url(self.base_url)

        goal = (
            f"Fill the login form with username '{creds.username}' "
            f"and password '{creds.password}', then click the login/submit button."
        )
        extra = (
            f"The username field might have placeholder 'Username' or similar. "
            f"The password field might have placeholder 'Password'. "
            f"Look for input fields of type 'text' and 'password'."
        )

        result = self.action_engine.execute_goal(goal=goal, extra_context=extra)

        if result.success:
            self._log(f"  Login successful → {result.current_title} ({result.current_url})")
        else:
            self._log(f"  Login may have failed: {result.failure_reason}")

    def _do_logout(self) -> None:
        """Log out by opening hamburger menu and clicking Logout."""
        goal = (
            "Open the navigation menu (hamburger menu button) if it exists, "
            "then click the 'Logout' link or button."
        )
        result = self.action_engine.execute_goal(goal=goal)
        if result.success:
            self._log("  Logged out.")
        else:
            # Fallback: navigate to base URL
            self.action_engine.navigate_to_url(self.base_url)
            self._log("  Logout fallback: navigated to base URL.")

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
    # Credentials
    # ================================================================

    def _format_credentials_for_planner(self) -> str:
        """Format credentials info for the traversal planner."""
        if not self.credentials:
            return "No credentials available."

        lines = []
        for c in self.credentials:
            lines.append(f"- Role: {c.role}, Username: {c.username}, Password: {c.password}")
        return "\n".join(lines)

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

    def _log_progress(
        self,
        results: Dict[str, SectionVerificationResult],
        all_sections: List[SpecSection],
    ) -> None:
        """Log a progress summary after each step."""
        verified = [
            f"{n} ({'✅' if r.verdict == 'pass' else '⚠️' if r.verdict == 'partial' else '❌'})"
            for n, r in results.items()
        ]
        remaining = [
            s.name for s in all_sections if s.name not in results
        ]
        current_url = get_current_url(self.browser_session)
        self._log(
            f"    [Progress] {len(results)}/{len(all_sections)} verified: "
            + ", ".join(verified)
        )
        if remaining:
            self._log(
                f"    [Progress] Remaining: {', '.join(remaining)}"
            )
        self._log(f"    [Progress] Current page: {current_url}")

    def _log(self, message: str) -> None:
        log(message, debug=self.debug, debug_file=self.debug_file)


# ---- Backward-compatible alias so __main__.py doesn't need changing ----
SpecVerifier = TraversalOrchestrator
