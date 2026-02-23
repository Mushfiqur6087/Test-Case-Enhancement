"""
URL normalization and PageIdentity computation.
Classifies query params as data vs structural, replaces numeric IDs with
wildcards, and produces PageIdentity keys for page deduplication.
"""

import re
from typing import Dict, Tuple
from urllib.parse import parse_qs, urljoin, urlparse

from intelligent_navigator.core.models import PageIdentity


class PageIdentityComputer:
    """Computes PageIdentity from raw URLs using normalization rules."""

    DATA_PARAM_NAMES = {
        "id", "courseid", "cmid", "userid", "page", "offset",
        "itemid", "sesskey", "contextid", "groupid", "forumid",
        "discussionid", "assignid", "quizid", "attemptid",
    }

    STRUCTURAL_PARAM_NAMES = {
        "action", "mode", "view", "tab", "type",
        "section", "report", "display", "component",
    }

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.base_host = urlparse(base_url).netloc
        self._disambiguation_cache: Dict[str, str] = {}

    def compute(self, url: str, role: str) -> PageIdentity:
        """Compute the PageIdentity for a given URL and role."""
        normalized_path, structural_params, _ = self.normalize_path(url)
        return PageIdentity(
            role=role,
            normalized_path=normalized_path,
            structural_params=structural_params,
        )

    def normalize_path(self, url: str) -> Tuple[str, Dict[str, str], Dict[str, str]]:
        """
        Parse URL and separate structural params from data params.

        Returns:
            (normalized_path, structural_params, data_params)
        """
        parsed = urlparse(url)
        path = parsed.path or "/"

        if path != "/" and path.endswith("/"):
            path = path.rstrip("/")

        params = parse_qs(parsed.query, keep_blank_values=True)
        structural_params: Dict[str, str] = {}
        data_params: Dict[str, str] = {}

        for name, values in params.items():
            value = values[0] if values else ""
            param_type = self._classify_param(name, value)
            if param_type == "structural":
                structural_params[name] = value
            else:
                data_params[name] = "*"

        if data_params:
            wildcard_query = "&".join(
                f"{k}=*" for k in sorted(data_params.keys())
            )
            normalized_path = f"{path}?{wildcard_query}"
        else:
            normalized_path = path

        return normalized_path, structural_params, data_params

    def _classify_param(self, param_name: str, param_value: str) -> str:
        """Classify a query parameter as 'data' or 'structural'."""
        name_lower = param_name.lower()

        if name_lower in self._disambiguation_cache:
            return self._disambiguation_cache[name_lower]

        if name_lower in self.DATA_PARAM_NAMES:
            self._disambiguation_cache[name_lower] = "data"
            return "data"

        if name_lower in self.STRUCTURAL_PARAM_NAMES:
            self._disambiguation_cache[name_lower] = "structural"
            return "structural"

        if param_value and param_value.isdigit():
            self._disambiguation_cache[name_lower] = "data"
            return "data"

        self._disambiguation_cache[name_lower] = "structural"
        return "structural"

    def is_external(self, url: str) -> bool:
        """Check if URL points to a different host."""
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False
            return parsed.netloc != self.base_host
        except Exception:
            return True

    def is_same_page_anchor(self, url: str) -> bool:
        """Check if URL is a fragment-only link or javascript:void."""
        if not url:
            return True
        url_stripped = url.strip()
        if url_stripped.startswith("#"):
            return True
        if url_stripped.startswith("javascript:"):
            return True
        if url_stripped == "":
            return True
        return False

    def resolve_url(self, url: str, current_url: str) -> str:
        """Resolve a relative URL against the current page URL."""
        if not url:
            return current_url
        return urljoin(current_url, url)
