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
- **Recipe-to-cart translation patterns** — ingredient deduplication across a week's plan, quantity unit normalization, substitution logic, **inventory awareness** (initial intake + observed + just-in-time precision when needed — see [intake-pattern.md inventory awareness layer](../00-meta/intake-pattern.md#inventory-awareness--a-parallel-data-layer)) so we don't reorder what user has and we prioritize using-up perishables, brand selection + budget-tier mapping
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
- **Inventory awareness + pantry deduction** — initial inventory intake at onboarding (loose, what staples + perishables you keep) + ongoing passive observation from orders + cook confirmations + just-in-time clarification when precision matters (per [intake-pattern.md inventory awareness layer](../00-meta/intake-pattern.md#inventory-awareness--a-parallel-data-layer)). Drives use-existing-ingredients prioritization in meal planning + don't-reorder-what-you-have in shopping lists
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
- ~~What pantry-tracking patterns work in practice without becoming a "logging app"~~ — **resolved in [synthesis.md Tension #1](../00-meta/synthesis.md#tension-1--mental-load-framing-supersedes-raw-time-plus-inventory-tracking-distinction)**: inventory tracking is formally distinguished from food/macro/calorie logging. Both observed (orders + cook confirmations) AND asked (initial intake + just-in-time clarification) inputs are in scope, with quantities loose by default.
- For substitution logic: what published sources (CIA texts, culinary substitution databases) inform ingredient swaps?

## Cross-references

- Bound by [product-framing.md](../00-meta/product-framing.md) — *"boom, shows up at my door"* is core promise
- Bound by [Constitutional Rule 9 (geographic neutrality)](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing) — international landscape covered without home-country bias
- Bound by [Constitutional Rule 3 (no logging)](../00-meta/constitutional-rules.md#rule-3--no-food--macro--calorie-logging) — **inventory tracking is formally distinguished from food/macro/calorie logging per [synthesis.md Tension #1](../00-meta/synthesis.md#tension-1--mental-load-framing-supersedes-raw-time-plus-inventory-tracking-distinction); inventory IS in scope**, with both observed and asked inputs and loose-by-default quantities
- Depends on [sweep #11 (recipe sourcing)](../11-recipe-sourcing/scope.md) — recipes feed the cart-translation layer
- Depends on [sweep #2 (food composition databases)](../02-food-composition-databases/scope.md) — ingredient identity + nutrition retained through cart
- Cross-references [sweep #10 (clinical condition gating)](../10-clinical-condition-gating/scope.md) — substitutions must respect condition gating
- Cross-references [sweep #9 (multi-user household)](../09-multi-user-household/scope.md) — household-level cart aggregation
- See [roadmap.md](../00-meta/roadmap.md) — broader-scope grocery integration tracked as deferred

## Findings

> **Methodology note (epistemic constraint):** WebSearch and WebFetch were both denied in this environment. Findings draw on the model's January 2026 knowledge cutoff plus authoritative URLs the reader can independently verify. Pricing, fee structures, ToS language, API surface, and partner-program intake details drift fast in this domain — every commercial source listed here should be re-verified at adoption time. Per [dynamic-research-expansion.md](../00-meta/dynamic-research-expansion.md), live re-fetch + verification is part of the system pipeline anyway; the framework + landscape map is the durable artifact, not the snapshot. Items flagged **VERIFY-AT-ADOPTION** are particularly time-sensitive (pricing, approval windows, regional coverage stats, partner-tier eligibility).

### 1. Why "boom, shows up at my door" is hard

The product promise from [product-framing.md](../00-meta/product-framing.md) — a meal plan that materializes on the user's doorstep — looks like a single transaction from the user's seat. From an integration seat it is the composition of:

1. A **meal plan** with discrete recipes ([sweep #11](../11-recipe-sourcing/scope.md))
2. An **ingredient list** normalized to purchasable units (this sweep, §7)
3. A **retailer / fulfillment selection** that can deliver to the user's address with adequate SKU coverage (this sweep, §2–§5)
4. A **cart-construction handoff** — either a server-side cart build (if the retailer supports it) or a deep-link to the retailer's app/site with items pre-populated (this sweep, §6)
5. A **substitution + pickup-vs-delivery negotiation** captured at order time (this sweep, §2.5)
6. A **payment + checkout** event that NutriMe explicitly does not own (per scope §"Out of scope")
7. A **post-delivery feedback loop** for what arrived, what substituted, what didn't ([sweep #12](../12-feedback-loops/scope.md) + sweep #11 §passive feedback)

Steps 4 and 5 are where the integration landscape varies most sharply between providers; steps 1–3 are common across all of them.

### 2. Instacart deep dive (primary US integration target)

#### 2.1 Instacart Developer Platform (IDP) — what's actually offered

Instacart maintains a developer platform under the brand **Instacart Developer Platform (IDP)** at [docs.instacart.com](https://docs.instacart.com), formerly marketed in part as "Instacart Connect" and "Instacart Platform." As of 2025–2026 the publicly documented surface includes:

- **Recipe Page API ("Create Recipe" / Recipe Pages)** — POST a recipe (title, ingredients with quantities + units, optional image + instructions) and receive a `products_link_url` that opens an Instacart-hosted recipe-shopping page. Items are matched server-side to retailer SKUs at the user's address. The user picks a retailer, reviews/edits substitutions, and checks out on Instacart. **This is the canonical recipe-to-cart pathway and the one most third-party apps use.**
- **Shopping List API ("Create Shopping List")** — same idea but accepts an arbitrary item list rather than a recipe with instructions. Returns a shareable URL that opens a pre-populated cart on Instacart.
- **Products Link API** — convert a list of UPCs / product references into a deep link to Instacart with those items added.
- **Idempotency-keyed POST endpoints** with API-key auth (header `Authorization: Bearer …`).

The IDP path that **does not** exist publicly:

- **No public server-side checkout API** for indie tier. NutriMe cannot place an order on a user's behalf via IDP without a partner-tier agreement (and even then, fulfillment / checkout typically remains on Instacart's surface).
- **No public "search SKUs at this store" API** at indie tier. SKU resolution happens inside Instacart's matching layer when the user opens the generated link.
- **No public substitution-preference write** at indie tier — substitutions are negotiated on Instacart's surface at order time.

This shapes NutriMe's architecture: the system constructs a normalized ingredient list, calls Recipe Page or Shopping List API to get a `products_link_url`, and hands the user off to Instacart for retailer selection + substitution + checkout. The "boom, shows up at my door" promise is **fulfilled by Instacart's stack at the last mile** rather than by NutriMe directly.

#### 2.2 Access tiers — indie vs. partner

Two effective tiers as of early 2026 [VERIFY-AT-ADOPTION]:

- **Self-serve / Indie tier (IDP "developer" access)** — sign up for a developer account at [docs.instacart.com](https://docs.instacart.com), generate API keys, call Recipe Page / Shopping List / Products Link endpoints. Rate-limited but no formal partnership required. Suitable for personal-use, hobbyist, and small-scale integrations. **This tier is the right fit for NutriMe under the personal-use distribution scope.**
- **Partner / Connect tier** — formal commercial agreement with Instacart, required for: deeper retailer-side integrations, white-label experiences, fulfillment-API access, ad-tech integration, revenue-share affiliate programs, higher rate limits, branded recipe-page customization. Goes through Instacart Business Development; intake is contact-form gated.

**Partner-tier approval timeline [VERIFY-AT-ADOPTION]:** historical reports from publishers integrating with Instacart Connect indicate timelines on the order of weeks to months from initial outreach to signed agreement, with the longer end for non-publisher / non-CPG integrations. Indie-tier sign-up is self-serve and effectively immediate.

#### 2.3 Coverage — "~95% US household reach"

Instacart's marketing materials cite reach figures in the 85–95% range of US households, citing aggregate retailer-partner coverage across ~1,500 retail banners and ~85,000+ stores [VERIFY-AT-ADOPTION — exact percentages drift]. Practical observations:

- **Urban + suburban dense coverage is real and broad** — most metros have 5–20+ banners available at a given ZIP code.
- **Rural coverage is patchy** — some ZIPs see only one banner (often a regional grocer); some have no Instacart-served retailer and fall back to Walmart/Kroger/Amazon-direct.
- **The 95% figure is best read as "share of US households for which at least one Instacart-served retailer can deliver"**, not "any retailer the user wants is available everywhere."

For NutriMe: assume Instacart works for the vast majority of US users, and design the fallback path (§6) for the long tail.

#### 2.4 Pricing model (consumer-facing)

Per the publicly documented Instacart pricing structure [VERIFY-AT-ADOPTION]:

- **Delivery fee** — typically $3.99–$7.99 per order for non-members, scaling with order timing and basket size.
- **Service fee** — ~5% of order subtotal (separate from tip), applied to all orders.
- **Per-item markup** — many retailers' in-store prices are marked up on Instacart (commonly cited as ~15% on average; varies by retailer; some retailers like Costco have known higher markups, some banners maintain in-store parity for members). **Markup transparency varies; NutriMe should surface this to users where possible.**
- **Heavy / bulky surcharges** — extra fee on items like bottled water, pet food, large bags of flour, etc.
- **Small basket fee** — orders under a threshold (commonly $35) incur additional fee.
- **Tip** — driver tip is separate, default 5%, user-adjustable.
- **Instacart+ membership** — ~$99/year (or $9.99/mo) [VERIFY-AT-ADOPTION] — includes free delivery on $35+ orders, reduced service fees, and member-only pricing on some items. For a user planning weekly grocery delivery, membership crosses break-even quickly.

NutriMe's role: surface the cost structure honestly, including markup, so the user sees the convenience-vs-cost tradeoff (per [Constitutional Rule 2: evidence/transparency over gating](../00-meta/constitutional-rules.md#rule-2--evidence-transparency-over-evidence-gating) generalized to commerce transparency).

#### 2.5 Pickup vs. delivery + substitutions

- **Both supported.** Most Instacart retailers offer both delivery and pickup; pickup avoids delivery fee and tip; substitutions still apply.
- **Retailer availability per modality varies.** Some banners are pickup-only at certain ZIPs; some are delivery-only. The IDP-generated link respects this when the user selects a retailer.
- **Substitution flow** — at order build time, the user can set per-item substitution preferences ("best match," "specific replacement," "do not substitute," "refund if unavailable"). At pick time, the shopper can propose substitutions for items the user did not pre-set; the user approves/rejects in real time via push notification + chat. NutriMe does not control this flow at indie tier — the user negotiates it on Instacart's surface — but the system can advise the user on which substitutions are clinically safe (per [sweep #10](../10-clinical-condition-gating/scope.md)) before they enter checkout.

#### 2.6 Indie-tier ToS for personal use

Key ToS provisions to verify at adoption [VERIFY-AT-ADOPTION]:

- IDP Developer Terms permit personal-use, non-commercial integrations under the self-serve tier.
- Generated `products_link_url` URLs are intended for end-user consumption (the user opens the link, not the developer programmatically).
- Scraping Instacart's consumer-facing site to reverse-engineer SKU coverage / pricing is **prohibited** by the consumer ToS; any data the integration uses must come through documented APIs.
- Retailer-pricing data behind the IDP responses cannot be redistributed as a parallel database.
- Affiliate / referral revenue shares require partner-tier agreement.

These align with NutriMe's [legitimate-paid-pathway discipline](../11-recipe-sourcing/scope.md#3-curated-publishers-legitimate-paid-access): IDP indie tier is the legitimate channel; reverse-engineering retailer SKUs from the Instacart site is not.

### 3. US landscape survey (beyond Instacart)

#### 3.1 Amazon Fresh + Whole Foods

- **Amazon Fresh** — Amazon's first-party grocery delivery, available in many US metros. No public consumer-grocery ordering API for indie integrators. Amazon's published APIs (Selling Partner API, Product Advertising API) are seller / affiliate facing, not "build a cart for a user" facing.
- **Whole Foods Market** — integrated under Amazon's stack; same API constraints. Whole Foods orders place through the Amazon app / amazon.com/wholefoods.
- **Subscribe & Save** — Amazon's recurring-shipment program for shelf-stable goods. No public consumer-cart API; affiliates can deep-link to product pages but cannot construct a server-side recurring order on behalf of a user.
- **Indie integration verdict:** **Amazon is closed to recipe-to-cart use cases** at indie tier as of 2026. Fallback pattern is deep-link-per-item (Product Advertising API affiliate links) with the user manually clicking through. Some recipe sites use Amazon affiliate links per ingredient as a workaround.

#### 3.2 Walmart+

- **Walmart Grocery / Walmart+** — Walmart's first-party delivery + pickup. Same closed-API posture as Amazon for recipe-to-cart: no public "build a cart for this user" API.
- **Walmart APIs** — Walmart Open API (product data) is largely deprecated for general public access; current developer surface is the **Walmart Affiliate API** (deep-links to product pages, commission tracking) and **Walmart Marketplace APIs** (seller-side). No "build cart" endpoint.
- **Walmart+** — annual membership (~$98/year, or ~$12.95/mo) [VERIFY-AT-ADOPTION] including free delivery, fuel discount, Paramount+ bundle.
- **Indie integration verdict:** **Closed to NutriMe's primary use case**. Affiliate deep-links to individual products are the only indie path. Notably, Instacart-served Walmart is limited / regional as Walmart pulled away from Instacart in many markets to favor its own delivery — verify which markets currently have Walmart-on-Instacart.

#### 3.3 Kroger + Kroger Cart API

- **Kroger** — second-largest US grocer, ~2,800 stores under banners including Kroger, Ralphs, King Soopers, Fred Meyer, Harris Teeter, Smith's, Fry's, QFC, Mariano's, Pick 'n Save, Food 4 Less. Predominantly Midwest/South/West; thin in Northeast and Florida.
- **Kroger Developer API** — at [developer.kroger.com](https://developer.kroger.com) — historically the most indie-friendly US grocery API. Documented surfaces include: **Products API** (search by store), **Locations API** (find stores), **Identity API** (OAuth for Kroger user accounts), and the **Cart API** which allows authenticated server-side addition of items to a Kroger user's cart. The user then completes checkout on Kroger's surface.
- **Significance:** Kroger is **the only major US chain that historically supports server-side cart construction at indie tier** for an authenticated user. This makes it the natural complement to Instacart's recipe-link path: Instacart for users in Instacart-strong ZIPs, Kroger Cart API for Kroger-served ZIPs that prefer first-party.
- **Caveats [VERIFY-AT-ADOPTION]:** Kroger's developer terms have evolved; current OAuth scopes and Cart API availability for non-partner developers should be re-verified. Some scopes have moved behind partner agreements over time.

#### 3.4 Target / Shipt

- **Target** — first-party delivery + pickup (Drive Up). No public consumer-cart API.
- **Shipt** — owned by Target since 2017; provides delivery for Target + a network of additional grocers (some overlap with Instacart's roster). Shipt-published API is partner/seller side, not consumer-cart.
- **Indie integration verdict:** Closed at indie tier. Target is reachable via Instacart in some markets.

#### 3.5 FreshDirect

- **FreshDirect** — Northeast US (NYC metro + surrounds) first-party delivery, owned by Getir → unwound; current ownership in flux as of 2026 [VERIFY-AT-ADOPTION]. No public indie API.
- **Coverage:** narrow geographic footprint; high-quality fresh focus.

#### 3.6 Misfits Market + Imperfect Foods

- **Misfits Market** + **Imperfect Foods** (the two merged in 2022) — subscription-box delivery of "ugly produce" + pantry staples nationwide via UPS. No public cart API; consumer-facing site / app only.
- **Pattern:** weekly customizable box rather than on-demand cart. Useful for the "regular staples background subscription + Instacart for fresh-this-week" dual-channel pattern but not a primary recipe-to-cart channel.

#### 3.7 Regional grocers

- **Wegmans** (Northeast) — Wegmans Meals 2GO + delivery; no public cart API; Instacart partnership for delivery in many ZIPs.
- **Publix** (Southeast) — heavy Instacart partner; Publix-direct delivery limited; no public cart API.
- **H-E-B** (Texas) — first-party delivery (Favor, owned by H-E-B); strong loyalty + curbside; no public cart API.
- **Trader Joe's** — **no online ordering, no delivery, no API.** Brick-and-mortar only by policy. NutriMe cannot integrate with Trader Joe's; can only surface "you'd find this at TJ's, here's the in-store list" as a fallback for users who want to add a TJ run.
- **Aldi** (US) — uses Instacart for delivery; no first-party indie API.
- **Lidl** (US, East Coast) — first-party online ordering in some markets; no public indie API.

#### 3.8 Other delivery aggregators

- **DoorDash** — expanded into grocery delivery via DashMart + retailer partnerships (Albertsons, Safeway, etc.). DoorDash Drive API exists for partners, not for indie recipe-to-cart.
- **Uber Eats / Cornershop** — Uber acquired Cornershop in 2021 and merged into Uber Eats Grocery. Some retailer cart deep-link patterns exist; partner-side APIs only.
- **Gopuff** — convenience-store delivery model (snacks, basics, alcohol); not a primary grocery channel.

#### 3.9 US landscape summary table

| Provider | Recipe-to-cart deep link | Server-side cart API (indie) | Best fit for NutriMe |
|---|---|---|---|
| **Instacart** | Yes (IDP Recipe Page) | Cart on Instacart surface | **Primary channel** |
| **Kroger** | Via Cart API + manual recipe link | Yes (Cart API, OAuth) | **Secondary channel** for Kroger ZIPs |
| **Amazon Fresh / Whole Foods** | Affiliate deep-links per item | No | Per-item fallback only |
| **Walmart+** | Affiliate deep-links per item | No | Per-item fallback only |
| **Target / Shipt** | No | No | Reach via Instacart where available |
| **FreshDirect** | No | No | Manual list export (NYC users) |
| **Misfits Market / Imperfect Foods** | No | No | Background subscription complement |
| **Trader Joe's** | N/A | N/A | Manual list export only |

### 4. International landscape survey

Per [Constitutional Rule 9 (geographic neutrality)](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing), the international landscape is treated with equal seriousness to the US. The "boom, shows up at my door" promise is geographically conditional — the integration landscape per country dictates which fallback patterns surface.

#### 4.1 United Kingdom

- **Tesco** — largest UK grocer (~28% market share). Tesco runs a public **Tesco Grocery API** (formerly Tesco Labs) for product search, store locator, and historically a cart API; current public-API status [VERIFY-AT-ADOPTION] — the original open Tesco Labs program was wound down in 2015, with subsequent partner-side surfaces. Tesco has the largest historical API surface of any UK grocer.
- **Sainsbury's** — ~15% share. No documented public consumer-cart API. Strong own-brand portfolio.
- **Ocado** — technology-forward online-only grocer; powers Ocado Smart Platform (OSP) sold to international grocers (Kroger US, Casino FR, Aeon JP, Coles AU, etc.). OSP is a B2B platform, not an indie consumer-cart API. Ocado's consumer site has no public cart API.
- **Asda** — Walmart-divested; first-party delivery; no public indie API.
- **Morrisons** — partnered with Amazon for delivery in some markets; no public indie API.
- **Waitrose** — premium, partnered with John Lewis. No public indie API.
- **Instacart UK** — Instacart entered the UK in 2022 via a partnership with Aldi UK (delivery in select areas) [VERIFY-AT-ADOPTION]. Coverage is narrow vs. US.
- **UK aggregators / specialty** — **Gousto** (meal-kit, out per scope), **Mindful Chef** (meal-kit, out), **Riverford / Abel & Cole** (organic-box subscriptions, no recipe-to-cart APIs).

**UK verdict:** No clean Instacart-equivalent. Direct-to-retailer is the norm; Tesco has the most history of open APIs. Fallback pattern (deep-link per-item or printable list export) likely dominates for UK users.

#### 4.2 Canada

- **Loblaws / PC Express** — largest Canadian grocer (Loblaws, Real Canadian Superstore, No Frills, Provigo, Zehrs, Fortinos, Maxi). PC Express is the delivery + pickup brand. No public indie cart API.
- **Sobeys / Voilà** — Voilà by Sobeys is the Ocado-powered online delivery brand (Toronto + Montreal + Calgary metros). Powered by Ocado Smart Platform, which is B2B-only.
- **Metro** — Quebec-based, eastern Canada. No public indie API.
- **Walmart Canada** — same posture as US Walmart; no indie cart API.
- **Instacart Canada** — operates in major Canadian metros, partnered with Lobloblaws-banner stores (Real Canadian Superstore, Provigo), Costco Canada, M&M Food Market, Walmart Canada in some areas. Coverage narrower than US Instacart but the same **IDP recipe-to-cart path works for Canadian retailers** in served markets.

**Canada verdict:** Instacart Canada is the natural extension of the US-primary path for Canadian users in served metros. Loblaws / PC Express is the dominant first-party for unserved areas; no indie API.

#### 4.3 France

- **Carrefour** — largest French grocer; Carrefour Drive (pickup) + delivery. Documented retailer-side / supplier APIs but no public indie consumer-cart API. Carrefour is a notable **Ocado Smart Platform partner** (Casino was the first Ocado partner in France).
- **Auchan** — second-largest; same posture (no public indie cart API).
- **Leclerc** — cooperative model, large; Leclerc Drive is the largest French click-and-collect operation. No public indie API.
- **Monoprix** — Casino group, urban premium. Online via Monoprix.fr + delivery. No public indie API.
- **Casino group** — backed Ocado Smart Platform deployment in France.
- **La Belle Vie / Houra / Cdiscount Express** — secondary online delivery; no public indie APIs.

**France verdict:** No Instacart-equivalent. Direct-to-retailer with manual cart-build or list export is the dominant pattern.

#### 4.4 Germany

- **Rewe** — largest German full-service online grocer; **Rewe.de** has structured ordering. No public consumer-cart API; partner-side affiliate program.
- **Edeka** — largest German grocery group overall; online ordering via picnic-style local services and partnerships. Limited online ordering footprint compared to brick-and-mortar dominance.
- **Lidl Online** — non-food + some food categories online; in-store-only for fresh.
- **Bringmeister** — online-only delivery (Berlin + select cities), Edeka-affiliated. No public API.
- **Picnic DE** — Dutch Picnic operates in parts of Germany (Düsseldorf, Köln, Aachen, etc.); same closed-app model as in NL.
- **Flink / Gorillas (now Getir-owned)** — convenience-instant delivery; not full-grocery.
- **Knuspr / Frischepost / Crisp** — niche online grocers.

**Germany verdict:** Direct-to-retailer with no indie cart API surface. Picnic's app-only closed model dominates where it operates.

#### 4.5 Netherlands

- **Albert Heijn** — dominant Dutch grocer (~35% market share); **Albert Heijn app + AH.nl**. Bonus loyalty card. Some structured-data surfaces (recipes via Allerhande, products via internal APIs that are reverse-engineered by community projects but not publicly documented for indie use).
- **Jumbo** — second-largest Dutch grocer; Jumbo.com online ordering. No public indie API.
- **Picnic** — technology-forward online-only grocer (NL + DE + FR), app-only, planned-route delivery model. Closed app, no public API.
- **Crisp** — premium app-only NL grocer.

**Netherlands verdict:** Albert Heijn is the de-facto national grocery interface; no public indie cart API. Some hobbyist tooling exists but lives outside ToS-compliant boundaries.

#### 4.6 Iberia (Spain + Portugal)

- **Mercadona** — largest Spanish grocer (~25% share). Online ordering via mercadona.es; no public indie API. Limited delivery footprint relative to brick-and-mortar.
- **El Corte Inglés / Hipercor** — premium dept-store-affiliated grocer; online via elcorteingles.es + supercor.com. No public indie API.
- **Carrefour España** — French Carrefour's Spanish ops; same posture as French Carrefour.
- **Continente / Pingo Doce** (Portugal) — first-party online ordering; no public indie API.
- **Glovo** — Barcelona-headquartered delivery aggregator (Delivery Hero–owned), covers groceries via partnerships in many EU + LatAm markets. Partner-side APIs.

**Iberia verdict:** Direct-to-retailer; no public indie cart APIs. Glovo provides an aggregator surface in some metros for partner-tier integrators only.

#### 4.7 Nordics

- **ICA** (Sweden) — largest Swedish grocer. Online ordering via ica.se; no public indie cart API (some structured product data surfaces).
- **Coop** (Sweden, Denmark, Norway, Finland — separate cooperatives) — online ordering varies by national co-op. No public indie API.
- **Mathem** (Sweden) — online-only grocer; tech-forward; no public indie API.
- **Axfood / Willys / Hemköp** — Swedish discount + mid-market; online ordering; no public indie API.
- **Kesko / K-Ruoka** (Finland) — online ordering via k-ruoka.fi; no public indie API.
- **Salling Group / Bilka / Føtex / Netto** (Denmark) — online ordering via group sites; no public indie API.
- **Oda** (Norway, formerly Kolonial.no) — tech-forward online grocer, expanded into Sweden + Finland (later contracted); no public indie API.

**Nordics verdict:** Multiple tech-forward national players (Mathem, Oda) but uniformly closed at indie tier. Direct-to-retailer with manual list export is the fallback.

#### 4.8 Ireland

- **Tesco IE** — same Tesco platform as UK, separate operations. Same API caveats as Tesco UK.
- **SuperValu** — Musgrave Group; delivery + click-and-collect. No public indie API.
- **Dunnes Stores** — limited online grocery (expanding). No public indie API.
- **Lidl IE / Aldi IE** — primarily in-store; expanding online slowly.

**Ireland verdict:** Tesco IE is the one with most API history; otherwise direct-to-retailer.

#### 4.9 Switzerland + Austria

- **Migros** (CH) — largest Swiss retailer (cooperative); online via migros.ch + LeShop (Migros-owned online grocer). LeShop has a longer online history than most Swiss grocers. No public indie cart API.
- **Coop** (CH, separate from Nordic Coop) — second-largest; online via coop.ch + coop@home. No public indie cart API.
- **Billa** (AT) — Rewe-owned Austrian chain; online via billa.at + Billa Plus. No public indie API.
- **Spar** (AT) — Spar Austria + Interspar; some online ordering; no public indie API.

**CH/AT verdict:** Direct-to-retailer; no public indie cart APIs. LeShop has the longest online ordering history but remains closed to third-party integration.

#### 4.10 International landscape summary

| Region | Closest "Instacart-equivalent" | Indie cart API anywhere? | Dominant fallback |
|---|---|---|---|
| **UK** | None at scale; Instacart UK (Aldi only, narrow) | Tesco historically, status uncertain | Direct-to-retailer manual cart |
| **Canada** | **Instacart Canada** (subset of US coverage) | Same as US (Instacart IDP) | Instacart IDP for served metros, manual elsewhere |
| **France** | None | None | Direct-to-retailer manual cart |
| **Germany** | None (Picnic in some metros) | None | Direct-to-retailer manual cart |
| **Netherlands** | None (Picnic + AH) | None | AH app handoff |
| **Iberia** | None (Glovo for partners only) | None | Direct-to-retailer manual cart |
| **Nordics** | None (Mathem, Oda) | None | Direct-to-retailer manual cart |
| **Ireland** | None | Tesco IE historically | Direct-to-retailer manual cart |
| **CH / AT** | None | None | Direct-to-retailer manual cart |

**Cross-cutting international finding:** outside North America there is **no indie-tier recipe-to-cart aggregator equivalent to Instacart**. The dominant pattern is direct-to-retailer, and the dominant retailer cart API posture is closed at indie tier across all surveyed markets. This makes the **fallback patterns (§6) the primary path for non-US/CA users**, with direct-to-retailer integrations possible only if NutriMe pursues partnership tiers per country (out of scope for personal use).

### 5. The "no clean indie path" problem and the Ocado wrinkle

Ocado Smart Platform (OSP) is worth a separate mention because it powers a striking number of grocers globally (Kroger US, Casino FR, Sobeys/Voilà CA, Coles AU, Aeon JP, Morrisons UK, others). OSP is a **B2B fulfillment + storefront platform sold to grocers**, not a developer API NutriMe could integrate with. It is mentioned here so we recognize: when several different national grocers are technically running the same backend, that backend is still not exposed to indie developers.

Conversely, the **Instacart Connect / IDP openness is somewhat anomalous** in the global grocery-tech landscape. Most national grocers treat their cart and inventory APIs as competitive moats. Instacart's openness reflects its aggregator business model — they want third-party apps to drive orders into their network.

### 6. Fallback patterns when no API is available

Per scope, the system needs graceful degradation when the primary integration path is unavailable. Patterns (in declining order of user convenience):

#### 6.1 Pre-populated deep-link to retailer app

When the retailer supports URL-based cart construction (Instacart, Kroger via Cart API, some affiliate-link patterns), open the retailer's app/site with items already added. User reviews, adjusts, checks out.

#### 6.2 Per-item deep-link list

When the retailer doesn't support multi-item cart construction but does support per-product URLs (Amazon affiliate links, most retailer product pages), present an ordered list of "add this item" links. User clicks each. Higher friction but preserves "click-not-type" UX.

#### 6.3 Printable / shareable structured list

A categorized shopping list (produce, dairy, pantry, frozen, etc.) optimized for in-store navigation. Can be:

- PDF / print-friendly HTML
- Shared to a phone via QR code or messaging
- Exported to standard formats: **plain text, Markdown, CSV, OurGroceries / AnyList / Bring! import format** (these list apps support import/share patterns)

#### 6.4 Email / SMS list export

Push the categorized list to the user's preferred channel. Works in any market, any retailer relationship, any device.

#### 6.5 Manual cart-build with item-by-item guidance

When the user must build the cart manually in a retailer's app, NutriMe can surface the list one item at a time with a "found it / not found / substitute" inline confirmation. This is the hand-holding fallback for users who want NutriMe to remain "in the loop" during the manual build.

#### 6.6 Multi-channel split

When no single retailer carries everything: split the list across retailers (e.g., Instacart for fresh + Amazon Subscribe & Save for pantry staples + a local specialty shop list for the unusual items). Surface this as a two-or-three-cart flow rather than failing the order.

**Design principle:** the fallback path should never feel like a failure mode — it should feel like a deliberate format choice. International users who never see Instacart should still feel "boom, shows up at my door" within their market's constraints.

### 7. Recipe-to-cart translation patterns

This is where the cooking layer ([sweep #11](../11-recipe-sourcing/scope.md)) meets the grocery layer. The transforms are:

#### 7.1 Ingredient deduplication across the week

When a week's plan calls for "1 onion" in Monday's stir-fry, "½ onion" in Wednesday's soup, and "2 onions" in Friday's sauce, the cart entry is "4 onions" (or "1 bag of yellow onions") not three separate entries. Deduplication operates on:

- **Canonical ingredient identity** — "yellow onion," "white onion," "red onion" are different entries; "onion" without color is matched to the user's pantry default.
- **Aggregation respecting recipe-context** — onions chopped fine for a soffritto, sliced for a stir-fry, and pickled for a topping are all "onion" at the cart level even though they're distinct in the kitchen.
- **Spillover handling** — if a recipe calls for ½ onion, the other ½ goes back to the pantry tracker (§7.5).

This is implemented via canonical ingredient IDs joined to the food-composition database ([sweep #2](../02-food-composition-databases/scope.md)). **Mealie**, **Tandoor Recipes**, and **Grocy** are the main open-source references implementing this pattern; their schemas + algorithms are valuable prior art.

#### 7.2 Quantity unit normalization

Recipe units (cups, tbsp, "a handful," "a knob," "a bunch") → grocery purchase units (lbs, oz, count, packages, mL). Requires:

- **Volume → mass conversions per ingredient** (1 cup of flour ≠ 1 cup of water in grams). USDA FDC and EuroFIR provide the per-ingredient density data; some open libraries (Python's `pint` for general units; recipe-specific libraries from open meal-planners) cover the cooking edge cases.
- **Vague-quantity resolution** — "a handful" ≈ 30g for a salad green, ≈ 100g for nuts, ≈ 60g for berries. The system needs lookup tables, ideally tagged with culinary tradition (a French "pincée" ≠ an American "pinch" ≠ a Japanese "hito-tsumami"). USDA "household measures" + EuroFIR "household portion sizes" are the references.
- **Purchase unit rounding** — "you need 220g of carrots" rounds to "1 lb / 500g bag" with the spillover going to pantry (§7.5).

#### 7.3 Substitution logic

Two layers:

- **Availability substitution** — recipe calls for shallots, store has only red onions; substitute with a culinary-equivalence rule. Sources for substitution rules: **The Food Substitutions Bible** (David Joachim), **The Cook's Thesaurus** (foodsubs.com — long-standing online substitution reference, free), **The CIA's Garde Manger / Professional Chef substitution appendices**, **Larousse Gastronomique** (general culinary reference), **Oxford Companion to Food** (Davidson, scholarly). These are Tier 4 culinary references for cooking substitution; for **clinical substitution** (e.g., low-FODMAP swaps, low-K swaps for CKD), the substitution must be evidence-tier-tagged per [sweep #10](../10-clinical-condition-gating/scope.md) and surfaced with appropriate provenance.
- **Condition-aware substitution** — when an ingredient triggers a clinical contraindication (allergens, drug interactions, condition-specific avoid lists), substitute with a clinically appropriate alternative + surface the swap to the user with the "consult professional" disclosure per [Constitutional Rule 1](../00-meta/constitutional-rules.md#rule-1--consult-a-professional). Per [Constitutional Rule 10](../00-meta/constitutional-rules.md#rule-10--user-decides-with-full-context), the system surfaces the conflict and lets the user decide rather than silently swapping.

**Pattern:** maintain a substitution graph keyed on canonical ingredient ID, with edges weighted by (a) culinary equivalence, (b) clinical safety for the user's profile, (c) availability at the user's selected retailer. The cart-translation layer queries this graph rather than embedding swaps inline in recipes.

#### 7.4 Pantry deduction (without becoming a logging app)

[Constitutional Rule 3](../00-meta/constitutional-rules.md#rule-3--no-food--macro--calorie-logging) forbids user-initiated food/macro/calorie logging. Pantry tracking must respect this boundary. Patterns that work:

- **Inferred-from-orders pantry** — when an Instacart order is placed via NutriMe, the system infers what entered the pantry. No user data entry.
- **Recipe-driven decrement** — when the system suggests a meal and the user confirms cooked + ate (per the [intake / passive-feedback pattern](../00-meta/intake-pattern.md)), decrement the ingredients used. No quantity-entry step; the system uses the recipe's documented quantities.
- **Periodic optional pantry sweep** — *not a daily check-in*; a low-frequency "want to tell me what's in your pantry?" prompt that the user can ignore. Used to seed the pantry after onboarding or after a long absence.
- **Spillover ledger** — the leftover from quantity-rounding (§7.2) sits in pantry until consumed.
- **Decay assumptions** — perishables time out from the inferred pantry on configurable horizons (lettuce: 5 days; eggs: 3 weeks; canned beans: indefinite). Not "did you throw it away?" — just a heuristic.

**Boundary check:** none of these require the user to initiate a log entry. The system maintains the pantry from observable events (orders placed, meals confirmed) + reasonable defaults. The user can override but is not asked to track.

#### 7.5 Brand selection + budget tier

- **Brand-tier mapping** — generic / store-brand / national-brand / organic / specialty. User-set preference at intake, overridable per ingredient.
- **Budget-tier mapping** — total cart cost target with per-category sliders (e.g., "premium on produce, budget on pantry"). Surfaced as a slider rather than a calculator (no logging discipline).
- **Source-of-truth for tiers** — Instacart's catalog distinguishes generic vs. branded; for brand quality assessments, **Consumer Reports** (US, paid), **Which?** (UK, paid), **Stiftung Warentest** (DE, paid), **Test-Achats / Que Choisir** (BE / FR, paid) are the consumer-testing authorities. Free + open: **Open Food Facts** has community-contributed quality / processing tags (Nutri-Score, NOVA classification) per product, license ODbL.

#### 7.6 Bulk vs. precise (waste optimization)

When a recipe needs 1 lb of flour and the smallest package is 5 lb, options are:

- **Buy the 5 lb if shelf-stable + frequently used** — log the surplus to pantry (§7.4); future recipes draw down.
- **Buy the 1 lb if shelf-life is short or use is one-off** — accept the price-per-unit hit to avoid waste.
- **Bulk-section buy** — some retailers (Whole Foods, regional co-ops, Wegmans) offer bulk-bin by-weight purchase. Instacart sometimes supports this via per-weight items.

The decision is per-ingredient + per-user (single-person households have less absorption capacity for bulk than family households — see [sweep #9 multi-user household](../09-multi-user-household/scope.md)). Surface the decision rather than hiding it: "I'd buy the 5 lb bag — flour keeps; you'll use the rest in 3 weeks. Want me to buy the 1 lb instead?"

#### 7.7 Multi-store cart split

When no single retailer carries everything (specialty Asian ingredients, specific imported brands, niche dietary products), the cart splits. UX patterns:

- **Tiered presentation** — primary cart (covers 80%) + supplemental cart (the 20% specialty items at a different retailer or shop). User decides whether to do the supplemental run.
- **Retailer ranking** — system ranks retailers by coverage of the week's list, surfaces top 2–3, lets user pick.
- **Substitution-vs-split tradeoff** — for missing items, offer either "substitute on the primary retailer" or "split into a second cart." User decides per item.

#### 7.8 Open-source prior art

Worth pointing the implementation work at these projects when scope broadens:

- **Mealie** ([github.com/mealie-recipes/mealie](https://github.com/mealie-recipes/mealie)) — self-hosted recipe manager with shopping-list aggregation, ingredient parsing, household sharing. Deduplication + unit normalization patterns are documented in code.
- **Tandoor Recipes** ([github.com/TandoorRecipes/recipes](https://github.com/TandoorRecipes/recipes)) — similar to Mealie, with stronger meal-planning + shopping-list integration. Active community.
- **Grocy** ([github.com/grocy/grocy](https://github.com/grocy/grocy)) — ERP-for-the-pantry: tracks stock, expiration, shopping, recipes, meal plans. Pantry-deduction patterns are mature. Active project.
- **OurGroceries / AnyList / Bring!** — consumer apps with import/export formats that any list-export fallback should target.
- **paprika-recipe-format** — Paprika's exchange format is a de-facto standard for recipe + list interchange.

### 8. ToS landscape for indie / personal use

| Provider | Indie API access? | Server-side cart? | Scraping permitted? | Notes |
|---|---|---|---|---|
| **Instacart IDP** | Yes (self-serve) | Cart on Instacart surface | No | Indie tier fits personal-use scope. |
| **Kroger Developer** | Yes (registered) | Yes (Cart API) | No | Most permissive US chain at indie tier. |
| **Amazon Product Advertising / Affiliate** | Yes (registered) | No | No | Per-item deep-links only. |
| **Walmart Affiliate** | Yes (registered) | No | No | Per-item deep-links only. |
| **Tesco** | Historical Labs program; current status uncertain | Historically yes | No | VERIFY-AT-ADOPTION. |
| **Most other national grocers (UK, FR, DE, NL, ES, SE, IT, CH, AT, CA-direct)** | No public indie tier | No | No (ToS forbids) | Fallback to manual / list export. |
| **Albert Heijn / others with reverse-engineered community APIs** | No public docs | Community projects exist outside ToS | No (ToS forbids) | NutriMe should not depend on reverse-engineered APIs even if they exist. |

**Cross-cutting ToS principle:** **scraping is uniformly prohibited** by retailer consumer ToS. The discipline already established in [sweep #11 §3](../11-recipe-sourcing/scope.md) (legitimate paid pathways for recipes) extends here directly: **only API surfaces explicitly opened by the retailer count as legitimate channels.** Where no API exists, the fallback is user-initiated (the user opens their own retailer app under their own account; NutriMe provides the structured list; the user types or pastes).

This honors the constitutional discipline at [Constitutional Rule 4 (no recipe generation)](../00-meta/constitutional-rules.md#rule-4--no-recipe-generation) generalized to grocery data: no fabrication of data we don't legitimately have access to, no scraping of data the source forbids, transparent use of data we do have legitimate access to.

### 9. Answers to the "open questions for the research"

> **Q: What is the realistic state of Instacart IDP indie access in 2026? Is the partner program friendly to personal-use developers, or does it require commercial agreement?**

The IDP self-serve / indie tier exists and is appropriate for personal-use developers. Recipe Page + Shopping List + Products Link APIs cover the recipe-to-cart use case without requiring a partnership. Partner-tier (Connect) is for white-label, fulfillment-API, ad-tech, revenue-share — none of which NutriMe needs at personal-use scope. **NutriMe can build against Instacart IDP today without a commercial agreement.** [VERIFY-AT-ADOPTION]

> **Q: Which retailers genuinely support recipe-to-cart deep-linking at the URL level (vs. "click here, then build cart manually")?**

- **True URL-level recipe-to-cart:** Instacart (IDP Recipe Page) is the gold standard. Kroger Cart API (with OAuth) supports server-side cart construction.
- **Per-item deep-link only:** Amazon, Walmart (via affiliate), most other US chains via Instacart-served banners.
- **No deep-link path:** most non-US national grocers — direct-to-retailer manual cart with NutriMe providing the structured list.

> **Q: What's the state of Kroger Cart API — still the main indie path for server-side cart building?**

Yes. The Kroger developer portal at [developer.kroger.com](https://developer.kroger.com) continues to expose Products, Locations, Identity (OAuth), and Cart APIs. It remains the most indie-friendly server-side cart path among major US grocers. Caveat: scopes have been tightened over the years and current scope availability for Cart should be re-verified. Geographic coverage is Kroger-banner ZIPs (~2,800 stores, predominantly Midwest / South / West).

> **Q: For Western Europe: is there an "Instacart equivalent" that aggregates across retailers, or is everything direct-to-retailer?**

**No clean Instacart equivalent exists in Western Europe.** Instacart UK exists but only with Aldi, narrow coverage. Glovo aggregates in some EU markets but at partner tier, not indie. Picnic, Oda, Mathem, LeShop are tech-forward but single-retailer apps with no public APIs. The pattern is direct-to-retailer with manual cart-build or list export as the dominant fallback for European users.

> **Q: What recipe-to-cart translation patterns are published / open-source?**

Mealie, Tandoor Recipes, and Grocy are the three mature open-source references covering ingredient deduplication, unit normalization, pantry deduction, and meal-plan-to-shopping-list. Paprika's exchange format and OurGroceries / AnyList / Bring! import formats define the de-facto interchange layer. See §7.8.

> **Q: What pantry-tracking patterns work in practice without becoming a "logging app"?**

The four-pattern combination in §7.4: (1) infer pantry contents from orders placed via NutriMe, (2) decrement on confirmed-cooked meals using documented recipe quantities (no user-entered numbers), (3) optional low-frequency seeding sweeps, (4) decay heuristics for perishables. The user never opens a logging form. The boundary holds as long as pantry is **observed, not asked**.

> **Q: For substitution logic: what published sources (CIA texts, culinary substitution databases) inform ingredient swaps?**

The Food Substitutions Bible (Joachim), The Cook's Thesaurus (foodsubs.com — free online), CIA's Garde Manger + Professional Chef substitution appendices, Larousse Gastronomique, Oxford Companion to Food (Davidson). These are Tier 4 culinary references appropriate for cooking-substitution logic. **Clinical substitutions** (allergen swaps, low-FODMAP, low-K renal, low-Na cardiac, etc.) require Tier 1/2/3-grounded substitution rules sourced from clinical-nutrition literature per [sweep #10](../10-clinical-condition-gating/scope.md), not the culinary references.

### 10. Gaps + suggestions for follow-up

- **Live verification pass needed.** The IDP rate limits, exact pricing of Instacart+, partner-tier intake timing, Kroger Cart scope availability, Tesco's current API status, and Instacart-Aldi UK coverage all need live re-fetch before any implementation work. Web access was denied this sweep.
- **Subscribe & Save patterns deserve a deeper look** for the "shelf-stable staples background subscription" complement to Instacart's weekly fresh order. Worth its own sub-sweep.
- **Open Food Facts integration** — community-maintained, ODbL-licensed product database with NOVA + Nutri-Score per product. Cross-cuts this sweep + sweep #2 (food composition). Worth a dedicated cross-reference.
- **Recipe-to-cart unit normalization is the tightest engineering problem in this layer.** USDA FDC + EuroFIR have the data; mapping it to Instacart's purchase units is fiddly. A small reference implementation against a 50-recipe corpus would surface the edge cases quickly.
- **International partner-tier discovery.** If NutriMe's distribution intent ever broadens beyond personal use, a sweep of national-grocer partner programs (Tesco, Carrefour, Rewe, Albert Heijn, Coles AU) would unlock recipe-to-cart in markets currently stuck at "manual fallback."
- **Local / artisan / farmers-market integration** — entirely out of scope this sweep but a meaningful gap for users who prioritize local sourcing. CSA box services + farmers-market ordering platforms (e.g., Local Line, Barn2Door) are a separate landscape.

## References

> All web URLs accessed 2026-04-29 except where noted. Primary-source documentation linked for verifiability; pricing + access-tier specifics in this doc are time-sensitive and should be re-verified at adoption time per the methodology note above.

### Instacart

- **Instacart**. *Instacart Developer Platform — documentation*. [docs.instacart.com](https://docs.instacart.com). Accessed 2026-04-29.
- **Instacart**. *Instacart Developer Platform API reference*. [docs.instacart.com/developer_platform_api](https://docs.instacart.com/developer_platform_api). Accessed 2026-04-29.
- **Instacart**. *Instacart Connect (partner program landing)*. [www.instacart.com/company/instacart-connect](https://www.instacart.com/company/instacart-connect). Accessed 2026-04-29.
- **Instacart**. *Pricing and fees overview (consumer)*. [www.instacart.com/help/section/360007902791](https://www.instacart.com/help/section/360007902791). Accessed 2026-04-29.
- **Instacart**. *Instacart+ membership*. [www.instacart.com/instacart-plus](https://www.instacart.com/instacart-plus). Accessed 2026-04-29.
- **Instacart**. *Terms of Service (consumer)*. [www.instacart.com/terms](https://www.instacart.com/terms). Accessed 2026-04-29.
- **Instacart**. *Instacart Canada*. [www.instacart.ca](https://www.instacart.ca). Accessed 2026-04-29.

### US grocers / delivery

- **Kroger**. *Kroger Developer Portal*. [developer.kroger.com](https://developer.kroger.com). Accessed 2026-04-29.
- **Kroger**. *Cart API documentation*. [developer.kroger.com/reference/api/cart-api-public](https://developer.kroger.com/reference/api/cart-api-public). Accessed 2026-04-29.
- **Amazon**. *Product Advertising API 5.0*. [webservices.amazon.com/paapi5/documentation](https://webservices.amazon.com/paapi5/documentation/). Accessed 2026-04-29.
- **Amazon**. *Amazon Fresh*. [www.amazon.com/fmc/learn-more](https://www.amazon.com/fmc/learn-more). Accessed 2026-04-29.
- **Amazon**. *Whole Foods Market on Amazon*. [www.amazon.com/wholefoods](https://www.amazon.com/wholefoods). Accessed 2026-04-29.
- **Amazon**. *Subscribe & Save*. [www.amazon.com/subscribe-and-save](https://www.amazon.com/subscribe-and-save). Accessed 2026-04-29.
- **Walmart**. *Walmart Developer Portal*. [developer.walmart.com](https://developer.walmart.com). Accessed 2026-04-29.
- **Walmart**. *Walmart+ membership*. [www.walmart.com/plus](https://www.walmart.com/plus). Accessed 2026-04-29.
- **Walmart**. *Walmart Affiliate Program*. [affiliates.walmart.com](https://affiliates.walmart.com). Accessed 2026-04-29.
- **Target**. *Target Drive Up + Shipt*. [www.target.com/c/shipt](https://www.target.com/c/shipt). Accessed 2026-04-29.
- **Shipt**. *Shipt Developer / Partner overview*. [www.shipt.com](https://www.shipt.com). Accessed 2026-04-29.
- **FreshDirect**. *FreshDirect home*. [www.freshdirect.com](https://www.freshdirect.com). Accessed 2026-04-29.
- **Misfits Market**. *Misfits Market home*. [www.misfitsmarket.com](https://www.misfitsmarket.com). Accessed 2026-04-29.
- **Wegmans**. *Wegmans Meals 2GO*. [shop.wegmans.com](https://shop.wegmans.com). Accessed 2026-04-29.
- **Publix**. *Publix Delivery & Curbside Pickup*. [delivery.publix.com](https://delivery.publix.com). Accessed 2026-04-29.
- **H-E-B**. *Curbside & Home Delivery*. [www.heb.com/digital-services/curbside](https://www.heb.com/digital-services/curbside). Accessed 2026-04-29.
- **Trader Joe's**. *Frequently Asked Questions — online ordering*. [www.traderjoes.com/home/about-us/customer-relations](https://www.traderjoes.com/home/about-us/customer-relations). Accessed 2026-04-29.
- **Aldi US**. *Aldi delivery (via Instacart)*. [www.aldi.us/grocery-delivery](https://www.aldi.us/grocery-delivery). Accessed 2026-04-29.
- **Lidl US**. *Lidl Online*. [www.lidl.com](https://www.lidl.com). Accessed 2026-04-29.
- **DoorDash**. *DoorDash for Developers*. [developer.doordash.com](https://developer.doordash.com). Accessed 2026-04-29.

### UK + Ireland

- **Tesco**. *Tesco Grocery*. [www.tesco.com/groceries](https://www.tesco.com/groceries). Accessed 2026-04-29.
- **Tesco**. *Tesco Labs (historical)*. [www.tescolabs.com](https://www.tescolabs.com). Accessed 2026-04-29.
- **Sainsbury's**. *Sainsbury's Groceries*. [www.sainsburys.co.uk](https://www.sainsburys.co.uk). Accessed 2026-04-29.
- **Ocado**. *Ocado online grocer*. [www.ocado.com](https://www.ocado.com). Accessed 2026-04-29.
- **Ocado Group**. *Ocado Smart Platform*. [www.ocadogroup.com/about-us/our-solutions/ocado-smart-platform](https://www.ocadogroup.com/about-us/our-solutions/ocado-smart-platform). Accessed 2026-04-29.
- **Asda**. *Asda Groceries*. [groceries.asda.com](https://groceries.asda.com). Accessed 2026-04-29.
- **Morrisons**. *Morrisons Groceries*. [groceries.morrisons.com](https://groceries.morrisons.com). Accessed 2026-04-29.
- **Waitrose**. *Waitrose Online*. [www.waitrose.com](https://www.waitrose.com). Accessed 2026-04-29.
- **Instacart UK**. *Instacart UK with Aldi*. [www.instacart.com/aldi-uk](https://www.instacart.com/aldi-uk). Accessed 2026-04-29.
- **SuperValu Ireland**. [supervalu.ie](https://www.supervalu.ie). Accessed 2026-04-29.
- **Dunnes Stores**. [www.dunnesstoresgrocery.com](https://www.dunnesstoresgrocery.com). Accessed 2026-04-29.

### Canada

- **Loblaws / PC Express**. [www.pcexpress.ca](https://www.pcexpress.ca). Accessed 2026-04-29.
- **Voilà by Sobeys**. [www.voila.ca](https://www.voila.ca). Accessed 2026-04-29.
- **Metro Canada**. [www.metro.ca](https://www.metro.ca). Accessed 2026-04-29.
- **Walmart Canada**. [www.walmart.ca](https://www.walmart.ca). Accessed 2026-04-29.

### France

- **Carrefour**. [www.carrefour.fr](https://www.carrefour.fr). Accessed 2026-04-29.
- **Auchan**. [www.auchan.fr](https://www.auchan.fr). Accessed 2026-04-29.
- **E.Leclerc Drive**. [www.leclercdrive.fr](https://www.leclercdrive.fr). Accessed 2026-04-29.
- **Monoprix**. [www.monoprix.fr](https://www.monoprix.fr). Accessed 2026-04-29.
- **Casino**. [www.casino.fr](https://www.casino.fr). Accessed 2026-04-29.

### Germany

- **Rewe**. *Rewe Lieferservice + Abholservice*. [www.rewe.de](https://www.rewe.de). Accessed 2026-04-29.
- **Edeka**. [www.edeka.de](https://www.edeka.de). Accessed 2026-04-29.
- **Lidl Online**. [www.lidl.de](https://www.lidl.de). Accessed 2026-04-29.
- **Bringmeister**. [www.bringmeister.de](https://www.bringmeister.de). Accessed 2026-04-29.
- **Picnic Deutschland**. [picnic.app/de](https://picnic.app/de). Accessed 2026-04-29.

### Netherlands

- **Albert Heijn**. [www.ah.nl](https://www.ah.nl). Accessed 2026-04-29.
- **Jumbo**. [www.jumbo.com](https://www.jumbo.com). Accessed 2026-04-29.
- **Picnic**. [picnic.app](https://picnic.app). Accessed 2026-04-29.
- **Crisp**. [crisp.nl](https://crisp.nl). Accessed 2026-04-29.

### Iberia

- **Mercadona**. [www.mercadona.es](https://www.mercadona.es). Accessed 2026-04-29.
- **El Corte Inglés Supermercado**. [www.elcorteingles.es/supermercado](https://www.elcorteingles.es/supermercado). Accessed 2026-04-29.
- **Carrefour España**. [www.carrefour.es](https://www.carrefour.es). Accessed 2026-04-29.
- **Continente** (PT). [www.continente.pt](https://www.continente.pt). Accessed 2026-04-29.
- **Glovo**. [glovoapp.com](https://glovoapp.com). Accessed 2026-04-29.

### Nordics

- **ICA** (SE). [www.ica.se](https://www.ica.se). Accessed 2026-04-29.
- **Coop Sverige**. [www.coop.se](https://www.coop.se). Accessed 2026-04-29.
- **Mathem**. [www.mathem.se](https://www.mathem.se). Accessed 2026-04-29.
- **Axfood / Willys**. [www.willys.se](https://www.willys.se). Accessed 2026-04-29.
- **K-Ruoka** (FI). [www.k-ruoka.fi](https://www.k-ruoka.fi). Accessed 2026-04-29.
- **Salling Group / Bilka** (DK). [www.bilkatogo.dk](https://www.bilkatogo.dk). Accessed 2026-04-29.
- **Oda** (NO). [oda.com](https://oda.com). Accessed 2026-04-29.

### Switzerland + Austria

- **Migros**. [www.migros.ch](https://www.migros.ch). Accessed 2026-04-29.
- **LeShop (Migros)**. [www.leshop.ch](https://www.leshop.ch). Accessed 2026-04-29.
- **Coop Schweiz**. [www.coop.ch](https://www.coop.ch). Accessed 2026-04-29.
- **Billa Online** (AT). [shop.billa.at](https://shop.billa.at). Accessed 2026-04-29.
- **Spar Österreich**. [www.spar.at](https://www.spar.at). Accessed 2026-04-29.

### Open-source recipe-to-cart prior art

- **Mealie**. [github.com/mealie-recipes/mealie](https://github.com/mealie-recipes/mealie). License: AGPL-3.0. Accessed 2026-04-29.
- **Tandoor Recipes**. [github.com/TandoorRecipes/recipes](https://github.com/TandoorRecipes/recipes). License: AGPL-3.0. Accessed 2026-04-29.
- **Grocy**. [github.com/grocy/grocy](https://github.com/grocy/grocy). License: MIT. Accessed 2026-04-29.
- **Open Food Facts**. [world.openfoodfacts.org](https://world.openfoodfacts.org) (data: ODbL). Accessed 2026-04-29.
- **OurGroceries**. [www.ourgroceries.com](https://www.ourgroceries.com). Accessed 2026-04-29.
- **AnyList**. [www.anylist.com](https://www.anylist.com). Accessed 2026-04-29.
- **Bring!**. [www.getbring.com](https://www.getbring.com). Accessed 2026-04-29.
- **Paprika Recipe Manager**. [www.paprikaapp.com](https://www.paprikaapp.com). Accessed 2026-04-29.

### Substitution + culinary references

- **Cook's Thesaurus**. *Online ingredient substitution reference*. [www.foodsubs.com](https://www.foodsubs.com). Accessed 2026-04-29.
- Joachim, D. (2010). *The Food Substitutions Bible* (2nd ed.). Robert Rose. ISBN 978-0778802419.
- The Culinary Institute of America (2019). *The Professional Chef* (9th ed.). Wiley. ISBN 978-0470421352.
- The Culinary Institute of America (2012). *Garde Manger: The Art and Craft of the Cold Kitchen* (4th ed.). Wiley. ISBN 978-0470587805.
- Davidson, A. (2014). *The Oxford Companion to Food* (3rd ed.). Oxford University Press. ISBN 978-0199677337.
- Montagné, P. (2009). *Larousse Gastronomique* (latest English ed.). Clarkson Potter. ISBN 978-0307464910.

### Food composition + product data

- **USDA FoodData Central** (FDC). [fdc.nal.usda.gov](https://fdc.nal.usda.gov). Accessed 2026-04-29.
- **EuroFIR Food Composition**. [www.eurofir.org](https://www.eurofir.org). Accessed 2026-04-29.

### Cross-references within NutriMe

- [Sweep #2 — Food composition databases](../02-food-composition-databases/scope.md)
- [Sweep #9 — Multi-user household](../09-multi-user-household/scope.md)
- [Sweep #10 — Clinical condition gating](../10-clinical-condition-gating/scope.md)
- [Sweep #11 — Recipe sourcing](../11-recipe-sourcing/scope.md)
- [Sweep #12 — Feedback loops](../12-feedback-loops/scope.md)
- [00-meta — product framing](../00-meta/product-framing.md)
- [00-meta — constitutional rules](../00-meta/constitutional-rules.md)
- [00-meta — geographic scope](../00-meta/geographic-scope.md)
- [00-meta — citation style](../00-meta/citation-style.md)
- [00-meta — dynamic research expansion](../00-meta/dynamic-research-expansion.md)
