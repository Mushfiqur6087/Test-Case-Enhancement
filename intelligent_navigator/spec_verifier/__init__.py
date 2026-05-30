"""
Spec Verifier -- Description-driven compliance checker.

Instead of exploring a web app by following links, this module reads a
functional description (markdown), navigates to each described page, and
uses an LLM to verify that the live HTML actually implements what the
spec says.

Main entry points:
  - SpecVerifier      : drives the full verification run
  - VerificationReport: the final output dataclass (also in core.models)
"""

from intelligent_navigator.spec_verifier.orchestrator import SpecVerifier
from intelligent_navigator.core.models import VerificationReport

__all__ = ["SpecVerifier", "VerificationReport"]
