# Vision-gap build plan — closing #26 / #27 / #28 (+ #25 rider)

> Planned 2026-10-04 against the roadmap § Vision-audit gaps. Four sub-commits,
> sequenced by dependency; shape decisions resolved here so each build session
> is mechanical. Per the two-track discipline: everything here is Track M
> ranking/UX work reading *summaries*, never raw atoms — no new seam crossings,
> no new PHI envelopes, no LLM dependency (key-403 doesn't block any of it).

## Sequencing

```
V1 learning-loop consumers (#26)      ← nothing depends on it; everything after reads its signal shape
V2 use-it-up + decrement (#27)        ← independent of V1, shares the Tonight panel surface
V3 horizon broadening (#28a)          ← REQUIRES V1 (novelty = absence in cook history)
V4 equipment surfacing (#28b)         ← independent; smallest; batch with V3
(#25 rider: periodic check-ins stay with Track G — NOT in this plan)
```

V1+V2 are one session ("recipe box → learning system"); V3+V4 a second.

## V1 — learning-loop consumers (#26)

**Shape decisions:**
- `feedback.py` gains `experience_summaries(conn, tenant_id) -> dict[recipe_id, summary]`
  (one pass over history; per-recipe lookups stay O(1) at search time). The existing
  per-recipe function stays for detail surfaces.
- **Search integration:** `SearchFilters` gains `experience: Mapping[str, dict] | None`.
  `_score` adds, for ranked recipes with history:
  - `_LOVED_POINTS = 1.0 * max(0, avg_enjoyment - 3)` (5-star avg → +2.0, i.e. one
    on-hand ingredient's weight — history never outweighs "what's in the fridge")
  - `_DISLIKED_POINTS = -1.0 * max(0, 3 - avg_enjoyment)` (boost-down, NEVER a filter —
    she can always still find a disliked recipe by name; seam discipline)
  - ease contributes nothing directly (enjoyment subsumes it for ranking; ease stays
    a detail-surface stat).
- **Time correction:** when a recipe's summary has `avg_time_delta_min`, display
  surfaces show `estimated + avg_delta` as "usually takes ~N min for you" alongside
  the stated time (never silently overwrite the source's claim — honesty discipline),
  and `max_total_time_min` filtering uses the corrected value when available
  (safe direction: her real times beat the blog's optimism).
- **Planner integration:** `assemble.py` candidate pools come from 5.3 search, so
  boosts flow in for free once the CLI/web callers pass `experience=`; plus one
  prompt-visible line per candidate (`cooked 3x, loved`) so the LLM selection sees
  history WITHOUT any new PHI (cook counts are not PHI; they ride the existing
  `{demographics}` envelope unchanged — confirm at build that the envelope audit
  shows no new categories).
- **Surfaces:** web search cards show a small `cooked Nx ♥` chip; detail view shows
  the full summary row.

**Tests:** boost arithmetic (loved beats equal-match unloved; disliked sinks below
no-history; never excluded), corrected-time filter direction, planner pool receives
boosts, envelope unchanged.

## V2 — use-it-up priority + cook decrement (#27)

**Shape decisions:**
- **Expiring-soon boost:** `SearchFilters.on_hand` entries gain optional urgency:
  new field `expiring: frozenset[str]` (names whose `best_by_date` ≤ today+4d —
  window constant, build-time tunable). `_score`: matches against `expiring` earn
  `_EXPIRING_POINTS = 2.0` ON TOP of on-hand points (a both-match = 4.0). Ordering
  stays on-hand-count-first (user direction 2026-10-04); expiring urgency breaks
  ties through score — it tilts, never reorders match counts.
- **Tonight panel strip:** `/api/tonight` adds `use_soon: [{name, best_by_date,
  days_left}]` (≤ 4 days, soonest first, cap 6). One-tap "find recipes" pre-fills
  the have-box with those names.
- **Cook decrement (presence-level, ask-don't-assume per Tension #1):**
  - `grocery/parse.py::needs_from_recipe_body` already extracts a recipe's
    ingredient names — reuse it at cook time: intersect recipe ingredients with
    current inventory names (normalize_food on both sides).
  - `meals cooked` (CLI + web) returns that intersection as `used_candidates`;
    the surface asks "used up any of these?" — checked items are REMOVED from
    inventory (presence model: gone, not quantity-math). Unchecked stay. No
    silent decrements, matching "observed, not asked… reach out and ask the user."
  - CLI: `--used-up "spinach,lemon"` flag + interactive prompt when a TTY;
    web: checkbox row in the cooked dialog (replace the prompt() chain with a
    small form in the Tonight panel — the prompt() UX was prototype-grade anyway).
- **Audit trail:** removals write an `inventory_item_consumed` op_event (existing
  event-log family) so "where did my spinach go" is answerable.

**Tests:** expiring boost stacks and tie-breaks correctly, window edge (today,
+4d, +5d), use_soon payload shape, decrement removes exactly the checked names,
unchecked survive, op_event written.

## V3 — horizon broadening (#28a, after V1)

**Shape decisions:**
- Novelty = absence in cook history at the **cuisine level** (meal_categories are
  too noisy per the 5.4 defect note; `cuisine_tradition_tags` are the clean axis).
- `feedback.py` gains `cooked_cuisines(conn, tenant_id) -> set[str]` from meal
  events joined to vault frontmatter at call time (no denormalization).
- **Planner-only by default:** novelty boosts apply in `plans generate` candidate
  pools (`_NOVELTY_POINTS = 0.5` for never-cooked cuisine — deliberately below
  preference boosts: broadening nudges, never overrides stated taste). Search
  stays non-novel by default — "what can I make right now" is not the moment to
  push new cuisines; a `--broaden` flag / web toggle opts in.
- **Surface:** plan view tags novel picks "new cuisine for you ✦"; Tonight panel
  shows the tag when tonight's meal is novel.

**Tests:** never-cooked cuisine outranks equal-score cooked one in planner pools;
stated "prefers" still beats novelty; opt-in flag gates search behavior.

## V4 — equipment surfacing (#28b)

**Shape decisions:**
- Populate-where-stated only: jsonld adapter maps schema.org `tool`/
  `HowToTool` entries → S9 `equipment_required`; other adapters leave it absent
  (historical books don't state it reliably; no inference at MVP — that would be
  guessing, which the honesty discipline forbids).
- Render on detail view ("Equipment: stand mixer, 9x13 pan") when present.
- NO own/don't-own dialogue, NO filtering (deferred until real use shows need —
  the genesis ask was *surface and clarify*, and surfacing is the MVP-honest cut).

**Tests:** jsonld tool extraction shapes (string, list, HowToTool objects),
absent field renders nothing, round-trips S9 validation.

## Explicitly out

- Quantity-aware pantry netting (beyond presence) — sweep #16 confirmed nobody
  does this well; new design work, not a vision gap.
- Novelty at ingredient level — cuisine-level first; revisit with usage.
- Equipment inference from instruction text — guessing violates honesty rules.
- #25 periodic check-ins — Track G resumption work, tracked there.
