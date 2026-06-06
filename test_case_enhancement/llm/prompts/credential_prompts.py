"""Credential parsing prompts."""

PROMPT_CREDENTIAL_PARSING = """\
Extract all username/password/role entries from this credentials file.

{credentials_content}

Respond with ONLY valid JSON:
{{
  "credentials": [
    {{
      "username": "the username",
      "password": "the password",
      "role": "the role name"
    }}
  ]
}}\
"""
