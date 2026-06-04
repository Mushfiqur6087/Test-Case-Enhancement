# Intelligent Navigator

An LLM-powered **spec verifier** that reads a functional specification (markdown), autonomously navigates a live web application, and verifies whether every described section is correctly implemented — with **zero hardcoded URLs, selectors, or keyword mappings**.

> **Latest result:** Swag Labs (saucedemo.com) — **10/10 sections PASS · 94/100 overall · 69 LLM calls**

---

## How It Works

```
Functional Spec (markdown)  +  Credentials (markdown)  +  Base URL
                │
                ▼
    ┌─────────────────────────┐
    │  TraversalPlanner (LLM) │  1 call — reads spec → ordered plan with typed steps
    └────────────┬────────────┘
                 │
         for each step in plan:
                 │
         ┌───────▼──────────────────────────────────────────┐
         │  Already on target page?                         │
         │     YES → skip navigation → verify in place      │
         │     NO  ↓                                        │
         │                                                  │
         │  form_gateway?  ──▶  Phase A: navigate + verify  │
         │                      Phase B: fill + submit       │
         │                                                  │
         │  Normal step:                                    │
         │    ActionEngine  (navigate ONLY, stop on arrival)│
         │         │                                        │
         │    PageIdentifier (which spec section is this?)  │
         │         │                                        │
         │    SpecChecker   (DOM + screenshot vs spec text) │
         │         │                                        │
         │    PostVerify    (run interactions_needed:       │
         │                   e.g. "add item to cart")       │
         └──────────────────────────────────────────────────┘
                 │
                 ▼  (step failed? → Replanner → new approach → retry)
                 │
    verification_report.{json, md}
```

---

## Architecture

```
intelligent_navigator/
├── __main__.py                     CLI entry point
├── agents/
│   ├── traversal_planner.py        Reads spec → generates ordered TraversalPlan
│   ├── action_engine.py            Goal-oriented browser executor (multi-step LLM loop)
│   ├── page_identifier.py          Identifies which spec section a live page matches
│   └── prompts.py                  All agent prompt templates
├── browser/
│   ├── controller.py               Playwright command execution (click, type, scroll, …)
│   ├── dom_builder.py              JS DOM extraction with enhanced visibility detection
│   ├── dom_parser.py               DOM tree parsing + interactive element mapping
│   ├── dom_helper.py               Full-page scroll-and-capture for lazy-loaded content
│   ├── selector_filter.py          DOM noise removal (decorative/skip elements)
│   ├── screenshot.py               Base64 full-page screenshot capture
│   └── session.py                  Playwright browser session management
├── core/
│   ├── llm.py                      LiteLLM client (text + vision)
│   ├── models.py                   Shared data models
│   ├── utils.py                    URL/title helpers
│   └── logging.py                  Debug log file management
├── exploration/
│   └── credentials.py              Parses credentials markdown → login data
└── spec_verifier/
    ├── orchestrator.py             Main execution loop — drives the full traversal
    ├── description_parser.py       Splits functional spec into SpecSection objects
    ├── checker.py                  SpecCheckerAgent — DOM + screenshot vs spec text
    ├── prompts.py                  Spec checker prompt templates
    └── report.py                   Builds verification_report.{json, md}
```

---

## Agents

### TraversalPlanner (`agents/traversal_planner.py`)

Called once at the start. Reads all spec sections and produces an **ordered `TraversalPlan`** — a list of typed steps with dependency information:

```python
TraversalStep(
    target_section   = "Shopping Cart",
    page_type        = "listing",          # form_gateway | listing | detail |
                                           # overlay | action | summary | confirmation
    how_to_reach     = "Click the cart icon from the inventory page",
    prerequisites    = ["at least one item in cart"],
    interactions_needed = "Click 'Add to cart' on the Sauce Labs Backpack",
)
```

- Understands the dependency graph (e.g., cart before checkout, login before inventory)
- Puts destructive steps (Logout, Reset) last
- Also used for **replanning** — if a step fails, generates an alternative `how_to_reach`

---

### ActionEngine (`agents/action_engine.py`)

Goal-oriented browser executor. Replaces the old Navigator + LinkDiscovery agents.

**Execution loop (per goal):**

```
Step 1: Read current DOM (selector map) + page title + URL
        → Ask LLM: what actions achieve the goal?
        → Execute actions via BrowserController
        → Check: goal_achieved? or goal_failed?
Step 2: Repeat with full action history until:
        - LLM signals goal_achieved (success)
        - LLM signals goal_failed (give up)
        - Max steps reached (stagnation guard)
```

**Key design rules enforced by the system prompt:**
- Navigation goals: **STOP immediately on arrival** — do not interact with the destination page
- Never click "Back", "Cancel", or return-navigation unless explicitly asked
- `goal_achieved = true` only after observing the URL/page change

**Supported browser actions:**

| Action | Description |
|---|---|
| `click_element` | Click an element by its DOM index |
| `input_text` | Type into a field by index |
| `clear_input` | Clear a field by index |
| `select_option` | Choose a `<select>` option by value or text |
| `hover` | Hover over an element |
| `scroll_down` / `scroll_up` | Scroll the page |
| `press_key` | Send keyboard input (Escape, Enter, Tab, …) |
| `navigate_to` | Direct URL navigation |
| `wait_for_element` | Wait for text to appear in the DOM |
| `go_back` | Browser back button |

---

### PageIdentifier (`agents/page_identifier.py`)

After every navigation, identifies which spec section the current page implements.

- Input: current URL, page title, visible body text + DOM selector map
- Matches against **only unvisited sections** (already-verified sections are excluded)
- Returns `(section_name, confidence)` — sections with confidence < 60 are treated as no-match
- For `overlay` and `action` type steps, verifies in-place even without a URL match

---

### SpecChecker (`spec_verifier/checker.py`)

Verifies a matched page against its spec section text.

- Input: spec section text + visible DOM (body text + selector map)
- Optionally attaches a **full-page screenshot** for vision-capable models
- Returns `compliance_score` (0–100), `matches`, `missing`, `mismatches`

---

### TraversalOrchestrator (`spec_verifier/orchestrator.py`)

The main execution loop. Coordinates all agents and manages state.

**Execution flow for each step:**

```
1. "Already here?" check
      PageIdentifier matches current page to target section (≥70% confidence)?
      → YES: skip navigation, verify in place, run post-verify interactions
      → NO:  continue below

2. form_gateway? (Login, Checkout Info, etc.)
      Phase A: ActionEngine navigates to the form page (navigation goal only)
               PageIdentifier confirms arrival
               SpecChecker verifies the form page (BEFORE submission)
      Phase B: ActionEngine executes interactions_needed (fill + submit)
               → lands on next page for subsequent steps

3. Normal step
      ActionEngine executes navigation goal (STOP on arrival)

      ← URL-change guard: if URL unchanged after action, retry once →
      (prevents premature goal_achieved declarations from the LLM)

      PageIdentifier identifies the landed page
      SpecChecker verifies against spec
      _run_post_verify_interactions() executes interactions_needed
        → side-effect actions run AFTER verification (no overshoot risk)
        → satisfies prerequisites for subsequent steps (e.g., items in cart)

4. Failed step? → Replanner generates alternative approach → retry (max 2)
```

---

### DOM Builder (`browser/dom_builder.py`)

Extracts an interactive element map from the live page using injected JavaScript.

**Visibility detection (multi-layer):**
1. Hard check: `display: none`, `visibility: hidden`, `opacity: 0` → invisible
2. Standard: `offsetWidth > 0 && offsetHeight > 0` → visible
3. `getBoundingClientRect()` fallback — catches `position: fixed/absolute` elements
4. Child-rect check for interactive tags — catches icon buttons (e.g., hamburger menus) where the `<button>` has zero dimensions but its `<span>` children are visible
5. `aria-label` / `aria-expanded` presence → treat as visible (named controls)

**Subtree pruning:**
- `aria-hidden="true"` containers are skipped entirely (closed menus, decorative overlays)
- Parent visibility no longer prunes child subtrees — each element checks itself independently (fixes hamburger menus inside zero-height wrapper divs)

**Output:** a numbered `selector_map` passed to the LLM:
```
[0]<button id='react-burger-menu-btn' inner_text='Open Menu' />
[1]<a data-test='shopping-cart-link' inner_text='1' />
[2]<select data-test='product-sort-container' />
[3]<button data-test='add-to-cart-sauce-labs-backpack' inner_text='Add to cart' />
...
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

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

```ini
# .env

# LiteLLM model string — provider/model-name
# Vision-capable models (gpt-4o, gpt-5-mini, claude-3, gemini) send screenshots automatically
LLM_MODEL=openai/gpt-5-mini

# API key for your provider
OPENAI_API_KEY=sk-proj-...

# Target application base URL
TARGET_URL=http://localhost:8080

# Output directory for reports
OUTPUT_DIR=output

# Enable debug logging (writes full LLM prompts/responses to logs/)
DEBUG=false
```

**Supported model formats (LiteLLM):**

| Provider | Example | Vision? |
|---|---|---|
| OpenAI | `openai/gpt-4o`, `openai/gpt-5-mini` | ✅ |
| Anthropic | `anthropic/claude-3-5-sonnet-20241022` | ✅ |
| OpenRouter | `openrouter/anthropic/claude-3.5-sonnet` | ✅ |
| OpenAI (text only) | `openai/gpt-3.5-turbo` | ❌ |

---

## Usage

```bash
python -m intelligent_navigator \
    --functional-desc datasets/swaglabs/SwagLabs,md \
    --credentials datasets/swaglabs/Mock_Data.md
```

### Override settings per run
```bash
python -m intelligent_navigator \
    --functional-desc datasets/swaglabs/SwagLabs,md \
    --credentials datasets/swaglabs/Mock_Data.md \
    --model openai/gpt-4o \
    --url https://www.saucedemo.com \
    --debug
```

---

## CLI Reference

| Flag | Default (from .env) | Description |
|---|---|---|
| `--functional-desc` | — | Path to functional spec markdown (**required**) |
| `--credentials` | `""` | Path to credentials markdown |
| `--url` | `TARGET_URL` | Base URL of the application |
| `--output` | `OUTPUT_DIR` | Output directory for reports |
| `--model` | `LLM_MODEL` | LiteLLM model string |
| `--api-key` | `OPENAI_API_KEY` | API key (overrides .env) |
| `--debug` | `DEBUG` | Write full debug log to `logs/` |

---

## Input Files

### Functional Specification

A markdown file with one `##` heading per page/feature. The spec text under each heading is passed verbatim to the SpecChecker and is used by the TraversalPlanner to understand dependencies:

```markdown
## Login
The login page has a Username field, a Password field, and a Login button.
Valid credentials redirect to the Product Inventory page.
Invalid credentials show an error message.

## Shopping Cart
Accessible via the cart icon (badge shows item count).
Lists items with quantity, description, price, and a Remove button per item.
A Checkout button navigates to the checkout flow.
```

### Credentials File

A markdown table of accounts — the LLM extracts username, password, and role automatically:

```markdown
| Username       | Password      | Role          |
|----------------|---------------|---------------|
| standard_user  | secret_sauce  | standard user |
```

Multiple roles trigger a separate authenticated traversal phase per role.

---

## What Gets Verified

| Category | Checked? |
|---|---|
| Fields, buttons, labels present in DOM | ✅ |
| Page structure matches spec description | ✅ |
| Navigation flow (correct page reached) | ✅ |
| Cart / session state (items in cart) | ✅ |
| Visual layout (via screenshot if vision model) | ✅ |
| Dynamic validation errors (post-interaction) | ✅ (via interactions_needed) |
| Server-side redirect behaviour | ❌ |

**Verdicts:** Pass (≥75) · Partial (40–74) · Fail (<40) · Skipped (section not reached)

---

## Output

| File | Contents |
|---|---|
| `output/verification_report.json` | Machine-readable results per section + LLM call count |
| `output/verification_report.md` | Human-readable report |

Example console output:
```
============================================================
VERIFICATION COMPLETE
Sections: 10 | Pass: 10 | Partial: 0 | Fail: 0 | Skipped: 0
Overall score: 94/100
JSON   → output/verification_report.json
Report → output/verification_report.md
LLM calls: 69
============================================================
```

---

## Debug Logging

Run with `--debug` to write a full trace to `logs/traversal_debug_<timestamp>.log`:

```
[Step 7/13] Target: 'Shopping Cart' (listing)
[ActionEngine] Step 1: Click cart icon (index 1) → Swag Labs (https://.../cart.html)
[ActionEngine] Goal achieved at step 2
[Checker] 'Shopping Cart': PASS (100/100) | 7 matches, 0 missing
[PostVerify] Executing interactions: Verify item listing with Remove button...
[PostVerify] Done → Swag Labs (https://.../cart.html)
```

The log contains for each step:
- Agent decisions and LLM reasoning
- Captured selector map (numbered interactive elements)
- Full LLM prompts and responses
- Vision call indicators (`[VISION]` prefix)
- Progress summary after every verified section

---

## Programmatic API

```python
from intelligent_navigator import SpecVerifier

config = {
    "base_url": "https://www.saucedemo.com",
    "api_key": "sk-...",
    "model_name": "openai/gpt-5-mini",
    "output_dir": "output/",
    "debug": False,
    "functional_desc_file": "datasets/swaglabs/SwagLabs,md",
    "credentials_file": "datasets/swaglabs/Mock_Data.md",
}

report = SpecVerifier(config).run()
print(f"Score: {report.overall_score:.0f}/100")
print(f"Pass: {report.passed} | Fail: {report.failed} | Skipped: {report.skipped}")
```

---

## Example — Swag Labs

`datasets/swaglabs/` contains a complete example for the Sauce Labs demo e-commerce app:
- **`SwagLabs,md`** — functional spec (10 sections: Login, Inventory, Cart, Checkout ×3, Nav Menu, Logout, Reset)
- **`Mock_Data.md`** — standard_user credentials

```bash
python -m intelligent_navigator \
    --functional-desc datasets/swaglabs/SwagLabs,md \
    --credentials datasets/swaglabs/Mock_Data.md \
    --url https://www.saucedemo.com \
    --debug
```

**Result (gpt-5-mini, 69 LLM calls):**

| Section | Score | Verdict |
|---|---|---|
| Login | 95/100 | ✅ PASS |
| Product Inventory | 95/100 | ✅ PASS |
| Navigation Menu | 95/100 | ✅ PASS |
| Product Detail | 90/100 | ✅ PASS |
| Shopping Cart | 100/100 | ✅ PASS |
| Checkout - Information | 90/100 | ✅ PASS |
| Checkout - Overview | 95/100 | ✅ PASS |
| Checkout - Confirmation | 95/100 | ✅ PASS |
| Reset App State | 90/100 | ✅ PASS |
| Logout | 90/100 | ✅ PASS |
| **Overall** | **94/100** | **10/10 PASS** |
