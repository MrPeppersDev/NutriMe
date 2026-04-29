# Sweep #13 — Grocery Sourcing, Ordering, and Delivery Infrastructure

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Map the grocery infrastructure that fulfills the *"boom, shows up at my door"* product promise. Primary focus on **Instacart (US)** as the locked-in initial integration target. Survey landscape (US first, then primary-audience international) for broader awareness so we know what's available when scope broadens.

Per personal-use distribution intent (per [product-framing.md](../00-meta/product-framing.md)), this sweep does not need to optimize for commercial-scale agreements; indie / personal-use access tiers are the primary focus.

## Deliverable

An annotated reference map containing:

- **Instacart deep dive** — IDP (Instacart Developer Platform), recipe-link integration, partner program, indie / personal-use access tiers, ToS, approval timelines, coverage, fees, delivery vs. pickup workflows
- **US landscape survey** — Amazon Fresh / Whole Foods, Walmart+ / Walmart APIs, Kroger Cart API, regional grocers (Wegmans, Publix, H-E-B), Shipt, FreshDirect — characterized for what's available to indie integrators
- **International landscape survey** for the primary audience future-proofing — Tesco / Sainsbury's / Ocado (UK), Loblaws / Voila / Instacart Canada, Carrefour (FR), Rewe / Edeka (DE), Picnic / Albert Heijn (NL), Mercadona (ES)
- **Recipe-to-cart translation patterns** — ingredient deduplication across a week's plan, quantity unit normalization, substitution logic, pantry deduction (don't reorder what user has), brand selection + budget-tier mapping
- **Pickup vs. delivery workflows** — both supported, user picks
- **Fallback strategies** — when primary path is unavailable (cart export to printable list, deep-link to native app, manual cart-build pattern)
- **ToS landscape** — what indie / personal-use access actually permits across providers

This is a **reference map**, not corpus build.

## In scope

### Instacart (primary)

- Instacart Developer Platform (IDP) — what API access is available, indie tier vs. partner tier
- Recipe-to-cart deep linking — recipe URL → cart with pre-populated items
- Coverage — ~95% US household reach claimed; verify
- Pricing model — delivery fees, service fees, membership (Instacart+), per-item markup
- Approval timeline for partner / IDP access
- ToS for indie + personal use
- Pickup vs. delivery workflows + retailer availability per modality
- Substitution preferences + pre-approval flow

### US landscape survey

- **Amazon Fresh + Whole Foods** — Amazon API (limited), Subscribe & Save patterns, Whole Foods integration via Amazon
- **Walmart+** — Walmart APIs (limited public access), affiliate API
- **Kroger Cart API** — historically the only indie path that builds carts server-side; covers ~2,700 stores in Midwest / South / West US
- **Regional grocers** — Wegmans, Publix, H-E-B, Trader Joe's (no online ordering), Aldi, Lidl
- **Other delivery services** — Shipt (Target), FreshDirect, Misfits Market, Imperfect Foods (subscription / specialty)

### International landscape survey (primary audience)

For Western audience countries:

- **UK** — Tesco (large API surface), Sainsbury's, Ocado (technology-forward), Asda, Morrisons, Waitrose
- **Canada** — Loblaws (Voila by Sobeys), Walmart Canada, Instacart Canada (limited coverage)
- **France** — Carrefour, Auchan, Leclerc, Monoprix
- **Germany** — Rewe, Edeka, Lidl Online, Bringmeister
- **Netherlands** — Picnic (technology-forward), Albert Heijn, Jumbo
- **Iberia** — Mercadona, El Corte Inglés
- **Nordic** — ICA (SE), Coop, Mathem
- **Ireland** — Tesco IE, SuperValu, Dunnes
- **Switzerland / Austria** — Migros, Coop (CH), Billa, Spar

### Recipe-to-cart translation infrastructure

This is where the cooking layer ([sweep #11](../11-recipe-sourcing/scope.md)) meets the grocery layer:

- **Ingredient deduplication** — when a week's meal plan calls for onions across 4 recipes, aggregate into one cart entry with appropriate quantity
- **Quantity normalization** — recipe units (cups, tbsp, "a handful") → grocery purchase units (lbs, oz, count, packages)
- **Substitution logic** — what to do when a specific ingredient isn't available; substitution patterns from culinary literature + clinical-condition-aware substitution (per [sweep #10](../10-clinical-condition-gating/scope.md))
- **Pantry deduction** — track what user has, don't reorder
- **Brand selection** — generic vs. organic vs. specialty; budget-tier mapping
- **Bulk vs. precise** — when to buy a 5-lb bag vs. 1-lb portion (waste optimization)
- **Multi-store cart split** — when no single retailer carries everything

### Fallback patterns

When primary integration path is unavailable:

- Cart export to printable / shareable list
- Deep-link to native grocery app with cart pre-populated where possible
- Manual cart-build pattern (system surfaces "build this cart yourself" with item-by-item guidance)
- Email / SMS list export

### ToS landscape for indie / personal use

- What does each retailer's ToS actually permit for personal-use indie integration?
- Where is scraping prohibited (consistent with [Constitutional Rule 4](../00-meta/constitutional-rules.md#rule-4--no-recipe-generation) discipline applied to grocery-data scraping)?
- What APIs require partnership vs. open / indie access?

## Out of scope (with reasons)

- **Building integrations** — research phase only; implementation deferred
- **Financial transactions / payment processing** — out; Instacart and equivalents handle their own checkout
- **Subscription model design for the product itself** — out per personal-use distribution
- **Restaurant / prepared meal delivery** — out per [product-framing](../00-meta/product-framing.md) (cooking-first, not prepared meals)
- **Meal kit services** (HelloFresh, Blue Apron, Sunbasket) — out for the same reason; ingredients-and-recipes-separately is the model
- **Commercial-tier partnership economics** — light coverage given personal-use distribution; can be revisited if scope broadens (tracked in [roadmap.md](../00-meta/roadmap.md))

## Geographic scope

Per [geographic-scope.md](../00-meta/geographic-scope.md). Primary US (Instacart locked in); primary-audience international (UK + Canada + Western Europe) at survey level. Other regions opportunistic.

## Open questions for the research

- What is the realistic state of Instacart IDP indie access in 2026? Is the partner program friendly to personal-use developers, or does it require commercial agreement?
- Which retailers genuinely support recipe-to-cart deep-linking at the URL level (vs. "click here, then build cart manually")?
- What's the state of Kroger Cart API — still the main indie path for server-side cart building?
- For Western Europe: is there an "Instacart equivalent" that aggregates across retailers, or is everything direct-to-retailer?
- What recipe-to-cart translation patterns are published / open-source? (Mealie has some patterns; what else?)
- What pantry-tracking patterns work in practice without becoming a "logging app" (per [Constitutional Rule 3](../00-meta/constitutional-rules.md#rule-3--no-food--macro--calorie-logging))?
- For substitution logic: what published sources (CIA texts, culinary substitution databases) inform ingredient swaps?

## Cross-references

- Bound by [product-framing.md](../00-meta/product-framing.md) — *"boom, shows up at my door"* is core promise
- Bound by [Constitutional Rule 9 (geographic neutrality)](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing) — international landscape covered without home-country bias
- Bound by [Constitutional Rule 3 (no logging)](../00-meta/constitutional-rules.md#rule-3--no-food--macro--calorie-logging) — pantry tracking must not become user-initiated logging
- Depends on [sweep #11 (recipe sourcing)](../11-recipe-sourcing/scope.md) — recipes feed the cart-translation layer
- Depends on [sweep #2 (food composition databases)](../02-food-composition-databases/scope.md) — ingredient identity + nutrition retained through cart
- Cross-references [sweep #10 (clinical condition gating)](../10-clinical-condition-gating/scope.md) — substitutions must respect condition gating
- Cross-references [sweep #9 (multi-user household)](../09-multi-user-household/scope.md) — household-level cart aggregation
- See [roadmap.md](../00-meta/roadmap.md) — broader-scope grocery integration tracked as deferred

## Findings

To be populated when research is run.

## References

To be populated. Add new sources to [sources.md](../00-meta/sources.md) when added.
