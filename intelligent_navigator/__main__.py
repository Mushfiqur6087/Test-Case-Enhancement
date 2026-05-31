"""
CLI entry point for the Intelligent Navigator.

Configuration priority (highest to lowest):
  1. CLI flags          --api-key, --model, --url, etc.
  2. .env file          LLM_MODEL, OPENAI_API_KEY, TARGET_URL, etc.
  3. Environment vars   OPENAI_API_KEY (standard)

Usage examples:
    # Spec verification
    python -m intelligent_navigator \\
        --functional-desc input/parabank/Parabank.md \\
        --credentials input/parabank/Mock_Data.md

    # Test case verification
    python -m intelligent_navigator \\
        --test-cases input/parabank/Test_Cases.md \\
        --credentials input/parabank/Mock_Data.md

    # Enrich test cases (no browser needed)
    python -m intelligent_navigator \\
        --enrich-test-cases input/parabank/Test_Cases.md \\
        --mock-data input/parabank/Mock_Data.md \\
        --verification-report output/test_case_report.json

    # All three modes in one run
    python -m intelligent_navigator \\
        --functional-desc input/parabank/Parabank.md \\
        --test-cases input/parabank/Test_Cases.md \\
        --enrich-test-cases input/parabank/Test_Cases.md \\
        --mock-data input/parabank/Mock_Data.md \\
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
        description="Intelligent Navigator — Spec Compliance Verifier & Test Case Toolkit",
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
        help="Path to the functional description markdown (Spec Verifier mode)",
    )
    parser.add_argument(
        "--test-cases",
        default=None,
        help="Path to the test cases markdown (Test Case Verifier mode)",
    )
    parser.add_argument(
        "--enrich-test-cases",
        default=None,
        metavar="TC_FILE",
        help="Path to the test cases markdown to enrich (no browser needed)",
    )
    parser.add_argument(
        "--mock-data",
        default=None,
        help="Path to mock data markdown used to fill placeholders (for --enrich-test-cases)",
    )
    parser.add_argument(
        "--verification-report",
        default=None,
        help="Path to a previous test_case_report.json (used by --enrich-test-cases to repair invalid TCs)",
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

    # ---- Validate at least one mode is specified ----
    if not args.functional_desc and not args.test_cases and not args.enrich_test_cases:
        print(
            "Error: At least one mode is required:\n"
            "  --functional-desc    Spec verification\n"
            "  --test-cases         Test case verification\n"
            "  --enrich-test-cases  Test case enrichment (no browser needed)"
        )
        sys.exit(1)

    for flag, path in [
        ("--functional-desc", args.functional_desc),
        ("--test-cases", args.test_cases),
        ("--enrich-test-cases", args.enrich_test_cases),
    ]:
        if path and not os.path.isfile(path):
            print(f"Error: File not found for {flag}: {path}")
            sys.exit(1)

    if args.enrich_test_cases and not args.mock_data:
        print("Error: --enrich-test-cases requires --mock-data <path>")
        sys.exit(1)

    if args.mock_data and not os.path.isfile(args.mock_data):
        print(f"Error: Mock data file not found: {args.mock_data}")
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
    if args.functional_desc:
        from intelligent_navigator.spec_verifier import SpecVerifier
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

    # ---- Test Case Verifier ----
    if args.test_cases:
        from intelligent_navigator.test_case_verifier import TestCaseVerifier
        tc_verifier = TestCaseVerifier({**base_config, "test_case_file": args.test_cases})
        try:
            tc_verifier.run()
        except KeyboardInterrupt:
            print("\nTest case verification interrupted.")
        except Exception as e:
            print(f"\nTest case verification failed: {e}")
            raise
        finally:
            try:
                tc_verifier.browser_controller.close()
            except Exception:
                pass

    # ---- Test Case Enricher (no browser) ----
    if args.enrich_test_cases:
        # If a verification report wasn't provided but we just ran the TC verifier,
        # auto-detect the default output location.
        verification_report = args.verification_report
        if not verification_report:
            default_report = os.path.join(args.output, "test_case_report.json")
            if os.path.isfile(default_report):
                verification_report = default_report
                print(f"\n[Enricher] Auto-detected verification report: {default_report}")

        from intelligent_navigator.test_case_enricher.enricher import TestCaseEnricher
        enricher = TestCaseEnricher({
            **base_config,
            "test_case_file": args.enrich_test_cases,
            "mock_data_file": args.mock_data,
            "verification_report": verification_report or "",
        })
        try:
            enricher.run()
        except KeyboardInterrupt:
            print("\nTest case enrichment interrupted.")
        except Exception as e:
            print(f"\nTest case enrichment failed: {e}")
            raise


if __name__ == "__main__":
    main()
