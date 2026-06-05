"""
Verification Report writer.

Converts a list of SectionVerificationResult objects (plus metadata) into:
  1. verification_report.json  — machine-readable full data
  2. verification_report.md    — human-readable summary with emoji verdicts
"""

import json
import os
from datetime import datetime
from typing import List

from test_case_enhancement.core.models import (
    SectionVerificationResult,
    VerificationReport,
)

# Emoji badges for each verdict
_VERDICT_BADGE = {
    "pass":    "✅",
    "partial": "⚠️",
    "fail":    "❌",
    "skipped": "⏭️",
}


def build_report(
    project_url: str,
    functional_desc_file: str,
    section_results: List[SectionVerificationResult],
    llm_calls_total: int = 0,
    extra_stats: dict = None,
) -> VerificationReport:
    """Build a VerificationReport dataclass from section results."""
    passed  = sum(1 for r in section_results if r.verdict == "pass")
    partial = sum(1 for r in section_results if r.verdict == "partial")
    failed  = sum(1 for r in section_results if r.verdict == "fail")
    skipped = sum(1 for r in section_results if r.verdict == "skipped")

    scored = [r for r in section_results if r.verdict != "skipped"]
    overall_score = (
        sum(r.compliance_score for r in scored) / len(scored)
        if scored else 0.0
    )

    return VerificationReport(
        project_url=project_url,
        functional_desc_file=functional_desc_file,
        captured_at=datetime.now().isoformat(),
        sections_checked=len(section_results),
        passed=passed,
        partial=partial,
        failed=failed,
        skipped=skipped,
        overall_score=overall_score,
        section_results=section_results,
        llm_calls_total=llm_calls_total,
        verification_stats=extra_stats or {},
    )


def write_report(report: VerificationReport, output_dir: str) -> dict:
    """
    Write both JSON and Markdown report files to output_dir.

    Returns a dict with the two file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "verification_report.json")
    md_path   = os.path.join(output_dir, "verification_report.md")

    # --- JSON ---
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)

    # --- Markdown ---
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(_render_markdown(report))

    return {"json": json_path, "markdown": md_path}


# ------------------------------------------------------------------ #
# Markdown renderer                                                   #
# ------------------------------------------------------------------ #

def _render_markdown(report: VerificationReport) -> str:
    lines = []

    # Header
    lines.append(f"# Spec Verification Report")
    lines.append(f"")
    lines.append(f"| | |")
    lines.append(f"|---|---|")
    lines.append(f"| **URL** | {report.project_url} |")
    lines.append(f"| **Spec file** | `{report.functional_desc_file}` |")
    lines.append(f"| **Date** | {report.captured_at[:10]} |")
    lines.append(f"| **Overall score** | **{report.overall_score:.0f} / 100** |")
    lines.append(f"")

    # Summary badge row
    lines.append(f"## Summary")
    lines.append(f"")
    lines.append(f"| Verdict | Count |")
    lines.append(f"|---------|-------|")
    lines.append(f"| ✅ Pass    | {report.passed} |")
    lines.append(f"| ⚠️  Partial | {report.partial} |")
    lines.append(f"| ❌ Fail    | {report.failed} |")
    lines.append(f"| ⏭️  Skipped | {report.skipped} |")
    lines.append(f"| **Total** | **{report.sections_checked}** |")
    lines.append(f"")
    lines.append(f"LLM calls used: {report.llm_calls_total}")
    lines.append(f"")
    lines.append("---")
    lines.append("")

    # Per-section results
    lines.append("## Section Results")
    lines.append("")

    for result in report.section_results:
        badge = _VERDICT_BADGE.get(result.verdict, "❓")
        lines.append(
            f"### {badge} {result.section_name} — "
            f"{result.verdict.upper()} ({result.compliance_score}/100)"
        )
        lines.append("")

        if result.actual_url:
            lines.append(f"**Page visited:** `{result.actual_url}` — *{result.actual_title}*")
            lines.append("")

        if not result.navigation_success:
            lines.append(
                f"> ⚠️ **Navigation failed:** {result.navigation_failure_reason}"
            )
            lines.append("")

        if result.matches:
            lines.append("**✔ Matches (spec requirements found in live UI):**")
            for item in result.matches:
                lines.append(f"- {item}")
            lines.append("")

        if result.missing:
            lines.append("**✘ Missing (spec says it should exist, not found in DOM):**")
            for item in result.missing:
                lines.append(f"- {item}")
            lines.append("")

        if result.mismatches:
            lines.append("**⚡ Mismatches (DOM contradicts the spec):**")
            for item in result.mismatches:
                lines.append(f"- {item}")
            lines.append("")

        if result.notes:
            lines.append(f"*{result.notes}*")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)
