# Intelligent Navigator

An LLM-powered **spec verifier** that reads a **functional description**, autonomously navigates a live web application using a real browser, and verifies whether the implementation matches the spec — with **zero hardcoded URLs or keyword mappings**.

---

## How It Works

```
┌─────────────────────────────────┐
│  Input files (Markdown)         │
│  ● Functional spec              │
│  ● Credentials / Mock data      │
└────────────┬────────────────────┘
             │
             ▼
    ┌───────────────────────┐
    │  TraversalOrchestrator│  Drives agentic BFS traversal
    └────────┬──────────────┘
             │
    ┌────────▼─────────────────────────────────────────┐
    │  Phase 1 — Public Traversal                      │
    │                                                  │
    │  Landing page ──▶ LinkDiscoveryAgent             │
    │                       │ ranked candidate links   │
    │                  Navigator (click/navigate)      │
    │                       │ lands on page            │
    │                  PageIdentifierAgent             │
    │                       │ matched spec section     │
    │                  SpecCheckerAgent                │
    │                       │ DOM + screenshot vs spec │
    │                  result stored ──▶ repeat BFS    │
    └──────────────────────────────────────────────────┘
             │
    ┌────────▼─────────────────────────────────────────┐
    │  Phase 2 — Per-Role Authenticated Traversal      │
    │                                                  │
    │  For each credential set:                        │
    │    login → fresh BFS from base URL → logout      │
    │    (same agent pipeline, auth-gated sections)    │
    └──────────────────────────────────────────────────┘
             │
             ▼
    verification_report.{json,md}
```

---

## Architecture

```
intelligent_navigator/
├── __init__.py                   # Exports: SpecVerifier (alias), VerificationReport
├── __main__.py                   # CLI entry point
├── agents/
│   ├── navigator.py              # Tactical agent: click-based multi-step navigation
│   ├── link_discovery.py         # Discovers & ranks links for unvisited spec sections
│   ├── page_identifier.py        # Identifies which spec section a live page matches
│   └── prompts.py                # All agent prompt templates
├── browser/
│   ├── controller.py             # Playwright command execution (click, type, scroll, …)
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
└── spec_verifier/
    ├── __init__.py               # Exports TraversalOrchestrator, SpecVerifier alias
    ├── orchestrator.py           # Two-phase BFS traversal loop
    ├── description_parser.py     # Splits functional spec into SpecSections
    ├── checker.py                # LLM: spec text vs live DOM (SpecCheckerAgent)
    ├── prompts.py                # Spec checker prompt templates
    └── report.py                 # Builds verification_report.{json,md}
```

---

## Agents

### TraversalOrchestrator
Drives the full verification run. Implements a BFS traversal loop across the live app using the three sub-agents below. No hardcoded URL tables or keyword mappings — all navigation is inferred from the live DOM.

**Two-phase execution:**
- **Phase 1 — Public traversal**: starts from `base_url`, discovers and verifies all publicly accessible spec sections.
- **Phase 2 — Authenticated traversal**: for each credential set, logs in fresh and re-runs the BFS to reach auth-gated sections. Results are merged (auth result preferred when better than public result).

**BFS circuit-breakers:**
- Max `200` visited URLs per phase
- Max `2` retries back to `base_url` when the frontier is empty

### LinkDiscoveryAgent (`agents/link_discovery.py`)
Given the current page, discovers which links are likely to lead to each unvisited spec section.

1. **Exposes hidden navigation** — hovers/clicks common nav toggle selectors (`[aria-haspopup]`, `button[class*='dropdown-toggle']`, hamburger buttons, etc.) to reveal dropdown menus before link extraction.
2. **Extracts all anchor links** from the fully-expanded DOM (up to 80 links, filtered for `javascript:` / `mailto:` / fragment-only hrefs).
3. **Asks an LLM** to rank links against the list of unvisited spec sections and return a confidence score (0–100) per match.
4. Only candidates with **confidence ≥ 60** are returned as `CandidateLink` objects.

### PageIdentifierAgent (`agents/page_identifier.py`)
After the Navigator lands on a page, this agent determines which spec section (if any) the page implements.

- Receives: current URL, page title, visible body text + DOM selector map.
- Asks an LLM to match the page against all spec sections.
- Returns `(section_name, confidence)`. Sections with **confidence < 60** are treated as no-match.
- Prevents double-counting: already-verified sections are skipped.

### Navigator (`agents/navigator.py`)
Tactical agent that physically navigates the browser to a given URL.

1. **Fast path** — tries direct URL navigation first (0 LLM calls).
2. **Multi-step LLM loop** (up to 5 steps) — reads the current DOM, asks the LLM which elements to click/type/hover, executes those actions, and checks if the target URL is reached. Carries full step history for route planning.
3. **Fallback** — if the loop exhausts all steps, retries direct URL navigation.
4. Also handles **login** (fills form with provided credentials) and **logout** commands.

Supported browser actions: `click_element`, `input_text`, `scroll_down`, `scroll_up`, `go_back`, `hover`, `select_option`, `press_key`, `clear_input`, `wait_for_element`, `switch_tab`, `open_tab`.

### SpecCheckerAgent (`spec_verifier/checker.py`)
Verifies a matched page against its spec section.

- Input: spec section text + visible DOM content (body text + selector map).
- Optionally attaches a **full-page screenshot** if the model is vision-capable.
- Returns a `compliance_score` (0–100) and structured notes.

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
LLM_MODEL=openai/gpt-5-mini

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

```bash
python -m intelligent_navigator \
    --functional-desc datasets/parabank/Parabank.md \
    --credentials datasets/parabank/Mock_Data.md
```

### Override settings per run
```bash
python -m intelligent_navigator \
    --functional-desc datasets/parabank/Parabank.md \
    --credentials datasets/parabank/Mock_Data.md \
    --model openai/gpt-4o \
    --url http://localhost:3000 \
    --debug
```

---

## CLI Reference

| Flag | Default (from .env) | Description |
|---|---|---|
| `--functional-desc` | — | Path to functional spec markdown (**required**) |
| `--credentials` | `""` | Path to credentials markdown for automatic login |
| `--url` | `TARGET_URL` | Base URL of the application |
| `--output` | `OUTPUT_DIR` | Output directory for reports |
| `--model` | `LLM_MODEL` | LiteLLM model string |
| `--api-key` | `OPENAI_API_KEY` | API key (overrides .env) |
| `--debug` | `DEBUG` | Write full debug log to `logs/` |

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

### Credentials File
A markdown table of accounts. The LLM extracts username, password, role, and seed data automatically:

```markdown
| Username | Password | Role |
|----------|----------|------|
| admin@example.com | Admin123! | Admin |
```

Multiple roles trigger separate authenticated traversal phases (one per distinct role).

---

## What Gets Verified

Checks only what is **visible in the static DOM snapshot** of each matched page:

| Category | Checked? |
|---|---|
| Fields, buttons, labels present | ✅ |
| Page structure / correct section | ✅ |
| Form validation errors | ❌ (post-submission) |
| Success/error messages | ❌ (post-action) |
| Redirect behavior | ❌ (post-submission) |

**Verdicts:** Pass (≥75) · Partial (40–74) · Fail (<40) · Skipped (section not reached)

---

## Vision Support

If your model is vision-capable (gpt-4o, gpt-5-mini, claude-3, gemini), the tool automatically:
1. Takes a full-page screenshot after DOM capture
2. Attaches it to every `SpecCheckerAgent` call alongside the DOM text
3. Falls back to text-only if the vision call fails for any reason

No configuration needed — vision is enabled automatically based on the model name.

---

## Output Files

| File | Contents |
|---|---|
| `output/verification_report.json` | Machine-readable results per section + per-role LLM call breakdown |
| `output/verification_report.md` | Human-readable report |

The JSON report includes per-agent LLM call counts:
```json
"extra_stats": {
  "llm_calls_orchestrator": 1,
  "llm_calls_navigator": 12,
  "llm_calls_page_identifier": 15,
  "llm_calls_link_discovery": 8,
  "llm_calls_checker": 13,
  "roles_verified": ["public", "admin"]
}
```

---

## Debug Logging

Run with `--debug` (or `DEBUG=true` in `.env`) to write a full trace to `logs/`:

```
[DEBUG] Log file: intelligent_navigator/logs/traversal_debug_20260604_012345.log
```

The log contains for each traversal step:
- Which agent is running and its decision
- Captured page body text and DOM selector map
- Full LLM prompts sent and responses received
- Vision call indicators (`[VISION]` prefix)
- BFS frontier state and visited URL set

---

## Programmatic API

```python
from intelligent_navigator import SpecVerifier

config = {
    "base_url": "http://localhost:8080",
    "api_key": "sk-...",
    "model_name": "openai/gpt-4o-mini",
    "output_dir": "output/",
    "debug": False,
    "functional_desc_file": "datasets/parabank/Parabank.md",
    "credentials_file": "datasets/parabank/Mock_Data.md",  # optional
}

report = SpecVerifier(config).run()
print(f"Score: {report.overall_score:.0f}/100")
print(f"Pass: {report.passed} | Partial: {report.partial} | Fail: {report.failed} | Skipped: {report.skipped}")
```

> `SpecVerifier` is a backward-compatible alias for `TraversalOrchestrator`.

---

## Example — Parabank

`datasets/parabank/` contains a complete example for an online banking demo app:
- **`Parabank.md`** — functional spec (13 sections)
- **`Mock_Data.md`** — seeded user credentials and account data

```bash
# Start the app
cd examples/parabank
docker compose up --build
# Frontend → http://localhost:8080

# Run Spec Verifier
cd ../..
python -m intelligent_navigator \
    --functional-desc datasets/parabank/Parabank.md \
    --credentials datasets/parabank/Mock_Data.md
```
