"""
Link Discovery Agent.

Given the current live page, this agent:
  1. Exposes hidden navigation (dropdowns, hover menus, hamburger toggles)
     by triggering hover/click actions on nav elements.
  2. Extracts all visible links from the fully-expanded DOM.
  3. Asks an LLM to rank which links most likely lead to each unvisited
     spec section.

Returns a ranked list of CandidateLink objects (confidence ≥ 60 only).
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from intelligent_navigator.core.llm import LLMClient
from intelligent_navigator.core.models import SpecSection
from intelligent_navigator.core.utils import log, parse_llm_json, wait_for_page
from intelligent_navigator.browser.dom_helper import DOMHelper
from intelligent_navigator.agents.prompts import (
    PROMPT_LINK_DISCOVERY_SYSTEM,
    PROMPT_LINK_DISCOVERY_USER,
)

_CONFIDENCE_THRESHOLD = 60
_MAX_LINKS = 80           # cap number of links sent to LLM
_MAX_SECTION_DESC = 300   # chars per section in the unvisited list


@dataclass
class CandidateLink:
    """A link on the current page that likely leads to a spec section."""
    section: str      # SpecSection.name this link is a candidate for
    href: str         # href value of the link
    link_text: str    # anchor text
    confidence: int   # 0-100


# Nav toggle selectors to try clicking/hovering to expose hidden menus.
# These are common patterns across many web frameworks.
_NAV_TOGGLE_PATTERNS = [
    "[aria-haspopup]",
    "[aria-expanded]",
    "button[class*='menu']",
    "button[class*='nav']",
    "button[class*='toggle']",
    "button[class*='hamburger']",
    "[class*='dropdown-toggle']",
    "[class*='nav-toggle']",
    "nav button",
]


class LinkDiscoveryAgent:
    """
    Discovers which links on the current page lead to unvisited spec sections.

    Handles dropdown/hover menus by triggering nav toggle elements before
    extracting the full link list.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        browser_controller,
        browser_session,
        dom_helper: DOMHelper,
        debug: bool = False,
        debug_file: Optional[str] = None,
    ):
        self.browser_controller = browser_controller
        self.browser_session = browser_session
        self.dom_helper = dom_helper
        self.debug = debug
        self.debug_file = debug_file
        self.llm_call_count = 0

        self._llm = LLMClient(
            api_key=llm_client.api_key,
            model_name=llm_client.model_name,
            system_prompt=PROMPT_LINK_DISCOVERY_SYSTEM,
            debug_file=debug_file,
        )

    def discover(
        self,
        current_url: str,
        current_title: str,
        unvisited_sections: List[SpecSection],
    ) -> List[CandidateLink]:
        """
        Expose hidden menus, extract links, and rank them against unvisited sections.

        Parameters
        ----------
        current_url        : URL of the current page
        current_title      : title of the current page
        unvisited_sections : spec sections not yet visited

        Returns
        -------
        List of CandidateLink objects sorted by confidence (descending).
        """
        if not unvisited_sections:
            return []

        # Step 1: Expand hidden nav menus
        self._expand_nav_menus()

        # Step 2: Extract all links from the fully-expanded DOM
        links = self._extract_links()
        if not links:
            log(
                "  [LinkDiscovery] No links found on page.",
                self.debug, self.debug_file,
            )
            return []

        log(
            f"  [LinkDiscovery] Found {len(links)} links. "
            f"Matching against {len(unvisited_sections)} unvisited sections...",
            self.debug, self.debug_file,
        )

        # Step 3: Ask LLM to match links → sections
        candidates = self._ask_llm(current_url, current_title, links, unvisited_sections)

        log(
            f"  [LinkDiscovery] {len(candidates)} candidate(s) found: "
            + ", ".join(f"{c.section} [{c.confidence}%]" for c in candidates),
            self.debug, self.debug_file,
        )

        return candidates

    # ----------------------------------------------------------------
    # Dropdown / Menu Expansion
    # ----------------------------------------------------------------

    def _expand_nav_menus(self) -> None:
        """
        Try to expand hidden nav menus by hovering/clicking toggle elements.
        Uses JavaScript to find and activate common nav toggle patterns.
        """
        try:
            page = self.browser_session.get_current_page()
            if page is None:
                return

            expanded_any = False
            for pattern in _NAV_TOGGLE_PATTERNS:
                try:
                    elements = page.query_selector_all(pattern)
                    for el in elements[:3]:  # limit to first 3 per pattern
                        try:
                            el.hover(timeout=1000)
                            page.wait_for_timeout(150)
                            expanded_any = True
                        except Exception:
                            pass
                except Exception:
                    continue

            if expanded_any:
                page.wait_for_timeout(300)
                log(
                    "  [LinkDiscovery] Nav menus expanded.",
                    self.debug, self.debug_file,
                )
        except Exception as e:
            log(
                f"  [LinkDiscovery] Nav expansion skipped: {e}",
                self.debug, self.debug_file,
            )

    # ----------------------------------------------------------------
    # Link Extraction
    # ----------------------------------------------------------------

    def _extract_links(self) -> List[Dict[str, str]]:
        """
        Extract all anchor links from the current page via JavaScript.
        Returns list of {"text": ..., "href": ...} dicts.
        """
        try:
            page = self.browser_session.get_current_page()
            if page is None:
                return []

            raw_links: List[Dict[str, str]] = page.evaluate("""
                () => {
                    const seen = new Set();
                    const results = [];
                    document.querySelectorAll('a[href]').forEach(a => {
                        const href = a.href || a.getAttribute('href') || '';
                        const text = (a.innerText || a.textContent || '').trim();
                        // Skip empty, anchor-only, javascript:, and mailto: links
                        if (!href || href.startsWith('#') ||
                            href.startsWith('javascript:') ||
                            href.startsWith('mailto:')) return;
                        const key = href + '::' + text;
                        if (seen.has(key)) return;
                        seen.add(key);
                        results.push({ text: text.slice(0, 80), href: href });
                    });
                    return results;
                }
            """)
            return raw_links[:_MAX_LINKS]
        except Exception as e:
            log(
                f"  [LinkDiscovery] Link extraction failed: {e}",
                self.debug, self.debug_file,
            )
            return []

    # ----------------------------------------------------------------
    # LLM Matching
    # ----------------------------------------------------------------

    def _ask_llm(
        self,
        current_url: str,
        current_title: str,
        links: List[Dict[str, str]],
        unvisited_sections: List[SpecSection],
    ) -> List[CandidateLink]:
        """Ask the LLM to match the link list against unvisited spec sections."""
        links_list = self._format_links(links)
        unvisited_str = self._format_unvisited(unvisited_sections)

        prompt = PROMPT_LINK_DISCOVERY_USER.format(
            current_url=current_url,
            current_title=current_title,
            links_list=links_list,
            unvisited_sections=unvisited_str,
        )

        try:
            response = self._llm.ask(prompt)
            self.llm_call_count += 1
            data = parse_llm_json(response)
        except Exception as e:
            log(f"  [LinkDiscovery] LLM error: {e}", self.debug, self.debug_file)
            self.llm_call_count += 1
            return []

        valid_section_names = {s.name for s in unvisited_sections}
        candidates: List[CandidateLink] = []
        seen_sections: set = set()

        for item in data.get("candidates", []):
            section = item.get("section", "")
            href = item.get("href", "")
            link_text = item.get("link_text", "")
            confidence = int(item.get("confidence", 0))

            # Validate
            if not section or not href:
                continue
            if section not in valid_section_names:
                continue
            if section in seen_sections:
                continue
            if confidence < _CONFIDENCE_THRESHOLD:
                continue

            candidates.append(CandidateLink(
                section=section,
                href=href,
                link_text=link_text,
                confidence=confidence,
            ))
            seen_sections.add(section)

        # Sort by confidence descending
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        return candidates

    # ----------------------------------------------------------------
    # Formatting Helpers
    # ----------------------------------------------------------------

    def _format_links(self, links: List[Dict[str, str]]) -> str:
        lines = []
        for i, link in enumerate(links, 1):
            text = link.get("text", "").strip() or "(no text)"
            href = link.get("href", "")
            lines.append(f"{i}. [{text}]({href})")
        return "\n".join(lines)

    def _format_unvisited(self, sections: List[SpecSection]) -> str:
        lines = []
        for s in sections:
            desc = s.raw_text[:_MAX_SECTION_DESC].replace("\n", " ").strip()
            if len(s.raw_text) > _MAX_SECTION_DESC:
                desc += "..."
            lines.append(f"- **{s.name}**: {desc}")
        return "\n".join(lines)
