# Sweep #11 — Recipe Sourcing, Licensing, Attribution, Distribution

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Map the full landscape of recipe sourcing across paid commercial APIs, curated publishers (under legitimate paid access), open datasets, public-domain historical cookbook collections at depth, modern indexed cookbook databases, video sources (YouTube + institutional culinary academies), and non-Western cuisine sources (national culinary institutes, cultural heritage organizations, peer-recognized practitioners). Build a **qualification framework** for recipe sources rather than a fixed list, so new sources can be added by passing through the framework. Address recipe IP law, ToS, attribution / provenance architecture, recipe interchange formats, and **multi-modal recipe presentation infrastructure** so recipes can be surfaced in formats matched to user cooking confidence (per [sweep #7](../07-cooking-behavioral-barriers/scope.md)).

Per [Constitutional Rule 4](../00-meta/constitutional-rules.md#rule-4--no-recipe-generation): **no LLM-generated recipes**. The system leans on curated, sourced, attributed recipe content — never invents.

## Deliverable

An annotated reference map containing:

- **Source qualification framework** — criteria for what makes a recipe source qualify (institutional credibility, peer recognition, engagement, ToS-compliant licensing, provenance retention) — instantiating the [framework-over-source-list principle](../00-meta/dynamic-research-expansion.md#framework-over-source-list--the-corpus-design-principle)
- Per-source-class inventory: paid APIs, curated publishers under legitimate paid access, open datasets, public-domain historical cookbooks (deep), institutional video sources (cooking academies), credentialed YouTube creators, non-Western cuisine sources
- Multi-modal presentation infrastructure: video / structured text / cookbook prose / illustrations
- Real-time terminology / technique lookup glossary sourcing
- Recipe interchange formats and conversion methodology
- Recipe IP law per primary research scope (Rule 9 equal-weighted)
- Attribution architecture preserving provenance through transformations
- Affiliate / cookbook-purchase linking analysis
- Application of [dynamic-research-expansion](../00-meta/dynamic-research-expansion.md) to recipe corpus

This is a **reference map**, not corpus build.

## Source qualification framework (the design center)

Recipe sources qualify by passing through the framework, not by appearing on a fixed list. Criteria:

- **Institutional credibility** — established culinary academy, national food institute, recognized publisher, credentialed practitioner with accountable platform
- **Peer / engagement signal** — engagement metrics (significant follower base, high comment quality), peer-recognized credibility (reviews, awards, citations), or institutional accreditation
- **License / ToS compliance** — accessible through legitimate paid pathways (subscriptions, paid API tiers, partnerships) OR public domain OR explicitly permissive license. **Scraping ToS-prohibited content stays out**, even when content is high-quality
- **Provenance retention** — source supports attribution + traceability through transformation
- **Quality coherence** — recipe content has been edited, tested, or otherwise quality-controlled (vs. raw user-generated noise)

A new source can be added by qualifying through the framework. Sources that no longer pass (e.g., license change, quality decline, ToS revision) can be retired.

## In scope

### Paid commercial APIs

- Spoonacular
- Edamam
- Tasty (BuzzFeed) API where available
- Yummly successors
- Regional commercial recipe APIs (e.g., regional German / Asian / Latin American APIs where they exist)

### Curated publishers (legitimate paid access)

- NYT Cooking (subscription + API where available)
- Bon Appétit / Epicurious
- Serious Eats
- America's Test Kitchen Online
- Eater editorial recipe content
- Bon App / regional editorial outlets
- BBC Good Food, NHS Eat Well (UK)
- Le Monde / Marmiton (France)
- ChefKoch (Germany)
- Equivalent regional editorial recipe publishers

Access through subscriptions, paid API tiers, official partnerships, RSS/affiliate where structured. Scraping ToS-prohibited content explicitly out.

### Open datasets

- RecipeNLG (~2.2M recipes, academic — quality varies, useful for breadth)
- Recipe1M+ (MIT, ~1M recipes with images)
- TheMealDB (free API, smaller)
- Food.com Kaggle datasets
- Open Recipes initiatives + successors
- Schema.org/Recipe scraped corpora — under appropriate ToS / scraping ethics analysis only

### Public-domain historical cookbooks (deep coverage)

Per user direction: real source, not just reference. Coverage at depth:

- **Project Gutenberg** — Mrs. Beeton, Fannie Farmer, multiple historical works
- **HathiTrust Digital Library** — extensive public-domain cookbook collection
- **Internet Archive** — broad historical cookbook holdings
- **Library of Congress** — culinary history collection
- **Schlesinger Library (Harvard)** — significant women's culinary archive
- **MSU Feeding America project** — digitized historical American cookbooks
- **Historical Western canon** — La Varenne, Carême, Escoffier (where public domain), Apicius (Roman), Mrs. Beeton (Victorian English), Fannie Farmer, Catherine Beecher
- **Historical non-Western canon** — Ibn Sayyar al-Warraq (10th c. Arab), Yuan Mei (18th c. Chinese), historical Japanese, Indian Ayurvedic culinary works (where public domain)
- Note: historical recipes have caveats — imprecise measurements, unavailable / changed ingredients, outdated techniques. Surface alongside modern equivalents per Rule 8 epistemic trail

### Modern indexed cookbook databases

- Eat Your Books (paywalled cookbook index — paid access in scope)
- ckbk (subscription cookbook library — paid access in scope)
- Cookpad (Japan-origin, very large UGC base, internationally available — qualification framework determines individual recipe inclusion)

### Recipe video sources

YouTube embeddable / linkable content qualifying through the framework:

- **Engagement + follower thresholds** — significant subscriber base, high-quality comment engagement
- **Institutional / credentialed sources** (priority):
  - French — Le Cordon Bleu, Institut Paul Bocuse, Ferrandi, École Nationale Supérieure de Pâtisserie
  - Italian — ALMA (Italian Culinary Institute), ICIF, Italian Culinary Institute for Foreigners
  - Japanese — Tsuji Culinary Institute, Hattori Nutrition College
  - Indian — Institute of Hotel Management (IHM, multiple cities), Indian Culinary Institute, Welcomgroup Graduate School of Hotel Administration
  - Chinese — China Culinary Academy, provincial culinary schools
  - Korean — Korean Food Foundation (Hansik), Korean Culinary Arts Society
  - Thai — Le Cordon Bleu Bangkok, Nai Lert Thai Cooking School
  - Mexican — ICUM (Instituto Culinario de México)
  - Turkish — Anatolian Culinary Federation
  - US — CIA (Culinary Institute of America), ICE, Johnson & Wales
  - UK — Leiths School of Food and Wine
- **Credentialed individual practitioners** (qualifying through framework):
  - Kenji López-Alt (CIA-credentialed, scientifically rigorous)
  - Maangchi (Korean home cooking, peer-recognized)
  - Madhur Jaffrey works (Indian, Beard Award)
  - Adam Ragusea, ATK creators, NYT Cooking video team, Bon Appétit Test Kitchen
  - Jiro Ono-style master practitioners with documented training lineage
- **Out**: TikTok / Instagram Reels short-form content (variable quality, hard to verify, qualification framework typically not met)
- **Subscription video** — MasterClass, NYT Cooking video tier, ATK Online video — paid access in scope

### Non-Western cuisine sourcing (gap closure)

Per user direction: ensure system isn't US/EU-centric. Build framework-qualifying sources from:

- **National culinary academies** (already listed above)
- **Cultural heritage organizations** — UNESCO Intangible Cultural Heritage food traditions registry, Slow Food International + country chapters, national food preservation societies
- **Academic culinary studies programs** in non-Western universities
- **Diaspora-curated content** — culturally-credentialed creators preserving and adapting traditional cuisines (e.g., Maangchi for diaspora Korean, Indian-origin chefs in UK / US documenting regional Indian)
- **National food institutes** — government-affiliated bodies publishing cuisine documentation (Indian Council of Agricultural Research, Korean Food Foundation, etc.)
- **Cookpad regional content** (Japan-origin platform with strong Asian cuisine coverage)

### Multi-modal recipe presentation requirements (from sweep #7 expansion)

The same recipe concept must be presentable in multiple modalities to match user cooking confidence:

- **Video recipes** — for users with lower cooking confidence
- **Structured text recipes** — middle-confidence; clear step-by-step with defined times, temperatures, techniques
- **Cookbook-style prose recipes** — higher-confidence; narrative format assuming baseline competence
- **Illustrated recipes** — diagrams, technique illustrations, plating photos
- **Real-time terminology / technique lookup** — when user encounters "blanch," "fold," "deglaze," "sweat," "temper," "blind bake," "score" they can tap for definition + technique demo. Glossary sourced from culinary education references — CIA's professional culinary glossary, Larousse Gastronomique technique sections, On Cooking, Joy of Cooking technique chapters, equivalent international references. **Terminology lookup ≠ cooking instruction** per [product-framing "not a cooking class" boundary](../00-meta/product-framing.md#what-nutrime-is-explicitly-not).

### Recipe metadata required for matching + ranking

- Time (active + total) — with per-user calibration from [semantic feedback](../00-meta/intake-pattern.md#mode-3--passive-confirmation--semantic-feedback)
- Skill / complexity tier (cross-references [sweep #12](../12-skills-by-cuisine/scope.md))
- Required equipment
- Required techniques (links to glossary)
- Cuisine + cultural context
- Nutrition (computed against [sweep #2](../02-food-composition-databases/scope.md))
- Cost / ingredient sourcing notes
- Adaptation paths (substitutions, scaling, dietary-accommodation variants)
- Provenance + attribution chain (full source-to-presentation trail)
- Modality availability (video / text / illustrated / etc.)
- Kid-friendly tags (per [sweep #9](../09-multi-user-household/scope.md) — kids as eaters)

### Legal + licensing landscape (global, equal-weighted per Rule 9)

**Distribution context:** Per [product-framing.md](../00-meta/product-framing.md), current distribution intent is **personal use**. This lowers commercial-licensing pressure but does not lower ToS-respect or attribution-ethics requirements — we use legitimate paid pathways and respect ToS regardless of distribution scope.

- US: recipes themselves not copyrightable per *Publications International v. Meredith Corp.* (1996); creative expression copyrighted
- EU: similar copyright regime + database-rights overlay (Directive 96/9/EC sui generis database right)
- UK: post-Brexit similar to EU
- Each primary research scope country: equal-weighted analysis of recipe IP and licensing rules
- ToS-respect across jurisdictions
- Attribution ethics — even when not strictly legally required, attribution to original source is a quality + trust signal
- Affiliate / cookbook-purchase linking — less directly relevant for personal-use distribution, but still ethical good citizenship to drive recognition / revenue back to recipe authors when feasible (broader-scope economics tracked in [roadmap.md](../00-meta/roadmap.md))

### Recipe interchange formats

- **Cooklang** — LLM-friendly plain-text DSL, parseable, diff-able
- **Schema.org/Recipe** — open-web standard, JSON-LD, widely adopted in recipe markup
- **hRecipe** — older microformat, still in legacy sites
- **RecipeML** — XML-based, less common
- Format conversion + canonical-internal-representation strategy

### Dynamic research expansion applied to recipes

Per [dynamic-research-expansion.md](../00-meta/dynamic-research-expansion.md): when a user wants a regional / niche / emerging cuisine not in base corpus, the system uses the same gap-detection → fetch → verify → integrate pipeline. Qualification framework gates which fetched recipes qualify; epistemic trail preserves provenance.

## Out of scope (with reasons)

- **Recipe generation** — explicitly out per [Constitutional Rule 4](../00-meta/constitutional-rules.md#rule-4--no-recipe-generation)
- **Cooking instruction delivery** — out per [product-framing "not a cooking class" boundary](../00-meta/product-framing.md#what-nutrime-is-explicitly-not). Terminology lookup is in; teaching technique is out.
- **Scraping ToS-prohibited content** — out regardless of content quality. We use legitimate paid pathways instead.
- **TikTok / Instagram Reels short-form** — qualification framework typically not met (variable quality, hard to verify, no provenance retention)
- **Implementation of recipe import / parsing pipelines** — research informs design; building comes later

## Open questions for the research

- For each paid commercial API: what's the pricing model, license terms, content quality, coverage breadth, regional bias?
- For each curated publisher: what legitimate paid access pathways exist (subscription tier, partnership, RSS, affiliate), what's the cost / value?
- For public-domain historical cookbooks: what's the realistic interpretive overhead (measurement conversion, ingredient substitution, technique modernization)?
- For institutional culinary academy YouTube content: what's actually published openly vs. paywalled vs. unavailable?
- For non-Western sources: what realistic English-language / translated coverage exists, and what's lost in translation?
- What's the state of recipe interchange format adoption — is Cooklang gaining traction, or is schema.org/Recipe still the practical standard?
- What attribution / provenance architecture patterns work in practice for recipes that get adapted, scaled, substituted, presented in alternative modalities?

## Cross-references

- Bound by [Constitutional Rule 4 (no recipe generation)](../00-meta/constitutional-rules.md#rule-4--no-recipe-generation)
- Bound by [product-framing "not a cooking class" boundary](../00-meta/product-framing.md#what-nutrime-is-explicitly-not)
- Bound by [Constitutional Rule 9 (geographic neutrality)](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing) — global recipe coverage equal-weighted
- Implements [framework-over-source-list principle](../00-meta/dynamic-research-expansion.md#framework-over-source-list--the-corpus-design-principle)
- Depends on [sweep #2 (food composition databases)](../02-food-composition-databases/scope.md) — recipes need nutrition computed against composition data
- Depends on [sweep #7 (cooking behavioral barriers)](../07-cooking-behavioral-barriers/scope.md) — cooking confidence + time-perception + equipment data shapes recipe selection + presentation modality
- Depends on [sweep #12 (skills-by-cuisine)](../12-skills-by-cuisine/scope.md) — skill ↔ cuisine matrix shapes recipe recommendation + skill metadata schema
- Cross-references [sweep #9 (multi-user household)](../09-multi-user-household/scope.md) — kid-friendly metadata, family-of-adults variants
- Cross-references [sweep #10 (clinical condition gating)](../10-clinical-condition-gating/scope.md) — condition-aware recipe filtering and adaptation

## Findings

To be populated when research is run.

## References

To be populated. Add new sources to [sources.md](../00-meta/sources.md) when added.
