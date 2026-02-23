"""
LLM-Guided Exploration Agent (Three-Agent Architecture).

Thin orchestrator that delegates to:
  - NavigatorAgent  (strategic: which page to visit)
  - PageNavigator   (tactical: how to get there)
  - PageExplorer    (thorough: extract links + sub-states)

The external API is unchanged: ExplorationAgent(config).run() → ExplorationResult.
"""

import json
import os
import sys
from typing import Any, Dict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, PROJECT_ROOT)

from test_case_enhancer.agent.exploration_agent.models import ExplorationResult
from test_case_enhancer.agent.exploration_agent.navigator_agent import NavigatorAgent


class ExplorationAgent:
    """
    Main entry point for web exploration.
    Delegates all work to NavigatorAgent which coordinates
    PageNavigator and PageExplorer sub-agents.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.navigator_agent = NavigatorAgent(config)
        # Expose browser_controller for cleanup in run_exploration.py
        self.browser_controller = self.navigator_agent.browser_controller

    def run(self) -> ExplorationResult:
        """Run the full exploration and return results."""
        return self.navigator_agent.run()
