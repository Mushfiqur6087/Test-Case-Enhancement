"""
Test Case Parser.

Reads a test-cases markdown file and produces a list of TestCase objects
grouped by module.

Expected format:
    ## 1. Login
    ### TC-001 — Title ✅ Positive | High
    | Field | Detail |
    | **Preconditions** | ... |
    | **Steps** | 1. step<br>2. step |
    | **Expected Result** | ... |
"""

import re
from typing import Dict, List

from intelligent_navigator.core.models import TestCase, TestStep

# Reuse the same URL hint table as DescriptionParser
_URL_HINTS: List[tuple] = [
    ("login",               "/login"),
    ("sign in",             "/login"),
    ("register",            "/register"),
    ("sign up",             "/register"),
    ("accounts overview",   "/dashboard"),
    ("account overview",    "/dashboard"),
    ("dashboard",           "/dashboard"),
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
]


def _infer_url(module_name: str) -> str:
    name_lower = module_name.lower().strip()
    for keyword, path in _URL_HINTS:
        if keyword in name_lower:
            return path
    slug = re.sub(r"[^a-z0-9]+", "-", name_lower).strip("-")
    return f"/{slug}"


def _parse_steps(steps_cell: str) -> List[TestStep]:
    """
    Parse the Steps table cell into individual TestStep objects.
    Handles both <br>-separated and plain numbered lists.
    """
    # Replace <br> variants with newlines
    text = re.sub(r"<br\s*/?>", "\n", steps_cell, flags=re.IGNORECASE)
    steps = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Match "1. step text" or "1) step text"
        m = re.match(r"^(\d+)[.)]\s+(.*)", line)
        if m:
            steps.append(TestStep(number=int(m.group(1)), description=m.group(2).strip()))
        elif steps:
            # Continuation of the previous step
            steps[-1] = TestStep(
                number=steps[-1].number,
                description=steps[-1].description + " " + line,
            )
    return steps


def _parse_table(tc_text: str) -> Dict[str, str]:
    """
    Extract Preconditions, Steps, Expected Result from the markdown table
    in a single test case block.
    """
    fields = {"preconditions": "", "steps": "", "expected_result": ""}
    for line in tc_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if len(cells) < 2:
            continue
        key = cells[0].lower().replace("**", "").strip()
        value = cells[1] if len(cells) > 1 else ""
        if "precondition" in key:
            fields["preconditions"] = value
        elif "step" in key:
            fields["steps"] = value
        elif "expected" in key:
            fields["expected_result"] = value
    return fields


class TestCaseParser:
    """Parses a test-cases markdown file into grouped TestCase objects."""

    def parse(self, markdown_text: str) -> List[TestCase]:
        """
        Parse the full markdown text and return a flat list of TestCase objects.
        Preserves module order; within each module preserves TC order.
        """
        test_cases: List[TestCase] = []

        # Split into module blocks on "## N. Module Name" headings
        module_pattern = re.compile(
            r"^##\s+\d+\.\s+(.+)$", re.MULTILINE
        )
        module_matches = list(module_pattern.finditer(markdown_text))

        for mi, mod_match in enumerate(module_matches):
            module_name = mod_match.group(1).strip()
            target_url = _infer_url(module_name)

            # Get the text belonging to this module
            mod_start = mod_match.end()
            mod_end = (
                module_matches[mi + 1].start()
                if mi + 1 < len(module_matches)
                else len(markdown_text)
            )
            mod_text = markdown_text[mod_start:mod_end]

            # Split module text on ### TC-XXX headings
            tc_pattern = re.compile(
                r"^###\s+(TC-\d+)\s+[—–-]+\s+(.+?)$", re.MULTILINE
            )
            tc_matches = list(tc_pattern.finditer(mod_text))

            for ti, tc_match in enumerate(tc_matches):
                tc_id = tc_match.group(1).strip()
                raw_title = tc_match.group(2).strip()

                # Parse type and priority from title: "Title ✅ Positive | High"
                tc_type, priority, title = _parse_heading_meta(raw_title)

                # Extract test case body
                tc_start = tc_match.end()
                tc_end = (
                    tc_matches[ti + 1].start()
                    if ti + 1 < len(tc_matches)
                    else len(mod_text)
                )
                tc_body = mod_text[tc_start:tc_end]

                fields = _parse_table(tc_body)
                steps = _parse_steps(fields["steps"])

                test_cases.append(TestCase(
                    tc_id=tc_id,
                    module=module_name,
                    title=title,
                    tc_type=tc_type,
                    priority=priority,
                    preconditions=fields["preconditions"],
                    steps=steps,
                    expected_result=fields["expected_result"],
                    target_url=target_url,
                ))

        return test_cases

    def group_by_module(self, test_cases: List[TestCase]) -> Dict[str, List[TestCase]]:
        """Return an ordered dict of module_name → [TestCase, ...]."""
        groups: Dict[str, List[TestCase]] = {}
        for tc in test_cases:
            groups.setdefault(tc.module, []).append(tc)
        return groups


def _parse_heading_meta(raw_title: str):
    """
    Extract (tc_type, priority, clean_title) from a heading like:
        "Successful sign-in with valid credentials ✅ Positive | High"
        "Authentication failure ❌ Negative | High"
        "Password at exact minimum ⚡ Edge/Boundary | Medium"
    """
    # Strip emoji characters
    clean = re.sub(r"[^\w\s|/—–\-.,()']", "", raw_title).strip()

    # Try "Title Positive | High" or "Title Edge/Boundary | Medium"
    m = re.search(
        r"(Positive|Negative|Edge[/\w]*)\s*\|\s*(High|Medium|Low)",
        clean,
        re.IGNORECASE,
    )
    if m:
        tc_type = m.group(1).strip()
        priority = m.group(2).strip()
        title = clean[: m.start()].strip().rstrip("-—– ")
        return tc_type, priority, title

    return "Unknown", "Medium", clean.strip()
