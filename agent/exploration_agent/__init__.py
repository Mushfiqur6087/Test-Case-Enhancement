"""Exploration Agent - LLM-guided web explorer that builds a navigation graph."""

# Lazy imports to avoid pulling in openai/playwright at package load time.
# Use: from test_case_enhancer.agent.exploration_agent.agent import ExplorationAgent
# Or:  from test_case_enhancer.agent.exploration_agent.models import ExplorationResult

__all__ = ["ExplorationAgent", "ExplorationResult"]
