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

import os
import sys

# Suppress noisy LiteLLM provider warnings before litellm is imported anywhere.
os.environ.setdefault("LITELLM_LOG", "ERROR")

from dotenv import load_dotenv  # type: ignore

from test_case_enhancement.cli import parse_args
from test_case_enhancement.orchestrator.coordinator import Coordinator

def main():
    """main method/function."""
    load_dotenv(override=False)
    
    config = parse_args()

    coordinator = Coordinator(config)
    try:
        coordinator.run()
    except KeyboardInterrupt:
        print("\nVerification interrupted.")
    except Exception as e:
        print(f"\nVerification failed: {e}")
        raise
    finally:
        try:
            coordinator.browser_controller.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
