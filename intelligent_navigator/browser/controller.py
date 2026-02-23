"""High-level browser command executor wrapping BrowserSession."""

from typing import Optional, Dict, Any, Union, List

from intelligent_navigator.browser.session import BrowserSession


class BrowserController:
    """Wraps BrowserSession to provide high-level browser operations."""

    def __init__(self, llm_client=None):
        self.browser_context = BrowserSession()
        self.llm_client = llm_client

    def execute_command(self, command: str, *args) -> Union[bool, Dict[str, Any], str]:
        """Execute a browser command with the provided arguments."""
        command_map = {
            "go_back":       self.go_back,
            "click_element": self.click_element_by_index,
            "input_text":    self.input_text,
            "scroll_down":   self.scroll_down,
            "scroll_up":     self.scroll_up,
            "switch_tab":    self.switch_tab,
            "open_tab":      self.open_tab,
            "close_tab":     self.close_tab,
            "navigate_to":   self.navigate_to,
            "end":           self.end,
        }

        if command not in command_map:
            return False

        try:
            return command_map[command](*args)
        except Exception:
            return False

    def go_back(self) -> bool:
        try:
            self.browser_context.go_back()
            return True
        except Exception:
            return False

    def click_element_by_index(self, element_index: int) -> bool:
        try:
            page = self.browser_context.get_current_page()
            if page is None:
                return False

            selector_map = self.browser_context.get_selector_map(refresh=True)
            if not selector_map or element_index not in selector_map:
                print(f"  [Controller] click_element({element_index}): index not in selector_map (size={len(selector_map) if selector_map else 0})")
                return False

            element = selector_map[element_index]
            xpath = element.xpath
            attrs = element.attributes or {}
            tag = element.tag_name if hasattr(element, 'tag_name') else ""
            el_type = attrs.get("type", "")

            url_before = page.url

            # ---- click with overlay-dismiss fallback ----
            try:
                if (elem_id := attrs.get("id")):
                    page.click(f"#{elem_id}", timeout=5000)
                else:
                    page.locator(f"xpath={xpath}").click(timeout=5000)
            except Exception:
                # Likely a Radix overlay / popover blocking pointer events.
                # Dismiss it, then retry with force=True.
                try:
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(300)
                except Exception:
                    pass
                try:
                    if (elem_id := attrs.get("id")):
                        page.click(f"#{elem_id}", timeout=5000, force=True)
                    else:
                        page.locator(f"xpath={xpath}").click(timeout=5000, force=True)
                except Exception as e2:
                    print(f"  [Controller] click_element({element_index}) error: {e2}")
                    return False

            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass

            if el_type == "submit" or (tag == "button" and el_type == "submit"):
                page.wait_for_timeout(2000)
                if page.url != url_before:
                    page.wait_for_timeout(2000)
                    try:
                        page.wait_for_load_state("networkidle", timeout=5000)
                    except Exception:
                        pass
                    self.browser_context._parser = None
                    self.browser_context._selector_map = None

            self.browser_context._parser = None
            self.browser_context._selector_map = None

            return True

        except Exception as e:
            print(f"  [Controller] click_element({element_index}) error: {e}")
            return False

    def input_text(self, element_index: int, text: str) -> bool:
        try:
            page = self.browser_context.get_current_page()
            if page is None:
                return False

            selector_map = self.browser_context.get_selector_map(refresh=True)
            if not selector_map or element_index not in selector_map:
                print(f"  [Controller] input_text({element_index}): index not in selector_map (size={len(selector_map) if selector_map else 0})")
                return False

            element = selector_map[element_index]
            xpath = element.xpath
            attrs = element.attributes or {}

            # ---- fill with overlay-dismiss fallback ----
            try:
                if (elem_id := attrs.get("id")):
                    page.fill(f"#{elem_id}", text, timeout=5000)
                else:
                    page.locator(f"xpath={xpath}").fill(text, timeout=5000)
            except Exception:
                try:
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(300)
                except Exception:
                    pass
                try:
                    if (elem_id := attrs.get("id")):
                        page.fill(f"#{elem_id}", text, timeout=5000)
                    else:
                        page.locator(f"xpath={xpath}").fill(text, timeout=5000)
                except Exception as e2:
                    print(f"  [Controller] input_text({element_index}) error: {e2}")
                    return False

            self.browser_context._parser = None
            self.browser_context._selector_map = None

            return True

        except Exception as e:
            print(f"  [Controller] input_text({element_index}) error: {e}")
            return False

    def switch_tab(self, tab_index: int) -> bool:
        try:
            return self.browser_context.switch_to_tab(tab_index)
        except Exception:
            return False

    def open_tab(self, url: Optional[str] = None) -> Dict[str, Any]:
        try:
            return self.browser_context.create_new_tab(url)
        except Exception:
            return {}

    def close_tab(self, tab_index: int) -> bool:
        try:
            return self.browser_context.close_tab(tab_index)
        except Exception:
            return False

    def scroll_down(self, amount: int = 500) -> bool:
        try:
            page = self.browser_context.get_current_page()
            if page is None:
                return False
            page.mouse.wheel(0, amount)
            page.wait_for_timeout(500)
            self.browser_context._parser = None
            self.browser_context._selector_map = None
            return True
        except Exception:
            return False

    def scroll_up(self, amount: int = 500) -> bool:
        try:
            page = self.browser_context.get_current_page()
            if page is None:
                return False
            page.mouse.wheel(0, -amount)
            page.wait_for_timeout(500)
            self.browser_context._parser = None
            self.browser_context._selector_map = None
            return True
        except Exception:
            return False

    def navigate_to(self, url: str) -> bool:
        try:
            self.browser_context.navigate_to(url)
            return True
        except Exception:
            return False

    def end(self, reason: Optional[str] = None) -> bool:
        try:
            self.browser_context.close()
            return True
        except Exception:
            return False

    def close(self) -> None:
        try:
            self.browser_context.close()
        except Exception:
            pass
