# Intelligent Navigator

An LLM-powered **three-mode toolkit** that reads a **functional description** and/or **test cases**, navigates to each page in a live web application using a real browser, verifies whether the implementation matches the spec, and then **enriches** the verified test cases with real data and automatic repairs — ready for execution.

---

## Modes

### 1. Spec Verifier (`--functional-desc`)
Compares a written specification against the live page DOM. Answers: *"Does this page implement what the spec says?"*

### 2. Test Case Verifier (`--test-cases`)
Checks whether each test case's steps are executable against the live page. Answers: *"Do the UI elements this test step references actually exist in the DOM?"*

### 3. Test Case Enricher (`--enrich-test-cases`)
A **browser-free** post-verification pass that takes the raw (possibly verified) test cases and upgrades them into execution-ready artifacts. Specifically, it:

- **Fills placeholders** — replaces every `<placeholder>` token in steps with a concrete value drawn from real mock/seed data (e.g. `<valid password>` → `Admin123!@#`)
- **Adds metadata** — direct page URLs, `requires_auth` flag, and a `test_data` dictionary of all concrete values used
- **Repairs broken steps** — if the verifier flagged a step as `invalid_steps`, the enricher rewrites those steps to match what *is* actually in the live DOM
- **Drops unrunnable tests** — marks and explains any TC whose preconditions cannot be satisfied by the available seed data

All three modes can run together in a single command.

---

## How It Works

```
┌─────────────────────────────────┐
│  Input files (Markdown)         │
│  ● Functional spec              │
│  ● Test cases                   │
│  ● Credentials / Mock data      │
└────────────┬────────────────────┘
             │
             ▼
    ┌─────────────────┐
    │  Navigator       │  Playwright browser — navigates to the target page
    └────────┬─────────┘
             │  page reached
             ▼
    ┌─────────────────┐
    │  DOM + Screenshot│  Full page content + optional screenshot (vision models)
    └────────┬─────────┘
             │
             ├─────────────────────────────────────────┐
             ▼                                         ▼
    ┌─────────────────┐                     ┌─────────────────────┐
    │  Spec Checker    │                     │  Step Checker        │
    │  spec vs DOM     │                     │  TC steps vs DOM     │
    └────────┬─────────┘                     └──────────┬──────────┘
             │                                          │
             └──────────────┬───────────────────────────┘
                            ▼
               verification_report.{json,md}
               test_case_report.{json,md}
                            │
                            ▼  (optional, no browser)
                  ┌─────────────────────┐
                  │  Test Case Enricher  │
                  │  fills placeholders  │
                  │  repairs steps       │
                  │  adds metadata       │
                  └──────────┬──────────┘
                             ▼
               enriched_test_cases.{json,md}
```

---

## Architecture

```
intelligent_navigator/
├── __init__.py                   # Exports: SpecVerifier, TestCaseVerifier
├── __main__.py                   # CLI entry point
├── agents/
│   ├── navigator.py              # Navigates the browser to target pages
│   └── prompts.py                # Navigator prompt templates
├── browser/
│   ├── controller.py             # Playwright command execution (click, type, scroll)
│   ├── dom_helper.py             # Full-page DOM capture with scroll
│   ├── dom_builder.py            # JavaScript DOM extraction
│   ├── dom_parser.py             # DOM tree parsing and element mapping
│   ├── screenshot.py             # Base64 screenshot capture for vision models
│   ├── selector_filter.py        # DOM noise removal
│   └── session.py                # Browser session management
├── core/
│   ├── llm.py                    # LiteLLM client — text + vision (ask_with_screenshot)
│   ├── models.py                 # All data models
│   ├── utils.py                  # Shared utilities
│   └── logging.py                # Debug log file management
├── exploration/
│   └── credentials.py            # Parses credentials markdown for login
├── spec_verifier/
│   ├── orchestrator.py           # Spec verification loop
│   ├── description_parser.py     # Splits functional spec into SpecSections
│   ├── checker.py                # LLM: spec text vs live DOM
│   ├── prompts.py                # Spec checker prompt templates
│   └── report.py                 # Builds verification_report.{json,md}
├── test_case_verifier/
│   ├── orchestrator.py           # TC verification loop (one navigation per module)
│   ├── test_case_parser.py       # Parses test case markdown into TestCase objects
│   ├── step_checker.py           # LLM: TC steps vs live DOM (batch per module)
│   ├── prompts.py                # Step checker prompt templates
│   └── report.py                 # Builds test_case_report.{json,md}
└── test_case_enricher/
    ├── enricher.py               # Enrichment pipeline (no browser)
    └── prompts.py                # Enricher prompt templates
```

---

## Installation

```bash
# 1. Enter the project directory
cd "Intelligent Navigator"

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -e .

# 4. Install Playwright's Chromium browser
playwright install chromium
```

---

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```ini
# .env

# LiteLLM model string — provider/model-name
# Vision-capable models (gpt-4o, gpt-5-mini, claude-3, gemini) also send screenshots
LLM_MODEL=openai/gpt-4o-mini

# API key for your provider
OPENAI_API_KEY=sk-proj-...

# Target application base URL
TARGET_URL=http://localhost:8080

# Output directory for reports
OUTPUT_DIR=output

# Enable debug logging (writes full LLM prompts/responses to logs/)
DEBUG=false

# Suppress noisy LiteLLM provider warnings
LITELLM_LOG=ERROR
```

**Supported model formats (LiteLLM):**

| Provider | Example | Vision? |
|---|---|---|
| OpenAI | `openai/gpt-4o-mini`, `openai/gpt-5-mini` | ✅ |
| Anthropic | `anthropic/claude-3-5-sonnet-20241022` | ✅ |
| OpenRouter | `openrouter/anthropic/claude-3.5-sonnet` | ✅ |
| OpenAI (text only) | `openai/gpt-3.5-turbo`, `openai/o1-mini` | ❌ |

> `litellm.drop_params = True` is set globally — temperature and other unsupported params are silently dropped per model.

---

## Usage

### Spec Verification only
```bash
python -m intelligent_navigator \
    --functional-desc input/parabank/Parabank.md \
    --credentials input/parabank/Mock_Data.md
```

### Test Case Verification only
```bash
python -m intelligent_navigator \
    --test-cases input/parabank/Test_Cases.md \
    --credentials input/parabank/Mock_Data.md
```

### Test Case Enrichment only (no browser needed)
```bash
python -m intelligent_navigator \
    --enrich-test-cases input/parabank/Test_Cases.md \
    --mock-data input/parabank/Mock_Data.md \
    --verification-report output/test_case_report.json
```

> **`--verification-report` is optional.** If omitted and a `test_case_report.json` already exists in the output directory, it is picked up automatically.

### All three modes in one run
```bash
python -m intelligent_navigator \
    --functional-desc input/parabank/Parabank.md \
    --test-cases input/parabank/Test_Cases.md \
    --enrich-test-cases input/parabank/Test_Cases.md \
    --mock-data input/parabank/Mock_Data.md \
    --credentials input/parabank/Mock_Data.md
```

When all three flags are combined, the pipeline runs in order:
1. Spec Verifier (browser)
2. Test Case Verifier (browser)
3. Test Case Enricher (no browser — auto-reads the fresh verification report)

### Override settings per run
```bash
python -m intelligent_navigator \
    --test-cases input/parabank/Test_Cases.md \
    --credentials input/parabank/Mock_Data.md \
    --model openai/gpt-4o \
    --url http://localhost:3000 \
    --debug
```

---

## CLI Reference

| Flag | Default (from .env) | Description |
|---|---|---|
| `--functional-desc` | — | Path to functional spec markdown (Spec Verifier) |
| `--test-cases` | — | Path to test cases markdown (Test Case Verifier) |
| `--enrich-test-cases` | — | Path to test cases markdown to enrich (no browser) |
| `--mock-data` | — | Path to mock data markdown (required by `--enrich-test-cases`) |
| `--verification-report` | auto-detect | Path to a previous `test_case_report.json` for repair context |
| `--credentials` | `""` | Path to credentials markdown for automatic login |
| `--url` | `TARGET_URL` | Base URL of the application |
| `--output` | `OUTPUT_DIR` | Output directory for reports |
| `--model` | `LLM_MODEL` | LiteLLM model string |
| `--api-key` | `OPENAI_API_KEY` | API key (overrides .env) |
| `--debug` | `DEBUG` | Write full debug log to `logs/` |

At least one of `--functional-desc`, `--test-cases`, or `--enrich-test-cases` is required.

---

## Input Files

### Functional Description
A markdown file with one `##` heading per page/feature:

```markdown
## Login
The login page has an email field, a password field, and a "Sign In" button.

## Dashboard
Shows a welcome message and a table of all customer accounts.
```

### Test Cases
A markdown file with test cases grouped under module headings. Each TC is a table with Preconditions, Steps, and Expected Result:

```markdown
## 1. Login

### TC-001 — Successful sign-in ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is unauthenticated on the Login page |
| **Steps** | 1. Enter <registered email><br>2. Enter <valid password><br>3. Click **Sign In** |
| **Expected Result** | User redirected to Dashboard |
```

> Note: `<placeholder>` tokens in steps are filled in automatically by the Test Case Enricher.

### Credentials / Mock Data File
A markdown table of accounts. The LLM extracts username, password, role, and seed data automatically:

```markdown
| Username | Password | Role |
|----------|----------|------|
| admin@example.com | Admin123! | Admin |
```

The same file can be passed to both `--credentials` (for browser login) and `--mock-data` (for enrichment).

---

## URL Inference

The tool infers target URLs from section/module names:

| Heading | Inferred URL |
|---|---|
| `Login` | `/login` |
| `Register` | `/register` |
| `Accounts Overview` | `/dashboard` |
| `Open New Account` | `/open-account` |
| `Transfer Funds` | `/transfer` |
| `Payments` / `Bill Pay` | `/bill-pay` |
| `Request Loan` | `/loan` |
| `Security Settings` | `/security` |
| anything else | `/slugified-name` |

The Navigator always confirms by navigating in the browser — the inferred URL is just a first guess.

---

## What Gets Verified / Enriched

### Spec Verifier
Checks only what is **visible in the static DOM snapshot**:

| Category | Checked? |
|---|---|
| Fields, buttons, labels present | ✅ |
| Page structure / correct section | ✅ |
| Form validation errors | ❌ (post-submission) |
| Success/error messages | ❌ (post-action) |
| Redirect behavior | ❌ (post-submission) |

**Verdicts:** Pass (≥75) · Partial (40–74) · Fail (<40) · Skipped (navigation failed)

### Test Case Verifier
For each step, checks: *"Does the UI element this step references exist in the DOM?"*

| Category | How handled |
|---|---|
| Input fields, buttons, dropdowns | ✅ Verified against DOM |
| Conditional UI (appears after click) | ✅ Trigger element verified; revealed field skipped |
| Autocomplete dropdowns | ✅ Input field verified; dropdown list skipped (dynamic) |
| Browser-Back multi-step flows | ✅ First-page elements verified; rest marked unverifiable |
| Expected results / error messages | ❌ Ignored (post-submission) |
| Backend state (balances, approvals) | ❌ Ignored (not in DOM) |

**Verdicts:** Valid · Invalid Steps (step references missing element) · Invalid (wrong page) · Skipped

### Test Case Enricher
Runs **without a browser** against the test cases file and optional verification report:

| Task | What it does |
|---|---|
| Fill placeholders | Replaces every `<placeholder>` in steps with a concrete value from mock data |
| Add metadata | Adds `direct_link`, `requires_auth`, and `test_data` fields to each TC |
| Repair broken steps | Rewrites steps flagged `invalid_steps` so they match what IS in the DOM |
| Drop unrunnable TCs | Marks TCs whose preconditions cannot be satisfied by seed data |

**Output per TC:** `kept` or `dropped` (with reason). Repaired steps are explained in a `notes` field.

---

## Vision Support

If your model is vision-capable (gpt-4o, gpt-5-mini, claude-3, gemini), the tool automatically:
1. Takes a full-page screenshot after DOM capture
2. Attaches it to every LLM checker call alongside the DOM text
3. Falls back to text-only if the vision call fails for any reason

No configuration needed — vision is enabled automatically based on the model name.

> The Test Case Enricher does **not** use vision (it never opens a browser).

---

## Output Files

### Spec Verifier
| File | Contents |
|---|---|
| `output/verification_report.json` | Machine-readable results |
| `output/verification_report.md` | Human-readable report |

### Test Case Verifier
| File | Contents |
|---|---|
| `output/test_case_report.json` | Machine-readable results per TC |
| `output/test_case_report.md` | Human-readable report grouped by module |

### Test Case Enricher
| File | Contents |
|---|---|
| `output/enriched_test_cases.json` | Enriched TC objects — execution-ready |
| `output/enriched_test_cases.md` | Human-readable enriched report |

---

## Debug Logging

Run with `--debug` (or `DEBUG=true` in `.env`) to write a full trace to `logs/`:

```
[DEBUG] Log file: intelligent_navigator/logs/tc_verification_debug_20260531_012345.log
[DEBUG] Log file: intelligent_navigator/logs/tc_enrichment_debug_20260531_012346.log
```

The log contains for each page / module:
- Captured page body text
- DOM selector map
- Full LLM prompts sent
- Full LLM responses (JSON verdicts)
- Vision call indicators (`[VISION]` prefix)

---

## Programmatic API

```python
from intelligent_navigator import SpecVerifier, TestCaseVerifier
from intelligent_navigator.test_case_enricher.enricher import TestCaseEnricher

config = {
    "base_url": "http://localhost:8080",
    "api_key": "sk-...",
    "model_name": "openai/gpt-4o-mini",
    "output_dir": "output/",
    "debug": False,
}

# Spec verification
spec_report = SpecVerifier({**config, "functional_desc_file": "Parabank.md"}).run()
print(f"Score: {spec_report.overall_score:.0f}/100")

# Test case verification
tc_report = TestCaseVerifier({**config, "test_case_file": "Test_Cases.md"}).run()
print(f"Valid: {tc_report.valid_count}/{tc_report.total}")

# Test case enrichment (no browser)
enriched = TestCaseEnricher({
    **config,
    "test_case_file": "Test_Cases.md",
    "mock_data_file": "Mock_Data.md",
    "verification_report": "output/test_case_report.json",  # optional
}).run()
print(f"Kept: {enriched['summary']['kept']} / Dropped: {enriched['summary']['dropped']}")
```

---

## Example — Parabank

`input/parabank/` contains a complete example for an online banking demo app:
- **`Parabank.md`** — functional spec (13 sections)
- **`Test_Cases.md`** — 50 curated test cases across all 13 modules
- **`Mock_Data.md`** — seeded user credentials and account data

```bash
# Start the app
cd examples/parabank
docker compose up --build
# Frontend → http://localhost:8080

# Run all three modes
cd ../..
python -m intelligent_navigator \
    --functional-desc input/parabank/Parabank.md \
    --test-cases input/parabank/Test_Cases.md \
    --enrich-test-cases input/parabank/Test_Cases.md \
    --mock-data input/parabank/Mock_Data.md \
    --credentials input/parabank/Mock_Data.md
```

Typical result:
```
# Spec Verifier
Overall score : 87 / 100
  ✅ Pass    : 10 / 13
  ⚠️  Partial : 3 / 13
  ❌ Fail    : 0 / 13

# Test Case Verifier
Total    : 50
  ✅ Valid          : 46
  ⚠️  Invalid Steps : 4
  ❌ Invalid        : 0
Accuracy : 92%
LLM calls: 13

# Test Case Enricher
Total input  : 50
  ✅ Kept    : 48
  🗑  Dropped : 2
LLM calls    : 13
```
