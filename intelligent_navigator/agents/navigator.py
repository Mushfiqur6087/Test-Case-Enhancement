"""
Navigator Agent (Tactical).
Given a target URL from the SpecVerifier, reads the current page's DOM
and intelligently decides which element(s) to click to reach the target.

Supports multi-step navigation: the Navigator runs a loop of up to
MAX_NAVIGATION_STEPS LLM calls, each time recapturing the DOM and
including step history for route planning.

For login commands, fills the login form with provided credentials.
Falls back to direct URL navigation only after exhausting the multi-step loop.
"""

from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from intelligent_navigator.core.llm import LLMClient
from intelligent_navigator.core.models import (
    NavigatorCommand,
    NavigationStepRecord,
    PageNavigatorResult,
)
from intelligent_navigator.core.utils import (
    parse_llm_json, log, wait_for_page,
    get_current_url, get_current_title,
)
from intelligent_navigator.browser.dom_helper import DOMHelper
from intelligent_navigator.browser.selector_filter import SelectorMapFilter
from intelligent_navigator.agents.prompts import (
    PROMPT_PAGE_NAVIGATOR_SYSTEM,
    PROMPT_PAGE_NAVIGATOR_STEP,
)

MAX_NAVIGATION_STEPS = 5


class Navigator:
    """
    Navigates the browser to a target page by reading the current DOM
    and deciding which element to click. Supports multi-step navigation
    with graph-aware route planning.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        browser_controller,
        browser_session,
        debug: bool = False,
        debug_file: str = None,
        selector_filter: SelectorMapFilter = None,
    ):
        self.browser_controller = browser_controller
        self.browser_session = browser_session
        self.debug = debug
        self.debug_file = debug_file
        self.selector_filter = selector_filter

        self.navigator_llm = LLMClient(
            api_key=llm_client.api_key,
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

    # ================================================================
    # Multi-Step Navigation Loop
    # ================================================================

    def _handle_navigation(self, command: NavigatorCommand) -> PageNavigatorResult:
        """Navigate to a target page using a multi-step approach."""

        # --- Try direct URL first (fast path, 0 LLM calls) ---
        direct_result = self._try_direct_url(command)
        if direct_result is not None:
            return direct_result

        # --- Multi-step LLM navigation loop ---
        all_actions_taken: List[Dict[str, Any]] = []
        step_history: List[NavigationStepRecord] = []

        for step_num in range(1, MAX_NAVIGATION_STEPS + 1):
            log(
                f"  [Navigator] Step {step_num}/{MAX_NAVIGATION_STEPS}",
                self.debug, self.debug_file
            )

            # 1. Dismiss overlays and capture the DOM
            self._dismiss_overlays()
            selector_map_json, selector_map_string = self.dom_helper.scroll_and_capture()
            selector_map_string = self._filter_selector_map(
                selector_map_json, selector_map_string
            )

            current_url = get_current_url(self.browser_session)
            current_title = get_current_title(self.browser_session)

            # 2. Check if we already reached the target (from a previous step)
            if step_num > 1 and self._is_target_reached(current_url, command.target_url):
                log(
                    f"  [Navigator] Reached target: {current_title} ({current_url})",
                    self.debug, self.debug_file
                )
                return PageNavigatorResult(
                    success=True,
                    current_url=current_url,
                    current_title=current_title,
                    actions_taken=all_actions_taken,
                    navigation_steps=step_num - 1,
                )

            # 3. Build history and context, ask LLM
            history_string = self._format_step_history(step_history)
            actions, return_to_orch, reasoning = self._ask_llm_for_actions(
                current_url, current_title, selector_map_string, command,
                step_number=step_num,
                step_history=history_string,
            )

            # 4. Handle return_to_orchestrator signal
            if return_to_orch:
                log(
                    f"  [Navigator] LLM signaled return_to_orchestrator: {reasoning}",
                    self.debug, self.debug_file
                )
                break

            # 5. Handle no actions returned
            if not actions:
                log("  [Navigator] No actions from LLM.", self.debug, self.debug_file)
                break

            # 6. Record step (before execution)
            record = NavigationStepRecord(
                step_number=step_num,
                url_before=current_url,
                title_before=current_title,
                actions_requested=actions,
                reasoning=reasoning,
            )

            # 7. Execute the actions
            actions_executed = self._execute_actions(actions)
            all_actions_taken.extend(actions_executed)

            wait_for_page(self.browser_session)

            new_url = get_current_url(self.browser_session)
            new_title = get_current_title(self.browser_session)

            # 8. Complete the step record
            record.actions_executed = actions_executed
            record.url_after = new_url
            record.title_after = new_title
            step_history.append(record)

            # 9. Check if target reached after this step
            if self._is_target_reached(new_url, command.target_url):
                log(
                    f"  [Navigator] Reached: {new_title} ({new_url})",
                    self.debug, self.debug_file
                )
                return PageNavigatorResult(
                    success=True,
                    current_url=new_url,
                    current_title=new_title,
                    actions_taken=all_actions_taken,
                    navigation_steps=step_num,
                )

            # 10. Detect stagnation (URL unchanged after actions)
            if new_url == current_url:
                log(
                    f"  [Navigator] URL unchanged after step {step_num}.",
                    self.debug, self.debug_file
                )

        # All steps exhausted or LLM returned to orchestrator -- fall back to direct URL
        log(
            f"  [Navigator] Multi-step navigation exhausted ({len(step_history)} steps). "
            f"Falling back to direct URL.",
            self.debug, self.debug_file
        )
        return self._retry_direct(command)

    # ================================================================
    # Step History Formatting
    # ================================================================

    # Dispatch table for formatting action records in step history
    _action_formatters = {
        "click_element":    lambda p: f"clicked element #{p.get('index')}",
        "input_text":       lambda p: f"typed '{p.get('text', '')}' into element #{p.get('index')}",
        "scroll_down":      lambda p: f"scrolled down {p.get('amount', 500)}px",
        "scroll_up":        lambda p: f"scrolled up {p.get('amount', 500)}px",
        "go_back":          lambda p: "navigated back",
        "hover":            lambda p: f"hovered element #{p.get('index')}",
        "select_option":    lambda p: f"selected '{p.get('value', '')}' in element #{p.get('index')}",
        "press_key":        lambda p: f"pressed key '{p.get('key', '')}'",
        "clear_input":      lambda p: f"cleared element #{p.get('index')}",
        "wait_for_element": lambda p: f"waited for element with text '{p.get('text', '')}'",
        "switch_tab":       lambda p: f"switched to tab #{p.get('tab_index')}",
        "open_tab":         lambda p: f"opened new tab{' at ' + p['url'] if p.get('url') else ''}",
    }

    def _format_step_history(self, history: List[NavigationStepRecord]) -> str:
        """Format the step history for inclusion in the LLM prompt."""
        if not history:
            return ""

        lines = ["\n## Navigation History (previous steps in this navigation attempt)"]
        for record in history:
            lines.append(f"\n### Step {record.step_number}")
            lines.append(f"- Page: {record.title_before} ({record.url_before})")
            lines.append(f"- Reasoning: {record.reasoning}")
            if record.actions_executed:
                action_descs = []
                for action in record.actions_executed:
                    action_name = list(action.keys())[0]
                    action_params = action[action_name]
                    formatter = self._action_formatters.get(action_name)
                    if formatter:
                        action_descs.append(formatter(action_params))
                    else:
                        action_descs.append(f"{action_name}({action_params})")
                lines.append(f"- Actions taken: {', '.join(action_descs)}")
            else:
                lines.append("- Actions taken: (none executed)")
            lines.append(f"- Result: landed on {record.title_after} ({record.url_after})")

        return "\n".join(lines)

    # ================================================================
    # Login / Logout Handlers
    # ================================================================

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

        selector_map_json, selector_map_string = self.dom_helper.scroll_and_capture()
        selector_map_string = self._filter_selector_map(
            selector_map_json, selector_map_string
        )
        current_url = get_current_url(self.browser_session)
        current_title = get_current_title(self.browser_session)

        creds = command.credentials
        if not creds:
            return PageNavigatorResult(
                success=False,
                current_url=current_url,
                failure_reason="No credentials provided for login command",
            )

        actions, _, _ = self._ask_llm_for_actions(
            current_url, current_title, selector_map_string, command,
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
        selector_map_json, selector_map_string = self.dom_helper.scroll_and_capture()
        selector_map_string = self._filter_selector_map(
            selector_map_json, selector_map_string
        )
        current_url = get_current_url(self.browser_session)
        current_title = get_current_title(self.browser_session)

        logout_command = NavigatorCommand(
            command_type="logout",
            target_url=command.target_url or "/logout",
            target_label="Logout",
        )
        actions, _, _ = self._ask_llm_for_actions(
            current_url, current_title, selector_map_string, logout_command,
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

    # ================================================================
    # Selector Map Filtering
    # ================================================================

    def _filter_selector_map(
        self, selector_map_json: str, selector_map_string: str
    ) -> str:
        """Apply rule-based filtering to the selector map to remove DOM noise."""
        if not self.selector_filter:
            return selector_map_string
        _, filtered_string = self.selector_filter.filter(selector_map_json)
        return filtered_string

    # ================================================================
    # LLM Interaction
    # ================================================================

    def _ask_llm_for_actions(
        self,
        current_url: str,
        current_title: str,
        selector_map_string: str,
        command: NavigatorCommand,
        step_number: int = 1,
        step_history: str = "",
    ) -> Tuple[List[Dict[str, Any]], bool, str]:
        """Ask the Navigator LLM which elements to interact with.

        Returns:
            (actions, return_to_orchestrator, reasoning)
        """
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
            step_number=step_number,
            current_url=current_url,
            current_title=current_title,
            selector_map_string=selector_map_string[:12000] if selector_map_string else "(empty page)",
            command_type=command.command_type,
            target_url=command.target_url,
            target_label=command.target_label or command.target_url,
            credentials_info=credentials_info,
            site_map="",
            source_page_hint="",
            step_history=step_history,
        )

        try:
            response = self.navigator_llm.ask(prompt)
            self.llm_call_count += 1
            data = parse_llm_json(response)
            actions = data.get("actions", [])
            return_to_orch = data.get("return_to_orchestrator", False)
            reasoning = data.get("reasoning", "")
            return (actions, return_to_orch, reasoning)
        except Exception as e:
            log(f"  [Navigator] LLM error: {e}", self.debug, self.debug_file)
            self.llm_call_count += 1
            return ([], False, "")

    # ================================================================
    # Action Execution
    # ================================================================

    def _execute_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a list of browser actions using dispatch table."""
        action_handlers = {
            "click_element":    self._handle_click_element,
            "input_text":       self._handle_input_text,
            "scroll_down":      self._handle_scroll_down,
            "scroll_up":        self._handle_scroll_up,
            "go_back":          self._handle_go_back,
            "hover":            self._handle_hover,
            "select_option":    self._handle_select_option,
            "press_key":        self._handle_press_key,
            "clear_input":      self._handle_clear_input,
            "wait_for_element": self._handle_wait_for_element,
            "switch_tab":       self._handle_switch_tab,
            "open_tab":         self._handle_open_tab,
        }

        actions_taken = []
        for action in actions:
            if not isinstance(action, dict) or len(action) != 1:
                continue

            action_name = list(action.keys())[0]
            action_params = action[action_name]
            handler = action_handlers.get(action_name)

            if handler is None:
                log(f"  [Navigator] Unknown action: {action_name}", self.debug, self.debug_file)
                continue

            try:
                if handler(action_params):
                    actions_taken.append(action)
            except Exception as e:
                log(f"  [Navigator] Action {action_name} failed: {e}", self.debug, self.debug_file)

        return actions_taken

    # ---- Individual action handlers ----

    def _handle_click_element(self, params: Dict[str, Any]) -> bool:
        idx = params.get("index")
        if idx is None:
            return False
        self.browser_controller.execute_command("click_element", int(idx))
        wait_for_page(self.browser_session)
        return True

    def _handle_input_text(self, params: Dict[str, Any]) -> bool:
        idx = params.get("index")
        text = params.get("text", "")
        if idx is None:
            return False
        self.browser_controller.execute_command("input_text", int(idx), text)
        return True

    def _handle_scroll_down(self, params: Dict[str, Any]) -> bool:
        amount = params.get("amount", 500)
        self.browser_controller.execute_command("scroll_down", int(amount))
        return True

    def _handle_scroll_up(self, params: Dict[str, Any]) -> bool:
        amount = params.get("amount", 500)
        self.browser_controller.execute_command("scroll_up", int(amount))
        return True

    def _handle_go_back(self, params: Dict[str, Any]) -> bool:
        self.browser_controller.execute_command("go_back")
        wait_for_page(self.browser_session)
        return True

    def _handle_hover(self, params: Dict[str, Any]) -> bool:
        idx = params.get("index")
        if idx is None:
            return False
        self.browser_controller.execute_command("hover", int(idx))
        return True

    def _handle_select_option(self, params: Dict[str, Any]) -> bool:
        idx = params.get("index")
        value = params.get("value", "")
        if idx is None or not value:
            return False
        self.browser_controller.execute_command("select_option", int(idx), value)
        return True

    def _handle_press_key(self, params: Dict[str, Any]) -> bool:
        key = params.get("key", "")
        if not key:
            return False
        self.browser_controller.execute_command("press_key", key)
        wait_for_page(self.browser_session)
        return True

    def _handle_clear_input(self, params: Dict[str, Any]) -> bool:
        idx = params.get("index")
        if idx is None:
            return False
        self.browser_controller.execute_command("clear_input", int(idx))
        return True

    def _handle_wait_for_element(self, params: Dict[str, Any]) -> bool:
        text = params.get("text", "")
        timeout = params.get("timeout", 5000)
        if not text:
            return False
        self.browser_controller.execute_command("wait_for_element", text, int(timeout))
        return True

    def _handle_switch_tab(self, params: Dict[str, Any]) -> bool:
        idx = params.get("tab_index")
        if idx is None:
            return False
        self.browser_controller.execute_command("switch_tab", int(idx))
        return True

    def _handle_open_tab(self, params: Dict[str, Any]) -> bool:
        url = params.get("url")
        if url:
            self.browser_controller.execute_command("open_tab", url)
        else:
            self.browser_controller.execute_command("open_tab")
        return True

    # ================================================================
    # Fallback & Helpers
    # ================================================================

    def _try_direct_url(self, command: NavigatorCommand) -> Optional[PageNavigatorResult]:
        """Try navigating directly to target URL before multi-step loop.

        Returns:
            PageNavigatorResult if target reached or redirect detected.
            None if direct navigation failed (caller should use multi-step loop).
        """
        if not command.target_url:
            return None

        original_url = get_current_url(self.browser_session)

        log(
            f"  [Navigator] Trying direct URL: {command.target_url}",
            self.debug, self.debug_file,
        )
        success = self.browser_controller.execute_command(
            "navigate_to", command.target_url
        )
        wait_for_page(self.browser_session)

        new_url = get_current_url(self.browser_session)
        new_title = get_current_title(self.browser_session)

        if success and self._is_target_reached(new_url, command.target_url):
            log(
                f"  [Navigator] Direct URL reached target: {new_url}",
                self.debug, self.debug_file,
            )
            return PageNavigatorResult(
                success=True,
                current_url=new_url,
                current_title=new_title,
                actions_taken=[{"navigate_to": {"url": command.target_url}}],
                navigation_steps=0,
            )

        if success:
            # navigate_to succeeded but URL differs → server-side redirect
            log(
                f"  [Navigator] Redirect detected: {command.target_url} -> {new_url}",
                self.debug, self.debug_file,
            )
            return PageNavigatorResult(
                success=False,
                current_url=new_url,
                current_title=new_title,
                failure_reason=(
                    f"Server redirected from {command.target_url} to {new_url}. "
                    f"The target page may require enrollment or different permissions."
                ),
                was_redirected=True,
                redirected_to=new_url,
            )

        # navigate_to failed entirely — go back, let multi-step handle it
        log(
            f"  [Navigator] Direct URL failed, falling back to multi-step.",
            self.debug, self.debug_file,
        )
        self.browser_controller.execute_command("navigate_to", original_url)
        wait_for_page(self.browser_session)
        return None

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

        # navigate_to succeeded (no exception) but landed on a different URL
        # → server-side redirect (e.g., access denied → enrollment page)
        if success:
            log(
                f"  [Navigator] Server redirected: {command.target_url} -> {new_url}",
                self.debug, self.debug_file,
            )
            return PageNavigatorResult(
                success=False,
                current_url=new_url,
                current_title=new_title,
                failure_reason=(
                    f"Server redirected from {command.target_url} to {new_url}. "
                    f"The target page may require enrollment or different permissions."
                ),
                retry_attempted=True,
                was_redirected=True,
                redirected_to=new_url,
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
