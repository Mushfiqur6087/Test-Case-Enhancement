"""
TestCaseEnricherAgent module for enriching and repairing test cases using mock data and DOM verification results.
"""

from typing import List, Dict, Any
import json

from test_case_enhancement.core.models import TestCase, TestCaseVerificationResult, EnrichedTestCase
from test_case_enhancement.agents.prompts import PROMPT_ENRICHER_SYSTEM, PROMPT_ENRICHER_CHECK
from test_case_enhancement.core.llm import LLMClient
from test_case_enhancement.core.utils import log, parse_llm_json

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
    return "\n".join(lines)

def format_verification_results(results: List[TestCaseVerificationResult]) -> str:
    """Format verification results for this module into a readable block."""
    if not results:
        return "(No verification results available — steps not previously checked)"

    lines = []
    for r in results:
        lines.append(f"### {r.tc_id} — verdict: {r.verdict}")
        if r.invalid_steps:
            lines.append("Invalid steps (element NOT in DOM):")
            for s in r.invalid_steps:
                lines.append(f"  - {s}")
        if r.notes:
            lines.append(f"Notes: {r.notes}")
        lines.append("")
    return "\n".join(lines)


class TestCaseEnricherAgent:
    """Agent that enriches and repairs test cases based on mock data and checker results."""

    def __init__(self, llm: LLMClient, debug: bool = False, debug_file: str = None):
        self.debug = debug
        self.debug_file = debug_file
        self.llm_call_count = 0
        
        self.enricher_llm = LLMClient(
            api_key=llm.api_key,
            model_name=llm.model_name,
            system_prompt=PROMPT_ENRICHER_SYSTEM,
            debug_file=debug_file,
        )

    def enrich_test_cases(
        self,
        module_name: str,
        base_url: str,
        mock_data: str,
        test_cases: List[TestCase],
        verification_results: List[TestCaseVerificationResult],
    ) -> List[EnrichedTestCase]:
        """Enrich a list of test cases for the given module."""
        if not test_cases:
            return []

        test_cases_block = format_test_cases_block(test_cases)
        verification_block = format_verification_results(verification_results)

        prompt = PROMPT_ENRICHER_CHECK.format(
            module_name=module_name,
            base_url=base_url,
            mock_data=mock_data,
            test_cases_block=test_cases_block,
            verification_results=verification_block,
        )

        try:
            response = self.enricher_llm.ask(prompt)
            self.llm_call_count += 1
            data = parse_llm_json(response)
        except Exception as e:
            log(f"  [TestCaseEnricherAgent] LLM error: {e}", self.debug, self.debug_file)
            self.llm_call_count += 1
            return []

        enriched_results = []
        for res in data.get("results", []):
            try:
                enriched_tc = EnrichedTestCase(
                    tc_id=res.get("tc_id", "Unknown"),
                    module=res.get("module", module_name),
                    title=res.get("title", ""),
                    type=res.get("type", ""),
                    priority=res.get("priority", ""),
                    direct_link=res.get("direct_link", ""),
                    requires_auth=res.get("requires_auth", False),
                    preconditions=res.get("preconditions", ""),
                    steps=res.get("steps", []),
                    expected_result=res.get("expected_result", ""),
                    test_data=res.get("test_data", {}),
                    verdict=res.get("verdict", "not_verified"),
                    issues=res.get("issues", []),
                    dropped=res.get("dropped", False),
                    drop_reason=res.get("drop_reason", ""),
                    notes=res.get("notes", ""),
                )
                enriched_results.append(enriched_tc)
            except Exception as e:
                log(f"  [TestCaseEnricherAgent] Error parsing enriched result for TC: {e}", self.debug, self.debug_file)
                
        return enriched_results
