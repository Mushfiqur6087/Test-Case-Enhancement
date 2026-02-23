"""
Directed navigation graph that grows as exploration proceeds.
Nodes are PageIdentity keys, edges are navigation actions.
"""

from typing import Any, Dict, List, Optional

from test_case_enhancer.agent.exploration_agent.models import (
    NavigationEdge,
    NavigationNode,
    NodeState,
    PageIdentity,
)


class NavigationGraph:
    """The central navigation graph built during exploration."""

    def __init__(self):
        self._nodes: Dict[str, NavigationNode] = {}  # key = PageIdentity.to_key_string()
        self._edges: List[NavigationEdge] = []

    def add_node(
        self,
        identity: PageIdentity,
        title: str = "",
        state: Optional[NodeState] = None,
    ) -> NavigationNode:
        """Add or update a node."""
        key = identity.to_key_string()

        if key in self._nodes:
            node = self._nodes[key]
            if title:
                node.title = title
            if state:
                node.state = state
            return node

        node = NavigationNode(
            identity=identity,
            state=state or NodeState.UNDISCOVERED,
            title=title,
        )
        self._nodes[key] = node
        return node

    def add_edge(
        self,
        source: PageIdentity,
        target: PageIdentity,
        action_description: str,
        source_url: str = "",
        target_url: str = "",
    ) -> NavigationEdge:
        """Add a directed edge. Creates undiscovered nodes if needed."""
        # Ensure both nodes exist
        if source.to_key_string() not in self._nodes:
            self.add_node(source)
        if target.to_key_string() not in self._nodes:
            self.add_node(target)

        # Add URL to target node's URL list
        target_node = self._nodes[target.to_key_string()]
        if target_url and target_url not in target_node.urls:
            target_node.urls.append(target_url)

        edge = NavigationEdge(
            source_identity_key=source.to_key_string(),
            target_identity_key=target.to_key_string(),
            action_description=action_description,
            source_url=source_url,
            target_url=target_url,
        )
        self._edges.append(edge)
        return edge

    def get_node(self, identity: PageIdentity) -> Optional[NavigationNode]:
        """Retrieve a node by its identity."""
        return self._nodes.get(identity.to_key_string())

    def has_node(self, identity: PageIdentity) -> bool:
        """Check if identity exists in graph."""
        return identity.to_key_string() in self._nodes

    def update_node_state(self, identity: PageIdentity, state: NodeState) -> None:
        """Transition a node to a new state."""
        key = identity.to_key_string()
        if key in self._nodes:
            self._nodes[key].state = state

    def mark_unreachable(self, identity: PageIdentity) -> None:
        """Mark a node as unreachable (navigation failure)."""
        key = identity.to_key_string()
        if key not in self._nodes:
            self.add_node(identity)
        self._nodes[key].state = NodeState.UNREACHABLE

    def serialize(self) -> Dict[str, Any]:
        """Serialize entire graph to dict for JSON output."""
        nodes_out = []
        for key, node in self._nodes.items():
            nodes_out.append({
                "identity_key": key,
                "state": node.state.value,
                "urls": node.urls,
                "title": node.title,
            })

        edges_out = []
        for edge in self._edges:
            edges_out.append({
                "source": edge.source_identity_key,
                "target": edge.target_identity_key,
                "action": edge.action_description,
            })

        return {
            "nodes": nodes_out,
            "edges": edges_out,
            "stats": self.get_stats(),
        }

    def get_stats(self) -> Dict[str, Any]:
        """Return graph statistics."""
        state_counts = {}
        for node in self._nodes.values():
            state_counts[node.state.value] = state_counts.get(node.state.value, 0) + 1

        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "by_state": state_counts,
        }
