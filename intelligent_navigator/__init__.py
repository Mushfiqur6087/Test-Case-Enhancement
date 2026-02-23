"""
Intelligent Navigator -- LLM-guided web exploration agent.

Automatically explores web applications, building a complete navigation
graph by combining three specialized agents:
  - Orchestrator: strategic planning (which page to visit next)
  - Navigator: tactical execution (how to reach a target page)
  - Explorer: thorough extraction (all links and sub-states on a page)
"""

from intelligent_navigator.agents.orchestrator import Orchestrator
from intelligent_navigator.core.models import ExplorationResult

__all__ = ["Orchestrator", "ExplorationResult"]
