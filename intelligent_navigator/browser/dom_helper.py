"""
Full-page DOM capture utilities.

Combines:
- FullPageDomTreeBuilder: captures ALL elements regardless of viewport
- FullPageDOMTreeParser: DOMTreeParser subclass using full-page builder
- DOMHelper: scroll-and-capture helper for lazy-loaded content
"""

from typing import Tuple

from intelligent_navigator.browser.dom_builder import DomTreeBuilder
from intelligent_navigator.browser.dom_parser import DOMTreeParser, DOMElementNode


class FullPageDomTreeBuilder(DomTreeBuilder):
    """DOM tree builder that captures ALL elements regardless of viewport."""

    def is_in_viewport(self, element_handle) -> bool:
        """Override: always return True so no element is skipped for being outside viewport."""
        return True


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
    """DOM capture helper. Scrolls the full page to trigger lazy-loaded content,
    then captures the complete interactive element map."""

    SCROLL_STEP_PX = 800
    MAX_SCROLLS = 15

    def __init__(self, browser_session):
        self.browser_session = browser_session

    def scroll_and_capture(self) -> Tuple[str, str]:
        """
        Scroll the full page to trigger lazy-loaded content, then capture
        the complete DOM. Returns (selector_map_json, selector_map_string).

        IMPORTANT: After building the parser, we write it back to
        BrowserSession._parser and _selector_map.  This ensures the
        BrowserController reuses the *exact same index space* the LLM
        received — preventing the split-brain where the ActionEngine's
        DOMHelper and the controller each build independent parsers whose
        indices diverge (root cause of "index not in selector_map" errors).
        """
        page = self.browser_session.get_current_page()
        if page is None:
            return ("{}", "")

        try:
            prev_height = 0
            for _ in range(self.MAX_SCROLLS):
                page.mouse.wheel(0, self.SCROLL_STEP_PX)
                page.wait_for_timeout(400)

                current_height = page.evaluate("document.documentElement.scrollHeight")
                scroll_top = page.evaluate("window.scrollY + window.innerHeight")
                if scroll_top >= current_height - 50:
                    break
                if current_height == prev_height:
                    break
                prev_height = current_height

            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(300)

        except Exception:
            pass

        return self._capture_dom()

    def _capture_dom(self) -> Tuple[str, str]:
        """Capture the current DOM as (selector_map_json, selector_map_string).

        Writes the built parser and its derived selector_map back to
        BrowserSession so the controller (click_element_by_index, input_text,
        etc.) always operates on the same index space the LLM just received.
        """
        page = self.browser_session.get_current_page()
        if page is None:
            return ("{}", "")
        try:
            parser = FullPageDOMTreeParser(page)
            parser.parse()

            # ---- Synchronise with BrowserSession ----
            # Store this parser as the session's canonical source of truth so
            # BrowserController.get_selector_map() returns the same indices.
            self.browser_session._parser = parser
            self.browser_session._selector_map = parser.selector_map()

            return (parser.selector_map_json(), parser.get_selector_map_string())
        except Exception:
            return ("{}", "")
