# Pipeline Walkthrough: End-to-End Verification Flow

This document walks through the complete execution flow of a verification run, step by step, with precise code references and concrete examples from the **Swag Labs** (saucedemo.com) dataset.

---

## Phase 0 — Startup & Configuration

### Entry Point

```
python -m test_case_enhancement \
    --url https://www.saucedemo.com/ \
    --functional-desc datasets/swaglabs/SwagLabs.md \
    --credentials datasets/swaglabs/Mock_Data.md \
    --test-cases datasets/swaglabs/Test_Cases.md \
    --model openai/gpt-4o-mini \
    --output output/swaglabs
```

**File:** `test_case_enhancement/__main__.py`

```python
load_dotenv(override=False)         # .env → environment
config = parse_args()               # CLI → config dict
coordinator = Coordinator(config)   # Initialize all agents + browser
coordinator.run()                   # Main pipeline
```

### Coordinator Initialization

**File:** `orchestrator/coordinator.py`

The `Coordinator.__init__()` instantiates:

| Component | What it creates |
|---|---|
| `DebugLogger` | Timestamped debug log file (if `--debug`) |
| `LLMClient` (base) | Shared LiteLLM client (provider-agnostic) |
| `BrowserController` | Playwright Chromium browser session |
| `DOMHelper` | Full-page DOM capture utility |
| `SelectorFilter` | Rule-based DOM noise remover |
| `NavigationPlannerAgent` | LLM agent for plan generation + replanning |
| `InteractionAgent` | LLM + browser action engine |
| `StateIdentifierAgent` | LLM page matcher |
| `ComplianceCheckerAgent` | LLM spec verifier |
| `TestStepVerifierAgent` | LLM test case auditor |
| `TestDataEnricherAgent` | LLM test case repairer |
| `DescriptionParser` | Markdown → SpecSection splitter |
| `CredentialParser` | LLM-assisted credential extractor |

Each agent creates its **own** `LLMClient` instance with a role-specific `system_prompt`, ensuring behavioral isolation even when all agents share the same model and API key.

---

## Phase 1 — Parsing Inputs

### 1A. Parse Functional Specification

**File:** `parsers/spec_parser.py` → `DescriptionParser.parse()`

The functional description markdown is split on `## ` headings (h2 level only). Each heading becomes a `SpecSection`:

**Input (`SwagLabs.md`):**
```markdown
# Functional Specification

## Navigation
Swag Labs is an e-commerce testing application...

## Login
The login page contains a Username field...

## Product Inventory
After login, the Product Inventory page lists all products...
```

**Output (`SpecSection[]`):**
```python
[
  SpecSection(name="Login", raw_text="The login page contains a Username field..."),
  SpecSection(name="Product Inventory", raw_text="After login, the Product Inventory page..."),
  SpecSection(name="Product Detail", raw_text="The Product Detail page shows..."),
  SpecSection(name="Shopping Cart", raw_text="The Shopping Cart page lists items..."),
  SpecSection(name="Checkout - Information", raw_text="Checkout starts with a form..."),
  SpecSection(name="Checkout - Overview", raw_text="The overview step shows an order summary..."),
  SpecSection(name="Checkout - Confirmation", raw_text="The confirmation page displays..."),
  SpecSection(name="Navigation Menu", raw_text="The hamburger menu opens a side panel..."),
  SpecSection(name="Logout", raw_text="Logout ends the session and returns..."),
  SpecSection(name="Reset App State", raw_text="Reset App State clears the cart..."),
]
```

> The `Navigation` section is **skipped by default** (added to `global_context` for the planner but not scheduled for verification). The planner uses it as background context for navigation decisions.

### 1B. Parse Credentials

**File:** `parsers/mockdata_parser.py` → `CredentialParser.parse_credentials()`

An **LLM call** reads the raw credentials markdown and extracts structured username/password/role data.

**Input (`Mock_Data.md`):**
```markdown
- Username: standard_user
- Password: secret_sauce
- Role: standard user
```

**Output (`RoleCredentials[]`):**
```python
[RoleCredentials(username="standard_user", password="secret_sauce", role="standard user")]
```

Duplicate roles are deduplicated so only one account per role is used.

### 1C. Parse Test Cases (Optional)

**File:** `parsers/testcase_parser.py` → `parse_test_cases()`

Parses the structured markdown test case format into `TestCase` objects, grouped by module name.

**Input format (excerpt from `Test_Cases.md`):**
```markdown
## 1. Login
### TC-001 — Valid Login ✅ Functional | High
| **Preconditions** | User is unauthenticated. |
| **Steps** | 1. Navigate to login page<br>2. Enter valid credentials<br>3. Click Login |
| **Expected Result** | User redirected to Product Inventory page. |
```

**Output:**
```python
{
  "Login": [TestCase(tc_id="TC-001", title="Valid Login", ...)],
  "Product Inventory": [TestCase(...), ...],
  ...
}
```

---

## Phase 2 — Generating the Traversal Plan

**File:** `agents/navigation_planner.py` → `NavigationPlannerAgent.generate_plan()`

### What happens:

1. All `SpecSection` objects are formatted into a single spec text string
2. Credentials and global context (navigation overview) are formatted
3. A single LLM call is made with `PROMPT_TRAVERSAL_PLANNER_USER`
4. The LLM response (JSON) is parsed into a `TraversalPlan`

### The LLM receives:

```
## Functional Specification
### Login
The login page contains a Username field, a Password field...

### Product Inventory
After login, the Product Inventory page lists all products...

[... all sections ...]

## Global Context (Navigation structure)
### Navigation
Swag Labs is an e-commerce testing application. Users start on the sign-in page...

## Credentials
- Role: standard user, Username: standard_user, Password: secret_sauce

## Base URL
https://www.saucedemo.com/
```

### The LLM returns (JSON):

```json
{
  "plan_reasoning": "Start with public phase (Login). After login, verify inventory, product detail, shopping cart, checkout flow. Overlays and destructive actions last.",
  "phases": [
    {
      "phase": "public",
      "login_required": false,
      "steps": [
        {
          "target_section": "Login",
          "page_type": "form_gateway",
          "how_to_reach": "Navigate to the base URL. The login form is the landing page.",
          "prerequisites": [],
          "interactions_needed": "Enter username 'standard_user' and password 'secret_sauce', then click the Login button."
        }
      ]
    },
    {
      "phase": "authenticated",
      "login_required": true,
      "steps": [
        {
          "target_section": "Product Inventory",
          "page_type": "listing",
          "how_to_reach": "After successful login, the browser automatically redirects to the Product Inventory page.",
          "prerequisites": ["Logged in as standard_user"],
          "interactions_needed": "Click on the first product name or image to open its detail view."
        },
        {
          "target_section": "Product Detail",
          "page_type": "detail",
          "how_to_reach": "Click any product name or image link from the Product Inventory page.",
          "prerequisites": ["On Product Inventory page"],
          "interactions_needed": "Click 'Add to cart' to add this product. Click the cart icon to navigate to Shopping Cart."
        },
        ...
        {
          "target_section": "Logout",
          "page_type": "action",
          "how_to_reach": "Open the hamburger menu in the header, then click the 'Logout' link.",
          "prerequisites": ["Logged in", "Navigation Menu verified"],
          "interactions_needed": ""
        },
        {
          "target_section": "Reset App State",
          "page_type": "action",
          "how_to_reach": "Open the hamburger menu, then click 'Reset App State'.",
          "prerequisites": ["Logged in", "Items in cart"],
          "interactions_needed": ""
        }
      ]
    }
  ]
}
```

### Parsed into `TraversalPlan`:

```python
TraversalPlan(
  reasoning="Start with public phase (Login)...",
  steps=[
    TraversalStep(target_section="Login", page_type="form_gateway", phase="public", ...),
    TraversalStep(target_section="Product Inventory", page_type="listing", phase="authenticated", ...),
    TraversalStep(target_section="Product Detail", page_type="detail", phase="authenticated", ...),
    TraversalStep(target_section="Shopping Cart", page_type="listing", phase="authenticated", ...),
    TraversalStep(target_section="Checkout - Information", page_type="form_gateway", phase="authenticated", ...),
    TraversalStep(target_section="Checkout - Overview", page_type="summary", phase="authenticated", ...),
    TraversalStep(target_section="Checkout - Confirmation", page_type="confirmation", phase="authenticated", ...),
    TraversalStep(target_section="Navigation Menu", page_type="overlay", phase="authenticated", ...),
    TraversalStep(target_section="Logout", page_type="action", phase="authenticated", ...),
    TraversalStep(target_section="Reset App State", page_type="action", phase="authenticated", ...),
  ]
)
```

> **Key constraint enforced by the planner system prompt**: destructive actions (`Logout`, `Reset App State`) are always placed **last** — after all page-structure verifications are complete.

---

## Phase 3 — Step Execution Loop

For each `TraversalStep`, the Coordinator calls `_execute_step()`.

### Example: Step 1 — Login (form_gateway)

**Step data:**
```
target_section: "Login"
page_type:      "form_gateway"
how_to_reach:   "Navigate to the base URL. The login form is the landing page."
interactions_needed: "Enter username 'standard_user' and password 'secret_sauce', then click Login."
phase:          "public"
```

**Execution:**

```
Phase A (Navigate + Verify):
  InteractionAgent.execute_goal("Navigate to https://www.saucedemo.com/")
  → BrowserController.execute_command("navigate_to", "https://www.saucedemo.com/")
  → DOMHelper.scroll_and_capture() → selector_map_string:
      [1]<input placeholder='Username' id='user-name' />
      [2]<input placeholder='Password' id='password' type='password' />
      [3]<button id='login-button' inner_text='Login' />
  
  ComplianceCheckerAgent.check(section=Login, dom=selector_map_string)
  → LLM response:
      verdict: "pass", score: 95
      matches: ["Username input present", "Password input present", "Login button present", ...]

Phase B (Submit):
  InteractionAgent.execute_goal(
    "Enter username 'standard_user' and password 'secret_sauce', then click Login."
  )
  → Step 1: LLM sees [1]<input id='user-name'/>, [2]<input id='password'/>, [3]<button>Login</button>
             Actions: [{input_text: {index:1, text:"standard_user"}}, {input_text: {index:2, text:"secret_sauce"}}]
  → Step 2: LLM sees form filled
             Actions: [{click_element: {index:3}}]
  → BrowserController.click_element_by_index(3) → page navigates → inventory.html
  → goal_achieved=True
```

**Result recorded:**
```python
SectionVerificationResult(
  section_name="Login", verdict="pass", compliance_score=95,
  actual_url="https://www.saucedemo.com/", navigation_success=True
)
```

**Auth tracking:** The coordinator detects this was a `form_gateway` with auth-intent keywords → `logged_in = True`.

---

### Example: Step 2 — Product Inventory (listing)

**Already-here check:**
```
StateIdentifierAgent.identify(current_url="https://www.saucedemo.com/inventory.html", ...)
→ matched_section: "Product Inventory", confidence: 95
→ Already on target! Skip navigation.
```

**Verify in-place:**
```
ComplianceCheckerAgent.check(section=Product Inventory, dom=selector_map_string)
→ score: 90, verdict: "pass"
  matches: ["Sort dropdown", "Product names", "Prices", "Add to cart buttons", ...]
  missing: ["Cart badge/count element"]
```

**Post-verify interactions:**
```
step.interactions_needed: "Click on the first product name to open its detail view."
InteractionAgent.execute_goal("Click on the first product name...")
→ Clicks "Sauce Labs Backpack" → navigates to inventory-item.html?id=4
```

**TestCase verification (for Login section, runs here because test_cases["Product Inventory"] exists):**
```
TestStepVerifierAgent.verify_test_cases(module_name="Product Inventory", dom=..., test_cases=[...])
→ TC-001: VALID, TC-002: VALID, TC-003: INVALID_STEPS (Remove button not in DOM)...
```

---

### Example: Step 9 — Logout (action with before/after snapshots)

**Prerequisite check (before snapshot):**
```
LLM prompt: "What observable state must exist for Logout to be verifiable?"
LLM response: {setup_needed: false, reasoning: "User is logged in — session already exists"}
```

**Before-state capture:**
```
before_url   = "https://www.saucedemo.com/inventory.html"
before_title = "Swag Labs"
before_dom   = "...[full selector map]..."
(Vision: before_screenshot_b64 = "iVBORw0KGgo..." )
```

**Execute action (max_steps=3):**
```
InteractionAgent.execute_goal("Open the hamburger menu, then click the Logout link.", max_steps=3)
→ Step 1: Actions: [{click_element: {index:4}}]   ← clicks hamburger ≡
           DOM updates: menu opens, Logout link visible
→ Step 2: Actions: [{click_element: {index:28}}]  ← clicks "Logout"
           URL changes to https://www.saucedemo.com/
           goal_achieved = True
```

**After-state capture:**
```
after_url   = "https://www.saucedemo.com/"
after_title = "Swag Labs"
after_dom   = "...[login page DOM]..."
(Vision: after_screenshot_b64 = "iVBORw0KGgo..." )
```

**Combined context for compliance checker:**
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

**Checker verdict:**
```
score: 90, verdict: "pass"
matches: ["Before URL was /inventory.html", "After URL is root/login URL", "Redirect occurred"]
notes: "Logout produced redirect from protected inventory URL to login page."
```

---

## Phase 4 — Self-Correction Example

### Low-Score Remediation

If the `Navigation Menu` step returns a low score because the hamburger menu is closed:

```
ComplianceCheckerAgent.check(section=Navigation Menu) → score: 30
result.missing: [
  "All Items link", "About link", "Logout link",
  "Reset App State link", "Close (X) button"
]

_try_remediate_and_reverify():
  remediation_goal = """
  The following items were expected but not found:
    - All Items link
    - About link
    - Logout link
    ...
  Take minimum actions to make them visible — e.g., open the hamburger menu.
  """
  InteractionAgent.execute_goal(remediation_goal, max_steps=3)
  → Clicks hamburger ≡ → menu opens

  Re-verify:
  ComplianceCheckerAgent.check(section=Navigation Menu) → score: 100
```

### Replanning Example

If `Checkout - Information` fails to navigate:

```
InteractionAgent.execute_goal("Click Checkout in the Shopping Cart") → ActionResult(success=False)

_replan_and_retry(attempt=1):
  NavigationPlannerAgent.replan_step(
    failed_step=...,
    current_url="https://www.saucedemo.com/cart.html",
    page_content="...[cart DOM, Checkout button visible at index 25]..."
  )
  → {can_reach: true, new_approach: "Click the Checkout button directly (index 25 in current DOM)"}
  
  new_step.how_to_reach = "Click the Checkout button directly"
  _execute_step(new_step) → success
```

---

## Phase 5 — Report Generation

**File:** `reporting/generator.py` → `build_report()` + `write_report()`

```python
report = build_report(
  project_url="https://www.saucedemo.com/",
  section_results=merged,    # 10 SectionVerificationResults
  llm_calls_total=77,        # Sum across all agents
  extra_stats={
    "llm_calls_orchestrator": 3,
    "llm_calls_planner": 8,
    "llm_calls_interaction_agent": 32,
    "llm_calls_state_identifier": 12,
    "llm_calls_compliance_checker": 10,
  }
)

paths = write_report(report, "output/swaglabs")
# → output/swaglabs/verification_report.json
# → output/swaglabs/verification_report.md
# → output/swaglabs/enriched_test_cases.json
# → output/swaglabs/enriched_test_cases.md
# → output/swaglabs/audited_test_cases.json
# → output/swaglabs/audited_test_cases.md
```

**Summary (Swag Labs actual run):**
```
Sections: 10 | Pass: 9 | Partial: 0 | Fail: 1 | Skipped: 0
Overall score: 87/100
LLM calls: 77
```

---

## Complete Execution Timeline

```
t=0.0s  Coordinator.run() begins
t=0.1s  Spec parsed → 10 sections
t=0.3s  Credentials parsed (1 LLM call)
t=1.5s  Traversal plan generated (1 LLM call, NavigationPlannerAgent)
t=2.0s  Browser navigates to https://www.saucedemo.com/

t=2.5s  [Step 1/10] Login (form_gateway)
           InteractionAgent navigates (0 clicks needed — already there)
           ComplianceCheckerAgent verifies form (1 LLM call)
           InteractionAgent fills + submits form (2 LLM calls)
           → logged_in = True

t=10s   [Step 2/10] Product Inventory (listing)
           Already-here detected (1 LLM call) → skip navigation
           ComplianceCheckerAgent verifies (1 LLM call)
           TestStepVerifierAgent audits 6 TCs (1 LLM call)
           TestDataEnricherAgent enriches 6 TCs (1 LLM call)
           Post-interact: click product to open detail

t=20s   [Step 3/10] Product Detail (detail) → ...

...

t=95s   [Step 9/10] Logout (action)
           Prerequisite check → no setup needed (1 LLM call)
           Before-state captured
           InteractionAgent opens menu + clicks Logout (2 LLM calls)
           After-state captured
           ComplianceCheckerAgent verifies transition (1 LLM call)

t=110s  [Step 10/10] Reset App State (action)
           ...

t=120s  Report built and written
         → output/swaglabs/verification_report.md (Score: 87/100)
```

---

## InteractionAgent Step Detail

Each InteractionAgent loop iteration:

```
1. DOMHelper.scroll_and_capture()
   → Scrolls page from top → bottom (up to 15 × 800px steps)
   → FullPageDOMTreeParser.parse() → builds DOMElementNode tree
   → Writes to BrowserSession._parser + _selector_map
   → Returns selector_map_string: "[1]<input ...> [2]<button ...> ..."

2. SelectorFilter.filter(selector_map_json)
   → Removes: aria-hidden=true, <i> tags, calendar cells, redundant spans
   → Preserves original indexes (no re-indexing)

3. Build LLM prompt (PROMPT_INTERACTION_AGENT_STEP):
   - current URL + title
   - filtered selector_map_string (max 12,000 chars)
   - natural language goal
   - step history (past actions + URLs)
   - tab context (if multiple tabs open)
   - screenshot (if vision model)

4. LLM responds with JSON:
   {
     "actions": [{"click_element": {"index": 3}}, {"input_text": {"index":1, "text":"user"}}],
     "goal_achieved": false,
     "goal_failed": false,
     "reasoning": "I need to fill the username field first."
   }

5. Execute actions via BrowserController:
   click_element(3) → page.click(css_id_selector(id) or xpath=..., timeout=5000)
   input_text(1, "user") → page.fill(...)

6. Wait for page to stabilize:
   page.wait_for_load_state("networkidle", timeout=5000)

7. If goal_achieved=True: return ActionResult(success=True)
   If goal_failed=True: return ActionResult(success=False)
   If stagnation detected (same URL + same DOM × 2): return ActionResult(success=False)
   Else: continue to next iteration
```

---

## DOM Selector Map Format

The selector map is the critical data structure that bridges LLM reasoning and browser execution.

**Raw format (sent to LLM):**
```
[1]<input placeholder='Username' id='user-name' name='user-name' />
[2]<input placeholder='Password' id='password' type='password' name='password' />
[3]<button id='login-button' type='submit' inner_text='Login' />
[4]<h4 inner_text='Accepted usernames are:' />
[5]<a href='#' id='react-burger-menu-btn' inner_text='Open Menu' />
```

**What the LLM does with it:**
- Reasons about element semantics (type, role, text)
- Returns `{index: N}` references in its actions
- Never invents selector strings — always uses the given indexes

**What the BrowserController does with it:**
- `click_element(3)` → looks up index 3 in `_selector_map` → gets XPath → calls `page.click(xpath)`
- `input_text(1, "standard_user")` → looks up index 1 → gets id → calls `page.fill("#user-name", "standard_user")`

---

## LLM Call Budget (Swag Labs Example)

| Agent | Calls | Notes |
|---|---|---|
| CredentialParser | 1 | Parse mock data file |
| NavigationPlannerAgent | 1 | Full plan generation |
| NavigationPlannerAgent (advisor) | 9 | One per completed step |
| InteractionAgent | ~32 | 2–4 per step × 10 steps |
| StateIdentifierAgent | ~12 | 1–2 per step |
| ComplianceCheckerAgent | 10 | One per section |
| TestStepVerifierAgent | 5 | One per section with test cases |
| TestDataEnricherAgent | 5 | One per section with test cases |
| PrerequisiteCheck | 2 | Before Logout + Reset steps |
| **Total** | **~77** | |

---

## Error Handling and Graceful Degradation

| Error | Handling |
|---|---|
| LLM API call fails | Logged; agent returns safe default (empty actions, score=0 result) |
| Navigation fails | `_replan_and_retry()` attempts up to 2 alternative routes |
| Section unreachable after replanning | Recorded as `verdict="skipped"` with reason |
| DOM capture fails | Empty selector map returned; verification proceeds with partial data |
| `KeyboardInterrupt` | Coordinator closes browser cleanly |
| Unhandled exception | Browser closed in `finally` block; exception propagates with full traceback |
| `index not in selector_map` | Handled per-action; action skipped, logged, execution continues |
| Browser dialog (alert/confirm) | Auto-accepted; message tracked in `_recent_alerts` |
| New tab opened unexpectedly | Tracked in `_tabs`; tab context injected into next LLM step |
