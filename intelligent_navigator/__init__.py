"""
Intelligent Navigator — Spec Compliance Verifier.

Reads a functional description markdown, navigates to each described page,
and uses an LLM to verify whether the live application correctly implements
what the spec says.

Main entry points:
  SpecVerifier      : drives the full verification run
  VerificationReport: the final output dataclass
"""

from intelligent_navigator.spec_verifier.orchestrator import SpecVerifier
from intelligent_navigator.core.models import VerificationReport

__all__ = ["SpecVerifier", "VerificationReport"]
