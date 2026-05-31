"""
Test Case Verifier Orchestrator.

Drives the test-case-driven verification loop (one navigation per module):

  1. Parse the test cases file into TestCase objects
  2. Group TCs by module
  3. Start a browser session
  4. (Optional) Log in if credentials are provided
  5. For each module group:
       a. Navigate to the module's target URL
       b. Detect 404 → mark all TCs in module as "invalid"
       c. Capture full page DOM + body text + optional screenshot
       d. Run StepCheckerAgent for all TCs in this module (ONE LLM call)
  6. Build and write the TestCaseReport (JSON + Markdown)
"""

import os
from typing import Any, Dict, List, Optional

from intelligent_navigator.core.llm import LLMClient
from intelligent_navigator.core.logging import DebugLogger
from intelligent_navigator.core.models import (
    NavigatorCommand,
    RoleCredentials,
    TestCase,
    TestCaseVerificationResult,
    TestCaseReport,
)
from intelligent_navigator.core.utils import log
from intelligent_navigator.agents.navigator import Navigator
from intelligent_navigator.browser.controller import BrowserController
from intelligent_navigator.browser.dom_helper import DOMHelper
from intelligent_navigator.browser.screenshot import capture_screenshot_b64
from intelligent_navigator.browser.selector_filter import SelectorMapFilter
from intelligent_navigator.exploration.credentials import CredentialParser
from intelligent_navigator.test_case_verifier.test_case_parser import TestCaseParser
from intelligent_navigator.test_case_verifier.step_checker import StepCheckerAgent
from intelligent_navigator.test_case_verifier.report import TestCaseReportBuilder


class TestCaseVerifier:
    """
    Orchestrates the full test case verification run.

    Parameters
    ----------
    config : dict with keys:
        base_url          : str
        test_case_file    : str
        credentials_file  : str   (optional)
        output_dir        : str
        api_key           : str
        model_name        : str
        debug             : bool
    """

    def __init__(self, config: Dict[str, Any]):
        self.base_url = config["base_url"].rstrip("/")
        self.test_case_file = config["test_case_file"]
        self.credentials_file = config.get("credentials_file", "")
        self.output_dir = config.get("output_dir", "output")
        self.debug = config.get("debug", False)

        # ---- Tracking ----
        self.debug_logger = DebugLogger()
        self.debug_file: Optional[str] = None
        if self.debug:
            self.debug_file = self.debug_logger.get_debug_file_path("tc_verification")
            print(f"\n[DEBUG] Log file: {self.debug_file}\n")

        # ---- LLM clients ----
        api_key = config["api_key"]
        model_name = config.get("model_name", "openai/gpt-4o-mini")

        self._base_llm = LLMClient(
            api_key=api_key,
            model_name=model_name,
            debug_file=self.debug_file,
        )

        # ---- Browser ----
        self.browser_controller = BrowserController(llm_client=self._base_llm)
        self.browser_session = self.browser_controller.browser_context

        # ---- DOM helpers ----
        self.dom_helper = DOMHelper(self.browser_session)
        self.selector_filter = SelectorMapFilter()

        # ---- Agents ----
        self.navigator = Navigator(
            llm_client=self._base_llm,
            browser_session=self.browser_session,
            browser_controller=self.browser_controller,
            selector_filter=self.selector_filter,
            debug=self.debug,
            debug_file=self.debug_file,
        )

        self.checker = StepCheckerAgent(
            llm_client=self._base_llm,
            debug=self.debug,
            debug_file=self.debug_file,
        )

        # ---- Parser / Report builder ----
        self.parser = TestCaseParser()
        self.report_builder = TestCaseReportBuilder()

    # ================================================================
    # Public API
    # ================================================================

    def run(self) -> TestCaseReport:
        """Execute the full test case verification run."""
        print("=" * 60)
        print("TEST CASE VERIFIER STARTED")
        print(f"Base URL  : {self.base_url}")
        print(f"TC file   : {self.test_case_file}")
        print("=" * 60)

        # --- Parse test cases ---
        with open(self.test_case_file, encoding="utf-8") as f:
            markdown_text = f.read()

        all_tcs: List[TestCase] = self.parser.parse(markdown_text)
        grouped = self.parser.group_by_module(all_tcs)

        modules = list(grouped.keys())
        print(f"Parsed {len(all_tcs)} test cases across {len(modules)} modules: {', '.join(modules)}\n")

        # --- Login ---
        credentials = self._load_credentials()
        if credentials:
            self._login(credentials[0])

        # --- Verify each module ---
        all_results: List[TestCaseVerificationResult] = []
        for module_name, tcs in grouped.items():
            results = self._verify_module(module_name, tcs)
            all_results.extend(results)

        # --- Build report ---
        total_llm_calls = self.checker.llm_call_count
        report = self.report_builder.build(
            project_url=self.base_url,
            test_case_file=self.test_case_file,
            results=all_results,
            llm_calls=total_llm_calls,
        )

        self.report_builder.write(report, self.output_dir)

        # --- Summary ---
        print("\n" + "=" * 60)
        print("TEST CASE VERIFICATION COMPLETE")
        print(f"Total    : {report.total}")
        print(f"  ✅ Valid          : {report.valid_count}")
        print(f"  ⚠️  Invalid Steps : {report.invalid_steps_count}")
        print(f"  ❌ Invalid        : {report.invalid_count}")
        print(f"  ⏭️  Skipped       : {report.skipped_count}")
        print(f"Accuracy : {report.overall_accuracy:.0f}%")
        print(f"LLM calls: {report.llm_calls_total}")
        print(f"\nOutputs:")
        print(f"  JSON   → {os.path.join(self.output_dir, 'test_case_report.json')}")
        print(f"  Report → {os.path.join(self.output_dir, 'test_case_report.md')}")
        print("=" * 60)

        return report

    # ================================================================
    # Module Verification (Option B)
    # ================================================================

    def _verify_module(
        self,
        module_name: str,
        tcs: List[TestCase],
    ) -> List[TestCaseVerificationResult]:
        """Navigate once to the module page, then check ALL TCs together.

        Precondition accuracy is verified by the LLM against the actual page —
        no TC is skipped based on precondition content.
        """
        print(f"\n--- Module: {module_name} ({len(tcs)} TCs) ---")

        target_url = self._build_target_url(tcs[0].target_url)

        # Navigate to the module page (once for all TCs in this module)
        print(f"  URL hint: {target_url}")
        nav_cmd = NavigatorCommand(
            command_type="explore_page",
            target_url=target_url,
            target_label=module_name,
        )
        nav_result = self.navigator.navigate(nav_cmd)
        current_url   = nav_result.current_url   or target_url
        current_title = nav_result.current_title or ""
        print(f"  Landed on: {current_title} ({current_url})")

        # Capture DOM + body text
        _, selector_map_string = self.dom_helper.scroll_and_capture()
        page_body_text = self._get_page_body_text()

        # Capture screenshot for vision-capable models
        screenshot_b64 = None
        if self._base_llm.is_vision:
            screenshot_b64 = capture_screenshot_b64(self.browser_session)

        # 404 detection — mark all TCs invalid if page doesn't exist
        body_lower = page_body_text.lower()
        is_error_page = (
            len(page_body_text) < 200
            and any(kw in body_lower for kw in ("404", "not found", "page not found", "oops"))
        )
        if is_error_page:
            print(f"  ⚠️  404 error page — all TCs in '{module_name}' marked invalid")
            return [
                TestCaseVerificationResult(
                    tc_id=tc.tc_id,
                    module=tc.module,
                    title=tc.title,
                    tc_type=tc.tc_type,
                    priority=tc.priority,
                    verdict="invalid",
                    invalid_reason=f"404/error page at {current_url}. "
                                   f"URL hint '{tcs[0].target_url}' may be wrong.",
                    actual_url=current_url,
                    actual_title=current_title,
                    navigation_success=False,
                )
                for tc in tcs
            ]

        # Build combined DOM context
        dom_context = selector_map_string
        if page_body_text:
            dom_context = (
                f"=== PAGE BODY TEXT ===\n{page_body_text}\n\n"
                f"=== DOM ELEMENTS ===\n{selector_map_string}"
            )

        # Debug: log captured content
        if self.debug and self.debug_file:
            with open(self.debug_file, "a", encoding="utf-8") as _f:
                _f.write(f"\n{'='*60}\n")
                _f.write(f"MODULE: {module_name} | URL: {current_url}\n")
                _f.write(f"{'='*60}\n")
                _f.write(f"\n--- PAGE BODY TEXT ({len(page_body_text)} chars) ---\n")
                _f.write(page_body_text or "(empty)")
                _f.write(f"\n\n--- DOM ({len(selector_map_string)} chars, first 2000) ---\n")
                _f.write(selector_map_string[:2000] or "(empty)")
                _f.write("\n")

        # Run the step checker — ONE LLM call for all TCs in this module
        return self.checker.check_module(
            module_name=module_name,
            page_url=current_url,
            page_title=current_title,
            dom_context=dom_context,
            test_cases=tcs,
            actual_url=current_url,
            actual_title=current_title,
            screenshot_b64=screenshot_b64,
        )

    # ================================================================
    # Login / Credentials
    # ================================================================

    def _load_credentials(self) -> List[RoleCredentials]:
        if not self.credentials_file or not os.path.isfile(self.credentials_file):
            return []
        print(f"\n--- Startup ---")
        print(f"Parsing credentials...")
        try:
            cred_parser = CredentialParser(self._base_llm)
            creds = cred_parser.parse_credentials(self.credentials_file)
            creds = cred_parser.deduplicate_roles(creds)
            creds = cred_parser.sort_by_privilege(creds)
            print(f"  Found {len(creds)} role(s): {', '.join(c.role for c in creds)}")
            return creds
        except Exception as e:
            print(f"  Warning: could not parse credentials: {e}")
            return []

    def _login(self, cred: RoleCredentials) -> None:
        login_url = self._build_target_url("/login")
        cmd = NavigatorCommand(
            command_type="login",
            target_url=login_url,
            credentials=cred,
        )
        result = self.navigator.navigate(cmd)
        if result.success:
            print(f"  Logged in as: {cred.role}")
        else:
            print(f"  Warning: login may have failed — {result.failure_reason}")

    # ================================================================
    # Helpers
    # ================================================================

    def _build_target_url(self, path: str) -> str:
        base = self.base_url.rstrip("/")
        path = path if path.startswith("/") else f"/{path}"
        return f"{base}{path}"

    def _get_page_body_text(self) -> str:
        """Extract visible plain text from the page body."""
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

    def _log(self, msg: str) -> None:
        """Write a message to both stdout and debug log."""
        print(msg)
        log(msg, self.debug, self.debug_file)
