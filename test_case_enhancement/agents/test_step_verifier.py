"""
TestStepVerifierAgent module for validating test case steps against a live web page.
"""

from typing import List, Dict, Any, Optional

from test_case_enhancement.llm.client import LLMClient
from test_case_enhancement.core.utils import log, parse_llm_json
from test_case_enhancement.core.models import TestCase, TestCaseVerificationResult
from test_case_enhancement.llm.prompts import (
    PROMPT_STEP_CHECKER_SYSTEM,
    PROMPT_STEP_CHECKER_CHECK,
)

def format_test_cases_block(test_cases: List[TestCase]) -> str:
    """Format a list of TestCase objects into the prompt block."""
    lines = []
    for tc in test_cases:
        lines.append(f"### {tc.tc_id} — {tc.title} ({tc.tc_type} | {tc.priority})")
        lines.append(f"Preconditions: {tc.preconditions}")
        lines.append("Steps:")
        for step in tc.steps:
            lines.append(f"  {step.number}. {step.description}")
        lines.append(f"Expected Result: {tc.expected_result}")
        lines.append("")
    return "\\n".join(lines)


class TestStepVerifierAgent:
    """Agent that verifies human-written test cases against a live page DOM."""

    def __init__(self, llm: LLMClient, debug: bool = False, debug_file: str = None):
        """Initialize the __init__ method."""
        self.debug = debug
        self.debug_file = debug_file
        self.llm_call_count = 0
        
        self.checker_llm = LLMClient(
            api_key=llm.api_key,
            model_name=llm.model_name,
            system_prompt=PROMPT_STEP_CHECKER_SYSTEM,
            debug_file=debug_file,
        )

    def verify_test_cases(
        self,
        module_name: str,
        page_url: str,
        page_title: str,
        dom_context: str,
        test_cases: List[TestCase],
        screenshot_b64: str = None,
    ) -> List[TestCaseVerificationResult]:
        """Verify a list of test cases for the given page context."""
        if not test_cases:
            return []

        test_cases_block = format_test_cases_block(test_cases)

        prompt = PROMPT_STEP_CHECKER_CHECK.format(
            module_name=module_name,
            page_url=page_url,
            page_title=page_title,
            dom_context=dom_context,
            test_cases_block=test_cases_block,
        )

        try:
            if self.checker_llm.is_vision and screenshot_b64:
                response = self.checker_llm.ask_with_screenshot(
                    user_prompt=prompt,
                    screenshot_b64=screenshot_b64,
                )
            else:
                response = self.checker_llm.ask(prompt)
            
            self.llm_call_count += 1
            data = parse_llm_json(response)
        except Exception as e:
            log(f"  [TestStepVerifierAgent] LLM error: {e}", self.debug, self.debug_file)
            self.llm_call_count += 1
            return []

        results = []
        for res in data.get("results", []):
            try:
                tc_result = TestCaseVerificationResult(
                    tc_id=res.get("tc_id", "Unknown"),
                    verdict=res.get("verdict", "invalid"),
                    valid_steps=res.get("valid_steps", []),
                    invalid_steps=res.get("invalid_steps", []),
                    missing_steps=res.get("missing_steps", []),
                    precondition_issues=res.get("precondition_issues", []),
                    invalid_reason=res.get("invalid_reason", ""),
                    notes=res.get("notes", ""),
                )
                results.append(tc_result)
            except Exception as e:
                log(f"  [TestStepVerifierAgent] Error parsing result for TC: {e}", self.debug, self.debug_file)
                
        return results
