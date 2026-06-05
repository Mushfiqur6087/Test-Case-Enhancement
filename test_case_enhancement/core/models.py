"""
Data models for the Test Case Enhancement spec verification pipeline.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RoleCredentials:
    """Credentials for a single role."""
    username: str
    password: str
    role: str


# ---- Spec Verifier Models ----

@dataclass
class TestCaseStep:
    number: int
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {"number": self.number, "description": self.description}


@dataclass
class TestCase:
    tc_id: str
    title: str
    tc_type: str
    priority: str
    module_name: str
    preconditions: str
    steps: List[TestCaseStep]
    expected_result: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tc_id": self.tc_id,
            "title": self.title,
            "tc_type": self.tc_type,
            "priority": self.priority,
            "module_name": self.module_name,
            "preconditions": self.preconditions,
            "steps": [s.to_dict() for s in self.steps],
            "expected_result": self.expected_result,
        }


@dataclass
class TestCaseVerificationResult:
    tc_id: str
    verdict: str  # "valid" | "invalid_steps" | "invalid"
    valid_steps: List[str] = field(default_factory=list)
    invalid_steps: List[str] = field(default_factory=list)
    missing_steps: List[str] = field(default_factory=list)
    precondition_issues: List[str] = field(default_factory=list)
    invalid_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tc_id": self.tc_id,
            "verdict": self.verdict,
            "valid_steps": self.valid_steps,
            "invalid_steps": self.invalid_steps,
            "missing_steps": self.missing_steps,
            "precondition_issues": self.precondition_issues,
            "invalid_reason": self.invalid_reason,
            "notes": self.notes,
        }


@dataclass
class EnrichedTestCase:
    tc_id: str
    module: str
    title: str
    type: str
    priority: str
    direct_link: str
    requires_auth: bool
    preconditions: str
    steps: List[str]
    expected_result: str
    test_data: Dict[str, Any]
    verdict: str
    issues: List[str]
    dropped: bool
    drop_reason: str
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tc_id": self.tc_id,
            "module": self.module,
            "title": self.title,
            "type": self.type,
            "priority": self.priority,
            "direct_link": self.direct_link,
            "requires_auth": self.requires_auth,
            "preconditions": self.preconditions,
            "steps": self.steps,
            "expected_result": self.expected_result,
            "test_data": self.test_data,
            "verdict": self.verdict,
            "issues": self.issues,
            "dropped": self.dropped,
            "drop_reason": self.drop_reason,
            "notes": self.notes,
        }

@dataclass
class SpecSection:
    """One section of a functional description document."""
    name: str       # e.g. "Login", "Register"
    raw_text: str   # Full markdown text of this section


@dataclass
class SectionVerificationResult:
    """The spec checker's verdict for one SpecSection."""
    section_name: str
    actual_url: str              # URL the browser landed on
    actual_title: str            # Page title the browser saw
    verdict: str                 # "pass" | "partial" | "fail" | "skipped"
    compliance_score: int        # 0-100
    matches: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    mismatches: List[str] = field(default_factory=list)
    notes: str = ""
    navigation_success: bool = True
    navigation_failure_reason: str = ""
    test_case_results: List[TestCaseVerificationResult] = field(default_factory=list)
    enriched_test_cases: List[EnrichedTestCase] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section_name": self.section_name,
            "actual_url": self.actual_url,
            "actual_title": self.actual_title,
            "verdict": self.verdict,
            "compliance_score": self.compliance_score,
            "matches": self.matches,
            "missing": self.missing,
            "mismatches": self.mismatches,
            "notes": self.notes,
            "navigation_success": self.navigation_success,
            "navigation_failure_reason": self.navigation_failure_reason,
            "test_case_results": [r.to_dict() for r in self.test_case_results],
            "enriched_test_cases": [r.to_dict() for r in self.enriched_test_cases],
        }


@dataclass
class VerificationReport:
    """Full output of a spec verification run."""
    project_url: str
    functional_desc_file: str
    captured_at: str
    sections_checked: int
    passed: int
    partial: int
    failed: int
    skipped: int
    overall_score: float           # Weighted average compliance score
    section_results: List[SectionVerificationResult] = field(default_factory=list)
    llm_calls_total: int = 0
    verification_stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_url": self.project_url,
            "functional_desc_file": self.functional_desc_file,
            "captured_at": self.captured_at,
            "summary": {
                "sections_checked": self.sections_checked,
                "passed": self.passed,
                "partial": self.partial,
                "failed": self.failed,
                "skipped": self.skipped,
                "overall_score": round(self.overall_score, 1),
            },
            "section_results": [r.to_dict() for r in self.section_results],
            "verification_stats": {
                **self.verification_stats,
                "llm_calls_total": self.llm_calls_total,
            },
        }
