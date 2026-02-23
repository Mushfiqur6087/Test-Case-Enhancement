"""
URL normalization and PageIdentity computation.
Implements the rules from Architecture Section 8: parse URLs, classify query params
as data vs structural, replace numeric IDs with wildcards, and produce PageIdentity keys.
"""

import json
import re
import os
import sys
from typing import Dict, Optional, Tuple
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, PROJECT_ROOT)

from test_case_enhancer.agent.exploration_agent.models import PageIdentity


class PageIdentityComputer:
    """Computes PageIdentity from raw URLs using normalization rules."""

    # Parameters that are almost always data selectors (not structural)
    DATA_PARAM_NAMES = {
        "id", "courseid", "cmid", "userid", "page", "offset",
        "itemid", "sesskey", "contextid", "groupid", "forumid",
        "discussionid", "assignid", "quizid", "attemptid",
    }

    # Parameters that typically change page structure
    STRUCTURAL_PARAM_NAMES = {
        "action", "mode", "view", "tab", "type",
        "section", "report", "display", "component",
    }

    def __init__(self, base_url: str, llm_client=None):
        self.base_url = base_url
        self.base_host = urlparse(base_url).netloc
        self.llm_client = llm_client
        self._disambiguation_cache: Dict[str, str] = {}

    def compute(self, url: str, role: str) -> PageIdentity:
        """
        Compute the PageIdentity for a given URL and role.

        Steps:
        1. Parse URL into path + params
        2. Classify each param as data or structural
        3. Replace numeric data param values with *
        4. Return PageIdentity
        """
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
            - normalized_path: URL path with numeric data param values replaced by *
            - structural_params: only params that change page structure
            - data_params: params that select data items (values replaced by *)
        """
        parsed = urlparse(url)
        path = parsed.path or "/"

        # Remove trailing slash for consistency (except root)
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

        # Build normalized path: path + data params with wildcard values
        if data_params:
            wildcard_query = "&".join(
                f"{k}=*" for k in sorted(data_params.keys())
            )
            normalized_path = f"{path}?{wildcard_query}"
        else:
            normalized_path = path

        return normalized_path, structural_params, data_params

    def _classify_param(self, param_name: str, param_value: str) -> str:
        """
        Classify a query parameter as 'data' or 'structural'.
        Uses name-based heuristic first, LLM fallback for ambiguous cases.
        """
        name_lower = param_name.lower()

        # Check the cache first
        if name_lower in self._disambiguation_cache:
            return self._disambiguation_cache[name_lower]

        # Name-based heuristic: known data params
        if name_lower in self.DATA_PARAM_NAMES:
            self._disambiguation_cache[name_lower] = "data"
            return "data"

        # Name-based heuristic: known structural params
        if name_lower in self.STRUCTURAL_PARAM_NAMES:
            self._disambiguation_cache[name_lower] = "structural"
            return "structural"

        # Heuristic: if the value is purely numeric, it's likely a data ID
        if param_value and param_value.isdigit():
            self._disambiguation_cache[name_lower] = "data"
            return "data"

        # Default: treat unknown non-numeric params as structural
        self._disambiguation_cache[name_lower] = "structural"
        return "structural"

    def llm_disambiguate_param(
        self, param_name: str, url1: str, url2: str, context: str = ""
    ) -> str:
        """
        LLM call to determine if a param is structural or data.
        Only called explicitly when automatic heuristic isn't confident.
        """
        if not self.llm_client:
            return "data"

        prompt = PROMPT_PAGE_IDENTITY_DISAMBIGUATION.format(
            param_name=param_name,
            url1=url1,
            url2=url2,
            context=context,
        )

        try:
            response = self.llm_client.ask(prompt)
            result = self._parse_json(response)
            param_type = result.get("param_type", "data")
            self._disambiguation_cache[param_name.lower()] = param_type
            return param_type
        except Exception:
            return "data"

    def is_external(self, url: str) -> bool:
        """Check if URL points to a different host."""
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False  # Relative URL -> internal
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

    def _parse_json(self, response: str) -> Dict:
        """Parse JSON from LLM response, handling markdown code blocks."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
