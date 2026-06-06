"""Verification Report writer."""

import json
import os
from datetime import datetime
from typing import List

from test_case_enhancement.core.models import (
    SectionVerificationResult,
    VerificationReport,
)
from test_case_enhancement.reporting.markdown_renderer import render_markdown

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
        f.write(render_markdown(report))

    # --- Enriched Test Cases JSON & Markdown ---
    all_enriched = []
    for section_res in report.section_results:
        if hasattr(section_res, "enriched_test_cases"):
            all_enriched.extend([tc.to_dict() for tc in section_res.enriched_test_cases])
            
    enriched_path = ""
    enriched_md_path = ""
    if all_enriched:
        enriched_path = os.path.join(output_dir, "enriched_test_cases.json")
        with open(enriched_path, "w", encoding="utf-8") as f:
            json.dump({"test_cases": all_enriched}, f, indent=2, ensure_ascii=False)
            
        enriched_md_path = os.path.join(output_dir, "enriched_test_cases.md")
        with open(enriched_md_path, "w", encoding="utf-8") as f:
            md = ["# Enriched Test Cases\n"]
            for tc in all_enriched:
                md.append(f"## {tc.get('tc_id', 'Unknown')} - {tc.get('title', 'Untitled')}")
                md.append(f"- **Module:** {tc.get('module', 'N/A')}")
                md.append(f"- **Direct Link:** {tc.get('direct_link', 'N/A')}")
                md.append(f"- **Requires Auth:** {tc.get('requires_auth', 'Unknown')}")
                md.append("\n### Steps")
                for step in tc.get('steps', []):
                    md.append(f"{step}")
                md.append("\n### Test Data")
                md.append("```json\n" + json.dumps(tc.get('test_data', {}), indent=2) + "\n```\n")
            f.write("\n".join(md))

    # --- Audited Test Cases JSON & Markdown ---
    all_audited = []
    for section_res in report.section_results:
        if hasattr(section_res, "test_case_results"):
            all_audited.extend([tc.to_dict() for tc in section_res.test_case_results])
            
    audited_path = ""
    audited_md_path = ""
    if all_audited:
        audited_path = os.path.join(output_dir, "audited_test_cases.json")
        with open(audited_path, "w", encoding="utf-8") as f:
            json.dump({"test_cases": all_audited}, f, indent=2, ensure_ascii=False)
            
        audited_md_path = os.path.join(output_dir, "audited_test_cases.md")
        with open(audited_md_path, "w", encoding="utf-8") as f:
            md = ["# Audited Test Cases\n"]
            for tc in all_audited:
                md.append(f"## {tc.get('tc_id', 'Unknown')} - {tc.get('verdict', 'Unknown').upper()}")
                md.append(f"- **Valid Steps:** {len(tc.get('valid_steps', []))}")
                md.append(f"- **Invalid Steps:** {len(tc.get('invalid_steps', []))}")
                if tc.get('invalid_reason'):
                    md.append(f"- **Reason:** {tc.get('invalid_reason')}")
                md.append(f"- **Notes:** {tc.get('notes', '')}\n")
            f.write("\n".join(md))

    return {
        "json": json_path,
        "markdown": md_path,
        "enriched_test_cases_json": enriched_path,
        "enriched_test_cases_md": enriched_md_path,
        "audited_test_cases_json": audited_path,
        "audited_test_cases_md": audited_md_path
    }
