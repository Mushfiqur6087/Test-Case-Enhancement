"""Credential parsing for the exploration agent."""

from typing import List

from test_case_enhancement.core.models import RoleCredentials
from test_case_enhancement.core.utils import parse_llm_json, read_file_contents


class CredentialParser:
    """Parses credential files into structured RoleCredentials."""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def parse_credentials(self, credentials_file_path: str) -> List[RoleCredentials]:
        """Read and parse credentials file using LLM to extract structured data."""
        from test_case_enhancement.agents.prompts import PROMPT_CREDENTIAL_PARSING

        content = read_file_contents(credentials_file_path)
        if content.startswith("Error:"):
            print(f"  Warning: {content}")
            return []

        if not self.llm_client:
            return []

        prompt = PROMPT_CREDENTIAL_PARSING.format(credentials_content=content)

        try:
            response = self.llm_client.ask(prompt)
            result = parse_llm_json(response)
            creds_list = result.get("credentials", [])
        except Exception:
            return []

        credentials: List[RoleCredentials] = []
        for item in creds_list:
            username = item.get("username", "")
            password = item.get("password", "")
            role = item.get("role", "user")
            if username and password:
                credentials.append(RoleCredentials(
                    username=username,
                    password=password,
                    role=role.lower().strip(),
                ))

        return credentials

    def deduplicate_roles(self, credentials: List[RoleCredentials]) -> List[RoleCredentials]:
        """Keep only one account per unique role name."""
        seen_roles: set = set()
        unique: List[RoleCredentials] = []
        for cred in credentials:
            role_key = cred.role.lower().strip()
            if role_key not in seen_roles:
                seen_roles.add(role_key)
                unique.append(cred)
        return unique

    def format_credentials_for_prompt(self, credentials: List[RoleCredentials]) -> str:
        """Format credentials for the LLM prompt."""
        if not credentials:
            return "No credentials available."
        lines = ["Available Credentials:"]
        for cred in credentials:
            lines.append(f"  - Role: {cred.role}, Username: {cred.username}, Password: {cred.password}")
        return "\n".join(lines)
