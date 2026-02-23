"""
Full-page DOM tree builder that captures ALL elements regardless of viewport position.
Subclass of DomTreeBuilder that overrides viewport filtering.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from test_case_enhancer.browser.dom_tree_builder import DomTreeBuilder


class FullPageDomTreeBuilder(DomTreeBuilder):
    """DOM tree builder that captures ALL elements regardless of viewport."""

    def is_in_viewport(self, element_handle) -> bool:
        """Override: always return True so no element is skipped for being outside viewport."""
        return True
