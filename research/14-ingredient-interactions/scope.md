# Sweep #14 — Ingredient Interactions, Flavor Science, and Pairing Knowledge

> Status: Scoped (research launching 2026-05-01)
> Last updated: 2026-05-01

## Purpose

Build a research-grounded reference map of ingredient interaction science, flavor pairing knowledge, and the underlying food-science basis for *why* ingredients work together. This is **flavor science + culinary pairing knowledge**, distinct from recipes (sweep #11), cuisine + technique knowledge (sweep #12), food composition data (sweep #2), and educational content (sweep #8).

## Why this matters for NutriMe

- **Substitution logic** ([sweep #13 grocery](../13-grocery-infrastructure/scope.md)) — when an ingredient isn't available, *why* a substitute works (or doesn't) requires pairing-science understanding
- **Audit-as-education** — when the system surfaces "we suggested adding lemon juice here," explaining *why* (acid balances richness, brightens herbal notes, cuts through fat) deepens the user's culinary literacy
- **Stretch-recipe disclosure** ([Tension #7](../00-meta/synthesis.md#tension-7--stretch-recipe-metadata-for-honest-disclosure-not-a-default-filter)) — when a recipe introduces a new ingredient or pairing, the *why* helps the user understand what they're trying
- **Cuisine horizon-broadening** — Korean dishes use gochugaru with garlic + ginger + sesame for specific reasons; understanding the principles makes new cuisines less mysterious
- **Knowledge model curiosity tracking** — when a user shows interest in a cuisine or technique, ingredient-interaction knowledge feeds richer educational delivery

## Deliverable

An annotated reference map containing:

- **Source qualification framework** for ingredient-interaction sources, instantiating the [framework-over-source-list principle](../00-meta/dynamic-research-expansion.md#framework-over-source-list--the-corpus-design-principle)
- Per-source-class inventory across Tiers 1–4 (below)
- The flavor-pairing-controversy audit — the aroma-compound-overlap hypothesis (Ahn et al. 2011) vs. contrasting-compound traditions (many Asian cuisines), with honest evidence-tier framing per the [audit-as-education pattern](../00-meta/evidence-tiers.md#audit-as-education-pattern)
- Geographic + cuisine pairing-tradition coverage across [primary research scope](../00-meta/geographic-scope.md)
- Scientific basis for pairings where peer-reviewed evidence exists (volatile compounds, Maillard chemistry, capsaicin pharmacology, taste-receptor science) — practitioner-book claims cross-referenced to primary sources where available
- Cross-references to existing sweeps for integration pass

This is a **reference map**, not corpus build.

## Source qualification framework

Recipe sources qualify by passing through the framework, not by appearing on a fixed list:

- **Institutional credibility** — peer-reviewed food-science journal, established culinary academy, recognized publisher, credentialed practitioner with accountable platform
- **Scientific grounding when available** — primary food-science sources cited where the claim is mechanistic; practitioner books cross-referenced to primary literature when the practitioner's claim has scientific basis
- **Honest evidence framing** — practitioner-knowledge claims (Tier 2) flagged as such even when widely accepted; controversies surfaced openly per audit-as-education
- **License / ToS compliance** — accessible through legitimate paid pathways or public domain or explicitly permissive license
- **Provenance retention** — source supports attribution + traceability through transformation

## In scope

### Tier 1 — institutional / canonical food science

- Harold McGee — *On Food and Cooking* (canonical; updated 2004 ed.)
- J. Kenji López-Alt — *The Food Lab* (CIA-credentialed, scientifically rigorous)
- Hervé This — *Molecular Gastronomy* + *Building a Meal* + *Note-by-Note Cooking* (molecular gastronomy / food chemistry)
- Nathan Myhrvold — *Modernist Cuisine* (6 vol.) + *Modernist Cuisine at Home* + *Modernist Bread* + *Modernist Pizza*
- Shirley Corriher — *CookWise* + *BakeWise*
- Peter Barham — *The Science of Cooking*
- Alan Davidson — *The Oxford Companion to Food* (2nd ed.; reference-grade)
- Ian Hornsey — *A History of Beer and Brewing* + *Alcohol and its Role in the Evolution of Human Society* (fermentation)
- Sandor Katz — *The Art of Fermentation* + *Fermentation Journeys* (fermentation as flavor source)
- Andoni Luis Aduriz / Ferran Adrià — *Mugaritz* + elBulli technique compendia (avant-garde flavor logic)
- Heston Blumenthal — *The Big Fat Duck Cookbook* + *In Search of Perfection* (technique + flavor science)
- Robert Wolke — *What Einstein Told His Cook* (food chemistry for general audiences but rigorously sourced)
- **Peer-reviewed food science journals** — *Journal of Food Science*, *Food Chemistry*, *International Journal of Gastronomy and Food Science*, *Journal of Sensory Studies*, *Food Quality and Preference*, *Chemical Senses*, *Flavour and Fragrance Journal*, *Journal of Agricultural and Food Chemistry*
- **Institutional white literature** — Monell Chemical Senses Center publications, Pangborn Sensory Science Symposium proceedings, Institute of Food Technologists (IFT) publications

### Tier 2 — practitioner-codified pairing knowledge

- *The Flavor Bible* + *The Vegetarian Flavor Bible* (Page + Dornenburg)
- Niki Segnit — *The Flavor Thesaurus* + *Lateral Cooking*
- Briscione + Parkhurst — *The Flavor Matrix* (data-driven pairings)
- Karen Page — *The Food Lover's Companion* (Herbst, ed.)
- *Larousse Gastronomique* (Hamlyn ed., reference-grade pairing tradition)
- *The Professional Chef* (CIA — pairing as curriculum element)
- *On Cooking* (Labensky + Hause — culinary pedagogy reference)
- *Joy of Cooking* technique sections (Rombauer / Becker — practitioner reference)
- *Salt, Fat, Acid, Heat* (Samin Nosrat — pairing through balance principles)
- *The Art of Mexican Cooking* (Diana Kennedy — regional Mexican flavor logic)
- Madhur Jaffrey works — *An Invitation to Indian Cooking* (regional Indian masala construction)
- Fuchsia Dunlop — *Land of Plenty* + *Every Grain of Rice* (regional Chinese flavor logic, especially Sichuan)
- Maangchi (Korean home-cooking flavor foundations)
- Yotam Ottolenghi — *Plenty* + *Jerusalem* + *Simple* (Mediterranean / Middle Eastern pairing pedagogy)
- Claudia Roden — *The New Book of Middle Eastern Food* (regional Middle Eastern + North African)
- Paula Wolfert — *The Cooking of the Eastern Mediterranean* + *The Food of Morocco* (regional reference)
- Cheryl Sternman Rule — pairing-focused works
- Institutional culinary academy curricula on flavor pairing (cross-references [sweep #12](../12-skills-by-cuisine/scope.md) institutional list — Le Cordon Bleu, ALMA, Tsuji, Ferrandi, Hattori, IHM India, China Culinary Academy, Korean Food Foundation, ICUM)

### Tier 3 — ingredient databases

- FlavorDB (academic; Indian Institute of Science)
- FoodPairing.com (commercial; Sense for Taste / Bernard Lahousse — based on aroma-compound-overlap hypothesis)
- Open Food Facts ingredient-level data (cross-references [sweep #2](../02-food-composition-databases/scope.md))

### Tier 4 — informational / cultural / hypothesis-generating

- Khymos blog (Martin Lersch, food science blog)
- Serious Eats food-science articles (cross-references [sweep #11](../11-recipe-sourcing/scope.md))
- Cultural cookbooks documenting traditional ingredient combinations (cross-references [sweep #11 historical canon](../11-recipe-sourcing/scope.md))

### The flavor-pairing controversy

The aroma-compound-overlap hypothesis (Ahn et al. 2011, *Scientific Reports*) — foods that share volatile compounds pair well — became the basis of FoodPairing.com and IBM Chef Watson. **Subsequent analysis has been mixed:**

- Western cuisines tend toward shared-compound pairings
- Many Asian cuisines tend toward *contrasting*-compound pairings
- The universality of the hypothesis is genuinely contested in the food-science literature

This is exactly the kind of evidence-tier question Rule 7 + audit-as-education exist for. The sweep should:

- Cover both compound-overlap AND contrasting-compound traditions equal-weighted (per Rule 9 geographic neutrality)
- Surface the controversy honestly in any audit-as-education content built from this corpus
- Cite the primary literature (Ahn et al. + critiques + alternative formulations) rather than presenting either hypothesis as settled

### Geographic + cuisine scope (primary)

Per [geographic-scope.md](../00-meta/geographic-scope.md). All of the following as primary, opportunistic for African / Caribbean / Pacific Islander where sources exist:

- Western flavor-pairing tradition (well-documented in English)
- Japanese umami / dashi tradition (Kikunae Ikeda's umami discovery; well-documented)
- Korean flavor-pairing (gochugaru + garlic + ginger + sesame foundational base; less documented in English)
- Chinese five-flavor balance (sweet/sour/salty/bitter/umami + cooling/warming Eastern medicine framings)
- Indian masala construction (regional variation: tadka / chhaunk / baghar; tempering as flavor-extraction)
- Middle Eastern + North African (za'atar / ras el hanout / dukkah construction; sumac / preserved-lemon roles)
- Latin American (sofrito / mirepoix variants; mole as flavor-pairing case study)
- Mexican specifically — chile-pairing science is its own deep tradition

### Corpus structure (informs design phase)

Both views supported:

- **Ingredient-as-node** — one document per ingredient (what is this, what role does it play, where does it come from, what's its food-science profile)
- **Pairing-as-document** — each meaningful pairing or pairing-family gets its own document (why these go together, scientific basis, cultural origin, technique requirements)

Storage cost is trivial; both views serve different real queries.

## Out of scope (with reasons)

- **Recipe corpus** — covered in [sweep #11](../11-recipe-sourcing/scope.md). Pairing knowledge informs recipe selection + substitution; this sweep doesn't duplicate recipes.
- **Cuisine + technique knowledge** — covered in [sweep #12](../12-skills-by-cuisine/scope.md). Pairing-as-technique cross-references but doesn't replicate.
- **Food composition data** — covered in [sweep #2](../02-food-composition-databases/scope.md). Composition-data ingredient identity informs pairing-corpus ingredient identity; cross-referenced via authority table.
- **Health / nutrition claims about specific pairings** — these need Tier 1/2 peer-reviewed evidence per Rule 7. Pairing science is about flavor + culinary function, not nutrition outcomes. Health claims based on pairings (e.g., "garlic + onion are anti-inflammatory together") are out unless backed by Tier 1/2 evidence and rooted in food-science mechanism.

## Cross-references built in from the start

- [Sweep #2 (food composition databases)](../02-food-composition-databases/scope.md) — composition data per ingredient; authority table resolves ingredient-name variants
- [Sweep #11 (recipe sourcing)](../11-recipe-sourcing/scope.md) — pairing examples in the recipe corpus; pairing knowledge informs recipe ranking
- [Sweep #12 (skills-by-cuisine)](../12-skills-by-cuisine/scope.md) — technique-pairing-cuisine knowledge (tadka enables Indian pairings, sofrito enables Latin / Spanish pairings)
- [Sweep #13 (grocery infrastructure)](../13-grocery-infrastructure/scope.md) — substitution logic informed by pairing science
- [Audit-as-education pattern](../00-meta/evidence-tiers.md#audit-as-education-pattern) — flavor-pairing-controversy framing
- [Operational tradition as supplementary basis](../00-meta/evidence-tiers.md#operational-tradition-as-supplementary-basis) — practitioner pairing knowledge sits in this category for many claims

## Open questions for the research

- What's the strongest peer-reviewed evidence on the aroma-compound-overlap hypothesis vs. contrasting-compound traditions? Where do current food-science meta-analyses land?
- For each pairing tradition (Western, Japanese umami, Chinese five-flavor, Indian masala, Middle Eastern aromatic, Latin sofrito-based, Korean gochugaru-base): what's the canonical reference + the primary-literature backing where it exists?
- Which Tier 1 sources have the strongest peer-reviewed citations vs. which are practitioner-authoritative without primary-literature support?
- How does the FlavorDB academic project compare to FoodPairing.com commercial framing — what's reproducible from FlavorDB?
- For non-Western pairing traditions: which sources (cookbook authors, academic centers, national culinary institutes) are best primary references?
- What's the state of food-science research on cooking transformations of pairings (e.g., does tomato + basil pairing science change between raw and cooked applications)?

## Cross-cuts (after research returns)

A structured **integration pass** runs after research findings come back to surface:

- Updates needed to existing sweeps (#2, #11, #12, #13)
- Updates needed to existing constitutional rules / meta docs (especially [evidence-tiers.md](../00-meta/evidence-tiers.md) for the flavor-pairing-controversy framing if it requires new framing)
- Stage 3 architecture decisions that may need updates (especially [B1](../00-meta/architecture.md#b1--semantic-rag-vs-structured-query-strategy) corpus organization — ingredient-as-node fits naturally with the markdown corpus + authority table from A4)
- Roadmap items (especially publication ambitions if ingredient-interaction work surfaces a publishable contribution)
- New tensions surfaced for synthesis dialogue

## Findings

To be populated when research is run.

## References

To be populated. Add new sources to [sources.md](../00-meta/sources.md) when added.
