"""
Description Parser.

Reads a functional-description markdown file (e.g. Parabank.md) and splits
it into SpecSection objects — one per ## heading.

No URL inference or auth heuristics. The agentic traversal system discovers
the real URL for each section by navigating the live application.
"""

import re
from typing import List, Optional, Tuple
from test_case_enhancement.core.models import SpecSection


class DescriptionParser:
    """
    Parses a functional-description markdown into SpecSection objects.

    Splits on ## headings. Each heading becomes one SpecSection containing
    the heading name and the raw markdown body text beneath it.
    The leading # (h1) title is ignored.

    Example
    -------
    Given Parabank.md with headings:
        # Functional Specification
        ## Navigation
        ## Login
        ## Register
        ...

    Returns SpecSection objects for: Login, Register, …
    (Navigation is skipped by default via skip_sections.)
    """

    def parse(
        self,
        markdown_text: str,
        skip_sections: Optional[List[str]] = None,
    ) -> Tuple[List[SpecSection], List[SpecSection]]:
        """
        Parse markdown text into a list of SpecSections and a list of skipped sections.

        Parameters
        ----------
        markdown_text : str
            Raw markdown content of the functional description.
        skip_sections : list[str], optional
            Section names to exclude (case-insensitive). Defaults to
            skipping generic overview sections like "Navigation".

        Returns
        -------
        Tuple[List[SpecSection], List[SpecSection]]
            (verified_sections, skipped_sections)
        """
        if skip_sections is None:
            skip_set = {"navigation"}
        else:
            skip_set = {s.lower().strip() for s in skip_sections}

        sections: List[SpecSection] = []
        skipped_sections: List[SpecSection] = []

        # Split on ## headings (h2 level only — ignore h1)
        pattern = re.compile(r"^## (.+)$", re.MULTILINE)
        matches = list(pattern.finditer(markdown_text))

        for i, match in enumerate(matches):
            heading = match.group(1).strip()

            # Grab body text (from just after this heading to the next heading)
            body_start = match.end()
            body_end = (
                matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
            )
            body = markdown_text[body_start:body_end].strip()

            if heading.lower().strip() in skip_set:
                skipped_sections.append(SpecSection(name=heading, raw_text=body))
                continue

            sections.append(SpecSection(name=heading, raw_text=body))

        return sections, skipped_sections
