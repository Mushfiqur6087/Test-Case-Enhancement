"""
Page Explorer Agent.
Thoroughly explores the CURRENT page: scrolls to trigger lazy content,
extracts all visible links, then discovers sub-states (tabs, modals,
dropdowns, collapsibles) by interacting with triggers.

Strict rule: NEVER navigate away. If a click changes the URL → go_back().
Returns PageExplorerResult with all links found (visible + sub-state).
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, PROJECT_ROOT)

from test_case_enhancer.agent.core_utils.llm import LLMClient
from test_case_enhancer.agent.exploration_agent.dom_capture import DOMHelper
from test_case_enhancer.agent.exploration_agent.link_extractor import LinkExtractor
from test_case_enhancer.agent.exploration_agent.models import (
    PageExplorerResult,
    PageSnapshot,
    SubStateInfo,
)
from test_case_enhancer.agent.exploration_agent.prompts import (
    PROMPT_PAGE_EXPLORER_SYSTEM,
    PROMPT_PAGE_EXPLORER_SUBSTATES,
)
from test_case_enhancer.agent.exploration_agent.sub_state_explorer import SubStateExplorer
from test_case_enhancer.agent.exploration_agent.page_identity import PageIdentityComputer


class PageExplorer:
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
        self.llm_client = llm_client
        self.browser_controller = browser_controller
        self.browser_session = browser_session
        self.base_url = base_url
        self.debug = debug
        self.debug_file = debug_file

        # Build a dedicated LLM client for page exploration
        self.explorer_llm = LLMClient(
            api_key=llm_client.client.api_key,
            model_name=llm_client.model_name,
            system_prompt=PROMPT_PAGE_EXPLORER_SYSTEM,
            debug_file=debug_file,
        )

        # Components
        self.dom_helper = DOMHelper(browser_session)
        self.page_identity_computer = PageIdentityComputer(base_url)
        self.link_extractor = LinkExtractor(base_url, self.page_identity_computer)
        self.sub_state_explorer = SubStateExplorer(
            llm_client=self.explorer_llm,
            browser_controller=browser_controller,
            dom_capture=self.dom_helper,
        )

        # Track LLM calls made by this agent
        self.llm_call_count = 0

    def explore(self) -> PageExplorerResult:
        """
        Main entry point. Explores the current page and returns all findings.
        Does NOT navigate away from the current page.
        """
        page = self.browser_session.get_current_page()
        if page is None:
            return PageExplorerResult(current_url="", current_title="")

        current_url = page.url
        current_title = self._get_title()
        self._log(f"  [PageExplorer] Exploring: {current_title} ({current_url})")

        # Step 1: Scroll page and capture full DOM
        selector_map_json, selector_map_string = self.dom_helper.scroll_and_capture()

        # Step 2: Extract visible links (no LLM)
        visible_links = self.link_extractor.extract_links(selector_map_json, current_url)
        self._log(f"  [PageExplorer] Found {len(visible_links)} visible links")

        # Step 3: Explore sub-states (LLM identifies triggers, then we interact)
        sub_states_info = self._explore_sub_states(
            current_url, current_title, selector_map_json, selector_map_string
        )

        # Merge sub-state links into a combined list
        all_sub_state_links = []
        for ss in sub_states_info:
            all_sub_state_links.extend(ss.new_links)

        self._log(
            f"  [PageExplorer] Sub-states: {len(sub_states_info)} triggers, "
            f"{len(all_sub_state_links)} new links from sub-states"
        )

        # Step 4: Count interactive elements for metadata
        try:
            elements = json.loads(selector_map_json)
            interactive_count = len(elements)
        except (json.JSONDecodeError, TypeError):
            interactive_count = 0

        # Detect forms
        has_forms = self._detect_forms(selector_map_json)

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

        # Build a PageSnapshot for SubStateExplorer
        snapshot = PageSnapshot(
            url=current_url,
            title=current_title,
            selector_map_json=selector_map_json,
            selector_map_string=selector_map_string,
        )

        # Use PageIdentityComputer to get identity for the current page
        identity = self.page_identity_computer.compute(current_url, "current")

        # Call SubStateExplorer
        try:
            sub_state_snapshots = self.sub_state_explorer.explore(
                page_identity=identity,
                snapshot=snapshot,
                feature_context="Explore all tabs, modals, dropdowns, and collapsible sections.",
            )
            self.llm_call_count += 1  # For the trigger identification call
        except Exception as e:
            self._log(f"  [PageExplorer] Sub-state exploration error: {e}")
            return []

        # Convert SubStateSnapshot → SubStateInfo with resolved links
        results: List[SubStateInfo] = []
        for ss in sub_state_snapshots:
            # Resolve raw hrefs to full URLs
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

    def _get_title(self) -> str:
        """Get current page title safely."""
        try:
            page = self.browser_session.get_current_page()
            return page.title() if page else ""
        except Exception:
            return ""

    def _log(self, message: str) -> None:
        """Log to console and debug file."""
        print(message)
        if self.debug and self.debug_file:
            try:
                with open(self.debug_file, "a", encoding="utf-8") as f:
                    f.write(f"{message}\n")
            except Exception:
                pass
