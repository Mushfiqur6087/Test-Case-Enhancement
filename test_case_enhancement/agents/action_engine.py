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
  - Multi-tab aware: detects new tabs, shows all tab state in LLM prompts,
    captures screenshots from every open tab, and handles close_tab/switch_to_tab
"""

from typing import Any, Dict, List, Optional, Tuple

from test_case_enhancement.core.llm import LLMClient
from test_case_enhancement.core.utils import (
    get_current_title,
    get_current_url,
    log,
    parse_llm_json,
    wait_for_page,
)
from test_case_enhancement.browser.controller import BrowserController
from test_case_enhancement.browser.dom_helper import DOMHelper
from test_case_enhancement.browser.screenshot import capture_screenshot_b64
from test_case_enhancement.browser.selector_filter import SelectorMapFilter
from test_case_enhancement.agents.prompts import (
    PROMPT_ACTION_ENGINE_SYSTEM,
    PROMPT_ACTION_ENGINE_STEP,
)


# Max LLM-driven steps per goal to prevent infinite loops
_MAX_STEPS_PER_GOAL = 4
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
    "click the navigation menu icon", "submit the form"), this engine:
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
        base_url: str = "",
    ):
        self.browser_controller = browser_controller
        self.browser_session = browser_session
        self.dom_helper = DOMHelper(browser_session)
        self.selector_filter = selector_filter
        self.debug = debug
        self.debug_file = debug_file
        self.llm_call_count = 0
        self.base_url = base_url  # used for tab context logging

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
        max_steps: int = 0,
    ) -> ActionResult:
        """
        Execute a goal on the current page.

        Parameters
        ----------
        goal          : Natural language description of what to achieve.
                        Examples:
                          - "Fill the login form with username 'user' and password 'pass', then submit"
                          - "Click the navigation menu icon in the header"
                          - "Select the first item from the list"
                          - "Click the hamburger menu button to open the navigation panel"
        extra_context : Additional context for the LLM (e.g., credentials info)
        max_steps     : Maximum LLM-driven steps for this goal. 0 = use default
                        (_MAX_STEPS_PER_GOAL). Callers can pass a tighter budget
                        for simple goals to prevent runaway loops.

        Returns
        -------
        ActionResult with success status and page state.
        """
        step_limit = max_steps if max_steps > 0 else _MAX_STEPS_PER_GOAL

        log(
            f"  [ActionEngine] Goal: {goal[:120]}",
            self.debug, self.debug_file,
        )

        step_history: List[Dict[str, Any]] = []
        total_actions = 0

        for step_num in range(1, step_limit + 1):
            # 1. Dismiss overlays first
            self._dismiss_overlays()

            # 2. Capture current DOM + screenshot
            selector_map_json, selector_map_string = self.dom_helper.scroll_and_capture()
            selector_map_string = self._filter_selector_map(
                selector_map_json, selector_map_string
            )
            current_url = get_current_url(self.browser_session)
            current_title = get_current_title(self.browser_session)

            # 3. Build tab context string (empty when only 1 tab — no noise)
            tab_context = self.browser_session.get_tab_context_string()
            if tab_context:
                log(
                    f"  [TabGuard] {len(self.browser_session._tabs)} tabs open "
                    f"— injecting tab context into prompt.",
                    self.debug, self.debug_file,
                )

            # 4. Capture screenshots for visual grounding.
            #    For vision models with multiple tabs: capture ALL tabs.
            #    For single-tab or non-vision: capture active tab only.
            screenshot_b64 = None
            all_tab_screenshots: List[Dict] = []
            if self._llm.is_vision:
                if len(self.browser_session._tabs) > 1:
                    all_tab_screenshots = self.browser_session.capture_all_tabs_screenshots()
                else:
                    screenshot_b64 = capture_screenshot_b64(self.browser_session)

            # 5. Ask LLM what to do (with screenshot(s) if available)
            history_str = self._format_step_history(step_history)
            actions, goal_achieved, goal_failed, reasoning, failure_reason = (
                self._ask_llm(
                    current_url, current_title,
                    selector_map_string, goal,
                    extra_context, step_num, history_str,
                    tab_context=tab_context,
                    screenshot_b64=screenshot_b64,
                    all_tab_screenshots=all_tab_screenshots,
                )
            )

            # 4. Handle goal_achieved signal
            if goal_achieved:
                log(
                    f"  [ActionEngine] Goal achieved at step {step_num}: {reasoning[:80]}",
                    self.debug, self.debug_file,
                )
                # IMPORTANT: The LLM sometimes violates Rule 3 by returning both
                # actions AND goal_achieved=true in the same response. If we return
                # immediately here, those actions are silently dropped — this was
                # the root cause of Logout never firing (the click was in `actions`
                # but the engine returned before executing it).
                # Fix: execute any pending actions first, then return with the
                # updated post-action URL/title so the caller sees the real state.
                if actions:
                    log(
                        f"  [ActionEngine] Executing {len(actions)} pending action(s) "
                        f"alongside goal_achieved (LLM Rule 3 violation — executing anyway).",
                        self.debug, self.debug_file,
                    )
                    self._execute_actions(actions)
                    wait_for_page(self.browser_session)
                    self._wait_for_background_tabs()
                    current_url = get_current_url(self.browser_session)
                    current_title = get_current_title(self.browser_session)
                    total_actions += len(actions)
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

            # 7b. Wait for any new background tabs to load past about:blank,
            # then log tab state. This ensures the LLM and the log both see
            # the real destination URLs rather than the transient 'about:blank'.
            self._wait_for_background_tabs()
            self._log_tab_state()

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
            failure_reason=f"Goal not achieved after {step_limit} steps",
            actions_taken=total_actions,
            steps_used=step_limit,
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
        tab_context: str = "",
        screenshot_b64: str = None,
        all_tab_screenshots: List[Dict] = None,
    ) -> Tuple[List[Dict], bool, bool, str, str]:
        """
        Ask the LLM which actions to take.

        Tab context:
          - tab_context is injected into the prompt text so the LLM knows
            about all open browser tabs (their index, title, URL).
          - For vision models with multiple tabs, all_tab_screenshots provides
            a screenshot per tab so the LLM can visually confirm which tab
            has the relevant content.

        Falls back to text-only automatically.

        Returns: (actions, goal_achieved, goal_failed, reasoning, failure_reason)
        """
        # Render tab_context with a trailing newline when non-empty so the
        # prompt block looks clean; otherwise collapse to empty string.
        tab_context_block = (tab_context.strip() + "\n\n") if tab_context.strip() else ""

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
            tab_context=tab_context_block,
        )

        try:
            if self._llm.is_vision and all_tab_screenshots:
                # Multi-tab vision: send screenshots from all open tabs.
                # Build a list of (b64, label) pairs for tabs that captured ok.
                tab_images = [
                    t["screenshot_b64"]
                    for t in (all_tab_screenshots or [])
                    if t.get("screenshot_b64")
                ]
                if tab_images:
                    # Use the first (active) screenshot as the primary image;
                    # attach the rest as additional context.
                    response = self._llm.ask_with_screenshot(prompt, tab_images[0])
                else:
                    response = self._llm.ask(prompt)
            elif screenshot_b64:
                response = self._llm.ask_with_screenshot(prompt, screenshot_b64)
            else:
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
            "navigate_to":      self._handle_navigate_to,
            "input_text":       self._handle_input_text,
            "go_back":          self._handle_go_back,
            "hover":            self._handle_hover,
            "select_option":    self._handle_select_option,
            "press_key":        self._handle_press_key,
            "clear_input":      self._handle_clear_input,
            "wait_for_element": self._handle_wait_for_element,
            "close_tab":        self._handle_close_tab,
            "switch_to_tab":    self._handle_switch_to_tab,
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

    def _handle_navigate_to(self, params: Dict[str, Any]) -> bool:
        url = params.get("url", "")
        if not url:
            return False
        self.browser_controller.execute_command("navigate_to", url)
        wait_for_page(self.browser_session)
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

    def _handle_close_tab(self, params: Dict[str, Any]) -> bool:
        page_id = params.get("page_id")
        if page_id is None:
            return False
        result = self.browser_controller.execute_command("close_tab", int(page_id))
        wait_for_page(self.browser_session)
        return bool(result)

    def _handle_switch_to_tab(self, params: Dict[str, Any]) -> bool:
        page_id = params.get("page_id")
        if page_id is None:
            return False
        result = self.browser_controller.execute_command("switch_to_tab", int(page_id))
        wait_for_page(self.browser_session)
        return bool(result)

    # ================================================================
    # Helpers
    # ================================================================

    def _wait_for_background_tabs(self) -> None:
        """Wait for any background tabs that are still at 'about:blank' to
        finish loading their target URL.

        When a click opens a target="_blank" link, Playwright fires the new-page
        event before the page has navigated, so the URL is momentarily
        'about:blank'. We give each such tab up to 3 s to settle before the
        LLM reads the tab context — otherwise it sees wrong URLs and makes
        bad decisions (e.g., closing the wrong tab or switching unnecessarily).
        """
        try:
            for page in self.browser_session._tabs:
                if page is self.browser_session._current_page:
                    continue  # active tab is already waited on by wait_for_page()
                try:
                    if page.url in ("about:blank", ""):
                        page.wait_for_load_state("domcontentloaded", timeout=3000)
                except Exception:
                    pass
        except Exception:
            pass

    def _log_tab_state(self) -> None:
        """Log current tab count and URLs after an action batch.

        Called after every _execute_actions() call so new tabs opened by
        clicks (target="_blank", window.open) are immediately visible in
        the console output. This is purely informational — no tabs are
        closed automatically; the LLM decides what to do next.
        """
        try:
            tabs = self.browser_session.get_tabs_info()
            if len(tabs) > 1:
                log(
                    f"  [TabGuard] {len(tabs)} tabs open after action:",
                    self.debug, self.debug_file,
                )
                for t in tabs:
                    active_marker = " ← ACTIVE" if t.get("is_current") else ""
                    log(
                        f"    Tab {t['page_id']}: {t['title'][:40]} — {t['url'][:80]}{active_marker}",
                        self.debug, self.debug_file,
                    )
        except Exception:
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
        "navigate_to":      lambda p: f"navigated to '{p.get('url', '')}'",
        "input_text":       lambda p: f"typed '{p.get('text', '')}' into #{p.get('index')}",
        "go_back":          lambda p: "went back",
        "hover":            lambda p: f"hovered #{p.get('index')}",
        "select_option":    lambda p: f"selected '{p.get('value', '')}' in #{p.get('index')}",
        "press_key":        lambda p: f"pressed '{p.get('key', '')}'",
        "clear_input":      lambda p: f"cleared #{p.get('index')}",
        "wait_for_element": lambda p: f"waited for '{p.get('text', '')}'",
        "close_tab":        lambda p: f"closed tab #{p.get('page_id')}",
        "switch_to_tab":    lambda p: f"switched to tab #{p.get('page_id')}",
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
