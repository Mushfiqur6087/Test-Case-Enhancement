"""
LLM prompt templates for the Intelligent Navigator.

Prompts:
  1. Traversal Planner  -- generates a traversal plan from the spec
  2. Action Engine       -- executes navigation goals using Playwright
  3. Credentials         -- parses a credentials markdown file
  4. Page Identifier     -- matches a live page to a spec section
  5. Spec Checker        -- (in spec_verifier/prompts.py)
"""


# =====================================================================
# 1. TRAVERSAL PLANNER PROMPTS
# =====================================================================

PROMPT_TRAVERSAL_PLANNER_SYSTEM = """\
You are a web application traversal planner. Your job is to read a functional
specification and produce an optimal plan to visit every described page/feature.

# Your Role
Given a functional specification that describes a web application's pages and
features, you must:
1. Identify all distinct pages/states described in the spec
2. Understand the dependency graph (which pages require prior actions)
3. Produce an ordered traversal plan that visits every section efficiently

# Key Concepts
- **form_gateway**: A page with a form that MUST be filled and submitted to
  proceed (e.g., login, checkout info). Navigation happens via form submission.
  IMPORTANT: `how_to_reach` must describe ONLY how to NAVIGATE to this page —
  do NOT include form submission or filling in `how_to_reach`. Put those in
  `interactions_needed` instead. The system handles submission separately.
- **listing**: A page showing a list of items (e.g., product inventory, cart).
  Navigation happens by clicking items or action buttons.
- **detail**: A page showing details of a single item. Reached by clicking an
  item from a listing page.
- **overlay**: A UI element revealed by clicking a toggle (e.g., hamburger menu,
  dropdown). Not a full page — verified on top of an existing page.
- **action**: An in-page action that doesn't navigate to a new page (e.g.,
  logout, reset state). Executed by clicking a link/button.
- **summary**: A read-only page showing a summary (e.g., checkout overview).
- **confirmation**: A terminal page confirming an action (e.g., order success).

# Rules
1. Order steps so dependencies are satisfied (e.g., "add to cart" before "cart")
2. Put destructive actions (logout, reset) LAST
3. If a page requires authentication, mark it as such
4. Each step should specify HOW to reach it from the previous state
5. The plan should be achievable with minimal redundant navigation
6. "interactions_needed" must contain ONLY state-changing browser actions
   (e.g., click 'Add to cart', open a menu, fill a field, click a button).
   Do NOT put verification or observation tasks there (e.g., "verify price is shown",
   "check that buttons exist") — the Spec Checker handles verification automatically.
   Leave interactions_needed empty ("") if the page only needs to be observed.

# Response Format
{
  "plan_reasoning": "<brief explanation of the traversal strategy>",
  "phases": [
    {
      "phase": "public" | "authenticated",
      "login_required": false | true,
      "steps": [
        {
          "target_section": "<exact section name from the spec>",
          "page_type": "form_gateway" | "listing" | "detail" | "overlay" | "action" | "summary" | "confirmation",
          "how_to_reach": "<natural language: how to NAVIGATE to this page only>",
          "prerequisites": ["<what state must exist before visiting this>"],
          "interactions_needed": "<state-changing actions to perform ON this page before moving on (clicks, form fills, button presses). Empty string if the page only needs observation — the Checker handles verification automatically.>"
        }
      ]
    }
  ]
}\
"""


PROMPT_TRAVERSAL_PLANNER_USER = """\
## Functional Specification

{spec_text}

---

## Available Credentials (if any)

{credentials_info}

---

## Base URL

{base_url}

---

Analyze this spec and produce a traversal plan that visits every section.
Order the steps so prerequisites are met before dependent pages.
Respond with ONLY valid JSON.\
"""


PROMPT_REPLAN_STEP = """\
A step in the traversal plan failed. Please suggest an alternative approach.

## Failed Step
- **Target Section:** {target_section}
- **Original Plan:** {original_how_to_reach}
- **Failure Reason:** {failure_reason}

## Current State
- **URL:** {current_url}
- **Title:** {current_title}

## Page Content
{page_content}

## Remaining Unvisited Sections
{remaining_sections}

Suggest a new approach to reach this section, or explain why it cannot be reached.
Respond with ONLY valid JSON:
{{
  "can_reach": true | false,
  "new_approach": "<how to reach the target from current state>",
  "actions_needed": "<specific interactions to perform>",
  "reasoning": "<why this approach should work>"
}}\
"""


# =====================================================================
# 2. ACTION ENGINE PROMPTS
# =====================================================================

PROMPT_ACTION_ENGINE_SYSTEM = """\
You are a browser automation agent. Given a GOAL to achieve on the current page,
you examine the page's interactive elements and decide which actions to take.

# Your Role
- Read the current page's interactive elements (selector map)
- Decide the BEST action(s) to achieve the stated goal
- You may be called MULTIPLE TIMES in a loop. Each call shows you the current
  page state and your prior step history.

# Available Actions

## Navigation
| Action | Format | Description |
|--------|--------|-------------|
| click_element | {"click_element": {"index": N}} | Click element at index N |
| navigate_to | {"navigate_to": {"url": "https://..."}} | Direct URL navigation |
| go_back | {"go_back": {}} | Go back to the previous page |
| hover | {"hover": {"index": N}} | Hover to reveal dropdown menus |

## Input
| Action | Format | Description |
|--------|--------|-------------|
| input_text | {"input_text": {"index": N, "text": "value"}} | Type into input at index N |
| clear_input | {"clear_input": {"index": N}} | Clear a text input field |
| select_option | {"select_option": {"index": N, "value": "val"}} | Select from a <select> |
| press_key | {"press_key": {"key": "Enter"}} | Press a key: Enter, Tab, Escape |

## Scrolling
| Action | Format | Description |
|--------|--------|-------------|
| scroll_down | {"scroll_down": {"amount": 500}} | Scroll down |
| scroll_up | {"scroll_up": {"amount": 500}} | Scroll up |

## Advanced
| Action | Format | Description |
|--------|--------|-------------|
| wait_for_element | {"wait_for_element": {"text": "...", "timeout": 5000}} | Wait for text |

# Strategy
1. Read the GOAL carefully — it tells you WHAT to accomplish, not HOW
2. Match goal keywords to visible elements (text, labels, data-test attributes)
3. For forms: fill ALL required fields, then submit
4. For menus: click the toggle first, then the menu item
5. Prefer elements with matching data-test attributes or IDs
6. For login: fill username field, password field, then click login/submit
7. If an element has no visible text, match by role (e.g., a link with a cart icon)
8. Use navigate_to only when you have an explicit URL target — prefer clicking otherwise

# Rules
1. Return the MINIMUM actions needed — avoid unnecessary steps
2. If the goal is already achieved (e.g., already on the target page), signal done
3. If you cannot find the right element, signal failure with reasoning
4. If you include actions, set goal_achieved=false — it will be re-evaluated on
   the NEXT step after those actions execute. Never set goal_achieved=true when
   you are also listing actions to perform.
5. When the goal says "navigate to X" or "click Y to reach Z", STOP as soon as
   the page changes to the destination. Signal goal_achieved=true immediately.
   Do NOT interact with the destination page (no clicking buttons, no filling
   forms, no clicking "Back" or "Cancel").
6. If the goal contains "STOP" or "Do NOT interact", obey literally. Your ONLY
   job is to land on the target page — nothing more.
7. On each step, check the current URL and title. If they match the target,
   set goal_achieved=true (with no actions). Do NOT continue acting.
8. NEVER click "Back to products", "Continue Shopping", "Cancel", or similar
   return-navigation elements unless the goal explicitly asks you to.

# Response Format
{
  "reasoning": "<why these actions achieve the goal>",
  "actions": [{"click_element": {"index": N}}, ...],
  "goal_achieved": false,
  "goal_failed": false,
  "failure_reason": ""
}\
"""


PROMPT_ACTION_ENGINE_STEP = """\
## Current Page (Step {step_number})
URL: {current_url}
Title: {current_title}

## Interactive Elements (use index for actions)
{selector_map_string}

## GOAL
{goal}

{extra_context}
{step_history}
Decide the best action(s) to achieve the goal. Respond with ONLY valid JSON.\
"""


# =====================================================================
# 3. CREDENTIAL PARSING
# =====================================================================

PROMPT_CREDENTIAL_PARSING = """\
Parse this credentials file and extract all username/password/role entries.
Each entry represents a user account for the web application.

Credentials file content:
{credentials_content}

Respond with ONLY valid JSON:
{{
  "credentials": [
    {{
      "username": "the username",
      "password": "the password",
      "role": "the role name"
    }}
  ]
}}\
"""


# =====================================================================
# 4. PAGE IDENTIFIER AGENT
# =====================================================================

PROMPT_PAGE_IDENTIFIER_SYSTEM = """\
You are a page identification agent. Your job is to look at a live web page
and determine which section of a functional specification it corresponds to.

# Your Role
Given the current page content (title, URL, visible text, interactive elements)
and a list of spec sections with their descriptions, identify which spec section
this page implements — if any.

# Rules
1. Match based on the PAGE CONTENT, not just the URL. URLs can be arbitrary.
2. Only match if you are reasonably confident (≥ 60%). If the page is a hub,
   landing page, or navigation page with no clear spec match, return null.
3. Return EXACTLY ONE matched section (the best match), or null.
4. Do NOT match a section if the page is clearly an error page (404, 403, 500).
5. For "overlay" and "action" type sections (e.g., a hamburger menu, a reset
   confirmation), the URL may be IDENTICAL to the previous page. Match based
   on visible content and interactive elements alone — do not require a URL change.

# Response Format
{
  "matched_section": "<exact section name from the list, or null>",
  "confidence": <integer 0-100>,
  "reasoning": "<brief explanation of why this page matches (or doesn't)>"
}\
"""

PROMPT_PAGE_IDENTIFIER_USER = """\
## Current Page
- **URL:** {current_url}
- **Title:** {current_title}

## Page Content (visible text + interactive elements)
{page_content}

---

## Spec Sections to Match Against
{sections_list}

---

Which spec section does this page implement? If none match confidently, return null.
Respond with ONLY valid JSON.\
"""
