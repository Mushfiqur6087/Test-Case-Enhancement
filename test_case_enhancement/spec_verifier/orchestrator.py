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

from test_case_enhancement.core.llm import LLMClient
from test_case_enhancement.core.logging import DebugLogger
from test_case_enhancement.core.models import (
    RoleCredentials,
    SectionVerificationResult,
    SpecSection,
    VerificationReport,
)
from test_case_enhancement.core.utils import (
    get_current_title,
    get_current_url,
    log,
    wait_for_page,
)
from test_case_enhancement.browser.controller import BrowserController
from test_case_enhancement.browser.dom_helper import DOMHelper
from test_case_enhancement.browser.selector_filter import SelectorMapFilter
from test_case_enhancement.exploration.credentials import CredentialParser
from test_case_enhancement.agents.page_identifier import PageIdentifierAgent
from test_case_enhancement.agents.traversal_planner import (
    TraversalPlannerAgent,
    TraversalStep,
)
from test_case_enhancement.agents.action_engine import ActionEngine
from test_case_enhancement.spec_verifier.description_parser import DescriptionParser
from test_case_enhancement.spec_verifier.checker import SpecCheckerAgent
from test_case_enhancement.spec_verifier import report as report_module
from test_case_enhancement.agents.tc_checker import TestCaseCheckerAgent
from test_case_enhancement.agents.tc_enricher import TestCaseEnricherAgent
from test_case_enhancement.tc_parser import parse_test_cases


# ---- Constants ----
_MAX_REPLAN_ATTEMPTS = 2   # max times to replan a single failed step
_LOW_SCORE_THRESHOLD = 50  # scores below this trigger remediation + re-verification


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
        self.test_cases_file = config.get("test_cases_file", "")

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
            base_url=self.base_url,
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
        self.tc_checker = TestCaseCheckerAgent(
            llm=self._base_llm,
            debug=self.debug,
            debug_file=self.debug_file,
        )
        self.tc_enricher = TestCaseEnricherAgent(
            llm=self._base_llm,
            debug=self.debug,
            debug_file=self.debug_file,
        )

        # ---- Spec components ----
        self.parser = DescriptionParser()
        self.credential_parser = CredentialParser(self._base_llm)
        self.credentials: List[RoleCredentials] = []
        self.test_cases: Dict[str, List[Any]] = {}

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

        # 2b. Parse test cases
        if self.test_cases_file:
            self._log(f"Loading test cases from: {self.test_cases_file}")
            self.test_cases = parse_test_cases(self.test_cases_file)
            total_tc = sum(len(tcs) for tcs in self.test_cases.values())
            self._log(f"Parsed {total_tc} test cases across {len(self.test_cases)} modules.")

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
            global_context=self.global_context,
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
                    # The plan's own form_gateway Login step should have
                    # already submitted credentials via Phase B. If so,
                    # logged_in was set below and we skip this entirely.
                    # This is only the FALLBACK for apps where the Login
                    # section is absent from the spec or wasn't planned.
                    self._ensure_authenticated()
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

                # ---- Track authentication state from the plan itself ----
                # When the plan's own Login step (a form_gateway) succeeds and
                # credentials were available, Phase B submitted them — the
                # session is now authenticated. Record this so the phase
                # transition to 'authenticated' knows NOT to call
                # _ensure_authenticated() again.
                if (
                    not logged_in
                    and step.page_type == "form_gateway"
                    and self.credentials
                    and result.navigation_success
                    and self._step_is_auth_intent(step)
                ):
                    logged_in = True
                    self._log(
                        "    [Auth] Credentials submitted via plan's form_gateway — "
                        "session is now authenticated."
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

            # ---- ADAPTIVE: Validate next step against current state ----
            # After each step, check if the NEXT planned step is still valid.
            # This catches stale prerequisites (e.g., required data missing,
            # logged out before authenticated step, etc.)
            current_result = results.get(section_name)
            next_idx = step_idx + 1
            while next_idx < len(plan.steps) and plan.steps[next_idx].target_section in results:
                next_idx += 1  # skip already-verified steps to find the real next

            if current_result and next_idx < len(plan.steps):
                next_step = plan.steps[next_idx]
                self._adapt_next_step(
                    completed_section=section_name,
                    completed_score=current_result.compliance_score,
                    next_step=next_step,
                    section_map=section_map,
                    results=results,
                )

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
        if "enriched_test_cases" in paths and paths["enriched_test_cases"]:
            self._log(f"Enriched TCs → {paths['enriched_test_cases']}")
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
        Execute a single traversal step.

        Execution flow depends on page_type, but the branching is minimal:
          - form_gateway → two-phase (verify form, then submit)
          - action       → single-shot with before/after state snapshots
          - everything else (listing, detail, overlay, summary, confirmation)
            → unified navigate → identify → verify → interact
        """
        section = section_map.get(step.target_section)
        if not section:
            return None

        # ---- CHECK: Are we already on the target page? ----
        # Only for page types that have a dedicated URL/page (not overlays or
        # in-page actions — their content exists on the parent page, so the
        # identifier would falsely match the parent).
        if self._should_check_already_here(step.page_type):
            result = self._check_already_on_target(step, section, section_map, results)
            if result is not None:
                return result

        # ---- FORM GATEWAY: Two-phase approach ----
        if step.page_type == "form_gateway":
            return self._execute_form_gateway_step(
                step=step,
                section_map=section_map,
                results=results,
                all_sections=all_sections,
            )

        # ---- Build goal with type-aware stop conditions ----
        goal = self._build_goal(step, section_map, results)
        extra_context = self._build_extra_context(step)

        # ---- ACTION: Single-shot with before/after snapshots ----
        if step.page_type == "action":
            return self._execute_action_step_with_snapshots(
                step=step,
                section=section,
                goal=goal,
                extra_context=extra_context,
            )

        # ---- UNIFIED: Navigate → Identify → Verify → Interact ----
        # Works for listing, detail, overlay, summary, confirmation.
        # The LLM handles overlay/navigation differences via _build_goal prompts.
        action_result = self.action_engine.execute_goal(
            goal=goal,
            extra_context=extra_context,
        )

        if not action_result.success:
            self._log(
                f"    Navigation failed: {action_result.failure_reason[:120]}"
            )
            return None

        # Identify the page we landed on and verify it
        result = self._identify_and_verify(
            step=step,
            section_map=section_map,
            results=results,
        )

        if result:
            result = self._try_remediate_and_reverify(result, section, step)
            self._run_post_verify_interactions(step)

        return result

    @staticmethod
    def _should_check_already_here(page_type: str) -> bool:
        """Return True if this page type supports the 'already here' optimization.

        Excluded types:
          - overlay / action — content lives on the parent page; the identifier
            would falsely match the parent before the trigger is activated.
          - form_gateway — these pages have a two-phase lifecycle (Phase A:
            navigate + verify the form, Phase B: fill + submit). Short-circuiting
            via _check_already_on_target would execute Phase A (verify) but
            completely skip Phase B (submit), leaving forms unsubmitted.
            This was the root cause of login forms being verified but never
            submitted, stranding the session on the login page.
        """
        return page_type not in ("overlay", "action", "form_gateway")

    def _check_already_on_target(
        self,
        step: TraversalStep,
        section: SpecSection,
        section_map: Dict[str, SpecSection],
        results: Dict[str, SectionVerificationResult],
    ) -> Optional[SectionVerificationResult]:
        """Check if we're already on the target page and verify if so."""
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
            result = self._try_remediate_and_reverify(result, section, step)
            self._run_post_verify_interactions(step)
            return result

        return None  # not on target — proceed with normal execution

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

        This ensures form pages (Login, Registration, Data Entry) get verified BEFORE
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

    def _execute_action_step_with_snapshots(
        self,
        step: TraversalStep,
        section: SpecSection,
        goal: str,
        extra_context: str,
    ) -> Optional[SectionVerificationResult]:
        """
        Execute an action-type step with before/after state snapshots.

        Action-type specs (Reset App State, Logout, Delete Account, etc.)
        describe STATE TRANSITIONS — what changes when the action is performed.
        A single page snapshot is insufficient for verifying transitions because
        the checker can't know what the state was *before* the action.

        This method:
          0. Ensures prerequisite observable state exists (Fix 2)
          1. Captures the full page state BEFORE the action
          2. Executes the action via ActionEngine
          3. Captures the full page state AFTER the action
          4. Builds a combined before/after context:
               - Vision models: compact URL header + before+after screenshots
               - Non-vision: full before+after text DOM dumps (unchanged)
          5. Passes both states to the checker so it can reason about the diff

        This is completely generic — works for any app, any action type.
        """
        # 0. Ensure observable state exists so before/after diff is meaningful
        self._setup_action_prerequisites(step, section)

        # 1. Capture BEFORE state (text always; screenshot for vision models)
        before_url = get_current_url(self.browser_session)
        before_title = get_current_title(self.browser_session)
        before_content = self._get_combined_page_content()
        before_screenshot_b64 = None
        if self._base_llm.is_vision:
            from test_case_enhancement.browser.screenshot import capture_screenshot_b64
            before_screenshot_b64 = capture_screenshot_b64(self.browser_session)

        self._log(
            f"    [Action] Capturing before-state: {before_title} ({before_url})"
        )

        # 2. Execute the action.
        # Action steps are typically 1–2 clicks, but some require a
        # trigger-then-click sequence, e.g.:
        #   Step 1: open hamburger menu
        #   Step 2: click 'Logout' link inside the now-visible menu
        #   Step 3: (optional) wait/confirm redirect to login
        #
        # max_steps=3 gives enough room for open-trigger + click + settle
        # while still being tight enough to prevent multi-step loops that
        # would second-guess and undo completed actions.
        action_result = self.action_engine.execute_goal(
            goal=goal,
            extra_context=extra_context,
            max_steps=3,
        )

        if not action_result.success:
            self._log(
                f"    Action failed: {action_result.failure_reason[:120]}"
            )
            return None

        self._log(
            f"    [Action] Action completed → "
            f"{action_result.current_title} ({action_result.current_url})"
        )

        # 3. Capture AFTER state
        after_url = get_current_url(self.browser_session)
        after_title = get_current_title(self.browser_session)
        after_content = self._get_combined_page_content()

        # 4. Build combined before/after context for the checker.
        # Vision models: compact URL header + two screenshots (cheaper, more
        # reliable — badge counts and page changes are visually unambiguous).
        # Non-vision models: full text dumps (only option available).
        if self._base_llm.is_vision and before_screenshot_b64:
            combined_content = (
                f"=== STATE TRANSITION ===\n"
                f"Before URL: {before_url}\n"
                f"Before Title: {before_title}\n"
                f"Action: '{step.target_section}' was executed.\n"
                f"After URL:  {after_url}\n"
                f"After Title: {after_title}\n"
                f"(See the before and after screenshots for full visual state)"
            )
        else:
            # Non-vision fallback: send full text DOM diffs
            # The checker can now reason about transitions:
            #   "badge count 2 → 0" = state cleared ✓
            #   "dashboard.html → login page" = session ended ✓
            combined_content = (
                f"=== STATE BEFORE ACTION ===\n"
                f"URL: {before_url}\n"
                f"Title: {before_title}\n"
                f"{before_content}\n\n"
                f"=== ACTION PERFORMED ===\n"
                f"The action '{step.target_section}' was executed.\n\n"
                f"=== STATE AFTER ACTION (current page) ===\n"
                f"URL: {after_url}\n"
                f"Title: {after_title}\n"
                f"{after_content}"
            )

        # 5. Verify with combined before/after context
        result = self._verify_section(
            section=section,
            current_url=after_url,
            current_title=after_title,
            page_content=combined_content,
            before_screenshot_b64=before_screenshot_b64,
        )

        self._log(
            f"    [Action] Verification: {result.verdict.upper()} "
            f"({result.compliance_score}/100)"
        )

        # Run post-verify interactions if any
        self._run_post_verify_interactions(step)

        return result

    def _setup_action_prerequisites(
        self,
        step: TraversalStep,
        section: SpecSection,
    ) -> None:
        """
        Ensure observable state exists BEFORE capturing the before-state snapshot
        for an action step.

        Action steps (Reset App State, Logout, Delete, etc.) are verified by
        comparing BEFORE vs AFTER page state. If the state the action is supposed
        to change doesn't exist yet, both snapshots will be identical — giving
        the checker nothing to diff and producing a PARTIAL score.

        This method asks the LLM: "Given this action's spec, what observable
        state must exist for the change to be verifiable?" and, if that state
        is missing from the current page, runs ActionEngine to set it up.

        Examples:
          - "Reset App State" spec says it clears the cart →
            prerequisite = at least one item in the cart (badge visible)
          - "Delete Record" spec says it removes a row →
            prerequisite = at least one record in the listing

        This is generic — driven entirely by the spec text, not hardcoded.
        """
        from test_case_enhancement.agents.prompts import PROMPT_ACTION_PREREQUISITE_CHECK
        from test_case_enhancement.core.utils import parse_llm_json

        current_url = get_current_url(self.browser_session)
        page_content = self._get_combined_page_content()

        prompt = PROMPT_ACTION_PREREQUISITE_CHECK.format(
            section_name=step.target_section,
            spec_text=section.raw_text,
            current_url=current_url,
            page_content=page_content[:4000],
        )

        try:
            response = self._base_llm.ask(prompt)
            self.llm_call_count += 1
            data = parse_llm_json(response)
        except Exception as e:
            self._log(f"    [PrereqCheck] LLM error: {e} — skipping prerequisite setup.")
            return

        setup_needed = data.get("setup_needed", False)
        setup_goal = data.get("setup_actions", "")
        reasoning = data.get("reasoning", "")

        if not setup_needed or not setup_goal:
            self._log(
                f"    [PrereqCheck] Observable state present — no setup needed. "
                f"({reasoning[:80]})"
            )
            return

        self._log(
            f"    [PrereqCheck] Setup needed before '{step.target_section}': "
            f"{setup_goal[:120]}"
        )

        setup_result = self.action_engine.execute_goal(
            goal=setup_goal,
            max_steps=3,
        )

        if setup_result.success:
            self._log(
                f"    [PrereqCheck] Setup done → "
                f"{setup_result.current_title} ({setup_result.current_url})"
            )
        else:
            self._log(
                f"    [PrereqCheck] Setup failed (non-fatal): "
                f"{setup_result.failure_reason[:100]}"
            )

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

    def _try_remediate_and_reverify(
        self,
        result: SectionVerificationResult,
        section: SpecSection,
        step: TraversalStep,
    ) -> SectionVerificationResult:
        """
        Self-correction loop: when a verification score is below the threshold,
        feed the checker's structured ``missing`` list to the ActionEngine as a
        targeted remediation goal, then re-verify once.

        Design rationale for using ``result.missing`` (not ``result.notes``):
          - ``missing`` is a List[str] — each item is a concrete, checkable thing
            e.g. "Navigation link not found", "Submit button not visible"
          - Feeding these verbatim gives the LLM maximum context to decide
            HOW to reveal them (open a menu, scroll, expand an accordion, etc.)
          - ``notes`` is a prose summary — less precise for action planning

        This is intentionally a single retry: if the page is still low-scoring
        after remediation, we accept it. Looping would risk infinite cycles.
        """
        if result.compliance_score >= _LOW_SCORE_THRESHOLD:
            return result  # score is acceptable — no remediation needed

        if not result.missing:
            return result  # nothing specific to act on

        # Build a targeted remediation goal from the structured missing list
        missing_bullets = "\n".join(f"  - {item}" for item in result.missing)
        remediation_goal = (
            f"The following items were expected on the page but could NOT be found:\n"
            f"{missing_bullets}\n\n"
            f"Take the MINIMUM actions needed to make these items visible — for example:\n"
            f"  • Open a menu or side panel (click a toggle button)\n"
            f"  • Expand an accordion or tab\n"
            f"  • Scroll to reveal hidden content\n"
            f"Do NOT navigate away from the current page. "
            f"Stop as soon as the missing items appear."
        )

        self._log(
            f"    [Remediate] Score {result.compliance_score}/100 < {_LOW_SCORE_THRESHOLD} "
            f"— {len(result.missing)} missing item(s). Attempting remediation."
        )

        remediate_result = self.action_engine.execute_goal(
            goal=remediation_goal,
            max_steps=3,  # tight budget — simple reveal actions only
        )

        if remediate_result.success:
            self._log(
                f"    [Remediate] Remediation done → "
                f"{remediate_result.current_title} ({remediate_result.current_url})"
            )
        else:
            self._log(
                f"    [Remediate] Remediation failed: "
                f"{remediate_result.failure_reason[:100]}"
            )

        # Re-verify once regardless of remediation outcome
        current_url = get_current_url(self.browser_session)
        current_title = get_current_title(self.browser_session)
        page_content = self._get_combined_page_content()

        new_result = self._verify_section(
            section=section,
            current_url=current_url,
            current_title=current_title,
            page_content=page_content,
        )

        self._log(
            f"    [Remediate] Re-verification: {new_result.compliance_score}/100 "
            f"(was {result.compliance_score}/100)"
        )

        return new_result  # always accept the second result, even if still low

    def _run_post_verify_interactions(self, step: TraversalStep) -> None:
        """
        Execute a step's interactions_needed AFTER the page has been verified.

        This is the post-verification side-effect phase. It satisfies prerequisites
        for subsequent steps without any app-specific logic:
          - Verification already happened → no risk of overshooting the target page
          - Interactions run now → next step's prerequisites are met
          - The planner specified what to do on each page — we just execute it

        Examples of what this executes:
          - Listing page: "Select an item" or "Create a record"
            → satisfies data prerequisite for a downstream detail/summary step
          - Overlay (side menu): "Close the menu" or "Click a navigation link"
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

    def _adapt_next_step(
        self,
        completed_section: str,
        completed_score: int,
        next_step: 'TraversalStep',
        section_map: Dict[str, SpecSection],
        results: Dict[str, SectionVerificationResult],
    ) -> None:
        """
        Lightweight adaptive check between steps.

        Asks the planner's step advisor whether the next planned step is
        still valid given the current page state. If not, adjusts the step's
        how_to_reach and executes any prerequisite actions.

        This is NOT full replanning — it's a quick validation that runs
        between every pair of steps to catch:
          - Stale prerequisites (required data missing but next step needs it)
          - Wrong page state (logged out but next step needs auth)
          - Navigation adjustments (current page changed unexpectedly)
        """
        current_url = get_current_url(self.browser_session)
        current_title = get_current_title(self.browser_session)
        page_content = self._get_combined_page_content()

        remaining = [
            section_map[n] for n in section_map
            if n not in results
        ]

        advice = self.planner.advise_next_step(
            completed_section=completed_section,
            completed_score=completed_score,
            current_url=current_url,
            current_title=current_title,
            page_content=page_content,
            next_step=next_step,
            remaining_sections=remaining,
            global_context=self.global_context,
        )

        if not advice:
            return  # LLM call failed — proceed with original plan

        if advice.get("next_step_valid", True):
            self._log(
                f"    [Advisor] Next step '{next_step.target_section}' "
                f"is valid — proceeding as planned."
            )
            return

        # Step is invalid — apply adjustments
        reasoning = advice.get("reasoning", "")
        self._log(
            f"    [Advisor] Next step '{next_step.target_section}' needs adjustment: "
            f"{reasoning[:120]}"
        )

        # Update how_to_reach if advisor suggests a new approach
        adjusted = advice.get("adjusted_how_to_reach", "")
        if adjusted:
            next_step.how_to_reach = adjusted
            self._log(f"    [Advisor] Adjusted how_to_reach: {adjusted[:120]}")

        # Execute prerequisite actions if needed
        prereq = advice.get("prerequisite_actions", "")
        if prereq:
            self._log(f"    [Advisor] Running prerequisite: {prereq[:120]}")
            self.action_engine.execute_goal(
                goal=prereq,
                max_steps=3,  # tight budget for prereq setup
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
                page_content=page_content,
                remaining_sections=remaining,
                global_context=self.global_context,
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

            # Go back to base URL to try again from a known state
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

        CRITICAL: The goal must ONLY be about reaching the target page or
        performing the target action. It must NOT include interactions_needed
        (like submitting forms, clicking navigation links, or clicking Back). Those cause
        the ActionEngine to overshoot past the target page before we can verify it.

        Stop-condition logic is TYPE-AWARE because different page types have
        fundamentally different definitions of "done":
          - navigation types  → URL/content changes to match the destination page
          - overlay type      → content appears ON the current page (no URL change)
          - action type       → a single click completes the action in-place (no URL change)
        Sending the wrong stop condition causes the LLM to loop (it performs the
        action but keeps waiting for a page transition that will never come).
        """
        section = section_map.get(step.target_section)
        section_desc = section.raw_text[:200] if section else ""

        goal = step.how_to_reach

        if step.page_type == "action":
            # Actions complete with a single click. Some stay on the same page
            # (Reset App State), some navigate (Logout). Don't assume either.
            goal += (
                f"\n\nThis is an ACTION — perform it by clicking the relevant "
                f"element, then immediately set goal_achieved=true. "
                f"Do NOT click the same element multiple times. "
                f"Do NOT wait for any specific page transition."
            )

        elif step.page_type == "overlay":
            # Overlays (hamburger menu, modals) reveal content on the current page.
            # No URL change — done when the overlay content becomes visible.
            goal += (
                f"\n\nThis opens an OVERLAY on the current page — the URL will "
                f"NOT change. Signal goal_achieved=true as soon as the overlay "
                f"content is visible in the DOM. "
                f"Expected overlay content: {section_desc}"
            )

        else:
            # All navigation types (listing, detail, summary, confirmation,
            # form_gateway) involve an actual page transition.
            goal += (
                f"\n\nIMPORTANT: STOP as soon as you arrive at a page that matches "
                f"this description: {section_desc}"
                f"\nDo NOT interact with the page after arriving. "
                f"Do NOT click any buttons or fill any forms on the destination page. "
                f"Do NOT navigate away from the destination page."
            )

        return goal

    # Keywords that signal a step is an authentication/login form.
    # Used to narrow credential injection to only relevant form_gateway steps.
    _AUTH_INTENT_KEYWORDS = {
        "login", "log in", "log-in", "sign in", "sign-in",
        "signin", "authenticate", "authentication", "credentials",
    }

    def _step_is_auth_intent(self, step: "TraversalStep") -> bool:
        """Return True if this step is an authentication/login step.

        Checks the target_section name and how_to_reach text against a set
        of auth-intent keywords. This determines whether credentials should
        be injected into the ActionEngine prompt and whether a successful
        form_gateway execution counts as 'logged in'.
        """
        haystack = (
            step.target_section.lower() + " " + step.how_to_reach.lower()
        )
        return any(kw in haystack for kw in self._AUTH_INTENT_KEYWORDS)

    def _build_extra_context(self, step: "TraversalStep") -> str:
        """Build extra context for the ActionEngine (e.g., credentials).

        Credentials are injected ONLY for authentication-intent steps
        (login, sign-in, authenticate) to avoid leaking them into unrelated
        forms such as registration, data-entry, or payment fields.
        """
        parts = []

        # Inject credentials only when the step is an auth/login step
        if self._step_is_auth_intent(step) and self.credentials:
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
        before_screenshot_b64: Optional[str] = None,
    ) -> SectionVerificationResult:
        """Run SpecCheckerAgent on the current page for a section.

        Parameters
        ----------
        before_screenshot_b64 : Optional base64 PNG of the BEFORE state.
            When provided (action steps, vision model), both the before and
            after screenshots are passed to the checker so it can diff them
            visually for state-transition verification.
        """
        screenshot_b64 = None
        if self._base_llm.is_vision:
            from test_case_enhancement.browser.screenshot import capture_screenshot_b64
            screenshot_b64 = capture_screenshot_b64(self.browser_session)

        result = self.checker.check(
            section=section,
            page_title=current_title,
            page_url=current_url,
            selector_map_string=page_content,
            actual_url=current_url,
            actual_title=current_title,
            screenshot_b64=screenshot_b64,
            before_screenshot_b64=before_screenshot_b64,
        )
        result.navigation_success = True

        # ---- TEST CASE VERIFICATION ----
        if getattr(self, "test_cases_file", None) and section.name in getattr(self, "test_cases", {}):
            tcs = self.test_cases[section.name]
            self._log(f"    [TestCaseChecker] Verifying {len(tcs)} test cases for '{section.name}'...")
            tc_results = self.tc_checker.verify_test_cases(
                module_name=section.name,
                page_url=current_url,
                page_title=current_title,
                dom_context=page_content,
                test_cases=tcs,
                screenshot_b64=screenshot_b64,
            )
            result.test_case_results = tc_results
            self._log(f"    [TestCaseChecker] Done. ({len(tc_results)} results)")

            # ---- TEST CASE ENRICHMENT ----
            mock_data = getattr(self, "mock_data_text", "")
            self._log(f"    [TestCaseEnricher] Enriching and repairing {len(tcs)} test cases...")
            enriched_results = self.tc_enricher.enrich_test_cases(
                module_name=section.name,
                base_url=self.base_url,
                mock_data=mock_data,
                test_cases=tcs,
                verification_results=tc_results,
            )
            result.enriched_test_cases = enriched_results
            self._log(f"    [TestCaseEnricher] Done. ({len(enriched_results)} enriched TCs)")

        return result

    # ================================================================
    # Login / Logout
    # ================================================================

    def _ensure_authenticated(self) -> None:
        """Fallback authentication — used ONLY when the plan has no form_gateway
        Login step (or that step failed) and a phase transition to 'authenticated'
        is encountered.

        Unlike the old _do_login(), this method:
          - Does NOT assume the login page is at base_url
          - Does NOT hard-navigate away from the current page first
          - Gives the ActionEngine a dynamic goal to FIND the login page from
            wherever we currently are (nav link, header button, etc.)
          - Falls back to base_url only as a last resort

        This makes authentication work for apps where login is at /auth/login,
        /signin, or an OAuth provider — any app, any URL structure.
        """
        if not self.credentials:
            self._log("  [Auth] No credentials — cannot authenticate.")
            return

        creds = self.credentials[0]
        self._log(f"  [Auth] Dynamic login fallback as: {creds.role} ({creds.username})")

        goal = (
            f"Find and navigate to the login or sign-in page. "
            f"Look for links or buttons labeled 'Login', 'Sign In', 'Log In', "
            f"'Get Started', or similar in the page header or navigation. "
            f"Once on the login page, fill the authentication form with "
            f"username '{creds.username}' and password '{creds.password}', "
            f"then submit the form and confirm you are redirected away from the login page."
        )
        extra = (
            f"Credentials: username='{creds.username}', password='{creds.password}'. "
            f"The username field may have placeholder 'Username', 'Email', or 'User ID'. "
            f"The password field may have placeholder 'Password' or 'Secret'."
        )

        result = self.action_engine.execute_goal(goal=goal, extra_context=extra, max_steps=6)

        if result.success:
            self._log(
                f"  [Auth] Login successful → {result.current_title} ({result.current_url})"
            )
            return

        # ---- Last resort: try from base_url ----
        self._log(
            f"  [Auth] Could not find login from current page — "
            f"trying base URL {self.base_url} as fallback."
        )
        self.action_engine.navigate_to_url(self.base_url)
        result = self.action_engine.execute_goal(goal=goal, extra_context=extra, max_steps=4)

        if result.success:
            self._log(
                f"  [Auth] Fallback login successful → {result.current_url}"
            )
        else:
            self._log(
                f"  [Auth] Fallback login also failed: {result.failure_reason[:120]}"
            )

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
        sections, skipped_sections = self.parser.parse(text, **kwargs)

        self.global_context = "\n\n".join(
            f"### {s.name}\n{s.raw_text}" for s in skipped_sections
        )
        return sections

    def _load_credentials(self) -> None:
        self._log("\n--- Credentials ---")
        self.mock_data_text = ""
        if self.credentials_file and os.path.isfile(self.credentials_file):
            with open(self.credentials_file, "r", encoding="utf-8") as f:
                self.mock_data_text = f.read()

            self.credentials = self.credential_parser.parse_credentials(
                self.credentials_file
            )
            self.llm_call_count += 1
            self.credentials = self.credential_parser.deduplicate_roles(self.credentials)
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
