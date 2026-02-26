"""
Link Curator Agent.
Receives all links extracted from a page, groups them by URL pattern,
and uses LLM to decide which patterns are worth exploring.
Picks one representative link per group for the exploration queue.
Caches decisions per source page template to avoid redundant LLM calls.
"""

import json
from collections import defaultdict
from typing import Any, Dict, List, Set

from intelligent_navigator.core.llm import LLMClient
from intelligent_navigator.core.utils import log, parse_llm_json
from intelligent_navigator.exploration.page_identity import PageIdentityComputer
from intelligent_navigator.agents.prompts import (
    PROMPT_LINK_CURATOR_SYSTEM,
    PROMPT_LINK_CURATOR_STEP,
)


class LinkCurator:
    """
    Agent that curates which extracted links go into the exploration queue.
    Groups links by normalized URL pattern, uses LLM to select which
    patterns are important, and caches decisions per source page template.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        page_identity_computer: PageIdentityComputer,
        debug: bool = False,
        debug_file: str = None,
    ):
        self.curator_llm = LLMClient(
            api_key=llm_client.client.api_key,
            model_name=llm_client.model_name,
            system_prompt=PROMPT_LINK_CURATOR_SYSTEM,
            debug_file=debug_file,
        )
        self._pic = page_identity_computer
        self.debug = debug
        self.debug_file = debug_file
        self.llm_call_count = 0

        # Cache: {source_normalized_path: {link_pattern: "keep"|"skip"}}
        self._decision_cache: Dict[str, Dict[str, str]] = {}

    def curate(
        self,
        links: List[Dict[str, Any]],
        source_url: str,
        graph_summary: str,
    ) -> Set[str]:
        """
        Main entry point. Returns the set of URLs that should be added
        to the exploration queue. The caller is responsible for recording
        ALL links as graph edges independently.

        Args:
            links: All extracted links (visible + sub-state) as dicts
                   with at least 'url' and optionally 'label'.
            source_url: The URL of the page these links were found on.
            graph_summary: Navigation graph summary string for LLM context.

        Returns:
            Set of URLs to add to the queue.
        """
        if not links:
            return set()

        # 1. Group links by normalized URL pattern
        groups = self._group_by_pattern(links)

        # 2. If no group has more than 1 link, keep all — nothing to deduplicate
        if all(len(g) <= 1 for g in groups.values()):
            log(
                f"  [LinkCurator] All patterns unique ({len(groups)} patterns). "
                f"Keeping all links.",
                self.debug, self.debug_file,
            )
            return {link["url"] for link in links}

        # 3. Compute source page template (cache key)
        source_template, _, _ = self._pic.normalize_path(source_url)

        # 4. Check cache
        if source_template in self._decision_cache:
            cached = self._decision_cache[source_template]
            result = self._apply_decisions(groups, cached)
            log(
                f"  [LinkCurator] Cache hit for {source_template}: "
                f"{len(links)} links -> {len(result)} kept",
                self.debug, self.debug_file,
            )
            return result

        # 5. Cache miss — call LLM with links + graph context
        decisions = self._ask_llm(source_url, groups, graph_summary)
        self._decision_cache[source_template] = decisions

        # 6. Apply decisions
        result = self._apply_decisions(groups, decisions)
        log(
            f"  [LinkCurator] LLM curated {source_template}: "
            f"{len(links)} links -> {len(result)} kept "
            f"({len(groups)} patterns)",
            self.debug, self.debug_file,
        )
        return result

    # ================================================================
    # Internal helpers
    # ================================================================

    def _group_by_pattern(
        self, links: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group links by their normalized URL pattern."""
        groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for link in links:
            url = link.get("url", "")
            if not url:
                continue
            normalized, _, _ = self._pic.normalize_path(url)
            groups[normalized].append(link)
        return dict(groups)

    def _ask_llm(
        self,
        source_url: str,
        groups: Dict[str, List[Dict[str, Any]]],
        graph_summary: str,
    ) -> Dict[str, str]:
        """
        Call LLM with grouped patterns + graph context.
        Returns {pattern: "keep"|"skip"}.
        """
        # Build pattern summary table for the prompt
        pattern_rows = []
        for pattern, group_links in sorted(
            groups.items(), key=lambda x: -len(x[1])
        ):
            pattern_rows.append({
                "pattern": pattern,
                "count": len(group_links),
                "example_urls": [lnk["url"] for lnk in group_links[:3]],
                "example_labels": [
                    lnk.get("label", "") for lnk in group_links[:3]
                ],
            })

        prompt = PROMPT_LINK_CURATOR_STEP.format(
            source_url=source_url,
            pattern_table=json.dumps(pattern_rows, indent=2),
            graph_summary=graph_summary or "(no pages explored yet)",
        )

        try:
            response = self.curator_llm.ask(prompt)
            self.llm_call_count += 1
            data = parse_llm_json(response)
            return self._parse_llm_decisions(data, groups)
        except Exception as e:
            log(
                f"  [LinkCurator] LLM error: {e}. Keeping all links.",
                self.debug, self.debug_file,
            )
            self.llm_call_count += 1
            # Fallback: keep everything
            return {pattern: "keep" for pattern in groups}

    def _parse_llm_decisions(
        self,
        data: Dict[str, Any],
        groups: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, str]:
        """Parse LLM response into {pattern: "keep"|"skip"} dict."""
        decisions: Dict[str, str] = {}

        for item in data.get("decisions", []):
            pattern = item.get("pattern", "")
            action = item.get("action", "keep")

            # Validate action
            if action not in ("keep", "skip"):
                action = "keep"

            if pattern in groups:
                decisions[pattern] = action

        # Default to "keep" for any patterns the LLM didn't mention
        for pattern in groups:
            if pattern not in decisions:
                decisions[pattern] = "keep"

        return decisions

    def _apply_decisions(
        self,
        groups: Dict[str, List[Dict[str, Any]]],
        decisions: Dict[str, str],
    ) -> Set[str]:
        """
        Apply decisions to produce the final set of URLs to keep.
        For "keep" patterns: pick the first link in DOM order.
        For "skip" patterns: exclude all links.
        For unknown patterns (not in cache): keep first link.
        """
        keep_urls: Set[str] = set()

        for pattern, group_links in groups.items():
            action = decisions.get(pattern, "keep")
            if action == "skip":
                continue
            # Keep one representative (first in DOM order)
            keep_urls.add(group_links[0]["url"])

        return keep_urls
