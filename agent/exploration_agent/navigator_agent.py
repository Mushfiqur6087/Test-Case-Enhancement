"""
Navigator Agent (Strategic).
The brain of the exploration system. Manages the exploration queue,
navigation graph, and decides WHICH page to visit next — but never
touches the browser directly.

Dispatches commands to Page Navigator (to get there) and Page Explorer
(to extract links). Processes their reports and feeds feedback into
the next decision.
"""

import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, PROJECT_ROOT)

from test_case_enhancer.agent.core_utils.llm import LLMClient
from test_case_enhancer.agent.core_utils.logging_utils import DebugLogger
from test_case_enhancer.agent.exploration_agent.completeness_checker import CompletenessChecker
from test_case_enhancer.agent.exploration_agent.frontier import ExplorationQueue
from test_case_enhancer.agent.exploration_agent.login_handler import CredentialParser
from test_case_enhancer.agent.exploration_agent.loop_prevention import LoopPrevention
from test_case_enhancer.agent.exploration_agent.models import (
    ExplorationResult,
    NavigatorCommand,
    NavigatorDecision,
    NodeState,
    PageExplorerResult,
    PageNavigatorResult,
    QueueItem,
    RoleCredentials,
)
from test_case_enhancer.agent.exploration_agent.navigation_graph import NavigationGraph
from test_case_enhancer.agent.exploration_agent.page_explorer import PageExplorer
from test_case_enhancer.agent.exploration_agent.page_identity import PageIdentityComputer
from test_case_enhancer.agent.exploration_agent.page_navigator import PageNavigator
from test_case_enhancer.agent.exploration_agent.prompts import (
    PROMPT_NAVIGATOR_SYSTEM,
    PROMPT_NAVIGATOR_STEP,
)
from test_case_enhancer.agent.tool_agent.credential_reader import CredentialReader
from test_case_enhancer.controller.browser_controller import BrowserController


class NavigatorAgent:
    """
    Strategic exploration agent. Decides what page to visit next,
    dispatches to Page Navigator + Page Explorer, processes results.
    """

    def __init__(self, config: Dict[str, Any]):
        # Config
        self.base_url = config["base_url"]
        self.output_dir = config.get("output_dir", "output")
        self.max_pages = config.get("max_pages", 50)
        self.max_llm_calls = config.get("max_llm_calls", 300)
        self.max_steps = config.get("max_steps", 100)
        self.debug = config.get("debug", False)

        # Input data
        self.functional_desc = config.get("functional_desc", "")
        self.credentials_file = config.get("credentials_file", "")
        self.navigation_file = config.get("navigation_file", "")
        self.expected_pages = self._load_expected_pages()

        # Tracking
        self.llm_call_count = 0
        self.step_count = 0
        self.roles_explored: List[str] = []
        self.current_role = "public"
        self.debug_logger = DebugLogger()
        self.debug_file = None
        if self.debug:
            self.debug_file = self.debug_logger.get_debug_file_path("exploration")

        # --- LLM clients ---
        api_key = config["api_key"]
        model_name = config.get("model_name", "gpt-4o-mini")

        # Navigator's own LLM (strategic decisions, no DOM)
        self.navigator_llm = LLMClient(
            api_key=api_key,
            model_name=model_name,
            system_prompt=PROMPT_NAVIGATOR_SYSTEM,
            debug_file=self.debug_file,
        )

        # A base LLM client for sub-agents (they build their own from this)
        self._base_llm = LLMClient(
            api_key=api_key,
            model_name=model_name,
            system_prompt="",  # Sub-agents override this
            debug_file=self.debug_file,
        )

        # --- Browser ---
        self.browser_controller = BrowserController(llm_client=self._base_llm)
        self.browser_session = self.browser_controller.browser_context

        # --- Sub-agents ---
        self.page_navigator = PageNavigator(
            llm_client=self._base_llm,
            browser_controller=self.browser_controller,
            browser_session=self.browser_session,
            debug=self.debug,
            debug_file=self.debug_file,
        )
        self.page_explorer = PageExplorer(
            llm_client=self._base_llm,
            browser_controller=self.browser_controller,
            browser_session=self.browser_session,
            base_url=self.base_url,
            debug=self.debug,
            debug_file=self.debug_file,
        )

        # --- Exploration state ---
        self.page_identity_computer = PageIdentityComputer(self.base_url)
        self.queue = ExplorationQueue()
        self.graph = NavigationGraph()
        self.loop_prevention = LoopPrevention()
        self.completeness_checker = CompletenessChecker()
        self.credential_parser = CredentialParser(
            self._base_llm, CredentialReader(self._base_llm)
        )
        self.credentials: List[RoleCredentials] = []

        # Feedback state (passed into next Navigator prompt)
        self._last_action_feedback = "This is the start of exploration. No actions taken yet."

    # ================================================================
    # Public API
    # ================================================================

    def run(self) -> ExplorationResult:
        """Main entry point: startup → loop → output."""
        self._log("=" * 60)
        self._log("NAVIGATOR AGENT STARTED (Three-Agent Architecture)")
        self._log(f"Base URL: {self.base_url}")
        self._log(f"Max pages: {self.max_pages} | Max steps: {self.max_steps} | Max LLM calls: {self.max_llm_calls}")
        self._log("=" * 60)

        # Phase 0: Parse credentials
        self._startup()

        # Phase 1: Navigate to base URL and explore landing page
        self.browser_controller.execute_command("navigate_to", self.base_url)
        self._wait_for_page()
        self._explore_current_page(source_url=None)

        # Phase 2: Main exploration loop
        self._exploration_loop()

        # Phase 3: Build and write output
        result = self._build_result()
        self._write_output(result)

        self._log("=" * 60)
        self._log("EXPLORATION COMPLETE")
        graph_stats = self.graph.get_stats()
        self._log(f"Nodes discovered: {graph_stats['total_nodes']}")
        self._log(f"Edges discovered: {graph_stats['total_edges']}")
        self._log(f"Roles explored: {', '.join(self.roles_explored) or 'public'}")
        self._log(f"Total LLM calls: {self._total_llm_calls()}")
        self._log(f"Steps taken: {self.step_count}")
        self._log("=" * 60)

        return result

    # ================================================================
    # Startup
    # ================================================================

    def _startup(self) -> None:
        """Parse credentials from file."""
        self._log("\n--- STARTUP ---")
        if self.credentials_file:
            self._log("Parsing credentials...")
            self.credentials = self.credential_parser.parse_credentials(
                self.credentials_file
            )
            self.llm_call_count += 1
            self.credentials = self.credential_parser.deduplicate_roles(self.credentials)
            self.credentials = self.credential_parser.sort_by_privilege(self.credentials)
            self._log(
                f"  Found {len(self.credentials)} unique roles: "
                + ", ".join(c.role for c in self.credentials)
            )
        else:
            self._log("  No credentials file provided")

    # ================================================================
    # Main Exploration Loop
    # ================================================================

    def _exploration_loop(self) -> None:
        """Core loop: ask Navigator LLM → dispatch to sub-agents → process results."""
        self._log("\n--- EXPLORATION LOOP ---")

        while True:
            # Budget checks
            if self.step_count >= self.max_steps:
                self._log(f"Max steps ({self.max_steps}) reached. Stopping.")
                break
            if self._total_llm_calls() >= self.max_llm_calls:
                self._log(f"LLM budget ({self.max_llm_calls}) exhausted. Stopping.")
                break
            if self.queue.visited_count >= self.max_pages:
                self._log(f"Max pages ({self.max_pages}) reached. Stopping.")
                break

            self.step_count += 1
            self._log(f"\n--- Step {self.step_count} ---")

            # 1. Ask Navigator LLM for next command
            decision = self._ask_navigator()
            if decision is None:
                self._log("  Failed to get decision from Navigator. Retrying...")
                continue

            self._log(f"  Decision: {decision.next_action} | {decision.reasoning[:120]}")

            # 2. Apply queue updates from Navigator
            added = self.queue.add_batch(decision.queue_additions)
            if added:
                self._log(f"  Added {added} URLs to queue")
            self.queue.mark_skipped_batch(decision.queue_removals)

            # 3. Execute the decision
            if decision.next_action == "done":
                self._log("  Navigator decided exploration is complete.")
                break

            elif decision.next_action == "explore_page":
                self._handle_explore_page(decision)

            elif decision.next_action == "login":
                self._handle_login(decision)

            elif decision.next_action == "logout":
                self._handle_logout(decision)

            else:
                self._log(f"  Unknown action: {decision.next_action}")
                self._last_action_feedback = f"Unknown action '{decision.next_action}'. Please use: explore_page, login, logout, or done."

            # 4. Cycle detection
            if self.loop_prevention.detect_cycle():
                self._log("  Cycle detected! Attempting to break out...")
                self._try_navigate_from_queue()

    # ================================================================
    # Decision Handlers
    # ================================================================

    def _handle_explore_page(self, decision: NavigatorDecision) -> None:
        """Handle an explore_page command: navigate there, then explore."""
        source_url = self._get_current_url()

        # Step 1: Page Navigator gets us there
        command = NavigatorCommand(
            command_type="explore_page",
            target_url=decision.target_url,
            target_label=decision.target_label,
            reasoning=decision.reasoning,
        )
        nav_result = self.page_navigator.navigate(command)

        if not nav_result.success:
            self._log(f"  Navigation failed: {nav_result.failure_reason}")
            self._last_action_feedback = (
                f"FAILED to reach {decision.target_url} ({decision.target_label}).\n"
                f"Reason: {nav_result.failure_reason}\n"
                f"Currently on: {nav_result.current_url}\n"
                f"Consider: login first if auth is needed, try a different path, or skip this page."
            )
            # Mark as unreachable in graph if we tried hard
            if nav_result.retry_attempted:
                identity = self.page_identity_computer.compute(
                    decision.target_url, self.current_role
                )
                self.graph.mark_unreachable(identity)
            return

        # Step 2: Page Explorer extracts everything from the page
        self._explore_current_page(source_url=source_url)

    def _handle_login(self, decision: NavigatorDecision) -> None:
        """Handle a login command: find credentials, dispatch to Page Navigator."""
        # Find the right credentials
        creds = self._find_credentials(decision.credential_role)
        if not creds:
            self._last_action_feedback = (
                f"FAILED: No credentials found for role '{decision.credential_role}'. "
                f"Available roles: {', '.join(c.role for c in self.credentials)}"
            )
            return

        command = NavigatorCommand(
            command_type="login",
            target_url=decision.target_url or self._find_login_url(),
            target_label="Login",
            credentials=creds,
        )
        nav_result = self.page_navigator.navigate(command)

        if nav_result.success:
            self.current_role = creds.role
            if creds.role not in self.roles_explored:
                self.roles_explored.append(creds.role)
            self._log(f"  Logged in as: {creds.role}")
            self._last_action_feedback = (
                f"Successfully logged in as '{creds.role}'. "
                f"Now on: {nav_result.current_url} ({nav_result.current_title})"
            )
            # Explore the post-login landing page
            self._explore_current_page(source_url=command.target_url)
        else:
            self._last_action_feedback = (
                f"LOGIN FAILED for role '{creds.role}'. "
                f"Reason: {nav_result.failure_reason}\n"
                f"Currently on: {nav_result.current_url}"
            )

    def _handle_logout(self, decision: NavigatorDecision) -> None:
        """Handle a logout command."""
        command = NavigatorCommand(
            command_type="logout",
            target_url=decision.target_url,
            target_label="Logout",
        )
        nav_result = self.page_navigator.navigate(command)

        if nav_result.success:
            prev_role = self.current_role
            self.current_role = "public"
            self._log(f"  Logged out from {prev_role}")
            self._last_action_feedback = (
                f"Successfully logged out from '{prev_role}'. Now browsing as public.\n"
                f"Currently on: {nav_result.current_url}"
            )
        else:
            self._last_action_feedback = (
                f"LOGOUT FAILED. {nav_result.failure_reason}\n"
                f"Currently on: {nav_result.current_url}"
            )

    # ================================================================
    # Page Exploration (calls Page Explorer)
    # ================================================================

    def _explore_current_page(self, source_url: Optional[str]) -> None:
        """Call Page Explorer on the current page and process its report."""
        explorer_result = self.page_explorer.explore()

        current_url = explorer_result.current_url
        current_title = explorer_result.current_title

        if not current_url:
            self._last_action_feedback = "Page Explorer returned empty result — no page loaded."
            return

        # Record in graph
        identity = self.page_identity_computer.compute(current_url, self.current_role)
        self.graph.add_node(identity, title=current_title, state=NodeState.VISITED)
        self.loop_prevention.mark_visited(current_url)
        self.queue.mark_visited(current_url)

        # Add edge from source
        if source_url and source_url != current_url:
            source_identity = self.page_identity_computer.compute(
                source_url, self.current_role
            )
            self.graph.add_edge(
                source_identity, identity,
                f"Navigated from {source_url}",
                source_url, current_url,
            )

        # Add discovered links to queue
        new_links_added = 0
        for link in explorer_result.links_found:
            item = QueueItem(
                url=link["url"],
                label=link.get("label", ""),
                source_page=current_url,
                reason="Discovered on page",
            )
            if self.queue.add(item):
                new_links_added += 1

        # Add sub-state links to queue
        sub_state_links_added = 0
        for ss in explorer_result.sub_states_found:
            for link in ss.new_links:
                item = QueueItem(
                    url=link["url"],
                    label=link.get("label", ""),
                    source_page=current_url,
                    reason=f"From sub-state: {ss.trigger_description}",
                )
                if self.queue.add(item):
                    sub_state_links_added += 1

        # Build feedback for Navigator
        link_summary = self._format_links_for_feedback(explorer_result.links_found[:15])
        sub_state_summary = ""
        if explorer_result.sub_states_found:
            ss_lines = []
            for ss in explorer_result.sub_states_found:
                ss_lines.append(
                    f"  - {ss.trigger_type}: {ss.trigger_description} "
                    f"({len(ss.new_links)} new links)"
                )
            sub_state_summary = "\nSub-states explored:\n" + "\n".join(ss_lines)

        self._last_action_feedback = (
            f"Successfully explored: {current_title} ({current_url})\n"
            f"Links found: {len(explorer_result.links_found)} "
            f"({new_links_added} new added to queue)\n"
            f"{link_summary}"
            f"{sub_state_summary}"
        )

        self._log(
            f"  Explored {current_title}: {len(explorer_result.links_found)} links, "
            f"{len(explorer_result.sub_states_found)} sub-states, "
            f"{new_links_added + sub_state_links_added} new to queue"
        )

    # ================================================================
    # Navigator LLM
    # ================================================================

    def _ask_navigator(self) -> Optional[NavigatorDecision]:
        """Build prompt, ask Navigator LLM, parse response."""
        prompt = self._build_navigator_prompt()

        try:
            response = self.navigator_llm.ask(prompt)
            self.llm_call_count += 1
        except Exception as e:
            self._log(f"  Navigator LLM error: {e}")
            self.llm_call_count += 1
            return None

        return self._parse_navigator_decision(response)

    def _build_navigator_prompt(self) -> str:
        """Build the per-step prompt for the Navigator LLM."""
        # Queue summary
        queue_summary = self.queue.get_state_summary()

        # Graph summary
        graph_data = self.graph.serialize()
        graph_stats = graph_data.get("stats", {})
        visited_pages = []
        for node in graph_data.get("nodes", []):
            if node.get("state") in ("visited", "fully_explored"):
                title = node.get("title", "Unknown")
                urls = node.get("urls", [])
                url = urls[0] if urls else node.get("identity_key", "")
                visited_pages.append(f"  - {title} ({url})")
        visited_summary = "\n".join(visited_pages) if visited_pages else "  (none yet)"

        # Credentials
        credentials_summary = self.credential_parser.format_credentials_for_prompt(
            self.credentials
        )

        # Auth state
        auth_state = f"Currently browsing as: {self.current_role}"
        if self.current_role != "public":
            auth_state += " (logged in)"
        else:
            auth_state += " (not logged in)"

        # Loop prevention warning
        current_url = self._get_current_url()
        revisit_warning = self.loop_prevention.get_revisit_warning(current_url)
        if revisit_warning:
            auth_state += f"\n{revisit_warning}"

        return PROMPT_NAVIGATOR_STEP.format(
            last_action_feedback=self._last_action_feedback,
            queue_summary=queue_summary,
            graph_node_count=graph_stats.get("total_nodes", 0),
            graph_edge_count=graph_stats.get("total_edges", 0),
            visited_pages_summary=visited_summary,
            expected_pages=self.expected_pages,
            credentials_summary=credentials_summary,
            auth_state=auth_state,
        )

    def _parse_navigator_decision(self, response: str) -> Optional[NavigatorDecision]:
        """Parse the Navigator LLM's JSON response."""
        try:
            data = self._parse_json(response)
        except Exception:
            return None

        try:
            queue_additions = []
            for item in data.get("queue_additions", []):
                queue_additions.append(QueueItem(
                    url=item.get("url", ""),
                    label=item.get("label", ""),
                    source_page=item.get("source_page", ""),
                    reason=item.get("reason", ""),
                ))

            return NavigatorDecision(
                reasoning=data.get("reasoning", ""),
                next_action=data.get("next_action", "done"),
                target_url=data.get("target_url", ""),
                target_label=data.get("target_label", ""),
                credential_role=data.get("credential_role", ""),
                queue_additions=queue_additions,
                queue_removals=data.get("queue_removals", []),
            )
        except Exception:
            return None

    # ================================================================
    # Helpers
    # ================================================================

    def _find_credentials(self, role: str) -> Optional[RoleCredentials]:
        """Find credentials for a given role name."""
        role_lower = role.lower().strip()
        for cred in self.credentials:
            if cred.role.lower().strip() == role_lower:
                return cred
        # Fuzzy match
        for cred in self.credentials:
            if role_lower in cred.role.lower() or cred.role.lower() in role_lower:
                return cred
        return None

    def _find_login_url(self) -> str:
        """Try to find a login URL from the queue or construct one."""
        for url in self.queue.get_unvisited_urls() + self.queue.get_visited_urls():
            if "/login" in url.lower() or "/signin" in url.lower():
                return url
        # Default: append /login to base URL
        return self.base_url.rstrip("/") + "/login"

    def _try_navigate_from_queue(self) -> None:
        """Fallback: navigate to the next unvisited URL from the queue."""
        unvisited = self.queue.get_unvisited_urls()
        for url in unvisited:
            if not self.loop_prevention.is_visited(url):
                self._log(f"  Fallback: navigating to queued URL: {url}")
                self.browser_controller.execute_command("navigate_to", url)
                self._wait_for_page()
                return
        self._log("  No unvisited URLs in queue for fallback.")

    def _format_links_for_feedback(self, links: List[Dict[str, Any]]) -> str:
        """Format a link list for the feedback string shown to Navigator."""
        if not links:
            return ""
        lines = ["Visible links:"]
        for link in links:
            logout_marker = " [LOGOUT]" if link.get("is_logout") else ""
            lines.append(f"  - {link.get('label', '')} → {link['url']}{logout_marker}")
        return "\n".join(lines)

    def _total_llm_calls(self) -> int:
        """Total LLM calls across all agents."""
        return (
            self.llm_call_count
            + self.page_navigator.llm_call_count
            + self.page_explorer.llm_call_count
        )

    def _wait_for_page(self) -> None:
        """Wait for page to stabilize."""
        try:
            page = self.browser_session.get_current_page()
            if page:
                page.wait_for_timeout(1000)
                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass
        except Exception:
            pass

    def _get_current_url(self) -> str:
        try:
            page = self.browser_session.get_current_page()
            return page.url if page else self.base_url
        except Exception:
            return self.base_url

    def _load_expected_pages(self) -> str:
        """Build expected pages list from Navigation.md and/or functional spec."""
        if self.navigation_file and os.path.exists(self.navigation_file):
            try:
                with open(self.navigation_file, 'r') as f:
                    nav_content = f.read()
                return f"Navigation structure:\n{nav_content.strip()}"
            except Exception:
                pass

        if self.functional_desc:
            headings = re.findall(r'^## (\w+)', self.functional_desc, re.MULTILINE)
            if headings:
                pages = [f"  - {h.replace('_', ' ').title()}" for h in headings]
                return "Expected pages:\n" + "\n".join(pages)

        return "(no navigation spec provided)"

    # ================================================================
    # Output
    # ================================================================

    def _build_result(self) -> ExplorationResult:
        """Build the final exploration result."""
        graph_data = self.graph.serialize()
        coverage = self.completeness_checker.get_coverage_summary(self.graph)

        return ExplorationResult(
            project_url=self.base_url,
            captured_at=datetime.now().isoformat(),
            roles_explored=self.roles_explored if self.roles_explored else ["public"],
            navigation_graph=graph_data,
            exploration_stats={
                "llm_calls_navigator": self.llm_call_count,
                "llm_calls_page_navigator": self.page_navigator.llm_call_count,
                "llm_calls_page_explorer": self.page_explorer.llm_call_count,
                "llm_calls_total": self._total_llm_calls(),
                "steps_taken": self.step_count,
                "queue_stats": self.queue.get_stats(),
                "loop_prevention": self.loop_prevention.get_stats(),
                "graph_stats": graph_data.get("stats", {}),
                "coverage": coverage,
            },
        )

    def _write_output(self, result: ExplorationResult) -> str:
        """Write ExplorationResult to JSON file."""
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, "navigation_graph.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

        self._log(f"Output written to: {output_path}")
        return output_path

    # ================================================================
    # Utilities
    # ================================================================

    def _parse_json(self, response: str) -> Dict:
        """Parse JSON from LLM response, handling markdown code blocks."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())

    def _log(self, message: str) -> None:
        print(message)
        if self.debug and self.debug_file:
            try:
                with open(self.debug_file, "a", encoding="utf-8") as f:
                    f.write(f"{message}\n")
            except Exception:
                pass
