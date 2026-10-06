"""Sub-commit 5.4 — LLM plan assembly.

Covers the plan vault round-trip and its own frontmatter contract, the
body render/parse pair that hands off to 6.1, the anti-hallucination
selection guard, per-meal crossing discipline (one call per meal, exactly one
PHI slice each), deterministic variety, fail-soft slot handling, and the CLI
surfaces including attribution-at-render (#23) on the plan display.
"""

from __future__ import annotations

import json
import random

import pytest

from nutrime.audit import AuditLog, attach_pre_egress_audit
from nutrime.db import apply_migrations, connect
from nutrime.llm.base import LlmRequest, ProviderError, ProviderResult
from nutrime.llm.client import LlmClient, LlmDecompositionError
from nutrime.llm.phi import MEAL_PLAN_GENERATION, register_llm_envelopes
from nutrime.paths import default_operational_migrations_dir
from nutrime.phi import PhiCategory, PhiEnvelopeRegistry, PhiEnvelopeRule
from nutrime.plans.assemble import (
    PlanSpec,
    SelectionError,
    assemble_plan,
    build_prompt,
    candidates_for_slot,
    parse_selection,
)
from nutrime.plans.store import (
    PlanEntry,
    PlanVault,
    new_plan_id,
    parse_plan_body,
    render_plan_body,
    validate_plan_frontmatter,
)
from nutrime.recipes.frontmatter import Attribution, Yields, build_recipe_frontmatter
from nutrime.recipes.search import SearchFilters
from nutrime.recipes.store import RecipeVault
from nutrime.rules import PromptInjectionGuard, RuleEngine


# -- fixtures --------------------------------------------------------------


def _frontmatter(recipe_id: str, title: str, **overrides):
    kwargs = dict(
        recipe_id=recipe_id,
        title=title,
        attribution=Attribution(
            source_name=overrides.pop("source_name", "TheMealDB"),
            source_url="https://example.test/r",
            source_license=overrides.pop("source_license", "free-tier-attribution"),
            ingested_at="2026-08-09T00:00:00Z",
            ingestion_method="rest_api",
        ),
        source_status="live",
        last_source_check_at="2026-08-09T00:00:00Z",
        yields=Yields(count=4),
        top_allergens_present=overrides.pop("allergens", []),
        estimated_total_time_min=overrides.pop("total_time", 30),
        meal_categories=overrides.pop("categories", ["dinner"]),
        cuisine_tradition_tags=overrides.pop("cuisines", ["american"]),
    )
    kwargs.update(overrides)
    return build_recipe_frontmatter(**kwargs)


def _body(*ingredients: str) -> str:
    lines = [">> title: t", "", "-- Ingredients", ""]
    lines += list(ingredients)
    lines += ["", "-- Instructions", "", "Cook everything.", ""]
    return "\n".join(lines)


@pytest.fixture()
def recipes(tmp_path):
    vault = RecipeVault(tmp_path / "corpus")
    for n in range(1, 5):
        vault.write(
            f"rcp-d{n}",
            _frontmatter(f"rcp-d{n}", f"Dinner {n}"),
            _body("@chicken{1}"),
        )
    for n in range(1, 3):
        vault.write(
            f"rcp-b{n}",
            _frontmatter(f"rcp-b{n}", f"Breakfast {n}", categories=["breakfast"]),
            _body("@oats{1}"),
        )
    return vault


@pytest.fixture()
def audit(tmp_path):
    conn = connect(tmp_path / "operational.db")
    apply_migrations(conn, default_operational_migrations_dir())
    yield AuditLog(conn)
    conn.close()


@pytest.fixture()
def engine(audit):
    registry = PhiEnvelopeRegistry()
    register_llm_envelopes(registry)
    engine = RuleEngine()
    engine.register(PromptInjectionGuard())
    engine.register(PhiEnvelopeRule(registry))
    attach_pre_egress_audit(engine, audit)
    return engine


class SelectingProvider:
    """Picks the Nth candidate offered, by parsing its own prompt."""

    name = "fake"
    model = "fake-model"
    # Local-mandatory world (2026-10-06): the planner's PHI crossing
    # requires a local-private provider — fakes model the local tier.
    capabilities = frozenset({"reasoning", "local-private"})

    def __init__(self, index: int = 0, errors_on: tuple[int, ...] = ()):
        self._index = index
        self._errors_on = errors_on
        self.requests: list[LlmRequest] = []

    def complete(self, request: LlmRequest) -> ProviderResult:
        call = len(self.requests)
        self.requests.append(request)
        if call in self._errors_on:
            raise ProviderError(
                "error_provider", "boom", request_payload='{"req": 1}'
            )
        ids = [
            line.split("id=")[1].split(" |")[0]
            for line in request.messages[0].content.splitlines()
            if "id=" in line
        ]
        chosen = ids[min(self._index, len(ids) - 1)]
        return ProviderResult(
            text=json.dumps({"recipe_id": chosen, "reason": "fits the night"}),
            model="fake-model",
            stop_reason="end_turn",
            prompt_tokens=10,
            completion_tokens=5,
            request_payload='{"req": 1}',
            response_payload='{"resp": 1}',
        )


def _client(engine, audit, provider):
    return LlmClient((provider,), engine, audit)


# -- vault -----------------------------------------------------------------


def _plan_fm(**overrides):
    fm = {
        "plan_id": "pln-1",
        "content_type": "meal_plan",
        "created_at": "2026-09-07T00:00:00Z",
        "tenant_id": "tnt-1",
        "days": 2,
        "meal_slots": ["dinner"],
        "meals_planned": 2,
        "model": "fake-model",
        "llm_request_ids": ["req-a", "req-b"],
        "llm_request_log_ids": ["llr-a", "llr-b"],
        "constraints_applied": [],
        "candidate_count": 8,
    }
    fm.update(overrides)
    return fm


class TestPlanVault:
    def test_round_trip(self, tmp_path):
        vault = PlanVault(tmp_path / "corpus")
        entries = [
            PlanEntry(1, "dinner", "rcp-d1", "Dinner 1", "quick"),
            PlanEntry(2, "dinner", "rcp-d2", "Dinner 2", ""),
        ]
        vault.write("pln-1", _plan_fm(), render_plan_body(entries))
        record = vault.read("pln-1")
        assert record.frontmatter["content_type"] == "meal_plan"
        assert record.frontmatter["llm_request_log_ids"] == ["llr-a", "llr-b"]
        assert record.entries() == tuple(entries)

    def test_iter_plans_newest_first(self, tmp_path):
        # Ordering must key off created_at, not the filename: uuid7() is not
        # monotonic within a millisecond, so ids minted back-to-back can sort
        # against creation order.
        vault = PlanVault(tmp_path / "corpus")
        older, newer = new_plan_id(), new_plan_id()
        vault.write(
            older,
            _plan_fm(plan_id=older, created_at="2026-09-01T00:00:00Z"),
            render_plan_body([]),
        )
        vault.write(
            newer,
            _plan_fm(plan_id=newer, created_at="2026-09-07T00:00:00Z"),
            render_plan_body([]),
        )
        assert [r.plan_id for r in vault.list_plans()] == [newer, older]
        assert vault.count() == 2

    def test_missing_field_rejected(self):
        fm = _plan_fm()
        del fm["llm_request_log_ids"]
        with pytest.raises(ValueError, match="llm_request_log_ids"):
            validate_plan_frontmatter(fm)

    def test_wrong_content_type_rejected(self):
        with pytest.raises(ValueError, match="content_type"):
            validate_plan_frontmatter(_plan_fm(content_type="recipe"))


class TestPlanBody:
    def test_unfilled_slot_round_trips_as_none(self):
        entries = [PlanEntry(1, "dinner", None, "", "no candidates matched")]
        [parsed] = parse_plan_body(render_plan_body(entries))
        assert parsed.recipe_id is None
        assert parsed.filled is False
        assert parsed.note == "no candidates matched"

    def test_pipe_in_title_survives(self):
        entries = [PlanEntry(1, "dinner", "rcp-x", "Fish | Chips", "")]
        [parsed] = parse_plan_body(render_plan_body(entries))
        assert parsed.title == "Fish | Chips"

    def test_prose_around_the_table_is_ignored(self):
        body = "# My plan\n\nSome notes.\n\n" + render_plan_body(
            [PlanEntry(1, "dinner", "rcp-x", "X", "")]
        )
        assert len(parse_plan_body(body)) == 1


# -- the guard -------------------------------------------------------------


class TestParseSelection:
    def test_accepts_candidate(self):
        text = '{"recipe_id": "rcp-d1", "reason": "quick"}'
        assert parse_selection(text, frozenset({"rcp-d1"})) == ("rcp-d1", "quick")

    def test_tolerates_prose_around_json(self):
        text = 'Sure!\n{"recipe_id": "rcp-d1", "reason": "ok"}\nHope that helps.'
        assert parse_selection(text, frozenset({"rcp-d1"}))[0] == "rcp-d1"

    def test_rejects_recipe_outside_candidate_set(self):
        # The load-bearing guard: the corpus is licensed recipe-by-recipe, so
        # a hallucinated or cross-slot id must never reach a plan.
        text = '{"recipe_id": "rcp-invented", "reason": "sounds nice"}'
        with pytest.raises(SelectionError, match="not among the"):
            parse_selection(text, frozenset({"rcp-d1", "rcp-d2"}))

    def test_rejects_non_json(self):
        with pytest.raises(SelectionError, match="no JSON object"):
            parse_selection("I recommend the chicken.", frozenset({"rcp-d1"}))

    def test_rejects_missing_recipe_id(self):
        with pytest.raises(SelectionError, match="no recipe_id"):
            parse_selection('{"reason": "tasty"}', frozenset({"rcp-d1"}))


# -- candidate generation --------------------------------------------------


class TestCandidates:
    def test_filters_by_slot(self, recipes):
        pool = candidates_for_slot(recipes, SearchFilters(), "breakfast")
        assert [c.recipe_id for c in pool] == ["rcp-b1", "rcp-b2"]

    def test_exclusion_keeps_pool_full(self, recipes):
        pool = candidates_for_slot(
            recipes, SearchFilters(), "dinner", exclude_ids=frozenset({"rcp-d1"}), limit=3
        )
        assert "rcp-d1" not in {c.recipe_id for c in pool}
        assert len(pool) == 3

    def test_seeded_pool_breaks_ties_off_alphabetical(self, tmp_path):
        # All-tie corpus (no inventory/constraints/history — a fresh
        # household): without a seed the pool is the first N titles A-Z.
        vault = RecipeVault(tmp_path / "corpus")
        for n in range(30):
            vault.write(
                f"rcp-t{n:02d}", _frontmatter(f"rcp-t{n:02d}", f"Dish {n:02d}"),
                _body("@rice{1}"),
            )
        alphabetical = [c.recipe_id for c in candidates_for_slot(
            vault, SearchFilters(), "dinner", limit=5
        )]
        assert alphabetical == [f"rcp-t{n:02d}" for n in range(5)]

        def seeded(seed):
            return [c.recipe_id for c in candidates_for_slot(
                vault, SearchFilters(), "dinner", limit=5,
                rng=random.Random(seed),
            )]

        assert seeded(7) == seeded(7)  # reproducible
        pools = {tuple(seeded(s)) for s in range(10)}
        assert len(pools) > 1
        assert any(p != tuple(alphabetical) for p in pools)

    def test_seeded_pool_keeps_ranking_signal_first(self, recipes):
        # Shuffling only reorders ties: an on-hand match still outranks
        # every zero-match recipe whatever the seed.
        filters = SearchFilters(on_hand=frozenset({"oats"}))
        for seed in range(5):
            pool = candidates_for_slot(
                recipes, filters, "breakfast", rng=random.Random(seed)
            )
            assert {c.recipe_id for c in pool[:2]} == {"rcp-b1", "rcp-b2"}

    def test_seeded_pool_honours_exclusions(self, recipes):
        pool = candidates_for_slot(
            recipes, SearchFilters(), "dinner",
            exclude_ids=frozenset({"rcp-d1"}), limit=3, rng=random.Random(1),
        )
        assert "rcp-d1" not in {c.recipe_id for c in pool}
        assert len(pool) == 3

    def test_prompt_lists_ids_and_asks_for_json(self, recipes):
        pool = candidates_for_slot(recipes, SearchFilters(), "dinner", limit=2)
        prompt = build_prompt(1, "dinner", pool, PlanSpec(days=1, slots=("dinner",)))
        assert "id=rcp-d1" in prompt
        assert "recipe_id" in prompt
        assert "Day 1 of 1" in prompt


# -- assembly --------------------------------------------------------------


class TestPlanSpec:
    def test_crossings_is_days_times_slots(self):
        assert PlanSpec(days=7, slots=("breakfast", "lunch", "dinner")).crossings == 21

    @pytest.mark.parametrize(
        "kwargs", [{"days": 0}, {"slots": ()}, {"servings": 0}]
    )
    def test_invalid_spec_rejected(self, kwargs):
        with pytest.raises(ValueError):
            PlanSpec(**kwargs)


class TestAssemble:
    def test_one_crossing_per_meal(self, recipes, engine, audit):
        provider = SelectingProvider()
        spec = PlanSpec(days=2, slots=("dinner", "breakfast"), servings=2)
        plan = assemble_plan(
            recipes, _client(engine, audit, provider), spec, SearchFilters()
        )
        assert len(provider.requests) == spec.crossings == 4
        assert len(plan.llm_request_log_ids) == 4
        assert len(audit.llm_requests()) == 4

    def test_every_crossing_carries_exactly_one_phi_slice(
        self, recipes, engine, audit
    ):
        provider = SelectingProvider()
        assemble_plan(
            recipes,
            _client(engine, audit, provider),
            PlanSpec(days=2, slots=("dinner",)),
            SearchFilters(),
        )
        for request in provider.requests:
            assert request.phi_categories == frozenset({PhiCategory.DEMOGRAPHICS})
            assert request.query_type == MEAL_PLAN_GENERATION

    def test_allergen_terms_never_reach_the_prompt(self, recipes, engine, audit):
        # Allergens are enforced locally at candidate generation; the model is
        # told only which recipes it may choose, never what to avoid.
        provider = SelectingProvider()
        filters = SearchFilters(exclude_allergens=frozenset({"shellfish"}))
        assemble_plan(
            recipes,
            _client(engine, audit, provider),
            PlanSpec(days=1, slots=("dinner",)),
            filters,
        )
        prompt = provider.requests[0].messages[0].content
        assert "shellfish" not in prompt.lower()

    def test_variety_excludes_already_chosen(self, recipes, engine, audit):
        provider = SelectingProvider()
        plan = assemble_plan(
            recipes,
            _client(engine, audit, provider),
            PlanSpec(days=3, slots=("dinner",)),
            SearchFilters(),
        )
        chosen = [e.recipe_id for e in plan.entries]
        assert len(set(chosen)) == 3

    def test_provider_error_leaves_slot_unfilled_and_continues(
        self, recipes, engine, audit
    ):
        provider = SelectingProvider(errors_on=(0,))
        plan = assemble_plan(
            recipes,
            _client(engine, audit, provider),
            PlanSpec(days=3, slots=("dinner",)),
            SearchFilters(),
        )
        assert len(plan.entries) == 3
        assert plan.entries[0].filled is False
        assert plan.filled == 2
        assert len(plan.failures) == 1
        # The failed crossing is still on the record.
        outcomes = [r.outcome for r in audit.llm_requests()]
        assert "error_provider" in outcomes

    def test_slot_with_no_candidates_is_unfilled_without_crossing(
        self, recipes, engine, audit
    ):
        provider = SelectingProvider()
        plan = assemble_plan(
            recipes,
            _client(engine, audit, provider),
            PlanSpec(days=1, slots=("dessert",)),
            SearchFilters(),
        )
        assert provider.requests == []
        assert plan.entries[0].filled is False
        assert plan.failures[0].error == "no candidates matched"

    def test_variety_exhaustion_is_reported_distinctly(
        self, recipes, engine, audit
    ):
        # Only two breakfasts exist; a third day cannot be filled without
        # repeating, and the note must say so rather than blame the filters.
        plan = assemble_plan(
            recipes,
            _client(engine, audit, SelectingProvider()),
            PlanSpec(days=3, slots=("breakfast",)),
            SearchFilters(),
        )
        assert plan.filled == 2
        assert "variety exhausted" in plan.entries[2].note

    def test_rejected_selection_leaves_slot_unfilled(self, recipes, engine, audit):
        class LiarProvider(SelectingProvider):
            def complete(self, request):
                self.requests.append(request)
                return ProviderResult(
                    text='{"recipe_id": "rcp-invented", "reason": "no"}',
                    model="fake-model",
                    stop_reason="end_turn",
                    prompt_tokens=1,
                    completion_tokens=1,
                    request_payload="{}",
                    response_payload="{}",
                )

        plan = assemble_plan(
            recipes,
            _client(engine, audit, LiarProvider()),
            PlanSpec(days=1, slots=("dinner",)),
            SearchFilters(),
        )
        assert plan.entries[0].filled is False
        assert "not among the" in plan.failures[0].error

    def test_two_slices_in_one_crossing_is_refused(self, engine, audit):
        # Proves the S4-Q2 guard at the planner boundary: the envelope permits
        # allergens AND demographics as a union, but never in one crossing.
        client = _client(engine, audit, SelectingProvider())
        with pytest.raises(LlmDecompositionError):
            client.complete(
                LlmRequest(
                    query_type=MEAL_PLAN_GENERATION,
                    messages=(),
                    phi_categories=frozenset(
                        {PhiCategory.DEMOGRAPHICS, PhiCategory.ALLERGENS}
                    ),
                )
            )


# -- CLI -------------------------------------------------------------------


class TestPlansCLI:
    def _seed(self, tmp_path):
        """Write recipes into the data dir's corpus the CLI will open."""
        from nutrime.cli import main
        from nutrime.paths import default_corpus_dir

        main(["init", "--data-dir", str(tmp_path)])
        vault = RecipeVault(default_corpus_dir(tmp_path))
        for n in range(1, 4):
            vault.write(
                f"rcp-d{n}",
                _frontmatter(f"rcp-d{n}", f"Dinner {n}"),
                _body("@chicken{1}"),
            )
        return vault

    def test_dry_run_shows_pool_without_crossing(self, tmp_path, capsys):
        from nutrime.cli import main

        self._seed(tmp_path)
        rc = main(
            [
                "plans", "generate", "--data-dir", str(tmp_path),
                "--days", "2", "--meals", "dinner", "--dry-run",
            ]
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert "2 LLM crossing(s)" in out
        assert "dry run" in out
        assert "3 candidate(s)" in out

    def test_unknown_slot_rejected(self, tmp_path, capsys):
        from nutrime.cli import main

        self._seed(tmp_path)
        rc = main(
            [
                "plans", "generate", "--data-dir", str(tmp_path),
                "--meals", "brunch", "--dry-run",
            ]
        )
        assert rc == 2
        assert "unknown meal slot" in capsys.readouterr().out

    def test_show_renders_attribution(self, tmp_path, capsys):
        # Issue #23 on the plan display surface: every rendered recipe carries
        # its source line adjacent to the content.
        from nutrime.cli import main
        from nutrime.paths import default_corpus_dir

        self._seed(tmp_path)
        plan_vault = PlanVault(default_corpus_dir(tmp_path))
        plan_vault.write(
            "pln-cli",
            _plan_fm(plan_id="pln-cli", days=1, meals_planned=1),
            render_plan_body([PlanEntry(1, "dinner", "rcp-d1", "Dinner 1", "quick")]),
        )
        rc = main(["plans", "show", "pln-cli", "--data-dir", str(tmp_path)])
        out = capsys.readouterr().out
        assert rc == 0
        assert "Dinner 1" in out
        assert "Source: TheMealDB (free-tier-attribution)" in out

    def test_show_unknown_plan(self, tmp_path, capsys):
        from nutrime.cli import main

        self._seed(tmp_path)
        rc = main(["plans", "show", "pln-nope", "--data-dir", str(tmp_path)])
        assert rc == 1
        assert "no such plan" in capsys.readouterr().out

    def test_list_shows_newest_first(self, tmp_path, capsys):
        from nutrime.cli import main
        from nutrime.paths import default_corpus_dir

        self._seed(tmp_path)
        plan_vault = PlanVault(default_corpus_dir(tmp_path))
        plan_vault.write(
            "pln-a",
            _plan_fm(plan_id="pln-a", created_at="2026-09-01T00:00:00Z"),
            render_plan_body([]),
        )
        plan_vault.write(
            "pln-b",
            _plan_fm(plan_id="pln-b", created_at="2026-09-07T00:00:00Z"),
            render_plan_body([]),
        )
        rc = main(["plans", "list", "--data-dir", str(tmp_path)])
        out = capsys.readouterr().out
        assert rc == 0
        assert out.index("pln-b") < out.index("pln-a")


class TestSlotProfiles:
    """Slots map to category profiles, not exact tags (see assemble docstring)."""

    @pytest.fixture()
    def mixed(self, tmp_path):
        vault = RecipeVault(tmp_path / "mixed")
        for rid, title, cats in [
            ("rcp-beef", "Beef Main", ["beef"]),
            ("rcp-veg", "Veg Main", ["vegetarian"]),
            ("rcp-cake", "Cake", ["dessert"]),
            ("rcp-eggs", "Eggs", ["breakfast"]),
            ("rcp-slaw", "Slaw", ["side"]),
        ]:
            vault.write(
                rid, _frontmatter(rid, title, categories=cats), _body("@x{1}")
            )
        return vault

    def test_dinner_is_defined_by_exclusion(self, mixed):
        # TheMealDB never emits a "dinner" tag; mains are what's left over.
        pool = candidates_for_slot(mixed, SearchFilters(), "dinner")
        assert {c.recipe_id for c in pool} == {"rcp-beef", "rcp-veg"}

    def test_lunch_and_dinner_share_the_main_profile(self, mixed):
        dinner = {c.recipe_id for c in candidates_for_slot(mixed, SearchFilters(), "dinner")}
        lunch = {c.recipe_id for c in candidates_for_slot(mixed, SearchFilters(), "lunch")}
        assert dinner == lunch

    def test_dessert_matches_positively(self, mixed):
        pool = candidates_for_slot(mixed, SearchFilters(), "dessert")
        assert [c.recipe_id for c in pool] == ["rcp-cake"]

    def test_unknown_slot_falls_back_to_exact_tag(self, mixed):
        assert candidates_for_slot(mixed, SearchFilters(), "brunch") == []
