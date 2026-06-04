"""JavaScript-based DOM tree builder using Playwright."""

import time


class DomTreeBuilder:
    def __init__(self, page, debug_mode=False):
        self.page = page
        self.debug_mode = debug_mode
        if debug_mode:
            self.perf_metrics = {
                "build_dom_tree_calls": 0,
                "timings": {
                    "build_dom_tree": 0,
                    "is_interactive_element": 0,
                    "is_element_visible": 0,
                },
                "node_metrics": {
                    "total_nodes": 0,
                    "processed_nodes": 0,
                    "skipped_nodes": 0,
                }
            }
        else:
            self.perf_metrics = None

        self._init_js_functions()

    def _init_js_functions(self):
        self.page.evaluate("""() => {
            window.domTreeHelpers = {
                isElementVisible: (element) => {
                    if (!element) return false;
                    const style = window.getComputedStyle(element);

                    // Hard-invisible: these always mean "not rendered"
                    if (style.display === 'none' ||
                        style.visibility === 'hidden' ||
                        style.opacity === '0') {
                        return false;
                    }

                    // Standard check: element has its own non-zero dimensions
                    if (element.offsetWidth > 0 && element.offsetHeight > 0) {
                        return true;
                    }

                    // Fallback 1: getBoundingClientRect — works for fixed/absolute
                    // elements where offsetWidth can be unreliable (e.g., icon buttons
                    // positioned with transform or inside overflow:hidden wrappers)
                    const rect = element.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        return true;
                    }

                    // Fallback 2: for interactive elements (buttons, links, inputs,
                    // role="button", etc.) check if any direct child has non-zero rect.
                    // This catches SVG-icon buttons and hamburger-menu style triggers
                    // where the <button> itself is 0x0 but its <span> children are visible.
                    const tag = element.tagName.toLowerCase();
                    const isInteractiveTag = ['button', 'a', 'input', 'select', 'textarea'].includes(tag);
                    const hasRole = element.hasAttribute('role');
                    if (isInteractiveTag || hasRole) {
                        for (let i = 0; i < element.children.length; i++) {
                            const childRect = element.children[i].getBoundingClientRect();
                            if (childRect.width > 0 && childRect.height > 0) {
                                return true;
                            }
                        }
                        // Also treat it as visible if it has an aria-label or
                        // aria-expanded — it's a meaningful, labelled control
                        // even if temporarily zero-sized.
                        if (element.hasAttribute('aria-label') ||
                            element.hasAttribute('aria-expanded')) {
                            return true;
                        }
                    }

                    return false;
                },

                isInteractiveElement: (element) => {
                    if (!element) return false;

                    const tagName = element.tagName.toLowerCase();

                    if (['a', 'button', 'input', 'select', 'textarea', 'details', 'audio', 'video'].includes(tagName)) {
                        return true;
                    }

                    if (element.hasAttribute('role') &&
                        ['button', 'link', 'checkbox', 'menuitem', 'menuitemcheckbox', 'menuitemradio',
                         'option', 'radio', 'searchbox', 'switch', 'tab'].includes(element.getAttribute('role'))) {
                        return true;
                    }

                    if (element.onclick || element.onmousedown || element.onmouseup ||
                        element.onkeydown || element.onkeyup) {
                        return true;
                    }

                    const style = window.getComputedStyle(element);
                    if (style.cursor === 'pointer') {
                        return true;
                    }

                    return false;
                },

                isInViewport: (element) => {
                    if (!element) return false;

                    const rect = element.getBoundingClientRect();
                    const viewportWidth = window.innerWidth;
                    const viewportHeight = window.innerHeight;

                    return (
                        rect.bottom >= 0 &&
                        rect.right >= 0 &&
                        rect.top <= viewportHeight &&
                        rect.left <= viewportWidth
                    );
                },

                getXPath: (element) => {
                    if (!element || element.nodeType !== 1) return '';
                    const segments = [];
                    for (let el = element; el && el.nodeType === 1; el = el.parentNode) {
                        let index = 1;
                        for (let sib = el.previousElementSibling; sib; sib = sib.previousElementSibling) {
                            if (sib.nodeName === el.nodeName) index++;
                        }
                        segments.unshift(el.nodeName.toLowerCase() + '[' + index + ']');
                    }
                    return '/' + segments.join('/');
                }
            };
        }""")

    def measure_time(self, fn, metric_name=None):
        if not self.debug_mode:
            return fn()

        start = time.time()
        result = fn()
        duration = (time.time() - start) * 1000

        if metric_name and metric_name in self.perf_metrics["timings"]:
            self.perf_metrics["timings"][metric_name] += duration

        return result

    def is_element_visible(self, element_handle):
        if element_handle is None:
            return False

        def check():
            try:
                return element_handle.evaluate("element => window.domTreeHelpers.isElementVisible(element)")
            except:
                return False

        return self.measure_time(check, "is_element_visible")

    def is_interactive_element(self, element_handle):
        if element_handle is None:
            return False

        def check():
            try:
                return element_handle.evaluate("element => window.domTreeHelpers.isInteractiveElement(element)")
            except:
                return False

        return self.measure_time(check, "is_interactive_element")

    def is_in_viewport(self, element_handle):
        try:
            return element_handle.evaluate("element => window.domTreeHelpers.isInViewport(element)")
        except:
            return False

    def build_dom_tree(self, element_handle=None):
        if self.debug_mode:
            self.perf_metrics["build_dom_tree_calls"] += 1

        if element_handle is None:
            element_handle = self.page.query_selector('body')

        if element_handle is None:
            return None

        start_time = time.time()
        if self.debug_mode:
            self.perf_metrics["node_metrics"]["total_nodes"] += 1

        is_visible = self.is_element_visible(element_handle)
        is_in_viewport = self.is_in_viewport(element_handle)

        # Prune aria-hidden="true" subtrees: these are intentionally hidden from
        # assistive technology and keyboard interaction. Closed overlay containers
        # (e.g., react-burger-menu's bm-menu-wrap) set aria-hidden="true" when
        # collapsed — skipping them removes sidebar links from the selector map
        # while the menu is closed. When the menu opens, aria-hidden becomes
        # "false" and the links are included normally.
        try:
            aria_hidden = element_handle.get_attribute("aria-hidden")
            if aria_hidden == "true":
                if self.debug_mode:
                    self.perf_metrics["node_metrics"]["skipped_nodes"] += 1
                return None
        except Exception:
            pass

        # Only hard-prune nodes that are truly outside the viewport.
        # FullPageDomTreeBuilder overrides is_in_viewport to always return True,
        # so this never prunes in practice during full-page capture.
        #
        # We deliberately do NOT prune based on is_visible here — if we did,
        # any child element inside an invisible parent container would be
        # silently skipped. This was causing hamburger-menu buttons (which are
        # position:fixed and visually present) to be missed when their wrapper
        # div had offsetWidth/Height = 0. Each child now checks its own
        # visibility independently via is_element_visible.
        if not is_in_viewport:
            if self.debug_mode:
                self.perf_metrics["node_metrics"]["skipped_nodes"] += 1
            return None

        if self.debug_mode:
            self.perf_metrics["node_metrics"]["processed_nodes"] += 1

        is_interactive = self.is_interactive_element(element_handle)

        tag_name = element_handle.evaluate("el => el.tagName.toLowerCase()")
        text_content = element_handle.evaluate("el => el.textContent || ''")
        inner_text = element_handle.evaluate("el => el.innerText || ''")
        xpath = element_handle.evaluate("el => window.domTreeHelpers.getXPath(el)")

        attributes = element_handle.evaluate("""
            element => {
                const attrs = {};
                for (const attr of element.attributes) {
                    attrs[attr.name] = attr.value;
                }
                return attrs;
            }
        """)

        node_data = {
            "nodeName": tag_name,
            "textContent": text_content,
            "innerText": inner_text,
            "xpath": xpath,
            "attributes": attributes,
            "children": [],
            "isInteractive": is_interactive,
            "isVisible": is_visible
        }

        child_elements = element_handle.query_selector_all(':scope > *')
        for child in child_elements:
            child_tree = self.build_dom_tree(child)
            if child_tree:
                node_data["children"].append(child_tree)

        if self.debug_mode:
            duration = (time.time() - start_time) * 1000
            self.perf_metrics["timings"]["build_dom_tree"] += duration

        return node_data

    def get_dom_tree(self):
        if self.debug_mode:
            for key in self.perf_metrics["timings"]:
                self.perf_metrics["timings"][key] = 0
            self.perf_metrics["build_dom_tree_calls"] = 0
            self.perf_metrics["node_metrics"] = {
                "total_nodes": 0,
                "processed_nodes": 0,
                "skipped_nodes": 0,
            }

        tree = self.build_dom_tree()
        result = {"tree": tree}

        if self.debug_mode:
            result["perfMetrics"] = self.perf_metrics

        return result
