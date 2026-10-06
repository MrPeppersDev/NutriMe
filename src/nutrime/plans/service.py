"""Plan generation as a service — one code path for the CLI and the web.

``plan_base_filters`` builds the shared candidate filters (household
constraints, inventory + use-it-up, cook-history boosts, novelty nudge);
``generate_and_store`` runs the planner, audits the pre-surface findings
(#30) and writes the plan to the vault.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Callable

from nutrime.plans.assemble import AssembledPlan, PlanSpec, SlotOutcome, assemble_plan
from nutrime.plans.store import PlanVault, new_plan_id, render_plan_body
from nutrime.recipes.search import SearchFilters, filters_from_constraints
from nutrime.recipes.store import RecipeVault

LOCAL_MODEL_SETUP = (
    "The local model isn't running. One-time setup: install Ollama from"
    " https://ollama.com, run `ollama pull qwen3:8b`, then start it"
    " (it runs in the background once installed; `ollama serve` starts it"
    " by hand)."
)


class PlanRefusedError(Exception):
    """A refuse-level disclosed condition blocks plan generation
    (sweep #10 behavior framework — deterministic, outside any LLM)."""


def plan_base_filters(
    app,
    *,
    max_time: int | None = None,
    apply_constraints: bool = True,
    use_inventory: bool = True,
) -> tuple[SearchFilters, list[str]]:
    """Shared filters for every slot + a human note of what applied."""
    from nutrime.feedback import cooked_cuisines, experience_summaries
    from nutrime.inventory.store import expiring_names, list_items
    from nutrime.knowledge.store import list_synthesized_entries

    filters = SearchFilters(max_total_time_min=max_time)
    applied: list[str] = []
    if apply_constraints:
        entries = list_synthesized_entries(
            app.substrate, app.tenant_id, entry_type="abstracted_constraint"
        )
        filters = filters_from_constraints(entries, base=filters)
        applied.append(f"{len(entries)} abstracted constraint(s)")
    if use_inventory:
        items = list_items(app.substrate, app.tenant_id)
        filters = replace(filters, on_hand=frozenset(item.name for item in items))
        applied.append(f"{len(items)} inventory item(s)")
        # V2: expiring items tilt candidate pools toward use-it-up.
        expiring = expiring_names(
            app.substrate, app.tenant_id, today=date.today().isoformat()
        )
        if expiring:
            filters = replace(
                filters, expiring=frozenset(i.name.lower() for i in expiring)
            )
            applied.append(f"{len(expiring)} expiring item(s) prioritized")
    # V1: cook history boosts candidate pools (loved up, disliked down).
    experience = experience_summaries(app.substrate, app.tenant_id)
    if experience:
        filters = replace(filters, experience=experience)
        applied.append(f"experience from {len(experience)} cooked recipe(s)")
    # V3: novelty nudge is planner-default (broadening is a planning-time
    # concern, not a what-can-I-make-right-now concern).
    cooked = cooked_cuisines(app.substrate, app.tenant_id, RecipeVault(app.corpus_dir))
    if cooked:
        filters = replace(filters, cooked_cuisines=frozenset(cooked))
        applied.append("novelty nudge (new-cuisine candidates boosted)")
    return filters, applied


def generate_and_store(
    app,
    client,
    spec: PlanSpec,
    filters: SearchFilters,
    applied: list[str],
    *,
    model_hint: str | None = None,
    actor: str = "planner",
    on_progress: Callable[[SlotOutcome], None] | None = None,
    seed: int | None = None,
) -> tuple[str, Path, AssembledPlan]:
    """Run the planner, audit surface findings, write the plan.

    Raises :class:`PlanRefusedError` before any LLM crossing when a
    household member disclosed a refuse-level condition (sweep #10).
    Gate-level conditions inject their constraint lines into every
    crossing's household note instead.
    """
    from nutrime.audit import _now_iso
    from nutrime.conditions import household_gates
    from nutrime.surface_rules import household_sensitivities

    gates = household_gates(app.substrate, app.tenant_id)
    if gates.refused:
        app.audit.record_event(
            event_kind="audit",
            event_subkind="condition_gate",
            actor=actor,
            payload={
                "action": "refused",
                "conditions": [c.canonical for c in gates.refusals],
            },
        )
        raise PlanRefusedError(gates.refusal_message())
    if gates.plan_notes:
        base = spec.household_note.strip() or f"{spec.servings} servings"
        spec = replace(
            spec,
            household_note=base + "; " + "; ".join(gates.plan_notes),
        )
        applied = applied + [
            f"condition rails ({len(gates.plan_notes)})"
        ]

    vault = RecipeVault(app.corpus_dir)
    plan = assemble_plan(
        vault, client, spec, filters, on_progress=on_progress, seed=seed,
        eater_sensitivities=household_sensitivities(app.substrate, app.tenant_id),
    )
    # #30: every pre-surface finding is audited (the reason text itself is
    # not — a blocked reason is not worth preserving, and the request log
    # already holds the raw response).
    for outcome in plan.outcomes:
        for finding in outcome.surface_findings:
            app.audit.record_event(
                event_kind="audit",
                event_subkind="surface_rule",
                actor=actor,
                request_id=outcome.request_id,
                payload={
                    "surface": "plan_reason",
                    "rule": finding.rule_name,
                    "action": finding.action,
                    "reason": finding.reason,
                    "day": outcome.day,
                    "slot": outcome.slot,
                },
            )
    plan_id = new_plan_id()
    frontmatter = {
        "plan_id": plan_id,
        "content_type": "meal_plan",
        "created_at": _now_iso(),
        "tenant_id": app.tenant_id,
        "days": spec.days,
        "meal_slots": list(spec.slots),
        "meals_planned": plan.filled,
        "model": plan.model or model_hint or "",
        "llm_request_ids": list(plan.request_ids),
        "llm_request_log_ids": list(plan.llm_request_log_ids),
        "constraints_applied": applied,
        "candidate_count": plan.candidate_count,
        "candidate_seed": seed,
    }
    path = PlanVault(app.corpus_dir).write(
        plan_id, frontmatter, render_plan_body(plan.entries)
    )
    return plan_id, path, plan


def local_client(app, model: str | None = None):
    """LlmClient over the local Ollama daemon, or None when it isn't up."""
    from nutrime.llm.client import LlmClient
    from nutrime.llm.ollama import OllamaProvider, is_available

    if not is_available():
        return None
    return LlmClient((OllamaProvider(model=model or ""),), app.rule_engine, app.audit)
