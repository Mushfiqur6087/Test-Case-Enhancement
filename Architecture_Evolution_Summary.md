# Architecture Evolution Summary

This document summarizes the architectural improvements made to the **Intelligent Navigator** during this session. We identified fundamental gaps in how the traversal and action engines operated and implemented a 4-phase solution to make the system robust, adaptive, and domain-agnostic.

## 1. The Problems Identified

After analyzing execution logs across multiple runs, particularly focusing on failures around actions like "Logout" and "Reset App State", we identified four core architectural gaps:

1. **Self-Defeating Action Loop:** The `ActionEngine` operated in a multi-step loop (up to 4 steps). For simple 1-click actions (like clicking "Logout"), it would successfully click the button on Step 1, navigate to the login page, but then Step 2 would evaluate the new page, conclude "this is the wrong page," and navigate *back*, effectively undoing the successful action.
2. **Visual Blindness:** The `ActionEngine` only received the textual DOM structure (the selector map). It could not *see* if a side menu was open, if a button changed from "Add" to "Remove", or if a cart badge disappeared. It was acting blindly, while the `SpecCheckerAgent` was the only one with vision.
3. **Stale Static Planning:** The `TraversalPlannerAgent` generated a plan once at the beginning of execution. However, runtime state frequently diverges from the initial plan (e.g., an earlier checkout step empties the cart, making a subsequent "clear cart" action impossible). The orchestrator lacked a mechanism to adapt to these stale prerequisites proactively.
4. **Hardcoded Domain Bias:** The prompts, orchestrator comments, and docstrings were heavily biased toward e-commerce applications (frequently using terms like "cart", "checkout", "product", "SwagLabs"). This restricted the agent's generalization to other domains like banking (e.g., ParaBank).
5. **Multi-Tab Blindness:** When a click opened an unexpected new tab (e.g., external social-media links using `target="_blank"`), the agent was blind to it. Playwright spawned the new page object, but the agent's `_current_page` pointer remained on the original page, leading to DOM misalignment, actions targeting the wrong page, and eventual traversal loops or failures.

---

## 2. The Solutions Implemented

We addressed these gaps through a phased evolution of the architecture:

### Phase 1: Screenshot-Augmented ActionEngine
We added visual grounding to the `ActionEngine`. If the configured LLM supports vision (e.g., `gpt-4o`, `claude-3-5-sonnet`), the engine now captures a base64 screenshot and sends it alongside the textual DOM map via `ask_with_screenshot`. 
* **Impact:** The LLM can now visually confirm state changes (like a menu opening or a page transition) and confidently declare `goal_achieved=true`.

### Phase 2: Single-Shot Execution
For `action`-type steps (like Logout or Reset), we restricted the `ActionEngine` execution to `max_steps=1`. 
* **Impact:** One click, one observation, done. This completely eliminated the self-defeating loop where Step 2 would reverse Step 1's successful work.

### Phase 3: Adaptive Post-Step Replanning
We introduced a lightweight "Step Advisor" (`PROMPT_STEP_ADVISOR`) to the `TraversalPlannerAgent`. 
* **Impact:** After every completed step, the orchestrator now calls `_adapt_next_step()`. This feeds the current page state and the *next* planned step to the LLM to validate if the next step is still possible. If prerequisites are stale, it adjusts the `how_to_reach` instructions and executes quick prerequisite actions on the fly, without needing a full, expensive re-plan.

### Phase 4: Consolidated Branching
We removed several hard-coded `if page_type == ...` branches in the orchestrator (such as manually skipping URL-unchanged retries for overlays). 
* **Impact:** We shifted the responsibility to the LLM. By injecting the `page_type` context directly into the `_build_goal` prompt, the LLM naturally handles the differences between overlays, form gateways, and standard navigations. The execution loop (`_execute_step`) is now significantly cleaner.

### Phase 5: Multi-Tab Awareness & Recovery
We implemented comprehensive tab-tracking and multi-tab control logic:
* **Detection:** `BrowserSession` registers a context-level `page` listener to dynamically intercept and track all new tabs opened in the context.
* **Context Injected Prompts:** When 2+ tabs are open, `ActionEngine` injects a detailed `## Browser Tabs` status list into the prompt, mapping each tab's index, title, URL, and active status.
* **Exposed Tab Actions:** We added `close_tab` and `switch_to_tab` to the controller and prompt dispatch tables. The LLM can explicitly close rogue/external tabs and switch back to its main working tab.
* **Multi-Tab Screenshots:** For vision-capable models, the session captures screenshots from all open tabs, allowing the model to ground its reasoning on the visual state of all tabs.
* **Impact:** The agent no longer gets trapped or crashes when external links open in a new tab; it recognizes the situation, closes the irrelevant tabs, switches back, and continues traversal smoothly.

### Cleanup: E-Commerce Bias Purge
We performed a comprehensive audit of all prompts, docstrings, and code logic:
* Replaced e-commerce examples ("add to cart", "checkout overview", "SwagLabs") with generic web app terminology ("create data before viewing it", "transaction summary", "listing page").
* Removed SwagLabs-specific rules from the ActionEngine prompt (e.g., "NEVER click 'Back to products'").
* Deleted unused, domain-specific constants (`_ACTION_SECTION_KEYWORDS`).

---

## 3. Conclusion
The Intelligent Navigator is now **domain-agnostic**, **visually aware**, **adaptable**, and **multi-tab capable**. It seamlessly handles complex, stateful workflows and recovers from tab changes across varying application types without relying on hard-coded rules or domain-specific assumptions.
