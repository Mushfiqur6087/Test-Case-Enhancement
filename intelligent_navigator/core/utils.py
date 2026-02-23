"""Shared utility functions used across the intelligent_navigator package."""

import json
import os
from typing import Dict, Optional


def parse_llm_json(response: str) -> Dict:
    """Parse JSON from an LLM response, handling markdown code blocks."""
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


def log(message: str, debug: bool = False, debug_file: Optional[str] = None) -> None:
    """Print to console and optionally append to a debug file."""
    print(message)
    if debug and debug_file:
        try:
            with open(debug_file, "a", encoding="utf-8") as f:
                f.write(f"{message}\n")
        except Exception:
            pass


def wait_for_page(browser_session, timeout: int = 1000) -> None:
    """Wait for the current page to stabilize after navigation."""
    try:
        page = browser_session.get_current_page()
        if page:
            page.wait_for_timeout(timeout)
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass
    except Exception:
        pass


def get_current_url(browser_session, fallback: str = "") -> str:
    """Get the current page URL safely."""
    try:
        page = browser_session.get_current_page()
        return page.url if page else fallback
    except Exception:
        return fallback


def get_current_title(browser_session) -> str:
    """Get the current page title safely."""
    try:
        page = browser_session.get_current_page()
        return page.title() if page else ""
    except Exception:
        return ""


def read_file_contents(file_path: str) -> str:
    """Read the raw contents of a file. Returns error string on failure."""
    try:
        if not os.path.isfile(file_path):
            return f"Error: File not found at {file_path}"
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"
