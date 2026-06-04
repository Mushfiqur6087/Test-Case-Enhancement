# Intelligent Navigator — Development Progress

> Last updated: 2026-06-05 | Swag Labs fully verified: **10/10 PASS · 94/100**

---

## Project Overview

**Intelligent Navigator** autonomously navigates a live web app, identifies pages, and verifies that each section of a functional spec is correctly implemented. Given a spec (markdown) + URL + credentials, it produces a PASS/PARTIAL/FAIL score for every section.

Test target: **Swag Labs** (`https://www.saucedemo.com/`) — 10 spec sections across login, inventory, cart, checkout, and navigation.

---

## Architecture Evolution

### Before: BFS + Link Discovery (broken)

| Problem | Consequence |
|---|---|
| Only found `<a>` tags | Buttons, forms, icons all missed |
| No plan awareness | Prerequisites (add-to-cart before checkout) never satisfied |
| Hamburger menu invisible | Navigation Menu / Logout / Reset always skipped |
| WorkflowAdvance looped | Same pages re-verified 5+ times, no forward progress |

**Result: 4/10 sections reachable.**

---

### v1 — Spec-Driven Plan-Based Architecture

Replaced BFS with a plan-generated, step-by-step executor:

| Component | Role |
|---|---|
| `TraversalPlannerAgent` | Reads spec → generates ordered plan with typed steps |
| `ActionEngine` | Goal-oriented browser executor (replaces Navigator + LinkDiscovery) |
| `orchestrator.py` | Runs plan: ActionEngine → PageIdentifier → SpecChecker per step |

**Deleted:** `link_discovery.py`, `navigator.py`

---

### v2 — Fixing Overshooting & Loops

Root cause: `interactions_needed` was merged into navigation goals, causing the LLM to keep acting after arrival.

| Fix | What it solved |
|---|---|
| Navigation-only goals (`_build_goal`) | LLM stops on arrival — no overshoot |
| "Already here" check (`_execute_step`) | Broke cart↔checkout navigation loops |
| Two-phase `form_gateway` handler | Form pages verified BEFORE submission (Login, Checkout Info) |
| ActionEngine prompt rules (4 new) | Enforced STOP-on-arrival behaviour |
| Progress logging | Transparent per-step status output |

---

### v3 — Hamburger Menu + Cart Prerequisites

| Fix | Root Cause | Solution |
|---|---|---|
| Hamburger menu invisible | `build_dom_tree` pruned entire subtrees on parent invisibility. The button's parent wrappers had `offsetHeight=0` (confirmed via DevTools). | Remove `is_visible` from subtree pruning; each element checks its own visibility independently. Also enhanced `isElementVisible` with `getBoundingClientRect()` fallback and child-rect check for interactive tags. |
| Cart empty during checkout | `interactions_needed` stripped from nav goals (correct) but side-effect actions (Add to Cart) were never executed. | New `_run_post_verify_interactions()`: runs `interactions_needed` **after** verification, **before** next step. Satisfies prerequisites without overshooting. |
| Escape kills open menus | `_dismiss_overlays()` pressed Escape at start of every ActionEngine step, closing the hamburger menu just opened. | Made `_dismiss_overlays()` a no-op. LLM sends Escape explicitly when needed. |

---

### v3 Polish — 3 Remaining Issues Fixed

After the first 10/10 run (94/100, 69 LLM calls), 3 minor issues found in logs:

| Issue | Root Cause | Fix |
|---|---|---|
| Checkout replan (6 extra LLM calls) | ActionEngine declared `goal_achieved=true` before navigation completed; PageIdentifier saw wrong page → replan triggered | Added URL-change check in `_execute_step`: if URL unchanged after action, retry once |
| Noisy closed-menu sidebar links in DOM | Removing parent-visibility pruning exposed `aria-hidden` containers' children (sidebar links with `tabindex='-1'`) | Added `aria-hidden="true"` subtree pruning in `build_dom_tree` |
| PostVerify fails on Product Inventory | Planner put verification text in `interactions_needed`; ActionEngine can't verify non-interactive elements | Added Rule 6 to planner prompt: `interactions_needed` = state-changing actions only |

---

## Final Results

| Section | BFS | v1 | v2 | v3 |
|---|---|---|---|---|
| Login | ❌ | ⚠️ not verified | ✅ 95 | ✅ 95 |
| Product Inventory | ✅ 90 | ✅ 90 | ✅ 95 | ✅ 95 |
| Product Detail | ❌ | ✅ 90 | ✅ 90 | ✅ 90 |
| Shopping Cart | ⚠️ 60 | ❌ overshoot | ✅ 100 | ✅ 100 |
| Checkout - Information | ❌ | ✅ 100 | ✅ 90 | ✅ 90 |
| Checkout - Overview | ❌ | ❌ loop | ✅ 95 | ✅ 95 |
| Checkout - Confirmation | ❌ | ❌ loop | ✅ 95 | ✅ 95 |
| Navigation Menu | ❌ | ❌ | ✅ 95 | ✅ 95 |
| Reset App State | ❌ | ❌ | ✅ 90 | ✅ 90 |
| Logout | ❌ | ❌ | ✅ 90 | ✅ 90 |
| **Overall** | **4/10** | **~6/10** | **10/10 · 94** | **10/10 · 94** |

---

## Files Changed (cumulative)

| File | Change |
|---|---|
| `spec_verifier/orchestrator.py` | Full rewrite; v2 fixes; v3 post-verify; URL-change retry |
| `agents/prompts.py` | New planner/action prompts; Rule 6 for interactions_needed |
| `agents/traversal_planner.py` | Created — spec → plan generation |
| `agents/action_engine.py` | Created — goal-oriented browser executor |
| `browser/dom_builder.py` | Enhanced visibility check; removed parent pruning; aria-hidden filter |
| `browser/dom_parser.py` | `_flatten` now requires `is_interactive AND is_visible` |
| `spec_verifier/__init__.py` | Updated exports |
| `agents/link_discovery.py` | **Deleted** |
| `agents/navigator.py` | **Deleted** |
