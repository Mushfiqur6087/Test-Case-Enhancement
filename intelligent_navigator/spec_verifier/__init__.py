"""
Spec Verifier — Agentic traversal-based compliance checker.

Navigates the live web application by following real links (discovered by
LinkDiscoveryAgent), identifies each page using PageIdentifierAgent, and
verifies it against the functional specification using SpecCheckerAgent.

No hardcoded URL mappings. No keyword guessing.

Main entry points:
  - TraversalOrchestrator : drives the full zero-hardcoding verification run
  - SpecVerifier          : alias for backward compatibility with __main__.py
  - VerificationReport    : the final output dataclass (also in core.models)
"""

from intelligent_navigator.spec_verifier.orchestrator import (
    TraversalOrchestrator,
    SpecVerifier,  # backward-compatible alias
)
from intelligent_navigator.core.models import VerificationReport

__all__ = ["TraversalOrchestrator", "SpecVerifier", "VerificationReport"]
