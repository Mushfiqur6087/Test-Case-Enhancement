"""
Data models for the Intelligent Navigator spec verification pipeline.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---- Navigator Models ----

@dataclass
class RoleCredentials:
    """Credentials for a single role."""
    username: str
    password: str
    role: str
    privilege_level: int = 0


@dataclass
class NavigatorCommand:
    """Command sent from SpecVerifier → Navigator.

    command_type:
        - explore_page : navigate to target_url so we can capture its DOM
        - login        : navigate to the login page and fill credentials
        - logout       : click the logout link on the current page
    """
    command_type: str   # "explore_page" | "login" | "logout"
    target_url: str = ""
    target_label: str = ""
    credentials: Optional[RoleCredentials] = None
    reasoning: str = ""


@dataclass
class PageNavigatorResult:
    """Result returned from Navigator → SpecVerifier."""
    success: bool
    current_url: str = ""
    current_title: str = ""
    failure_reason: str = ""
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    retry_attempted: bool = False
    navigation_steps: int = 0
    was_redirected: bool = False
    redirected_to: str = ""


@dataclass
class NavigationStepRecord:
    """Record of a single step in the Navigator's multi-step loop."""
    step_number: int
    url_before: str
    title_before: str
    actions_requested: List[Dict[str, Any]] = field(default_factory=list)
    actions_executed: List[Dict[str, Any]] = field(default_factory=list)
    url_after: str = ""
    title_after: str = ""
    reasoning: str = ""


# ---- Spec Verifier Models ----

@dataclass
class SpecSection:
    """One section of a functional description document."""
    name: str                    # e.g. "Login", "Register"
    raw_text: str                # Full markdown text of this section
    url_hint: str = ""           # Best-guess URL path, e.g. "/login"
    requires_auth: bool = False  # True if this section implies a logged-in state


@dataclass
class SectionVerificationResult:
    """The spec checker's verdict for one SpecSection."""
    section_name: str
    url_hint: str
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section_name": self.section_name,
            "url_hint": self.url_hint,
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


# ---- Test Case Verifier Models ----

@dataclass
class TestStep:
    """A single numbered step from a test case."""
    number: int
    description: str  # e.g. "Enter email in Email/Username field"


@dataclass
class TestCase:
    """A fully-parsed test case from a test cases markdown file."""
    tc_id: str              # "TC-001"
    module: str             # "Login"
    title: str              # "Successful sign-in with valid credentials"
    tc_type: str            # "Positive" | "Negative" | "Edge/Boundary" etc.
    priority: str           # "High" | "Medium" | "Low"
    preconditions: str
    steps: List[TestStep]
    expected_result: str
    target_url: str         # inferred URL hint, e.g. "/login"


@dataclass
class TestCaseVerificationResult:
    """Verdict for a single test case."""
    tc_id: str
    module: str
    title: str
    tc_type: str
    priority: str
    verdict: str            # "valid" | "invalid_steps" | "invalid" | "skipped"
    valid_steps: List[str] = field(default_factory=list)
    invalid_steps: List[str] = field(default_factory=list)       # TC steps not found in DOM
    missing_steps: List[str] = field(default_factory=list)       # Mandatory interactions not in steps
    precondition_issues: List[str] = field(default_factory=list) # Preconditions that don't match page
    invalid_reason: str = ""
    notes: str = ""
    actual_url: str = ""
    actual_title: str = ""
    navigation_success: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tc_id": self.tc_id,
            "module": self.module,
            "title": self.title,
            "type": self.tc_type,
            "priority": self.priority,
            "verdict": self.verdict,
            "valid_steps": self.valid_steps,
            "invalid_steps": self.invalid_steps,
            "missing_steps": self.missing_steps,
            "precondition_issues": self.precondition_issues,
            "invalid_reason": self.invalid_reason,
            "notes": self.notes,
            "actual_url": self.actual_url,
            "actual_title": self.actual_title,
            "navigation_success": self.navigation_success,
        }


@dataclass
class TestCaseReport:
    """Full output of a test case verification run."""
    project_url: str
    test_case_file: str
    captured_at: str
    total: int
    valid_count: int
    invalid_steps_count: int    # TCs with verdict == "invalid_steps"
    invalid_count: int          # TCs with verdict == "invalid" (page wrong/missing)
    skipped_count: int
    overall_accuracy: float     # % of TCs with verdict == "valid"
    results: List[TestCaseVerificationResult] = field(default_factory=list)
    llm_calls_total: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_url": self.project_url,
            "test_case_file": self.test_case_file,
            "captured_at": self.captured_at,
            "summary": {
                "total": self.total,
                "valid": self.valid_count,
                "invalid_steps": self.invalid_steps_count,
                "invalid": self.invalid_count,
                "skipped": self.skipped_count,
                "overall_accuracy_pct": round(self.overall_accuracy, 1),
            },
            "results": [r.to_dict() for r in self.results],
            "llm_calls_total": self.llm_calls_total,
        }
