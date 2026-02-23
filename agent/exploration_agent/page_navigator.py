"""
Page Navigator Agent.
Given a target URL from the Navigator Agent, reads the current page's DOM
and intelligently decides which element(s) to click to reach the target.

For login commands, fills the login form with provided credentials.
Always tries clicking first; falls back to direct URL navigation on retry.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, PROJECT_ROOT)

from test_case_enhancer.agent.core_utils.llm import LLMClient
from test_case_enhancer.agent.exploration_agent.dom_capture import DOMHelper
from test_case_enhancer.agent.exploration_agent.models import (
    NavigatorCommand,
    PageNavigatorResult,
    RoleCredentials,
)
from test_case_enhancer.agent.exploration_agent.prompts import (
    PROMPT_PAGE_NAVIGATOR_SYSTEM,
    PROMPT_PAGE_NAVIGATOR_STEP,
)


class PageNavigator:
    """
    Navigates the browser to a target page by reading the current DOM
    and deciding which element to click. Uses LLM to match target URL
    to the right interactive element.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        browser_controller,
        browser_session,
        debug: bool = False,
        debug_file: str = None,
    ):
        self.browser_controller = browser_controller
        self.browser_session = browser_session
        self.debug = debug
        self.debug_file = debug_file

        # Dedicated LLM client for page navigation
        self.navigator_llm = LLMClient(
            api_key=llm_client.client.api_key,
            model_name=llm_client.model_name,
            system_prompt=PROMPT_PAGE_NAVIGATOR_SYSTEM,
            debug_file=debug_file,
        )

        # DOM helper for reading current page
        self.dom_helper = DOMHelper(browser_session)

        # Track LLM calls
        self.llm_call_count = 0

    def navigate(self, command: NavigatorCommand) -> PageNavigatorResult:
        """
        Main entry point. Navigate to the target specified in the command.

        For explore_page: find and click the right element to reach target_url.
        For login: fill the form with credentials and submit.
        For logout: find and click the logout element.

        Returns PageNavigatorResult with success/failure info.
        """
        self._log(
            f"  [PageNavigator] Command: {command.command_type} → "
            f"{command.target_url} ({command.target_label})"
        )

        if command.command_type == "login":
            return self._handle_login(command)
        elif command.command_type == "logout":
            return self._handle_logout(command)
        else:
            return self._handle_navigation(command)

    def _handle_navigation(self, command: NavigatorCommand) -> PageNavigatorResult:
        """Navigate to a target page by clicking the right element."""
        # Step 1: Read current page DOM
        _, selector_map_string = self.dom_helper.get_dom_for_link_extraction()

        current_url = self._get_current_url()
        current_title = self._get_current_title()

        # Step 2: Ask LLM which element to click
        actions = self._ask_llm_for_actions(
            current_url, current_title, selector_map_string, command
        )

        if not actions:
            # LLM couldn't find the element — retry with direct navigation
            self._log("  [PageNavigator] No actions from LLM. Retrying with direct URL.")
            return self._retry_direct(command)

        # Step 3: Execute the actions
        actions_taken = self._execute_actions(actions)

        # Step 4: Verify we reached the target
        self._wait_for_page()
        new_url = self._get_current_url()
        new_title = self._get_current_title()

        if self._is_target_reached(new_url, command.target_url):
            self._log(f"  [PageNavigator] Reached: {new_title} ({new_url})")
            return PageNavigatorResult(
                success=True,
                current_url=new_url,
                current_title=new_title,
                actions_taken=actions_taken,
            )

        # Step 5: Didn't reach target — retry with direct URL
        self._log(
            f"  [PageNavigator] Landed on {new_url}, expected {command.target_url}. Retrying."
        )
        return self._retry_direct(command)

    def _handle_login(self, command: NavigatorCommand) -> PageNavigatorResult:
        """Handle a login command: navigate to login page, fill form, submit."""
        # First navigate to the login page if we're not already there
        current_url = self._get_current_url()
        login_indicators = ["/login", "/signin", "/sign-in"]

        if not any(ind in current_url.lower() for ind in login_indicators):
            # Navigate to the login page first
            if command.target_url:
                success = self.browser_controller.execute_command(
                    "navigate_to", command.target_url
                )
                if not success:
                    return PageNavigatorResult(
                        success=False,
                        current_url=current_url,
                        failure_reason="Failed to navigate to login page",
                    )
                self._wait_for_page()

        # Now read the login form
        _, selector_map_string = self.dom_helper.get_dom_for_link_extraction()
        current_url = self._get_current_url()
        current_title = self._get_current_title()

        # Build credentials info for the prompt
        creds = command.credentials
        if not creds:
            return PageNavigatorResult(
                success=False,
                current_url=current_url,
                failure_reason="No credentials provided for login command",
            )

        # Ask LLM to fill the login form
        actions = self._ask_llm_for_actions(
            current_url, current_title, selector_map_string, command
        )

        if not actions:
            return PageNavigatorResult(
                success=False,
                current_url=current_url,
                failure_reason="LLM could not identify login form fields",
            )

        # Execute form filling + submit
        actions_taken = self._execute_actions(actions)
        self._wait_for_page()

        new_url = self._get_current_url()
        new_title = self._get_current_title()

        # Check if we left the login page (login success indicator)
        if not any(ind in new_url.lower() for ind in login_indicators):
            self._log(f"  [PageNavigator] Login successful → {new_title} ({new_url})")
            return PageNavigatorResult(
                success=True,
                current_url=new_url,
                current_title=new_title,
                actions_taken=actions_taken,
            )
        else:
            self._log(f"  [PageNavigator] Login may have failed — still on {new_url}")
            return PageNavigatorResult(
                success=False,
                current_url=new_url,
                current_title=new_title,
                failure_reason="Still on login page after form submission — credentials may be wrong",
                actions_taken=actions_taken,
            )

    def _handle_logout(self, command: NavigatorCommand) -> PageNavigatorResult:
        """Handle a logout command: find and click the logout link."""
        _, selector_map_string = self.dom_helper.get_dom_for_link_extraction()
        current_url = self._get_current_url()
        current_title = self._get_current_title()

        # Ask LLM to find the logout element
        logout_command = NavigatorCommand(
            command_type="logout",
            target_url=command.target_url or "/logout",
            target_label="Logout",
        )
        actions = self._ask_llm_for_actions(
            current_url, current_title, selector_map_string, logout_command
        )

        if not actions:
            # Try direct navigation to logout URL
            if command.target_url:
                self.browser_controller.execute_command("navigate_to", command.target_url)
                self._wait_for_page()

        actions_taken = self._execute_actions(actions) if actions else []
        self._wait_for_page()

        new_url = self._get_current_url()
        new_title = self._get_current_title()

        login_indicators = ["/login", "/signin", "/sign-in"]
        logged_out = any(ind in new_url.lower() for ind in login_indicators)

        return PageNavigatorResult(
            success=logged_out,
            current_url=new_url,
            current_title=new_title,
            actions_taken=actions_taken,
            failure_reason="" if logged_out else "Could not confirm logout",
        )

    def _ask_llm_for_actions(
        self,
        current_url: str,
        current_title: str,
        selector_map_string: str,
        command: NavigatorCommand,
    ) -> List[Dict[str, Any]]:
        """Ask the Page Navigator LLM which elements to interact with."""
        # Build credentials info if this is a login command
        credentials_info = ""
        if command.command_type == "login" and command.credentials:
            creds = command.credentials
            credentials_info = (
                f"Credentials to use:\n"
                f"  Username: {creds.username}\n"
                f"  Password: {creds.password}\n"
                f"  Role: {creds.role}"
            )

        prompt = PROMPT_PAGE_NAVIGATOR_STEP.format(
            current_url=current_url,
            current_title=current_title,
            selector_map_string=selector_map_string[:4000] if selector_map_string else "(empty page)",
            command_type=command.command_type,
            target_url=command.target_url,
            target_label=command.target_label or command.target_url,
            credentials_info=credentials_info,
        )

        try:
            response = self.navigator_llm.ask(prompt)
            self.llm_call_count += 1
            data = self._parse_json(response)
            return data.get("actions", [])
        except Exception as e:
            self._log(f"  [PageNavigator] LLM error: {e}")
            self.llm_call_count += 1
            return []

    def _execute_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a list of browser actions. Returns the actions attempted."""
        actions_taken = []
        for action in actions:
            if not isinstance(action, dict) or len(action) != 1:
                continue

            action_name = list(action.keys())[0]
            action_params = action[action_name]

            try:
                if action_name == "click_element":
                    idx = action_params.get("index")
                    if idx is not None:
                        self.browser_controller.execute_command("click_element", int(idx))
                        self._wait_for_page()
                        actions_taken.append(action)

                elif action_name == "input_text":
                    idx = action_params.get("index")
                    text = action_params.get("text", "")
                    if idx is not None:
                        self.browser_controller.execute_command("input_text", int(idx), text)
                        actions_taken.append(action)

                elif action_name == "scroll_down":
                    amount = action_params.get("amount", 500)
                    self.browser_controller.execute_command("scroll_down", int(amount))
                    actions_taken.append(action)

            except Exception as e:
                self._log(f"  [PageNavigator] Action {action_name} failed: {e}")

        return actions_taken

    def _retry_direct(self, command: NavigatorCommand) -> PageNavigatorResult:
        """Retry navigation using direct URL as fallback."""
        if not command.target_url:
            return PageNavigatorResult(
                success=False,
                current_url=self._get_current_url(),
                failure_reason="No target URL to retry with",
                retry_attempted=True,
            )

        self._log(f"  [PageNavigator] Retry: direct navigate_to({command.target_url})")
        success = self.browser_controller.execute_command("navigate_to", command.target_url)
        self._wait_for_page()

        new_url = self._get_current_url()
        new_title = self._get_current_title()

        if success and self._is_target_reached(new_url, command.target_url):
            return PageNavigatorResult(
                success=True,
                current_url=new_url,
                current_title=new_title,
                actions_taken=[{"navigate_to": {"url": command.target_url}}],
                retry_attempted=True,
            )

        return PageNavigatorResult(
            success=False,
            current_url=new_url,
            current_title=new_title,
            failure_reason=f"Could not reach {command.target_url}. Landed on {new_url} instead.",
            retry_attempted=True,
        )

    def _is_target_reached(self, current_url: str, target_url: str) -> bool:
        """Check if current URL matches the target (path-level match)."""
        from urllib.parse import urlparse

        try:
            current_path = urlparse(current_url).path.rstrip("/") or "/"
            target_path = urlparse(target_url).path.rstrip("/") or "/"
            return current_path == target_path
        except Exception:
            return current_url == target_url

    def _wait_for_page(self) -> None:
        """Wait for page to stabilize after navigation."""
        try:
            page = self.browser_session.get_current_page()
            if page:
                page.wait_for_timeout(1000)
                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass
        except Exception:
            pass

    def _get_current_url(self) -> str:
        try:
            page = self.browser_session.get_current_page()
            return page.url if page else ""
        except Exception:
            return ""

    def _get_current_title(self) -> str:
        try:
            page = self.browser_session.get_current_page()
            return page.title() if page else ""
        except Exception:
            return ""

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

    def _log(self, message: str) -> None:
        """Log to console and debug file."""
        print(message)
        if self.debug and self.debug_file:
            try:
                with open(self.debug_file, "a", encoding="utf-8") as f:
                    f.write(f"{message}\n")
            except Exception:
                pass
