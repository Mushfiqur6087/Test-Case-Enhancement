# Test Case Enhancement — LLM-Powered Spec Compliance Verifier

An autonomous, agentic system that verifies whether a live web application correctly implements its functional specification — and repairs/enriches existing test cases against the real DOM.

---

## What It Does

Given:
- A **functional specification** (Markdown file describing what the app should do)
- A **live web application URL**
- Optionally: **existing test cases** and **mock data/credentials**

The system will:
1. **Parse** the spec into discrete verifiable sections
2. **Generate** a dependency-ordered traversal plan using an LLM
3. **Navigate** the live application autonomously using a Playwright-controlled browser
4. **Verify** each page against its spec section — scoring from 0 to 100
5. **Audit** existing test case steps against the live DOM
6. **Enrich** test cases with real URLs, concrete data, and repaired steps
7. **Write** structured JSON + human-readable Markdown reports

The system works on **any web application** — e-commerce, banking, CMS, social media — without any hardcoded URL patterns or application-specific logic.

---

## Quick Start

### Prerequisites

```bash
pip install -e .
playwright install chromium
```

### Create a `.env` file

```dotenv
OPENAI_API_KEY=sk-...
LLM_MODEL=openai/gpt-4o-mini
TARGET_URL=https://www.saucedemo.com/
OUTPUT_DIR=output/swaglabs
```

### Run

```bash
# Minimal — spec verification only
python -m test_case_enhancement \
    --url https://www.saucedemo.com/ \
    --functional-desc datasets/swaglabs/SwagLabs.md

# Full pipeline — with credentials + test case audit + enrichment
python -m test_case_enhancement \
    --url https://www.saucedemo.com/ \
    --functional-desc datasets/swaglabs/SwagLabs.md \
    --credentials datasets/swaglabs/Mock_Data.md \
    --test-cases datasets/swaglabs/Test_Cases.md \
    --output output/swaglabs

# With debug logging
python -m test_case_enhancement \
    --url https://www.saucedemo.com/ \
    --functional-desc datasets/swaglabs/SwagLabs.md \
    --debug
```

### Output

```
output/swaglabs/
├── verification_report.md         Human-readable results
├── verification_report.json       Machine-readable full report
├── enriched_test_cases.md         Repaired test cases with real data
├── enriched_test_cases.json       Same, as JSON
├── audited_test_cases.md          Step-level DOM audit results
└── audited_test_cases.json        Same, as JSON
```

---

## Configuration

| CLI Flag | Env Variable | Required | Default | Description |
|---|---|---|---|---|
| `--url` | `TARGET_URL` | ✅ | — | Base URL of the web application |
| `--functional-desc` | — | ✅ | — | Path to functional spec markdown |
| `--credentials` | — | — | — | Path to credentials/mock data markdown |
| `--test-cases` | — | — | — | Path to test cases markdown |
| `--output` | `OUTPUT_DIR` | — | `output` | Output directory |
| `--api-key` | `OPENAI_API_KEY` etc. | ✅ | — | LLM API key |
| `--model` | `LLM_MODEL` | — | `openai/gpt-4o-mini` | LiteLLM model string |
| `--debug` | `DEBUG=true` | — | `false` | Write full LLM I/O to debug log |

**Configuration priority:** CLI flags → `.env` file → environment variables

### Supported Model Providers

The system uses [LiteLLM](https://github.com/BerriAI/litellm) for unified model routing:

```bash
# OpenAI
LLM_MODEL=openai/gpt-4o-mini
OPENAI_API_KEY=sk-...

# Anthropic
LLM_MODEL=anthropic/claude-3-5-haiku-20241022
ANTHROPIC_API_KEY=sk-ant-...

# OpenRouter (access to many models)
LLM_MODEL=openrouter/anthropic/claude-3.5-sonnet
OPENROUTER_API_KEY=sk-or-...

# Google Gemini
LLM_MODEL=gemini/gemini-1.5-flash
GOOGLE_API_KEY=...
```

**Vision-capable models** (automatic screenshot-based verification):
`gpt-4o`, `gpt-5`, `gpt-4-turbo`, `claude-3-*`, `gemini-*`

---

## Input File Formats

### Functional Specification (`--functional-desc`)

A Markdown file with `##` headings — one per verifiable section.

```markdown
# Functional Specification

## Navigation
[Background context about the app structure — skipped by default]

## Login
The login page contains a Username field, a Password field, and a Login button.
When the user submits valid credentials, the system redirects to the inventory page.

## Product Inventory
After login, the Product Inventory page lists all products with name, description,
price, and an "Add to cart" button...

## Checkout - Information
Checkout starts with a form collecting First Name, Last Name, and Zip/Postal Code...
```

> Only `##` level headings are parsed as sections. The `Navigation` section is automatically treated as background context (not verified), as it describes site structure rather than a verifiable page.

### Credentials / Mock Data (`--credentials`)

Any Markdown format — the LLM extracts credentials automatically:

```markdown
# Test Credentials

## Standard User
- Username: standard_user
- Password: secret_sauce

## Admin User
- Username: admin_user
- Password: admin_pass
```

### Test Cases (`--test-cases`)

A structured Markdown format:

```markdown
## 1. Login

### TC-001 — Valid Login ✅ Functional | High
| **Preconditions** | User is unauthenticated. |
| **Steps** | 1. Navigate to login page<br>2. Enter valid credentials<br>3. Click Login |
| **Expected Result** | User redirected to Product Inventory page. |

### TC-002 — Invalid Password ❌ Negative | High
| **Preconditions** | User is unauthenticated. |
| **Steps** | 1. Navigate to login page<br>2. Enter valid username and wrong password<br>3. Click Login |
| **Expected Result** | Error banner displayed: "Epic sadface: Username and password do not match..." |
```

---

## Output Format

### verification_report.md (excerpt)

```markdown
# Spec Verification Report

| | |
|---|---|
| **URL** | https://www.saucedemo.com/ |
| **Spec file** | `datasets/swaglabs/SwagLabs.md` |
| **Date** | 2026-06-06 |
| **Overall score** | **87 / 100** |

## Summary
| Verdict | Count |
|---------|-------|
| ✅ Pass    | 9 |
| ⚠️  Partial | 0 |
| ❌ Fail    | 1 |
| ⏭️  Skipped | 0 |
| **Total** | **10** |

LLM calls used: 77

---

### ✅ Login — PASS (95/100)

**Page visited:** `https://www.saucedemo.com/` — *Swag Labs*

**✔ Matches (spec requirements found in live UI):**
- Username input with placeholder present
- Password input with placeholder present
- Login submit button labeled 'Login' present
- Accepted usernames list visible on page

**Test Case Verification:**
- **TC-001** ✅ VALID
- **TC-002** ⚠️ INVALID_STEPS
  - ❌ step 2: Error banner element not found in DOM (requires form submission)

---

### ❌ Reset App State — FAIL (20/100)

**✔ Matches:**
- Cart icon with item-count badge is visible

**✘ Missing:**
- Cleared cart badge (no item count)
- Empty-cart indicator after reset

**⚡ Mismatches:**
- Cart badge still shows '2' but should be cleared
```

---

## Project Structure

```
Test-Case-Enhancement/
│
├── pyproject.toml              Package metadata + dependencies
├── .env.example                Environment variable template
├── .gitignore
│
├── datasets/                   Sample datasets for two demo applications
│   ├── swaglabs/               Sauce Labs demo e-commerce app
│   │   ├── SwagLabs.md         Functional specification
│   │   ├── Test_Cases.md       Test case suite (100+ TCs)
│   │   └── Mock_Data.md        Test credentials
│   └── parabank/               ParaBank demo banking app
│       ├── Parabank.md         Functional specification
│       ├── Test_Cases.md       Test case suite
│       ├── Mock_Data.md        Test credentials
│       └── app/                Local app deployment (if needed)
│
├── output/                     Generated verification reports
│   ├── swaglabs/               SwagLabs run outputs
│   └── parabank/               ParaBank run outputs
│
├── docs/                       Architecture documentation
│   ├── architecture.md         System design, modules, data flow
│   ├── pipeline.md             End-to-end walkthrough with examples
│   ├── agents.md               All 6 LLM agents — inputs, outputs, design
│   └── data_models.md          All dataclasses and structured types
│
└── test_case_enhancement/      Main Python package
    ├── __main__.py             Entry point
    ├── cli.py                  Argument parser
    ├── __init__.py             Public API
    ├── orchestrator/           Coordinator (central loop)
    ├── agents/                 6 specialized LLM agents
    ├── browser/                Playwright browser + DOM pipeline
    ├── llm/                    LiteLLM client + prompt templates
    ├── parsers/                Spec, test case, credential parsers
    ├── core/                   Shared models, utils, logging
    └── reporting/              Report builder + Markdown renderer
```

---

## Datasets Included

### Swag Labs (`datasets/swaglabs/`)
- **App**: [Sauce Labs Demo](https://www.saucedemo.com/) — public e-commerce test application
- **Spec sections**: 10 (Login, Inventory, Product Detail, Cart, Checkout ×3, Navigation Menu, Logout, Reset)
- **Test cases**: 80+ test cases across all modules
- **Result** (actual run): 9/10 Pass, 87/100 overall score

### ParaBank (`datasets/parabank/`)
- **App**: [ParaBank](https://parabank.parasoft.com/) — public banking demo application
- **Spec sections**: 12 (Login, Registration, Accounts, Transactions, Bill Pay, etc.)
- **Test cases**: 80+ test cases across all modules
- **Demonstrates**: Multi-step authenticated workflows, form-heavy applications

---

## Supported Page Types

| Type | Description | Example |
|---|---|---|
| `form_gateway` | Form requiring fill + submit | Login, Registration, Checkout form |
| `listing` | Collection of records/items | Product list, Transaction history |
| `detail` | Single-record detail view | Product detail, Account details |
| `overlay` | Toggle-revealed panel/modal | Hamburger menu, Modal dialog |
| `action` | In-place state change | Logout, Reset cart, Delete record |
| `summary` | Read-only review page | Order summary, Review screen |
| `confirmation` | Terminal success page | Order complete, Registration success |

---

## Architecture Overview

```
CLI / Entry Point
       │
       ▼
  Coordinator (Orchestrator)
  ├── Parse spec → SpecSection[]
  ├── Parse credentials → RoleCredentials[]
  ├── Parse test cases → Dict[module, TestCase[]]
  ├── NavigationPlannerAgent → TraversalPlan
  └── For each TraversalStep:
       ├── InteractionAgent  → navigate / execute actions
       ├── StateIdentifierAgent → confirm which section we're on
       ├── ComplianceCheckerAgent → score vs spec (0-100)
       ├── TestStepVerifierAgent → audit test case steps vs DOM
       ├── TestDataEnricherAgent → enrich + repair test cases
       └── Self-correction: remediation + replanning
            │
            ▼
       VerificationReport → JSON + Markdown + Enriched TCs
```

See [`docs/architecture.md`](docs/architecture.md) for the full system design.

---

## Documentation

| Document | Contents |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | System design, module map, data flow, design decisions |
| [`docs/pipeline.md`](docs/pipeline.md) | Step-by-step execution walkthrough with concrete examples |
| [`docs/agents.md`](docs/agents.md) | All 6 LLM agents — purpose, inputs, outputs, behaviors |
| [`docs/data_models.md`](docs/data_models.md) | All dataclasses, enumerations, JSON structures |

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `litellm` | ≥ 1.40 | Unified LLM API router (OpenAI, Anthropic, Gemini, OpenRouter) |
| `playwright` | ≥ 1.40 | Browser automation (Chromium) |
| `python-dotenv` | ≥ 1.0 | `.env` file loading |

Python ≥ 3.10 required.

---

## License

MIT License — see `pyproject.toml`.
