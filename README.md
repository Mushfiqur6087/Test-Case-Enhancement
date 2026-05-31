# Intelligent Navigator

An LLM-powered dual-mode verifier that reads a **functional description** and/or **test cases**, navigates to each page in a live web application using a real browser, and verifies whether the implementation matches the spec.

---

## Modes

### 1. Spec Verifier (`--functional-desc`)
Compares a written specification against the live page DOM. Answers: *"Does this page implement what the spec says?"*

### 2. Test Case Verifier (`--test-cases`)
Checks whether each test case's steps are executable against the live page. Answers: *"Do the UI elements this test step references actually exist in the DOM?"*

Both modes can run together in a single command.

---

## How It Works

```
┌─────────────────────────────────┐
│  Input files (Markdown)         │
│  ● Functional spec              │
│  ● Test cases                   │
│  ● Credentials (optional)       │
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
             ▼
    ┌─────────────────┐
    │  LLM Checker     │  Compares spec/TC steps against what's on the page
    └────────┬─────────┘
             │
             ▼
    JSON + Markdown report
```

---

## Architecture

```
intelligent_navigator/
├── __init__.py               # Exports: SpecVerifier, TestCaseVerifier
├── __main__.py               # CLI entry point
├── agents/
│   ├── navigator.py          # Navigates the browser to target pages
│   └── prompts.py            # Navigator prompt templates
├── browser/
│   ├── controller.py         # Playwright command execution (click, type, scroll)
│   ├── dom_helper.py         # Full-page DOM capture with scroll
│   ├── dom_builder.py        # JavaScript DOM extraction
│   ├── dom_parser.py         # DOM tree parsing and element mapping
│   ├── screenshot.py         # Base64 screenshot capture for vision models
│   ├── selector_filter.py    # DOM noise removal
│   └── session.py            # Browser session management
├── core/
│   ├── llm.py                # LiteLLM client — text + vision (ask_with_screenshot)
│   ├── models.py             # All data models
│   ├── utils.py              # Shared utilities
│   └── logging.py            # Debug log file management
├── exploration/
│   └── credentials.py        # Parses credentials markdown for login
├── spec_verifier/
│   ├── orchestrator.py       # Spec verification loop
│   ├── description_parser.py # Splits functional spec into SpecSections
│   ├── checker.py            # LLM: spec text vs live DOM
│   ├── prompts.py            # Spec checker prompt templates
│   └── report.py             # Builds verification_report.{json,md}
└── test_case_verifier/
    ├── orchestrator.py       # TC verification loop (one navigation per module)
    ├── test_case_parser.py   # Parses test case markdown into TestCase objects
    ├── step_checker.py       # LLM: TC steps vs live DOM (batch per module)
    ├── prompts.py            # Step checker prompt templates
    └── report.py             # Builds test_case_report.{json,md}
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

### Both modes in one run
```bash
python -m intelligent_navigator \
    --functional-desc input/parabank/Parabank.md \
    --test-cases input/parabank/Test_Cases.md \
    --credentials input/parabank/Mock_Data.md
```

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
| `--functional-desc` | — | Path to functional spec markdown |
| `--test-cases` | — | Path to test cases markdown |
| `--credentials` | `""` | Path to credentials markdown |
| `--url` | `TARGET_URL` | Base URL of the application |
| `--output` | `OUTPUT_DIR` | Output directory for reports |
| `--model` | `LLM_MODEL` | LiteLLM model string |
| `--api-key` | `OPENAI_API_KEY` | API key (overrides .env) |
| `--debug` | `DEBUG` | Write full debug log to `logs/` |

At least one of `--functional-desc` or `--test-cases` is required.

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
| **Steps** | 1. Enter email<br>2. Enter password<br>3. Click **Sign In** |
| **Expected Result** | User redirected to Dashboard |
```

### Credentials File
A markdown table of accounts. The LLM extracts username, password, and role automatically:

```markdown
| Username | Password | Role |
|----------|----------|------|
| admin@example.com | Admin123! | Admin |
```

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

## What Gets Verified

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

---

## Vision Support

If your model is vision-capable (gpt-4o, gpt-5-mini, claude-3, gemini), the tool automatically:
1. Takes a full-page screenshot after DOM capture
2. Attaches it to every LLM checker call alongside the DOM text
3. Falls back to text-only if the vision call fails for any reason

No configuration needed — vision is enabled automatically based on the model name.

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

---

## Debug Logging

Run with `--debug` (or `DEBUG=true` in `.env`) to write a full trace to `logs/`:

```
[DEBUG] Log file: intelligent_navigator/logs/tc_verification_debug_20260531_012345.log
```

The log contains for each page:
- Captured page body text
- DOM selector map
- Full LLM prompts sent
- Full LLM responses (JSON verdicts)
- Vision call indicators (`[VISION]` prefix)

---

## Programmatic API

```python
from intelligent_navigator import SpecVerifier, TestCaseVerifier

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
```

---

## Example — Parabank

`input/parabank/` contains a complete example for an online banking demo app:
- **`Parabank.md`** — functional spec (13 sections)
- **`Test_Cases.md`** — 50 curated test cases across all 13 modules
- **`Mock_Data.md`** — seeded user credentials

```bash
# Start the app
cd examples/parabank
docker compose up --build
# Frontend → http://localhost:8080

# Run both verifiers
cd ../..
python -m intelligent_navigator \
    --functional-desc input/parabank/Parabank.md \
    --test-cases input/parabank/Test_Cases.md \
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
```
