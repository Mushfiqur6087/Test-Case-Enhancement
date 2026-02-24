"""
CLI entry point for the Intelligent Navigator.

Usage:
    python -m intelligent_navigator \
        --url http://localhost:8080 \
        --credentials path/to/credentials.md \
        --functional-desc path/to/functional_desc.txt \
        --output output/ \
        --api-key "sk-..." \
        --model gpt-4o \
        --max-steps 100 \
        --max-pages 50 \
        --max-llm-calls 150 \
        --debug
"""

import argparse
import os
import sys

from intelligent_navigator.agents.orchestrator import Orchestrator


def main():
    parser = argparse.ArgumentParser(
        description="Intelligent Navigator -- LLM-guided web exploration agent"
    )
    parser.add_argument(
        "--url", required=True, help="Base URL of the web application"
    )
    parser.add_argument(
        "--credentials", default="", help="Path to credentials markdown file"
    )
    parser.add_argument(
        "--functional-desc",
        default="",
        help="Path to functional description text file",
    )
    parser.add_argument(
        "--navigation",
        default="",
        help="Path to Navigation.md file (expected pages checklist)",
    )
    parser.add_argument(
        "--output", default="output", help="Output directory (default: output)"
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="OpenAI API key (or set OPENAI_API_KEY env var)",
    )
    parser.add_argument(
        "--model", default="gpt-4o-mini", help="Model name (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=100,
        help="Max exploration steps (default: 100)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=50,
        help="Max pages to visit (default: 50)",
    )
    parser.add_argument(
        "--max-llm-calls",
        type=int,
        default=300,
        help="Max LLM calls total across all agents (default: 300)",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging"
    )

    args = parser.parse_args()

    # Resolve API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: No API key provided. Set --api-key or OPENAI_API_KEY env var.")
        sys.exit(1)

    # Read functional description (optional)
    functional_desc = ""
    if args.functional_desc:
        try:
            with open(args.functional_desc, "r", encoding="utf-8") as f:
                functional_desc = f.read()
        except FileNotFoundError:
            print(f"Warning: Functional description file not found: {args.functional_desc}")

    config = {
        "base_url": args.url,
        "credentials_file": args.credentials,
        "functional_desc": functional_desc,
        "navigation_file": args.navigation,
        "output_dir": args.output,
        "api_key": api_key,
        "model_name": args.model,
        "max_steps": args.max_steps,
        "max_pages": args.max_pages,
        "max_llm_calls": args.max_llm_calls,
        "debug": args.debug,
    }

    orchestrator = Orchestrator(config)
    try:
        result = orchestrator.run()
        print(f"\nNavigation graph written to: {os.path.join(args.output, 'navigation_graph.json')}")
        graph_stats = result.navigation_graph.get("stats", {})
        print(f"Nodes discovered: {graph_stats.get('total_nodes', 0)}")
        print(f"Edges discovered: {graph_stats.get('total_edges', 0)}")
        print(f"Roles explored: {', '.join(result.roles_explored)}")
        print(f"LLM calls used: {result.exploration_stats.get('llm_calls_total', 0)}")
        print(f"Steps taken: {result.exploration_stats.get('steps_taken', 0)}")
    except KeyboardInterrupt:
        print("\nExploration interrupted by user.")
    except Exception as e:
        print(f"\nExploration failed: {e}")
        raise
    finally:
        try:
            orchestrator.browser_controller.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
