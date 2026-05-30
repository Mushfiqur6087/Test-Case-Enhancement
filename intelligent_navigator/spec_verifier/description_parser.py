"""
Description Parser.

Reads a functional-description markdown file (e.g. Parabank.md) and splits
it into SpecSection objects -- one per ## heading.

For each section it also infers:
  - url_hint  : a best-guess URL path (e.g. "Login" → "/login")
  - requires_auth : whether this section is likely behind a login wall

URL inference is intentionally loose; the Navigator confirms the real URL
by clicking through the app.
"""

import re
from typing import List

from intelligent_navigator.core.models import SpecSection

# ------------------------------------------------------------------ #
# Keyword → URL fragment mapping (lower-case keys)                   #
# ------------------------------------------------------------------ #
_URL_HINTS: List[tuple] = [
    # Auth / public pages
    ("login",               "/login"),
    ("sign in",             "/login"),
    ("sign-in",             "/login"),
    ("register",            "/register"),
    ("sign up",             "/register"),
    ("forgot password",     "/forgot-password"),
    ("password reset",      "/forgot-password"),

    # Common dashboard patterns
    ("accounts overview",   "/dashboard"),
    ("account overview",    "/dashboard"),
    ("dashboard",           "/dashboard"),
    ("home",                "/"),

    # Banking-domain sections (Parabank-style)
    ("open new account",    "/open-account"),
    ("open account",        "/open-account"),
    ("transfer funds",      "/transfer"),
    ("transfer",            "/transfer"),
    ("bill pay",            "/bill-pay"),
    ("payments",            "/bill-pay"),
    ("request loan",        "/loan"),
    ("loan",                "/loan"),
    ("update contact",      "/profile"),
    ("contact info",        "/profile"),
    ("profile",             "/profile"),
    ("manage cards",        "/cards"),
    ("cards",               "/cards"),
    ("investments",         "/investments"),
    ("account statements",  "/statements"),
    ("statements",          "/statements"),
    ("security settings",   "/security"),
    ("security",            "/security"),
    ("support center",      "/support"),
    ("support",             "/support"),
    ("settings",            "/settings"),
    ("admin",               "/admin"),
]

# Sections whose names suggest they require a logged-in user
_AUTH_REQUIRED_KEYWORDS = {
    "dashboard", "overview", "account", "transfer", "payment", "bill pay",
    "loan", "profile", "contact", "card", "investment", "statement",
    "security", "support center", "settings", "logout", "log out",
}


def _infer_url_hint(section_name: str) -> str:
    """Return a best-guess URL path for this section name."""
    name_lower = section_name.lower().strip()
    for keyword, path in _URL_HINTS:
        if keyword in name_lower:
            return path
    # Fallback: slugify the section name
    slug = re.sub(r"[^a-z0-9]+", "-", name_lower).strip("-")
    return f"/{slug}"


def _requires_auth(section_name: str) -> bool:
    """Heuristic: does this section require authentication?"""
    name_lower = section_name.lower()
    for kw in _AUTH_REQUIRED_KEYWORDS:
        if kw in name_lower:
            return True
    return False


class DescriptionParser:
    """
    Parses a functional-description markdown into SpecSection objects.

    Splits on ## headings. Each heading becomes one SpecSection.
    The leading # (h1) title is ignored.

    Example
    -------
    Given Parabank.md with headings:
        # Functional Specification
        ## Navigation
        ## Login
        ## Register
        ...

    Returns SpecSection objects for: Navigation, Login, Register, …
    """

    def parse(self, markdown_text: str, skip_sections: List[str] = None) -> List[SpecSection]:
        """
        Parse markdown text into a list of SpecSections.

        Parameters
        ----------
        markdown_text : str
            Raw markdown content of the functional description.
        skip_sections : list[str], optional
            Section names to exclude (case-insensitive). Defaults to
            skipping generic overview sections like "Navigation".

        Returns
        -------
        list[SpecSection]
        """
        if skip_sections is None:
            skip_sections = {"navigation"}
        else:
            skip_sections = {s.lower().strip() for s in skip_sections}

        sections: List[SpecSection] = []

        # Split on ## headings (h2 level only — ignore h1)
        # Pattern captures heading name and everything until the next ## or EOF
        pattern = re.compile(r"^## (.+)$", re.MULTILINE)
        matches = list(pattern.finditer(markdown_text))

        for i, match in enumerate(matches):
            heading = match.group(1).strip()

            # Skip unwanted sections
            if heading.lower().strip() in skip_sections:
                continue

            # Grab body text (from just after this heading to the next heading)
            body_start = match.end()
            body_end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
            body = markdown_text[body_start:body_end].strip()

            sections.append(SpecSection(
                name=heading,
                raw_text=body,
                url_hint=_infer_url_hint(heading),
                requires_auth=_requires_auth(heading),
            ))

        return sections
