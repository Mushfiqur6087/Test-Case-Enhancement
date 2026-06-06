# Data Models Reference

Complete reference for all dataclasses, enumerations, and structured data types used in the system.

---

## Spec Models (`core/models/spec.py`)

### SpecSection

Represents one verifiable section of the functional description.

```python
@dataclass
class SpecSection:
    name: str       # Section heading, e.g. "Login", "Product Inventory"
    raw_text: str   # Full markdown body beneath the ## heading
```

**Produced by:** `DescriptionParser.parse()` (`parsers/spec_parser.py`)

**Consumed by:**
- `NavigationPlannerAgent.generate_plan()` — to build the traversal plan
- `StateIdentifierAgent.identify()` — to match live pages to spec
- `ComplianceCheckerAgent.check()` — for the spec text to check against
- `Coordinator._format_credentials_for_planner()` — credential formatting

**Example:**
```python
SpecSection(
    name="Login",
    raw_text="The login page contains a Username field, a Password field, and a Login button. "
             "The page also lists accepted test usernames..."
)
```

---

### SectionVerificationResult

The compliance checker's verdict for one spec section.

```python
@dataclass
class SectionVerificationResult:
    section_name: str                              # Matches SpecSection.name
    actual_url: str                                # URL the browser landed on
    actual_title: str                              # Page title seen by browser
    verdict: str                                   # "pass" | "partial" | "fail" | "skipped"
    compliance_score: int                          # 0–100
    matches: List[str] = field(default_factory=list)        # Requirements found in live UI
    missing: List[str] = field(default_factory=list)        # Requirements NOT found
    mismatches: List[str] = field(default_factory=list)     # DOM contradicts spec
    notes: str = ""                                # Narrative summary from LLM
    navigation_success: bool = True                # Was navigation successful?
    navigation_failure_reason: str = ""            # Reason if navigation failed
    test_case_results: List[TestCaseVerificationResult] = ...  # TC audit results
    enriched_test_cases: List[EnrichedTestCase] = ...         # Enriched TCs
```

**Verdict thresholds:**

| Score | Verdict |
|---|---|
| ≥ 75 | `"pass"` |
| 40–74 | `"partial"` |
| < 40 | `"fail"` |
| N/A | `"skipped"` (navigation never succeeded) |

**Produced by:**
- `ComplianceCheckerAgent.check()` (core verdict)
- `Coordinator._skipped_result()` (skipped cases)

**Used in:**
- `VerificationReport.section_results`
- `report_module.build_report()` for summary statistics
- `render_markdown()` for human-readable output

---

### VerificationReport

Full output of a verification run.

```python
@dataclass
class VerificationReport:
    project_url: str                                    # Target application URL
    functional_desc_file: str                           # Path to spec file
    captured_at: str                                    # ISO 8601 timestamp
    sections_checked: int                               # Total sections in spec
    passed: int                                         # Sections with verdict "pass"
    partial: int                                        # Sections with verdict "partial"
    failed: int                                         # Sections with verdict "fail"
    skipped: int                                        # Sections with verdict "skipped"
    overall_score: float                                # Weighted mean (skipped excluded)
    section_results: List[SectionVerificationResult] = ...
    llm_calls_total: int = 0
    verification_stats: Dict[str, Any] = ...            # Per-agent call counts
```

**Overall score formula:**
```python
scored = [r for r in section_results if r.verdict != "skipped"]
overall_score = sum(r.compliance_score for r in scored) / len(scored)
```

**`to_dict()` output (JSON report structure):**
```json
{
  "project_url": "https://www.saucedemo.com/",
  "functional_desc_file": "datasets/swaglabs/SwagLabs.md",
  "captured_at": "2026-06-06T01:05:00",
  "summary": {
    "sections_checked": 10,
    "passed": 9,
    "partial": 0,
    "failed": 1,
    "skipped": 0,
    "overall_score": 87.0
  },
  "section_results": [...],
  "verification_stats": {
    "llm_calls_orchestrator": 3,
    "llm_calls_planner": 8,
    "llm_calls_interaction_agent": 32,
    "llm_calls_state_identifier": 12,
    "llm_calls_compliance_checker": 10,
    "llm_calls_total": 77
  }
}
```

---

## Test Case Models (`core/models/test_case.py`)

### TestCaseStep

One numbered step in a test case procedure.

```python
@dataclass
class TestCaseStep:
    number: int           # Step number (1-indexed)
    description: str      # Natural language step description
```

---

### TestCase

A human-authored test case, parsed from the test cases markdown file.

```python
@dataclass
class TestCase:
    tc_id: str                    # Unique identifier, e.g. "TC-001"
    title: str                    # Test case title
    tc_type: str                  # e.g. "Functional", "Negative", "Edge Case"
    priority: str                 # e.g. "High", "Medium", "Low"
    module_name: str              # Spec section this TC belongs to
    preconditions: str            # Setup requirements before execution
    steps: List[TestCaseStep]     # Numbered procedure steps
    expected_result: str          # What should happen after execution
```

**Example:**
```python
TestCase(
    tc_id="TC-001",
    title="Valid Login with Standard User",
    tc_type="Functional",
    priority="High",
    module_name="Login",
    preconditions="User is unauthenticated.",
    steps=[
        TestCaseStep(1, "Navigate to the login page."),
        TestCaseStep(2, "Enter username 'standard_user' in the Username field."),
        TestCaseStep(3, "Enter password 'secret_sauce' in the Password field."),
        TestCaseStep(4, "Click the Login button."),
        TestCaseStep(5, "Verify redirect to Product Inventory page."),
    ],
    expected_result="User is redirected to Product Inventory page and authenticated."
)
```

---

### TestCaseVerificationResult

The DOM-audit verdict for one test case (from `TestStepVerifierAgent`).

```python
@dataclass
class TestCaseVerificationResult:
    tc_id: str                         # Matches TestCase.tc_id
    verdict: str                       # "valid" | "invalid_steps" | "invalid"
    valid_steps: List[str] = ...       # Steps that are feasible in current DOM
    invalid_steps: List[str] = ...     # Steps where elements not found in DOM
    missing_steps: List[str] = ...     # Steps requiring state not present
    precondition_issues: List[str] = ... # Precondition mismatches detected
    invalid_reason: str = ""           # Summary reason for invalidity
    notes: str = ""                    # Narrative explanation
```

**Verdict semantics:**

| Verdict | Meaning |
|---|---|
| `"valid"` | All steps feasible; elements referenced by steps exist in DOM |
| `"invalid_steps"` | Some steps reference elements not in current DOM or require state not present |
| `"invalid"` | Fundamental failure — preconditions cannot be met at all |

**Example (product in wrong cart state):**
```python
TestCaseVerificationResult(
    tc_id="TC-003",
    verdict="invalid_steps",
    valid_steps=["step 1: Navigate to Product Inventory page"],
    invalid_steps=["step 2: 'Remove' button in product row not found — only 'Add to cart' buttons present"],
    precondition_issues=["Precondition requires InCart state; current page shows NotInCart for all products"],
    notes="Page appears to be in NotInCart state. The test case assumes an item is already in cart."
)
```

---

### EnrichedTestCase

A repaired and enriched version of a `TestCase`, produced by `TestDataEnricherAgent`.

```python
@dataclass
class EnrichedTestCase:
    tc_id: str                    # Matches original TC
    module: str                   # Spec section name
    title: str                    # Test case title (may be clarified)
    type: str                     # Test type
    priority: str                 # Priority level
    direct_link: str              # Full URL to the relevant page
    requires_auth: bool           # Whether user must be authenticated
    preconditions: str            # Enriched/clarified preconditions
    steps: List[str]              # Repaired steps (plain strings, no TestCaseStep)
    expected_result: str          # Expected outcome
    test_data: Dict[str, Any]     # Concrete data values injected from mock data
    verdict: str                  # "verified" | "not_verified" | "partial"
    issues: List[str]             # Specific problems found during enrichment
    dropped: bool                 # True if TC should be removed from suite
    drop_reason: str              # Reason for dropping
    notes: str                    # Enricher's narrative notes
```

**Example (enriched login TC):**
```python
EnrichedTestCase(
    tc_id="TC-001",
    module="Login",
    title="Valid Login with Standard User",
    type="Functional",
    priority="High",
    direct_link="https://www.saucedemo.com/",
    requires_auth=False,
    preconditions="User is unauthenticated. Browser is at https://www.saucedemo.com/.",
    steps=[
        "1. Navigate to https://www.saucedemo.com/ (login page is the landing page)",
        "2. Enter username 'standard_user' in the field with placeholder 'Username' (id='user-name')",
        "3. Enter password 'secret_sauce' in the field with placeholder 'Password' (id='password')",
        "4. Click the 'Login' button (id='login-button')",
        "5. Verify redirect to https://www.saucedemo.com/inventory.html (Product Inventory page)",
    ],
    expected_result="User is authenticated and the Product Inventory page is displayed.",
    test_data={
        "username": "standard_user",
        "password": "secret_sauce",
        "expected_redirect": "https://www.saucedemo.com/inventory.html"
    },
    verdict="verified",
    issues=[],
    dropped=False,
    drop_reason="",
    notes="All steps valid. Concrete credentials and URLs injected from mock data."
)
```

---

## Traversal Plan Models (`agents/navigation_planner.py`)

### TraversalStep

One step in the LLM-generated traversal plan.

```python
@dataclass
class TraversalStep:
    target_section: str       # SpecSection.name to visit
    page_type: str            # form_gateway | listing | detail | overlay | action | summary | confirmation
    how_to_reach: str         # Natural language: how to navigate to this page
    prerequisites: List[str]  # State required before visiting
    interactions_needed: str  # Post-verify side effects; "" if none
    phase: str = "public"     # "public" or "authenticated"
```

**`page_type` determines execution branch in Coordinator:**

| page_type | Execution branch | Navigation expected? |
|---|---|---|
| `form_gateway` | Two-phase: navigate+verify, then submit | Yes |
| `listing` | Unified: navigate → identify → verify | Yes |
| `detail` | Unified: navigate → identify → verify | Yes |
| `overlay` | Unified, verify in-place | No (content appears on current page) |
| `action` | Before/after snapshot | No (in-place action) |
| `summary` | Unified: navigate → identify → verify | Yes |
| `confirmation` | Unified: navigate → identify → verify | Yes |

---

### TraversalPlan

The complete plan for a verification run.

```python
@dataclass
class TraversalPlan:
    reasoning: str                   # LLM's explanation of the traversal strategy
    phases: List[Dict[str, Any]]     # Raw phase data from LLM response
    steps: List[TraversalStep]       # Flattened, ordered list of steps
```

---

## Common Models (`core/models/common.py`)

### RoleCredentials

A set of login credentials for one user role.

```python
@dataclass
class RoleCredentials:
    username: str
    password: str
    role: str       # e.g. "admin", "standard user", "locked out user"
```

**Produced by:** `CredentialParser.parse_credentials()`

**Used by:**
- `Coordinator._format_credentials_for_planner()` — formats for planner prompt
- `Coordinator._build_extra_context()` — injects into auth-intent step prompts
- `Coordinator._ensure_authenticated()` — fallback login goal construction

---

## Action-Related Models (`agents/interaction_agent.py`)

### ActionResult

Result of one `InteractionAgent.execute_goal()` call.

```python
class ActionResult:
    success: bool           # True if goal was achieved
    current_url: str        # URL after execution (success or failure)
    current_title: str      # Page title after execution
    failure_reason: str     # Populated on failure; empty on success
    actions_taken: int      # Total browser actions executed
    steps_used: int         # LLM reasoning steps consumed
```

---

## Model Relationships

```
VerificationReport
 └── section_results: List[SectionVerificationResult]
      ├── section_name → SpecSection.name
      ├── test_case_results: List[TestCaseVerificationResult]
      │    └── tc_id → TestCase.tc_id
      └── enriched_test_cases: List[EnrichedTestCase]
           └── tc_id → TestCase.tc_id

TestCase
 └── steps: List[TestCaseStep]
      └── number, description

TraversalPlan
 └── steps: List[TraversalStep]
      └── target_section → SpecSection.name
```

---

## JSON Serialization

All primary models implement `to_dict()` for JSON serialization. The report writer calls these recursively:

```python
report.to_dict()
  → section_results: [r.to_dict() for r in self.section_results]
      → test_case_results: [r.to_dict() for r in ...]
      → enriched_test_cases: [r.to_dict() for r in ...]
```

This produces the `verification_report.json` artifact. The entire nested structure is serializable without custom JSON encoders.
