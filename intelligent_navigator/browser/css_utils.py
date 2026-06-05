"""
CSS selector utilities for safe element targeting.

Handles element IDs that contain CSS-special characters (`.`, `()`, `#`, `:`,
`[]`, etc.) by using attribute selectors instead of bare `#id` selectors.

Background:
  Many real-world applications generate HTML element IDs containing dots,
  parentheses, or other characters that are structural tokens in CSS selector
  syntax.  For example, Sauce Demo produces IDs like:

      add-to-cart-test.allthethings()-t-shirt-(red)

  Using this raw in `#add-to-cart-test.allthethings()-t-shirt-(red)` causes
  Playwright's CSS parser to choke because `.` starts a class selector and
  `()` is invalid syntax.

  The `[id="..."]` attribute selector treats the value as a plain quoted
  string, making all those characters harmless.  Only `\\` and `"` need
  escaping inside the quoted value (extremely rare in HTML IDs).
"""

import re

# IDs matching this pattern are safe for direct #id CSS selectors:
# must start with a letter/underscore, contain only [a-zA-Z0-9_-]
_SAFE_CSS_ID = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_-]*$')


def css_id_selector(elem_id: str) -> str:
    """Build a CSS selector that targets an element by its ID.

    Simple IDs (e.g., ``login-button``) produce the fast ``#login-button``
    form.  IDs containing CSS-special characters fall back to the attribute
    selector ``[id="..."]`` which is immune to parsing issues.

    Parameters
    ----------
    elem_id : str
        The raw HTML ``id`` attribute value.

    Returns
    -------
    str
        A valid CSS selector string.

    Examples
    --------
    >>> css_id_selector("login-button")
    '#login-button'
    >>> css_id_selector("add-to-cart-test.allthethings()-t-shirt-(red)")
    '[id="add-to-cart-test.allthethings()-t-shirt-(red)"]'
    """
    if _SAFE_CSS_ID.match(elem_id):
        return f"#{elem_id}"
    # Escape only backslash and double-quote inside the attribute value
    escaped = elem_id.replace('\\', '\\\\').replace('"', '\\"')
    return f'[id="{escaped}"]'
