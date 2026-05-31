"""
Test Case Report Builder.

Builds JSON and Markdown reports from a TestCaseReport object.
"""

import json
import os
from datetime import datetime
from typing import List

from intelligent_navigator.core.models import TestCaseReport, TestCaseVerificationResult

_VERDICT_BADGE = {
    "valid":          "✅ Valid",
    "invalid_steps":  "⚠️ Invalid Steps",
    "invalid":        "❌ Invalid",
    "skipped":        "⏭️ Skipped",
}


class TestCaseReportBuilder:

    def build(
        self,
        project_url: str,
        test_case_file: str,
        results: List[TestCaseVerificationResult],
        llm_calls: int,
    ) -> TestCaseReport:
        total                = len(results)
        valid_count          = sum(1 for r in results if r.verdict == "valid")
        invalid_steps_count  = sum(1 for r in results if r.verdict == "invalid_steps")
        invalid_count        = sum(1 for r in results if r.verdict == "invalid")
        skipped_count        = sum(1 for r in results if r.verdict == "skipped")
        overall_accuracy     = (valid_count / total * 100) if total > 0 else 0.0

        return TestCaseReport(
            project_url=project_url,
            test_case_file=test_case_file,
            captured_at=datetime.now().isoformat(),
            total=total,
            valid_count=valid_count,
            invalid_steps_count=invalid_steps_count,
            invalid_count=invalid_count,
            skipped_count=skipped_count,
            overall_accuracy=overall_accuracy,
            results=results,
            llm_calls_total=llm_calls,
        )

    def write(self, report: TestCaseReport, output_dir: str) -> None:
        os.makedirs(output_dir, exist_ok=True)
        json_path = os.path.join(output_dir, "test_case_report.json")
        md_path   = os.path.join(output_dir, "test_case_report.md")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self._build_markdown(report))

    def _build_markdown(self, report: TestCaseReport) -> str:
        lines = []
        lines.append("# Test Case Verification Report\n")
        lines.append(f"**Application:** {report.project_url}  ")
        lines.append(f"**Test Cases:** `{report.test_case_file}`  ")
        lines.append(f"**Generated:** {report.captured_at}  ")
        lines.append(f"**LLM Calls:** {report.llm_calls_total}\n")
        lines.append("---\n")

        # Summary table
        accuracy = report.overall_accuracy
        lines.append("## Summary\n")
        lines.append("| Metric | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| ✅ Valid | {report.valid_count} |")
        lines.append(f"| ⚠️ Invalid Steps | {report.invalid_steps_count} |")
        lines.append(f"| ❌ Invalid | {report.invalid_count} |")
        lines.append(f"| ⏭️ Skipped | {report.skipped_count} |")
        lines.append(f"| **Total** | **{report.total}** |")
        lines.append(f"| **Accuracy** | **{accuracy:.0f}%** |\n")
        lines.append("---\n")

        # Quick results table
        lines.append("## Results Table\n")
        lines.append("| TC ID | Module | Type | Priority | Verdict | Notes |")
        lines.append("|-------|--------|------|----------|---------|-------|")
        for r in report.results:
            badge = _VERDICT_BADGE.get(r.verdict, r.verdict)
            short_notes = (r.notes or "")[:80].replace("|", "\\|")
            lines.append(
                f"| {r.tc_id} | {r.module} | {r.tc_type} | {r.priority} "
                f"| {badge} | {short_notes} |"
            )
        lines.append("")

        # Per-module detail
        lines.append("---\n")
        lines.append("## Detail by Module\n")

        current_module = None
        for r in report.results:
            if r.module != current_module:
                current_module = r.module
                lines.append(f"### {r.module}\n")

            badge = _VERDICT_BADGE.get(r.verdict, r.verdict)
            lines.append(f"#### {badge} — {r.tc_id}: {r.title}")
            lines.append(f"**Type:** {r.tc_type} | **Priority:** {r.priority}  ")
            lines.append(f"**URL:** {r.actual_url}\n")

            if r.valid_steps:
                lines.append("**✔ Valid Steps:**")
                for s in r.valid_steps:
                    lines.append(f"- {s}")
                lines.append("")

            if r.precondition_issues:
                lines.append("**⚠ Precondition Issues:**")
                for s in r.precondition_issues:
                    lines.append(f"- {s}")
                lines.append("")

            if r.invalid_steps:
                lines.append("**✘ Invalid Steps (referenced element NOT found in DOM):**")
                for s in r.invalid_steps:
                    lines.append(f"- {s}")
                lines.append("")

            if r.missing_steps:
                lines.append("**⚠ Missing Steps (mandatory interaction absent from test):**")
                for s in r.missing_steps:
                    lines.append(f"- {s}")
                lines.append("")

            if r.invalid_reason:
                lines.append(f"**Invalid Reason:** {r.invalid_reason}\n")

            if r.notes:
                lines.append(f"**Notes:** {r.notes}\n")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)
