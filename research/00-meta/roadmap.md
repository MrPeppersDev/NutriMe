# NutriMe — Roadmap

> Living tracker of stretch goals, deferred items, and "noted but not now" features that surfaced during scoping. **Not a strategic 5-year plan** — just a list so things don't get buried in individual sweep "out of scope" sections. Build what we need; ensure it works in the ways we need it to.

## Format

Each item: short name + one-line description + which sweep / context it surfaced in + status (`stretch` / `deferred-architectural` / `broader-scope-future`).

---

## Stretch goals

Features the user has tagged as "would be cool, not now":

- **Real-time meal-glucose response personalization (CGM-driven)** — `stretch` — surfaced in sweep #5; user said "really fucking cool idea, absolutely have as a stretch goal, but not too worried about at the moment"
- **Where-to-learn cooking instruction surfacing** — `stretch` — surfaced in sweep #7 (and reinforced in sweep #12 at reference level). System maps where to learn skills, never delivers cooking instruction itself
- **One-time CGM trial as diagnostic input to intake** — `stretch` — surfaced in sweep #5, distinct from the real-time use case above
- **Cuisine-context-aware adaptive intake at finer cultural granularity** — surfaced in sweep #3, broad framework now, deeper per-tradition mapping deferred to corpus-build phase

## Broader-scope future

Items deferred because the current product is personal-use (user + family + a couple friends):

- **Children as cooks (children's nutrition + cooking education)** — out per [product-framing.md](product-framing.md). Currently kids are eaters in households, never cooks. A separate product entirely.
- **Households of 3+ adults** — system handles in principle; not optimized for. Surfaced in sweep #9.
- **Roommate / shared-kitchen-but-not-meals scenarios** — different problem; out
- **Food-insecure / kitchen-less populations** — different product entirely; out
- **Commercial-tier grocery partnership economics** — surfaced in sweep #13. Currently focused on indie / personal-use access. Revisit if distribution intent changes.
- **Provider directory integration / telehealth partnerships** — out per sweep #10 user direction. Specialty surfacing yes; integration no.
- **Localization beyond English / language translation layer** — implicitly in scope long-term given broad audience but no concrete plan; deferred-architectural

## Pre-corpus-build verification pass (required)

Wave 1 research (sweeps #1, #2, #6, #11) was executed in an environment where WebSearch and WebFetch were denied. Findings in those scope docs are populated from the agents' training-data knowledge of well-documented public-sector sources. The reference-map structure is intact and citation-complete; **specific time-sensitive details require re-verification before any corpus-build phase**:

- **Sweep #1 (international nutrition standards)** — verify current versions of DRI / DRV / NRV publications, especially translations of CDRI 2023 (China), DRI-J 2025 (Japan), DGE 2024 (Germany), NNR 2023 status, Russian Rospotrebnadzor 2021 currency. AU/NZ NHMRC was unreachable during sweep — re-fetch from canonical domain.
- **Sweep #2 (food composition databases)** — verify item counts (especially Open Food Facts product count, USDA FDC sub-dataset sizes), API rate limits / pricing, and license-text currency. Re-confirm whether BLS Germany remains paid-license.
- **Sweep #6 (wearable & biometric data)** — verify vendor API current state (especially Fitbit Web API sunset trajectory, Garmin pricing tiers, Whoop v2 scope changes, Apple SpO2 patent-litigation status), re-confirm doctor-portal patient-API rollouts (ONC Cures Act §170.315(g)(10) compliance, Korean My HealthWay, Israeli Eitan, EHDS implementation timelines).
- **Sweep #11 (recipe sourcing)** — re-verify all commercial API pricing + ToS at adoption time (Spoonacular, Edamam, ckbk, Eat Your Books, NYT Cooking subscription tiers).

This verification pass becomes a research-pipeline task before corpus-build phase begins. It is not a re-do of the sweeps — the framework, source identification, and analytical structure stand. It's a freshness check on time-sensitive details that the wave-1 environment couldn't capture.

When wave 2 / wave 3 sweeps complete, this section should be extended with their analogous verification needs.

## Deferred to architecture phase

Items that are real but properly architectural — handled when implementation begins:

- **Tech stack (LLM provider, framework, orchestration, database)** — deferred to architecture phase
- **Update cadence + corpus refresh design** — DRIs revise every 5–10 years; food composition periodically; recipes constantly; regulatory ad-hoc. Architecture must plan for refresh alongside dynamic-research-expansion.
- **Authentication / identity infrastructure** — household + per-user model confirmed; implementation TBD
- **Privacy + data retention model** — for iterative intake + semantic feedback + clinical data pipeline; not addressed during scoping
- **Time-zone / scheduling architecture** for grocery delivery + cooking timing
- **Multi-modal recipe presentation rendering** — sourcing covered in sweep #11; rendering layer architectural
- **Glossary / terminology lookup infrastructure** — sourcing covered in sweep #11; in-context lookup UX architectural
- **System learning rate** — how quickly the system updates its model of the user from semantic feedback; tunable in implementation

## Resolved during scoping (formerly stretch / deferred)

Items that were initially proposed as stretch / out-of-scope but moved into scope during the discovery dialog:

- **Recipe video sourcing for low-confidence users** — moved into sweep #11 scope
- **Real-time terminology lookup in recipes** — moved into sweep #11 scope
- **Iterative intake + horizon-broadening** — moved from "later feature" to defining product property
- **Passive confirmation + semantic feedback** — moved from "logging alternative" to defining personalization mechanism
- **Audit-as-education pattern for evidence-weak topics** — moved from defensive to first-class feature
- **Dynamic research expansion** — moved from architectural to capability requirement
- **Pediatric assessment instruments + pediatric conditions** — moved into scope when kids confirmed as eaters in households
- **Skills-by-cuisine mapping** — added as sweep #12
- **Grocery infrastructure** — added as sweep #13

## How this doc gets used

- When something surfaces during work that isn't immediately needed, add it here rather than burying it in a sweep "out of scope" section
- When considering whether to take on a new feature, check here for pre-existing context
- When the personal-use scope evolves (e.g., user decides to share with broader audience), the "broader-scope future" section becomes a real backlog
- Doc is a living list, not a strategic plan — the user has been clear that long-horizon strategic planning isn't the point: "we're looking at just building what we need and ensuring that it works in the ways that we need it to"

## Source

- User direction (2026-04-28, post-scoping consistency pass): "we definitely want to do a meta roadmap so that we can keep these things tracked. I don't think we're looking at five- to ten-year phases here. I think we're looking at just building what we need and ensuring that it works in the ways that we need it to."
