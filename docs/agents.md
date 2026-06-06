# Agent Reference

Detailed specification of every LLM agent in the system — inputs, outputs, prompts, behaviors, and design rationale.

---

## 1. NavigationPlannerAgent

**File:** `agents/navigation_planner.py`  
**Class:** `NavigationPlannerAgent`

### Purpose

Reads the **entire functional specification** at once and generates a dependency-ordered traversal plan — a sequence of `TraversalStep` objects that covers every spec section, with prerequisites satisfied and destructive actions scheduled last.

### When It Runs

- **Once at startup** (`generate_plan()`) — produces the initial full plan
- **After each failed step** (`replan_step()`) — suggests an alternative navigation route
- **After each successful step** (`advise_next_step()`) — lightweight validation of the next step

### Inputs

| Input | Type | Description |
|---|---|---|
| `all_sections` | `List[SpecSection]` | All parsed spec sections |
| `base_url` | `str` | Application base URL |
| `credentials_info` | `str` | Formatted credential summary |
| `global_context` | `str` | Skipped sections (e.g., Navigation) formatted as background context |

### Outputs

| Output | Type | Description |
|---|---|---|
| `TraversalPlan` | dataclass | Contains `reasoning`, `phases`, `steps: List[TraversalStep]` |

### TraversalStep Fields

| Field | Type | Description |
|---|---|---|
| `target_section` | `str` | Exact `SpecSection.name` to visit |
| `page_type` | `str` | One of 7 types (see below) |
| `how_to_reach` | `str` | Natural language: navigate FROM previous step's state |
| `prerequisites` | `List[str]` | State that must exist before this step |
| `interactions_needed` | `str` | Post-verification side effects (set up next step's data) |
| `phase` | `str` | `"public"` or `"authenticated"` |

### Page Type Taxonomy

| Type | Description | Example |
|---|---|---|
| `form_gateway` | Form page requiring fill + submit to proceed | Login, Registration, Checkout Info |
| `listing` | Collection/grid of records | Product Inventory, Order History |
| `detail` | Single-record view reached from a listing | Product Detail, Account Details |
| `overlay` | UI element revealed by toggle, no URL change | Hamburger menu, Modal dialog |
| `action` | In-place state-changing action | Logout, Reset Cart, Delete Record |
| `summary` | Read-only review page | Checkout Overview |
| `confirmation` | Terminal success/completion page | Order Confirmation, Success Message |

### Planner Rules (Encoded in System Prompt)

1. Order steps so dependencies are satisfied (create data before viewing it)
2. **Destructive actions last** — logout, reset, delete must come after all page verifications
3. `how_to_reach` must describe visual interactions only — never invent URLs
4. `interactions_needed` should be empty unless a minimal navigation action is needed for a later step
5. Mark pages requiring authentication with `phase: "authenticated"`

### LLM Configuration

- **System prompt**: `PROMPT_TRAVERSAL_PLANNER_SYSTEM` (full page type taxonomy + rules)
- **User prompt**: `PROMPT_TRAVERSAL_PLANNER_USER` (spec text + credentials + base URL)
- **Replan LLM**: Separate `LLMClient` with lightweight system prompt for `replan_step()` and `advise_next_step()`

### Fallback Behavior

If the LLM fails or returns invalid JSON, `_fallback_plan()` generates a sequential plan visiting all sections in spec order as `listing` type with `phase="authenticated"`.

---

### Adaptive Methods

#### `replan_step(failed_step, failure_reason, current_state...)`

Called when `InteractionAgent` fails to reach a target page. Returns:
```json
{
  "can_reach": true,
  "new_approach": "Click the Cart icon in the header to navigate to the cart page.",
  "actions_needed": "",
  "reasoning": "The cart icon is always visible in the header; direct URL guessing failed."
}
```

#### `advise_next_step(completed_section, completed_score, next_step, current_state...)`

Lightweight inter-step check after every successful step. Returns:
```json
{
  "next_step_valid": true,
  "adjusted_how_to_reach": "",
  "prerequisite_actions": "Add an item to the cart first so Reset App State has something to clear.",
  "reasoning": "The cart appears empty — Reset App State needs observable state to produce a visible diff."
}
```

---

## 2. InteractionAgent

**File:** `agents/interaction_agent.py`  
**Class:** `InteractionAgent`

### Purpose

A **goal-oriented browser action engine** that accepts a natural-language goal and executes the minimum browser actions to achieve it — or gives up cleanly if it cannot.

### Architecture

```
execute_goal(goal, extra_context, max_steps)
  │
  └─ Loop (up to max_steps):
       1. DOMHelper.scroll_and_capture()        ← get current indexed DOM
       2. SelectorFilter.filter()               ← remove noise
       3. Capture screenshot (vision models)
       4. _ask_llm(dom, goal, history, tabs)    ← decide what to do
       5. _execute_actions(actions)             ← click/fill/navigate
       6. Wait for page to stabilize
       7. Check goal_achieved / goal_failed / stagnation
```

### Inputs

| Input | Type | Description |
|---|---|---|
| `goal` | `str` | Natural language instruction |
| `extra_context` | `str` | Optional additional context (credentials, prerequisites) |
| `max_steps` | `int` | Step budget (default: 4, tight: 3 for actions/remediation) |

### Output: ActionResult

```python
class ActionResult:
    success: bool
    current_url: str        # URL after goal execution
    current_title: str      # Page title after goal execution
    failure_reason: str     # Populated on failure
    actions_taken: int      # Total actions executed
    steps_used: int         # LLM steps consumed
```

### Action Set

The LLM can emit any combination of these actions in each step:

| Action | Parameters | Description |
|---|---|---|
| `click_element` | `{index: N}` | Click element at index N in selector map |
| `input_text` | `{index: N, text: "..."}` | Fill text into input at index N |
| `navigate_to` | `{url: "..."}` | Direct URL navigation |
| `go_back` | `{}` | Browser back button |
| `hover` | `{index: N}` | Hover to reveal dropdown/tooltip |
| `select_option` | `{index: N, value: "..."}` | Select dropdown option |
| `press_key` | `{key: "Enter"}` | Keyboard press (whitelisted keys only) |
| `clear_input` | `{index: N}` | Clear a text field |
| `wait_for_element` | `{text: "...", timeout: 5000}` | Wait for element to appear |
| `close_tab` | `{page_id: N}` | Close a browser tab |
| `switch_to_tab` | `{page_id: N}` | Switch active tab |

### LLM Response Format

```json
{
  "actions": [
    {"click_element": {"index": 4}},
    {"input_text": {"index": 1, "text": "standard_user"}}
  ],
  "goal_achieved": false,
  "goal_failed": false,
  "reasoning": "Opening the hamburger menu to find the Logout link."
}
```

### Key Behaviors

**Rule 3 Fix** (LLM compliance issue): The LLM sometimes returns `goal_achieved=true` alongside pending `actions`. If this happens, actions are executed first, then `ActionResult(success=True)` is returned with updated URL/title. This was the fix for logout actions that were "achieved" before the click was fired.

**Stagnation detection**: If the URL and DOM are both identical for 2 consecutive steps, `ActionResult(success=False, failure_reason="Page state unchanged")` is returned without consuming more steps.

**Multi-tab support**: When multiple browser tabs are open, the tab context string is injected into every LLM prompt. The LLM can decide to `close_tab` or `switch_to_tab` as needed.

**Overlay-dismiss fallback**: If a click fails (e.g., blocked by a Radix UI popover), the controller:
1. Presses `Escape` to dismiss
2. Retries with `force=True`

### Step Budget Context

| Caller | `max_steps` | Rationale |
|---|---|---|
| Normal navigation | 4 (default) | Multi-step flows (menu → link → page) |
| Action steps (Logout, Reset) | 3 | Simple 1–2 click actions; tight to prevent loops |
| Remediation | 3 | Reveal hidden content; single trigger expected |
| Prerequisite setup | 3 | Minimal state establishment |
| Fallback authentication | 4–6 | Login can be multi-step |

---

## 3. StateIdentifierAgent

**File:** `agents/state_identifier.py`  
**Class:** `StateIdentifierAgent`

### Purpose

After navigation, determines **which spec section the current live page implements**. Enables opportunistic verification (finding a section the plan didn't expect here) and the "already-here" optimization (skipping navigation when already on the target).

### Inputs

| Input | Type | Description |
|---|---|---|
| `current_url` | `str` | Live page URL |
| `current_title` | `str` | Live page title |
| `page_content` | `str` | Combined body text + DOM selector map |
| `all_sections` | `List[SpecSection]` | Sections to match against (only unvisited) |

### Output

```python
(section_name: Optional[str], confidence: int)
# section_name = None if confidence < 60
```

### Confidence Threshold

- **≥60%**: Valid match — proceed with this section
- **<60%**: No match — handled differently per page type:
  - `overlay`/`action` types: verify in-place (no URL change expected)
  - All others: log "no match" and return `None` (step may be replanned)

### LLM Prompt Design

Each section is formatted as: `- **Section Name**: first 400 chars of spec text...`

This compact representation keeps the prompt small even with 10+ sections, while giving the LLM enough semantic signal to match URLs and page titles against spec descriptions.

### Validation

The returned `matched_section` name is validated against the known section name set. Unknown names are discarded (LLM hallucination guard).

---

## 4. ComplianceCheckerAgent

**File:** `agents/compliance_checker.py`  
**Class:** `ComplianceCheckerAgent`

### Purpose

The **scoring engine**. Compares a live page (DOM content or before/after state) against a spec section and produces a structured verdict with detailed evidence.

### Inputs

| Input | Type | Description |
|---|---|---|
| `section` | `SpecSection` | The spec section being verified |
| `page_title` | `str` | Current page title |
| `page_url` | `str` | Current page URL |
| `selector_map_string` | `str` | DOM content (or before+after for actions, max 16,000 chars) |
| `screenshot_b64` | `Optional[str]` | Base64 PNG of AFTER state (vision models) |
| `before_screenshot_b64` | `Optional[str]` | Base64 PNG of BEFORE state (vision, action steps) |

### Output: SectionVerificationResult

```python
SectionVerificationResult(
    section_name="Login",
    actual_url="https://www.saucedemo.com/",
    actual_title="Swag Labs",
    verdict="pass",           # "pass" | "partial" | "fail" | "skipped"
    compliance_score=95,      # 0–100
    matches=[                 # Spec requirements found in live UI
        "Username input with placeholder present",
        "Password input with placeholder present",
        "Login button labeled 'Login' present",
    ],
    missing=[],               # Spec requirements NOT found
    mismatches=[],            # DOM items contradicting the spec
    notes="Core login elements verified..."
)
```

### Scoring Thresholds

| Score Range | Verdict | Meaning |
|---|---|---|
| 75–100 | `pass` | Page correctly implements the spec |
| 40–74 | `partial` | Key elements missing or ambiguous |
| 0–39 | `fail` | Page significantly deviates from spec |

> The checker's own threshold is overridden by the coordinator's lenient thresholds (75/40) so pages are not downgraded by an overly strict LLM assessment.

### Vision Mode

When a vision-capable model is configured:
- **Standard verification**: `page.screenshot()` is attached as context
- **Action steps**: Both `before_screenshot_b64` and `after_screenshot_b64` are attached, labeled `[IMAGE 1 = BEFORE]` and `[IMAGE 2 = AFTER]`

### Action Step Verification

For `action`-type steps, the `selector_map_string` argument contains a combined before/after context:

```
=== STATE BEFORE ACTION ===
URL: https://www.saucedemo.com/inventory.html
Title: Swag Labs
[full DOM of inventory page]

=== ACTION PERFORMED ===
The action 'Logout' was executed.

=== STATE AFTER ACTION (current page) ===
URL: https://www.saucedemo.com/
Title: Swag Labs
[full DOM of login page]
```

The checker is asked to reason about the **transition**, not just the final state.

---

## 5. TestStepVerifierAgent

**File:** `agents/test_step_verifier.py`  
**Class:** `TestStepVerifierAgent`

### Purpose

Given a set of human-authored test cases for a module and the live page DOM, determines whether each test case's steps are **feasible** given the current page state.

### Inputs

| Input | Type | Description |
|---|---|---|
| `module_name` | `str` | Spec section name |
| `page_url` | `str` | Current page URL |
| `page_title` | `str` | Current page title |
| `dom_context` | `str` | Full DOM selector map as text |
| `test_cases` | `List[TestCase]` | Test cases to audit |
| `screenshot_b64` | `Optional[str]` | Screenshot for vision models |

### Output: List[TestCaseVerificationResult]

```python
TestCaseVerificationResult(
    tc_id="TC-003",
    verdict="invalid_steps",           # "valid" | "invalid_steps" | "invalid"
    valid_steps=["step 1: Navigate to login page"],
    invalid_steps=["step 2: 'Remove' button not found in DOM"],
    missing_steps=[],
    precondition_issues=["Precondition requires InCart state, but no Remove buttons visible"],
    invalid_reason="Remove button not found in current DOM snapshot",
    notes="Page appears to be in NotInCart state for all products."
)
```

### Verdict Levels

| Verdict | Meaning |
|---|---|
| `valid` | All steps feasible, preconditions met |
| `invalid_steps` | Some steps refer to elements not in DOM, or preconditions not met |
| `invalid` | Test case fundamentally cannot be executed in this state |

### Design Note

TestStepVerifier operates on **DOM snapshots** — it cannot execute steps. It checks whether elements described by the steps **exist in the current DOM**. Dynamic behaviors (form validation errors, page redirects) are flagged as state-dependent and noted, not penalized.

---

## 6. TestDataEnricherAgent

**File:** `agents/test_data_enricher.py`  
**Class:** `TestDataEnricherAgent`

### Purpose

Repairs and enriches human-authored test cases by:
- Filling in real test data values from the mock data file
- Adding direct page URLs
- Flagging authentication requirements
- Repairing broken steps based on verification results
- Marking cases that should be dropped (impossible to execute)

### Inputs

| Input | Type | Description |
|---|---|---|
| `module_name` | `str` | Spec section name |
| `base_url` | `str` | Application base URL |
| `mock_data` | `str` | Raw mock data markdown text |
| `test_cases` | `List[TestCase]` | Original test cases |
| `verification_results` | `List[TestCaseVerificationResult]` | Step audit results from TestStepVerifierAgent |

### Output: List[EnrichedTestCase]

```python
EnrichedTestCase(
    tc_id="TC-001",
    module="Login",
    title="Valid Login with Standard User",
    type="Functional",
    priority="High",
    direct_link="https://www.saucedemo.com/",
    requires_auth=False,
    preconditions="User is unauthenticated",
    steps=[
        "1. Navigate to https://www.saucedemo.com/",
        "2. Enter username 'standard_user' in the Username field",
        "3. Enter password 'secret_sauce' in the Password field",
        "4. Click the 'Login' button",
        "5. Verify redirect to https://www.saucedemo.com/inventory.html"
    ],
    expected_result="User is authenticated and redirected to Product Inventory",
    test_data={
        "username": "standard_user",
        "password": "secret_sauce"
    },
    verdict="verified",
    issues=[],
    dropped=False,
    drop_reason="",
    notes="All steps valid against current DOM."
)
```

### Enrichment Actions

| Action | Trigger | Result |
|---|---|---|
| Data injection | Step references a credential or value | Fills in real value from `mock_data` |
| URL injection | Step says "navigate to X page" | Replaces vague description with actual URL |
| Step repair | `invalid_steps` in verification result | Rewrites step with correct element reference |
| Case dropping | Fundamentally broken preconditions | `dropped=True`, `drop_reason="..."` |
| Auth flagging | Step requires protected route | `requires_auth=True` |

---

## Agent Initialization Pattern

All agents follow the same initialization pattern:

```python
class SomeAgent:
    def __init__(self, llm_client: LLMClient, debug: bool, debug_file: str):
        self._llm = LLMClient(
            api_key=llm_client.api_key,
            model_name=llm_client.model_name,
            system_prompt=PROMPT_SOME_AGENT_SYSTEM,    # Role-specific
            debug_file=debug_file,
        )
        self.llm_call_count = 0   # Per-agent call tracking
        self.debug = debug
        self.debug_file = debug_file
```

This ensures:
- Each agent has its own behavioral role (different system prompts)
- LLM calls are counted per agent (visible in `verification_stats`)
- Debug output includes agent-labeled entries
- All agents share the same API key and model but operate independently

---

## LLM Response Parsing

All agents use `parse_llm_json()` from `core/utils.py`:

```python
def parse_llm_json(response: str) -> Dict:
    """Parse JSON from LLM response, handling markdown code fences."""
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        cleaned = response.strip()
        # Strip ```json ... ``` or ``` ... ``` blocks
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())
```

LLMs are instructed to "respond with ONLY valid JSON" in every prompt. The parser handles the common case where the model wraps JSON in markdown code fences anyway.

---

## LLM Call Count Summary (Per-Agent)

Each agent's `llm_call_count` is tracked independently and aggregated in the final `VerificationReport.verification_stats`:

```json
{
  "llm_calls_orchestrator": 3,
  "llm_calls_planner": 8,
  "llm_calls_interaction_agent": 32,
  "llm_calls_state_identifier": 12,
  "llm_calls_compliance_checker": 10,
  "llm_calls_total": 77
}
```

This breakdown allows researchers to understand LLM usage patterns and cost distribution across the pipeline.
