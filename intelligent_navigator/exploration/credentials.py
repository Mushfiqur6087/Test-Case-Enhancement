"""Credential parsing for the exploration agent."""

import json
from typing import List

from intelligent_navigator.core.models import RoleCredentials
from intelligent_navigator.core.utils import parse_llm_json, read_file_contents


class CredentialParser:
    """Parses credential files into structured RoleCredentials."""

    ROLE_PRIVILEGE_MAP = {
        "admin": 100, "administrator": 100, "site admin": 100,
        "manager": 80, "course creator": 70,
        "teacher": 60, "instructor": 60, "editing teacher": 60,
        "non-editing teacher": 50, "teaching assistant": 50,
        "student": 30, "learner": 30,
        "guest": 10,
        "user": 40,
    }

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def parse_credentials(self, credentials_file_path: str) -> List[RoleCredentials]:
        """Read and parse credentials file using LLM to extract structured data."""
        from intelligent_navigator.agents.prompts import PROMPT_CREDENTIAL_PARSING

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
                privilege = self._get_privilege_level(role)
                credentials.append(RoleCredentials(
                    username=username,
                    password=password,
                    role=role.lower().strip(),
                    privilege_level=privilege,
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

    def sort_by_privilege(self, credentials: List[RoleCredentials]) -> List[RoleCredentials]:
        """Sort by privilege level descending."""
        return sorted(credentials, key=lambda c: c.privilege_level, reverse=True)

    def format_credentials_for_prompt(self, credentials: List[RoleCredentials]) -> str:
        """Format credentials for the LLM exploration prompt."""
        if not credentials:
            return "No credentials available."
        lines = ["Available Credentials:"]
        for cred in credentials:
            lines.append(f"  - Role: {cred.role}, Username: {cred.username}, Password: {cred.password}")
        return "\n".join(lines)

    def _get_privilege_level(self, role: str) -> int:
        """Get privilege level for a role, defaulting to 40."""
        role_lower = role.lower().strip()
        for key, level in self.ROLE_PRIVILEGE_MAP.items():
            if key in role_lower or role_lower in key:
                return level
        return 40
