"""High-level browser command executor wrapping BrowserSession."""

from typing import Optional, Dict, Any, Union, List

from intelligent_navigator.browser.css_utils import css_id_selector
from intelligent_navigator.browser.session import BrowserSession


class BrowserController:
    """Wraps BrowserSession to provide high-level browser operations."""

    def __init__(self, llm_client=None):
        self.browser_context = BrowserSession()
        self.llm_client = llm_client

    def execute_command(self, command: str, *args) -> Union[bool, Dict[str, Any], str]:
        """Execute a browser command with the provided arguments."""
        command_map = {
            "go_back":          self.go_back,
            "click_element":    self.click_element_by_index,
            "input_text":       self.input_text,
            "scroll_down":      self.scroll_down,
            "scroll_up":        self.scroll_up,
            "hover":            self.hover_element,
            "select_option":    self.select_option,
            "press_key":        self.press_key,
            "clear_input":      self.clear_input,
            "wait_for_element": self.wait_for_element,
            "navigate_to":      self.navigate_to,
            "close_tab":        self.close_tab,
            "switch_to_tab":    self.switch_to_tab,
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
                    page.click(css_id_selector(elem_id), timeout=5000)
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
                        page.click(css_id_selector(elem_id), timeout=5000, force=True)
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
                    page.fill(css_id_selector(elem_id), text, timeout=5000)
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
                        page.fill(css_id_selector(elem_id), text, timeout=5000)
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

    def hover_element(self, element_index: int) -> bool:
        """Hover over an element to reveal dropdowns, tooltips, or menus."""
        try:
            page = self.browser_context.get_current_page()
            if page is None:
                return False

            selector_map = self.browser_context.get_selector_map(refresh=True)
            if not selector_map or element_index not in selector_map:
                print(f"  [Controller] hover_element({element_index}): index not in selector_map (size={len(selector_map) if selector_map else 0})")
                return False

            element = selector_map[element_index]
            xpath = element.xpath
            attrs = element.attributes or {}

            try:
                if (elem_id := attrs.get("id")):
                    page.hover(css_id_selector(elem_id), timeout=5000)
                else:
                    page.locator(f"xpath={xpath}").hover(timeout=5000)
            except Exception:
                try:
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(300)
                except Exception:
                    pass
                try:
                    if (elem_id := attrs.get("id")):
                        page.hover(css_id_selector(elem_id), timeout=5000, force=True)
                    else:
                        page.locator(f"xpath={xpath}").hover(timeout=5000, force=True)
                except Exception as e2:
                    print(f"  [Controller] hover_element({element_index}) error: {e2}")
                    return False

            page.wait_for_timeout(500)
            self.browser_context._parser = None
            self.browser_context._selector_map = None
            return True

        except Exception as e:
            print(f"  [Controller] hover_element({element_index}) error: {e}")
            return False

    def select_option(self, element_index: int, value: str) -> bool:
        """Select an option from a <select> dropdown by value or visible label."""
        try:
            page = self.browser_context.get_current_page()
            if page is None:
                return False

            selector_map = self.browser_context.get_selector_map(refresh=True)
            if not selector_map or element_index not in selector_map:
                print(f"  [Controller] select_option({element_index}): index not in selector_map (size={len(selector_map) if selector_map else 0})")
                return False

            element = selector_map[element_index]
            xpath = element.xpath
            attrs = element.attributes or {}

            if (elem_id := attrs.get("id")):
                locator = page.locator(css_id_selector(elem_id))
            else:
                locator = page.locator(f"xpath={xpath}")

            # Try by value first, then by visible label text
            try:
                locator.select_option(value=value, timeout=5000)
            except Exception:
                locator.select_option(label=value, timeout=5000)

            page.wait_for_timeout(500)
            self.browser_context._parser = None
            self.browser_context._selector_map = None
            return True

        except Exception as e:
            print(f"  [Controller] select_option({element_index}, {value}) error: {e}")
            return False

    ALLOWED_KEYS = {
        "Enter", "Tab", "Escape", "Backspace", "Delete",
        "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight",
        "Home", "End", "PageUp", "PageDown", "Space",
    }
    ALLOWED_KEY_COMBOS = {
        "Control+a", "Control+c", "Control+v",
    }

    def press_key(self, key: str) -> bool:
        """Press a keyboard key or key combination (whitelisted for safety)."""
        try:
            if key not in self.ALLOWED_KEYS and key not in self.ALLOWED_KEY_COMBOS:
                print(f"  [Controller] press_key: key '{key}' not allowed")
                return False

            page = self.browser_context.get_current_page()
            if page is None:
                return False

            page.keyboard.press(key)
            page.wait_for_timeout(300)
            self.browser_context._parser = None
            self.browser_context._selector_map = None
            return True

        except Exception as e:
            print(f"  [Controller] press_key({key}) error: {e}")
            return False

    def clear_input(self, element_index: int) -> bool:
        """Clear a text input field."""
        try:
            page = self.browser_context.get_current_page()
            if page is None:
                return False

            selector_map = self.browser_context.get_selector_map(refresh=True)
            if not selector_map or element_index not in selector_map:
                print(f"  [Controller] clear_input({element_index}): index not in selector_map (size={len(selector_map) if selector_map else 0})")
                return False

            element = selector_map[element_index]
            xpath = element.xpath
            attrs = element.attributes or {}

            if (elem_id := attrs.get("id")):
                page.fill(css_id_selector(elem_id), "", timeout=5000)
            else:
                page.locator(f"xpath={xpath}").fill("", timeout=5000)

            self.browser_context._parser = None
            self.browser_context._selector_map = None
            return True

        except Exception as e:
            print(f"  [Controller] clear_input({element_index}) error: {e}")
            return False

    def wait_for_element(self, text: str, timeout: int = 5000) -> bool:
        """Wait for an element containing specific text to become visible."""
        try:
            page = self.browser_context.get_current_page()
            if page is None:
                return False

            timeout = min(timeout, 10000)  # Cap at 10 seconds
            page.get_by_text(text).first.wait_for(state="visible", timeout=timeout)
            self.browser_context._parser = None
            self.browser_context._selector_map = None
            return True

        except Exception as e:
            print(f"  [Controller] wait_for_element('{text}') error: {e}")
            return False

    def navigate_to(self, url: str) -> bool:
        try:
            self.browser_context.navigate_to(url)
            return True
        except Exception:
            return False

    def close_tab(self, page_id: int) -> bool:
        """Close a browser tab by its index."""
        try:
            result = self.browser_context.close_tab(page_id)
            if result:
                print(f"  [Controller] Closed tab {page_id}")
            return result
        except Exception as e:
            print(f"  [Controller] close_tab({page_id}) error: {e}")
            return False

    def switch_to_tab(self, page_id: int) -> bool:
        """Switch the active tab to the one at the given index."""
        try:
            result = self.browser_context.switch_to_tab(page_id)
            if result:
                print(f"  [Controller] Switched to tab {page_id}")
            return result
        except Exception as e:
            print(f"  [Controller] switch_to_tab({page_id}) error: {e}")
            return False

    def close(self) -> None:
        try:
            self.browser_context.close()
        except Exception:
            pass
