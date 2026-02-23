"""
Data models for the Exploration Agent.
All dataclasses used by the exploration pipeline.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class NodeState(Enum):
    UNDISCOVERED = "undiscovered"
    VISITED = "visited"
    FULLY_EXPLORED = "fully_explored"
    UNREACHABLE = "unreachable"


@dataclass
class PageIdentity:
    """Unique identifier for a page template. The core deduplication key."""
    role: str
    normalized_path: str
    structural_params: Dict[str, str]

    def __hash__(self) -> int:
        return hash((self.role, self.normalized_path,
                     frozenset(self.structural_params.items())))

    def __eq__(self, other) -> bool:
        if not isinstance(other, PageIdentity):
            return False
        return (self.role == other.role and
                self.normalized_path == other.normalized_path and
                self.structural_params == other.structural_params)

    def with_role(self, new_role: str) -> "PageIdentity":
        """Return a copy with a different role."""
        return PageIdentity(
            role=new_role,
            normalized_path=self.normalized_path,
            structural_params=dict(self.structural_params),
        )

    def to_key_string(self) -> str:
        """Deterministic string for serialization and display."""
        params_str = "&".join(
            f"{k}={v}" for k, v in sorted(self.structural_params.items())
        )
        return f"({self.role}){self.normalized_path}{'?' + params_str if params_str else ''}"


@dataclass
class NavigationEdge:
    """A directed edge in the navigation graph."""
    source_identity_key: str
    target_identity_key: str
    action_description: str
    source_url: str = ""
    target_url: str = ""


@dataclass
class NavigationNode:
    """A node in the navigation graph."""
    identity: PageIdentity
    state: NodeState = NodeState.UNDISCOVERED
    urls: List[str] = field(default_factory=list)
    title: str = ""


@dataclass
class RoleCredentials:
    """Credentials for a single role."""
    username: str
    password: str
    role: str
    privilege_level: int = 0


# ---- Queue models for LLM-guided exploration ----

@dataclass
class QueueItem:
    """An item in the exploration queue, managed by the LLM."""
    url: str
    label: str
    source_page: str  # URL of the page where this link was discovered
    reason: str  # LLM's reason for queuing this link


@dataclass
class ExplorationDecision:
    """Parsed LLM response for a single exploration step."""
    reasoning: str
    queue_additions: List[QueueItem]
    queue_removals: List[str]  # URLs to remove from queue (already visited or irrelevant)
    next_action: str  # "navigate" | "interact" | "go_back" | "done"
    target_url: Optional[str] = None  # For "navigate" action
    browser_actions: Optional[List[Dict[str, Any]]] = None  # For "interact" action


@dataclass
class ExplorationResult:
    """The final output structure — navigation graph + exploration metadata."""
    project_url: str
    captured_at: str
    roles_explored: List[str]
    navigation_graph: Dict[str, Any]
    exploration_stats: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dict for JSON output."""
        return {
            "project_url": self.project_url,
            "captured_at": self.captured_at,
            "roles_explored": self.roles_explored,
            "navigation_graph": self.navigation_graph,
            "exploration_stats": self.exploration_stats,
        }


# ---- Three-Agent Communication Models ----

@dataclass
class NavigatorCommand:
    """Command sent from Navigator Agent → Page Navigator.

    command_type:
        - explore_page: navigate to target_url, then Page Explorer takes over
        - login: navigate to target_url (login page) and fill credentials
        - logout: click the logout link on the current page
        - done: exploration complete, stop
    """
    command_type: str  # "explore_page" | "login" | "logout" | "done"
    target_url: str = ""
    target_label: str = ""
    credentials: Optional[RoleCredentials] = None
    reasoning: str = ""


@dataclass
class PageNavigatorResult:
    """Result returned from Page Navigator → orchestrator."""
    success: bool
    current_url: str = ""
    current_title: str = ""
    failure_reason: str = ""
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    retry_attempted: bool = False


@dataclass
class SubStateInfo:
    """Summary of a single sub-state discovered by Page Explorer."""
    trigger_description: str
    trigger_type: str  # "tab" | "modal" | "dropdown" | "collapsible" | "radio" | etc.
    new_links: List[Dict[str, Any]] = field(default_factory=list)  # links revealed


@dataclass
class PageExplorerResult:
    """Result returned from Page Explorer → Navigator Agent."""
    current_url: str
    current_title: str
    links_found: List[Dict[str, Any]] = field(default_factory=list)
    sub_states_found: List[SubStateInfo] = field(default_factory=list)
    page_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NavigatorDecision:
    """Parsed LLM response from the Navigator Agent."""
    reasoning: str
    next_action: str  # "explore_page" | "login" | "logout" | "done"
    target_url: str = ""
    target_label: str = ""
    credential_role: str = ""  # which role to login as
    queue_additions: List[QueueItem] = field(default_factory=list)
    queue_removals: List[str] = field(default_factory=list)


# ---- Sub-state exploration models (used by SubStateExplorer / PageExplorer) ----

@dataclass
class PageSnapshot:
    """A captured snapshot of a page's state."""
    url: str
    title: str
    selector_map_json: str
    selector_map_string: str


@dataclass
class SubStateSnapshot:
    """A snapshot of a sub-state revealed by a trigger interaction."""
    trigger_description: str
    trigger_element_index: int
    trigger_type: str
    selector_map_json: str = ""
    new_links_found: List[str] = field(default_factory=list)
