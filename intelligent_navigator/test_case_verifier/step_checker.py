"""
Step Checker Agent.

Given a module's DOM snapshot and a list of TestCase objects for that module,
asks an LLM to verify each test case's steps against the live page and returns
a list of TestCaseVerificationResult objects.

Option B: ONE LLM call per module (not per test case), checking all TCs together.
"""

from typing import List

from intelligent_navigator.core.llm import LLMClient
from intelligent_navigator.core.models import TestCase, TestCaseVerificationResult
from intelligent_navigator.core.utils import log, parse_llm_json
from intelligent_navigator.test_case_verifier.prompts import (
    PROMPT_STEP_CHECKER_SYSTEM,
    PROMPT_STEP_CHECKER_CHECK,
    format_test_cases_block,
)

_MAX_DOM_CHARS = 12_000


class StepCheckerAgent:
    """
    Verifies test case steps against a live page DOM — one LLM call per module.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        debug: bool = False,
        debug_file: str = None,
    ):
        self.debug = debug
        self.debug_file = debug_file
        self.llm_call_count = 0

        self.checker_llm = LLMClient(
            api_key=llm_client.api_key,
            model_name=llm_client.model_name,
            system_prompt=PROMPT_STEP_CHECKER_SYSTEM,
            debug_file=debug_file,
        )

    def check_module(
        self,
        module_name: str,
        page_url: str,
        page_title: str,
        dom_context: str,
        test_cases: List[TestCase],
        actual_url: str = "",
        actual_title: str = "",
        screenshot_b64: str = None,
    ) -> List[TestCaseVerificationResult]:
        """
        Run step verification for ALL test cases in a module in one LLM call.
        Attaches a screenshot if the model supports vision.
        """
        if not test_cases:
            return []

        log(
            f"  [Checker] Checking {len(test_cases)} TCs for module '{module_name}' against {page_url}"
            + (" [+screenshot]" if screenshot_b64 and self.checker_llm.is_vision else ""),
            self.debug, self.debug_file,
        )

        truncated_dom = dom_context[:_MAX_DOM_CHARS]
        if len(dom_context) > _MAX_DOM_CHARS:
            truncated_dom += "\n... (truncated)"

        prompt = PROMPT_STEP_CHECKER_CHECK.format(
            module_name=module_name,
            page_url=page_url,
            page_title=page_title,
            dom_context=truncated_dom or "(empty page)",
            test_cases_block=format_test_cases_block(test_cases),
        )

        try:
            if screenshot_b64 and self.checker_llm.is_vision:
                response = self.checker_llm.ask_with_screenshot(prompt, screenshot_b64)
            else:
                response = self.checker_llm.ask(prompt)
            self.llm_call_count += 1
            data = parse_llm_json(response)
        except Exception as e:
            log(
                f"  [Checker] LLM error for module '{module_name}': {e}",
                self.debug, self.debug_file,
            )
            self.llm_call_count += 1
            return [
                self._error_result(tc, actual_url, actual_title, f"LLM error: {e}")
                for tc in test_cases
            ]

        raw_results = data.get("results", [])
        # Build a lookup by TC ID so we can match safely even if order changes
        result_map = {r.get("tc_id", ""): r for r in raw_results if isinstance(r, dict)}

        results: List[TestCaseVerificationResult] = []
        for tc in test_cases:
            r = result_map.get(tc.tc_id)
            if r is None:
                # LLM didn't return a result for this TC — mark invalid
                results.append(self._error_result(
                    tc, actual_url, actual_title,
                    "LLM did not return a result for this test case."
                ))
                continue

            raw_verdict = r.get("verdict", "invalid")
            verdict = raw_verdict if raw_verdict in (
                "valid", "invalid_steps", "invalid", "skipped"
            ) else "invalid"

            results.append(TestCaseVerificationResult(
                tc_id=tc.tc_id,
                module=tc.module,
                title=tc.title,
                tc_type=tc.tc_type,
                priority=tc.priority,
                verdict=verdict,
                valid_steps=r.get("valid_steps", []),
                invalid_steps=r.get("invalid_steps", []),
                missing_steps=r.get("missing_steps", []),
                precondition_issues=r.get("precondition_issues", []),
                invalid_reason=r.get("invalid_reason", ""),
                notes=r.get("notes", ""),
                actual_url=actual_url or page_url,
                actual_title=actual_title or page_title,
                navigation_success=True,
            ))

            _icon = {
                "valid": "✅", "invalid_steps": "⚠️ ",
                "invalid": "❌", "skipped": "⏭️ ",
            }.get(verdict, "❓")
            log(
                f"    {_icon} {tc.tc_id}: {verdict}",
                self.debug, self.debug_file,
            )

        return results

    def _error_result(
        self,
        tc: TestCase,
        actual_url: str,
        actual_title: str,
        reason: str,
    ) -> TestCaseVerificationResult:
        return TestCaseVerificationResult(
            tc_id=tc.tc_id,
            module=tc.module,
            title=tc.title,
            tc_type=tc.tc_type,
            priority=tc.priority,
            verdict="invalid",
            invalid_reason=reason,
            notes=reason,
            actual_url=actual_url,
            actual_title=actual_title,
            navigation_success=False,
        )
