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

from test_case_enhancement.llm.client import LLMClient
from test_case_enhancement.core.models import SpecSection, SectionVerificationResult
from test_case_enhancement.core.utils import log, parse_llm_json
from test_case_enhancement.llm.prompts import (
    PROMPT_COMPLIANCE_CHECKER_SYSTEM,
    PROMPT_COMPLIANCE_CHECKER_CHECK,
)

# Maximum characters of the DOM context string sent to the checker LLM.
# We now send body text + full DOM, so this needs to be higher.
_MAX_SELECTOR_MAP_CHARS = 16_000


class ComplianceCheckerAgent:
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
        """Initialize the __init__ method."""
        self.debug = debug
        self.debug_file = debug_file
        self.llm_call_count = 0

        self.checker_llm = LLMClient(
            api_key=llm_client.api_key,
            model_name=llm_client.model_name,
            system_prompt=PROMPT_COMPLIANCE_CHECKER_SYSTEM,
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
        before_screenshot_b64: str = None,
    ) -> SectionVerificationResult:
        """
        Run the spec check for one section against the current page DOM.

        Parameters
        ----------
        section              : the SpecSection being verified
        page_title           : title of the live page
        page_url             : URL of the live page
        selector_map_string  : DOM selector map / before+after context string
        actual_url           : same as page_url (kept for result hydration)
        actual_title         : same as page_title (kept for result hydration)
        screenshot_b64       : optional base64 PNG of the AFTER state
        before_screenshot_b64: optional base64 PNG of the BEFORE state.
                               When provided alongside screenshot_b64 for a
                               vision model, both are sent so the LLM can
                               visually diff before vs after for action steps.

        Returns
        -------
        SectionVerificationResult
        """
        has_before = bool(before_screenshot_b64 and self.checker_llm.is_vision)
        log(
            f"  [Checker] Checking section '{section.name}' against {page_url}"
            + (" [+before/after screenshots]" if has_before
               else " [+screenshot]" if screenshot_b64 and self.checker_llm.is_vision
               else ""),
            self.debug, self.debug_file,
        )

        # Truncate the selector map so we don't blow the context window
        truncated_map = selector_map_string[:_MAX_SELECTOR_MAP_CHARS]
        if len(selector_map_string) > _MAX_SELECTOR_MAP_CHARS:
            truncated_map += "\n... (truncated)"

        prompt = PROMPT_COMPLIANCE_CHECKER_CHECK.format(
            section_name=section.name,
            spec_text=section.raw_text,
            page_title=page_title,
            page_url=page_url,
            page_content=truncated_map or "(empty page — no interactive elements found)",
        )

        try:
            if has_before and screenshot_b64:
                # Vision action step: send before screenshot first, then after.
                # The LLM receives the before image as the "primary" screenshot
                # and sees the after state in the prompt text + second image.
                # We embed the after screenshot label into the prompt so the LLM
                # knows which image is which.
                labeled_prompt = (
                    "[IMAGE 1 = BEFORE the action] "
                    "[IMAGE 2 = AFTER the action]\n\n"
                    + prompt
                )
                response = self.checker_llm.ask_with_screenshot(
                    labeled_prompt, before_screenshot_b64
                )
                # Also send the after screenshot in a follow-up context note.
                # Since most LLM clients support only one image per call, we
                # fall back to using just the after screenshot when the client
                # doesn't support multi-image. The before URL/title in the text
                # still provides the diff signal.
                if not response or len(response) < 10:
                    response = self.checker_llm.ask_with_screenshot(prompt, screenshot_b64)
            elif screenshot_b64 and self.checker_llm.is_vision:
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
