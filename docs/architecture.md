# Architecture: LLM-Powered Spec Compliance Verifier

## Overview

**Test-Case-Enhancement** is an agentic, LLM-powered system that automatically verifies whether a live web application correctly implements its functional specification. It does this by:

1. Parsing a human-written functional description (Markdown) into discrete spec sections
2. Using an LLM to generate a dependency-aware traversal plan
3. Autonomously navigating the live web application using a Playwright-controlled browser
4. Verifying each page against its corresponding spec section via a compliance-checking LLM call
5. Enriching, auditing, and repairing existing test cases against the live DOM
6. Producing structured JSON + Markdown verification reports

The system is **fully domain-agnostic** — it works on any web application (e-commerce, banking, CMS, social media) without any hardcoded URLs, selectors, or application-specific logic.

---

## Design Philosophy

| Principle | Implementation |
|---|---|
| **Spec-driven** | No hardcoded URL patterns or application-specific logic. Everything flows from the functional description. |
| **Agentic** | An LLM interprets and executes goals in natural language — not rigid scripts. |
| **Self-correcting** | Low-scoring verifications trigger autonomous remediation and re-verification. |
| **Adaptive** | Step-by-step replanning when a navigation step fails. |
| **Provider-agnostic** | Uses LiteLLM to support OpenAI, Anthropic, Google Gemini, OpenRouter, and any compatible provider. |
| **Vision-aware** | Automatically upgrades to screenshot-based verification when a vision-capable model is configured. |

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLI / Entry Point                           │
│     python -m test_case_enhancement --url ... --functional-desc ... │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Coordinator (Orchestrator)                    │
│                   orchestrator/coordinator.py                       │
│                                                                     │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────────────┐   │
│  │SpecSection[] │  │ TraversalPlan  │  │ VerificationReport   │   │
│  │   (parsed)   │  │  (LLM-built)   │  │  (JSON + Markdown)   │   │
│  └──────────────┘  └────────────────┘  └──────────────────────┘   │
└────┬──────────┬──────────┬───────────────────┬──────────────────────┘
     │          │          │                   │
     ▼          ▼          ▼                   ▼
┌─────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────────────────┐
│ Nav     │ │Interaction│ │  State       │ │   Compliance Checker     │
│ Planner │ │  Agent   │ │  Identifier  │ │       Agent              │
│ Agent   │ │          │ │   Agent      │ │                          │
│(LLM)   │ │ (LLM +   │ │   (LLM)      │ │      (LLM ± vision)      │
│         │ │ Browser) │ │              │ │                          │
└─────────┘ └────┬─────┘ └──────────────┘ └──────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────────────┐
│                      Browser Layer                                  │
│   BrowserController → BrowserSession (Playwright) → Chromium      │
│   DOMHelper → FullPageDOMTreeParser → SelectorMap                  │
│   SelectorFilter (rule-based noise removal)                        │
└────────────────────────────────────────────────────────────────────┘
```

---

## Module Map

```
test_case_enhancement/
│
├── __main__.py             Entry point; loads .env, delegates to Coordinator
├── cli.py                  Argument parser; builds config dict
├── __init__.py             Public API: Coordinator, VerificationReport
│
├── orchestrator/
│   ├── coordinator.py      Central loop: plan → execute → verify → report
│   └── session_manager.py  (Reserved for future multi-session support)
│
├── agents/
│   ├── navigation_planner.py   TraversalPlannerAgent — generates ordered plan
│   ├── interaction_agent.py    InteractionAgent — goal-driven browser control
│   ├── state_identifier.py     StateIdentifierAgent — maps live pages → spec sections
│   ├── compliance_checker.py   ComplianceCheckerAgent — scores pages vs spec
│   ├── test_step_verifier.py   TestStepVerifierAgent — audits test case steps vs DOM
│   └── test_data_enricher.py   TestDataEnricherAgent — enriches/repairs test cases
│
├── browser/
│   ├── session.py          BrowserSession — Playwright lifecycle + multi-tab tracking
│   ├── controller.py       BrowserController — high-level command dispatcher
│   ├── dom_builder.py      DomTreeBuilder — raw Playwright DOM tree capture
│   ├── dom_parser.py       DOMTreeParser — converts raw DOM → element index map
│   ├── dom_helper.py       DOMHelper — scroll + full-page capture utility
│   ├── selector_filter.py  SelectorFilter — rule-based DOM noise removal
│   ├── screenshot.py       Screenshot capture (base64, PNG)
│   └── css_utils.py        CSS selector helpers
│
├── llm/
│   ├── client.py           LLMClient — LiteLLM wrapper; text + vision calls
│   └── prompts/
│       ├── __init__.py          Prompt registry (all exports)
│       ├── planner_prompts.py   System + user prompts for traversal planner
│       ├── interaction_prompts.py  System + step prompts for interaction agent
│       ├── state_prompts.py     System + user prompts for state identifier
│       ├── compliance_prompts.py   System + check prompts for compliance checker
│       ├── enricher_prompts.py  System + check prompts for TC verifier + enricher
│       └── credential_prompts.py   LLM prompt for credential extraction
│
├── parsers/
│   ├── spec_parser.py        DescriptionParser — splits markdown → SpecSection[]
│   ├── testcase_parser.py    parse_test_cases() — parses test case markdown tables
│   └── mockdata_parser.py    CredentialParser — LLM-assisted credential extraction
│
├── core/
│   ├── logging.py            DebugLogger — timestamped debug file management
│   ├── utils.py              Shared helpers: log(), parse_llm_json(), wait_for_page()
│   └── models/
│       ├── __init__.py       Re-exports all dataclasses
│       ├── spec.py           SpecSection, SectionVerificationResult, VerificationReport
│       ├── test_case.py      TestCase, TestCaseStep, TestCaseVerificationResult, EnrichedTestCase
│       └── common.py         RoleCredentials
│
└── reporting/
    ├── generator.py          build_report() + write_report() — JSON + Markdown output
    └── markdown_renderer.py  render_markdown() — human-readable report formatting
```

---

## Data Flow

### Input → Processing → Output

```
INPUTS
  datasets/<app>/
  ├── <App>.md          Functional specification (markdown)
  ├── Test_Cases.md     Existing test case suite (optional)
  └── Mock_Data.md      Test credentials + mock data (optional)

  .env / CLI flags
  ├── TARGET_URL        Base URL of the application under test
  ├── LLM_MODEL         LiteLLM model string (e.g., openai/gpt-4o-mini)
  ├── OPENAI_API_KEY    (or ANTHROPIC_API_KEY / OPENROUTER_API_KEY)
  └── OUTPUT_DIR        Where to write reports

PROCESSING
  Coordinator.run()
  → parse spec → build plan → execute steps → verify pages → enrich TCs

OUTPUTS
  output/<app>/
  ├── verification_report.json     Full machine-readable report
  ├── verification_report.md       Human-readable verification results
  ├── enriched_test_cases.json     Enriched + repaired test cases (JSON)
  ├── enriched_test_cases.md       Enriched test cases (Markdown)
  ├── audited_test_cases.json      Test case DOM audit results (JSON)
  └── audited_test_cases.md        Test case audit summary (Markdown)
```

---

## Key Data Structures

### SpecSection
```python
@dataclass
class SpecSection:
    name: str       # e.g. "Login", "Product Inventory"
    raw_text: str   # Full markdown body of this section
```

### TraversalStep
```python
@dataclass
class TraversalStep:
    target_section: str       # Exact SpecSection.name to verify
    page_type: str            # form_gateway | listing | detail | overlay | action | summary | confirmation
    how_to_reach: str         # Natural language navigation instruction
    prerequisites: List[str]  # Required prior state
    interactions_needed: str  # Post-verification side effects
    phase: str                # "public" or "authenticated"
```

### SectionVerificationResult
```python
@dataclass
class SectionVerificationResult:
    section_name: str
    actual_url: str
    actual_title: str
    verdict: str              # "pass" | "partial" | "fail" | "skipped"
    compliance_score: int     # 0–100
    matches: List[str]        # Spec requirements found in live UI
    missing: List[str]        # Spec requirements NOT found
    mismatches: List[str]     # DOM items that contradict the spec
    notes: str
    navigation_success: bool
    test_case_results: List[TestCaseVerificationResult]
    enriched_test_cases: List[EnrichedTestCase]
```

### VerificationReport
```python
@dataclass
class VerificationReport:
    project_url: str
    functional_desc_file: str
    captured_at: str
    sections_checked: int
    passed: int
    partial: int
    failed: int
    skipped: int
    overall_score: float          # Weighted average across all non-skipped sections
    section_results: List[SectionVerificationResult]
    llm_calls_total: int
    verification_stats: Dict[str, Any]   # Per-agent LLM call breakdown
```

---

## Agent Architecture

The system uses **five specialized LLM agents**, each with its own system prompt and a single responsibility:

### 1. NavigationPlannerAgent
- **Role**: Reads the entire functional spec and generates a dependency-ordered traversal plan
- **Input**: All `SpecSection` objects, base URL, credential info
- **Output**: `TraversalPlan` with ordered `TraversalStep` objects
- **Key behaviors**:
  - One LLM call for the full plan
  - Understands page type taxonomy (form_gateway, listing, detail, overlay, action, summary, confirmation)
  - Orders destructive actions (logout, reset) last
  - Separates phases: `public` vs. `authenticated`
  - Falls back to a sequential plan if the LLM fails
- **Adaptive capabilities** (during execution):
  - `replan_step()` — alternative routing when a step fails
  - `advise_next_step()` — lightweight inter-step validation

### 2. InteractionAgent
- **Role**: Goal-oriented browser action execution engine
- **Input**: Natural-language goal, current DOM state, optional screenshot
- **Output**: `ActionResult` (success/failure + current URL/title)
- **Key behaviors**:
  - Multi-step loop (up to 4 steps by default, configurable)
  - Reads full page DOM as a selector map (indexed elements)
  - Passes step history to LLM for context
  - Executes: click, fill, navigate, go_back, hover, select, press_key, close_tab, switch_tab
  - Stagnation detection: fails if URL and DOM unchanged after 2 consecutive steps
  - Multi-tab aware: injects tab context into prompts, captures screenshots per tab

### 3. StateIdentifierAgent
- **Role**: Determines which spec section the current live page implements
- **Input**: Current URL, title, page content, all spec sections
- **Output**: `(section_name, confidence_score)` — or `(None, 0)` if no match
- **Key behaviors**:
  - Confidence threshold: 60% (lower = treated as no match)
  - Validates returned section name against the known set
  - Enables opportunistic verification (can verify a section found "on the way")

### 4. ComplianceCheckerAgent
- **Role**: Scores a live page against its spec section
- **Input**: `SpecSection`, page title/URL, DOM content (or before+after for actions), optional screenshot(s)
- **Output**: `SectionVerificationResult` with score, matches, missing, mismatches, notes
- **Key behaviors**:
  - Score thresholds: ≥75 = pass, ≥40 = partial, <40 = fail
  - Vision-capable: accepts before+after screenshots for action-type steps
  - Handles state-transition verification (before URL → after URL diff)

### 5. TestStepVerifierAgent + TestDataEnricherAgent (paired)
- **Role**: Audit and repair human-authored test cases against the live DOM
- **TestStepVerifier** — checks each test case step's feasibility against the current page DOM
- **TestDataEnricher** — repairs broken steps, fills in real test data, marks dropped cases
- **Output**: `TestCaseVerificationResult[]` + `EnrichedTestCase[]`

---

## Browser Layer Architecture

### BrowserSession (Playwright lifecycle)
- Manages Playwright instance, browser, context, and pages
- Tracks multiple tabs in `_tabs: List[Page]`
- Fires `_on_new_page_opened()` for `target="_blank"` links and popups
- Provides `get_tab_context_string()` for multi-tab LLM context injection
- Maintains `_selector_map` cache — shared with `BrowserController` to guarantee index consistency

### BrowserController (command dispatcher)
- Wraps `BrowserSession` with typed command methods
- Dispatches: `click_element`, `input_text`, `navigate_to`, `go_back`, `hover`, `select_option`, `press_key`, `clear_input`, `wait_for_element`, `close_tab`, `switch_to_tab`
- Overlay-dismiss fallback: if a click fails, presses Escape then retries with `force=True`
- Cache invalidation: clears `_parser` and `_selector_map` after navigation actions

### DOM Pipeline
```
BrowserSession.get_current_page()
        │
        ▼
FullPageDomTreeBuilder.get_dom_tree()     ← captures ALL elements (ignores viewport)
        │
        ▼
FullPageDOMTreeParser.parse()             ← builds DOMElementNode tree with XPaths
        │
        ▼
DOMHelper.scroll_and_capture()            ← scrolls page, triggers lazy-load, captures
        │
        ├── selector_map_json             ← Dict[index, element_attrs]  (for controller)
        └── selector_map_string           ← Human-readable "[idx]<tag attr='val' />"
                │
                ▼
        SelectorFilter.filter()           ← removes: aria-hidden, icon <i>, calendar cells,
                                            redundant child spans, decorative anchors
```

The **selector map** is the critical shared state:
- `DOMHelper` builds it and writes it to `BrowserSession._selector_map`
- `InteractionAgent` reads the string and sends it to the LLM
- `BrowserController` reads the same map to resolve `index → XPath`
- This single shared instance prevents index divergence ("index not in selector_map" errors)

---

## LLM Client Architecture

```python
class LLMClient:
    model_name: str          # LiteLLM model string
    system_prompt: str       # Role-specific system prompt
    supports_vision: bool    # Auto-detected from model_name
    
    def ask(user_prompt) → str                          # Text-only call
    def ask_with_screenshot(user_prompt, b64) → str     # Vision call (falls back to text)
```

**Vision detection** uses substring matching against known vision-capable model families:
`gpt-4o`, `gpt-5`, `gpt-4-turbo`, `claude-3`, `gemini`, `vision`

**LiteLLM configuration**:
- `litellm.drop_params = True` — silently drops unsupported parameters (e.g., `temperature` on reasoning models)
- `num_retries=2`, `timeout=120` (180s for vision)
- Temperature: `0.2` for consistent structured JSON output

Each agent instantiates its **own** `LLMClient` with a role-specific `system_prompt`. This keeps agents behaviorally isolated even when sharing the same model and API key.

---

## Prompt Architecture

Each agent has a pair of prompts — a system prompt (role definition) and a user/step prompt (per-call template):

| Agent | System Prompt | User/Step Prompt |
|---|---|---|
| NavigationPlannerAgent | `PROMPT_TRAVERSAL_PLANNER_SYSTEM` | `PROMPT_TRAVERSAL_PLANNER_USER` |
| InteractionAgent | `PROMPT_INTERACTION_AGENT_SYSTEM` | `PROMPT_INTERACTION_AGENT_STEP` |
| StateIdentifierAgent | `PROMPT_STATE_IDENTIFIER_SYSTEM` | `PROMPT_STATE_IDENTIFIER_USER` |
| ComplianceCheckerAgent | `PROMPT_COMPLIANCE_CHECKER_SYSTEM` | `PROMPT_COMPLIANCE_CHECKER_CHECK` |
| TestStepVerifierAgent | `PROMPT_STEP_CHECKER_SYSTEM` | `PROMPT_STEP_CHECKER_CHECK` |
| TestDataEnricherAgent | `PROMPT_ENRICHER_SYSTEM` | `PROMPT_ENRICHER_CHECK` |
| Replanning (inline) | (lightweight system prompt) | `PROMPT_REPLAN_STEP` |
| Step Advisor (inline) | (lightweight system prompt) | `PROMPT_STEP_ADVISOR` |
| Prerequisite Check | (inline in coordinator) | `PROMPT_ACTION_PREREQUISITE_CHECK` |
| Credential Parsing | (none — uses base LLM) | `PROMPT_CREDENTIAL_PARSING` |

All LLM responses are expected to be **valid JSON objects**. `parse_llm_json()` handles markdown code fence stripping before JSON parsing.

---

## Coordinator Execution Loop

The `Coordinator.run()` method is the central control flow:

```
1. Parse spec → SpecSection[]
2. Parse credentials → RoleCredentials[]
3. Parse test cases → Dict[module_name, TestCase[]]   (optional)
4. Navigate to base URL
5. NavigationPlannerAgent.generate_plan() → TraversalPlan
6. For each TraversalStep in plan.steps:
   a. Already-here check (skip navigation if already on target page)
   b. Branch on page_type:
      ├── form_gateway → two-phase (navigate + verify form, then submit)
      ├── action       → before/after snapshot + execute + diff verify
      └── all others   → navigate → identify → verify
   c. Low-score remediation: if score < 50 → remediate → re-verify (once)
   d. Post-verify interactions (prepare next step's prerequisites)
   e. Adaptive step validation: check next planned step is still valid
   f. Replanning: if navigation fails → try up to 2 alternative approaches
7. Handle any unreached sections → mark as "skipped"
8. Build VerificationReport
9. Write JSON + Markdown reports
```

---

## Step Execution Branches

### Branch A: `form_gateway` (Two-Phase)
Used for login forms, registration, data entry forms.

```
Phase A: Navigate to the form page
         → InteractionAgent.execute_goal(nav_goal)
         → StateIdentifierAgent.identify()   ← confirms we're on the form
         → ComplianceCheckerAgent.check()    ← verifies form structure BEFORE submit

Phase B: Fill and submit the form
         → InteractionAgent.execute_goal(step.interactions_needed)
         ← credentials injected if this is an auth-intent step
```

This design ensures form pages are **verified before** submission navigates away.

### Branch B: `action` (Before/After Snapshots)
Used for logout, reset state, delete actions.

```
0. Prerequisite check:
   → Ask LLM: "what observable state must exist before this action?"
   → If missing: InteractionAgent establishes it (e.g., add item to cart before "Reset Cart")

1. Capture BEFORE state (URL, title, DOM, optional screenshot)

2. Execute action:
   → InteractionAgent.execute_goal(goal, max_steps=3)

3. Capture AFTER state

4. Build combined context:
   ├── Vision model: "Before URL: X, After URL: Y" + two screenshots
   └── Text model: full before DOM + full after DOM

5. ComplianceCheckerAgent.check(combined_context)
   ← checker reasons about the STATE TRANSITION, not just the page
```

### Branch C: Unified (listing, detail, overlay, summary, confirmation)
```
1. InteractionAgent.execute_goal(nav_goal)
2. StateIdentifierAgent.identify()         ← which section did we land on?
   ├── Matched expected section → verify it
   ├── Matched a different unvisited section → verify that instead (opportunistic)
   └── No match + overlay/action type → verify in-place (no URL change expected)
3. ComplianceCheckerAgent.check()
4. Low-score remediation if score < 50
5. Post-verify interactions (e.g., click a product to set up detail page)
```

---

## Self-Correction Mechanisms

| Mechanism | Trigger | Action |
|---|---|---|
| **Remediation loop** | Compliance score < 50 | InteractionAgent reveals hidden content (menus, accordions, modals), then re-verifies once |
| **Step replanning** | InteractionAgent navigation fails | NavigationPlannerAgent generates alternative routing (up to 2 attempts) |
| **Step advisor** | After every successful step | Planner validates next step; adjusts `how_to_reach` and executes prerequisites |
| **Prerequisite setup** | Before `action`-type steps | LLM checks if required observable state exists; InteractionAgent sets it up |
| **Stagnation detection** | InteractionAgent sees no change | Exits after 2 consecutive steps with same URL + same DOM |
| **Already-here optimization** | StateIdentifier ≥ 70% confidence | Skips navigation, verifies in-place |

---

## Configuration

| CLI Flag | Env Variable | Default | Description |
|---|---|---|---|
| `--url` | `TARGET_URL` | (required) | Base URL of the web app |
| `--functional-desc` | — | (required) | Path to functional spec markdown |
| `--credentials` | — | — | Path to credentials markdown |
| `--test-cases` | — | — | Path to test cases markdown |
| `--output` | `OUTPUT_DIR` | `output` | Output directory |
| `--api-key` | `OPENAI_API_KEY` etc. | (required) | LLM API key |
| `--model` | `LLM_MODEL` | `openai/gpt-4o-mini` | LiteLLM model string |
| `--debug` | `DEBUG=true` | `false` | Write full LLM I/O to debug file |

Configuration priority (highest to lowest): CLI flags → `.env` file → environment variables.

---

## Output Artifacts

### verification_report.md
Human-readable markdown report. For each section:
- Verdict badge (✅ Pass, ⚠️ Partial, ❌ Fail, ⏭️ Skipped) with score
- URL visited + page title
- Lists of: Matches, Missing, Mismatches
- Narrative notes from the LLM
- Per-section test case verification results (if test cases provided)

### verification_report.json
Machine-readable structured report. Contains:
- Summary counts and overall score
- Full section results with all fields
- LLM call breakdown per agent
- Enriched test case data

### enriched_test_cases.md / .json
Repaired and enriched version of the input test cases. Adds:
- `direct_link`: direct URL to the relevant page
- `requires_auth`: whether authentication is needed
- `test_data`: concrete values filled in from mock data
- `verdict`: whether the test case is valid, invalid, or should be dropped
- `issues`: list of specific problems found

### audited_test_cases.md / .json
Step-level DOM audit results. For each test case:
- Which steps are valid (element exists in DOM)
- Which steps are invalid (element not found, describes state-dependent steps)
- Precondition issues detected
- Per-step failure reasons

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `litellm` | ≥1.40 | Unified LLM API router |
| `playwright` | ≥1.40 | Browser automation (Chromium) |
| `python-dotenv` | ≥1.0 | `.env` file loading |

Python ≥ 3.10 required. Install with:
```bash
pip install -e .
playwright install chromium
```

---

## Design Decisions and Trade-offs

### Why not Selenium/Puppeteer?
Playwright's synchronous API gives deterministic page state control, robust `wait_for_load_state`, and native multi-tab support needed for handling `target="_blank"` links.

### Why LiteLLM?
Single abstraction layer for OpenAI, Anthropic, Google Gemini, and OpenRouter. Switching models requires changing one environment variable.

### Why a shared selector map?
The DOM is parsed once per InteractionAgent step, then the same indexed map is used by both the LLM (to reason about elements) and the BrowserController (to execute actions). Building separate maps causes index divergence where the LLM references element #42 but the controller's freshly-built map has a different element at index #42.

### Why no URL inference?
Hardcoded URL patterns break across deployments and application variants. The planner generates navigation instructions based on the spec; the agent discovers URLs by actually clicking links — exactly as a human tester would.

### Why two-phase form_gateway?
If the form is submitted before verification, the agent navigates away and the form page is never checked. Phase A verifies; Phase B submits. This prevents entire form sections from being recorded as "skipped."

### Why before/after snapshots for action steps?
Action specs describe **transitions** ("the cart is cleared", "the session ends"). A single DOM snapshot cannot confirm a state change occurred. Before/after diff gives the checker evidence that the action took effect.
