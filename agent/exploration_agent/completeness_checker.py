"""
Lightweight completeness checker for the LLM-guided Exploration Agent.
The LLM sees the functional spec directly in its prompt and reasons about
coverage itself. This module provides a summary for the final output.
"""

import os
import sys
from typing import Any, Dict, List

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, PROJECT_ROOT)

from test_case_enhancer.agent.exploration_agent.navigation_graph import NavigationGraph


class CompletenessChecker:
    """Provides coverage summary based on the navigation graph."""

    def __init__(self):
        pass

    def get_coverage_summary(self, graph: NavigationGraph) -> Dict[str, Any]:
        """Return a summary of what the graph covers for the final output."""
        graph_data = graph.serialize()
        nodes = graph_data.get("nodes", [])

        visited_pages = []
        for node in nodes:
            if node.get("state") in ("visited", "fully_explored"):
                title = node.get("title", "")
                urls = node.get("urls", [])
                url_str = urls[0] if urls else node.get("identity_key", "")
                visited_pages.append({"title": title, "url": url_str})

        return {
            "total_pages_discovered": len(nodes),
            "pages_visited": len(visited_pages),
            "visited_page_list": visited_pages,
        }
