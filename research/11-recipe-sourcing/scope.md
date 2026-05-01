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
- **Ingredient list normalized for inventory match** — per [Stage 2 Tension #1 resolution](../00-meta/synthesis.md#tension-1--mental-load-framing-supersedes-raw-time-plus-inventory-tracking-distinction), recipe selection prioritizes recipes that consume ingredients already on hand (per [intake-pattern.md inventory awareness](../00-meta/intake-pattern.md#inventory-awareness--a-parallel-data-layer)). Recipe metadata must support ingredient identity matching + perishable-prioritization scoring (use-up-soonest)
- **Stretch dimension — novelty count + failure cost (honest disclosure metadata, NOT a default filter)** — per [Stage 2 Tension #7 resolution](../00-meta/synthesis.md#tension-7--stretch-recipe-metadata-for-honest-disclosure-not-a-default-filter), recipe metadata captures both *novelty count* (how many new skills relative to a given user's mastered set) and *failure cost* (high-failure-cost techniques like deep-frying, fermentation, complex laminated doughs). The system does NOT pre-filter recipe surfaces by stretch level; instead, it uses this metadata to *name* the stretch in the recipe surface so the user picks with full context per Rule 10. Both dimensions feed the [knowledge-model stretch-readiness](../00-meta/knowledge-model.md#per-user-knowledge-model) signal for the user's self-understanding, not for filtering options down.
- **Pairing-tradition tags (per [sweep #14](../14-ingredient-interactions/scope.md) integration pass)** — recipes annotated with the pairing tradition(s) they exemplify (Western shared-compound, Japanese umami-synergy, Chinese five-flavor balance, Indian masala-with-tadka, Latin sofrito-base, Korean gochugaru-base, etc.). Enables audit-as-education explanations of *why* a recipe's combinations work + supports horizon-broadening recommendations that move users into adjacent pairing traditions.

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

> Methodology note: this sweep was conducted under live-web-fetch denial in this environment. Findings draw on the model's January 2026 knowledge cutoff and authoritative URLs the reader can independently verify. Pricing tiers, ToS details, and license fine print drift; every commercial source listed here should be re-verified at adoption time. Per [dynamic-research-expansion.md](../00-meta/dynamic-research-expansion.md), live re-fetch + verification is part of the system pipeline anyway; the framework is the durable artifact, not the snapshot.

### 1. Source qualification framework (operationalized for recipes)

The five framework criteria from [scope.md §"Source qualification framework"](#source-qualification-framework-the-design-center) above translate into concrete recipe-source gates:

| Criterion | Operationalization for recipe sources |
|---|---|
| **Institutional credibility** | Source is one of: an accredited culinary academy (CIA, Le Cordon Bleu, ALMA, Tsuji, IHM, ICE, Leiths, ICUM, etc.); a peer-recognized publisher (NYT Cooking, Serious Eats, ATK, BBC Good Food, NHS Eat Well, Marmiton, ChefKoch, etc.); a national / cultural-heritage food body (Korean Food Foundation, Slow Food International, UNESCO ICH–listed culinary tradition); a national public-health body (NHS, USDA MyPlate, Health Canada, EFSA-affiliated); an academic / library digitization project (Project Gutenberg, HathiTrust, MSU Feeding America, Schlesinger Library); or a credentialed individual practitioner with documented training lineage (e.g., Beard Award, James Beard Foundation recognition, Michelin recognition, IACP credentials, ATK / NYT Cooking staff). |
| **Peer / engagement signal** | One or more of: subscriber count above a regionally calibrated floor (rough heuristic: ≥250k subscribers for English-language YouTube institutional channels, lower for non-English-language and niche-cuisine specialists); awards (Beard, Michelin, IACP, regional equivalents); peer citation by other framework-qualified sources; long publication history (≥5 years) with stable editorial standards; high comment-quality signal (constructive cooking discussion vs. spam/reaction noise). The signal floor calibrates per cuisine and language — non-Western cuisine specialists are explicitly held to lower follower thresholds to avoid English-language bias. |
| **License / ToS compliance** | Source must be reachable through one of: (a) an official paid API tier whose ToS permits storage/derivation; (b) an editorial subscription whose terms permit personal-use linking + small-quote excerpting; (c) public domain (work expired into PD or US-government-published); (d) a permissive license (CC-BY, CC-BY-SA, CC0, ODbL, MIT-style, etc.) with attribution honored; (e) explicit license/partnership granted by the rights holder. Scraping ToS-prohibited content stays out regardless of quality. Personal-use distribution lowers commercial-licensing pressure but does not lower ToS-respect or attribution-ethics. |
| **Provenance retention** | Source provides stable identifiers (canonical URL, DOI, ISBN+page, video URL+timestamp, dataset row id) and supports attribution chain through transformation. A source that cannot be cited back specifically (e.g., bare aggregator with no per-recipe origin metadata) fails this gate even if the content is legitimate. |
| **Quality coherence** | Recipe content has been edited, tested, or otherwise quality-controlled. Editorial recipes pass automatically; UGC platforms (Cookpad, Food.com user uploads) qualify per-recipe by additional gates: rating count, engagement, optionally cross-validation against another framework-qualified source. Raw scraped corpora (RecipeNLG-style) qualify for breadth/embedding/retrieval but not for direct user surfacing without a second pass. |

**Framework-over-source-list discipline:** the lists below are *examples* of sources that currently pass the framework, not the canonical corpus. New sources qualify by passing the gates; sources retire when they fail (license change, quality decline, ToS revision). This is the recipe-domain instantiation of [framework-over-source-list](../00-meta/dynamic-research-expansion.md#framework-over-source-list--the-corpus-design-principle).

**Per-recipe vs. per-source qualification.** Some sources qualify wholesale (NYT Cooking — every recipe inherits the source's editorial gate). Others require per-recipe qualification (Cookpad, Food.com, RecipeNLG — corpus qualifies for retrieval; individual recipes qualify for surfacing only after a per-item check on rating, completeness, plausibility against composition data). The architecture must distinguish these two modes.

### 2. Paid commercial APIs

#### Spoonacular (sp.) — [spoonacular.com/food-api](https://spoonacular.com/food-api)

- **Coverage:** ~365k+ recipes (per vendor materials), aggregated from web sources with recipe markup + their own additions. Strong English-language Western coverage; thinner on non-Western regional specificity.
- **Pricing model:** Freemium tiered. Free dev tier (rate-limited, ~150 points/day where most recipe endpoints cost 1 point). Paid tiers (Cook, Culinarian, Chef, Food Service) scale by points/day and quota. As of 2025, paid tiers ranged roughly $29–$249/month, with custom enterprise pricing above; **re-verify at adoption time**.
- **License terms:** ToS permits use of returned data within applications; explicitly forbids redistribution of bulk recipe datasets and forbids re-creating their database. Attribution to source URL (the original publisher Spoonacular ingested from) is contractually required. Caching for performance is generally allowed; building a parallel database is not.
- **Strengths:** Built-in nutrition computation, ingredient parsing, meal planning endpoints, dietary filters (vegan, GF, etc.), substitution suggestions. Lowest-friction integration for an early-stage system.
- **Weaknesses / regional bias:** Heavy US/UK Anglophone bias. Many "international" recipes are Anglo-language adaptations rather than authoritative source-language recipes. Quality varies because aggregation surfaces both editorial and SEO content.
- **Framework verdict:** Qualifies for breadth + nutrition/filter scaffolding. Per-recipe qualification gate (provenance back to original publisher must be retained and re-verified) needed before user surfacing for non-Western cuisine.

#### Edamam — [developer.edamam.com](https://developer.edamam.com)

- **Coverage:** ~2.3M+ recipes (vendor claim) sourced from major food publishers under licensed partnerships (Food Network, Allrecipes historically, BBC Good Food historically, etc. — partnership roster shifts; verify).
- **Pricing model:** Recipe Search API has a free Developer plan (rate-limited, attribution-required, restricted commercial use), then Production tiers priced per request bucket; nutrition + food database APIs priced separately. **Re-verify at adoption time.**
- **License terms:** Free tier requires "Powered by Edamam" attribution + linkback to the original recipe URL on the publisher's site. Paid tiers loosen attribution but still require linkback for editorial-source content. Storage for caching allowed within tier; no bulk redistribution.
- **Strengths:** Recipes are sourced from named publishers, so provenance retention is strong by construction. Nutrition data is computed and exposed alongside. Diet/health labels (low-FODMAP, paleo, etc.) attached at recipe level.
- **Weaknesses:** Western-publisher bias even more pronounced than Spoonacular for the recipe API specifically. Content quality is gated upstream by partner-publisher editorial standards.
- **Framework verdict:** Qualifies. Strongest provenance-retention story among aggregator APIs.

#### Tasty (BuzzFeed) — community-mirrored via [rapidapi.com/apidojo/api/tasty](https://rapidapi.com/apidojo/api/tasty)

- **Coverage:** ~3–10k Tasty editorial recipes with strong video integration; primarily US/Anglo casual cooking.
- **Pricing model:** No first-party public API. Third-party RapidAPI mirror (apidojo) freemium; existence and ToS-status of the mirror should not be relied upon — Tasty does not appear to officially license bulk API access for recipe content as of 2026.
- **License terms:** Tasty's own ToS forbids scraping. The third-party RapidAPI mirror's legitimacy is questionable; **NutriMe should treat Tasty as a "publisher to link to under fair-use editorial linking," not as a content source to ingest**.
- **Framework verdict:** **Does not qualify** for ingest. Qualifies as a linkable publisher (cite + link out, do not host content).

#### Yummly successors

- **History:** Yummly was acquired by Whirlpool (2017) and its public Recipe API was deprecated in stages; legacy Yummly app/site continues but the open developer API is effectively gone for new integrators as of the late 2010s onward.
- **Successors / functional equivalents:** Spoonacular, Edamam, Whisk (acquired by Samsung, now Samsung Food — has a partner-only API), Mealime (consumer app, no API), Paprika (consumer app, no API), Innit (B2B partnerships, not open).
- **Framework verdict:** Yummly itself does not qualify (no accessible API). Samsung Food / Whisk qualifies *only* under a formal partnership; out for personal-use scope.

#### Regional commercial APIs

- **Chefkoch (DE)** — [chefkoch.de](https://www.chefkoch.de) — large German-speaking community recipe site (Gruner+Jahr/RTL Group). No general public API; structured data (schema.org/Recipe) is in page markup. Personal-use linking under standard fair-use editorial linking; ingest stays out without partnership.
- **Marmiton (FR)** — [marmiton.org](https://www.marmiton.org) — TF1 Group, large French recipe community. Same pattern: no public API, schema.org/Recipe markup, link-only treatment.
- **750g (FR)** — [750g.com](https://www.750g.com) — Webedia, French recipes. No public API. Link-only.
- **Cookpad** — see §6.
- **Sapore di Cooking / GialloZafferano (IT)** — [giallozafferano.it](https://www.giallozafferano.it) — Mondadori, dominant Italian recipe site. No public API. Link-only.
- **Recetas Gratis (ES, LatAm)** — link-only.
- **Yamicook / Cookbook-style aggregators in Mandarin / Cantonese** — generally no English-accessible APIs; partnerships required.
- **Framework verdict:** Most regional commercial recipe sites do not expose first-party APIs. They qualify as **publishers to link out to**, with schema.org/Recipe markup as the structured-data interchange surface (see §11). Ingest requires partnership.

### 3. Curated publishers (legitimate paid access)

| Publisher | Region | Access pathway | Notes |
|---|---|---|---|
| **NYT Cooking** [cooking.nytimes.com](https://cooking.nytimes.com) | US | Subscription (~$5/mo separate from main NYT). No public recipe API. RSS feeds for new content. Personal-use deep-linking allowed; in-app embedding/reproduction is not. | Top-tier editorial quality; tested recipes; strong "user notes" engagement signal; rich video tier. Framework: qualifies for personal-use linking + subscriber-side referencing. |
| **Bon Appétit / Epicurious** [bonappetit.com](https://www.bonappetit.com), [epicurious.com](https://www.epicurious.com) | US (Condé Nast) | Free web access (ad-supported); no public API. Schema.org/Recipe markup. RSS available. | Both editorial-tested. Epicurious holds historical Gourmet + Bon Appétit archive. Framework: qualifies as link-out publisher. |
| **Serious Eats** [seriouseats.com](https://www.seriouseats.com) | US (Dotdash Meredith) | Free web access; no public API. Schema.org markup. | High testing rigor (Kenji López-Alt legacy, Stella Parks legacy, ongoing test kitchen). Framework: qualifies. |
| **America's Test Kitchen Online** [americastestkitchen.com](https://www.americastestkitchen.com) | US | Tiered subscription ($45–$80/year typical) granting access to ATK + Cook's Illustrated + Cook's Country. No public API. | Strongest evidence-based-recipe-development reputation in US market. Test methodology is itself documentation-grade. Framework: qualifies for subscriber-side reference. |
| **Eater** [eater.com](https://www.eater.com) | US (Vox Media) | Free web; no API. | Editorial recipe content is a small fraction of overall coverage; primarily restaurant journalism. Framework: qualifies for the editorial recipe slice. |
| **Food52** [food52.com](https://food52.com) | US | Free web + paid cookbook line. No public API. | Mix of editorial + community; community gate per-recipe. Framework: qualifies, with per-recipe gate for community-uploaded content. |
| **King Arthur Baking** [kingarthurbaking.com](https://www.kingarthurbaking.com) | US | Free web; structured recipes; large baking-tested corpus. | Domain-specialist source — the baking equivalent of ATK rigor. Framework: qualifies. |
| **BBC Good Food** [bbcgoodfood.com](https://www.bbcgoodfood.com) | UK (Immediate Media) | Free web (some content paywalled); no public API. Schema.org markup. | Largest UK editorial recipe corpus; tested content. Framework: qualifies. |
| **NHS Eat Well** [nhs.uk/live-well/eat-well](https://www.nhs.uk/live-well/eat-well) | UK | Free, public, government-licensed (Open Government Licence v3.0 covers most NHS content). | Rare case of a Tier 1–authoritative-body recipe source. Smaller corpus, conservative recommendations, explicit health framing. Framework: qualifies as both recipe source and health-claim source. |
| **Marmiton** [marmiton.org](https://www.marmiton.org) | FR | Free web; no API. | Largest francophone community recipe site; per-recipe quality gate required. Framework: qualifies as link-out + per-recipe gate. |
| **Le Monde / Le Monde Cuisine** | FR | Subscription. | Editorial; small recipe footprint. Framework: qualifies for subscriber-side reference. |
| **ChefKoch** [chefkoch.de](https://www.chefkoch.de) | DE | Free web; no API. | Largest germanophone recipe community; per-recipe gate. Framework: qualifies as link-out + per-recipe gate. |
| **EatSmarter** [eatsmarter.de](https://eatsmarter.de) | DE | Free web; no API. | Editorial + nutrition focus. Framework: qualifies. |
| **Gesundheit.gv.at / German national health portals** | DE/AT | Government, openly licensed. | Small recipe footprint but Tier 1 health-claim provenance. Framework: qualifies. |
| **AllerHande / Albert Heijn** | NL | Retailer-published. | Limited but professionally tested; framework qualifies for link-out. |
| **GialloZafferano** | IT | Free web; no API. | Largest IT recipe site. Framework: qualifies as link-out + per-recipe gate. |
| **Recetas de Cocina from El Comidista (El País)** | ES | Subscription/free hybrid. | Editorial. Framework: qualifies. |
| **NHS / Health Canada / Australian Eat for Health / Japanese MAFF Shokuiku** | various | Government, openly licensed in most cases. | Authoritative-body recipes — small corpus, evidence-aligned. Framework: qualifies and additionally satisfies Tier 1 attached-health-claim rule. |
| **Korean Food Foundation (Hansik)** [hansik.or.kr](https://www.hansik.or.kr) | KR | Government / cultural body, public. | Curates Korean cuisine corpus in Korean + English. Framework: qualifies as both recipe source and cultural-authority source. |
| **MAFF / Kikkoman / national Japanese culinary bodies** | JP | Mixed public + commercial. | Japanese ministry of agriculture publishes Shokuiku materials including recipes. Framework: government corpus qualifies; commercial corpora link-out. |

**Personal-use access pattern.** Under the personal-use distribution scope, the dominant access mode for editorial publishers is **subscription-side reference + link-out**, not bulk ingest. The system fetches the recipe from the publisher under the user's authenticated subscription session (or from publicly available pages), retains the canonical URL + access timestamp + selected metadata, and presents under attribution. This minimizes redistribution exposure while honoring publisher economics.

**Scraping is explicitly out** for ToS-prohibited publishers regardless of the technical possibility. NYT, Condé Nast, Dotdash Meredith, BBC, Immediate Media, Webedia, TF1, Mondadori, Gruner+Jahr/RTL, etc. all forbid programmatic scraping in their respective ToS.

### 4. Open datasets

| Dataset | Size / scope | Source / origin | License | Quality + use |
|---|---|---|---|---|
| **RecipeNLG** [recipenlg.cs.put.poznan.pl](https://recipenlg.cs.put.poznan.pl) (Bień et al. 2020) | ~2.23M recipes | Polish academic NLG dataset built on top of Recipe1M+ + scraped sources | Academic / non-commercial research only; the dataset's terms restrict to non-commercial research use | Useful for embedding, retrieval, ingredient/technique extraction. Not directly user-surfacing under personal-use *if* "personal use" is read as private + non-redistributing — re-verify the dataset's terms vs. personal-use intent. |
| **Recipe1M+** [pic2recipe.csail.mit.edu](http://pic2recipe.csail.mit.edu) (Marin et al. 2019, MIT CSAIL) | ~1M recipes + ~13M food images | Scraped from cooking websites (Food.com, Allrecipes, etc.) | Academic research only; explicit terms restrict to non-commercial research | Vision/text alignment use case; same caveat as RecipeNLG for surfacing. |
| **TheMealDB** [themealdb.com/api.php](https://www.themealdb.com/api.php) | ~300+ curated recipes | Hand-curated by the maintainer + community | Free API for personal/educational use; Patreon-supported "premium" key for higher rate; CC-BY-equivalent attribution requested | Tiny corpus relative to Spoonacular/Edamam, but every recipe is traceable + well-formed + has cuisine tagging. Useful for scaffolding + tests. Framework: qualifies. |
| **Food.com Recipes & Interactions (Kaggle)** [kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions) | ~230k recipes + ~1.1M reviews | Scraped from Food.com (Generally Recognized as Foods Inc. / Dotdash Meredith) | Kaggle license is CC-BY-NC-SA-4.0 on this dataset; the **upstream Food.com ToS forbids scraping**, so derivative use carries upstream risk regardless of Kaggle re-license. | Strong rating signal; useful for popularity weighting research. Framework: qualifies for *research / training-internal* use; **does not qualify for ingest into user-facing surfacing** because of upstream ToS exposure. |
| **OpenRecipes (legacy)** [github.com/fictivekin/openrecipes](https://github.com/fictivekin/openrecipes) | ~170k recipe stubs (titles + URLs + minimal metadata) | Aggregated schema.org/Recipe and hRecipe markup harvested 2012–2015, then archived | MIT-style on the harvester code; stubs link out to original publishers | Project is dormant. Useful as historical reference for the schema.org/Recipe scraping pattern. Framework: qualifies as a pointer index; per-recipe content remains the publisher's. |
| **Open Food Facts — recipe extension** | n/a | OFF is primarily product-level. | ODbL. | Not a recipe dataset; cross-references with sweep #2. |
| **Schema.org/Recipe scraped corpora generally** | varies | Web crawl of any site marking recipes with schema.org/Recipe JSON-LD | Per-site; the markup is structured data the publisher exposes, but reproducing the recipe text remains under the publisher's copyright + ToS. | Common Crawl (commoncrawl.org) is the practical "open" entry point. Use for **structure/metadata learning + linkable index**, not for re-hosting bodies. |
| **EpiRecipes / FOODRGB / various smaller academic sets** | varies | Academic | Per-paper | Niche; cite per-use. |

**Synthesis on open datasets.** The realistic role of open datasets in NutriMe is **structural** (shape of recipe data, ingredient parsing, technique vocabulary, embedding/retrieval surfaces) and **historical/archival** (PD cookbook corpora — see §5), not "user-surfacing recipe corpus." The user-surfacing layer leans on **(a) public-domain historical cookbooks + (b) authoritative-body recipes + (c) editorial publishers via legitimate access + (d) framework-qualified video sources**, with open datasets used for indexing, embedding, retrieval scaffolding, and evaluation.

### 5. Public-domain historical cookbooks (deep coverage)

#### Library / digitization platforms

- **Project Gutenberg** [gutenberg.org](https://www.gutenberg.org) — public domain text repository. Holds *Mrs. Beeton's Book of Household Management* (1861/1907 editions in PD), *The Boston Cooking-School Cook Book* (Fannie Farmer, 1896), *Miss Parloa's New Cook Book* (1880), *The White House Cook Book* (Gillette & Ziemann, 1887), *The Virginia Housewife* (Mary Randolph, 1824), *Common Sense in the Household* (Marion Harland, 1871), *Aunt Babette's Cook Book* (1889 — Jewish-American), and dozens more US/UK cookbooks pre-1929. License: PD; Project Gutenberg adds a small derivative-license layer on the *PG-encoded text version*, easy to comply with.
- **HathiTrust Digital Library** [hathitrust.org](https://www.hathitrust.org) — federation of US research-library digitizations. Has the deepest US PD cookbook holdings — tens of thousands of cookbook-classified items, of which a large subset is full-view PD. Member-institution access for non-PD; PD items globally readable + downloadable. License: PD items are PD; HathiTrust attribution requested.
- **Internet Archive** [archive.org](https://archive.org) — broad cookbook digitization, including community-uploaded PD scans + library-partnered scans. Historical regional cookbooks (church cookbooks, community fundraiser cookbooks, foreign-language cookbooks) often surface here first. License: per-item; often PD or CC.
- **Library of Congress** [loc.gov](https://www.loc.gov) — Rare Book and Special Collections + American Memory holdings include US culinary history. License: US-government works are PD; library-curated digitizations PD where the source is PD.
- **Schlesinger Library on the History of Women in America (Harvard Radcliffe Institute)** [radcliffe.harvard.edu/schlesinger-library](https://www.radcliffe.harvard.edu/schlesinger-library) — Culinary Collections include Julia Child papers, M.F.K. Fisher papers, Elizabeth David, and a large pre-1929 women's cookbook corpus. Many items PD; some access-restricted. Important for women's culinary history under-representation.
- **Michigan State University Feeding America: The Historic American Cookbook Project** [d.lib.msu.edu/fa](https://d.lib.msu.edu/fa) — 76 fully digitized historic American cookbooks 1798–1922, all PD, full text + page images. Curated specifically as a research corpus; this is the cleanest single entry point to US PD cookbooks.
- **Bibliothèque nationale de France — Gallica** [gallica.bnf.fr](https://gallica.bnf.fr) — French PD cookbooks: La Varenne, Carême, Gouffé, Audot, Viard, etc. License: BnF non-commercial reuse default for digitized PD; commercial reuse requires permission. Personal use clearly permitted.
- **Deutsche Digitale Bibliothek** [deutsche-digitale-bibliothek.de](https://www.deutsche-digitale-bibliothek.de) — German PD cookbooks: Henriette Davidis, Rumohr, etc.
- **Europeana** [europeana.eu](https://www.europeana.eu) — federated EU cultural-heritage portal; holds significant PD European cookbook material with rights statements per item.
- **Wellcome Collection** [wellcomecollection.org](https://wellcomecollection.org) — historical health-and-food works, PD where applicable.

#### Western canon (PD or near-PD reference editions)

- **Apicius — *De re coquinaria*** (~4th–5th c. compiled). Latin text PD; multiple translations PD or under varying license. The foundational Roman cookbook.
- **Le Ménagier de Paris** (~1393). Old French; PD. Domestic + culinary instruction.
- **François Pierre La Varenne — *Le Cuisinier françois*** (1651). PD. Foundational of modern French cuisine.
- **Hannah Glasse — *The Art of Cookery Made Plain and Easy*** (1747). PD. Massively influential English cookbook.
- **Marie-Antoine Carême — *L'Art de la cuisine française au dix-neuvième siècle*** (1833–1847). PD. Grande cuisine codification.
- **Jules Gouffé — *Le Livre de cuisine*** (1867). PD.
- **Isabella Beeton — *Mrs. Beeton's Book of Household Management*** (1861). PD. The canonical Victorian English household manual.
- **Fannie Farmer — *The Boston Cooking-School Cook Book*** (1896). PD. Introduced precise measurement standardization.
- **Catharine Beecher — *Domestic Receipt Book*** (1846). PD.
- **Auguste Escoffier — *Le Guide culinaire*** (1903). **PD status varies by jurisdiction** — author died 1935; PD in EU after 2005; in the US the 1903 edition is PD but later editions/translations may not be. Verify edition before use.
- **Ali-Bab (Henri Babinski) — *Gastronomie pratique*** (1907, expanded later). Earliest editions PD; later expansions vary.
- **Larousse Gastronomique** (1938 first ed., Prosper Montagné) — **NOT PD** in most jurisdictions; modern editions in copyright. Use as reference under fair use, not as ingestible source.

#### Non-Western canon (PD or scholarly-translated)

- **Ibn Sayyar al-Warraq — *Kitāb al-Ṭabīkh*** (~10th c. Baghdad). Arabic text PD; the Nawal Nasrallah English translation (2007, Brill, *Annals of the Caliphs' Kitchens*) is in copyright. The original text + older translations are PD. This is the foundational medieval Arab cookbook.
- **Muhammad ibn al-Hasan al-Baghdadi — *Kitāb al-Ṭabīkh*** (1226). Arabic PD; Charles Perry's translation in copyright.
- **Yuan Mei — *Suiyuan Shidan / Recipes from the Garden of Contentment*** (1792). Chinese text PD. The Sean J.S. Chen English translation (2018) is in copyright; Chinese-language PD versions widely available.
- **Jia Sixie — *Qimin Yaoshu*** (~6th c. China). Chinese agricultural-cum-culinary work; PD.
- ***Manasollasa* / *Abhilashitartha Chintamani*** by Someshvara III (~12th c., Sanskrit, India). PD; surveys cooking among many other arts.
- **Charaka Samhita / Sushruta Samhita** (Ayurvedic medical texts, ~1st millennium BCE–CE). PD; contain dietetic/culinary guidance, not pure recipes. Surface as cultural-context, not as direct recipe corpus.
- **Bhojanakutuhalam** by Raghunatha Suri (~17th c. South India, Sanskrit). PD. Comprehensive Sanskrit dietary + culinary treatise.
- **Pakadarpanam** (early modern Sanskrit culinary text). PD.
- **Ryōri Monogatari** (1643, Japan — the earliest printed Japanese cookbook). PD.
- **Tofu Hyakuchin** (1782, Japan). PD.
- **Eumsik Dimibang** (~1670, Korea — the earliest Korean cookbook by a woman, Jang Gye-hyang). PD; modern translations may be in copyright.
- **Suunbo / Gyuhap Chongseo** (early 19th c. Korean). PD.
- ***Lo libre de Sent Soví*** (Catalan, ~1324). PD.
- ***Libro de Arte Coquinaria*** by Maestro Martino (~1465, Italian). PD.
- ***Opera*** by Bartolomeo Scappi (1570, Italian). PD.
- **Diego Granado — *Libro del arte de cozina*** (1599, Spanish). PD.
- **Juan Altamiras — *Nuevo arte de cocina*** (1745, Spanish). PD.

#### Caveats for historical PD content (Rule 8 epistemic-trail surface required)

- **Imprecise measurement** — pre-Fannie-Farmer (and outside the standardization era), measures are "a teacupful," "a piece of butter the size of an egg," "a slow oven," "until done." Modern surfacing requires conversion, and conversion is interpretation, which is itself an epistemic-trail event.
- **Unavailable / changed ingredients** — heirloom varieties, animal cuts no longer common, fish stocks no longer available, ingredients with different fat / sugar / starch content than modern equivalents. Substitution is interpretation.
- **Outdated technique assumptions** — open-hearth cooking, coal range, ice-house refrigeration, no microbial safety understanding (raw eggs in hollandaise per period, undercooking standards differ). Some recipes need modern food-safety overlay.
- **Outdated nutritional / health framing** — historical works often attach health claims that are now Tier 4 or refuted. Per Rule 7, those claims do not transfer to NutriMe; the recipe-as-cultural-artifact does, the attached health claim does not without modern evidence.
- **Cultural / colonial framing** — many 19th- and early 20th-century cookbooks contain racial, colonial, and class language that should be acknowledged when the work is surfaced (curatorial annotation, not silent omission).

**Architectural implication.** Historical recipes enter the corpus with a "needs-modernization" flag carrying the specific gap (measurement, ingredient, technique, safety, framing). The system can surface the historical recipe as cultural artifact OR a modernized adaptation, but the link between the two must be explicit (provenance: "Adapted from Mrs. Beeton 1861, p. 412; measurements converted; raw-egg step replaced with pasteurized-egg equivalent; ingredient X substituted because Y is unavailable") — this is the recipe-domain instantiation of [Rule 8 epistemic trail](../00-meta/constitutional-rules.md#rule-8--epistemic-trail-of-honesty).

### 6. Modern indexed cookbook databases

- **Eat Your Books** [eatyourbooks.com](https://www.eatyourbooks.com) — paid subscription (~$30/yr typical) indexing ~250k+ cookbooks + ~2M+ recipes by ingredient, cuisine, occasion. The index is searchable; full recipe text is not hosted (you pull the cookbook off your shelf or buy it). **Critically valuable** for retrieval over the user's own cookbook library + for discovery. Personal-use API access not public; web access only. Framework: qualifies as **discovery + indexing layer**, not a content host.
- **ckbk** [ckbk.com](https://www.ckbk.com) — subscription cookbook library (~$15/mo or annual). Hosts full text of ~1000+ cookbooks under publisher license — includes Modernist Cuisine, Larousse Gastronomique, regional + international titles. The most cuisine-diverse legitimate cookbook subscription as of 2026 (notable Indian, African, Latin American, Middle Eastern coverage relative to peers). Personal-use subscriber-side access. Framework: qualifies as **first-class content source under subscriber-side reference**. No public API for ingest; ingest requires partnership.
- **Cookpad** [cookpad.com](https://cookpad.com) — Japan-origin, multi-country (~30+ country sites). Vast UGC corpus (~5M+ recipes), strongest in Japanese / South Asian / Southeast Asian / Latin American home cooking. Per-recipe quality varies wildly; some cuisines have stronger curation than others. No public consumer API; partner-program API limited. **Per-recipe qualification gate is essential** (rating, completeness, plausibility). Framework: qualifies for retrieval with strong per-recipe gate, especially valuable for non-Western home-cooking coverage.
- **KitchenStories** [kitchenstories.com](https://www.kitchenstories.com) — German-origin, multi-language editorial + video. No public API; framework: qualifies as link-out publisher.
- **Paprika / Mealime / Plan to Eat** — consumer recipe-management apps; not data sources, not relevant for sourcing.

### 7. Recipe video sources

#### Institutional / credentialed culinary academies (priority sources)

These channels qualify automatically on institutional credibility. YouTube is the dominant publishing surface; some maintain additional Vimeo / institutional sites. Verify channel URLs and content language at adoption time — institutional output varies.

| Region | Institution | Notes |
|---|---|---|
| France | **Le Cordon Bleu** [cordonbleu.edu](https://www.cordonbleu.edu) | YouTube channel publishes technique demos + chef interviews; substantial educational content; multilingual. |
| France | **Institut Paul Bocuse** [institutpaulbocuse.com](https://www.institutpaulbocuse.com) | Now "Institut Lyfe." YouTube + institutional video. |
| France | **Ferrandi Paris** [ferrandi-paris.com](https://www.ferrandi-paris.com) | "L'École française de gastronomie." YouTube channel, technique-focused. |
| France | **École Nationale Supérieure de Pâtisserie (ENSP) — Ducasse Education** [ensp-adf.com](https://www.ensp-adf.com) | Pâtisserie focus. |
| Italy | **ALMA — La Scuola Internazionale di Cucina Italiana** [alma.scuolacucina.it](https://www.alma.scuolacucina.it) | Italian cuisine + multilingual programs. |
| Italy | **ICIF — Italian Culinary Institute for Foreigners** [icif.com](https://www.icif.com) | Designed for international students. |
| Japan | **Tsuji Culinary Institute (辻調理師専門学校)** [tsuji.ac.jp](https://www.tsuji.ac.jp) | Major Japanese culinary academy; some publicly available video; primarily Japanese-language. |
| Japan | **Hattori Nutrition College** [hattori.ac.jp](https://www.hattori.ac.jp) | Yukio Hattori; nutrition + culinary; mostly Japanese-language. |
| India | **Institute of Hotel Management (IHM)** — multi-city federated, [ihmpusa.gov.in](https://www.ihmpusa.gov.in), [ihmctan.edu](https://ihmctan.edu) (Mumbai), etc. | Regional IHMs publish technique + cuisine demonstrations; quality + accessibility varies by campus. |
| India | **Indian Culinary Institute (ICI)** [ici.nic.in](https://ici.nic.in) | Government-affiliated; cuisine documentation + research. |
| India | **Welcomgroup Graduate School of Hotel Administration (WGSHA), Manipal** | Industry-aligned. |
| China | **China Cuisine Association / 中国烹饪协会** [ccas.com.cn](http://www.ccas.com.cn) | National body; cuisine documentation. |
| Korea | **Korean Food Foundation (한식진흥원, "Hansik")** [hansik.or.kr](https://www.hansik.or.kr) | Government cultural body; English + Korean cuisine documentation, recipes, video. Strongest single Korean-cuisine institutional source. |
| Thailand | **Le Cordon Bleu Bangkok** | Verified extension. |
| Thailand | **Blue Elephant Cooking School (Bangkok)** | Long-running, peer-recognized. |
| Mexico | **ICUM — Instituto Culinario de México** [icum.edu.mx](https://icum.edu.mx) | National. |
| Mexico | **Centro Culinario Ambrosía** | Regional. |
| Turkey | **Anatolian Culinary Federation / national gastronomy programs** | Federated. |
| US | **Culinary Institute of America (CIA)** [ciachef.edu](https://www.ciachef.edu) | YouTube channel + open courseware fragments; technique reference. |
| US | **Institute of Culinary Education (ICE)** [ice.edu](https://www.ice.edu) | YouTube + content marketing. |
| US | **Johnson & Wales University, College of Food Innovation & Technology** [jwu.edu](https://www.jwu.edu) | Limited public video. |
| UK | **Leiths School of Food and Wine** [leiths.com](https://leiths.com) | Some publicly available content; primarily course-tuition. |
| UK | **Westminster Kingsway / Bournemouth & Poole / national vocational programs** | Limited. |

#### Editorial / publisher video teams (qualify on publisher institutional credibility)

- **NYT Cooking video** [youtube.com/@NYTCooking](https://www.youtube.com/@NYTCooking) — staff-produced; content marketing for the subscription product.
- **Bon Appétit Test Kitchen** [youtube.com/@bonappetit](https://www.youtube.com/@bonappetit) — Condé Nast; high engagement. (Note: significant talent turnover post-2020 — verify present-team credentialing per [framework gate "institutional credibility"](#1-source-qualification-framework-operationalized-for-recipes).)
- **America's Test Kitchen / Cook's Country** [youtube.com/@americastestkitchen](https://www.youtube.com/@americastestkitchen) — staff-produced; tested recipes.
- **Serious Eats video** — limited; primarily editorial site.
- **BBC Good Food video** — editorial content marketing.
- **Tasty** — institutional but format/quality is short-form casual; framework qualifies cautiously (high follower, lower per-video editorial rigor than ATK/NYT).

#### Credentialed individual practitioners

- **J. Kenji López-Alt** — CIA-credentialed, *The Food Lab* author, Serious Eats former chief culinary advisor. YouTube channel + book corpus. Scientifically rigorous.
- **Maangchi (Emily Kim)** — 6M+ subscribers, two cookbooks, pre-eminent diaspora-Korean home-cooking source.
- **Madhur Jaffrey** — James Beard Award; foundational author for English-language Indian cooking. Book corpus primary; selected video.
- **Adam Ragusea** — Mercer professor of journalism; cooking-with-a-source-trail format.
- **Helen Rennie** — classically trained instructor; technique-focused.
- **Pailin Chongchitnant (Hot Thai Kitchen)** — Le Cordon Bleu; pre-eminent diaspora-Thai source.
- **China Sichuan Food (Elaine Luo)**; **Made With Lau (Randy Lau)** — Cantonese household cooking with documented practitioner lineage.
- **Lidia Bastianich**, **Marcella Hazan (book corpus)** — foundational Italian-American.
- **Samin Nosrat** (*Salt Fat Acid Heat*); **Yotam Ottolenghi** (book + Guardian column corpus); **Claudia Roden** (foundational Middle Eastern).
- **Diana Kennedy** (book corpus, foundational Mexican); **Pati Jinich** (Mexican Table, public broadcasting).
- **Vivek Singh, Asma Khan, Romy Gill, Dishoom team** (UK-based regional Indian).
- **Jiro Ono / *Jiro Dreams of Sushi* lineage** — exemplar of master-practitioner documented training lineage.
- **Andong (Andre Meyer-Vitali)** — Asian regional cuisine + serious sourcing methodology.
- **Brian Lagerstrom** — ex-restaurant; high editorial quality.
- **Internet Shaquille** — meta/technique focus; more education than recipe-source.
- **Kwoklyn Wan**, **Ken Hom (book corpus)** — Cantonese.
- **Saveur / Eater contributors** — case-by-case framework qualification.

#### Out-of-scope per scope.md

- **TikTok / Instagram Reels short-form** — qualification framework typically not met (variable quality, limited provenance retention, hard to verify institutional credibility, ToS often restricts derivative use). Stays out.

#### Subscription video sources (qualify under subscriber-side reference)

- **MasterClass** — chef-taught lessons (Thomas Keller, Gordon Ramsay, Massimo Bottura, Yotam Ottolenghi, Niki Nakayama, Carla Hall, etc.). Personal subscription. Not generally an ingestible recipe corpus; reference + link-out.
- **NYT Cooking video tier** — included in subscription.
- **ATK Online video** — included in subscription.
- **Rouxbe Cooking School** — paid online culinary school; technique-grade.

### 8. Non-Western cuisine sourcing (gap-closure priority)

Non-Western coverage is the most likely place for a Western-built system to under-perform; the framework explicitly down-weights English-language follower-count gates for non-Western specialists, and the categories below are first-class.

#### National culinary academies + national food institutes

Listed in §7 above. Add for completeness:

- **Indian Council of Agricultural Research (ICAR)** [icar.org.in](https://icar.org.in) and **National Institute of Nutrition (NIN), Hyderabad** [nin.res.in](https://www.nin.res.in) — Indian government bodies publishing dietary + recipe-adjacent material.
- **MAFF Japan (Ministry of Agriculture, Forestry, Fisheries) — Shokuiku materials** [maff.go.jp](https://www.maff.go.jp) — Japanese national food-education program; recipe-adjacent.
- **CONABIO (México)** [biodiversidad.gob.mx](https://www.biodiversidad.gob.mx) — biodiversity body that documents traditional Mexican cuisine ingredients.
- **EMBRAPA (Brazil)** [embrapa.br](https://www.embrapa.br) — agricultural research; cuisine-adjacent.
- **Korean Food Foundation (한식진흥원)** — already listed; the most actively English-publishing Asian national food body.
- **Egyptian Chefs Association**; **Lebanese Culinary Federation**; **regional Slow Food convivia** — peer-recognized.

#### Cultural-heritage organizations

- **UNESCO Intangible Cultural Heritage list — culinary traditions** [ich.unesco.org](https://ich.unesco.org) — inscribed elements include: Mediterranean Diet (2010, multi-country); Traditional Mexican Cuisine (2010); Washoku, traditional Japanese dietary cultures (2013); Kimjang, the making and sharing of kimchi in Korea (2013); Gingerbread craft from Northern Croatia (2010); French gastronomic meal (2010); Neapolitan pizzaiuolo art (2017); Arabic coffee (2015, multi-country); Ceviche (2023, Peru); Singapore hawker culture (2020); Ethiopian injera-related traditions; Haitian joumou soup (2021); Raï music–adjacent food culture; Couscous (2020, multi-Maghreb); Borscht (2022, Ukraine, urgent-safeguarding inscription); Beer culture in Belgium (2016); Gastronomic meal-adjacent inscriptions worldwide. **UNESCO ICH listings are framework-qualifying as cultural-heritage authority** — the recipes themselves still need source-quality gating, but the cuisine + practice context is authoritative.
- **Slow Food International** [slowfood.com](https://www.slowfood.com) — Ark of Taste catalogs ~6000+ heritage food products + traditional recipes; Presidia projects sustain regional production. Framework: qualifies as cultural-heritage authority + recipe-adjacent.
- **National food preservation societies / Indigenous food organizations**, e.g., **NATIFS / Indigenous Food Lab (Sean Sherman)** [natifs.org](https://www.natifs.org); **First Nations Development Institute** food-sovereignty work; **Māori kai sovereignty bodies in NZ**; **First Peoples' Cultural Council (Canada)** — qualify per institutional credibility.

#### Academic culinary studies (non-Western universities)

- **Le Cordon Bleu Bangkok / Mahidol gastronomy programs (Thailand)**.
- **Centro de Cultura Culinaria de Tijuana / UAM Xochimilco gastronomy (Mexico)**.
- **Yonsei / Ewha Korean Food / Hanyang gastronomy (Korea)**.
- **Tsinghua / China Agricultural University food studies (China)**.
- **Hong Kong Polytechnic University, School of Hotel and Tourism Management** — strong Asian food-studies output.
- **University of Gastronomic Sciences, Pollenzo (Italy)** [unisg.it](https://www.unisg.it) — Slow Food academic arm.
- **OCAD / U Toronto / U Sydney food studies — diaspora research output**.

#### Diaspora-curated content (qualifies through framework)

Diaspora creators bridge cultural authenticity with English-language reach, and frequently surface regional / household cooking that institutional sources omit:

- **Maangchi** (Korean), **Hot Thai Kitchen / Pailin Chongchitnant** (Thai), **Made With Lau** (Cantonese household), **China Sichuan Food / Elaine Luo** (Sichuanese), **Munchies / Vice Asia regional contributors**, **Aaron and Claire** (Korean), **Tara O'Brady** (Indian-Canadian, *Seven Spoons*), **Nik Sharma** (Indian-American, *Season*, *The Flavor Equation*), **Priya Krishna** (Indian-American), **Hetty McKinnon** (Chinese-Australian), **Eric Kim at NYT Cooking** (Korean-American), **Andrea Nguyen** (Vietnamese-American, *The Pho Cookbook*, *Vietnamese Food Any Day*), **Charles Phan, Helen Le, Uyen Luu** (Vietnamese), **Yotam Ottolenghi + Sami Tamimi** (Palestinian/Israeli), **Reem Kassis** (Palestinian, *The Palestinian Table*), **Anissa Helou** (multi-Mediterranean/Levantine/Maghrebi scholarly cookbook author), **Ozlem Warren** (Turkish), **Selin Kiazim** (Turkish-Cypriot), **Olia Hercules** (Ukrainian/Caucasus), **Caroline Eden** (Central Asian travel/food writing), **Tomiko Cary, Sonoko Sakai** (Japanese-American), **Eric Sze (886 NYC, Taiwanese-American)**, **Lucas Sin** (Cantonese-American).

#### African / Latin American / Middle Eastern / Central + South Asian (frequent Western-system gaps)

- **Yewande Komolafe**, **Tunde Wey**, **Lerato Umah-Shaylor**, **Pierre Thiam** (West African); **Marcus Samuelsson** (Ethiopian-American); **Selassie Atadika** (Ghanaian fine-dining); **Zoe Adjonyoh** (Ghanaian); **The Groundnut Cookbook** team — African + diaspora.
- **Maricel Presilla** (Latin American, *Gran Cocina Latina*); **Pati Jinich**; **Diana Kennedy corpus**; **Bricia Lopez** (Oaxacan); **Enrique Olvera** (Mexican fine-dining); **Pia León**, **Virgilio Martínez** (Peruvian); **Roberto Santibañez**.
- **Najmieh Batmanglij** (foundational Persian); **Greg + Lucy Malouf** (Levantine); **Sami Tamimi**; **Reem Kassis**; **Olia Hercules**.
- **Floyd Cardoz**, **Asma Khan**, **Romy Gill**, **Maunika Gowardhan**, **Meera Sodha**, **Anjum Anand**, **Cyrus Todiwala**, **Vivek Singh** (regional Indian + diaspora); **Jaffrey corpus** (foundational); **Nik Sharma**.
- **Nigella Lawson, Yotam Ottolenghi, Claudia Roden** corpora — UK-based, regionally cross-cutting, peer-canonical.

### 9. Real-time terminology / technique lookup glossary sources

The "tap to look up 'blanch' / 'fold' / 'deglaze'" feature requires a glossary corpus; per [product-framing "not a cooking class" boundary](../00-meta/product-framing.md#what-nutrime-is-explicitly-not), **terminology lookup ≠ cooking instruction**. The glossary defines + shows briefly; teaching is out of scope.

| Source | Use | License posture |
|---|---|---|
| **Culinary Institute of America — *The Professional Chef* + glossary appendices** ([ciachef.edu](https://www.ciachef.edu)) | Industry-canonical professional glossary | In-copyright — fair-use definitional citation, not bulk reproduction. |
| **Larousse Gastronomique** (Hamlyn / Clarkson Potter, latest ed. 2009 EN) | Comprehensive culinary reference, definitional + cultural | In-copyright — fair-use definitional citation; available via ckbk subscription for personal reference. |
| **Sarah R. Labensky, Alan M. Hause — *On Cooking: A Textbook of Culinary Fundamentals*** (Pearson, 6th ed.) | Standard US culinary-school textbook | In-copyright — definitional fair use. |
| **Joy of Cooking** (Rombauer family, current 2019 75th-anniversary ed.) | Technique chapters + glossary | In-copyright — definitional fair use. |
| **Harold McGee — *On Food and Cooking: The Science and Lore of the Kitchen*** (Scribner, 2004 rev.) | Science-based explanation of techniques (the "why") | In-copyright — definitional fair use. |
| **Modernist Cuisine** (Nathan Myhrvold et al.) | Modernist + scientific culinary reference | In-copyright; available via ckbk subscription. |
| **Le Cordon Bleu — Le Petit Larousse Cuisinier / Cuisine et techniques** (where PD or licensed) | French-language technique reference | Mostly in-copyright. |
| **Wikipedia / Wiktionary culinary technique pages** | Free-license definitional content | CC-BY-SA. Useful as a baseline, must be quality-gated. |
| **NHS / NHS Eat Well food/cooking glossary** | Authoritative-body definitional content | OGL v3.0. |
| **Dictionnaire de l'Académie française** (where applicable for FR terms) | Authoritative French definition | Public for reference. |
| **Wiktionary multilingual** | Multilingual cuisine-vocabulary baseline | CC-BY-SA. |
| **Specific publisher glossaries** — Serious Eats glossary, BBC Good Food cooking glossary, NYT Cooking glossary | Editorial definitional content | Per-publisher; link-out + brief-quote fair use. |
| **Maangchi Korean ingredients glossary**, **Hot Thai Kitchen ingredients glossary**, **regional cuisine glossaries** | Cultural-context definitional content | Per-creator; link-out + brief-quote fair use. |

**Implementation note.** A practical approach is a NutriMe-internal glossary, written in-house or under explicit license, that synthesizes definitions from the sources above with full source citation per term. The system also surfaces "see also" links to in-depth technique videos from §7 sources for users who want the full demo — but per the not-a-cooking-class boundary, that's a link-out, not embedded instruction.

### 10. Recipe IP law per primary research scope (Rule 9 equal-weighted)

| Jurisdiction | Recipe-itself protection | Creative-expression protection | Database / sui generis | Notes |
|---|---|---|---|---|
| **United States** | **Not protectable.** Recipe ingredient lists + functional method steps are uncopyrightable as "mere lists of ingredients" / functional procedures per *Publications International, Ltd. v. Meredith Corp.*, 88 F.3d 473 (7th Cir. 1996); reaffirmed by 17 U.S.C. §102(b)'s exclusion of procedures/processes; see also *Lambing v. Godiva Chocolatier* (1998), *Tomaydo-Tomahhdo v. Vozary*, 629 F. App'x 658 (6th Cir. 2015). | Headnotes, narrative, photography, illustrations, expressive arrangement protected under standard copyright. | No general database right (*Feist Publications v. Rural Telephone* (1991) rules out sweat-of-the-brow). | Trademark, trade-secret, contract / ToS still apply. |
| **European Union** | Functional method generally not copyrightable, similar to US, under originality threshold of *Infopaq* (CJEU, C-5/08) and *Painer* (C-145/10). | Creative expression protected (Berne / InfoSoc Directive 2001/29/EC). | **Sui generis database right** under Directive 96/9/EC ("Database Directive"). Substantial-investment-in-collection databases get 15-year (renewable) protection independent of copyright. | A bulk recipe corpus assembled with substantial investment (Edamam-style) can attract DB right even if individual recipes don't attract copyright. |
| **United Kingdom (post-Brexit)** | Inherits substantively similar regime to EU on recipes. | Same. | UK retains a domestic database-right framework substantially similar to the EU directive (post-Brexit retained EU law); UK and EU databases are no longer reciprocally protected by default. | NHS content licensable under OGL v3.0. |
| **Canada** | Similar to US — recipes themselves not copyrightable as functional/procedural; creative expression protected (Copyright Act, R.S.C. 1985, c. C-42). | Creative expression protected. | No EU-style sui generis database right; "sweat of the brow" rejected per *CCH Canadian Ltd. v. Law Society of Upper Canada* (2004 SCC 13). | |
| **Australia** | Similar to US/Canada; *IceTV v. Nine Network* (2009) limits protection of factual compilations. | Creative expression protected (Copyright Act 1968 (Cth)). | No EU-style sui generis. | |
| **New Zealand** | Similar; Copyright Act 1994. | Creative expression protected. | No EU-style sui generis. | |
| **Japan** | Recipe itself generally not protectable as idea/method; creative expression protected (Copyright Act of Japan, Act No. 48 of 1970). | Creative expression protected. | Limited database protection under Article 12bis (creativity-in-selection-or-arrangement standard). | |
| **Korea** | Similar; recipe procedure itself not copyrightable; expression protected (Copyright Act, Act No. 432 of 1957, as amended). | Yes. | Database right under Korean Copyright Act Chapter IV-2 (substantial-investment protection, 5-year term). | |
| **China** | Recipe itself generally not protectable as method; expressive arrangement protectable (Copyright Law of the PRC, 1990, amended 2010, 2020). | Yes. | No EU-style sui generis; expressive collections protected as compilations. | |
| **Israel** | Similar to US/UK; Copyright Act 5768-2007. | Creative expression protected. | Limited database protection through compilation-as-work. | |
| **Russia** | Civil Code Part IV protects creative expression; recipe-as-method not protectable. | Yes. | Database right under Civil Code (Article 1334) — 15 years. | |

**Operational implication for NutriMe (personal use).** The system can recompose ingredient lists + method steps from prior recipes (these are not copyrightable in any jurisdiction surveyed), but recomposed presentation must (a) generate its own creative expression (or remain stripped-down/factual) and (b) preserve and surface attribution to the source recipe(s) it drew from. ToS and database-right risk limit *bulk ingest*; per-recipe linked attribution + on-demand fetch under user subscription respects both legal and ethical constraints.

The personal-use distribution scope materially reduces sui generis database-right exposure (no public redistribution), but does not eliminate it for cross-border use under EU/UK rules. ToS-respect is unaffected by distribution scale — scraping a ToS-prohibited site for personal use still violates contract.

### 11. Recipe interchange formats

| Format | Standard / source | Adoption | Strengths | Weaknesses | Verdict |
|---|---|---|---|---|---|
| **schema.org/Recipe (JSON-LD)** [schema.org/Recipe](https://schema.org/Recipe) | W3C-adjacent open standard, Google-driven | **De facto dominant.** Embedded in nearly every major recipe publisher's HTML to drive Google rich results. | Web-native, JSON-LD machine-readable, large existing footprint. | Inconsistent field usage across publishers (e.g., `recipeYield`, `cookTime`, `recipeIngredient` formatting varies); free-text within fields. Doesn't cleanly express step-level ingredient binding (which step uses which ingredient). | **Practical interchange standard.** NutriMe should consume schema.org/Recipe as the primary external import format and emit it for interop. |
| **Cooklang** [cooklang.org](https://cooklang.org) | Open source, plain-text DSL with `@ingredient{quantity%unit}`, `#equipment`, `~timer{duration}` syntax | **Niche but growing** in tech-cooking communities; supported by a handful of OSS apps (Cooklang for iOS/macOS, CookCLI). | Plain-text, diff-able, version-controllable, LLM-friendly (token-efficient), step↔ingredient binding is structural. | Tiny ecosystem vs. schema.org; no standardization body; less complete metadata coverage. | **Excellent internal canonical representation** for NutriMe's own recipe corpus. Convert from schema.org on import; emit schema.org on share. |
| **hRecipe** [microformats.org/wiki/hrecipe](https://microformats.org/wiki/hrecipe) | Microformats community standard | Largely **superseded** by schema.org/Recipe; legacy presence on older sites. | HTML-native (not separate JSON-LD block). | Effectively deprecated. | Read-only legacy support. |
| **h-recipe** (microformats2) [microformats.org/wiki/h-recipe](https://microformats.org/wiki/h-recipe) | Microformats2 update | Marginal adoption. | Same as hRecipe. | Same. | Read-only. |
| **RecipeML** [www.formatdata.com/recipeml](http://www.formatdata.com/recipeml) | XML, ~2002 | **Effectively dead.** Some old desktop apps. | XML-rigorous. | Heavy, abandoned. | Optional legacy import. |
| **Open Recipe Format** [open-recipe-format.readthedocs.io](https://open-recipe-format.readthedocs.io) | YAML-based, OSS | Niche. | Human-friendly YAML. | Tiny ecosystem. | Optional. |
| **Cuisine.txt / Recipe Markdown variants** | Various | Niche. | Markdown-readable. | No standard. | Internal use only. |
| **MealMaster .mmf / MasterCook .mxp / MX2** | Legacy desktop formats | Legacy archives only. | Large historical user-recipe archives. | Old, encoding inconsistencies. | Read-only legacy import, useful for some PD-era community-collected corpora. |

**Architectural decision implication.** Use **schema.org/Recipe (JSON-LD)** as the primary import/export interchange and **Cooklang** (or a Cooklang-superset) as the internal canonical representation. Cooklang's step↔ingredient binding directly enables the multi-modal presentation requirement (Cookbook prose / structured text / video-anchored / illustrated) and the substitution / scaling / dietary-adaptation operations.

### 12. Attribution architecture — preserving provenance through transformation

Recipes commonly undergo a transformation chain: **sourced → adapted (substitution / scaling / dietary swap) → presented (modality choice) → executed (user-side cooking).** Per [Rule 8 epistemic trail](../00-meta/constitutional-rules.md#rule-8--epistemic-trail-of-honesty), each transformation is a provenance event.

**Recommended attribution data model:**

```
Recipe {
  id: <uuid>
  source: {
    type: <publisher | dataset | cookbook-PD | video | API | user-personal>
    citation: <full citation per citation-style.md>
    canonical_url | doi | isbn_page | video_url+timestamp | dataset_row_id
    accessed_on: <date>
    license: <license tag>
    framework_qualification: { criteria_met: [...], reviewed_on: <date> }
  }
  transformations: [
    { type: <import | conversion | substitution | scaling | dietary_adaptation | modality_swap>,
      operator: <user | system + version>,
      from: <prior_state_hash>, to: <new_state_hash>,
      rationale: <text>, evidence: [<citations>], performed_on: <timestamp> }
  ]
  presentation: {
    modality: <video-led | structured-text | cookbook-prose | illustrated>
    glossary_links: [<technique terms with source>]
  }
  attributions_surface_to_user: <required text + linkbacks shown adjacent to recipe>
}
```

**Patterns observed in the wild:**

- **Eat Your Books**-style: cite cookbook + page; never re-host body. Strongest provenance discipline.
- **NYT Cooking adaptation footers** ("Adapted from X by Y"): plaintext attribution; community norm in food publishing.
- **Smitten Kitchen / Food52 community norm**: "Adapted from [link]" with explanation of changes — informal but consistent.
- **Recipe blog with schema.org/Recipe + `isBasedOn` field**: machine-readable adaptation provenance; underused in practice but supported by schema.org.
- **Edamam API returns `source` field per recipe** — programmatic provenance.
- **Cookpad regional sites' "tsukurepo" (made-it report) chain** — UGC fork tree with attribution.
- **Academic / scholarly cookbook editions** (HathiTrust historical edition with editor's notes): explicit "[Editor's note: substitute X for Y, no longer available]" pattern — direct precedent for NutriMe's modernization annotations.

**Three architectural rules emerge:**

1. **Provenance is content, not metadata.** Source citation is rendered to the user adjacent to the recipe, not buried — same posture as Rule 1's "consult-professional adjacent to the uncertain content."
2. **Every transformation is logged with rationale.** Substitutions, scalings, dietary swaps, modality conversions — all carry a rationale + evidence chain queryable by the user (and by [audit-as-education](../00-meta/evidence-tiers.md#audit-as-education-pattern)).
3. **Modality is a presentation transformation, not a separate recipe.** A video-led, a structured-text, a cookbook-prose, and an illustrated rendering of the same Cooklang canonical recipe are four projections of one entity — provenance and substitutions persist across projections.

### 13. Open-questions answers (best-current)

**Q. Pricing model / license / quality / coverage / regional bias for each paid commercial API.**
Spoonacular and Edamam are the practical front-runners; pricing scales from free dev tier into ~$30–$250/mo for serious paid use; Edamam has stronger publisher-traceable provenance, Spoonacular has more nutrition / planning scaffolding. Both carry significant Western/Anglophone bias. Tasty has no legitimate API. Yummly is effectively gone for new integrators. Whisk → Samsung Food is partner-only. Regional commercial sites (Marmiton, ChefKoch, GialloZafferano, Cookpad-country sites) typically expose schema.org/Recipe markup but no general API; they are best treated as **link-out publishers**. **Re-verify all pricing tiers + ToS at adoption time** — the per-vendor specifics drift quarterly.

**Q. Legitimate paid pathways for editorial publishers.**
For NYT Cooking, ATK, ckbk, and Eat Your Books: subscription + subscriber-side reference + linkout. For Bon Appétit / Epicurious / Serious Eats / Food52 / King Arthur / BBC Good Food / Marmiton / ChefKoch: free public access + linkout + schema.org markup consumption. For NHS Eat Well / Health Canada / national health portals: open licensed; ingest permitted under attribution. For most non-Western national-cuisine portals (Hansik, MAFF Shokuiku materials): open / cultural-body licensed; ingest permitted. **Affiliate / cookbook-purchase linking** (Amazon Associates, Bookshop.org, publisher affiliate programs) is a feasible economic returnflow; lower priority for personal-use distribution but ethically appropriate where author revenue can be supported.

**Q. Realistic interpretive overhead for PD historical cookbooks.**
Substantial — see §5 caveats. Realistic estimate: a moderately experienced editor needs ~30–60 minutes per recipe to produce a usable modern adaptation with full provenance and modernization annotations. LLM-assisted modernization is feasible but constitutes a transformation that must carry a Rule 8 trail and human verification before user surfacing — and per Rule 4, the final recipe still derives from the source, not from generation. The per-recipe overhead is justified for high-value cultural-canon entries and not justified for the long tail; corpus-design implication: select a curated PD subset (~500–2000 recipes) for full modernization, leave the rest as historical-artifact references.

**Q. What's actually published openly vs. paywalled vs. unavailable for institutional culinary academy YouTube.**
Highly variable. Le Cordon Bleu, ICE, CIA, ATK, and Bon Appétit publish substantial open YouTube content for marketing purposes; their full curricula are paywalled. ALMA, Tsuji, Hattori publish much less open content in English. Hansik (Korea) is exceptionally open and English-accessible. IHM India campuses are inconsistent — some publish actively, others not at all. The system should treat any single institution as a *probable* source whose actual yield must be verified at corpus-build time.

**Q. Realistic English-language coverage of non-Western sources, and what's lost in translation.**
Coverage is asymmetric: Korean (Hansik + Maangchi + diaspora), Japanese (large diaspora + MAFF Shokuiku translation effort), Indian (large diaspora + IHM + ICAR English output), Mexican (Diana Kennedy lineage + Pati Jinich), and Levantine (Ottolenghi/Roden/Tamimi/Kassis lineage) are well-covered in English. **Substantial gaps**: West / East / Southern African cuisines (improving but thin); Central Asian; many regional Chinese cuisines beyond Cantonese / Sichuan / Shanghai (Hunan, Yunnan, Hakka, Dongbei underrepresented); regional Brazilian beyond Bahian; Andean beyond Peruvian; many regional Indian cuisines (Northeast India, smaller communities); Pacific Islander; regional South-East-Asian beyond Thai/Vietnamese (Filipino growing, Lao/Burmese/Cambodian thin). What gets lost in translation: ingredient-substitution precision, technique vocabulary that doesn't map cleanly (e.g., wok hei, dashi categories, masala-building sequences), regional pantry assumptions, household-vs-restaurant register distinctions, and culturally-loaded dietary framing (e.g., Ayurvedic guna categories, TCM food-energy categories) that get flattened in English.

**Q. State of recipe interchange format adoption.**
**schema.org/Recipe (JSON-LD) is the practical standard** — driven by Google rich-results market pressure, embedded in nearly every major recipe publisher. **Cooklang is the most interesting alternative** for a system like NutriMe because of its structural step↔ingredient binding and LLM-friendly plain-text format, but its ecosystem is small. NutriMe should consume schema.org, canonicalize internally to a Cooklang-superset, and emit schema.org for interop.

**Q. Attribution / provenance architecture patterns that work in practice.**
See §12. The robust pattern is: source citation rendered adjacent to recipe (not buried); every transformation logged with rationale + evidence; modalities treated as projections of one canonical recipe entity; user-visible audit trail per [audit-as-education](../00-meta/evidence-tiers.md#audit-as-education-pattern).

### 14. Surprises + gaps surfaced during the sweep

- **Tasty has no legitimate ingest path** — was assumed to be a viable API source; turns out third-party RapidAPI mirrors carry ToS risk and Tasty itself doesn't license bulk API. Strict link-out treatment only.
- **Yummly is effectively gone** — implications: don't plan around it.
- **Korean Food Foundation (Hansik) is unusually open** — qualifies simultaneously as cuisine source, cultural-heritage authority, and Tier 1–adjacent national-body source. There is no fully analogous body for many other major non-Western cuisines (no equivalent for Indian, Chinese, Mexican, Vietnamese, Thai national cuisine bodies that publish at Hansik's openness + English-output level). This is a real asymmetry worth surfacing.
- **ckbk is the strongest legitimate cookbook-content subscription** under personal-use scope and is more cuisine-diverse than US-centric peers. Worth foregrounding.
- **Public-domain non-Western canon is more accessible than expected** in source-language form (Ibn Sayyar al-Warraq, Yuan Mei, Eumsik Dimibang) but the **English translations are mostly in copyright**, which means non-English-reading users lose access without subscription/library mediation.
- **Cooklang is small but technically excellent** for an LLM-mediated system; this is a place where NutriMe's design is moderately ahead of most consumer recipe apps.
- **Database-right exposure** under EU/UK Directive 96/9/EC is the single biggest sui-generis legal lever a future-non-personal-use scope must plan for.
- **Major non-Western coverage gaps**: West/East/Southern African; regional Chinese beyond top-3; regional Indian beyond top-5; Central Asian; Pacific Islander. Diaspora creators close some of these gaps; institutional sources do not.
- **TikTok / Reels exclusion is correct but costs reach** to younger users for whom these are the dominant cuisine-discovery surface. Worth revisiting in a future scope as a **discovery / recommendation signal** (what's trending) without ingesting the content itself.
- **"Recipe-as-method is uncopyrightable" is universally true across surveyed jurisdictions** but the *expressive* layer (headnotes, photography, narrative) is universally protected, so an attribution-respecting design is required regardless of legal floor.

## References

> All web URLs accessed 2026-04-28 (the dynamic re-verification step in [dynamic-research-expansion.md](../00-meta/dynamic-research-expansion.md) applies to commercial pricing + ToS specifics in particular).

### Commercial APIs

- **Spoonacular** (n.d.). *Food API & Documentation*. spoonacular. https://spoonacular.com/food-api. Accessed 2026-04-28.
- **Spoonacular** (n.d.). *Food API Pricing*. spoonacular. https://spoonacular.com/food-api/pricing. Accessed 2026-04-28.
- **Edamam** (n.d.). *Recipe Search API*. Edamam. https://developer.edamam.com/edamam-recipe-api. Accessed 2026-04-28.
- **Edamam** (n.d.). *API Plans and Pricing*. Edamam. https://www.edamam.com/api-plans-and-pricing. Accessed 2026-04-28.
- **TheMealDB** (n.d.). *TheMealDB API*. TheMealDB. https://www.themealdb.com/api.php. Accessed 2026-04-28.
- **Samsung Food (formerly Whisk)** (n.d.). *Samsung Food*. Samsung. https://samsungfood.com. Accessed 2026-04-28.
- **BuzzFeed Tasty** (n.d.). *Terms of Use*. BuzzFeed. https://www.buzzfeed.com/about/terms. Accessed 2026-04-28.

### Curated publishers — paid + free editorial

- **The New York Times Company** (n.d.). *NYT Cooking*. https://cooking.nytimes.com. Accessed 2026-04-28.
- **Condé Nast** (n.d.). *Bon Appétit*. https://www.bonappetit.com. Accessed 2026-04-28.
- **Condé Nast** (n.d.). *Epicurious*. https://www.epicurious.com. Accessed 2026-04-28.
- **Dotdash Meredith** (n.d.). *Serious Eats*. https://www.seriouseats.com. Accessed 2026-04-28.
- **America's Test Kitchen** (n.d.). *America's Test Kitchen Online*. https://www.americastestkitchen.com. Accessed 2026-04-28.
- **Vox Media** (n.d.). *Eater*. https://www.eater.com. Accessed 2026-04-28.
- **Food52, Inc.** (n.d.). *Food52*. https://food52.com. Accessed 2026-04-28.
- **King Arthur Baking Company** (n.d.). *King Arthur Baking*. https://www.kingarthurbaking.com. Accessed 2026-04-28.
- **Immediate Media** (n.d.). *BBC Good Food*. https://www.bbcgoodfood.com. Accessed 2026-04-28.
- **NHS** (n.d.). *Eat Well*. National Health Service (UK). https://www.nhs.uk/live-well/eat-well. Accessed 2026-04-28. License: Open Government Licence v3.0.
- **TF1 Group** (n.d.). *Marmiton*. https://www.marmiton.org. Accessed 2026-04-28.
- **Webedia** (n.d.). *750g*. https://www.750g.com. Accessed 2026-04-28.
- **Gruner+Jahr / RTL Deutschland** (n.d.). *Chefkoch*. https://www.chefkoch.de. Accessed 2026-04-28.
- **EatSmarter** (n.d.). *EatSmarter*. https://eatsmarter.de. Accessed 2026-04-28.
- **Mondadori** (n.d.). *GialloZafferano*. https://www.giallozafferano.it. Accessed 2026-04-28.
- **El País** (n.d.). *El Comidista*. https://elpais.com/gastronomia/el-comidista. Accessed 2026-04-28.
- **Albert Heijn** (n.d.). *AllerHande*. https://www.ah.nl/allerhande. Accessed 2026-04-28.
- **Health Canada** (n.d.). *Canada's Food Guide — Recipes*. https://food-guide.canada.ca/en/recipes. Accessed 2026-04-28.
- **Korean Food Foundation** (n.d.). *Hansik — Korean Food*. https://www.hansik.or.kr. Accessed 2026-04-28.
- **Ministry of Agriculture, Forestry and Fisheries (Japan)** (n.d.). *MAFF — Shokuiku materials*. https://www.maff.go.jp. Accessed 2026-04-28.

### Open datasets

- Bień, M., Gilski, M., Maciejewska, M., Taisner, W., Wisniewski, D., & Lawrynowicz, A. (2020). *RecipeNLG: A Cooking Recipes Dataset for Semi-Structured Text Generation*. Proceedings of the 13th International Conference on Natural Language Generation. https://recipenlg.cs.put.poznan.pl. Accessed 2026-04-28.
- Marin, J., Biswas, A., Ofli, F., Hynes, N., Salvador, A., Aytar, Y., Weber, I., & Torralba, A. (2019). *Recipe1M+: A Dataset for Learning Cross-Modal Embeddings for Cooking Recipes and Food Images*. IEEE Transactions on Pattern Analysis and Machine Intelligence. http://pic2recipe.csail.mit.edu. Accessed 2026-04-28.
- **Food.com Recipes & Interactions (Kaggle)** (n.d.). https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions. Accessed 2026-04-28. License: CC-BY-NC-SA-4.0 on Kaggle re-publication; upstream Food.com ToS forbids scraping.
- **OpenRecipes** (legacy, fictivekin). https://github.com/fictivekin/openrecipes. Accessed 2026-04-28.
- **Common Crawl Foundation** (n.d.). *Common Crawl*. https://commoncrawl.org. Accessed 2026-04-28.
- **schema.org** (n.d.). *Recipe schema*. https://schema.org/Recipe. Accessed 2026-04-28.

### Public-domain historical cookbook libraries + works

- **Project Gutenberg** (n.d.). https://www.gutenberg.org. Accessed 2026-04-28.
- **HathiTrust Digital Library** (n.d.). https://www.hathitrust.org. Accessed 2026-04-28.
- **Internet Archive** (n.d.). https://archive.org. Accessed 2026-04-28.
- **Library of Congress** (n.d.). *Rare Book and Special Collections*. https://www.loc.gov. Accessed 2026-04-28.
- **Schlesinger Library on the History of Women in America** (n.d.). Harvard Radcliffe Institute. https://www.radcliffe.harvard.edu/schlesinger-library. Accessed 2026-04-28.
- **Michigan State University Libraries** (n.d.). *Feeding America: The Historic American Cookbook Project*. https://d.lib.msu.edu/fa. Accessed 2026-04-28.
- **Bibliothèque nationale de France** (n.d.). *Gallica*. https://gallica.bnf.fr. Accessed 2026-04-28.
- **Deutsche Digitale Bibliothek** (n.d.). https://www.deutsche-digitale-bibliothek.de. Accessed 2026-04-28.
- **Europeana** (n.d.). https://www.europeana.eu. Accessed 2026-04-28.
- **Wellcome Collection** (n.d.). https://wellcomecollection.org. Accessed 2026-04-28.
- Apicius (compiled ~4th–5th c.). *De re coquinaria*. (Public domain Latin text; multiple PD translations.)
- La Varenne, F.P. (1651). *Le Cuisinier françois*. (PD via Gallica.)
- Beeton, I. (1861). *Mrs. Beeton's Book of Household Management*. (PD via Project Gutenberg.)
- Farmer, F.M. (1896). *The Boston Cooking-School Cook Book*. (PD via Project Gutenberg.)
- Carême, M.-A. (1833–1847). *L'Art de la cuisine française au dix-neuvième siècle*. (PD.)
- Glasse, H. (1747). *The Art of Cookery Made Plain and Easy*. (PD.)
- Escoffier, A. (1903). *Le Guide culinaire*. (PD status varies — verify edition + jurisdiction.)
- Ibn Sayyar al-Warraq (~10th c.). *Kitāb al-Ṭabīkh*. (Source-language PD; modern translations typically in copyright.)
- Yuan Mei (1792). *Suiyuan Shidan / 隨園食單*. (Source-language PD; Sean J.S. Chen 2018 translation in copyright.)
- Jang Gye-hyang (~1670). *Eumsik Dimibang / 음식디미방*. (Source-language PD.)

### Modern indexed cookbook databases

- **Eat Your Books** (n.d.). https://www.eatyourbooks.com. Accessed 2026-04-28.
- **ckbk** (n.d.). https://www.ckbk.com. Accessed 2026-04-28.
- **Cookpad** (n.d.). https://cookpad.com. Accessed 2026-04-28.
- **Kitchen Stories** (n.d.). https://www.kitchenstories.com. Accessed 2026-04-28.

### Institutional culinary academies + national / cultural bodies

- **Le Cordon Bleu** (n.d.). https://www.cordonbleu.edu. Accessed 2026-04-28.
- **Institut Lyfe (formerly Institut Paul Bocuse)** (n.d.). https://www.institutpaulbocuse.com. Accessed 2026-04-28.
- **Ferrandi Paris** (n.d.). https://www.ferrandi-paris.com. Accessed 2026-04-28.
- **École Nationale Supérieure de Pâtisserie / Ducasse Education** (n.d.). https://www.ensp-adf.com. Accessed 2026-04-28.
- **ALMA — La Scuola Internazionale di Cucina Italiana** (n.d.). https://www.alma.scuolacucina.it. Accessed 2026-04-28.
- **ICIF — Italian Culinary Institute for Foreigners** (n.d.). https://www.icif.com. Accessed 2026-04-28.
- **Tsuji Culinary Institute** (n.d.). https://www.tsuji.ac.jp. Accessed 2026-04-28.
- **Hattori Nutrition College** (n.d.). https://www.hattori.ac.jp. Accessed 2026-04-28.
- **Indian Culinary Institute** (n.d.). https://ici.nic.in. Accessed 2026-04-28.
- **National Council for Hotel Management and Catering Technology / IHM federated network** (n.d.). https://www.nchm.gov.in. Accessed 2026-04-28.
- **National Institute of Nutrition (India)** (n.d.). https://www.nin.res.in. Accessed 2026-04-28.
- **Indian Council of Agricultural Research** (n.d.). https://icar.org.in. Accessed 2026-04-28.
- **China Cuisine Association / 中国烹饪协会** (n.d.). http://www.ccas.com.cn. Accessed 2026-04-28.
- **Korean Food Foundation (Hansik)** (n.d.). https://www.hansik.or.kr. Accessed 2026-04-28.
- **ICUM — Instituto Culinario de México** (n.d.). https://icum.edu.mx. Accessed 2026-04-28.
- **CONABIO — Comisión Nacional para el Conocimiento y Uso de la Biodiversidad (México)** (n.d.). https://www.biodiversidad.gob.mx. Accessed 2026-04-28.
- **Culinary Institute of America** (n.d.). https://www.ciachef.edu. Accessed 2026-04-28.
- **Institute of Culinary Education** (n.d.). https://www.ice.edu. Accessed 2026-04-28.
- **Johnson & Wales University** (n.d.). https://www.jwu.edu. Accessed 2026-04-28.
- **Leiths School of Food and Wine** (n.d.). https://leiths.com. Accessed 2026-04-28.
- **University of Gastronomic Sciences, Pollenzo** (n.d.). https://www.unisg.it. Accessed 2026-04-28.

### Cultural-heritage organizations

- **UNESCO** (n.d.). *Intangible Cultural Heritage Lists*. https://ich.unesco.org. Accessed 2026-04-28. Includes inscribed culinary traditions (Mediterranean Diet 2010; Traditional Mexican Cuisine 2010; Washoku 2013; Kimjang 2013; French gastronomic meal 2010; Couscous 2020; Ceviche 2023; Singapore hawker culture 2020; Borscht 2022; etc.).
- **Slow Food International** (n.d.). https://www.slowfood.com. Accessed 2026-04-28.
- **NATIFS / Indigenous Food Lab** (n.d.). https://www.natifs.org. Accessed 2026-04-28.
- **First Nations Development Institute** (n.d.). https://www.firstnations.org. Accessed 2026-04-28.

### Recipe-IP law sources

- *Publications International, Ltd. v. Meredith Corp.*, 88 F.3d 473 (7th Cir. 1996). https://law.justia.com/cases/federal/appellate-courts/F3/88/473/. Accessed 2026-04-28.
- *Tomaydo-Tomahhdo, LLC v. Vozary*, 629 F. App'x 658 (6th Cir. 2015). https://law.justia.com/cases/federal/appellate-courts/ca6/14-3964/14-3964-2015-08-04.html. Accessed 2026-04-28.
- *Feist Publications, Inc. v. Rural Telephone Service Co.*, 499 U.S. 340 (1991). https://supreme.justia.com/cases/federal/us/499/340/. Accessed 2026-04-28.
- 17 U.S.C. §102 — *Subject matter of copyright: In general*. https://www.law.cornell.edu/uscode/text/17/102. Accessed 2026-04-28.
- U.S. Copyright Office (n.d.). *Recipes (FAQ)*. https://www.copyright.gov/help/faq/faq-protect.html#recipe. Accessed 2026-04-28.
- **Directive 96/9/EC of the European Parliament and of the Council of 11 March 1996 on the legal protection of databases**. https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:31996L0096. Accessed 2026-04-28.
- **Directive 2001/29/EC** (InfoSoc). https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:32001L0029. Accessed 2026-04-28.
- *Infopaq International A/S v. Danske Dagblades Forening*, C-5/08 (CJEU 2009). https://curia.europa.eu/juris/liste.jsf?num=C-5/08. Accessed 2026-04-28.
- *Painer v. Standard VerlagsGmbH*, C-145/10 (CJEU 2011). https://curia.europa.eu/juris/liste.jsf?num=C-145/10. Accessed 2026-04-28.
- *CCH Canadian Ltd. v. Law Society of Upper Canada*, 2004 SCC 13. https://scc-csc.lexum.com/scc-csc/scc-csc/en/item/2125/index.do. Accessed 2026-04-28.
- *IceTV Pty Ltd v. Nine Network Australia Pty Ltd*, [2009] HCA 14. http://www.austlii.edu.au/cgi-bin/viewdoc/au/cases/cth/HCA/2009/14.html. Accessed 2026-04-28.
- **UK Copyright, Designs and Patents Act 1988** (with retained-EU database-rights amendments post-Brexit). https://www.legislation.gov.uk/ukpga/1988/48/contents. Accessed 2026-04-28.
- **National Archives (UK)** (n.d.). *Open Government Licence v3.0*. https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/. Accessed 2026-04-28.
- **Copyright Act of Japan, Act No. 48 of 1970** (English translation, Japanese Law Translation). http://www.japaneselawtranslation.go.jp/law/detail/?id=3379. Accessed 2026-04-28.
- **Copyright Law of the People's Republic of China** (1990, amended 2010 + 2020). http://en.npc.gov.cn.cdurl.cn. Accessed 2026-04-28.
- **Korean Copyright Act** (Act No. 432 of 1957, as amended). https://elaw.klri.re.kr. Accessed 2026-04-28.
- **Copyright Act 1968 (Cth) (Australia)**. https://www.legislation.gov.au/Series/C1968A00063. Accessed 2026-04-28.
- **Copyright Act 1994 (NZ)**. https://www.legislation.govt.nz/act/public/1994/0143/latest/DLM345634.html. Accessed 2026-04-28.
- **Copyright Act, R.S.C. 1985, c. C-42 (Canada)**. https://laws-lois.justice.gc.ca/eng/acts/c-42/. Accessed 2026-04-28.

### Recipe interchange formats

- **schema.org** (n.d.). *Recipe*. https://schema.org/Recipe. Accessed 2026-04-28.
- **Cooklang** (n.d.). https://cooklang.org. Accessed 2026-04-28.
- **Microformats** (n.d.). *hRecipe + h-recipe*. https://microformats.org/wiki/hrecipe and https://microformats.org/wiki/h-recipe. Accessed 2026-04-28.
- **RecipeML** (n.d.). http://www.formatdata.com/recipeml. Accessed 2026-04-28.
- **Open Recipe Format** (n.d.). https://open-recipe-format.readthedocs.io. Accessed 2026-04-28.

### Glossary / technique reference works

- The Culinary Institute of America (2011). *The Professional Chef* (9th ed.). Wiley. ISBN 978-0470421352.
- Montagné, P. (Ed., orig. 1938; updated 2009 EN ed.). *Larousse Gastronomique*. Hamlyn / Clarkson Potter.
- Labensky, S.R., & Hause, A.M. (current ed.). *On Cooking: A Textbook of Culinary Fundamentals*. Pearson.
- Rombauer, I.S., Becker, M.R., Becker, E., & Becker, J. (2019). *Joy of Cooking* (2019 ed.). Scribner.
- McGee, H. (2004). *On Food and Cooking: The Science and Lore of the Kitchen* (rev. ed.). Scribner.
- Myhrvold, N., Young, C., & Bilet, M. (2011 + ongoing). *Modernist Cuisine*. The Cooking Lab.
- **Wikipedia / Wiktionary culinary technique pages**. https://en.wikipedia.org and https://en.wiktionary.org. License: CC-BY-SA. Accessed 2026-04-28.
