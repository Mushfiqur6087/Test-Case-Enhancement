"""
Sub-state exploration: discovers and captures hidden UI states
(tabs, modals, radios, collapsibles, dropdowns, mode toggles).
Clicks triggers on the current page, captures new DOM if URL unchanged,
goes back immediately if URL changes (only Navigator decides page transitions).
"""

import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, PROJECT_ROOT)

from test_case_enhancer.agent.exploration_agent.models import (
    PageIdentity,
    PageSnapshot,
    SubStateSnapshot,
)
from test_case_enhancer.agent.exploration_agent.prompts import PROMPT_PAGE_EXPLORER_SUBSTATES


class SubStateExplorer:
    """Explores sub-states on a page by interacting with triggers."""

    # Words on buttons that must NEVER be clicked during sub-state exploration
    FORBIDDEN_ACTIONS = {
        "submit", "save", "send", "pay", "delete", "remove",
        "enrol", "enroll", "create", "confirm", "apply",
        "logout", "log out", "sign out", "cancel enrollment",
        "sign in", "log in", "login", "register",
    }

    def __init__(self, llm_client, browser_controller, dom_capture):
        """
        Args:
            llm_client: LLMClient instance
            browser_controller: BrowserController instance
            dom_capture: DOMCaptureHelper instance
        """
        self.llm_client = llm_client
        self.browser_controller = browser_controller
        self.dom_capture = dom_capture

    def explore(
        self,
        page_identity: PageIdentity,
        snapshot: PageSnapshot,
        feature_context: str = "",
    ) -> List[SubStateSnapshot]:
        """
        Main entry point. Identifies and explores all sub-state triggers.

        Args:
            page_identity: Identity of the current page
            snapshot: Base state snapshot
            feature_context: Optional context string about expected features

        Returns:
            List of SubStateSnapshot objects
        """

        # Ask LLM to identify sub-state triggers
        triggers = self._identify_triggers(
            snapshot.selector_map_string,
            snapshot.title,
            snapshot.url,
            feature_context,
        )

        if not triggers:
            return []

        # Record original URL for restoration
        original_url = snapshot.url

        sub_states: List[SubStateSnapshot] = []

        for trigger in triggers:
            element_index = trigger.get("element_index")
            if element_index is None:
                continue

            # Safety check
            if not self._is_safe_trigger(element_index, snapshot.selector_map_json):
                continue

            # Interact with the trigger
            sub_state = self._interact_with_trigger(
                element_index,
                trigger.get("trigger_type", "unknown"),
                trigger.get("description", ""),
                original_url,
            )

            if sub_state:
                sub_states.append(sub_state)

        return sub_states

    def _identify_triggers(
        self,
        selector_map_string: str,
        page_title: str,
        page_url: str,
        feature_context: str,
    ) -> List[Dict[str, Any]]:
        """
        Ask LLM to identify sub-state triggers from interactive elements.
        """
        if not self.llm_client or not selector_map_string:
            return []

        prompt = PROMPT_PAGE_EXPLORER_SUBSTATES.format(
            page_title=page_title,
            page_url=page_url,
            selector_map_string=selector_map_string,
            feature_context=feature_context or "No specific context available.",
        )

        try:
            response = self.llm_client.ask(prompt)
            result = self._parse_json(response)
            return result.get("triggers", [])
        except Exception:
            return []

    def _is_safe_trigger(self, element_index: int, selector_map_json: str) -> bool:
        """
        Safety check: ensure the trigger element is not a submit/delete/logout button.
        """
        try:
            elements = json.loads(selector_map_json)
            elem = elements.get(str(element_index), {})
            inner_text = elem.get("inner_text", "").lower().strip()
            attrs = elem.get("attributes", {})

            # Check inner text against forbidden actions
            for forbidden in self.FORBIDDEN_ACTIONS:
                if forbidden in inner_text:
                    return False

            # Check type attribute
            input_type = attrs.get("type", "").lower()
            if input_type == "submit":
                return False

            # Check value attribute (for input buttons)
            value = attrs.get("value", "").lower()
            for forbidden in self.FORBIDDEN_ACTIONS:
                if forbidden in value:
                    return False

            return True

        except (json.JSONDecodeError, TypeError):
            return False

    def _interact_with_trigger(
        self,
        element_index: int,
        trigger_type: str,
        description: str,
        original_url: str,
    ) -> Optional[SubStateSnapshot]:
        """
        Click/select the trigger, wait for DOM update, capture new state.
        """
        try:
            # Get current URL before clicking
            page = self.browser_controller.browser_context.get_current_page()
            if not page:
                return None
            pre_click_url = page.url

            # Click the element
            success = self.browser_controller.execute_command(
                "click_element", element_index
            )
            if not success:
                return None

            # Brief wait for DOM to update
            page.wait_for_timeout(800)

            # Check if URL changed (would mean this was navigation, not a sub-state)
            post_click_url = page.url
            if self._url_changed_significantly(pre_click_url, post_click_url):
                # This was navigation, not a sub-state trigger. Go back.
                self.browser_controller.execute_command("go_back")
                page.wait_for_timeout(500)
                return None

            # URL unchanged -- this is a valid sub-state. Capture DOM.
            new_map_json, _ = self.dom_capture.get_dom_for_link_extraction()

            # Find new links revealed by this sub-state
            new_links = self._extract_new_links_from_sub_state(
                snapshot.selector_map_json, new_map_json
            )

            sub_state = SubStateSnapshot(
                trigger_description=description,
                trigger_element_index=element_index,
                trigger_type=trigger_type,
                selector_map_json=new_map_json,
                new_links_found=new_links,
            )

            # Try to restore page state
            self._restore_page_state(original_url, trigger_type, element_index)

            return sub_state

        except Exception:
            # On any error, try to get back to the original page
            try:
                self.browser_controller.execute_command("navigate_to", original_url)
            except Exception:
                pass
            return None

    def _url_changed_significantly(self, before: str, after: str) -> bool:
        """Check if the URL changed in a way that indicates page navigation."""
        if before == after:
            return False

        from urllib.parse import urlparse
        parsed_before = urlparse(before)
        parsed_after = urlparse(after)

        # If path changed, it's definitely a navigation
        if parsed_before.path != parsed_after.path:
            return True

        # If query changed significantly, it might be navigation
        if parsed_before.query != parsed_after.query:
            # Minor changes (e.g., adding a hash) are not navigation
            return True

        return False

    def _restore_page_state(
        self, original_url: str, trigger_type: str, element_index: int
    ) -> None:
        """
        Attempt to restore the page to its previous state.
        """
        try:
            page = self.browser_controller.browser_context.get_current_page()
            if not page:
                return

            if trigger_type in ("collapsible", "modal", "mode_toggle"):
                # Click again to toggle back, or press Escape for modals
                if trigger_type == "modal":
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(500)
                else:
                    self.browser_controller.execute_command(
                        "click_element", element_index
                    )
                    page.wait_for_timeout(500)

            elif trigger_type in ("tab", "radio"):
                # Can't easily "undo" a tab/radio selection without knowing the original
                # Just leave it; the base state was already captured
                pass

        except Exception:
            # If restoration fails, re-navigate to the URL
            try:
                self.browser_controller.execute_command("navigate_to", original_url)
            except Exception:
                pass



    def _extract_new_links_from_sub_state(
        self, base_selector_json: str, sub_state_selector_json: str
    ) -> List[str]:
        """
        Compare sub-state selector map against base state to find new links.
        """
        try:
            base_elems = json.loads(base_selector_json)
            sub_elems = json.loads(sub_state_selector_json)
        except (json.JSONDecodeError, TypeError):
            return []

        base_hrefs = set()
        for elem in base_elems.values():
            href = elem.get("attributes", {}).get("href", "")
            if href:
                base_hrefs.add(href)

        new_links = []
        for elem in sub_elems.values():
            href = elem.get("attributes", {}).get("href", "")
            if href and href not in base_hrefs:
                new_links.append(href)

        return new_links

    def _parse_json(self, response: str) -> Dict:
        """Parse JSON from LLM response, handling markdown code blocks."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
