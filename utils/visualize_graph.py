#!/usr/bin/env python3
"""
Navigation Graph Visualizer

Converts a navigation_graph.json file into a visual graph image.

Usage:
    python -m test_case_enhancer.utils.visualize_graph <input_json> [output_image]
    
Examples:
    python -m test_case_enhancer.utils.visualize_graph output/page_catalog.json
    python -m test_case_enhancer.utils.visualize_graph output/page_catalog.json graph.png

Requirements:
    pip install networkx matplotlib
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install networkx matplotlib")
    sys.exit(1)


# Color scheme for node states
STATE_COLORS = {
    "visited": "#4CAF50",        # Green
    "fully_explored": "#2196F3", # Blue
    "undiscovered": "#9E9E9E",   # Gray
    "unreachable": "#F44336",    # Red
}

# Color scheme for roles
ROLE_COLORS = {
    "public": "#FF9800",   # Orange
    "admin": "#E91E63",    # Pink
    "user": "#9C27B0",     # Purple
    "guest": "#00BCD4",    # Cyan
}


def load_graph(json_path: str) -> dict:
    """Load navigation graph from JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_role(identity_key: str) -> str:
    """Extract role from identity key like '(admin)/dashboard'."""
    if identity_key.startswith("(") and ")" in identity_key:
        return identity_key[1:identity_key.index(")")]
    return "unknown"


def extract_path(identity_key: str) -> str:
    """Extract path from identity key like '(admin)/dashboard'."""
    if ")" in identity_key:
        return identity_key[identity_key.index(")") + 1:]
    return identity_key


def shorten_label(identity_key: str, max_len: int = 20) -> str:
    """Create a short label for display."""
    path = extract_path(identity_key)
    role = extract_role(identity_key)
    
    # Remove leading slash
    path = path.lstrip("/")
    
    # Shorten if too long
    if len(path) > max_len:
        path = path[:max_len-3] + "..."
    
    return f"{path}\n[{role}]"


def build_networkx_graph(data: dict) -> nx.DiGraph:
    """Convert JSON data to NetworkX directed graph.
    
    Supports two formats:
    1. New format with "pages" array (from page_catalog.json)
    2. Legacy format with "nodes" and "edges" arrays
    """
    G = nx.DiGraph()
    
    # Check for new format (pages array)
    if "pages" in data:
        pages = data["pages"]
        
        # Build a map from URL to page info
        url_to_page = {}
        for page in pages:
            url = page.get("url", "")
            url_to_page[url] = page
        
        # Add nodes
        for page in pages:
            url = page.get("url", "")
            role = page.get("role", "public")
            route = page.get("normalized_route_pattern", url)
            
            # Create identity key like "(role)/path"
            identity_key = f"({role}){route}"
            
            G.add_node(
                identity_key,
                title=route,
                state="visited",  # All pages in output are visited
                role=role,
                urls=[url],
            )
        
        # Add edges from outgoing_links
        for page in pages:
            source_url = page.get("url", "")
            source_role = page.get("role", "public")
            source_route = page.get("normalized_route_pattern", source_url)
            source_key = f"({source_role}){source_route}"
            
            for target_url in page.get("outgoing_links", []):
                # Find target page info
                if target_url in url_to_page:
                    target_page = url_to_page[target_url]
                    target_role = target_page.get("role", "public")
                    target_route = target_page.get("normalized_route_pattern", target_url)
                    target_key = f"({target_role}){target_route}"
                else:
                    # External or undiscovered link - extract path from URL
                    from urllib.parse import urlparse
                    parsed = urlparse(target_url)
                    target_route = parsed.path or "/"
                    target_key = f"(unknown){target_route}"
                    
                    # Add undiscovered node
                    if target_key not in G.nodes():
                        G.add_node(
                            target_key,
                            title=target_route,
                            state="undiscovered",
                            role="unknown",
                            urls=[target_url],
                        )
                
                # Add edge (avoid self-loops)
                if source_key != target_key:
                    G.add_edge(source_key, target_key, action="link")
        
        return G
    
    # Legacy format with nodes/edges arrays
    for node in data.get("nodes", []):
        identity_key = node["identity_key"]
        G.add_node(
            identity_key,
            title=node.get("title", ""),
            state=node.get("state", "undiscovered"),
            role=extract_role(identity_key),
            urls=node.get("urls", []),
        )
    
    for edge in data.get("edges", []):
        G.add_edge(
            edge["source"],
            edge["target"],
            action=edge.get("action", ""),
        )
    
    return G


def visualize_graph(
    G: nx.DiGraph,
    output_path: str = None,
    figsize: tuple = (16, 12),
    show: bool = True,
):
    """Render the graph as an image."""
    if len(G.nodes()) == 0:
        print("Graph is empty, nothing to visualize.")
        return
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Choose layout
    if len(G.nodes()) <= 10:
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    else:
        pos = nx.kamada_kawai_layout(G)
    
    # Prepare node colors based on state
    node_colors = []
    for node in G.nodes():
        state = G.nodes[node].get("state", "undiscovered")
        node_colors.append(STATE_COLORS.get(state, "#9E9E9E"))
    
    # Prepare node border colors based on role
    node_edge_colors = []
    for node in G.nodes():
        role = G.nodes[node].get("role", "public")
        node_edge_colors.append(ROLE_COLORS.get(role, "#000000"))
    
    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors,
        edgecolors=node_edge_colors,
        linewidths=3,
        node_size=2000,
        alpha=0.9,
    )
    
    # Draw edges with arrows
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color="#666666",
        arrows=True,
        arrowsize=20,
        arrowstyle="-|>",
        connectionstyle="arc3,rad=0.1",
        alpha=0.7,
        width=1.5,
    )
    
    # Draw labels
    labels = {node: shorten_label(node) for node in G.nodes()}
    nx.draw_networkx_labels(
        G, pos, ax=ax,
        labels=labels,
        font_size=8,
        font_weight="bold",
    )
    
    # Add legend for states
    state_patches = [
        mpatches.Patch(color=color, label=state.replace("_", " ").title())
        for state, color in STATE_COLORS.items()
    ]
    
    # Add legend for roles
    role_patches = [
        mpatches.Patch(
            facecolor="white", 
            edgecolor=color, 
            linewidth=2,
            label=f"Role: {role}"
        )
        for role, color in ROLE_COLORS.items()
    ]
    
    # Combine legends
    ax.legend(
        handles=state_patches + role_patches,
        loc="upper left",
        fontsize=8,
        framealpha=0.9,
    )
    
    # Title with stats
    stats = f"Nodes: {len(G.nodes())} | Edges: {len(G.edges())}"
    ax.set_title(f"Navigation Graph\n{stats}", fontsize=14, fontweight="bold")
    
    ax.axis("off")
    plt.tight_layout()
    
    # Save if output path provided
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
        print(f"Graph saved to: {output_path}")
    
    # Show interactively
    if show:
        plt.show()
    
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Visualize navigation graph JSON as an image"
    )
    parser.add_argument(
        "input",
        help="Path to navigation_graph.json or page_catalog.json",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Output image path (e.g., graph.png). If not provided, shows interactively.",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Don't show interactive window (useful for headless servers)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=16,
        help="Figure width in inches (default: 16)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=12,
        help="Figure height in inches (default: 12)",
    )
    
    args = parser.parse_args()
    
    # Load graph
    if not Path(args.input).exists():
        print(f"Error: File not found: {args.input}")
        sys.exit(1)
    
    print(f"Loading graph from: {args.input}")
    data = load_graph(args.input)
    
    # Build NetworkX graph first
    G = build_networkx_graph(data)
    
    # Print stats based on actual graph
    print(f"  Nodes: {len(G.nodes())}")
    print(f"  Edges: {len(G.edges())}")
    
    # Determine output path
    output_path = args.output
    if output_path is None and args.no_show:
        # Auto-generate output path
        input_path = Path(args.input)
        output_path = str(input_path.with_suffix(".png"))
    
    # Visualize
    visualize_graph(
        G,
        output_path=output_path,
        figsize=(args.width, args.height),
        show=not args.no_show,
    )


if __name__ == "__main__":
    main()
