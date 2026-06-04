"""
Spec Checker Agent.

Given a SpecSection (from the functional description) and the live page's
DOM (selector map), asks an LLM to determine whether the page correctly
implements the spec.

Returns a SectionVerificationResult with:
  - verdict       : "pass" | "partial" | "fail"
  - compliance_score : 0-100
  - matches       : things the spec described that ARE present
  - missing       : things the spec described that are NOT present
  - mismatches    : things present that contradict the spec
  - notes         : brief narrative summary
"""

from intelligent_navigator.core.llm import LLMClient
from intelligent_navigator.core.models import SpecSection, SectionVerificationResult
from intelligent_navigator.core.utils import log, parse_llm_json
from intelligent_navigator.spec_verifier.prompts import (
    PROMPT_SPEC_CHECKER_SYSTEM,
    PROMPT_SPEC_CHECKER_CHECK,
)

# Maximum characters of the DOM context string sent to the checker LLM.
# We now send body text + full DOM, so this needs to be higher.
_MAX_SELECTOR_MAP_CHARS = 16_000


class SpecCheckerAgent:
    """
    Compares a spec section against the live page DOM using an LLM.

    One instance is shared across all section checks within a verification
    run (the LLM client is stateless between calls).
    """

    def __init__(
        self,
        llm_client: LLMClient,
        debug: bool = False,
        debug_file: str = None,
    ):
        self.debug = debug
        self.debug_file = debug_file
        self.llm_call_count = 0

        self.checker_llm = LLMClient(
            api_key=llm_client.api_key,
            model_name=llm_client.model_name,
            system_prompt=PROMPT_SPEC_CHECKER_SYSTEM,
            debug_file=debug_file,
        )

    def check(
        self,
        section: SpecSection,
        page_title: str,
        page_url: str,
        selector_map_string: str,
        actual_url: str = "",
        actual_title: str = "",
        screenshot_b64: str = None,
    ) -> SectionVerificationResult:
        """
        Run the spec check for one section against the current page DOM.

        Parameters
        ----------
        section            : the SpecSection being verified
        page_title         : title of the live page
        page_url           : URL of the live page
        selector_map_string: DOM selector map in human-readable form
        actual_url         : same as page_url (kept for result hydration)
        actual_title       : same as page_title (kept for result hydration)
        screenshot_b64     : optional base64 PNG screenshot for vision models

        Returns
        -------
        SectionVerificationResult
        """
        log(
            f"  [Checker] Checking section '{section.name}' against {page_url}"
            + (" [+screenshot]" if screenshot_b64 and self.checker_llm.is_vision else ""),
            self.debug, self.debug_file,
        )

        # Truncate the selector map so we don't blow the context window
        truncated_map = selector_map_string[:_MAX_SELECTOR_MAP_CHARS]
        if len(selector_map_string) > _MAX_SELECTOR_MAP_CHARS:
            truncated_map += "\n... (truncated)"

        prompt = PROMPT_SPEC_CHECKER_CHECK.format(
            section_name=section.name,
            spec_text=section.raw_text,
            page_title=page_title,
            page_url=page_url,
            page_content=truncated_map or "(empty page — no interactive elements found)",
        )

        try:
            if screenshot_b64 and self.checker_llm.is_vision:
                response = self.checker_llm.ask_with_screenshot(prompt, screenshot_b64)
            else:
                response = self.checker_llm.ask(prompt)
            self.llm_call_count += 1
            data = parse_llm_json(response)
        except Exception as e:
            log(
                f"  [Checker] LLM error for section '{section.name}': {e}",
                self.debug, self.debug_file,
            )
            self.llm_call_count += 1
            return SectionVerificationResult(
                section_name=section.name,
                actual_url=actual_url or page_url,
                actual_title=actual_title or page_title,
                verdict="fail",
                compliance_score=0,
                notes=f"Checker LLM error: {e}",
            )

        verdict = data.get("verdict", "fail")
        score = int(data.get("compliance_score", 0))
        matches = data.get("matches", [])
        missing = data.get("missing", [])
        mismatches = data.get("mismatches", [])
        notes = data.get("notes", "")

        # --- Normalise verdict to match our lenient thresholds ---
        # The LLM may apply its own threshold; we enforce ours so a 78-score
        # page isn't downgraded to "partial" just because the LLM was strict.
        if score >= 75:
            verdict = "pass"
        elif score >= 40:
            verdict = "partial"
        else:
            verdict = "fail"

        log(
            f"  [Checker] '{section.name}': {verdict.upper()} ({score}/100) | "
            f"{len(matches)} matches, {len(missing)} missing, {len(mismatches)} mismatches",
            self.debug, self.debug_file,
        )

        return SectionVerificationResult(
            section_name=section.name,
            actual_url=actual_url or page_url,
            actual_title=actual_title or page_title,
            verdict=verdict,
            compliance_score=score,
            matches=matches,
            missing=missing,
            mismatches=mismatches,
            notes=notes,
        )
