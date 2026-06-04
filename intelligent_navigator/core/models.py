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
        - click_element: click a specific element identified by link_text on the
                         current page (used for SPA navigation where href="#")
        - login        : navigate to the login page and fill credentials
        - logout       : click the logout link on the current page
    """
    command_type: str   # "explore_page" | "click_element" | "login" | "logout"
    target_url: str = ""
    target_label: str = ""
    credentials: Optional[RoleCredentials] = None
    reasoning: str = ""
    click_target_text: str = ""   # visible text of the element to click (for click_element)


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



