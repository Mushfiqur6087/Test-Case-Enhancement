"""
Page Identifier Agent.

Given the current live page (title, URL, body text, DOM elements) and the
full list of spec sections, determines which spec section this page implements.

Returns the best-matching section name (or None) with a confidence score.
Confidence threshold: 60 — below that it is treated as no match.
"""

from typing import Optional, Dict, Any, List, Tuple
import json

from test_case_enhancement.llm.client import LLMClient
from test_case_enhancement.core.utils import log, parse_llm_json
from test_case_enhancement.llm.prompts import (
    PROMPT_STATE_IDENTIFIER_SYSTEM,
    PROMPT_STATE_IDENTIFIER_USER,
)
from test_case_enhancement.core.models import SpecSection

_CONFIDENCE_THRESHOLD = 60
_MAX_PAGE_CONTENT_CHARS = 8_000
_MAX_SECTION_DESC_CHARS = 400  # per section in the sections list


class StateIdentifierAgent:
    """
    Matches a live page against a list of spec sections using an LLM.

    One instance is shared across the full traversal run.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        debug: bool = False,
        debug_file: Optional[str] = None,
    ):
        """Initialize the __init__ method."""
        self.debug = debug
        self.debug_file = debug_file
        self.llm_call_count = 0

        self._llm = LLMClient(
            api_key=llm_client.api_key,
            model_name=llm_client.model_name,
            system_prompt=PROMPT_STATE_IDENTIFIER_SYSTEM,
            debug_file=debug_file,
        )

    def identify(
        self,
        current_url: str,
        current_title: str,
        page_content: str,
        all_sections: List[SpecSection],
    ) -> Tuple[Optional[str], int]:
        """
        Identify which spec section (if any) the current page implements.

        Parameters
        ----------
        current_url   : live page URL
        current_title : live page title
        page_content  : visible body text + DOM selector map string (combined)
        all_sections  : all SpecSection objects (visited + unvisited)

        Returns
        -------
        (section_name, confidence)
            section_name is None if no confident match was found.
        """
        if not all_sections:
            return None, 0

        sections_list = self._format_sections_list(all_sections)
        truncated_content = page_content[:_MAX_PAGE_CONTENT_CHARS]

        prompt = PROMPT_STATE_IDENTIFIER_USER.format(
            current_url=current_url,
            current_title=current_title,
            page_content=truncated_content or "(empty page)",
            sections_list=sections_list,
        )

        try:
            response = self._llm.ask(prompt)
            self.llm_call_count += 1
            data = parse_llm_json(response)
        except Exception as e:
            log(f"  [StateIdentifier] LLM error: {e}", self.debug, self.debug_file)
            self.llm_call_count += 1
            return None, 0

        matched = data.get("matched_section")
        confidence = int(data.get("confidence", 0))
        reasoning = data.get("reasoning", "")

        # Validate the returned section name exists in our list
        valid_names = {s.name for s in all_sections}
        if matched and matched not in valid_names:
            log(
                f"  [StateIdentifier] LLM returned unknown section '{matched}' — ignoring.",
                self.debug, self.debug_file,
            )
            matched = None
            confidence = 0

        if confidence < _CONFIDENCE_THRESHOLD:
            matched = None

        log(
            f"  [StateIdentifier] '{current_title}' ({current_url}) → "
            f"{'«' + matched + '»' if matched else 'no match'} "
            f"[{confidence}%] — {reasoning[:80]}",
            self.debug, self.debug_file,
        )

        return matched, confidence

    def _format_sections_list(self, sections: List[SpecSection]) -> str:
        """Format spec sections for inclusion in the LLM prompt."""
        lines = []
        for s in sections:
            desc_excerpt = s.raw_text[:_MAX_SECTION_DESC_CHARS].replace("\n", " ").strip()
            if len(s.raw_text) > _MAX_SECTION_DESC_CHARS:
                desc_excerpt += "..."
            lines.append(f"- **{s.name}**: {desc_excerpt}")
        return "\n".join(lines)
