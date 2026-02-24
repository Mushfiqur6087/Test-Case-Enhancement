"""
Explorer Agent.
Thoroughly explores the CURRENT page: scrolls to trigger lazy content,
extracts all visible links, then discovers sub-states (tabs, modals,
dropdowns, collapsibles) by interacting with triggers.

Strict rule: NEVER navigate away. If a click changes the URL -> go_back().
Returns PageExplorerResult with all links found (visible + sub-state).
"""

import json
from typing import Any, Dict, List
from urllib.parse import urlparse

from intelligent_navigator.core.llm import LLMClient
from intelligent_navigator.core.models import (
    PageExplorerResult,
    PageSnapshot,
    SubStateInfo,
)
from intelligent_navigator.core.utils import log, get_current_title, parse_llm_json
from intelligent_navigator.browser.dom_helper import DOMHelper
from intelligent_navigator.exploration.link_extractor import LinkExtractor
from intelligent_navigator.exploration.page_identity import PageIdentityComputer
from intelligent_navigator.agents.prompts import PROMPT_PAGE_EXPLORER_SYSTEM, PROMPT_PAGE_AUTH_CLASSIFY
from intelligent_navigator.agents.sub_state import SubStateExplorer


class Explorer:
    """
    Explores the current page in-depth to extract every possible link.
    1. Scroll & capture full DOM
    2. Extract visible links (pure DOM, no LLM)
    3. Ask LLM to identify sub-state triggers (tabs, modals, etc.)
    4. Click each trigger (via SubStateExplorer), capture new links
    5. Return all links + sub-state info
    """

    def __init__(
        self,
        llm_client: LLMClient,
        browser_controller,
        browser_session,
        base_url: str,
        debug: bool = False,
        debug_file: str = None,
    ):
        self.browser_controller = browser_controller
        self.browser_session = browser_session
        self.base_url = base_url
        self.debug = debug
        self.debug_file = debug_file

        self.explorer_llm = LLMClient(
            api_key=llm_client.client.api_key,
            model_name=llm_client.model_name,
            system_prompt=PROMPT_PAGE_EXPLORER_SYSTEM,
            debug_file=debug_file,
        )

        self.dom_helper = DOMHelper(browser_session)
        self.page_identity_computer = PageIdentityComputer(base_url)
        self.link_extractor = LinkExtractor(base_url, self.page_identity_computer)
        self.sub_state_explorer = SubStateExplorer(
            llm_client=self.explorer_llm,
            browser_controller=browser_controller,
            dom_capture=self.dom_helper,
        )

        self.llm_call_count = 0

    def explore(self) -> PageExplorerResult:
        """Main entry point. Explores the current page and returns all findings."""
        page = self.browser_session.get_current_page()
        if page is None:
            return PageExplorerResult(current_url="", current_title="")

        current_url = page.url
        current_title = get_current_title(self.browser_session)
        log(f"  [Explorer] Exploring: {current_title} ({current_url})", self.debug, self.debug_file)

        selector_map_json, selector_map_string = self.dom_helper.scroll_and_capture()

        visible_links = self.link_extractor.extract_links(selector_map_json, current_url)
        log(f"  [Explorer] Found {len(visible_links)} visible links", self.debug, self.debug_file)

        sub_states_info = self._explore_sub_states(
            current_url, current_title, selector_map_json, selector_map_string
        )

        all_sub_state_links = []
        for ss in sub_states_info:
            all_sub_state_links.extend(ss.new_links)

        log(
            f"  [Explorer] Sub-states: {len(sub_states_info)} triggers, "
            f"{len(all_sub_state_links)} new links from sub-states",
            self.debug, self.debug_file
        )

        try:
            elements = json.loads(selector_map_json)
            interactive_count = len(elements)
        except (json.JSONDecodeError, TypeError):
            interactive_count = 0

        has_forms = self._detect_forms(selector_map_json)

        # Classify page as public or auth-required via LLM
        requires_auth = self._classify_page_auth(current_url, current_title, selector_map_string)

        return PageExplorerResult(
            current_url=current_url,
            current_title=current_title,
            links_found=visible_links,
            sub_states_found=sub_states_info,
            page_metadata={
                "interactive_element_count": interactive_count,
                "has_forms": has_forms,
                "sub_state_count": len(sub_states_info),
            },
            page_requires_auth=requires_auth,
        )

    def _explore_sub_states(
        self,
        current_url: str,
        current_title: str,
        selector_map_json: str,
        selector_map_string: str,
    ) -> List[SubStateInfo]:
        """Use LLM + SubStateExplorer to find and interact with sub-state triggers."""
        if not selector_map_string:
            return []

        snapshot = PageSnapshot(
            url=current_url,
            title=current_title,
            selector_map_json=selector_map_json,
            selector_map_string=selector_map_string,
        )

        identity = self.page_identity_computer.compute(current_url, "current")

        try:
            sub_state_snapshots = self.sub_state_explorer.explore(
                page_identity=identity,
                snapshot=snapshot,
                feature_context="Explore all tabs, modals, dropdowns, and collapsible sections.",
            )
            self.llm_call_count += 1
        except Exception as e:
            log(f"  [Explorer] Sub-state exploration error: {e}", self.debug, self.debug_file)
            return []

        results: List[SubStateInfo] = []
        for ss in sub_state_snapshots:
            resolved_links = []
            for href in ss.new_links_found:
                resolved_url = self.page_identity_computer.resolve_url(href, current_url)
                if not self.page_identity_computer.is_external(resolved_url):
                    resolved_links.append({
                        "url": resolved_url,
                        "label": f"(from {ss.trigger_description})",
                        "source": f"sub-state:{ss.trigger_type}",
                    })

            results.append(SubStateInfo(
                trigger_description=ss.trigger_description,
                trigger_type=ss.trigger_type,
                new_links=resolved_links,
            ))

        return results

    def _detect_forms(self, selector_map_json: str) -> bool:
        """Check if the page has any form-related elements."""
        try:
            elements = json.loads(selector_map_json)
            for elem in elements.values():
                tag = elem.get("tag_name", "")
                attrs = elem.get("attributes", {})
                if tag in ("form", "input", "textarea", "select"):
                    return True
                if attrs.get("type") in ("text", "password", "email", "submit"):
                    return True
        except (json.JSONDecodeError, TypeError):
            pass
        return False

    def _classify_page_auth(self, current_url: str, current_title: str, selector_map_string: str) -> bool:
        """Ask LLM whether this page requires authentication. Returns True if auth required."""
        if not selector_map_string:
            return True  # Conservative default

        # Heuristic: well-known public URL paths never need an LLM call
        _PUBLIC_PATH_PATTERNS = (
            "/login", "/signin", "/sign-in",
            "/register", "/signup", "/sign-up",
            "/forgot-password", "/reset-password",
        )
        parsed_path = urlparse(current_url).path.rstrip("/").lower()
        if any(parsed_path == p or parsed_path.endswith(p) for p in _PUBLIC_PATH_PATTERNS):
            log(f"  [Explorer] Page auth classification: requires_auth=False (heuristic URL match)", self.debug, self.debug_file)
            return False

        # Truncate to keep this call cheap
        prompt = PROMPT_PAGE_AUTH_CLASSIFY.format(
            page_url=current_url,
            page_title=current_title,
            selector_map_string=selector_map_string[:3000],
        )

        try:
            response = self.explorer_llm.ask(prompt)
            self.llm_call_count += 1
            data = parse_llm_json(response)
            result = data.get("requires_auth", True)
            log(f"  [Explorer] Page auth classification: requires_auth={result}", self.debug, self.debug_file)
            return bool(result)
        except Exception as e:
            log(f"  [Explorer] Auth classification error: {e}", self.debug, self.debug_file)
            self.llm_call_count += 1
            return True  # Conservative default
