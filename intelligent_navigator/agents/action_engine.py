"""
Action Engine — Unified Playwright-based goal execution.

Replaces the old Navigator + LinkDiscovery agents with a single,
goal-oriented action engine that:
  1. Takes a navigation GOAL in natural language
  2. Reads the current page's DOM (selector map)
  3. Asks an LLM which actions to take
  4. Executes them using the BrowserController's Playwright-backed actions
  5. Verifies the page state changed

Key improvements over Navigator:
  - Goal-oriented (not index-oriented or text-match-oriented)
  - Handles forms, buttons, icons, and all interactive elements
  - Progress detection: detects when actions don't change page state
  - Multi-step with history: can chain multiple actions toward one goal
  - Merges login/logout/click/form into a single unified flow
"""

from typing import Any, Dict, List, Optional, Tuple

from intelligent_navigator.core.llm import LLMClient
from intelligent_navigator.core.models import RoleCredentials
from intelligent_navigator.core.utils import (
    get_current_title,
    get_current_url,
    log,
    parse_llm_json,
    wait_for_page,
)
from intelligent_navigator.browser.controller import BrowserController
from intelligent_navigator.browser.dom_helper import DOMHelper
from intelligent_navigator.browser.selector_filter import SelectorMapFilter
from intelligent_navigator.agents.prompts import (
    PROMPT_ACTION_ENGINE_SYSTEM,
    PROMPT_ACTION_ENGINE_STEP,
)


# Max LLM-driven steps per goal to prevent infinite loops
_MAX_STEPS_PER_GOAL = 8
# Max characters of selector map to send to LLM
_MAX_SELECTOR_MAP_CHARS = 12_000


class ActionResult:
    """Result of a goal execution attempt."""

    def __init__(
        self,
        success: bool,
        current_url: str = "",
        current_title: str = "",
        failure_reason: str = "",
        actions_taken: int = 0,
        steps_used: int = 0,
    ):
        self.success = success
        self.current_url = current_url
        self.current_title = current_title
        self.failure_reason = failure_reason
        self.actions_taken = actions_taken
        self.steps_used = steps_used


class ActionEngine:
    """
    Goal-oriented browser action execution engine.

    Given a natural-language goal (e.g., "fill the login form and submit",
    "click the shopping cart icon", "add an item to the cart"), this engine:
      1. Captures the current DOM state
      2. Asks an LLM what actions to take
      3. Executes the actions via BrowserController
      4. Checks if the goal was achieved
      5. Repeats if needed (up to _MAX_STEPS_PER_GOAL)
    """

    def __init__(
        self,
        llm_client: LLMClient,
        browser_controller: BrowserController,
        browser_session,
        debug: bool = False,
        debug_file: Optional[str] = None,
        selector_filter: Optional[SelectorMapFilter] = None,
    ):
        self.browser_controller = browser_controller
        self.browser_session = browser_session
        self.dom_helper = DOMHelper(browser_session)
        self.selector_filter = selector_filter
        self.debug = debug
        self.debug_file = debug_file
        self.llm_call_count = 0

        self._llm = LLMClient(
            api_key=llm_client.api_key,
            model_name=llm_client.model_name,
            system_prompt=PROMPT_ACTION_ENGINE_SYSTEM,
            debug_file=debug_file,
        )

    # ================================================================
    # Public API
    # ================================================================

    def execute_goal(
        self,
        goal: str,
        extra_context: str = "",
    ) -> ActionResult:
        """
        Execute a goal on the current page.

        Parameters
        ----------
        goal          : Natural language description of what to achieve.
                        Examples:
                          - "Fill the login form with username 'user' and password 'pass', then submit"
                          - "Click the shopping cart icon in the header"
                          - "Add the first product to the cart"
                          - "Click the hamburger menu button to open the navigation panel"
        extra_context : Additional context for the LLM (e.g., credentials info)

        Returns
        -------
        ActionResult with success status and page state.
        """
        log(
            f"  [ActionEngine] Goal: {goal[:120]}",
            self.debug, self.debug_file,
        )

        step_history: List[Dict[str, Any]] = []
        total_actions = 0

        for step_num in range(1, _MAX_STEPS_PER_GOAL + 1):
            # 1. Dismiss overlays first
            self._dismiss_overlays()

            # 2. Capture current DOM
            selector_map_json, selector_map_string = self.dom_helper.scroll_and_capture()
            selector_map_string = self._filter_selector_map(
                selector_map_json, selector_map_string
            )
            current_url = get_current_url(self.browser_session)
            current_title = get_current_title(self.browser_session)

            # 3. Ask LLM what to do
            history_str = self._format_step_history(step_history)
            actions, goal_achieved, goal_failed, reasoning, failure_reason = (
                self._ask_llm(
                    current_url, current_title,
                    selector_map_string, goal,
                    extra_context, step_num, history_str,
                )
            )

            # 4. Handle goal_achieved signal
            if goal_achieved:
                log(
                    f"  [ActionEngine] Goal achieved at step {step_num}: {reasoning[:80]}",
                    self.debug, self.debug_file,
                )
                return ActionResult(
                    success=True,
                    current_url=current_url,
                    current_title=current_title,
                    actions_taken=total_actions,
                    steps_used=step_num,
                )

            # 5. Handle goal_failed signal
            if goal_failed:
                log(
                    f"  [ActionEngine] Goal failed at step {step_num}: {failure_reason[:120]}",
                    self.debug, self.debug_file,
                )
                return ActionResult(
                    success=False,
                    current_url=current_url,
                    current_title=current_title,
                    failure_reason=failure_reason or reasoning,
                    actions_taken=total_actions,
                    steps_used=step_num,
                )

            # 6. Handle no actions
            if not actions:
                log(
                    f"  [ActionEngine] No actions returned at step {step_num}.",
                    self.debug, self.debug_file,
                )
                return ActionResult(
                    success=False,
                    current_url=current_url,
                    current_title=current_title,
                    failure_reason="LLM returned no actions",
                    actions_taken=total_actions,
                    steps_used=step_num,
                )

            # 7. Execute the actions
            url_before = current_url
            actions_executed = self._execute_actions(actions)
            total_actions += len(actions_executed)
            wait_for_page(self.browser_session)

            new_url = get_current_url(self.browser_session)
            new_title = get_current_title(self.browser_session)

            # 8. Record step history
            step_history.append({
                "step": step_num,
                "url_before": url_before,
                "url_after": new_url,
                "title_after": new_title,
                "actions": actions_executed,
                "reasoning": reasoning,
            })

            log(
                f"  [ActionEngine] Step {step_num}: {reasoning[:80]} → {new_title} ({new_url})",
                self.debug, self.debug_file,
            )

            # 9. Detect stagnation (same URL, same title)
            if new_url == url_before and step_num > 1:
                # Check if DOM actually changed (for SPA apps)
                _, new_dom = self.dom_helper.scroll_and_capture()
                if new_dom == selector_map_string:
                    log(
                        f"  [ActionEngine] Page unchanged after step {step_num} — stopping.",
                        self.debug, self.debug_file,
                    )
                    # Don't immediately fail — let the LLM decide in next step
                    # But if we've stagnated for 2+ steps, bail
                    if len(step_history) >= 2 and step_history[-2].get("url_after") == new_url:
                        return ActionResult(
                            success=False,
                            current_url=new_url,
                            current_title=new_title,
                            failure_reason="Page state unchanged after multiple action attempts",
                            actions_taken=total_actions,
                            steps_used=step_num,
                        )

        # Exhausted all steps
        current_url = get_current_url(self.browser_session)
        current_title = get_current_title(self.browser_session)
        return ActionResult(
            success=False,
            current_url=current_url,
            current_title=current_title,
            failure_reason=f"Goal not achieved after {_MAX_STEPS_PER_GOAL} steps",
            actions_taken=total_actions,
            steps_used=_MAX_STEPS_PER_GOAL,
        )

    def navigate_to_url(self, url: str) -> ActionResult:
        """Direct URL navigation — used for base_url and fallbacks."""
        self.browser_controller.execute_command("navigate_to", url)
        wait_for_page(self.browser_session)
        current_url = get_current_url(self.browser_session)
        current_title = get_current_title(self.browser_session)
        return ActionResult(
            success=True,
            current_url=current_url,
            current_title=current_title,
        )

    # ================================================================
    # LLM Interaction
    # ================================================================

    def _ask_llm(
        self,
        current_url: str,
        current_title: str,
        selector_map_string: str,
        goal: str,
        extra_context: str,
        step_number: int,
        step_history: str,
    ) -> Tuple[List[Dict], bool, bool, str, str]:
        """
        Ask the LLM which actions to take.

        Returns: (actions, goal_achieved, goal_failed, reasoning, failure_reason)
        """
        prompt = PROMPT_ACTION_ENGINE_STEP.format(
            step_number=step_number,
            current_url=current_url,
            current_title=current_title,
            selector_map_string=(
                selector_map_string[:_MAX_SELECTOR_MAP_CHARS]
                if selector_map_string else "(empty page)"
            ),
            goal=goal,
            extra_context=extra_context,
            step_history=step_history,
        )

        try:
            response = self._llm.ask(prompt)
            self.llm_call_count += 1
            data = parse_llm_json(response)
        except Exception as e:
            log(f"  [ActionEngine] LLM error: {e}", self.debug, self.debug_file)
            self.llm_call_count += 1
            return ([], False, True, "", f"LLM error: {e}")

        actions = data.get("actions", [])
        goal_achieved = data.get("goal_achieved", False)
        goal_failed = data.get("goal_failed", False)
        reasoning = data.get("reasoning", "")
        failure_reason = data.get("failure_reason", "")

        return (actions, goal_achieved, goal_failed, reasoning, failure_reason)

    # ================================================================
    # Action Execution (reused from Navigator pattern)
    # ================================================================

    def _execute_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a list of browser actions using the BrowserController."""
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
        }

        actions_taken = []
        for action in actions:
            if not isinstance(action, dict) or len(action) != 1:
                continue

            action_name = list(action.keys())[0]
            action_params = action[action_name]
            handler = action_handlers.get(action_name)

            if handler is None:
                log(
                    f"  [ActionEngine] Unknown action: {action_name}",
                    self.debug, self.debug_file,
                )
                continue

            try:
                if handler(action_params):
                    actions_taken.append(action)
            except Exception as e:
                log(
                    f"  [ActionEngine] Action {action_name} failed: {e}",
                    self.debug, self.debug_file,
                )

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

    # ================================================================
    # Helpers
    # ================================================================

    def _dismiss_overlays(self) -> None:
        """No-op: overlays are handled by the LLM via explicit press_key: Escape.
        Unconditional Escape was removed because it closed intentionally-opened
        overlays (hamburger menu, dropdowns) between ActionEngine steps."""
        pass

    def _filter_selector_map(
        self, selector_map_json: str, selector_map_string: str
    ) -> str:
        """Apply rule-based filtering to reduce DOM noise."""
        if not self.selector_filter:
            return selector_map_string
        _, filtered_string = self.selector_filter.filter(selector_map_json)
        return filtered_string

    # Dispatch table for formatting action records in step history
    _action_formatters = {
        "click_element":    lambda p: f"clicked element #{p.get('index')}",
        "input_text":       lambda p: f"typed '{p.get('text', '')}' into #{p.get('index')}",
        "scroll_down":      lambda p: f"scrolled down {p.get('amount', 500)}px",
        "scroll_up":        lambda p: f"scrolled up {p.get('amount', 500)}px",
        "go_back":          lambda p: "went back",
        "hover":            lambda p: f"hovered #{p.get('index')}",
        "select_option":    lambda p: f"selected '{p.get('value', '')}' in #{p.get('index')}",
        "press_key":        lambda p: f"pressed '{p.get('key', '')}'",
        "clear_input":      lambda p: f"cleared #{p.get('index')}",
        "wait_for_element": lambda p: f"waited for '{p.get('text', '')}'",
    }

    def _format_step_history(self, history: List[Dict[str, Any]]) -> str:
        """Format step history as compact single-line entries for the LLM prompt."""
        if not history:
            return ""

        lines = ["\n## Action History (previous steps for this goal)"]
        for record in history:
            step = record["step"]
            action_descs = []
            for action in record.get("actions", []):
                action_name = list(action.keys())[0]
                action_params = action[action_name]
                formatter = self._action_formatters.get(action_name)
                if formatter:
                    action_descs.append(formatter(action_params))
                else:
                    action_descs.append(f"{action_name}({action_params})")
            actions_str = ", ".join(action_descs) if action_descs else "no actions"
            lines.append(
                f"Step {step}: [{actions_str}] → {record['title_after']} ({record['url_after']})"
            )

        return "\n".join(lines)
