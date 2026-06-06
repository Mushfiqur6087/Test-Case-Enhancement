"""
Module: cli.py
"""
import argparse
import os
import sys

def parse_args():
    # Pull defaults from .env / environment
    """parse_args method/function."""
    env_api_key = (
        os.getenv("OPENAI_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY")
        or os.getenv("OPENROUTER_API_KEY")
        or ""
    )
    env_model   = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
    env_url     = os.getenv("TARGET_URL", "")
    env_output  = os.getenv("OUTPUT_DIR", "output")
    env_debug   = os.getenv("DEBUG", "false").lower() == "true"

    parser = argparse.ArgumentParser(
        description="Test Case Enhancement — Spec Compliance Verifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--url",
        default=env_url or None,
        required=not env_url,
        help="Base URL of the web application (env: TARGET_URL)",
    )
    parser.add_argument(
        "--functional-desc",
        default=None,
        required=True,
        help="Path to the functional description markdown",
    )
    parser.add_argument(
        "--credentials",
        default="",
        help="Path to credentials markdown for automatic login",
    )
    parser.add_argument(
        "--test-cases",
        default="",
        help="Path to test cases markdown file for step verification",
    )
    parser.add_argument(
        "--output",
        default=env_output,
        help=f"Output directory for reports (env: OUTPUT_DIR, default: {env_output})",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="LLM API key — overrides OPENAI_API_KEY / ANTHROPIC_API_KEY / OPENROUTER_API_KEY",
    )
    parser.add_argument(
        "--model",
        default=env_model,
        help=(
            f"LiteLLM model string (env: LLM_MODEL, default: {env_model}). "
            "Format: provider/model-name"
        ),
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=env_debug,
        help="Enable debug logging to logs/ directory (env: DEBUG=true)",
    )

    args = parser.parse_args()

    # ---- Resolve API key ----
    api_key = args.api_key or env_api_key
    if not api_key:
        print(
            "Error: No API key found.\n"
            "Set OPENAI_API_KEY (or ANTHROPIC_API_KEY / OPENROUTER_API_KEY) in .env, "
            "or pass --api-key."
        )
        sys.exit(1)

    if not os.path.isfile(args.functional_desc):
        print(f"Error: File not found for --functional-desc: {args.functional_desc}")
        sys.exit(1)

    return {
        "base_url": args.url,
        "functional_desc_file": args.functional_desc,
        "credentials_file": args.credentials,
        "test_cases_file": args.test_cases,
        "output_dir": args.output,
        "api_key": api_key,
        "model_name": args.model,
        "debug": args.debug,
    }
