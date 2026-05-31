"""
Test Case Enricher Orchestrator.

Standalone pipeline (no browser needed):

  1. Parse the test cases file into TestCase objects, grouped by module
  2. Load the mock data markdown
  3. (Optional) Load a previous verification report JSON for context
  4. For each module:
       a. Build prompt with TCs + mock data + verification results
       b. ONE LLM call → enriched JSON per TC
  5. Write enriched_test_cases.json + enriched_test_cases.md
"""

import json
import os
from typing import Any, Dict, List, Optional

from intelligent_navigator.core.llm import LLMClient
from intelligent_navigator.core.logging import DebugLogger
from intelligent_navigator.core.models import TestCase
from intelligent_navigator.core.utils import log, parse_llm_json
from intelligent_navigator.test_case_verifier.test_case_parser import TestCaseParser
from intelligent_navigator.test_case_enricher.prompts import (
    PROMPT_ENRICHER_SYSTEM,
    PROMPT_ENRICHER_CHECK,
    format_test_cases_block,
    format_verification_results,
)


class TestCaseEnricher:
    """
    Enriches all test cases with real data, metadata, and step repairs.

    Parameters
    ----------
    config : dict with keys:
        base_url            : str
        test_case_file      : str
        mock_data_file      : str
        verification_report : str  (optional path to test_case_report.json)
        output_dir          : str
        api_key             : str
        model_name          : str
        debug               : bool
    """

    def __init__(self, config: Dict[str, Any]):
        self.base_url = config["base_url"].rstrip("/")
        self.test_case_file = config["test_case_file"]
        self.mock_data_file = config["mock_data_file"]
        self.verification_report_path = config.get("verification_report", "")
        self.output_dir = config.get("output_dir", "output")
        self.debug = config.get("debug", False)

        self.debug_logger = DebugLogger()
        self.debug_file: Optional[str] = None
        if self.debug:
            self.debug_file = self.debug_logger.get_debug_file_path("tc_enrichment")
            print(f"\n[DEBUG] Log file: {self.debug_file}\n")

        api_key = config["api_key"]
        model_name = config.get("model_name", "openai/gpt-4o-mini")

        self.llm = LLMClient(
            api_key=api_key,
            model_name=model_name,
            system_prompt=PROMPT_ENRICHER_SYSTEM,
            debug_file=self.debug_file,
        )
        self.parser = TestCaseParser()
        self.llm_call_count = 0

    # ================================================================
    # Public API
    # ================================================================

    def run(self) -> Dict[str, Any]:
        """Execute the enrichment pipeline and return the enriched report dict."""
        print("=" * 60)
        print("TEST CASE ENRICHER STARTED")
        print(f"Base URL   : {self.base_url}")
        print(f"TC file    : {self.test_case_file}")
        print(f"Mock data  : {self.mock_data_file}")
        if self.verification_report_path:
            print(f"Verify rpt : {self.verification_report_path}")
        print("=" * 60)

        # --- Load inputs ---
        mock_data = self._load_mock_data()
        verification_map = self._load_verification_report()

        with open(self.test_case_file, encoding="utf-8") as f:
            markdown_text = f.read()

        all_tcs: List[TestCase] = self.parser.parse(markdown_text)
        grouped = self.parser.group_by_module(all_tcs)

        print(f"Parsed {len(all_tcs)} test cases across {len(grouped)} modules\n")

        # --- Enrich each module ---
        all_enriched: List[Dict[str, Any]] = []

        for module_name, tcs in grouped.items():
            enriched = self._enrich_module(
                module_name=module_name,
                tcs=tcs,
                mock_data=mock_data,
                verification_map=verification_map,
            )
            all_enriched.extend(enriched)

        # --- Build report ---
        kept = [r for r in all_enriched if not r.get("dropped")]
        dropped = [r for r in all_enriched if r.get("dropped")]

        report = {
            "base_url": self.base_url,
            "test_case_file": self.test_case_file,
            "mock_data_file": self.mock_data_file,
            "summary": {
                "total_input": len(all_enriched),
                "kept": len(kept),
                "dropped": len(dropped),
                "llm_calls": self.llm_call_count,
            },
            "test_cases": all_enriched,
        }

        self._write_outputs(report)

        # --- Summary ---
        print("\n" + "=" * 60)
        print("ENRICHMENT COMPLETE")
        print(f"Total input  : {len(all_enriched)}")
        print(f"  ✅ Kept    : {len(kept)}")
        print(f"  🗑  Dropped : {len(dropped)}")
        print(f"LLM calls    : {self.llm_call_count}")
        print(f"\nOutputs:")
        print(f"  JSON   → {os.path.join(self.output_dir, 'enriched_test_cases.json')}")
        print(f"  Report → {os.path.join(self.output_dir, 'enriched_test_cases.md')}")
        print("=" * 60)

        return report

    # ================================================================
    # Module Enrichment
    # ================================================================

    def _enrich_module(
        self,
        module_name: str,
        tcs: List[TestCase],
        mock_data: str,
        verification_map: Dict[str, List[Dict]],
    ) -> List[Dict[str, Any]]:
        """Enrich all TCs in a module via one LLM call."""
        print(f"\n--- Module: {module_name} ({len(tcs)} TCs) ---")

        verification_results = verification_map.get(module_name, [])

        prompt = PROMPT_ENRICHER_CHECK.format(
            module_name=module_name,
            base_url=self.base_url,
            mock_data=mock_data,
            test_cases_block=format_test_cases_block(tcs),
            verification_results=format_verification_results(verification_results),
        )

        try:
            response = self.llm.ask(prompt)
            self.llm_call_count += 1
            data = parse_llm_json(response)
        except Exception as e:
            log(f"  LLM error for module '{module_name}': {e}", self.debug, self.debug_file)
            # Fallback: return minimal records
            return [
                {
                    "tc_id": tc.tc_id,
                    "module": tc.module,
                    "title": tc.title,
                    "type": tc.tc_type,
                    "priority": tc.priority,
                    "direct_link": f"{self.base_url}{tc.target_url}",
                    "requires_auth": False,
                    "preconditions": tc.preconditions,
                    "steps": [f"{s.number}. {s.description}" for s in tc.steps],
                    "expected_result": tc.expected_result,
                    "test_data": {},
                    "verdict": "not_verified",
                    "issues": [],
                    "dropped": False,
                    "drop_reason": "",
                    "notes": f"Enrichment LLM call failed: {e}",
                }
                for tc in tcs
            ]

        results = data.get("results", [])

        # Match LLM output back to TCs by tc_id; fill gaps with fallback
        tc_map = {tc.tc_id: tc for tc in tcs}
        enriched = []
        for r in results:
            tc_id = r.get("tc_id", "")
            status = "🗑 " if r.get("dropped") else "✅"
            drop_note = f" ({r.get('drop_reason', '')})" if r.get("dropped") else ""
            print(f"    {status} {tc_id}: {'dropped' if r.get('dropped') else 'enriched'}{drop_note}")
            enriched.append(r)

        return enriched

    # ================================================================
    # Loaders
    # ================================================================

    def _load_mock_data(self) -> str:
        if not self.mock_data_file or not os.path.isfile(self.mock_data_file):
            print("  Warning: mock data file not found — placeholders will not be filled")
            return "(No mock data provided)"
        with open(self.mock_data_file, encoding="utf-8") as f:
            return f.read()

    def _load_verification_report(self) -> Dict[str, List[Dict]]:
        """
        Returns a dict keyed by module name → list of TC result dicts.
        """
        if not self.verification_report_path or not os.path.isfile(self.verification_report_path):
            return {}

        try:
            with open(self.verification_report_path, encoding="utf-8") as f:
                report = json.load(f)

            by_module: Dict[str, List[Dict]] = {}
            for r in report.get("results", []):
                module = r.get("module", "Unknown")
                by_module.setdefault(module, []).append(r)
            print(f"  Loaded verification results for {len(by_module)} modules")
            return by_module
        except Exception as e:
            print(f"  Warning: could not load verification report: {e}")
            return {}

    # ================================================================
    # Output
    # ================================================================

    def _write_outputs(self, report: Dict[str, Any]) -> None:
        os.makedirs(self.output_dir, exist_ok=True)

        json_path = os.path.join(self.output_dir, "enriched_test_cases.json")
        md_path   = os.path.join(self.output_dir, "enriched_test_cases.md")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self._build_markdown(report))

    def _build_markdown(self, report: Dict[str, Any]) -> str:
        lines = []
        lines.append("# Enriched Test Cases\n")
        lines.append(f"**Application:** {report['base_url']}  ")
        lines.append(f"**TC File:** `{report['test_case_file']}`  ")
        lines.append(f"**Mock Data:** `{report['mock_data_file']}`  \n")
        lines.append("---\n")

        s = report["summary"]
        lines.append("## Summary\n")
        lines.append("| Metric | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Input | {s['total_input']} |")
        lines.append(f"| ✅ Kept | {s['kept']} |")
        lines.append(f"| 🗑 Dropped | {s['dropped']} |")
        lines.append(f"| LLM Calls | {s['llm_calls']} |\n")
        lines.append("---\n")

        # Group by module
        by_module: Dict[str, list] = {}
        for tc in report["test_cases"]:
            by_module.setdefault(tc.get("module", "Unknown"), []).append(tc)

        for module_name, tcs in by_module.items():
            lines.append(f"## {module_name}\n")

            for tc in tcs:
                dropped = tc.get("dropped", False)
                badge = "🗑 Dropped" if dropped else "✅ Kept"
                verdict = tc.get("verdict", "not_verified")
                verdict_badge = {
                    "valid": "✅ Valid", "invalid_steps": "⚠️ Invalid Steps",
                    "invalid": "❌ Invalid", "skipped": "⏭️ Skipped",
                    "not_verified": "—",
                }.get(verdict, verdict)

                lines.append(f"### {badge} — {tc.get('tc_id')} — {tc.get('title')}")
                lines.append(f"**Type:** {tc.get('type')} | **Priority:** {tc.get('priority')} | "
                             f"**Verified:** {verdict_badge}  ")
                lines.append(f"**URL:** [{tc.get('direct_link', '—')}]({tc.get('direct_link', '')}) | "
                             f"**Requires Auth:** {'Yes' if tc.get('requires_auth') else 'No'}\n")

                if dropped:
                    lines.append(f"> 🗑 **Dropped:** {tc.get('drop_reason', '')}\n")
                else:
                    lines.append(f"**Preconditions:** {tc.get('preconditions', '')}  \n")

                    if tc.get("steps"):
                        lines.append("**Steps:**")
                        for step in tc["steps"]:
                            lines.append(f"- {step}")
                        lines.append("")

                    if tc.get("expected_result"):
                        lines.append(f"**Expected Result:** {tc['expected_result']}  \n")

                    if tc.get("test_data"):
                        lines.append("**Test Data:**")
                        for k, v in tc["test_data"].items():
                            lines.append(f"- `{k}`: {v}")
                        lines.append("")

                    if tc.get("issues"):
                        lines.append("**Issues:**")
                        for issue in tc["issues"]:
                            lines.append(f"- {issue}")
                        lines.append("")

                    if tc.get("notes"):
                        lines.append(f"**Notes:** {tc['notes']}  \n")

                lines.append("---\n")

        return "\n".join(lines)
