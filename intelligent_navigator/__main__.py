"""
CLI entry point for the Intelligent Navigator — Spec Compliance Verifier.

Configuration priority (highest to lowest):
  1. CLI flags          --api-key, --model, --url, etc.
  2. .env file          LLM_MODEL, OPENAI_API_KEY, TARGET_URL, etc.
  3. Environment vars   OPENAI_API_KEY (standard)

Usage:
    python -m intelligent_navigator \\
        --url http://localhost:8080 \\
        --functional-desc input/parabank/Parabank.md \\
        --credentials input/parabank/Mock_Data.md \\
        --output output/ \\
        --model openai/gpt-5-mini \\
        --debug
"""

import argparse
import os
import sys

# Suppress noisy LiteLLM provider warnings (botocore, sagemaker, etc.)
# before litellm is imported anywhere in the package.
os.environ.setdefault("LITELLM_LOG", "ERROR")

from dotenv import load_dotenv  # type: ignore

# Load .env from the project root (silently ignored if missing)
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
        description="Intelligent Navigator — Spec Compliance Verifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--url",
        default=env_url or None,
        required=not env_url,
        help="Base URL of the web application to verify (env: TARGET_URL)",
    )
    parser.add_argument(
        "--functional-desc",
        required=True,
        help="Path to the functional description markdown file (e.g. Parabank.md)",
    )
    parser.add_argument(
        "--credentials",
        default="",
        help="Path to credentials markdown file (username / password / role)",
    )
    parser.add_argument(
        "--output",
        default=env_output,
        help=f"Output directory (env: OUTPUT_DIR, default: {env_output})",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="LLM API key — overrides OPENAI_API_KEY / ANTHROPIC_API_KEY / OPENROUTER_API_KEY env vars",
    )
    parser.add_argument(
        "--model",
        default=env_model,
        help=(
            f"LiteLLM model string (env: LLM_MODEL, default: {env_model}). "
            "Format: provider/model-name — e.g. openai/gpt-5-mini, "
            "anthropic/claude-3-5-sonnet-20241022, openrouter/anthropic/claude-3.5-sonnet"
        ),
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=env_debug,
        help="Enable debug logging to file (env: DEBUG=true)",
    )

    args = parser.parse_args()

    # ---- Resolve API key (CLI flag beats .env) ----
    api_key = args.api_key or env_api_key
    if not api_key:
        print(
            "Error: No API key found.\n"
            "Set OPENAI_API_KEY (or ANTHROPIC_API_KEY / OPENROUTER_API_KEY) in .env, "
            "or pass --api-key."
        )
        sys.exit(1)

    # ---- Validate inputs ----
    if not os.path.isfile(args.functional_desc):
        print(f"Error: Functional description file not found: {args.functional_desc}")
        sys.exit(1)

    # ---- Run ----
    from intelligent_navigator.spec_verifier import SpecVerifier

    config = {
        "base_url": args.url,
        "functional_desc_file": args.functional_desc,
        "credentials_file": args.credentials,
        "output_dir": args.output,
        "api_key": api_key,
        "model_name": args.model,
        "debug": args.debug,
    }

    verifier = SpecVerifier(config)
    try:
        report = verifier.run()
        json_path = os.path.join(args.output, "verification_report.json")
        md_path   = os.path.join(args.output, "verification_report.md")
        print(f"\n{'=' * 50}")
        print(f"Spec Verification Complete")
        print(f"{'=' * 50}")
        print(f"Model         : {args.model}")
        print(f"Overall score : {report.overall_score:.0f} / 100")
        print(f"Sections      : {report.sections_checked} total")
        print(f"  ✅ Pass    : {report.passed}")
        print(f"  ⚠️  Partial : {report.partial}")
        print(f"  ❌ Fail    : {report.failed}")
        print(f"  ⏭️  Skipped : {report.skipped}")
        print(f"LLM calls used: {report.llm_calls_total}")
        print(f"\nOutputs:")
        print(f"  JSON   → {json_path}")
        print(f"  Report → {md_path}")
    except KeyboardInterrupt:
        print("\nVerification interrupted by user.")
    except Exception as e:
        print(f"\nVerification failed: {e}")
        raise
    finally:
        try:
            verifier.browser_controller.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
