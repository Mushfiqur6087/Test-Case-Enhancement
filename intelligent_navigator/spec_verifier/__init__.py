"""
Spec Verifier — Plan-based agentic traversal compliance checker.

Uses a TraversalPlannerAgent to analyze the functional specification and
generate an ordered traversal plan. An ActionEngine then executes each
step using Playwright-driven actions. Pages are identified by
PageIdentifierAgent and verified by SpecCheckerAgent.

No hardcoded URL mappings. No keyword guessing. No BFS link discovery.

Main entry points:
  - TraversalOrchestrator : drives the full plan-based verification run
  - SpecVerifier          : alias for backward compatibility with __main__.py
  - VerificationReport    : the final output dataclass (also in core.models)
"""

from intelligent_navigator.spec_verifier.orchestrator import (
    TraversalOrchestrator,
    SpecVerifier,  # backward-compatible alias
)
from intelligent_navigator.core.models import VerificationReport

__all__ = ["TraversalOrchestrator", "SpecVerifier", "VerificationReport"]
