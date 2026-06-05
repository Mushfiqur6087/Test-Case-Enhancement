"""Playwright browser session manager."""

import base64
from typing import Optional, List, Dict, Any
from playwright.sync_api import Page, BrowserContext, sync_playwright, Browser

from test_case_enhancement.browser.dom_parser import DOMTreeParser, DOMElementNode
from test_case_enhancement.browser.dom_helper import FullPageDOMTreeParser


class BrowserSession:
    """Simple browser session manager using Playwright."""

    def __init__(self):
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._current_page: Optional[Page] = None
        self._tabs: List[Page] = []

        self._parser: Optional[DOMTreeParser] = None
        self._selector_map: Optional[Dict[int, DOMElementNode]] = None

        self._recent_alerts: List[Dict[str, Any]] = []
        self._max_alert_history: int = 2

    def _initialize_session(self, headless: bool = False) -> Browser:
        if self._playwright is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=headless)
        return self._browser

    def _create_context(self) -> BrowserContext:
        if self._browser is None:
            self._initialize_session()
        self._context = self._browser.new_context()
        # Listen for new tabs/popups opened by the page (target="_blank", window.open)
        self._context.on("page", self._on_new_page_opened)
        return self._context

    def _on_new_page_opened(self, page: Page) -> None:
        """Called by Playwright whenever a new tab/popup is opened in the context.

        Tracks the new tab so the agent can see it and decide what to do.
        Does NOT auto-close — the LLM decides whether to keep or close it.

        Note: Playwright fires this event when the page object is *created* —
        i.e. before it has navigated anywhere. The URL is therefore 'about:blank'
        at this point. We wait a short time for the tab to navigate so the
        logged URL is meaningful.
        """
        if page not in self._tabs:
            self._tabs.append(page)
            page.once("close", lambda _: self._on_close(page))
            self._setup_alert_handlers(page)

        # Wait briefly for the new tab to navigate past about:blank so the
        # logged URL reflects the real destination (not the creation URL).
        resolved_url = self._resolve_tab_url(page)

        # Suppress the misleading startup message: the very first page opened
        # in a fresh context is always about:blank (it's our working tab, not
        # a genuine popup). Only log when it's a real secondary tab.
        if len(self._tabs) > 1 or resolved_url not in ("about:blank", ""):
            print(
                f"  [TabGuard] New tab detected: {resolved_url} "
                f"(total tabs: {len(self._tabs)})"
            )

    def _resolve_tab_url(self, page: Page, timeout_ms: int = 3000) -> str:
        """Return the page's current URL, waiting briefly for it to navigate
        past 'about:blank' (which is the initial URL for every new page object
        before Playwright loads any content into it).

        Parameters
        ----------
        page       : the Playwright Page to inspect
        timeout_ms : maximum time (ms) to wait for a real URL
        """
        try:
            # Fast path: already at a real URL
            url = page.url
            if url and url not in ("about:blank", ""):
                return url

            # Slow path: wait for the page to navigate away from about:blank
            try:
                page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            except Exception:
                pass

            url = page.url
            return url if url else "about:blank"
        except Exception:
            return "about:blank"

    def get_session(self) -> dict:
        return {
            "playwright": self._playwright,
            "browser": self._browser,
            "context": self._context,
            "current_page": self._current_page,
            "tab_count": len(self._tabs),
        }

    def get_current_page(self) -> Optional[Page]:
        if self._current_page:
            return self._current_page
        if self._context:
            pages = self._context.pages
            if pages:
                self._tabs = pages.copy()
                self._current_page = self._tabs[0]
                return self._current_page
        self._create_context()
        return self.create_new_page()

    def create_new_page(self) -> Page:
        """Create a new browser page and make it the current tab.

        Note: calling self._context.new_page() fires the context-level 'page'
        event synchronously, which triggers _on_new_page_opened(). That handler
        already appends the page to self._tabs and registers close/alert handlers.
        We must NOT duplicate those calls here — doing so creates ghost duplicate
        entries in self._tabs, causing both 'both ACTIVE' display bugs and empty
        selector maps after tab operations.
        """
        if self._context is None:
            self._create_context()
        page = self._context.new_page()
        # _on_new_page_opened has already appended page to _tabs and registered
        # handlers. Only set the active page pointer here.
        self._current_page = page
        # Safety guard: if somehow _on_new_page_opened didn't run (edge case),
        # ensure the page is tracked and handlers are wired.
        if page not in self._tabs:
            self._tabs.append(page)
            page.once("close", lambda _: self._on_close(page))
            self._setup_alert_handlers(page)
        return page

    def _on_close(self, page: Page):
        """Called when a tracked page is closed. Remove it from _tabs and
        update _current_page if needed. Uses identity check (is) to avoid
        false matches from __eq__ on Playwright Page objects."""
        if page in self._tabs:
            self._tabs.remove(page)
        if self._current_page is page:
            self._current_page = self._tabs[0] if self._tabs else None

    def navigate_to(self, url: str) -> None:
        page = self.get_current_page()
        page.goto(url)
        self._parser = None
        self._selector_map = None

    def refresh_page(self) -> None:
        page = self.get_current_page()
        if page:
            page.reload()
            self._parser = None
            self._selector_map = None

    def go_back(self) -> None:
        page = self.get_current_page()
        if page:
            page.go_back()
            self._parser = None
            self._selector_map = None

    def go_forward(self) -> None:
        page = self.get_current_page()
        if page:
            page.go_forward()
            self._parser = None
            self._selector_map = None

    def get_tabs_info(self) -> List[Dict[str, Any]]:
        """Return metadata for every tracked tab.

        For tabs whose URL is still 'about:blank' (page created but not yet
        navigated), we wait briefly so callers get the real destination URL
        rather than the creation-time placeholder.
        """
        infos = []
        for idx, page in enumerate(self._tabs):
            try:
                url = self._resolve_tab_url(page)
                try:
                    title = page.title()
                except Exception:
                    title = "Unknown"
                infos.append({
                    "page_id": idx,
                    "url": url,
                    "title": title,
                    "is_current": page is self._current_page
                })
            except Exception:
                infos.append({
                    "page_id": idx,
                    "url": "about:blank",
                    "title": "Unknown",
                    "is_current": False
                })
        return infos

    def switch_to_tab(self, page_id: int) -> bool:
        if 0 <= page_id < len(self._tabs):
            self._current_page = self._tabs[page_id]
            self._parser = None
            self._selector_map = None
            return True
        return False

    def create_new_tab(self, url: Optional[str] = None) -> Dict[str, Any]:
        page = self.create_new_page()
        if url:
            page.goto(url)
        self._parser = None
        self._selector_map = None
        return {
            "page_id": len(self._tabs) - 1,
            "url": page.url,
            "title": page.title() if url else "New Tab",
            "is_current": True
        }

    def close_tab(self, page_id: int) -> bool:
        if 0 <= page_id < len(self._tabs):
            page = self._tabs[page_id]
            if page is self._current_page:
                if len(self._tabs) > 1:
                    self._current_page = self._tabs[1] if page_id == 0 else self._tabs[0]
                else:
                    self._current_page = None
            self._tabs.remove(page)
            page.close()
            self._parser = None
            self._selector_map = None
            return True
        return False

    # ---- Multi-tab context for LLM prompts ----

    def get_tab_context_string(self) -> str:
        """Build a compact tab summary for injection into LLM prompts.

        Returns an empty string when there is only one tab (no noise for
        the normal case). When multiple tabs are open, returns a block like:

            ## Browser Tabs (2 open)
            Tab 0 (ACTIVE): Swag Labs — https://www.saucedemo.com/inventory.html
            Tab 1:          Facebook — https://www.facebook.com/saucelabs

        URLs are resolved via _resolve_tab_url() so background tabs that are
        still loading past about:blank show their real destination URL instead
        of the transient creation-time placeholder.
        """
        if len(self._tabs) <= 1:
            return ""

        lines = [f"## Browser Tabs ({len(self._tabs)} open)"]
        for idx, page in enumerate(self._tabs):
            # Use resolved URL so we never send 'about:blank' for a tab
            # that has already navigated to a real page.
            url = self._resolve_tab_url(page)
            try:
                title = page.title()
            except Exception:
                title = "Unknown"
            marker = " (ACTIVE)" if page is self._current_page else ""
            lines.append(f"Tab {idx}{marker}: {title} — {url}")

        lines.append("")
        lines.append(
            "IMPORTANT: If any tab is NOT relevant to your current goal "
            "(e.g., external social media page), close it with close_tab "
            "and switch back to your working tab with switch_to_tab before "
            "continuing."
        )
        return "\n".join(lines)

    def capture_all_tabs_screenshots(self) -> List[Dict[str, Any]]:
        """Capture a screenshot from every open tab.

        Returns a list of dicts:
          [{"tab_index": 0, "url": "...", "title": "...", "screenshot_b64": "...", "is_active": True}, ...]

        Tabs that fail to screenshot are included with screenshot_b64=None.
        """
        results = []
        for idx, page in enumerate(self._tabs):
            entry: Dict[str, Any] = {
                "tab_index": idx,
                "is_active": page is self._current_page,
            }
            try:
                entry["url"] = page.url
                entry["title"] = page.title()
            except Exception:
                entry["url"] = "about:blank"
                entry["title"] = "Unknown"

            try:
                png_bytes: bytes = page.screenshot(full_page=True)
                entry["screenshot_b64"] = base64.b64encode(png_bytes).decode("utf-8")
            except Exception:
                entry["screenshot_b64"] = None

            results.append(entry)
        return results

    def get_element_tree(self, refresh: bool = True) -> Optional[DOMElementNode]:
        """Returns the root DOMElementNode."""
        page = self.get_current_page()
        if page is None:
            return None

        if self._parser is None or refresh:
            self._parser = FullPageDOMTreeParser(page)
            try:
                self._parser.parse()
            except Exception:
                self._parser = None
                return None

        return self._parser.dom_tree

    def get_selector_map(self, refresh: bool = True) -> Optional[Dict[int, DOMElementNode]]:
        """Returns a flat map of interactive elements.

        When DOMHelper.scroll_and_capture() has just run, it writes both
        self._parser and self._selector_map to the session.  In that case
        we return the pre-built map directly, even when refresh=True, to
        guarantee the controller operates on the *exact same index space*
        that the LLM received.  Rebuilding a fresh parser here would assign
        new indices and cause 'index not in selector_map' failures.
        """
        # Fast-path: the DOMHelper just synced a fresh map — reuse it.
        if self._selector_map is not None:
            return self._selector_map

        # No cached map: build one from the existing parser, or parse fresh.
        parser = self._parser if self._parser else None
        if parser is None:
            root = self.get_element_tree(refresh=refresh)
            if root is None or self._parser is None:
                return None
            parser = self._parser

        try:
            self._selector_map = parser.selector_map()
            return self._selector_map
        except Exception:
            return None

    def get_selector_map_string(self, refresh: bool = True) -> str:
        """Returns a human-readable string of interactive elements."""
        if self._parser is None:
            self.get_element_tree(refresh=refresh)
        if not self._parser:
            return ""
        try:
            return self._parser.get_selector_map_string()
        except Exception:
            return ""

    def get_selector_map_json(self, refresh: bool = True) -> str:
        """Returns a JSON string of interactive elements."""
        if self._parser is None:
            self.get_element_tree(refresh=refresh)
        if not self._parser:
            return "{}"
        try:
            return self._parser.selector_map_json()
        except Exception:
            return "{}"

    def get_element_tree_string(self, refresh: bool = True) -> str:
        """Returns a human-readable string of the element tree."""
        if self._parser is None:
            self.get_element_tree(refresh=refresh)
        if not self._parser:
            return ""
        try:
            return self._parser.get_dom_string()
        except Exception:
            return ""

    def close(self) -> None:
        self._tabs.clear()
        self._parser = None
        self._selector_map = None
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        self._browser = None
        self._context = None
        self._current_page = None
        self._playwright = None

    def _track_alert(self, message: str, alert_type: str = "info") -> None:
        if len(self._recent_alerts) >= self._max_alert_history:
            self._recent_alerts.pop(0)
        self._recent_alerts.append({
            "message": message,
            "type": alert_type
        })

    def get_recent_alerts(self) -> List[Dict[str, Any]]:
        return self._recent_alerts

    def clear_alerts(self) -> None:
        self._recent_alerts.clear()

    def _setup_alert_handlers(self, page: Page) -> None:
        def handle_alert(dialog):
            try:
                message = dialog.message
                dialog_type = dialog.type
                self._track_alert(message, dialog_type)
                if dialog_type in ['alert', 'confirm']:
                    dialog.accept()
                elif dialog_type == 'prompt':
                    dialog.accept("")
                else:
                    dialog.accept()
            except Exception:
                try:
                    dialog.accept()
                except:
                    pass

        page.on("dialog", handle_alert)

    def get_formatted_alerts_for_llm(self) -> str:
        if not self._recent_alerts:
            return ""
        alert_lines = ["Recent Browser Alerts:"]
        for i, alert in enumerate(self._recent_alerts, 1):
            alert_lines.append(f"{i}. [{alert['type'].upper()}] {alert['message']}")
        return "\n".join(alert_lines)

    def has_recent_alerts(self) -> bool:
        return len(self._recent_alerts) > 0
