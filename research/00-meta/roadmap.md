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
- **Sweep #3 (clinical nutrition assessment)** — re-verify sensitivity/specificity figures against original validation studies (agent flagged with inline `[verify]` tags); audit instrument copyright/licensing before any item-text embedding; map cross-cultural validation gaps per instrument for Rule 9 surfacing.
- **Sweep #4 (adaptive intake agent)** — re-verify open-source repo states (Rasa / OpenDialog / Concerto status), Wysa / Limbic post-2024 publication updates, AMIE follow-up papers, any new PROMIS banks added in 2024–2026 window.
- **Sweep #8 (nutrition education + why delivery)** — re-verify HLS-19 most recent country reports, 2024–2026 AI-credibility literature (post-ChatGPT publishing pace), latest Cochrane PLS template revisions, 2025–2026 ICMJE / WAME AI-disclosure guidance updates.
- **Sweep #5 (personalized nutrition evidence audit)** — live re-verification on every URL once tools available (Tier 4 vendor pages especially — marketing language drifts fastest); track NIH Nutrition for Precision Health program annually for first outcome publications (likely late 2020s onward).
- **Sweep #7 (cooking time + barriers)** — DOIs and a small number of journal volumes/issues flagged `[verify]`; meal-kit behaviour-shift literature deserves a focused mini-sweep before sweep #13's grocery-sourcing UX freezes.
- **Sweep #9 (multi-user household)** — Brisbane / Australian couple-intervention specific PI/trial citations need primary verification (`[verify]` tagged); Russian and Israeli household-meal patterns under-covered relative to primary scope; South Asian peer-reviewed slice is thinnest — adding NIN Hyderabad / AIIMS work would strengthen.
- **Sweep #10 (clinical condition gating)** — `[VERIFY]`-tagged regulatory items need live re-fetch against FDA, MHRA, TGA, NMPA, MHLW, Roszdravnadzor pages; build dynamic-expansion fetch pipeline against DailyMed + openFDA + EMA SmPC + LactMed + NIH ODS as Tier 1 path.
- **Sweep #13 (grocery infrastructure)** — all `VERIFY-AT-ADOPTION` items: Instacart IDP indie-tier status + pricing + ToS, Kroger Cart API current state, Subscribe & Save current pricing, international retailer API states.
- **Sweep #12 (skills-by-cuisine)** — live URL verification on the ~40 citations (academy curricula, canonical texts, cuisine-specific works); bottom-up dish-set validation pass to confirm the skill matrix against actual recipe-skill extraction; English-language coverage uneven across regional cuisines (Sichuan/Punjabi well-covered, Hunan/Bengali/Yucateco less so) — broader source-language coverage may need translation budget.

This verification pass becomes a research-pipeline task before corpus-build phase begins. It is not a re-do of the sweeps — the framework, source identification, and analytical structure stand. It's a freshness check on time-sensitive details that the wave environment couldn't capture.

All 13 sweeps now have populated Findings and References sections. Pre-corpus-build verification pass is complete in scope; execution awaits a session with live web tools.

## Synthesis-phase tensions to resolve

Surfaced during research, these are real product-design tensions that synthesis (post-Stage 1) needs to resolve. They do not block research but should not be lost. **Resolved tensions move to [synthesis.md](synthesis.md).**

### Resolved

- **Tension 1 — Mental-load framing supersedes raw-time + inventory tracking distinction** — resolved 2026-04-29. See [synthesis.md Tension #1](synthesis.md#tension-1--mental-load-framing-supersedes-raw-time-plus-inventory-tracking-distinction). This resolution preemptively closed the pantry "observed not asked" tension as well (see below).
- **Tension 2 — "Common base + per-plate deltas" evidence basis honesty** — resolved 2026-04-29. See [synthesis.md Tension #2](synthesis.md#tension-2--common-base--per-plate-deltas-evidence-basis-honesty). User-facing transparency: describe the pattern operationally. New cross-cutting principle added: operational tradition is a legitimate supplementary evidence basis when peer-reviewed evidence is thin — but must be flagged as such. Codified in [evidence-tiers.md "Operational tradition as supplementary basis"](evidence-tiers.md#operational-tradition-as-supplementary-basis).

### Open

- **Spaced-repetition cadence vs. no-daily-check-in rule.** Sweep #8 (education delivery) found that spaced-repetition delivery is one of the strongest evidence-based patterns for nutrition concept retention. The intake-pattern.md "no daily check-in" rule rules out the streak-design / daily-engagement model that most spaced-repetition systems use. Synthesis needs to figure out how to deliver spaced repetition through the passive-confirmation surface (per-meal feedback) or via opt-in microlearning that doesn't become streak-driven. Flagged in sweep #8; touches sweep #4 (adaptive intake agent) too.
- **Consumer-friendly clinical instrument adaptation vs. validity preservation.** Sweep #3 found that consumer-friendly translations of clinical instruments routinely lose psychometric validity. Synthesis needs to decide whether to stay closer to clinical-grade administration (more friction, validated) or accept validity loss with explicit framing (less friction, weaker measurement). Touches the consumer-vs-clinical-fidelity question in sweep #4 too.
- **GRADE 4-level certainty vs. consumer comprehension.** Sweep #8 found consumer comprehension of full GRADE is unfavourable; recommends a 2- or 3-level user-facing display with full GRADE preserved in the audit trail. Touches the audit-as-education pattern in evidence-tiers.md.
- **No-dominant food-relationship instrument** is a Sweep #3 finding that *positively* validates NutriMe's iterative-dialog elicitation approach (vs. trying to adopt a single canonical scale).
- ~~**Mental-load framing supersedes raw-time framing.**~~ — **resolved 2026-04-29 by [synthesis.md Tension #1](synthesis.md#tension-1--mental-load-framing-supersedes-raw-time-plus-inventory-tracking-distinction).** Mental-load is co-equal frame with time-saving (not replacement); convenience driver list expanded to surface deciding/remembering/monitoring; time stays central as surface frame because accurate time *reduces* mental load.
- **No indie-tier recipe-to-cart aggregator outside US/Canada.** Sweep #13 surfaces that Instacart's openness is anomalous globally; everywhere else the indie path is closed. If distribution scope ever broadens to UK/EU primary audience, the "boom shows up at my door" promise breaks unless we partner-tier with retailers individually. Tracked under Broader-scope future as well.
- ~~**Pantry tracking can stay on the right side of Rule 3 via "observed, not asked".**~~ — **resolved 2026-04-29 by [synthesis.md Tension #1](synthesis.md#tension-1--mental-load-framing-supersedes-raw-time-plus-inventory-tracking-distinction).** Inventory tracking is formally distinguished from food/macro/calorie logging. Both observed (orders + cook confirmations) AND asked (initial intake + just-in-time clarification) inputs are in scope, with loose-by-default quantities. Sweep #13's "observed not asked" pattern is incorporated but no longer constrained as a Rule-3 workaround.
- **Adolescent-confidentiality wrinkle in parent-mediated intake.** Sweep #9 surfaces that as kids age into adolescence, the parent-mediated-intake model needs nuance — adolescents have legitimate confidentiality interests (especially around eating, body, mental health). Not blocking now (target user is busy adults; kids are eaters), but synthesis should address the developmental transition.
- **Pediatric obesity AAP 2023 guideline controversy.** Sweep #10 flags that the contested 2023 AAP guideline (meds + surgery for severe pediatric obesity) means the refuse/gate/proceed assignment for pediatric obesity needs a second pass. Part of the "needs second pass" condition list (depression/anxiety boundary, SIBO, NCGS, histamine intolerance, orthorexia, long COVID, pediatric obesity, ASD-without-ARFID).
- **Cross-sweep gap: wearable-data sharing within households.** Sits at the #6 / #9 intersection — neither sweep addressed it. Synthesis needs to define the privacy + consent model for wearable signals shared across household members.
- ~~**"Common base + per-plate deltas" pattern is operationally grounded but academically thin.**~~ — **resolved 2026-04-29 by [synthesis.md Tension #2](synthesis.md#tension-2--common-base--per-plate-deltas-evidence-basis-honesty).** Operational tradition is a legitimate supplementary basis when peer-reviewed evidence is thin; user-facing surfaces describe operationally and flag honestly. Codified as cross-cutting principle in [evidence-tiers.md](evidence-tiers.md#operational-tradition-as-supplementary-basis).

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
