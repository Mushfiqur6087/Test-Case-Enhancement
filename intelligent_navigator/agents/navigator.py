"""
Navigator Agent (Tactical).
Given a target URL from the Orchestrator, reads the current page's DOM
and intelligently decides which element(s) to click to reach the target.

For login commands, fills the login form with provided credentials.
Always tries clicking first; falls back to direct URL navigation on retry.
"""

from typing import Any, Dict, List
from urllib.parse import urlparse

from intelligent_navigator.core.llm import LLMClient
from intelligent_navigator.core.models import (
    NavigatorCommand,
    PageNavigatorResult,
)
from intelligent_navigator.core.utils import (
    parse_llm_json, log, wait_for_page,
    get_current_url, get_current_title,
)
from intelligent_navigator.browser.dom_helper import DOMHelper
from intelligent_navigator.agents.prompts import (
    PROMPT_PAGE_NAVIGATOR_SYSTEM,
    PROMPT_PAGE_NAVIGATOR_STEP,
)


class Navigator:
    """
    Navigates the browser to a target page by reading the current DOM
    and deciding which element to click.
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

        self.navigator_llm = LLMClient(
            api_key=llm_client.client.api_key,
            model_name=llm_client.model_name,
            system_prompt=PROMPT_PAGE_NAVIGATOR_SYSTEM,
            debug_file=debug_file,
        )

        self.dom_helper = DOMHelper(browser_session)
        self.llm_call_count = 0

    def navigate(self, command: NavigatorCommand) -> PageNavigatorResult:
        """Main entry point. Navigate to the target specified in the command."""
        log(
            f"  [Navigator] Command: {command.command_type} -> "
            f"{command.target_url} ({command.target_label})",
            self.debug, self.debug_file
        )

        if command.command_type == "login":
            return self._handle_login(command)
        elif command.command_type == "logout":
            return self._handle_logout(command)
        else:
            return self._handle_navigation(command)

    def _dismiss_overlays(self) -> None:
        """Press Escape to dismiss any open overlay (Radix dropdown, dialog, etc.)."""
        try:
            page = self.browser_session.get_current_page()
            if page:
                page.keyboard.press("Escape")
                page.wait_for_timeout(200)
        except Exception:
            pass

    def _handle_navigation(self, command: NavigatorCommand) -> PageNavigatorResult:
        """Navigate to a target page by clicking the right element."""
        self._dismiss_overlays()
        _, selector_map_string = self.dom_helper.scroll_and_capture()

        current_url = get_current_url(self.browser_session)
        current_title = get_current_title(self.browser_session)

        actions = self._ask_llm_for_actions(
            current_url, current_title, selector_map_string, command
        )

        if not actions:
            log("  [Navigator] No actions from LLM. Retrying with direct URL.", self.debug, self.debug_file)
            return self._retry_direct(command)

        actions_taken = self._execute_actions(actions)

        wait_for_page(self.browser_session)
        new_url = get_current_url(self.browser_session)
        new_title = get_current_title(self.browser_session)

        if self._is_target_reached(new_url, command.target_url):
            log(f"  [Navigator] Reached: {new_title} ({new_url})", self.debug, self.debug_file)
            return PageNavigatorResult(
                success=True,
                current_url=new_url,
                current_title=new_title,
                actions_taken=actions_taken,
            )

        log(
            f"  [Navigator] Landed on {new_url}, expected {command.target_url}. Retrying.",
            self.debug, self.debug_file
        )
        return self._retry_direct(command)

    def _handle_login(self, command: NavigatorCommand) -> PageNavigatorResult:
        """Handle a login command: navigate to login page, fill form, submit."""
        self._dismiss_overlays()
        current_url = get_current_url(self.browser_session)
        login_indicators = ["/login", "/signin", "/sign-in"]

        if not any(ind in current_url.lower() for ind in login_indicators):
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
                wait_for_page(self.browser_session)

        _, selector_map_string = self.dom_helper.scroll_and_capture()
        current_url = get_current_url(self.browser_session)
        current_title = get_current_title(self.browser_session)

        creds = command.credentials
        if not creds:
            return PageNavigatorResult(
                success=False,
                current_url=current_url,
                failure_reason="No credentials provided for login command",
            )

        actions = self._ask_llm_for_actions(
            current_url, current_title, selector_map_string, command
        )

        if not actions:
            return PageNavigatorResult(
                success=False,
                current_url=current_url,
                failure_reason="LLM could not identify login form fields",
            )

        actions_taken = self._execute_actions(actions)
        wait_for_page(self.browser_session)

        new_url = get_current_url(self.browser_session)
        new_title = get_current_title(self.browser_session)

        if not any(ind in new_url.lower() for ind in login_indicators):
            log(f"  [Navigator] Login successful -> {new_title} ({new_url})", self.debug, self.debug_file)
            return PageNavigatorResult(
                success=True,
                current_url=new_url,
                current_title=new_title,
                actions_taken=actions_taken,
            )
        else:
            log(f"  [Navigator] Login may have failed -- still on {new_url}", self.debug, self.debug_file)
            return PageNavigatorResult(
                success=False,
                current_url=new_url,
                current_title=new_title,
                failure_reason="Still on login page after form submission",
                actions_taken=actions_taken,
            )

    def _handle_logout(self, command: NavigatorCommand) -> PageNavigatorResult:
        """Handle a logout command: find and click the logout link."""
        self._dismiss_overlays()
        _, selector_map_string = self.dom_helper.scroll_and_capture()
        current_url = get_current_url(self.browser_session)
        current_title = get_current_title(self.browser_session)

        logout_command = NavigatorCommand(
            command_type="logout",
            target_url=command.target_url or "/logout",
            target_label="Logout",
        )
        actions = self._ask_llm_for_actions(
            current_url, current_title, selector_map_string, logout_command
        )

        if not actions:
            # Try navigating to a logout/login URL as fallback
            fallback_url = command.target_url or "/login"
            self.browser_controller.execute_command("navigate_to", fallback_url)
            wait_for_page(self.browser_session)

        actions_taken = self._execute_actions(actions) if actions else []
        wait_for_page(self.browser_session)

        new_url = get_current_url(self.browser_session)
        new_title = get_current_title(self.browser_session)

        login_indicators = ["/login", "/signin", "/sign-in", "/register"]
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
        """Ask the Navigator LLM which elements to interact with."""
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
            selector_map_string=selector_map_string[:12000] if selector_map_string else "(empty page)",
            command_type=command.command_type,
            target_url=command.target_url,
            target_label=command.target_label or command.target_url,
            credentials_info=credentials_info,
        )

        try:
            response = self.navigator_llm.ask(prompt)
            self.llm_call_count += 1
            data = parse_llm_json(response)
            return data.get("actions", [])
        except Exception as e:
            log(f"  [Navigator] LLM error: {e}", self.debug, self.debug_file)
            self.llm_call_count += 1
            return []

    def _execute_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a list of browser actions."""
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
                        wait_for_page(self.browser_session)
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
                log(f"  [Navigator] Action {action_name} failed: {e}", self.debug, self.debug_file)

        return actions_taken

    def _retry_direct(self, command: NavigatorCommand) -> PageNavigatorResult:
        """Retry navigation using direct URL as fallback."""
        if not command.target_url:
            return PageNavigatorResult(
                success=False,
                current_url=get_current_url(self.browser_session),
                failure_reason="No target URL to retry with",
                retry_attempted=True,
            )

        log(f"  [Navigator] Retry: direct navigate_to({command.target_url})", self.debug, self.debug_file)
        success = self.browser_controller.execute_command("navigate_to", command.target_url)
        wait_for_page(self.browser_session)

        new_url = get_current_url(self.browser_session)
        new_title = get_current_title(self.browser_session)

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
        try:
            current_path = urlparse(current_url).path.rstrip("/") or "/"
            target_path = urlparse(target_url).path.rstrip("/") or "/"
            return current_path == target_path
        except Exception:
            return current_url == target_url
