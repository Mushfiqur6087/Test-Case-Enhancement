"""Markdown renderer for the Verification Report."""

from test_case_enhancement.core.models import VerificationReport

# Emoji badges for each verdict
_VERDICT_BADGE = {
    "pass":    "✅",
    "partial": "⚠️",
    "fail":    "❌",
    "skipped": "⏭️",
}

def render_markdown(report: VerificationReport) -> str:
    """render_markdown method/function."""
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

        if hasattr(result, "test_case_results") and result.test_case_results:
            lines.append("#### Test Case Verification")
            lines.append("")
            for tc_res in result.test_case_results:
                tc_badge = _VERDICT_BADGE.get(tc_res.verdict, "❓")
                if tc_res.verdict == "invalid_steps":
                    tc_badge = "⚠️"
                elif tc_res.verdict == "valid":
                    tc_badge = "✅"
                elif tc_res.verdict == "invalid":
                    tc_badge = "❌"
                    
                lines.append(f"- **{tc_res.tc_id}** {tc_badge} {tc_res.verdict.upper()}")
                if tc_res.invalid_steps:
                    for invalid in tc_res.invalid_steps:
                        lines.append(f"  - ❌ {invalid}")
                if tc_res.missing_steps:
                    for missing in tc_res.missing_steps:
                        lines.append(f"  - ⚠️ {missing}")
                if tc_res.precondition_issues:
                    for pre in tc_res.precondition_issues:
                        lines.append(f"  - 🛑 {pre}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)
