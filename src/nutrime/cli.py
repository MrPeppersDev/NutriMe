"""Minimal CLI for the deployment shell + first-run baseline intake + inventory.

Subcommands ship with the components that require them; each new sub-commit
adds only the subparser it needs. Current surface:

- ``nutrime init``               — open DBs, apply migrations, ensure tenant row
- ``nutrime intake``             — first-run baseline intake (step 2 s.c. 2.1)
- ``nutrime inventory add``      — add pantry/fridge/freezer items (2.2)
- ``nutrime inventory list``     — show current inventory grouped by location (2.2)
- ``nutrime knowledge sync``     — derive atoms + constraint stub from intake (step 3)
- ``nutrime knowledge list``     — show currently-valid atoms + constraints (step 3)
- ``nutrime recipes fetch``      — seed corpus from an external source (step 4 s.c. 4.1/4.2)
- ``nutrime recipes list``       — show recipes in the local vault (step 4 s.c. 4.1)
- ``nutrime audit list``         — show recent operational audit events (step 5 s.c. 5.1)
- ``nutrime llm ping``           — end-to-end LLM pipeline smoke test (step 5 s.c. 5.2)
- ``nutrime recipes search``     — query the vault with filters + ranking (step 5 s.c. 5.3)
- ``nutrime plans generate``     — assemble a meal plan, one crossing per meal (5.4)
- ``nutrime plans list``         — show plans in the local vault (5.4)
- ``nutrime plans show``         — render a plan with per-recipe attribution (5.4)
- ``nutrime serve``              — localhost web UI prototype (product pull 2026-10-03)
- ``nutrime members``            — household members: list / add / rename / archive (#29)
- ``nutrime backup|restore``     — one-zip backup + safe restore (#34)
- ``nutrime doctor``             — plain-language installation check (#34)
"""

from __future__ import annotations

import argparse
from pathlib import Path

from nutrime import __version__, credstore
from nutrime.app import initialize
from nutrime.intake.baseline import run_baseline_intake
from nutrime.inventory.capture import capture_items
from nutrime.inventory.store import by_location, list_items
from nutrime.knowledge.derivation import sync_from_intake
from nutrime.knowledge.store import list_atoms, list_synthesized_entries
from nutrime.recipes.gutenberg import seed_recipes as gutenberg_seed_recipes
from nutrime.recipes.jsonld import (
    read_urls_file,
    seed_recipes as jsonld_seed_recipes,
)
from nutrime.recipes.myplate_wayback import seed_recipes as myplate_seed_recipes
from nutrime.recipes.nhlbi import seed_recipes as nhlbi_seed_recipes
from nutrime.recipes.search import attribution_line
from nutrime.recipes.store import RecipeVault
from nutrime.recipes.themealdb import TheMealDBClient, seed_recipes
from nutrime.recipes.web import Pacer


def _cmd_init(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    print(f"data_dir:    {app.data_dir}")
    print(f"substrate:   {app.data_dir / 'substrate.db'}")
    print(f"operational: {app.data_dir / 'operational.db'}")
    print(f"tenant_id:   {app.tenant_id}")
    return 0


def _resolve_data_dir(args: argparse.Namespace) -> Path:
    from nutrime.paths import default_data_dir

    return Path(args.data_dir).expanduser() if args.data_dir else default_data_dir()


def _cmd_backup(args: argparse.Namespace) -> int:
    from nutrime.maintenance import create_backup

    try:
        archive = create_backup(
            _resolve_data_dir(args),
            Path(args.out).expanduser() if args.out else None,
        )
    except FileNotFoundError as err:
        print(str(err))
        return 1
    size_mb = archive.stat().st_size / 1_000_000
    print(f"backup written: {archive} ({size_mb:.1f} MB)")
    print("keep a copy somewhere other than this computer (USB drive, another machine)")
    return 0


def _cmd_restore(args: argparse.Namespace) -> int:
    from nutrime.maintenance import RestoreError, read_manifest, restore_backup

    archive = Path(args.archive).expanduser()
    if not archive.exists():
        print(f"no such file: {archive}")
        return 1
    try:
        manifest = read_manifest(archive)
        print(f"backup from {manifest.get('created_at')}: {manifest.get('counts')}")
        outcome = restore_backup(archive, _resolve_data_dir(args), force=args.force)
    except RestoreError as err:
        print(str(err))
        return 2
    except PermissionError as err:
        print(f"a file is in use ({err}). Stop NutriMe first, then restore again.")
        return 2
    if outcome.safety_backup:
        print(f"the data it replaced was saved first: {outcome.safety_backup}")
    print("restored. Start NutriMe as usual.")
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    from nutrime.maintenance import run_doctor

    marks = {"ok": "ok  ", "warn": "WARN", "fail": "FAIL"}
    checks = run_doctor(_resolve_data_dir(args), check_model=not args.skip_model)
    for c in checks:
        print(f"[{marks[c.status]}] {c.name}: {c.detail}")
        if c.fix and c.status != "ok":
            print(f"       fix: {c.fix}")
    failed = any(c.status == "fail" for c in checks)
    print("— all good —" if not any(c.status != "ok" for c in checks)
          else "— needs attention —" if failed else "— working, with suggestions —")
    return 1 if failed else 0


def _member_or_none(app, args: argparse.Namespace) -> str | None:
    """Resolve --member (name or id; default member when omitted).
    Prints the reason and returns None on an unknown member."""
    from nutrime.members import MemberError, resolve_member

    try:
        return resolve_member(
            app.substrate, app.tenant_id, getattr(args, "member", None)
        )
    except MemberError as err:
        print(str(err))
        return None


def _cmd_intake(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    member_id = _member_or_none(app, args)
    if member_id is None:
        return 2
    run_baseline_intake(
        app.substrate,
        app.tenant_id,
        prompter=input,
        emitter=print,
        member_id=member_id,
    )
    return 0


def _cmd_checkin(args: argparse.Namespace) -> int:
    from nutrime.checkins import checkin_history, checkin_status, run_checkin_interactive
    from nutrime.consent import ConsentError

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    member_id = _member_or_none(app, args)
    if member_id is None:
        return 2
    if args.status:
        st = checkin_status(app.substrate, app.tenant_id, member_id)
        if not st.has_profile:
            print("no profile yet — run `nutrime intake` first")
            return 0
        print(("due now" if st.due else f"next due {str(st.due_at)[:10]}")
              + f" (every {st.interval_days} days, {st.interval_source})")
        for h in checkin_history(app.substrate, app.tenant_id, member_id, limit=5):
            print(f"  {h['completed_at'][:10]}  {'; '.join(h.get('changes') or ['no changes'])}")
        return 0
    try:
        result = run_checkin_interactive(
            app.substrate, app.tenant_id, member_id,
            prompter=input, emitter=print, vault=RecipeVault(app.corpus_dir),
        )
    except (ValueError, ConsentError) as err:
        print(str(err))
        return 2
    return 0 if result is not None else 1


def _cmd_members_list(args: argparse.Namespace) -> int:
    from nutrime.intake.store import household_profiles
    from nutrime.members import list_members

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    profiled = household_profiles(app.substrate, app.tenant_id)
    default = app.default_member_id
    for m in list_members(
        app.substrate, app.tenant_id, include_archived=args.all
    ):
        marks = []
        if m.id == default:
            marks.append("default")
        if m.id in profiled:
            marks.append("profile")
        if not m.active:
            marks.append("archived")
        suffix = f"  ({', '.join(marks)})" if marks else ""
        print(f"  {m.display_name:<20} {m.id}{suffix}")
    return 0


def _cmd_members_add(args: argparse.Namespace) -> int:
    from nutrime.members import MemberError, add_member

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    try:
        member = add_member(app.substrate, app.tenant_id, args.name)
    except MemberError as err:
        print(str(err))
        return 2
    print(f"added {member.display_name}  [{member.id}]")
    print(f'  next: nutrime intake --member "{member.display_name}"')
    return 0


def _cmd_members_rename(args: argparse.Namespace) -> int:
    from nutrime.members import MemberError, rename_member, resolve_member

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    try:
        member_id = resolve_member(app.substrate, app.tenant_id, args.member)
        member = rename_member(app.substrate, app.tenant_id, member_id, args.name)
    except MemberError as err:
        print(str(err))
        return 2
    print(f"renamed to {member.display_name}  [{member.id}]")
    return 0


def _cmd_members_archive(args: argparse.Namespace) -> int:
    from nutrime.members import MemberError, archive_member, resolve_member

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    try:
        member_id = resolve_member(app.substrate, app.tenant_id, args.member)
        archive_member(app.substrate, app.tenant_id, member_id)
    except MemberError as err:
        print(str(err))
        return 2
    print(f"archived {args.member} — their history is kept; they leave the picker")
    return 0


def _cmd_inventory_add(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    capture_items(app.substrate, app.tenant_id, prompter=input, emitter=print)
    return 0


def _cmd_inventory_list(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    items = list_items(app.substrate, app.tenant_id)
    if not items:
        print("(no inventory items yet — run `nutrime inventory add`)")
        return 0
    for location, group in sorted(by_location(items).items()):
        print(f"— {location} —")
        for item in group:
            if item.quantity is not None:
                qty = f"{item.quantity:g} {item.unit}"
            else:
                qty = "on hand"
            best_by = f", best by {item.best_by_date}" if item.best_by_date else ""
            notes = f" ({item.notes})" if item.notes else ""
            print(f"  {item.name}: {qty}{best_by}{notes}")
    return 0


def _cmd_knowledge_sync(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    outcome = sync_from_intake(app.substrate, app.tenant_id)
    if outcome.total_atoms_added == 0 and outcome.constraints_added == 0:
        print("(nothing to derive — knowledge model already in sync with intake)")
        return 0
    if outcome.total_atoms_added:
        print(f"Added {outcome.total_atoms_added} atom(s):")
        for atom_type, count in sorted(outcome.atoms_added.items()):
            print(f"  {atom_type}: {count}")
    if outcome.constraints_added:
        print(f"Emitted {outcome.constraints_added} abstracted constraint(s).")
    return 0


def _cmd_knowledge_list(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    atoms = list_atoms(app.substrate, app.tenant_id)
    constraints = list_synthesized_entries(
        app.substrate, app.tenant_id, entry_type="abstracted_constraint"
    )
    if not atoms and not constraints:
        print("(no atoms yet — run `nutrime intake` then `nutrime knowledge sync`)")
        return 0
    by_type: dict[str, list] = {}
    for atom in atoms:
        by_type.setdefault(atom.type, []).append(atom)
    for atom_type, group in sorted(by_type.items()):
        print(f"— {atom_type} ({len(group)}) —")
        for atom in group:
            summary = _atom_summary(atom.type, atom.payload)
            print(f"  {summary}")
    if constraints:
        print(f"— abstracted_constraint ({len(constraints)}) —")
        for entry in constraints:
            print(f"  {entry.payload.get('abstracted_text', '(no text)')}")
    return 0


def _cmd_recipes_fetch(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    vault = RecipeVault(app.corpus_dir)
    pacer = Pacer(delay_s=args.delay)
    if args.source == "themealdb":
        client = TheMealDBClient()
        letters = tuple(args.letters)
        outcome = seed_recipes(
            client, vault, letters=letters, limit=args.limit
        )
    elif args.source == "nhlbi":
        outcome = nhlbi_seed_recipes(vault, pacer=pacer, limit=args.limit)
    elif args.source == "myplate_wayback":
        outcome = myplate_seed_recipes(vault, pacer=pacer, limit=args.limit)
    elif args.source == "gutenberg":
        books = (
            tuple(b.strip() for b in args.books.split(",") if b.strip())
            if args.books
            else None
        )
        outcome = gutenberg_seed_recipes(
            vault, pacer=pacer, books=books, limit=args.limit
        )
    elif args.source == "pinterest":
        from nutrime.recipes.pinterest import (
            MissingTokenError,
            PinterestAuthError,
            PinterestClient,
            resolve_token,
            sync_pins,
        )

        try:
            token = resolve_token()
        except MissingTokenError as err:
            print(str(err))
            return 2
        client = PinterestClient(token=token, pacer=pacer)
        try:
            sync = sync_pins(
                client,
                vault,
                board_name=args.board,
                limit=args.limit,
                pacer=pacer,
            )
        except (PinterestAuthError, ValueError) as err:
            print(str(err))
            return 2
        print(
            f"Pinterest: {sync.pins_seen} pin(s) seen,"
            f" {sync.pins_with_links} with recipe links,"
            f" {sync.pins_without_links} without usable links"
            " (image-only pins stay on the #24 follow-up)."
        )
        outcome = sync.ingest
    elif args.source == "board":
        from nutrime.recipes.pinboard import (
            GalleryDlUnavailable,
            backfill_board,
        )

        if not args.board_url:
            print("--source board requires --board-url <public board URL>")
            return 2
        try:
            backfill = backfill_board(
                args.board_url,
                vault,
                app.data_dir,
                pacer=pacer,
                limit=args.limit,
            )
        except (GalleryDlUnavailable, RuntimeError) as err:
            print(str(err))
            return 2
        print(
            f"Board: {backfill.pins_seen} pin(s) seen,"
            f" {backfill.pins_with_links} with recipe links,"
            f" {backfill.image_only_total} image-only"
            f" ({backfill.image_only_queued} newly queued for vision"
            " extraction)."
        )
        outcome = backfill.ingest
    elif args.source == "urls":
        if not args.urls_file:
            print("--source urls requires --urls-file <path> (one URL per line)")
            return 2
        urls = read_urls_file(Path(args.urls_file).expanduser())
        outcome = jsonld_seed_recipes(
            vault, urls, pacer=pacer, limit=args.limit
        )
    else:
        print(
            f"unknown --source {args.source!r}; wired sources:"
            " themealdb, nhlbi, myplate_wayback, gutenberg, urls,"
            " pinterest, board"
        )
        return 2
    print(
        f"Fetched {outcome.fetched} recipe(s); wrote {outcome.written} new"
        f" recipe file(s) to {vault.root}."
    )
    if outcome.skipped_upstream_ids:
        print(
            f"Skipped {len(outcome.skipped_upstream_ids)} already-ingested"
            " upstream id(s)."
        )
    for url, reason in getattr(outcome, "failures", ()):
        print(f"  ! {url} — {reason}")
    return 0


def _cmd_recipes_list(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    vault = RecipeVault(app.corpus_dir)
    records = vault.list_recipes()
    if not records:
        print(
            "(no recipes yet — run `nutrime recipes fetch` to seed the vault)"
        )
        return 0
    shown = records if args.limit is None else records[: args.limit]
    print(f"— {len(shown)} of {len(records)} recipe(s) —")
    for record in shown:
        fm = record.frontmatter
        title = fm.get("title", "(untitled)")
        cuisine = ", ".join(fm.get("cuisine_tradition_tags", ())) or "-"
        categories = ", ".join(fm.get("meal_categories", ())) or "-"
        allergens = ", ".join(fm.get("top_allergens_present", ())) or "none"
        print(f"  {record.recipe_id}")
        print(f"    title:     {title}")
        print(f"    cuisine:   {cuisine}")
        print(f"    category:  {categories}")
        print(f"    allergens: {allergens}")
        print(f"    {attribution_line(fm)}")
    return 0


def _cmd_recipes_search(args: argparse.Namespace) -> int:
    from nutrime.knowledge.store import list_synthesized_entries
    from nutrime.recipes.search import (
        SearchFilters,
        filters_from_constraints,
        search,
    )

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    vault = RecipeVault(app.corpus_dir)

    def _split(raw: str | None) -> frozenset[str]:
        if not raw:
            return frozenset()
        return frozenset(t.strip() for t in raw.split(",") if t.strip())

    filters = SearchFilters(
        query=args.query,
        exclude_allergens=_split(args.exclude_allergen),
        exclude_ingredients=_split(args.exclude_ingredient),
        max_total_time_min=args.max_time,
        meal_category=args.category,
        cuisine=args.cuisine,
        sources=_split(getattr(args, "source_filter", None)),
    )
    applied: list[str] = []
    # V1: cook history always consults on the search surface too.
    from dataclasses import replace as _history_replace

    from nutrime.feedback import experience_summaries

    experience = experience_summaries(app.substrate, app.tenant_id)
    if experience:
        filters = _history_replace(filters, experience=experience)
    if args.apply_constraints:
        entries = list_synthesized_entries(
            app.substrate, app.tenant_id, entry_type="abstracted_constraint"
        )
        filters = filters_from_constraints(entries, base=filters)
        applied.append(f"{len(entries)} abstracted constraint(s)")
    if args.use_inventory:
        items = list_items(app.substrate, app.tenant_id)
        from dataclasses import replace as _replace

        filters = _replace(
            filters,
            on_hand=frozenset(item.name for item in items),
        )
        applied.append(f"{len(items)} inventory item(s)")
    if applied:
        print(f"(applying {', '.join(applied)})")

    results = search(vault, filters, limit=args.limit)
    if not results:
        print("(no recipes matched — relax a filter or fetch more sources)")
        return 0
    print(f"— {len(results)} result(s) —")
    for rank, result in enumerate(results, start=1):
        time_str = (
            f"{result.total_time_min} min"
            if result.total_time_min is not None
            else "time unknown"
        )
        allergens = ", ".join(result.allergens) or "none detected"
        print(f"{rank:>2}. {result.title}  [{result.recipe_id}]")
        print(f"    {time_str} · allergens: {allergens} · score {result.score:g}")
        if result.on_hand_matches:
            print(f"    uses on-hand: {', '.join(result.on_hand_matches)}")
        if result.prefer_matches:
            print(f"    matches preference: {', '.join(result.prefer_matches)}")
        print(f"    {result.attribution}")
    return 0


def _cmd_llm_ping(args: argparse.Namespace) -> int:
    from nutrime.llm.base import ChatMessage, LlmRequest, MissingApiKeyError, ProviderError
    from nutrime.llm.phi import LLM_PING

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    client = _build_llm_client(app, args.provider, args.model)
    if client is None:
        return 2
    request = LlmRequest(
        query_type=LLM_PING,
        messages=(
            ChatMessage(role="user", content="Reply with the single word: pong"),
        ),
        max_tokens=16,
    )
    try:
        response = client.complete(request)
    except MissingApiKeyError as exc:
        print(f"config error: {exc}")
        return 2
    except ProviderError as exc:
        print(f"provider error ({exc.outcome}): {exc.detail}")
        print("(the failed call was audit-logged — see `nutrime audit list`)")
        return 1
    print(f"provider:   {response.provider} ({response.model})")
    print(f"response:   {response.text.strip()}")
    print(
        f"tokens:     {response.prompt_tokens} in / {response.completion_tokens} out"
    )
    print(f"latency:    {response.latency_ms} ms")
    print(f"audit row:  {response.llm_request_log_id} (request {response.request_id})")
    return 0


def _cmd_audit_list(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    events = app.audit.events(event_kind=args.kind, limit=args.limit)
    if not events:
        print("(no audit events yet)")
        return 0
    print(f"— {len(events)} most recent event(s), newest first —")
    for event in events:
        subkind = f"/{event.event_subkind}" if event.event_subkind else ""
        request = f"  request={event.request_id}" if event.request_id else ""
        print(f"  {event.recorded_at}  {event.event_kind}{subkind}"
              f"  actor={event.actor}{request}")
        summary = ", ".join(
            f"{key}={value}" for key, value in sorted(event.payload.items())
        )
        if len(summary) > 120:
            summary = summary[:117] + "..."
        print(f"    {summary}")
    return 0


def _atom_summary(atom_type: str, payload: dict) -> str:
    if atom_type == "clinical_disclosure":
        return (
            f"{payload.get('disclosure_type', '?')}: "
            f"{payload.get('disclosure_text', '?')}"
        )
    if atom_type == "preference_statement":
        return (
            f"{payload.get('preference_type', '?')}: "
            f"{payload.get('subject_text', '?')}"
        )
    if atom_type == "screener_result":
        interp = payload.get("score_interpretation", "?")
        score = payload.get("score", "?")
        instrument = payload.get("instrument_id", "?")
        return f"{instrument}: score {score} → {interp}"
    return f"{atom_type}"


def _plan_base_filters(app, args) -> tuple[object, list[str]]:
    """Build the shared search filters for every slot + a note of what applied."""
    from nutrime.plans.service import plan_base_filters

    return plan_base_filters(
        app,
        max_time=args.max_time,
        apply_constraints=args.apply_constraints,
        use_inventory=args.use_inventory,
    )


def _build_llm_client(app, provider_choice: str, model: str | None):
    """Local-first provider stack (direction reset 2026-10-06).

    Default: Ollama only — the product runs with local models, no key.
    ``--provider cloud`` opts into Anthropic for PHI-free work (the
    local-mandatory routing in LlmClient still refuses PHI→cloud).
    """
    from nutrime.llm.client import LlmClient
    from nutrime.llm.ollama import (
        DEFAULT_MODEL,
        INSTALL_COMMAND,
        OllamaProvider,
        is_available,
    )

    if provider_choice == "cloud":
        from nutrime.llm.anthropic import AnthropicProvider

        cloud = (
            AnthropicProvider(model=model) if model else AnthropicProvider()
        )
        providers = (
            (OllamaProvider(), cloud) if is_available() else (cloud,)
        )
    else:
        if not is_available():
            from nutrime.plans.service import LOCAL_MODEL_SETUP

            print(LOCAL_MODEL_SETUP)
            return None
        providers = (OllamaProvider(model=model or ""),)
    return LlmClient(providers, app.rule_engine, app.audit)


def _cmd_plans_generate(args: argparse.Namespace) -> int:
    from nutrime.llm.base import MissingApiKeyError
    from nutrime.plans.assemble import (
        MEAL_SLOTS,
        PlanSpec,
        candidates_for_slot,
    )

    slots = tuple(s.strip().lower() for s in args.meals.split(",") if s.strip())
    unknown = [s for s in slots if s not in MEAL_SLOTS]
    if unknown:
        print(f"unknown meal slot(s): {', '.join(unknown)}")
        print(f"known slots: {', '.join(MEAL_SLOTS)}")
        return 2

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    vault = RecipeVault(app.corpus_dir)

    try:
        spec = PlanSpec(
            days=args.days,
            slots=slots,
            servings=args.servings,
            household_note=args.household or "",
            candidates_per_slot=args.candidates,
        )
    except ValueError as exc:
        print(f"invalid plan spec: {exc}")
        return 2

    filters, applied = _plan_base_filters(app, args)
    if applied:
        print(f"(applying {', '.join(applied)})")

    print(
        f"plan: {spec.days} day(s) x {len(spec.slots)} slot(s)"
        f" = {spec.crossings} LLM crossing(s)"
    )
    import random

    seed = args.seed if args.seed is not None else random.randrange(2**31)
    print(f"(candidate seed {seed} — pass --seed {seed} to reproduce these pools)")

    if args.dry_run:
        print("(dry run — nothing crosses)")
        for slot in spec.slots:
            pool = candidates_for_slot(
                vault,
                filters,
                slot,
                limit=spec.candidates_per_slot,
                rng=random.Random(seed),
            )
            preview = ", ".join(c.title for c in pool[:5]) or "(none)"
            print(f"  {slot}: {len(pool)} candidate(s) — {preview}")
        return 0

    client = _build_llm_client(app, args.provider, args.model)
    if client is None:
        return 2

    def _progress(outcome) -> None:
        label = f"  day {outcome.day} {outcome.slot}"
        if outcome.error:
            print(f"{label}: unfilled — {outcome.error}")
        else:
            print(f"{label}: {outcome.entry.title}  [{outcome.entry.recipe_id}]")

    from nutrime.plans.service import PlanRefusedError, generate_and_store

    try:
        plan_id, path, plan = generate_and_store(
            app, client, spec, filters, applied,
            model_hint=args.model, on_progress=_progress, seed=seed,
        )
    except PlanRefusedError as exc:
        print(str(exc))
        return 3
    except MissingApiKeyError as exc:
        print(f"config error: {exc}")
        return 2

    print(f"— plan {plan_id} written to {path} —")
    print(f"{plan.filled} of {spec.crossings} slot(s) filled")
    if plan.failures:
        print(
            f"({len(plan.failures)} slot(s) unfilled — every failed crossing is"
            " audit-logged; see `nutrime audit list`)"
        )
    return 0


def _cmd_plans_list(args: argparse.Namespace) -> int:
    from nutrime.plans.store import PlanVault

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    records = PlanVault(app.corpus_dir).list_plans()[: args.limit]
    if not records:
        print("(no plans yet — run `nutrime plans generate`)")
        return 0
    print(f"— {len(records)} plan(s), newest first —")
    for record in records:
        fm = record.frontmatter
        slots = ", ".join(str(s) for s in fm.get("meal_slots", ()) or ())
        print(f"{record.plan_id}")
        print(
            f"    {fm.get('created_at', '?')} · {fm.get('days', '?')} day(s)"
            f" · {slots or 'no slots'} · {fm.get('meals_planned', 0)} meal(s)"
            f" · {fm.get('model', 'unknown model')}"
        )
    return 0


def _cmd_plans_show(args: argparse.Namespace) -> int:
    from nutrime.plans.store import PlanVault

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    plan_vault = PlanVault(app.corpus_dir)
    if not plan_vault.exists(args.plan_id):
        print(f"no such plan: {args.plan_id}")
        return 1
    record = plan_vault.read(args.plan_id)
    vault = RecipeVault(app.corpus_dir)
    fm = record.frontmatter

    print(f"plan {record.plan_id}")
    print(
        f"  {fm.get('created_at', '?')} · {fm.get('days', '?')} day(s)"
        f" · {fm.get('model', 'unknown model')}"
    )
    constraints = fm.get("constraints_applied", ()) or ()
    if constraints:
        print(f"  applied: {', '.join(str(c) for c in constraints)}")
    log_ids = fm.get("llm_request_log_ids", ()) or ()
    print(f"  audit rows: {len(log_ids)} crossing(s) — see `nutrime audit list`")
    print()

    for entry in record.entries():
        header = f"Day {entry.day} · {entry.slot}"
        if not entry.filled:
            print(f"{header}: (unfilled) {entry.note}".rstrip())
            print()
            continue
        print(f"{header}: {entry.title}  [{entry.recipe_id}]")
        if entry.note:
            print(f"    {entry.note}")
        # Attribution renders adjacent to recipe content on every display
        # surface (issue #23) — this is the plan-side surface.
        try:
            recipe = vault.read(entry.recipe_id)
        except OSError:
            print("    Source: (recipe no longer in vault)")
        else:
            print(f"    {attribution_line(recipe.frontmatter)}")
        print()
    return 0


def _cmd_recipes_crawl(args: argparse.Namespace) -> int:
    from nutrime.recipes.crawl import (
        DEFAULT_SOURCES_PATH,
        SOURCES_FILE,
        STATE_FILE,
        CrawlConfigError,
        crawl_sources,
        load_sources,
    )

    if args.example:
        print(DEFAULT_SOURCES_PATH.read_text(encoding="utf-8"), end="")
        return 0
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    custom = app.data_dir / SOURCES_FILE
    try:
        sources = load_sources(custom)
    except CrawlConfigError as err:
        print(str(err))
        return 2
    origin = str(custom) if custom.exists() else "the bundled default list"
    if args.list:
        print(f"crawl sources from {origin}:")
        for s in sources.values():
            print(f"  {s.key:<22} {s.kind:<9} {s.name}  (budget {s.max_pages}/run)")
        return 0
    if not sources:
        print(f"no enabled sources in {origin}")
        return 2
    if args.source:
        unknown = [k for k in args.source if k not in sources]
        if unknown:
            print(f"unknown source(s): {', '.join(unknown)};"
                  f" configured: {', '.join(sorted(sources))}")
            return 2
        chosen = [sources[k] for k in args.source]
    else:
        chosen = list(sources.values())
    print(f"crawling {len(chosen)} source(s) from {origin}; each site's"
          " robots.txt decides whether NutriMe may fetch it")

    def _report(url: str, result: str) -> None:
        if args.verbose or result not in ("known",):
            print(f"  {result:<14} {url}")

    outcomes = crawl_sources(
        RecipeVault(app.corpus_dir),
        chosen,
        app.data_dir / STATE_FILE,
        max_pages=args.max_pages,
        dry_run=args.dry_run,
        on_page=_report,
    )
    verb = "would fetch" if args.dry_run else "fetched"
    for o in outcomes:
        if o.listings_blocked and not o.listings_fetched:
            print(f"— {o.source}: skipped — its robots.txt doesn't allow NutriMe's crawler")
            continue
        print(
            f"— {o.source}: {o.discovered} found; {verb} {o.fetched};"
            f" wrote {o.written}; {o.already_known} already known;"
            f" {o.not_recipes} not recipes; {o.blocked_by_robots} blocked by"
            f" robots.txt; {len(o.failures)} failed"
            + ("; budget reached — run again to continue" if o.budget_exhausted else "")
        )
    if not args.dry_run and any(o.written for o in outcomes):
        # New recipes are vetted straight away so junk and cross-source
        # duplicates never surface in search.
        from nutrime.recipes.vetting import vet_vault

        vetted = vet_vault(RecipeVault(app.corpus_dir))
        print(
            f"vetted new recipes: {vetted.quarantined} hidden as junk,"
            f" {vetted.duplicates} duplicate(s) hidden, {vetted.flagged} flagged"
        )
    return 0


def _cmd_recipes_vet(args: argparse.Namespace) -> int:
    from nutrime.recipes.vetting import vet_vault

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    vault = RecipeVault(app.corpus_dir)
    if args.list_quarantined:
        shown = 0
        for record in vault.iter_recipes():
            status = record.frontmatter.get("vetting_status")
            if status == "quarantined":
                shown += 1
                print(f"  {record.recipe_id}")
                print(f"    title:  {record.frontmatter.get('title')}")
                print(f"    reason: {record.frontmatter.get('vetting_reason')}")
            elif status == "duplicate":
                shown += 1
                print(f"  {record.recipe_id}")
                print(f"    title:  {record.frontmatter.get('title')}")
                print(f"    duplicate of: {record.frontmatter.get('duplicate_of')}")
        print(f"— {shown} hidden recipe(s) (quarantined or duplicate) —")
        return 0
    if args.list_flagged:
        shown = 0
        for record in vault.iter_recipes():
            flags = record.frontmatter.get("vetting_flags") or []
            if flags:
                shown += 1
                print(f"  {record.recipe_id}  {record.frontmatter.get('title')}")
                print(f"    flags: {', '.join(flags)}")
        print(f"— {shown} flagged recipe(s) (still searchable) —")
        return 0
    outcome = vet_vault(vault, revet=args.revet)
    print(
        f"Examined {outcome.examined}; normalized {outcome.titles_normalized}"
        f" title(s); quarantined {outcome.quarantined};"
        f" flagged {outcome.flagged} for review;"
        f" {outcome.duplicates} duplicate(s) hidden;"
        f" allergen tags added on {outcome.allergens_added};"
        f" {outcome.already_vetted} already vetted."
    )
    return 0


def _cmd_meals_cooked(args: argparse.Namespace) -> int:
    from nutrime.consent import ConsentError
    from nutrime.feedback import (
        record_cooking_experience,
        record_meal_event,
        record_time_feedback,
    )

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    vault = RecipeVault(app.corpus_dir)
    if not vault.exists(args.recipe_id):
        print(f"no such recipe: {args.recipe_id}")
        return 1
    record = vault.read(args.recipe_id)
    title = str(record.frontmatter.get("title", "(untitled)"))
    member_id = _member_or_none(app, args)
    if member_id is None:
        return 2
    try:
        meal_event_id = record_meal_event(
            app.substrate,
            app.tenant_id,
            member_id=member_id,
            recipe_id=args.recipe_id,
            recipe_title=title,
            plan_id=args.plan_id,
        )
        print(f"cooked: {title}  [{meal_event_id}]")
        if args.ease is not None and args.enjoyment is not None:
            record_cooking_experience(
                app.substrate,
                app.tenant_id,
                member_id=member_id,
                meal_event_id=meal_event_id,
                ease_rating=args.ease,
                enjoyment_rating=args.enjoyment,
                freetext_notes=args.notes,
            )
            print("  cooking-experience feedback recorded")
        if args.actual_minutes is not None:
            estimated = record.frontmatter.get("estimated_total_time_min")
            record_time_feedback(
                app.substrate,
                app.tenant_id,
                member_id=member_id,
                meal_event_id=meal_event_id,
                estimated_time_min=(
                    int(estimated) if estimated is not None else None
                ),
                actual_time_min=args.actual_minutes,
            )
            print("  time feedback recorded")
    except ConsentError as err:
        print(str(err))
        return 2
    except ValueError as err:
        print(str(err))
        return 2
    return 0


def _cmd_meals_feel(args: argparse.Namespace) -> int:
    from nutrime.consent import ConsentError
    from nutrime.feedback import meal_history, record_body_response

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    member_id = _member_or_none(app, args)
    if member_id is None:
        return 2
    meal_event_id = args.meal_event_id
    if meal_event_id is None:
        history = meal_history(app.substrate, app.tenant_id, limit=1)
        if not history:
            print("(no cooked meals yet — `nutrime meals cooked <recipe-id>`)")
            return 1
        meal_event_id = history[0].meal_event_id
        print(f"(latest meal: {history[0].recipe_title})")
    try:
        record_body_response(
            app.substrate,
            app.tenant_id,
            member_id=member_id,
            meal_event_id=meal_event_id,
            freetext_response=args.response,
            energy_rating=args.energy,
            digestion_rating=args.digestion,
            fullness_rating=args.fullness,
            mood_rating=args.mood,
        )
    except (ConsentError, ValueError) as err:
        print(str(err))
        return 2
    print("body-response feedback recorded")
    return 0


def _cmd_meals_history(args: argparse.Namespace) -> int:
    from nutrime.feedback import meal_history

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    member_id = None
    if args.member:
        member_id = _member_or_none(app, args)
        if member_id is None:
            return 2
    entries = meal_history(
        app.substrate, app.tenant_id, limit=args.limit, member_id=member_id
    )
    if not entries:
        print("(no cooked meals yet)")
        return 0
    for entry in entries:
        line = f"  {entry.cooked_at}  {entry.recipe_title}"
        details = []
        if entry.ease_rating:
            details.append(
                f"ease {entry.ease_rating}/5, fun {entry.enjoyment_rating}/5"
            )
        if entry.actual_time_min:
            delta = (
                f" ({entry.time_delta_min:+d} vs estimate)"
                if entry.time_delta_min is not None
                else ""
            )
            details.append(f"{entry.actual_time_min} min{delta}")
        if entry.body_response:
            details.append(f'felt: "{entry.body_response}"')
        if details:
            line += "  — " + "; ".join(details)
        print(line)
    return 0


def _cmd_consent_list(args: argparse.Namespace) -> int:
    from nutrime.consent import list_current

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    member_id = None
    if args.member:
        member_id = _member_or_none(app, args)
        if member_id is None:
            return 2
    for record in list_current(app.substrate, app.tenant_id, member_id=member_id):
        state = "granted" if record.granted else "declined"
        retro = " (retroactive)" if record.retroactive else ""
        scope = ""
        if member_id:
            scope = "  [own]" if record.subject_user == member_id else "  [household]"
        print(
            f"  {record.data_category:>24} / {record.purpose:<22}"
            f" {state}{retro} — {record.granted_at}{scope}"
        )
    return 0


def _cmd_consent_set(args: argparse.Namespace) -> int:
    from nutrime.consent import record_decision

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    member_id = None
    if args.member:
        member_id = _member_or_none(app, args)
        if member_id is None:
            return 2
    try:
        consent_id = record_decision(
            app.substrate,
            app.tenant_id,
            data_category=args.category,
            purpose=args.purpose,
            granted=args.decision == "grant",
            note=args.note,
            member_id=member_id,
        )
    except ValueError as err:
        print(str(err))
        return 2
    print(f"recorded {consent_id}: {args.category}/{args.purpose} {args.decision}")
    return 0


def _cmd_grocery_build(args: argparse.Namespace) -> int:
    from nutrime.grocery.build import (
        build_grocery_list,
        render_markdown,
        render_text,
    )
    from nutrime.inventory.store import list_items
    from nutrime.plans.store import PlanVault

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    plan_vault = PlanVault(app.corpus_dir)

    plan_id = args.plan_id
    if plan_id is None:
        plans = plan_vault.list_plans()
        if not plans:
            print("(no plans yet — run `nutrime plans generate`)")
            return 1
        plan_id = plans[0].plan_id  # list_plans is newest-first
    if not plan_vault.exists(plan_id):
        print(f"no such plan: {plan_id}")
        return 1

    inventory = [
        item.name for item in list_items(app.substrate, app.tenant_id)
    ]
    groceries = build_grocery_list(
        plan_vault.read(plan_id),
        RecipeVault(app.corpus_dir),
        inventory_names=inventory,
    )
    render = render_markdown if args.format == "markdown" else render_text
    text = render(groceries)
    if args.out:
        out_path = Path(args.out).expanduser()
        out_path.write_text(text, encoding="utf-8")
        print(f"wrote {out_path}")
    else:
        print(text, end="")
    return 0


def _cmd_pinterest_connect(args: argparse.Namespace) -> int:
    from nutrime.recipes.pinterest import PinterestAuthError, connect_interactive

    client_id = args.client_id or input("Pinterest app ID: ").strip()
    client_secret = args.client_secret or input("Pinterest app secret: ").strip()
    if not client_id or not client_secret:
        print("both the app ID and secret are required")
        return 2
    try:
        connect_interactive(client_id, client_secret, port=args.port)
    except PinterestAuthError as err:
        print(str(err))
        return 1
    except OSError as err:
        print(f"connect failed: {err}")
        return 1
    return 0


def _cmd_pinterest_refresh(args: argparse.Namespace) -> int:
    from nutrime.recipes.pinterest import (
        MissingTokenError,
        PinterestAuthError,
        refresh_access_token,
    )

    try:
        refresh_access_token()
    except (MissingTokenError, PinterestAuthError) as err:
        print(str(err))
        return 1
    print(f"Access token refreshed and stored in the {credstore.backend_name()}.")
    return 0


def _cmd_pinterest_status(args: argparse.Namespace) -> int:
    from nutrime.recipes.pinterest import has_token

    if has_token():
        print("connected (access token present)")
        return 0
    print("not connected — run `nutrime pinterest connect`")
    return 1


def _cmd_serve(args: argparse.Namespace) -> int:
    from nutrime.webui import serve

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    server = serve(data_dir=data_dir, host=args.host, port=args.port)
    print(f"NutriMe web UI: http://{args.host}:{args.port}/")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    finally:
        server.server_close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nutrime")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser(
        "init",
        help="Open DBs, apply migrations, and ensure the tenant row.",
    )
    init.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    init.set_defaults(func=_cmd_init)

    intake = subparsers.add_parser(
        "intake",
        help="Run first-run baseline intake (screener trio + demographics).",
    )
    intake.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    intake.add_argument("--member", default=None, help="Household member (name or id). Default: the first member.")
    intake.set_defaults(func=_cmd_intake)

    checkin = subparsers.add_parser(
        "checkin",
        help="Periodic 5-15 minute check-in that revises your profile.",
    )
    checkin.add_argument("--status", action="store_true", help="Show when the next one is due.")
    checkin.add_argument("--member", default=None, help="Household member (name or id).")
    checkin.add_argument("--data-dir")
    checkin.set_defaults(func=_cmd_checkin)

    backup = subparsers.add_parser(
        "backup",
        help="Save everything (databases, recipes, plans) to one zip file (#34).",
    )
    backup.add_argument("--out", default=None, help="Folder for the zip (default: <data dir>/backups).")
    backup.add_argument("--data-dir")
    backup.set_defaults(func=_cmd_backup)

    restore = subparsers.add_parser(
        "restore", help="Restore a backup zip (stop NutriMe first)."
    )
    restore.add_argument("archive", help="Path to a nutrime-backup-*.zip")
    restore.add_argument(
        "--force", action="store_true",
        help="Replace existing data (a safety backup is taken first).",
    )
    restore.add_argument("--data-dir")
    restore.set_defaults(func=_cmd_restore)

    doctor = subparsers.add_parser(
        "doctor", help="Check the installation and say how to fix anything wrong."
    )
    doctor.add_argument(
        "--skip-model", action="store_true", help="Don't check the local model."
    )
    doctor.add_argument("--data-dir")
    doctor.set_defaults(func=_cmd_doctor)

    members = subparsers.add_parser(
        "members",
        help="Household members — one shared device, a profile per person (#29).",
    )
    members_sub = members.add_subparsers(dest="members_command", required=True)
    mb_list = members_sub.add_parser("list", help="Show household members.")
    mb_list.add_argument("--all", action="store_true", help="Include archived.")
    mb_list.add_argument("--data-dir")
    mb_list.set_defaults(func=_cmd_members_list)
    mb_add = members_sub.add_parser("add", help="Add a household member.")
    mb_add.add_argument("name")
    mb_add.add_argument("--data-dir")
    mb_add.set_defaults(func=_cmd_members_add)
    mb_rename = members_sub.add_parser("rename", help="Rename a member.")
    mb_rename.add_argument("member", help="Current name or id.")
    mb_rename.add_argument("name", help="New name.")
    mb_rename.add_argument("--data-dir")
    mb_rename.set_defaults(func=_cmd_members_rename)
    mb_archive = members_sub.add_parser(
        "archive", help="Archive a member (history kept, never deleted)."
    )
    mb_archive.add_argument("member", help="Name or id.")
    mb_archive.add_argument("--data-dir")
    mb_archive.set_defaults(func=_cmd_members_archive)

    inventory = subparsers.add_parser(
        "inventory",
        help="Manage pantry/fridge/freezer inventory (add-many + list).",
    )
    inventory_sub = inventory.add_subparsers(dest="inventory_command", required=True)

    inv_add = inventory_sub.add_parser("add", help="Add items to the inventory.")
    inv_add.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    inv_add.set_defaults(func=_cmd_inventory_add)

    inv_list = inventory_sub.add_parser(
        "list", help="Show current inventory grouped by location."
    )
    inv_list.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    inv_list.set_defaults(func=_cmd_inventory_list)

    knowledge = subparsers.add_parser(
        "knowledge",
        help="Derive + inspect the knowledge model (atoms + constraint stub).",
    )
    knowledge_sub = knowledge.add_subparsers(
        dest="knowledge_command", required=True
    )

    kn_sync = knowledge_sub.add_parser(
        "sync",
        help="Derive atoms + abstracted constraints from intake data (idempotent).",
    )
    kn_sync.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    kn_sync.set_defaults(func=_cmd_knowledge_sync)

    kn_list = knowledge_sub.add_parser(
        "list",
        help="Show currently-valid atoms + abstracted constraints.",
    )
    kn_list.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    kn_list.set_defaults(func=_cmd_knowledge_list)

    recipes = subparsers.add_parser(
        "recipes",
        help="Seed + inspect the recipe corpus vault (step 4).",
    )
    recipes_sub = recipes.add_subparsers(dest="recipes_command", required=True)

    rec_fetch = recipes_sub.add_parser(
        "fetch",
        help="Fetch recipes from a seed source and write them to the vault.",
    )
    rec_fetch.add_argument(
        "--source",
        default="themealdb",
        help=(
            "Seed source: themealdb (4.1), nhlbi or myplate_wayback (4.2),"
            " gutenberg (4.3), urls (4.4 schema.org JSON-LD scrape),"
            " pinterest (board sync via API, #24),"
            " board (public-board backfill via gallery-dl, #24)."
        ),
    )
    rec_fetch.add_argument(
        "--board-url",
        default=None,
        help=(
            "For --source board: public Pinterest board URL"
            " (pin.it short links are followed)."
        ),
    )
    rec_fetch.add_argument(
        "--board",
        default=None,
        help=(
            "For --source pinterest: sync only the named board"
            " (default: all pins on the account)."
        ),
    )
    rec_fetch.add_argument(
        "--urls-file",
        default=None,
        help=(
            "For --source urls: file with one recipe-page URL per line"
            " (# comments allowed) — e.g. links from a Pinterest export."
        ),
    )
    rec_fetch.add_argument(
        "--books",
        default=None,
        help=(
            "Comma-separated Gutenberg book keys"
            " (beeton,farmer,forme_of_cury,golden_age; default: all)."
        ),
    )
    rec_fetch.add_argument(
        "--letters",
        default="a",
        help="Letters to iterate for TheMealDB search.php?f=<letter> (default: a).",
    )
    rec_fetch.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Cap the number of writes (default: no cap).",
    )
    rec_fetch.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Politeness delay in seconds between HTTP requests (default: 1.0).",
    )
    rec_fetch.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    rec_fetch.set_defaults(func=_cmd_recipes_fetch)

    rec_list = recipes_sub.add_parser(
        "list",
        help="Show recipes in the vault with their headline frontmatter fields.",
    )
    rec_list.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Show at most N recipes (default: show all).",
    )
    rec_list.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    rec_list.set_defaults(func=_cmd_recipes_list)

    rec_search = recipes_sub.add_parser(
        "search",
        help="Query the vault: filters + on-hand/preference ranking (5.3).",
    )
    rec_search.add_argument(
        "--query", default=None, help="Substring match on recipe title."
    )
    rec_search.add_argument(
        "--exclude-allergen",
        default=None,
        help="Comma-separated top-9 allergens to hard-block.",
    )
    rec_search.add_argument(
        "--exclude-ingredient",
        default=None,
        help="Comma-separated ingredient terms to exclude.",
    )
    rec_search.add_argument(
        "--max-time",
        type=int,
        default=None,
        help=(
            "Max estimated total minutes (recipes without a time estimate are"
            " excluded when set)."
        ),
    )
    rec_search.add_argument(
        "--category", default=None, help="Meal category filter (exact tag)."
    )
    rec_search.add_argument(
        "--cuisine", default=None, help="Cuisine tag filter (exact tag)."
    )
    rec_search.add_argument(
        "--source-filter",
        default=None,
        help=(
            "Comma-separated source collections: pins, themealdb, myplate,"
            " nhlbi, historical."
        ),
    )
    rec_search.add_argument(
        "--use-inventory",
        action="store_true",
        help="Rank recipes that use what's on hand higher.",
    )
    rec_search.add_argument(
        "--apply-constraints",
        action="store_true",
        help=(
            "Apply the knowledge model's abstracted constraints"
            " (avoids -> hard-block, prefers -> boost)."
        ),
    )
    rec_search.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Show at most N results (default: 10).",
    )
    rec_search.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    rec_search.set_defaults(func=_cmd_recipes_search)

    rec_crawl = recipes_sub.add_parser(
        "crawl",
        help=(
            "Crawl major public recipe sites + Pinterest top food pins"
            " (robots.txt decides per site; paced, attributed) (#32)."
        ),
    )
    rec_crawl.add_argument(
        "--source", action="append", default=None,
        help="Source key from crawl_sources.toml (repeatable; default: all).",
    )
    rec_crawl.add_argument(
        "--max-pages", type=int, default=None,
        help="Fetch budget per source this run (default: the source's max_pages).",
    )
    rec_crawl.add_argument(
        "--dry-run", action="store_true",
        help="Discover and list what would be fetched; fetch no recipe pages.",
    )
    rec_crawl.add_argument(
        "--example", action="store_true",
        help="Print the bundled source list (a starting point for crawl_sources.toml).",
    )
    rec_crawl.add_argument(
        "--list", action="store_true", help="Show the sources a run would use."
    )
    rec_crawl.add_argument("--verbose", action="store_true")
    rec_crawl.add_argument("--data-dir")
    rec_crawl.set_defaults(func=_cmd_recipes_crawl)

    rec_vet = recipes_sub.add_parser(
        "vet",
        help=(
            "Normalize titles, quarantine junk, flag quality issues, reconcile"
            " allergen tags, hide cross-source duplicates (idempotent)."
        ),
    )
    rec_vet.add_argument(
        "--revet", action="store_true", help="Re-examine already-vetted rows."
    )
    rec_vet.add_argument(
        "--list-quarantined",
        action="store_true",
        help="Show hidden entries (quarantined + duplicates) instead of running the pass.",
    )
    rec_vet.add_argument(
        "--list-flagged",
        action="store_true",
        help="Show entries flagged for review (still searchable).",
    )
    rec_vet.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    rec_vet.set_defaults(func=_cmd_recipes_vet)

    audit = subparsers.add_parser(
        "audit",
        help="Inspect the operational audit trail (op_event_log).",
    )
    audit_sub = audit.add_subparsers(dest="audit_command", required=True)

    aud_list = audit_sub.add_parser(
        "list",
        help="Show recent audit events, newest first.",
    )
    aud_list.add_argument(
        "--kind",
        choices=("audit", "epistemic_trail", "system"),
        default=None,
        help="Filter by event kind (default: all kinds).",
    )
    aud_list.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Show at most N events (default: 20).",
    )
    aud_list.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    aud_list.set_defaults(func=_cmd_audit_list)

    llm = subparsers.add_parser(
        "llm",
        help="LLM provider layer (step 5 s.c. 5.2).",
    )
    llm_sub = llm.add_subparsers(dest="llm_command", required=True)

    llm_ping = llm_sub.add_parser(
        "ping",
        help=(
            "Send a tiny PHI-free request through the full pipeline"
            " (envelope -> rules -> provider -> audit log)."
        ),
    )
    llm_ping.add_argument(
        "--provider",
        choices=("local", "cloud"),
        default="local",
        help="local (Ollama, default) or cloud opt-in (PHI-free only).",
    )
    llm_ping.add_argument(
        "--model",
        default=None,
        help="Model override (default: qwen3:8b local / claude-opus-4-8 cloud).",
    )
    llm_ping.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    llm_ping.set_defaults(func=_cmd_llm_ping)

    plans = subparsers.add_parser(
        "plans",
        help="Meal-plan assembly (step 5 s.c. 5.4).",
    )
    plans_sub = plans.add_subparsers(dest="plans_command", required=True)

    pl_gen = plans_sub.add_parser(
        "generate",
        help=(
            "Assemble a plan of X meals across Y days — one audited LLM"
            " crossing per meal, selecting only from the licensed corpus."
        ),
    )
    pl_gen.add_argument(
        "--days", type=int, default=7, help="Number of days to plan (default: 7)."
    )
    pl_gen.add_argument(
        "--meals",
        default="dinner",
        help=(
            "Comma-separated meal slots per day"
            " (default: dinner; e.g. breakfast,lunch,dinner)."
        ),
    )
    pl_gen.add_argument(
        "--servings", type=int, default=2, help="Servings per meal (default: 2)."
    )
    pl_gen.add_argument(
        "--household",
        default=None,
        help="Free-text household context in place of a plain servings count.",
    )
    pl_gen.add_argument(
        "--candidates",
        type=int,
        default=12,
        help="Candidate recipes offered per slot (default: 12).",
    )
    pl_gen.add_argument(
        "--max-time",
        type=int,
        default=None,
        help=(
            "Max estimated total minutes per meal (recipes without a time"
            " estimate are excluded when set)."
        ),
    )
    pl_gen.add_argument(
        "--use-inventory",
        action="store_true",
        help="Rank recipes that use what's on hand higher.",
    )
    pl_gen.add_argument(
        "--apply-constraints",
        action="store_true",
        help=(
            "Apply the knowledge model's abstracted constraints"
            " (avoids -> hard-block, prefers -> boost)."
        ),
    )
    pl_gen.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the candidate pools and crossing count without calling out.",
    )
    pl_gen.add_argument(
        "--seed",
        type=int,
        default=None,
        help=(
            "Seed for shuffling equally-ranked candidates (default: random;"
            " recorded in the plan so it can be reproduced)."
        ),
    )
    pl_gen.add_argument(
        "--provider",
        choices=("local", "cloud"),
        default="local",
        help="local (Ollama, default) or cloud opt-in (PHI-free only).",
    )
    pl_gen.add_argument(
        "--model",
        default=None,
        help="Model override (default: qwen3:8b local / claude-opus-4-8 cloud).",
    )
    pl_gen.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    pl_gen.set_defaults(func=_cmd_plans_generate)

    pl_list = plans_sub.add_parser(
        "list", help="Show plans in the vault, newest first."
    )
    pl_list.add_argument(
        "--limit", type=int, default=20, help="Show at most N plans (default: 20)."
    )
    pl_list.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    pl_list.set_defaults(func=_cmd_plans_list)

    pl_show = plans_sub.add_parser(
        "show",
        help="Render one plan's schedule with per-recipe attribution.",
    )
    pl_show.add_argument("plan_id", help="Plan id (pln-...).")
    pl_show.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    pl_show.set_defaults(func=_cmd_plans_show)

    meals = subparsers.add_parser(
        "meals",
        help="Record cooked meals + feedback (step 7, C5 two-stage).",
    )
    meals_sub = meals.add_subparsers(dest="meals_command", required=True)
    ml_cooked = meals_sub.add_parser(
        "cooked",
        help="Confirm a cook; optionally rate it and report actual time.",
    )
    ml_cooked.add_argument("recipe_id", help="Recipe that was cooked.")
    ml_cooked.add_argument("--plan-id", default=None)
    ml_cooked.add_argument(
        "--ease", type=int, default=None, help="1-5: how easy to make."
    )
    ml_cooked.add_argument(
        "--enjoyment", type=int, default=None, help="1-5: how fun to make."
    )
    ml_cooked.add_argument("--notes", default=None)
    ml_cooked.add_argument(
        "--actual-minutes", type=int, default=None, help="Actual cook time."
    )
    ml_cooked.add_argument("--data-dir")
    ml_cooked.add_argument("--member", default=None, help="Household member (name or id). Default: the first member.")
    ml_cooked.set_defaults(func=_cmd_meals_cooked)
    ml_feel = meals_sub.add_parser(
        "feel",
        help="Later prompt: how did the meal make your body feel?",
    )
    ml_feel.add_argument("response", help="Free text — the feeling is the data.")
    ml_feel.add_argument(
        "--meal-event-id", default=None, help="Default: the latest meal."
    )
    ml_feel.add_argument("--energy", type=int, default=None)
    ml_feel.add_argument("--digestion", type=int, default=None)
    ml_feel.add_argument("--fullness", type=int, default=None)
    ml_feel.add_argument("--mood", type=int, default=None)
    ml_feel.add_argument("--data-dir")
    ml_feel.add_argument("--member", default=None, help="Household member (name or id). Default: the first member.")
    ml_feel.set_defaults(func=_cmd_meals_feel)
    ml_history = meals_sub.add_parser("history", help="Cooked-meal log.")
    ml_history.add_argument("--limit", type=int, default=20)
    ml_history.add_argument("--data-dir")
    ml_history.add_argument(
        "--member", default=None,
        help="Show this member's own body responses (default: anyone's latest).",
    )
    ml_history.set_defaults(func=_cmd_meals_history)

    consent = subparsers.add_parser(
        "consent",
        help="Inspect + change standing consent decisions (E2, #21).",
    )
    consent_sub = consent.add_subparsers(dest="consent_command", required=True)
    cn_list = consent_sub.add_parser("list", help="Show current decisions.")
    cn_list.add_argument("--data-dir")
    cn_list.add_argument(
        "--member", default=None,
        help="Show the decisions in force for this member (own over household).",
    )
    cn_list.set_defaults(func=_cmd_consent_list)
    cn_set = consent_sub.add_parser("set", help="Record a decision.")
    cn_set.add_argument("category", help="Data category (see `consent list`).")
    cn_set.add_argument(
        "decision", choices=("grant", "decline"), help="The decision."
    )
    cn_set.add_argument(
        "--purpose",
        default="local_operation",
        choices=("local_operation", "publication_aggregate"),
    )
    cn_set.add_argument("--note", default=None)
    cn_set.add_argument("--data-dir")
    cn_set.add_argument(
        "--member", default=None,
        help="Record this member's own decision (default: household-wide).",
    )
    cn_set.set_defaults(func=_cmd_consent_set)

    grocery = subparsers.add_parser(
        "grocery",
        help="Build a grocery list from a meal plan (6.1).",
    )
    grocery_sub = grocery.add_subparsers(dest="grocery_command", required=True)
    gr_build = grocery_sub.add_parser(
        "build",
        help="Aggregate a plan's recipes into a consolidated list.",
    )
    gr_build.add_argument(
        "--plan-id",
        default=None,
        help="Plan to shop for (default: most recent plan).",
    )
    gr_build.add_argument(
        "--format",
        choices=("text", "markdown"),
        default="text",
        help="Output format (default: text checklist).",
    )
    gr_build.add_argument(
        "--out",
        default=None,
        help="Write to a file instead of stdout.",
    )
    gr_build.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    gr_build.set_defaults(func=_cmd_grocery_build)

    pinterest = subparsers.add_parser(
        "pinterest",
        help="Connect + maintain the Pinterest link (#24).",
    )
    pinterest_sub = pinterest.add_subparsers(
        dest="pinterest_command", required=True
    )
    pin_connect = pinterest_sub.add_parser(
        "connect",
        help="One-time OAuth: opens the browser, stores tokens in the"
        " OS credential store.",
    )
    pin_connect.add_argument(
        "--client-id", default=None, help="Pinterest app ID (prompted if omitted)."
    )
    pin_connect.add_argument(
        "--client-secret",
        default=None,
        help="Pinterest app secret (prompted if omitted).",
    )
    pin_connect.add_argument(
        "--port",
        type=int,
        default=8766,
        help="Localhost OAuth redirect port — the app's Redirect URI must be"
        " http://localhost:<port>/ (default: 8766).",
    )
    pin_connect.set_defaults(func=_cmd_pinterest_connect)
    pin_refresh = pinterest_sub.add_parser(
        "refresh",
        help="Renew the 30-day access token from the stored refresh token.",
    )
    pin_refresh.set_defaults(func=_cmd_pinterest_refresh)
    pin_status = pinterest_sub.add_parser(
        "status", help="Show whether Pinterest is connected."
    )
    pin_status.set_defaults(func=_cmd_pinterest_status)

    serve = subparsers.add_parser(
        "serve",
        help="Run the localhost web UI prototype (fridge search + phase"
        " boosts + URL import).",
    )
    serve.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind address (default: 127.0.0.1 — localhost only).",
    )
    serve.add_argument(
        "--port", type=int, default=8765, help="Port (default: 8765)."
    )
    serve.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    serve.set_defaults(func=_cmd_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
