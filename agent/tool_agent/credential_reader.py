"""
Credential Reader Tool
Reads a credentials/data markdown file and uses the LLM to match
relevant data values to the form fields detected on the page.
"""

import os
import json
from typing import Dict, Any, Optional


class CredentialReader:
    """
    Reads a credentials.md file and uses the LLM to extract
    relevant field values based on the page's form elements.
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def read_credentials_file(self, file_path: str) -> str:
        """
        Read the raw contents of a credentials/data markdown file.

        Args:
            file_path: Absolute or relative path to the .md file

        Returns:
            The file contents as a string, or an error message
        """
        try:
            if not os.path.isfile(file_path):
                return f"Error: File not found at {file_path}"
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def match_credentials_to_fields(
        self,
        credentials_content: str,
        form_fields_json: str,
        page_context: Dict[str, Any],
        llm_client=None,
    ) -> Dict[str, Any]:
        """
        Use the LLM to match data from the credentials file to the
        detected form fields on the page.

        Args:
            credentials_content: Raw text from the credentials.md file
            form_fields_json: JSON string of interactive elements on the page
            page_context: Dict with url, page_title, etc.
            llm_client: Optional override LLM client

        Returns:
            Dict mapping each form field to its matched value
        """
        active_llm = llm_client or self.llm_client
        if not active_llm:
            return {"error": "No LLM client available"}

        prompt = f"""
You are a test data matcher. Given a dataset of available credentials/test data and a list of form fields from a web page, select the most appropriate value for EACH form field.

# Available Test Data
{credentials_content}

# Page Context
URL: {page_context.get('url', 'Unknown')}
Page Title: {page_context.get('page_title', 'Unknown')}

# Form Fields Detected on the Page (JSON)
{form_fields_json}

# Task
For each form field, pick the best matching value from the test data above.
Match by field name, id, type, and placeholder text.

Respond with ONLY a valid JSON object in this format:
{{
  "matched_fields": [
    {{
      "field_id": "the id or name attribute of the field",
      "field_description": "human-readable description (e.g. 'Email input')",
      "css_selector": "CSS selector for this field",
      "matched_value": "the value to fill in from the credentials data",
      "match_reason": "brief reason why this value was chosen"
    }}
  ],
  "unmatched_fields": [
    {{
      "field_id": "id or name of fields that could not be matched",
      "field_description": "description",
      "reason": "why no match was found"
    }}
  ]
}}

Rules:
- Only match fields that are fillable (input, textarea, select)
- Skip buttons, submit elements, and non-fillable elements
- If a field has type="password" and there is a confirm password field, use the SAME password for both
- Pick the most contextually appropriate data category (e.g. "Valid User" for a signup form)
- If no suitable data exists for a field, put it in unmatched_fields
"""

        try:
            response = active_llm.ask(prompt)

            # Parse JSON
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:]
                if response.endswith("```"):
                    response = response[:-3]
                try:
                    result = json.loads(response.strip())
                except json.JSONDecodeError:
                    result = {"raw_response": response, "parse_error": True}

            return result

        except Exception as e:
            return {"error": f"Credential matching failed: {e}"}
