"""
CLI entry point for the Test Case Enhancement.

Configuration priority (highest to lowest):
  1. CLI flags          --api-key, --model, --url, etc.
  2. .env file          LLM_MODEL, OPENAI_API_KEY, TARGET_URL, etc.
  3. Environment vars   OPENAI_API_KEY (standard)

Usage examples:
    # Spec verification
    python -m test_case_enhancement \
        --functional-desc input/parabank/Parabank.md \
        --credentials input/parabank/Mock_Data.md
"""

import argparse
import os
import sys

# Suppress noisy LiteLLM provider warnings before litellm is imported anywhere.
os.environ.setdefault("LITELLM_LOG", "ERROR")

from dotenv import load_dotenv  # type: ignore

load_dotenv(override=False)


def main():
    # Pull defaults from .env / environment
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
        help="Path to the functional description markdown (Spec Verifier mode)",
    )
    parser.add_argument(
        "--credentials",
        default="",
        help="Path to credentials markdown for automatic login",
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
            "Format: provider/model-name — e.g. openai/gpt-5-mini, "
            "anthropic/claude-3-5-sonnet-20241022"
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

    base_config = {
        "base_url": args.url,
        "credentials_file": args.credentials,
        "output_dir": args.output,
        "api_key": api_key,
        "model_name": args.model,
        "debug": args.debug,
    }

    # ---- Spec Verifier ----
    from test_case_enhancement.spec_verifier import SpecVerifier
    verifier = SpecVerifier({**base_config, "functional_desc_file": args.functional_desc})
    try:
        verifier.run()
    except KeyboardInterrupt:
        print("\nSpec verification interrupted.")
    except Exception as e:
        print(f"\nSpec verification failed: {e}")
        raise
    finally:
        try:
            verifier.browser_controller.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
