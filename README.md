# Intelligent Navigator — Spec Compliance Verifier

An LLM-powered tool that reads your **functional description**, navigates to each described page in a live web application, and verifies whether the HTML actually implements what the spec says.

## What It Does

Given a functional description written in plain markdown, the tool:

1. **Parses** the description into sections (`## Login`, `## Register`, etc.)
2. **Logs in** automatically if credentials are provided
3. **Navigates** to each section's page in a real browser (Playwright)
4. **Captures** the live page DOM + visible body text
5. **Checks** — an LLM compares the spec text against what's on the page
6. **Reports** — writes a `verification_report.md` and `verification_report.json`

## How It Works

```
Functional Description (Parabank.md)
         │
         ▼  split on ## headings
  [ Login ] [ Register ] [ Accounts Overview ] [ ... ]
         │
         ▼  for each section:
  ┌──────────────────────────────┐
  │  Navigator                   │  clicks through the live app to reach the page
  └──────────────┬───────────────┘
                 │  page reached
                 ▼
  ┌──────────────────────────────┐
  │  DOM + Body Text Capture     │  full page content (not just interactive elements)
  └──────────────┬───────────────┘
                 │
                 ▼
  ┌──────────────────────────────┐
  │  Spec Checker (LLM)          │  "Does this page match the spec?"
  └──────────────┬───────────────┘
                 │  pass / partial / fail + details
                 ▼
  verification_report.json + verification_report.md
```

## Architecture

```
intelligent_navigator/
├── __init__.py               # Exports: SpecVerifier, VerificationReport
├── __main__.py               # CLI entry point (reads .env automatically)
├── agents/
│   ├── navigator.py          # Clicks through the app to reach target pages
│   └── prompts.py            # Navigator + Credentials prompt templates
├── browser/                  # Playwright browser automation
│   ├── controller.py         # Command execution (click, type, scroll)
│   ├── dom_helper.py         # Full-page DOM capture with scrolling
│   ├── dom_builder.py        # JavaScript DOM extraction
│   ├── dom_parser.py         # DOM tree parsing and element mapping
│   ├── selector_filter.py    # Rule-based DOM noise removal
│   └── session.py            # Browser session management
├── core/
│   ├── llm.py                # LiteLLM client (any provider, auto drops unsupported params)
│   ├── models.py             # Data models (SpecSection, VerificationReport, …)
│   ├── utils.py              # Shared utilities
│   └── logging.py            # Debug log file management
├── exploration/
│   └── credentials.py        # Parses credentials markdown for login
└── spec_verifier/
    ├── orchestrator.py       # Drives the full verification loop
    ├── description_parser.py # Splits functional spec into SpecSections
    ├── checker.py            # LLM agent: spec text vs live page
    ├── prompts.py            # Checker prompt templates
    └── report.py             # Builds JSON + Markdown report
```

## Installation

```bash
# 1. Clone and enter the project
cd "Intelligent Navigator"

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -e .

# 4. Install Playwright's Chromium browser
playwright install chromium
```

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```ini
# .env

# LiteLLM model string — provider/model-name
LLM_MODEL=openai/gpt-4o-mini

# API key for your provider
OPENAI_API_KEY=sk-proj-...

# Default target application URL
TARGET_URL=http://localhost:8080

# Output directory for reports
OUTPUT_DIR=output

# Enable debug logging (writes full LLM prompts/responses to logs/)
DEBUG=false

# Suppress noisy LiteLLM provider warnings
LITELLM_LOG=ERROR
```

**Supported model formats (LiteLLM):**

| Provider | Example model string |
|---|---|
| OpenAI | `openai/gpt-4o-mini`, `openai/gpt-4o`, `openai/gpt-5-mini` |
| Anthropic | `anthropic/claude-3-5-sonnet-20241022` |
| OpenRouter | `openrouter/anthropic/claude-3.5-sonnet` |
| GitHub Models | `github/gpt-4o` |

> All models work regardless of whether they support `temperature` — LiteLLM handles it automatically.

## Quick Start

### 1. Write a functional description

Create a markdown file with `##` headings — one per page or feature:

```markdown
# My App Spec

## Login
The login page has an email field, a password field, and a "Sign In" button.

## Dashboard
Shows a welcome message and a table of recent activity.
```

### 2. (Optional) Create a credentials file

```markdown
## Accounts

| Username | Password | Role |
|----------|----------|------|
| admin@example.com | Admin123! | Admin |
```

### 3. Run

```bash
# Everything from .env — no flags needed
python -m intelligent_navigator \
    --functional-desc input/parabank/Parabank.md \
    --credentials input/parabank/Mock_Data.md

# Override specific settings per run
python -m intelligent_navigator \
    --functional-desc input/parabank/Parabank.md \
    --credentials input/parabank/Mock_Data.md \
    --model openai/gpt-4o \
    --url http://localhost:3000 \
    --debug
```

## CLI Reference

| Flag | Required | Default (env var) | Description |
|---|---|---|---|
| `--functional-desc` | ✅ | — | Path to functional description markdown |
| `--url` | — | `TARGET_URL` | Base URL of the web application |
| `--credentials` | — | `""` | Path to credentials markdown |
| `--output` | — | `OUTPUT_DIR` | Output directory for reports |
| `--model` | — | `LLM_MODEL` | LiteLLM model string |
| `--api-key` | — | `OPENAI_API_KEY` | API key (overrides .env) |
| `--debug` | — | `DEBUG` | Write full debug log to `logs/` |

## Input Files

### Functional Description

A markdown file with one `##` heading per page/feature. The tool infers the URL from the section name:

| Section heading | Inferred URL |
|---|---|
| `## Login` | `/login` |
| `## Register` | `/register` |
| `## Accounts Overview` | `/dashboard` |
| `## Open New Account` | `/open-account` |
| `## Transfer Funds` | `/transfer` |
| `## Payments` / `## Bill Pay` | `/bill-pay` |
| `## Request Loan` | `/loan` |
| `## Security Settings` | `/security` |
| anything else | `/slugified-name` |

The Navigator confirms the real URL by navigating in the browser — the hint is just a first guess.

### Credentials File

A markdown file with a table of accounts. The LLM extracts username, password, and role automatically:

```markdown
## Accounts

| Username | Password | Role |
|----------|----------|------|
| admin@example.com | Admin123! | Admin |
| user@example.com  | User123!  | User  |
```

## What the Checker Verifies

The checker examines only what is **visible in the static DOM snapshot**. It is intentionally lenient about things that require interaction:

| Category | Checked? | Reason |
|---|---|---|
| Fields, buttons, labels present | ✅ Yes | Visible in static DOM |
| Page structure / correct section | ✅ Yes | Visible in static DOM |
| Form validation errors | ❌ No | Only appear after submission |
| Real-time input formatting | ❌ No | Only appear while typing |
| Success / error messages | ❌ No | Only appear after action |
| Redirect behavior | ❌ No | Happens post-submission |

**Verdict thresholds:**

| Score | Verdict |
|---|---|
| ≥ 75 | ✅ Pass |
| 40 – 74 | ⚠️ Partial |
| < 40 | ❌ Fail |

## Output

Two files are written to `--output`:

| File | Contents |
|---|---|
| `verification_report.json` | Full machine-readable results |
| `verification_report.md` | Human-readable report with emoji verdict badges |

### Example report

```
Overall score : 87 / 100
Sections      : 13 total
  ✅ Pass    : 10
  ⚠️  Partial : 3
  ❌ Fail    : 0
```

```markdown
### ✅ Accounts Overview — PASS (90/100)

**✔ Matches:**
- Welcome message with user's name
- Accounts table with Account Number, Type, Balance, Status, Date columns
- Account numbers masked (****5001 format)
- Total balance footer row
- Active badge on account status

**✘ Missing:**
- (none)
```

## Debug Logging

Run with `--debug` (or set `DEBUG=true` in `.env`) to write a full trace to `logs/`:

```
[DEBUG] Log file: intelligent_navigator/logs/verification_debug_20260531_000000.log
```

The log contains for each section:
- Captured page body text
- DOM selector map (first 3000 chars)
- Full LLM prompt sent to checker
- Full LLM response (JSON verdict)

## Programmatic API

```python
from intelligent_navigator import SpecVerifier

config = {
    "base_url": "http://localhost:8080",
    "functional_desc_file": "input/parabank/Parabank.md",
    "credentials_file": "input/parabank/Mock_Data.md",
    "output_dir": "output/",
    "api_key": "sk-...",
    "model_name": "openai/gpt-4o-mini",
    "debug": False,
}

verifier = SpecVerifier(config)
report = verifier.run()

print(f"Overall score: {report.overall_score:.0f}/100")
for result in report.section_results:
    print(f"  {result.section_name}: {result.verdict} ({result.compliance_score}/100)")
```

## Example Project — Parabank

`input/parabank/` contains a complete example for a banking demo app:
- **`Parabank.md`** — full functional spec (13 sections)
- **`Mock_Data.md`** — seeded user credentials

`examples/parabank/` contains the actual Parabank web app (Node.js + Vite + PostgreSQL):

```bash
# Start the app
cd examples/parabank
docker compose up --build
# Frontend → http://localhost:8080

# Run the verifier
cd ../..
python -m intelligent_navigator \
    --functional-desc input/parabank/Parabank.md \
    --credentials input/parabank/Mock_Data.md
```

Typical result:
```
Overall score : 87 / 100
  ✅ Pass    : 10 / 13
  ⚠️  Partial : 3 / 13
  ❌ Fail    : 0 / 13
LLM calls used: 15
```
