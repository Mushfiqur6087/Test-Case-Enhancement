"""
Rule-based first-pass filter for selector maps.

Removes obvious DOM noise (calendar cells, decorative icons, redundant
child spans) while preserving original element indexes so the browser
controller can still resolve action indexes correctly.
"""

import json
import re
from typing import Dict, Set, Tuple


# Tags that are always worth keeping when interactive
_FORM_TAGS = {"input", "select", "textarea"}
_ACTION_TAGS = {"a", "button"}

# ARIA roles that indicate a meaningful interactive element
_MEANINGFUL_ROLES = {
    "button", "menuitem", "menuitemcheckbox", "menuitemradio",
    "tab", "switch", "checkbox", "radio", "searchbox", "option",
    "link", "combobox",
}

# Attributes whose mere presence signals a calendar / data-display cell
_CALENDAR_ATTRS = {"data-day-timestamp", "data-day"}


class SelectorMapFilter:
    """Rule-based first-pass filter that removes obvious DOM noise."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def filter(self, selector_map_json: str) -> Tuple[str, str]:
        """
        Filter raw selector map JSON.

        Returns (filtered_json_str, filtered_human_string).
        Original indexes are PRESERVED (not re-indexed).
        """
        try:
            elements: Dict[str, dict] = json.loads(selector_map_json)
        except (json.JSONDecodeError, TypeError):
            return (selector_map_json, "")

        # Collect parent xpaths of kept elements for child-dedup
        kept_xpaths: Set[str] = set()
        kept_texts: Dict[str, str] = {}  # xpath -> inner_text of kept elements

        # First pass: decide keep/remove for each element
        keep_indexes: Set[int] = set()
        for idx_str, elem in elements.items():
            idx = int(idx_str)
            if self._should_keep(elem):
                keep_indexes.add(idx)
                xpath = elem.get("xpath", "")
                kept_xpaths.add(xpath)
                kept_texts[xpath] = (elem.get("inner_text") or "").strip()

        # Second pass: remove children whose text is a subset of an
        # already-kept parent's text (redundant nested elements)
        final_indexes: Set[int] = set()
        for idx in keep_indexes:
            elem = elements[str(idx)]
            if self._is_redundant_child(elem, kept_xpaths, kept_texts):
                continue
            final_indexes.add(idx)

        # Build outputs
        filtered_elements = {
            k: v for k, v in elements.items() if int(k) in final_indexes
        }
        filtered_json = json.dumps(filtered_elements, indent=2)
        filtered_string = self._build_string(filtered_elements)

        return (filtered_json, filtered_string)

    # ------------------------------------------------------------------
    # Filtering rules
    # ------------------------------------------------------------------

    def _should_keep(self, elem: dict) -> bool:
        """Return True if this element passes the rule-based filter."""
        tag = elem.get("tag_name", "").lower()
        attrs = elem.get("attributes", {})
        inner_text = (elem.get("inner_text") or "").strip()
        role = attrs.get("role", "").lower()

        # --- REMOVE rules (checked first) ---

        # 1. aria-hidden decorative elements
        if attrs.get("aria-hidden") == "true":
            return False

        # 2. Icon tags (<i>) are always decorative
        if tag == "i":
            return False

        # 3. Calendar day cells
        if tag == "td" and any(a in attrs for a in _CALENDAR_ATTRS):
            return False

        # 4. Elements whose inner_text is just a single digit/number
        #    (calendar day numbers, pagination fragments)
        if inner_text and re.fullmatch(r"\d{1,2}", inner_text):
            # Exception: form elements or buttons with numeric text are ok
            if tag not in _FORM_TAGS and tag not in _ACTION_TAGS:
                return False

        # --- KEEP rules ---

        # 5. Form elements are always useful
        if tag in _FORM_TAGS:
            return True

        # 6. Buttons are always useful
        if tag == "button":
            return True

        # 7. <a> tags
        if tag == "a":
            href = attrs.get("href", "")
            # Skip-links: href="#..." with "Skip" in text
            if href.startswith("#") and "skip" in inner_text.lower():
                return False
            # SPA links (href="#") with no text AND no id/data-test → decorative
            if href.startswith("#") and not inner_text and not role:
                has_id = bool(attrs.get("id"))
                has_data = any(k.startswith("data-") for k in attrs)
                if not has_id and not has_data:
                    return False
            # Everything else (including SPA links with text or data-test) is kept
            return True

        # 8. Elements with meaningful ARIA roles
        if role in _MEANINGFUL_ROLES:
            return True

        # 9. <div>/<span> without href, role, or form capability → remove
        if tag in ("span", "div"):
            return False

        # 10. Default: keep (be conservative with unknown element types)
        return True

    def _is_redundant_child(
        self,
        elem: dict,
        kept_xpaths: Set[str],
        kept_texts: Dict[str, str],
    ) -> bool:
        """
        Check if this element is a child of another kept element
        and its inner_text is a subset of the parent's text.
        """
        tag = elem.get("tag_name", "").lower()
        # Only dedup span/div children, never dedup links, buttons, inputs
        if tag not in ("span", "div"):
            return False

        parent_xpath = elem.get("parent", "")
        if not parent_xpath:
            return False

        elem_text = (elem.get("inner_text") or "").strip().lower()
        if not elem_text:
            return True  # Empty text child of a kept parent is redundant

        # Walk up the parent chain (simple check: direct parent only)
        if parent_xpath in kept_xpaths:
            parent_text = kept_texts.get(parent_xpath, "").lower()
            if elem_text in parent_text:
                return True

        return False

    # ------------------------------------------------------------------
    # Output formatting
    # ------------------------------------------------------------------

    def _build_string(self, elements: Dict[str, dict]) -> str:
        """Build human-readable selector map string from filtered elements."""
        _skip_attrs = {"class", "style"}
        lines = []

        for idx_str in sorted(elements.keys(), key=lambda x: int(x)):
            elem = elements[idx_str]
            tag = elem.get("tag_name", "")
            attrs = elem.get("attributes", {})
            inner_text = elem.get("inner_text") or ""

            # Build attribute string (skip class/style)
            attr_parts = []
            for k, v in attrs.items():
                if k not in _skip_attrs and v != "":
                    attr_parts.append(f"{k}='{v}'")
            attrs_str = " " + " ".join(attr_parts) if attr_parts else ""

            # Truncate inner_text
            if inner_text:
                inner_text = " ".join(inner_text.split())
                if len(inner_text) > 100:
                    inner_text = inner_text[:100] + "..."
            text_str = f" inner_text='{inner_text}'" if inner_text else ""

            lines.append(f"[{idx_str}]<{tag}{attrs_str}{text_str} />")

        return "\n".join(lines)
