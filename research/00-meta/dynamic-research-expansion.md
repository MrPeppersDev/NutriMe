# NutriMe — Dynamic Research Expansion Pattern

> When the system encounters a gap in its corpus and the missing information is plausibly available from authoritative public sources, the system fetches it, verifies it under the [epistemic trail](epistemic-trail.md), and integrates it into the working corpus.

This is a system capability requirement — the architecture (TBD) must support this pattern. It is not itself an architecture decision.

## The pattern

NutriMe operates on a base corpus assembled from authoritative sources (DRIs, food composition, condition gating, drug-nutrient interactions, recipes, etc.). The base corpus is comprehensive but cannot be exhaustive — gaps will appear in real use:

- A drug the user is taking that isn't in the base drug-interaction dataset
- A clinical condition that's globally recognized but not deeply enumerated in our framework
- An ingredient or regional food that's outside our composition database
- A cuisine technique outside our terminology corpus
- An emerging research finding that postdates our last corpus refresh

When the system detects such a gap AND the missing information is plausibly available from authoritative public sources, the system uses the dynamic research expansion pipeline:

1. **Gap detection** — the system identifies that data needed for an inference, recommendation, or explanation is missing or insufficient
2. **Public-availability assessment** — would this information plausibly exist in authoritative public sources (peer-reviewed literature, government databases, professional society guidance, clinical reference databases, etc.)?
3. **Targeted fetch** — retrieve the relevant data from those sources
4. **Verification** — pass the fetched data through the [epistemic trail verification](epistemic-trail.md#3-verification-before-presenting):
   - Confirm provenance (which source, when accessed)
   - Confirm peer-reviewed support (per [Rule 7](constitutional-rules.md#rule-7--peer-reviewed-evidence-floor))
   - Sanity-check against existing corpus (does the new data contradict established Tier 1/2 sources? if so, flag)
   - Generate causal explanation as verification (per [epistemic-trail.md](epistemic-trail.md#3-verification-before-presenting))
5. **Integration** — fold the verified data into the working corpus, with full provenance retained
6. **User-facing trail** — the user sees that this information was dynamically fetched, when, from where, and that it passed verification

## Domains where this pattern applies

- **Drug-nutrient interactions** — base corpus + on-demand fetch when user reports a drug we don't have
- **Clinical conditions** — base corpus of common conditions + on-demand deep research for less-common conditions
- **Cuisines and regional dishes** — base corpus of major cuisines + on-demand expansion for niche regional / diaspora / emerging-fusion patterns
- **Ingredients and regional foods** — base food composition + on-demand fetch for ingredients outside the base set
- **Emerging research** — periodic refresh + on-demand fetch when a user query touches recent literature
- **Regulatory / authoritative guidance updates** — base captured at corpus build + on-demand re-fetch when guidance is known to have updated

## Limits of the pattern

The pattern does NOT bypass any constitutional rule:

- **Rule 1 (consult-professional)** still applies — fetched information that surfaces uncertainty triggers the consult-professional callout
- **Rule 7 (peer-reviewed floor)** still applies — fetched data that fails the peer-reviewed-floor cannot drive system behavior
- **Rule 8 (epistemic trail)** still applies — fetched data carries the same provenance + verification + trail requirements as base-corpus data
- **Rule 9 (geographic neutrality)** still applies — fetched data from any country's authoritative source is equal-weighted

The system declines to fetch when:

- The information is not plausibly available from authoritative public sources
- The fetch would require violating ToS or scraping content the system isn't licensed to use
- The verification step fails (the fetched data doesn't pass sanity / provenance / peer-review checks)
- The information is genuinely contested at the authoritative-body level — surface the contest, do not synthesize a "winning" answer

## What this is NOT

This is not "let the LLM make stuff up when it doesn't know." Dynamic research expansion is structured retrieval from authoritative sources, with verification, with provenance, with the full epistemic trail. It is the opposite of unconstrained generation.

## Framework over source-list — the corpus design principle

The same philosophy that drives dynamic research expansion also drives **how the base corpus is built**: define qualification frameworks (criteria for what counts as a valid source) rather than hard-coded source lists. A new source can be added by passing through the framework; a deprecated source can be retired without restructuring.

Qualification criteria vary by domain but generally include:

- **Institutional credibility** — published authority, recognized credentialing, accountability
- **Peer recognition** — citation, professional / academic acknowledgment
- **Evidence tier** — meets the [peer-reviewed floor](evidence-tiers.md) for the domain
- **Engagement / use signal** (where applicable, e.g., recipe popularity) — not the only signal but contextually meaningful
- **Licensing / ToS compliance** — sources can be used legitimately given our access pathway
- **Provenance retention** — the source supports attribution + traceability

Domain-specific examples:

- **Recipes** ([sweep #11](../11-recipe-sourcing/scope.md)) — qualification framework spans paid commercial APIs, public-domain historical cookbooks, institutional culinary academies, credentialed YouTube creators (engagement + follower thresholds), curated publishers under legitimate paid access. New sources qualify if they meet the framework.
- **Drugs / interactions** — qualification framework: appears in regulatory drug labels, in established pharmacology databases, in peer-reviewed clinical pharmacology literature
- **Conditions** — qualification framework: ICD recognition, DSM recognition, professional society guidance, peer-reviewed prevalence + management literature
- **Cuisines / cultural foods** — qualification framework: national culinary institutes, cultural heritage organizations, peer-recognized practitioners, academic culinary studies

This means we should **never pigeon-hole the system into a fixed list of sources**. Build frameworks that can extract what's needed when it's needed.

## Source

- User direction (2026-04-28, sweep #10 scoping) on drugs: "if we come across a drug that we don't have in a database for ourselves and we know the information should be publicly available, there should be a situation where we can go and fetch and verify that information and work it in as needed"
- User direction (2026-04-28, sweep #10 scoping) on conditions: "Let's start with what are the top things we're looking at that all the experts are looking at across the globe, and then where we need to pull in more specified information. We should have some sort of framework in place to identify that in the data we're collecting and then pass that off to deep research analysis to pull back information as needed."
- User direction (2026-04-28, sweep #11 scoping) on framework over source-list: "We want to make sure that we're not pigeon-holing ourselves in any sort of way, but building frameworks that can extract what we need when desired."

## Operational pipeline architecture *(per [architecture.md B3](architecture.md#b3--dynamic-research-expansion-infrastructure))*

The above pattern is operationalized through a concrete pipeline architecture decided in Stage 3 Block B3:

- **Gap detection** — hybrid reactive (gap surfaces during real query) + proactive (intake-triggered or background-scheduled fetches for predictable gaps)
- **Source adapters** — hybrid explicit per-source code adapters (USDA FDC, OpenFDA, DailyMed, EMA SmPC, NIH ODS, PubMed, FlavorDB, Cochrane, authoritative DRI publications, major recipe APIs) + generic web-fetch + LLM-extraction adapter for one-off / unstructured / low-volume sources
- **Verification harness** — both source-specific (in adapter, "well-formed for its type") + centralized (peer-reviewed-floor, sanity-range, contradiction detection, causal-explanation generation per [B2 epistemic trail verification](architecture.md#b2--rule-8-epistemic-trail-implementation))
- **Cache + freshness** — per-content-type TTL defaults (drug labels monthly; DRIs annual; food composition quarterly; recipes per-recipe lazy-refresh; regulatory guidance annual + on-demand; peer-reviewed literature indefinite with citation-tracking for retractions; cuisine/technique annual; ingredient-interaction annual) + change-triggered re-fetch when TTL fires
- **Failure handling** — cascade failure with partial-success rebuild: independent per-sub-fetch success/fail; partial corpus rebuild; retry only failed sub-fetches with bounded exponential backoff; surface cascade state to user; downgrade inference confidence with specific gap acknowledgment per Rule 8
- **Cascade composition** — both system-defined templates (drug-nutrient, recipe, condition-gating) + LLM-decomposed for novel queries
- **Late-arriving sub-fetch surfacing** — trail update always notified (low-key); material refinements that change the answer surfaced prominently
- **Per-sub-fetch retry caps** — default 3 retries with exponential backoff (30s / 2m / 10m); per-source-type override available

## Related

- [epistemic-trail.md](epistemic-trail.md) — verification flow
- [evidence-tiers.md](evidence-tiers.md) — sources fetched must meet the same tier discipline
- [constitutional-rules.md](constitutional-rules.md) — Rules 1, 7, 8, 9 all apply to fetched data
- [architecture.md B3](architecture.md#b3--dynamic-research-expansion-infrastructure) — operational pipeline architecture
