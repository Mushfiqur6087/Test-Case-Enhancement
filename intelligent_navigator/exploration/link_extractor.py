"""Pure DOM-based link extraction. No LLM calls."""

import json
from typing import Any, Dict, List

from intelligent_navigator.exploration.page_identity import PageIdentityComputer


class LinkExtractor:
    """Extracts outgoing links from a page using pure DOM parsing."""

    LOGOUT_KEYWORDS = {
        "logout", "log out", "log_out", "signout", "sign out", "sign_out",
    }

    def __init__(self, base_url: str, page_identity_computer: PageIdentityComputer):
        self.base_url = base_url
        self.identity_computer = page_identity_computer

    def extract_links(
        self,
        selector_map_json: str,
        page_url: str,
    ) -> List[Dict[str, Any]]:
        """
        Extract all navigable links from the selector map JSON.
        Returns a flat list of dicts: {url, label, element_index, tag, is_logout}.
        """
        links: List[Dict[str, Any]] = []
        seen_urls: set = set()

        try:
            elements = json.loads(selector_map_json)
        except (json.JSONDecodeError, TypeError):
            return links

        for idx_str, elem in elements.items():
            tag = elem.get("tag_name", "")
            attrs = elem.get("attributes", {})
            inner_text = elem.get("inner_text", "").strip()
            href = attrs.get("href", "")

            if tag == "a" and href:
                resolved = self.identity_computer.resolve_url(href, page_url)

                if self.identity_computer.is_external(resolved):
                    continue
                if self.identity_computer.is_same_page_anchor(href):
                    continue

                if resolved in seen_urls:
                    continue
                seen_urls.add(resolved)

                is_logout = self._is_logout_link(resolved, inner_text)

                links.append({
                    "url": resolved,
                    "label": inner_text[:100] if inner_text else href[:100],
                    "element_index": int(idx_str),
                    "tag": tag,
                    "is_logout": is_logout,
                })

        return links

    def _is_logout_link(self, url: str, text: str) -> bool:
        """Check if a link is a logout link based on URL and text."""
        text_lower = text.lower()
        url_lower = url.lower()
        for keyword in self.LOGOUT_KEYWORDS:
            if keyword in text_lower or keyword in url_lower:
                return True
        return False
