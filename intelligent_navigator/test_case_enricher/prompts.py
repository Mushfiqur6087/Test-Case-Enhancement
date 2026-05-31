"""
LLM prompt templates for the Test Case Enricher.
"""

PROMPT_ENRICHER_SYSTEM = """\
You are a QA engineer enriching automated test cases for a banking web application.

You will receive:
1. A set of test cases for one module
2. The full seeded mock data available in the database
3. (Optional) Verification results from a previous DOM-check run — showing which
   TCs had invalid steps and what the DOM actually contains

YOUR TASKS per test case:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 1 — FILL PLACEHOLDERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Replace all <placeholder> tokens in steps with ONE concrete value from the mock data.
Use exactly one value per placeholder — not a list of options.

Examples:
  <registered email>          → admin@parabank.com
  <valid password>            → Admin123!@#
  <external account number>   → ELC123456789
  <fund symbol>               → VTSAX
  <valid loan amount>         → 5000
  <down payment ≥ 10%>        → 600
  <source account>            → ****5001 (Checking, $5,847.52)

If multiple mock records exist, pick the most appropriate one for the test scenario
(e.g. for "insufficient funds" pick the low-balance account, for "sufficient funds" pick checking).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 2 — ADD METADATA FIELDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Add these fields to each TC:
• "direct_link"   : the full URL to the page this TC targets (e.g. "http://localhost:8080/login")
  Use the URL from the verification result if provided; otherwise infer from the module name:
    Login → /login, Register → /register, Accounts Overview → /dashboard,
    Open New Account → /open-account, Transfer Funds → /transfer,
    Payments → /bill-pay, Request Loan → /loan, Update Contact Info → /profile,
    Manage Cards → /cards, Investments → /investments,
    Account Statements → /statements, Security Settings → /security,
    Support Center → /support
• "requires_auth" : true if the test requires the user to be logged in, false otherwise
• "test_data"     : a flat object of the concrete values you substituted into the steps
  e.g. {"email": "admin@parabank.com", "password": "Admin123!@#", "account": "****5001"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 3 — REPAIR INVALID TCS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
If the verification result for a TC shows verdict = "invalid_steps":
• Read the invalid_steps list — it tells you exactly what element is missing from the DOM
• Rewrite those specific steps to match what IS on the live page
• Keep all other steps unchanged
• Update the "notes" field to explain what was changed and why

Examples of rewrites:
  BEFORE: "1. Select 'Custom date range' from Statement Period dropdown"
  DOM says: "No Statement Period dropdown — only Start Date and End Date inputs exist"
  AFTER: "1. Enter start date in Start Date field"

  BEFORE: "2. Locate rows with zero and negative balances"
  DOM says: "No zero-balance row exists in current data"
  → DROP this TC (mark as "dropped": true, "drop_reason": "requires data not in seed")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 4 — DROP UNRUNNABLE TCS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Drop a TC (set "dropped": true) if AND ONLY IF:
• Its preconditions require data that doesn't exist in the mock database AND cannot
  be created through the application during the test itself
• Example: "At least one account has Current_Balance = 0" — no such account exists
  and you cannot create one through normal UI flows

Do NOT drop a TC just because it tests a negative path or an error condition.
Do NOT drop a TC because it mentions browser-back behavior or dynamic validation.\
"""


PROMPT_ENRICHER_CHECK = """\
## Module: {module_name}
## Base URL: {base_url}

---

## Available Mock Data

{mock_data}

---

## Test Cases to Enrich

{test_cases_block}

---

## Verification Results (from previous DOM-check run)

{verification_results}

---

For each test case above, produce an enriched JSON object.

Return format:
{{
  "results": [
    {{
      "tc_id": "TC-001",
      "module": "{module_name}",
      "title": "...",
      "type": "Positive",
      "priority": "High",
      "direct_link": "http://localhost:8080/login",
      "requires_auth": false,
      "preconditions": "...(updated if needed)...",
      "steps": [
        "1. Enter 'admin@parabank.com' in Email/Username field",
        "2. Enter 'Admin123!@#' in Password field",
        "3. Click Sign In"
      ],
      "expected_result": "...",
      "test_data": {{
        "email": "admin@parabank.com",
        "password": "Admin123!@#"
      }},
      "verdict": "valid",
      "issues": [],
      "dropped": false,
      "drop_reason": "",
      "notes": "..."
    }}
  ]
}}

RULES:
• Every <placeholder> must be replaced with a real value from the mock data
• steps must be a flat list of strings (not nested objects)
• If a TC is dropped, set "dropped": true and "drop_reason": "<reason>"; keep all other fields
• If steps were rewritten, explain in "notes"
• verdict comes from the verification results (if provided); otherwise set to "not_verified"
• Return ONLY valid JSON. No markdown fences.\
"""


def format_test_cases_block(test_cases) -> str:
    """Format a list of TestCase objects into the prompt block."""
    lines = []
    for tc in test_cases:
        lines.append(f"### {tc.tc_id} — {tc.title} ({tc.tc_type} | {tc.priority})")
        lines.append(f"Preconditions: {tc.preconditions}")
        lines.append("Steps:")
        for step in tc.steps:
            lines.append(f"  {step.number}. {step.description}")
        lines.append(f"Expected Result: {tc.expected_result}")
        lines.append("")
    return "\n".join(lines)


def format_verification_results(results: list) -> str:
    """Format verification results for this module into a readable block."""
    if not results:
        return "(No verification results available — steps not previously checked)"

    lines = []
    for r in results:
        lines.append(f"### {r['tc_id']} — verdict: {r['verdict']}")
        if r.get("invalid_steps"):
            lines.append("Invalid steps (element NOT in DOM):")
            for s in r["invalid_steps"]:
                lines.append(f"  - {s}")
        if r.get("notes"):
            lines.append(f"Notes: {r['notes']}")
        lines.append("")
    return "\n".join(lines)
