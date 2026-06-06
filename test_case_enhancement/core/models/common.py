"""Common data models."""
from dataclasses import dataclass

@dataclass
class RoleCredentials:
    """Credentials for a single role."""
    username: str
    password: str
    role: str
