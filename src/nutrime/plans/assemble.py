"""Plan assembly (5.4) — candidate generation, the crossing, the guard.

One LLM call per meal. Each call gets its own candidate pool from 5.3 search,
its own :class:`~nutrime.llm.base.LlmRequest`, and its own audit row. The
model's only job is *selection* from that pool.

PHI discipline (S4-Q2). ``meal_plan_generation`` declares
``{allergens, demographics}`` as the union across decomposed slices, and
:meth:`LlmClient.complete` rejects any single crossing carrying more than one.
This module carries exactly one: ``demographics`` (household size / servings).
The allergen slice is handled entirely locally — 5.3's
``filters_from_constraints`` hard-blocks allergens at candidate generation, so
the pool handed to the model is already safe and the prompt never names a
constraint. That local filtering *is* the aggregation half of decomposition.

Variety is deterministic, not delegated: already-chosen recipe ids are removed
from later slots' candidate pools rather than asked-for in the prompt.

Pre-surface (#30, hardened per #49): the model writes NO display text at
all. It picks a ``reason_code`` from a fixed vocabulary and the note is
rendered deterministically from corpus facts (time, on-hand matches,
expiring matches). Paraphrase space is unbounded, so filtering free text
was unwinnable — constraining the output is the fix the regex layer
couldn't be. The surface guard still runs on the rendered note as
defense in depth, and findings ride on the outcome for audit.
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, field, replace
from typing import Callable, Sequence

from nutrime.llm.base import (
    CAP_REASONING,
    ChatMessage,
    LlmRequest,
    ProviderError,
)
from nutrime.llm.client import LlmClient
from nutrime.llm.phi import MEAL_PLAN_GENERATION
from nutrime.phi import PhiCategory
from nutrime.plans.store import PlanEntry
from nutrime.recipes.search import SearchFilters, SearchResult, search
from nutrime.recipes.store import RecipeVault
from nutrime.surface_rules import (
    SurfaceContent,
    SurfaceFinding,
    SurfaceGuard,
    default_surface_guard,
)

# Slot vocabulary -> corpus category profile.
#
# Corpus ``meal_categories`` are not a meal-slot vocabulary: TheMealDB tags by
# course (dessert, side, starter), protein (beef, chicken, lamb) and diet
# (vegetarian) in the same field, and never emits "dinner" or "lunch" at all.
# So the main-course slots are defined by *exclusion* — anything not obviously
# a dessert, side, or breakfast is a candidate main — while the slots that do
# have real tags match positively.
_NON_MAIN = frozenset(
    {
        "dessert",
        "side",
        "starter",
        "breakfast",
        "baking",
        "pudding",
        "tart",
        "snack",
    }
)


@dataclass(frozen=True)
class SlotProfile:
    include_any: frozenset[str] = frozenset()
    exclude: frozenset[str] = frozenset()


SLOT_PROFILES: dict[str, SlotProfile] = {
    "breakfast": SlotProfile(include_any=frozenset({"breakfast"})),
    "lunch": SlotProfile(exclude=_NON_MAIN),
    "dinner": SlotProfile(exclude=_NON_MAIN),
    "snack": SlotProfile(include_any=frozenset({"snack", "starter", "side"})),
    "side": SlotProfile(include_any=frozenset({"side"})),
    "dessert": SlotProfile(
        include_any=frozenset({"dessert", "pudding", "tart", "baking"})
    ),
}

MEAL_SLOTS = tuple(SLOT_PROFILES)

DEFAULT_CANDIDATES = 12

_SYSTEM = (
    "You are a meal planner. You select meals from a fixed list of candidate"
    " recipes; you never invent a recipe, and you never suggest one that is"
    " not in the list. You never write prose: you report your pick and a"
    " reason code from the fixed vocabulary. Reply with JSON only."
)


class SelectionError(ValueError):
    """The model returned something that is not a candidate for this slot."""


@dataclass(frozen=True)
class PlanSpec:
    days: int = 7
    slots: tuple[str, ...] = ("dinner",)
    servings: int = 2
    household_note: str = ""
    candidates_per_slot: int = DEFAULT_CANDIDATES

    def __post_init__(self) -> None:
        if self.days < 1:
            raise ValueError("days must be >= 1")
        if not self.slots:
            raise ValueError("at least one meal slot is required")
        if self.servings < 1:
            raise ValueError("servings must be >= 1")

    @property
    def crossings(self) -> int:
        """How many LLM calls a full run of this spec will make."""
        return self.days * len(self.slots)


@dataclass(frozen=True)
class SlotOutcome:
    day: int
    slot: str
    entry: PlanEntry
    candidate_count: int
    request_id: str | None = None
    llm_request_log_id: str | None = None
    error: str | None = None
    surface_findings: tuple[SurfaceFinding, ...] = ()


@dataclass
class AssembledPlan:
    entries: list[PlanEntry] = field(default_factory=list)
    outcomes: list[SlotOutcome] = field(default_factory=list)
    request_ids: list[str] = field(default_factory=list)
    llm_request_log_ids: list[str] = field(default_factory=list)
    candidate_count: int = 0
    model: str = ""

    @property
    def filled(self) -> int:
        return sum(1 for e in self.entries if e.filled)

    @property
    def failures(self) -> list[SlotOutcome]:
        return [o for o in self.outcomes if o.error is not None]


# -- candidate generation --------------------------------------------------


def candidates_for_slot(
    vault: RecipeVault,
    base_filters: SearchFilters,
    slot: str,
    *,
    exclude_ids: frozenset[str] = frozenset(),
    limit: int = DEFAULT_CANDIDATES,
    rng: random.Random | None = None,
) -> list[SearchResult]:
    """Pool for one meal slot: 5.3 search, minus anything already chosen.

    ``exclude_ids`` is applied after ranking, so over-fetching keeps the pool
    full once earlier slots have consumed the top results.

    ``rng`` shuffles *within* ranking ties. Search breaks ties by title A-Z,
    which is right for a browsable list but wrong for a pool: with no
    inventory / constraints / history every recipe scores 0, and the planner
    saw the same dozen digit- and quote-led titles out of ~2,200 on every
    run. Ranking signal still dominates — only equal (match-count, score)
    rows are reordered.
    """
    profile = SLOT_PROFILES.get(slot, SlotProfile(include_any=frozenset({slot})))
    filters = replace(
        base_filters,
        meal_categories_any=profile.include_any,
        exclude_categories=profile.exclude,
    )
    if rng is None:
        over_fetch = limit + len(exclude_ids)
        results = search(vault, filters, limit=over_fetch)
    else:
        results = search(vault, filters, limit=None)
        rng.shuffle(results)
        # Stable sort: ties keep their shuffled order.
        results.sort(key=lambda r: (-len(r.on_hand_matches), -r.score))
    return [r for r in results if r.recipe_id not in exclude_ids][:limit]


# -- prompt ----------------------------------------------------------------


def build_prompt(
    day: int, slot: str, candidates: Sequence[SearchResult], spec: PlanSpec
) -> str:
    household = spec.household_note.strip() or f"{spec.servings} servings"
    lines = [
        f"Day {day} of {spec.days}. Choose the {slot} for a household needing"
        f" {household}.",
        "",
        "Candidates:",
    ]
    for index, candidate in enumerate(candidates, start=1):
        time_str = (
            f"{candidate.total_time_min} min"
            if candidate.total_time_min is not None
            else "time unknown"
        )
        lines.append(
            f"{index}. id={candidate.recipe_id} | {candidate.title} | {time_str}"
        )
    lines += [
        "",
        "Pick exactly one candidate. Reply with JSON only, in this form:",
        '{"recipe_id": "<id copied from the list>", "reason_code":'
        ' "<one of: ' + ", ".join(REASON_CODES) + '>"}',
    ]
    return "\n".join(lines)


# -- reason vocabulary (#49) -------------------------------------------------
# The model picks a code; the sentence the household reads is rendered
# here, from corpus facts. No model-written display text exists, so no
# paraphrased health claim can reach a plan note.

REASON_CODES: tuple[str, ...] = (
    "quick",          # short total time
    "uses_on_hand",   # overlaps the kitchen inventory
    "uses_expiring",  # uses up something due soon
    "variety",        # breaks up the week / new cuisine
    "crowd_pleaser",  # broadly liked, mild
    "seasonal_fit",   # fits the season / weather
    "balanced",       # rounds out the day's other meals
)


def render_reason(
    code: str, candidate: "SearchResult | None"
) -> str:
    """Deterministic display text for a reason code.

    Facts come from the search result (corpus + inventory), never from
    the model. An unknown code renders as "" — fail-closed to silence.
    """
    on_hand = ", ".join(candidate.on_hand_matches[:3]) if candidate else ""
    expiring = ", ".join(candidate.expiring_matches[:3]) if candidate else ""
    time_min = candidate.total_time_min if candidate else None
    if code == "quick":
        return (
            f"On the table in about {time_min} minutes."
            if time_min
            else "Quick to make."
        )
    if code == "uses_on_hand":
        return (
            f"Uses what's in the kitchen: {on_hand}."
            if on_hand
            else "Works with what's already in the kitchen."
        )
    if code == "uses_expiring":
        return (
            f"Uses up food that's due soon: {expiring}."
            if expiring
            else "Uses up ingredients before they go to waste."
        )
    if code == "variety":
        return "Something different to break up the week."
    if code == "crowd_pleaser":
        return "Mild and broadly liked — an easy sell at the table."
    if code == "seasonal_fit":
        return "A good fit for the season."
    if code == "balanced":
        return "Rounds out the day's other meals."
    return ""


# -- the guard -------------------------------------------------------------

_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def parse_selection(
    text: str, candidate_ids: frozenset[str]
) -> tuple[str, str]:
    """Extract ``(recipe_id, reason)``, rejecting anything off the candidate list.

    This is the load-bearing guard: the corpus is licensed recipe-by-recipe,
    so a plan may only ever name a recipe the vault actually holds. A model
    that invents an id, or picks one from another slot's pool, fails here.
    """
    match = _JSON_OBJECT.search(text or "")
    if match is None:
        raise SelectionError(f"no JSON object in model reply: {text!r:.200}")
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise SelectionError(f"model reply is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise SelectionError("model reply JSON is not an object")
    recipe_id = str(payload.get("recipe_id", "")).strip()
    if not recipe_id:
        raise SelectionError("model reply has no recipe_id")
    if recipe_id not in candidate_ids:
        raise SelectionError(
            f"model selected {recipe_id!r}, which was not among the"
            f" {len(candidate_ids)} candidates offered for this slot"
        )
    # #49: the model picks from a fixed vocabulary — it does not write
    # display text. An off-vocabulary code (including legacy free-text
    # "reason") degrades to "" rather than failing the selection.
    code = str(payload.get("reason_code", "")).strip().lower()
    if code not in REASON_CODES:
        code = ""
    return recipe_id, code


# -- assembly --------------------------------------------------------------


def assemble_plan(
    vault: RecipeVault,
    client: LlmClient,
    spec: PlanSpec,
    base_filters: SearchFilters,
    *,
    max_tokens: int = 256,
    on_progress: Callable[[SlotOutcome], None] | None = None,
    seed: int | None = None,
    surface_guard: SurfaceGuard | None = None,
    eater_sensitivities: frozenset[str] = frozenset(),
) -> AssembledPlan:
    """Fill every day x slot, one audited crossing each.

    Fails soft per slot: a provider error or a rejected selection leaves that
    slot unfilled and the run continues. Every failure is already recorded in
    ``op_llm_request_log`` by the client, so nothing is lost by carrying on.

    ``seed`` turns on tie-shuffled candidate pools (see
    :func:`candidates_for_slot`); the same seed reproduces the same pools.
    """
    plan = AssembledPlan()
    chosen: set[str] = set()
    rng = random.Random(seed) if seed is not None else None
    guard = surface_guard or default_surface_guard()

    for day in range(1, spec.days + 1):
        for slot in spec.slots:
            candidates = candidates_for_slot(
                vault,
                base_filters,
                slot,
                exclude_ids=frozenset(chosen),
                limit=spec.candidates_per_slot,
                rng=rng,
            )
            plan.candidate_count += len(candidates)

            if not candidates:
                # Distinguish "filters too tight" from "the corpus ran out of
                # unused recipes for this slot" — very different user fixes.
                exhausted = bool(
                    chosen
                    and candidates_for_slot(
                        vault, base_filters, slot, limit=1
                    )
                )
                reason = (
                    "variety exhausted — no unused recipe left for this slot"
                    if exhausted
                    else "no candidates matched"
                )
                outcome = SlotOutcome(
                    day=day,
                    slot=slot,
                    entry=PlanEntry(day=day, slot=slot, note=reason),
                    candidate_count=0,
                    error=reason,
                )
                plan.entries.append(outcome.entry)
                plan.outcomes.append(outcome)
                if on_progress:
                    on_progress(outcome)
                continue

            request = LlmRequest(
                query_type=MEAL_PLAN_GENERATION,
                system=_SYSTEM,
                messages=(
                    ChatMessage(
                        role="user",
                        content=build_prompt(day, slot, candidates, spec),
                    ),
                ),
                max_tokens=max_tokens,
                # Exactly one slice. Allergens stay local (see module docstring).
                phi_categories=frozenset({PhiCategory.DEMOGRAPHICS}),
                # Local-mandatory (2026-10-06): the planner demands
                # reasoning only; locality is decided by the client's
                # PHI routing, never by the caller asking for cloud.
                required_capabilities=frozenset(
                    {CAP_REASONING}
                ),
                caller_context=f"plan/day{day}/{slot}",
            )

            candidate_ids = frozenset(c.recipe_id for c in candidates)
            titles = {c.recipe_id: c.title for c in candidates}

            try:
                response = client.complete(request)
            except ProviderError as exc:
                outcome = SlotOutcome(
                    day=day,
                    slot=slot,
                    entry=PlanEntry(
                        day=day, slot=slot, note=f"provider error: {exc.outcome}"
                    ),
                    candidate_count=len(candidates),
                    error=f"{exc.outcome}: {exc.detail}",
                )
                plan.entries.append(outcome.entry)
                plan.outcomes.append(outcome)
                if on_progress:
                    on_progress(outcome)
                continue

            plan.request_ids.append(response.request_id)
            plan.llm_request_log_ids.append(response.llm_request_log_id)
            plan.model = response.model

            try:
                recipe_id, reason_code = parse_selection(
                    response.text, candidate_ids
                )
            except SelectionError as exc:
                outcome = SlotOutcome(
                    day=day,
                    slot=slot,
                    entry=PlanEntry(
                        day=day, slot=slot, note="selection rejected"
                    ),
                    candidate_count=len(candidates),
                    request_id=response.request_id,
                    llm_request_log_id=response.llm_request_log_id,
                    error=str(exc),
                )
                plan.entries.append(outcome.entry)
                plan.outcomes.append(outcome)
                if on_progress:
                    on_progress(outcome)
                continue

            chosen.add(recipe_id)
            # #49: the note is rendered here from corpus facts — the
            # model only contributed a vocabulary code. The guard still
            # runs on the rendered text as defense in depth (a template
            # edit or interpolated fact could regress).
            chosen_candidate = next(
                (c for c in candidates if c.recipe_id == recipe_id), None
            )
            rendered = render_reason(reason_code, chosen_candidate)
            verdict = guard.check(
                SurfaceContent(
                    surface="plan_reason",
                    text=rendered,
                    generated=True,
                    eater_sensitivities=eater_sensitivities,
                )
            )
            entry = PlanEntry(
                day=day,
                slot=slot,
                recipe_id=recipe_id,
                title=titles.get(recipe_id, ""),
                note=verdict.text,
            )
            outcome = SlotOutcome(
                day=day,
                slot=slot,
                entry=entry,
                candidate_count=len(candidates),
                request_id=response.request_id,
                llm_request_log_id=response.llm_request_log_id,
                surface_findings=verdict.findings,
            )
            plan.entries.append(entry)
            plan.outcomes.append(outcome)
            if on_progress:
                on_progress(outcome)

    return plan
