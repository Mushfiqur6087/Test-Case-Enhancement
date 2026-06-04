"""
Traversal Planner Agent.

Reads the full functional specification and generates an ordered traversal
plan — a sequence of steps that visits every described page/feature with
dependencies satisfied.

The plan is generated once at startup, then refined step-by-step during
execution when a step fails and the agent needs to adapt.

Key design:
  - Single LLM call to analyze the full spec → produce initial plan
  - Per-step replanning when a step fails → adapt using current page state
  - No hardcoded URL patterns, no link extraction, no keyword matching
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from intelligent_navigator.core.llm import LLMClient
from intelligent_navigator.core.models import SpecSection
from intelligent_navigator.core.utils import log, parse_llm_json
from intelligent_navigator.agents.prompts import (
    PROMPT_TRAVERSAL_PLANNER_SYSTEM,
    PROMPT_TRAVERSAL_PLANNER_USER,
    PROMPT_REPLAN_STEP,
)


@dataclass
class TraversalStep:
    """One step in the traversal plan."""
    target_section: str       # exact SpecSection.name
    page_type: str            # form_gateway, listing, detail, overlay, action, summary, confirmation
    how_to_reach: str         # natural language description of how to get here
    prerequisites: List[str]  # what state must exist first
    interactions_needed: str   # what to do ON this page before moving on
    phase: str = "public"     # "public" or "authenticated"


@dataclass
class TraversalPlan:
    """Full traversal plan for a web application."""
    reasoning: str
    phases: List[Dict[str, Any]]  # raw phases from the LLM
    steps: List[TraversalStep] = field(default_factory=list)  # flattened ordered steps


class TraversalPlannerAgent:
    """
    Generates and refines a spec-aware traversal plan.

    Phase 1: Generate initial plan from the full functional description.
    Phase 2: Replan individual steps when they fail during execution.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        debug: bool = False,
        debug_file: Optional[str] = None,
    ):
        self.debug = debug
        self.debug_file = debug_file
        self.llm_call_count = 0

        self._llm = LLMClient(
            api_key=llm_client.api_key,
            model_name=llm_client.model_name,
            system_prompt=PROMPT_TRAVERSAL_PLANNER_SYSTEM,
            debug_file=debug_file,
        )
        # Separate LLM for replanning (uses a lighter system prompt)
        self._replan_llm = LLMClient(
            api_key=llm_client.api_key,
            model_name=llm_client.model_name,
            system_prompt="You are a browser automation replanning agent. Help find alternative ways to navigate a web application.",
            debug_file=debug_file,
        )

    def generate_plan(
        self,
        all_sections: List[SpecSection],
        base_url: str,
        credentials_info: str = "No credentials available.",
    ) -> TraversalPlan:
        """
        Generate the initial traversal plan from the full functional spec.

        Parameters
        ----------
        all_sections     : all parsed SpecSection objects
        base_url         : the application's base URL
        credentials_info : formatted string of available credentials

        Returns
        -------
        TraversalPlan with ordered steps.
        """
        # Build the full spec text
        spec_text = self._format_spec(all_sections)

        prompt = PROMPT_TRAVERSAL_PLANNER_USER.format(
            spec_text=spec_text,
            credentials_info=credentials_info,
            base_url=base_url,
        )

        try:
            response = self._llm.ask(prompt)
            self.llm_call_count += 1
            data = parse_llm_json(response)
        except Exception as e:
            log(f"  [Planner] LLM error: {e}", self.debug, self.debug_file)
            self.llm_call_count += 1
            return self._fallback_plan(all_sections)

        return self._parse_plan(data, all_sections)

    def replan_step(
        self,
        failed_step: TraversalStep,
        failure_reason: str,
        current_url: str,
        current_title: str,
        page_content: str,
        remaining_sections: List[SpecSection],
    ) -> Optional[Dict[str, Any]]:
        """
        Ask the LLM to suggest an alternative approach for a failed step.

        Returns a dict with {can_reach, new_approach, actions_needed, reasoning}
        or None if the LLM call fails.
        """
        remaining_text = "\n".join(
            f"- **{s.name}**: {s.raw_text[:200]}"
            for s in remaining_sections
        )

        prompt = PROMPT_REPLAN_STEP.format(
            target_section=failed_step.target_section,
            original_how_to_reach=failed_step.how_to_reach,
            failure_reason=failure_reason,
            current_url=current_url,
            current_title=current_title,
            page_content=page_content[:6000],
            remaining_sections=remaining_text,
        )

        try:
            response = self._replan_llm.ask(prompt)
            self.llm_call_count += 1
            return parse_llm_json(response)
        except Exception as e:
            log(f"  [Planner] Replan error: {e}", self.debug, self.debug_file)
            self.llm_call_count += 1
            return None

    # ----------------------------------------------------------------
    # Internal Helpers
    # ----------------------------------------------------------------

    def _format_spec(self, sections: List[SpecSection]) -> str:
        """Format the full spec for the planner prompt."""
        parts = []
        for s in sections:
            parts.append(f"### {s.name}\n\n{s.raw_text}")
        return "\n\n---\n\n".join(parts)

    def _parse_plan(
        self,
        data: Dict[str, Any],
        all_sections: List[SpecSection],
    ) -> TraversalPlan:
        """Parse the LLM response into a TraversalPlan."""
        valid_section_names = {s.name for s in all_sections}
        reasoning = data.get("plan_reasoning", "")
        phases = data.get("phases", [])
        steps: List[TraversalStep] = []

        for phase_data in phases:
            phase_name = phase_data.get("phase", "public")
            for step_data in phase_data.get("steps", []):
                section_name = step_data.get("target_section", "")
                if section_name not in valid_section_names:
                    log(
                        f"  [Planner] Unknown section '{section_name}' in plan — skipping.",
                        self.debug, self.debug_file,
                    )
                    continue

                steps.append(TraversalStep(
                    target_section=section_name,
                    page_type=step_data.get("page_type", "listing"),
                    how_to_reach=step_data.get("how_to_reach", ""),
                    prerequisites=step_data.get("prerequisites", []),
                    interactions_needed=step_data.get("interactions_needed", ""),
                    phase=phase_name,
                ))

        # Ensure all sections are in the plan (add missing ones at the end)
        planned_sections = {s.target_section for s in steps}
        for section in all_sections:
            if section.name not in planned_sections:
                log(
                    f"  [Planner] Section '{section.name}' not in plan — appending.",
                    self.debug, self.debug_file,
                )
                steps.append(TraversalStep(
                    target_section=section.name,
                    page_type="listing",
                    how_to_reach=f"Navigate to the page described by '{section.name}'",
                    prerequisites=[],
                    interactions_needed="",
                    phase="authenticated",
                ))

        plan = TraversalPlan(
            reasoning=reasoning,
            phases=phases,
            steps=steps,
        )

        log(
            f"  [Planner] Generated plan with {len(steps)} steps: "
            + " → ".join(s.target_section for s in steps),
            self.debug, self.debug_file,
        )

        return plan

    def _fallback_plan(self, all_sections: List[SpecSection]) -> TraversalPlan:
        """Generate a basic fallback plan if the LLM fails."""
        log(
            "  [Planner] Using fallback plan (LLM failed).",
            self.debug, self.debug_file,
        )
        steps = [
            TraversalStep(
                target_section=s.name,
                page_type="listing",
                how_to_reach=f"Navigate to the page described by '{s.name}'",
                prerequisites=[],
                interactions_needed="",
                phase="authenticated",
            )
            for s in all_sections
        ]
        return TraversalPlan(
            reasoning="Fallback: visit sections in spec order.",
            phases=[],
            steps=steps,
        )
