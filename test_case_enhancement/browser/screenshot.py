"""
Screenshot utility.

Captures a base64-encoded PNG screenshot from the current Playwright page.
Used by both the Spec Verifier and Test Case Verifier orchestrators to provide
visual context to vision-capable LLMs.
"""

import base64
from typing import Optional


def capture_screenshot_b64(browser_session) -> Optional[str]:
    """
    Take a full-page screenshot and return it as a base64 string.

    Returns None if the screenshot fails for any reason (so callers can
    gracefully fall back to text-only LLM calls).
    """
    try:
        page = browser_session.get_current_page()
        if page is None:
            return None
        png_bytes: bytes = page.screenshot(full_page=True)
        return base64.b64encode(png_bytes).decode("utf-8")
    except Exception:
        return None
