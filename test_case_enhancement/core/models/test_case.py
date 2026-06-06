"""Test case related models."""
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class TestCaseStep:
    """TestCaseStep class."""
    number: int
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """to_dict method/function."""
        return {"number": self.number, "description": self.description}


@dataclass
class TestCase:
    """TestCase class."""
    tc_id: str
    title: str
    tc_type: str
    priority: str
    module_name: str
    preconditions: str
    steps: List[TestCaseStep]
    expected_result: str

    def to_dict(self) -> Dict[str, Any]:
        """to_dict method/function."""
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
    """TestCaseVerificationResult class."""
    tc_id: str
    verdict: str  # "valid" | "invalid_steps" | "invalid"
    valid_steps: List[str] = field(default_factory=list)
    invalid_steps: List[str] = field(default_factory=list)
    missing_steps: List[str] = field(default_factory=list)
    precondition_issues: List[str] = field(default_factory=list)
    invalid_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """to_dict method/function."""
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
    """EnrichedTestCase class."""
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
        """to_dict method/function."""
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
