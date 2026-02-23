"""
Lightweight DOM access utility for the Exploration Agent.
Provides temporary DOM reads for link extraction — nothing is persisted.
Includes scroll-and-capture to find below-fold navigation elements.
"""

import os
import sys
from typing import Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, PROJECT_ROOT)

from test_case_enhancer.browser.full_page_dom_builder import FullPageDomTreeBuilder
from test_case_enhancer.browser.dom_tree_parser import DOMTreeParser, DOMElementNode


class FullPageDOMTreeParser(DOMTreeParser):
    """DOMTreeParser subclass that uses FullPageDomTreeBuilder for full-page capture."""

    def parse(self) -> DOMElementNode:
        """Override parse() to use the full-page builder (no viewport filtering)."""
        data = FullPageDomTreeBuilder(self.page, debug_mode=False).get_dom_tree()
        self._raw_json = data["tree"]
        self._counts.clear()
        self.dom_tree = self._build_element(
            self._raw_json, parent_xpath="/html[1]/", parent=None
        )
        return self.dom_tree


class DOMHelper:
    """Temporary DOM access for link extraction. Nothing is stored."""

    SCROLL_STEP_PX = 800
    MAX_SCROLLS = 15

    def __init__(self, browser_session):
        self.browser_session = browser_session

    def scroll_and_capture(self) -> Tuple[str, str]:
        """
        Scroll the full page to trigger lazy-loaded content, then capture
        the complete DOM. Returns (selector_map_json, selector_map_string).
        """
        page = self.browser_session.get_current_page()
        if page is None:
            return ("{}", "")

        try:
            # Scroll down incrementally to trigger lazy loading
            prev_height = 0
            for _ in range(self.MAX_SCROLLS):
                page.mouse.wheel(0, self.SCROLL_STEP_PX)
                page.wait_for_timeout(400)

                # Check if we've reached the bottom
                current_height = page.evaluate("document.documentElement.scrollHeight")
                scroll_top = page.evaluate("window.scrollY + window.innerHeight")
                if scroll_top >= current_height - 50:
                    break
                if current_height == prev_height:
                    break  # No new content loaded
                prev_height = current_height

            # Scroll back to top
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(300)

        except Exception:
            pass  # Continue even if scrolling fails

        # Now capture the DOM
        return self.get_dom_for_link_extraction()

    def get_dom_for_link_extraction(self) -> Tuple[str, str]:
        """
        Get both selector_map_json and selector_map_string in one parse.
        Returns (selector_map_json, selector_map_string).
        """
        page = self.browser_session.get_current_page()
        if page is None:
            return ("{}", "")
        try:
            parser = FullPageDOMTreeParser(page)
            parser.parse()
            return (parser.selector_map_json(), parser.get_selector_map_string())
        except Exception:
            return ("{}", "")
