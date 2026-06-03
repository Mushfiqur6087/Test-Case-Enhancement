"""
Intelligent Navigator — Spec Compliance Verifier.

Main entry points:
  SpecVerifier        : drives spec compliance verification
  VerificationReport  : spec verification output
"""

from intelligent_navigator.spec_verifier.orchestrator import SpecVerifier
from intelligent_navigator.core.models import VerificationReport

__all__ = ["SpecVerifier", "VerificationReport"]
