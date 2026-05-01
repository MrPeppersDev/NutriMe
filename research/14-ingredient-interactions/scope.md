# Sweep #14 — Ingredient Interactions, Flavor Science, and Pairing Knowledge

> Status: Researched + integration pass applied (2026-05-01)
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

### 0. Epistemic note (web-tools constraint)

This sweep was executed with **WebSearch and WebFetch denied**. All findings below draw on training-data recall and standard reference knowledge. The following classes of detail are **most prone to memory drift** and should be **re-verified during the integration pass** when web access is restored:

- Specific publication dates / edition numbers for cookbooks (especially McGee 2004 vs. 1984 vs. 2025 hypothetical revisions, Modernist Cuisine volume counts, *Larousse Gastronomique* edition years)
- Journal impact factors, current editorial scope, and any title changes since training cutoff
- Exact author lists and DOIs for the Ahn et al. 2011 paper and its critique chain (Jain et al., Varshney, etc.)
- URLs for FlavorDB (academic site) and FoodPairing.com (commercial), and current license / API terms
- Whether specific cookbooks have been re-issued, expanded, or had companion volumes added
- Institutional white-literature publication catalogues (Monell, Pangborn, IFT) — current proceedings titles and access pathways

Specific numbers, dates, and counts are tagged inline with `[verify]` where memory drift is plausible. The structure of the inventory, the qualitative framing of each source, and the substantive scientific content (Maillard, umami synergy, capsaicin pharmacology) are stable across sources and lower drift risk.

### 1. Source qualification framework operationalized

Applying the [framework-over-source-list principle](../00-meta/dynamic-research-expansion.md#framework-over-source-list--the-corpus-design-principle) to ingredient-interaction sources, the qualification gates are:

1. **Institutional credibility** — peer-reviewed journal indexed in Web of Science / Scopus / PubMed; cookbook published by a recognized house (Scribner, Norton, Ten Speed, Phaidon, Workman, Ecco, Knopf, Wiley); author with credentialed practice (CIA / Le Cordon Bleu / FCSI / IFST / IFT) or institutional affiliation (university food-science department, Monell, INRAE, Wageningen, UC Davis, Cornell, Reading, Nottingham).
2. **Scientific grounding when available** — for any mechanistic claim (e.g., "tomato + basil share volatile X"), the practitioner book's claim should be cross-walked to a primary food-science citation (typically *Journal of Agricultural and Food Chemistry*, *Food Chemistry*, *Flavour and Fragrance Journal*). Practitioner books are quoted; primary literature is cited as the authority.
3. **Honest evidence framing** — practitioner-tradition claims (e.g., Page + Dornenburg "matches well with") tagged Tier 4 informational unless cross-walked to a primary source. Where cross-walked, retain dual provenance (practitioner + primary).
4. **License / ToS compliance** — books accessed via legitimate purchase or library. Academic databases (FlavorDB) accessed per their stated license. Commercial APIs (FoodPairing.com) treated as Tier 4 commercial unless we hold a license.
5. **Provenance retention** — every pairing claim in the corpus retains: source-author + source-title + page-or-section + evidence-tier + (where applicable) primary-literature cross-reference + accessed-on date.
6. **Geographic neutrality (Rule 9)** — Western pairing tradition does not get default-canon status. Korean / Indian / Chinese / Mexican / Middle Eastern pairing logics are first-class with equivalent depth of treatment.

### 2. Tier 1 inventory — institutional / canonical food science

#### Books (per source: description / scientific-grounding strength / NutriMe value)

- **Harold McGee — *On Food and Cooking* (Scribner, rev. ed. 2004 [verify])** — Canonical chemistry-of-cooking reference, ingredient-by-ingredient + technique-by-technique. **Grounding: very strong** — McGee threads primary-literature citations through; the bibliography is itself a research map. **NutriMe value: foundational** — most pairing-mechanism claims can be backed here as a first-pass authority and then cross-walked to primary literature.
- **J. Kenji López-Alt — *The Food Lab* (Norton, 2015 [verify])** — Test-kitchen-driven food-science book; A/B testing of techniques. **Grounding: strong on technique, moderate on chemistry** — López-Alt cites McGee + primary sources but focuses on empirical kitchen-testing. **NutriMe value: high for technique-pairing logic** (sear-then-roast, fond + deglazing, salt-timing).
- **Hervé This — *Molecular Gastronomy* (Columbia UP, 2006 [verify]); *Building a Meal* (2009 [verify]); *Note-by-Note Cooking* (2014 [verify])** — Founding theorist of molecular gastronomy. **Grounding: high** — This is himself a peer-reviewed researcher (INRAE); bibliography is academic. **NutriMe value: theoretical scaffold** — taxonomies of culinary transformations, "complex disperse systems" framing for foams / gels / emulsions.
- **Nathan Myhrvold et al. — *Modernist Cuisine* (5 vol. + kitchen manual, 2011 [verify]); *MC at Home* (2012); *Modernist Bread* (2017); *Modernist Pizza* (2021)** — Encyclopedic technique + science compendium with original measurements. **Grounding: very strong** — original lab work + extensive primary citation. **NutriMe value: exceptional reference for technique-mechanism + ingredient-interaction at depth.**
- **Shirley Corriher — *CookWise* (1997); *BakeWise* (2008)** — Biochemist-trained writer, problem/solution format ("what went wrong, why, how to fix"). **Grounding: strong on chemistry, light on primary citation.** **NutriMe value: practitioner-friendly mechanism explanations** — bridges Tier 1 chemistry to kitchen action.
- **Peter Barham — *The Science of Cooking* (Springer, 2001 [verify])** — Physicist's treatment, especially strong on heat transfer + emulsions. **Grounding: high.** **NutriMe value: precise physical-chemistry framing for cooking transformations.**
- **Alan Davidson — *The Oxford Companion to Food* (OUP, 2nd ed. 2006 [verify], ed. Tom Jaine)** — Reference-grade encyclopedia; ingredient + dish entries with historical + cultural context. **Grounding: scholarly-historical, less mechanistic.** **NutriMe value: authoritative ingredient-identity + cultural-context entries** — counters Western-default by including global ingredients.
- **Ian Hornsey — *A History of Beer and Brewing* (RSC, 2003 [verify]); *Alcohol and its Role in the Evolution of Human Society* (RSC, 2012 [verify])** — Royal Society of Chemistry imprint; rigorous fermentation chemistry + history. **Grounding: very strong.** **NutriMe value: fermentation-as-flavor-source authoritative reference.**
- **Sandor Katz — *The Art of Fermentation* (Chelsea Green, 2012); *Fermentation Journeys* (2021)** — Practitioner-scholar; *Art of Fermentation* won James Beard Award. **Grounding: practitioner-rigorous, lighter on primary citation than Hornsey.** **NutriMe value: cross-cultural fermentation pairing-logic** (kimchi, miso, garum, lacto-ferments, tepache); strong geographic-neutrality positioning.
- **Andoni Luis Aduriz — *Mugaritz: A Natural Science of Cooking* (Phaidon, 2012 [verify]); Ferran Adrià — *elBulli* compendia (2003–2011)** — Avant-garde technique compendia. **Grounding: practitioner; technique-documented.** **NutriMe value: pushes pairing logic beyond conventional Western-tradition into deconstructed / contrasting-element pairings**, useful as evidence for the "contrasting-compound" side of the controversy.
- **Heston Blumenthal — *The Big Fat Duck Cookbook* (Bloomsbury, 2008 [verify]); *In Search of Perfection* (Bloomsbury, 2006 [verify])** — Chef-as-scientist collaboration with Hervé This + others. **Grounding: hybrid practitioner + academic collaboration.** **NutriMe value: documented pairings derived from compound-overlap reasoning** (white chocolate + caviar is the canonical example), useful as the high-profile case for the aroma-overlap hypothesis.
- **Robert Wolke — *What Einstein Told His Cook* (Norton, 2002); *Vol. 2* (2005)** — Chemistry professor writing for general audiences. **Grounding: rigorous, well-sourced for popular-science.** **NutriMe value: clear-prose mechanism explanations** that map well to user-facing audit-as-education content.

#### Peer-reviewed journals (Tier 1 floor)

| Journal | Publisher | Scope for sweep #14 |
|---|---|---|
| *Journal of Agricultural and Food Chemistry* (*JAFC*) | ACS | Volatile compounds, Maillard chemistry, primary food-chemistry results |
| *Food Chemistry* | Elsevier | Ingredient composition, flavor chemistry, processing effects |
| *International Journal of Gastronomy and Food Science* (*IJGFS*) | Elsevier | Bridge between chef research + academic food-science; pairing studies appear here |
| *Journal of Sensory Studies* | Wiley | Sensory methodology, descriptive analysis |
| *Food Quality and Preference* | Elsevier | Hedonic / consumer studies, cross-cultural sensory |
| *Chemical Senses* | OUP | Olfaction + gustation receptor science (TRPV1, T1R, T2R) |
| *Flavour and Fragrance Journal* | Wiley | Aroma compound identification + analysis |
| *Journal of Food Science* | IFT / Wiley | Broad food-science incl. processing + composition |

These are the peer-reviewed floor for any **mechanistic claim** about pairing in NutriMe (per Rule 7).

#### Institutional white literature

- **Monell Chemical Senses Center** (Philadelphia) — leading independent research center on taste + smell; publishes in *Chemical Senses* + *Nature Comms* + *PNAS*. White-literature outputs include educational materials + symposium proceedings.
- **Pangborn Sensory Science Symposium** (biennial, Elsevier-affiliated) — proceedings are a primary venue for cross-cultural sensory + flavor-pairing research.
- **Institute of Food Technologists (IFT)** — *Food Technology* magazine + *Journal of Food Science* + *Comprehensive Reviews in Food Science and Food Safety*; institutional position papers on flavor + processing.

### 3. Tier 2 inventory — practitioner-codified pairing knowledge

#### Books (per source: description / pairing-knowledge style / cultural focus / scientific cross-reference strength)

- **Karen Page + Andrew Dornenburg — *The Flavor Bible* (Little, Brown, 2008); *The Vegetarian Flavor Bible* (2014)** — Lookup-table format: ingredient → "matches well with" lists curated from interviews with named chefs. Style: chef-aggregated practitioner consensus. Cultural focus: Western-restaurant-chef-dominant; some global. Cross-reference strength: **low** — no primary citations; chef attribution only. Treat as Tier 4 informational unless cross-walked.
- **Niki Segnit — *The Flavor Thesaurus* (Bloomsbury, 2010); *Lateral Cooking* (2018)** — Pairwise-pairing essays organized by flavor family. Style: literary-tasting-notes + recipe miniatures. Cultural focus: Western with selective global. Cross-reference strength: **low**, but Segnit cites McGee + Davidson + others; better-sourced than Flavor Bible.
- **James Briscione + Brooke Parkhurst — *The Flavor Matrix* (Houghton Mifflin, 2018)** — Data-driven pairings using IBM/ICE collaboration on aroma-compound databases. Style: explicitly compound-overlap-derived. Cultural focus: Western-default but with global ingredients. Cross-reference strength: **moderate** — references compound databases, but the underlying hypothesis (Ahn et al.) is contested; should be surfaced with the controversy framing.
- **Sharon Tyler Herbst (ed. James Peterson revisions) — *The Food Lover's Companion* (Barron's, multiple eds.)** — Encyclopedia of culinary terms + ingredients. Style: dictionary-reference. Cross-reference strength: low; reference-grade for ingredient identity.
- **Larousse Gastronomique (Hamlyn ed., Eng. translation; current Eng. ed. 2009 [verify])** — Reference-grade French + global encyclopedia. Style: encyclopedia. Cultural focus: French-canon-anchored, global coverage. Cross-reference strength: low for science, high for tradition-citation.
- **CIA — *The Professional Chef* (Wiley, 9th ed. 2011 [verify])** — Culinary academy textbook. Style: pedagogical, with technique-based pairing logic. Cultural focus: Western-Continental-anchored, global appendices. Cross-reference strength: low for primary literature; high institutional credibility.
- **Sarah Labensky + Alan Hause — *On Cooking* (Pearson, 6th ed. [verify])** — Culinary pedagogy textbook. Similar profile to CIA's *Professional Chef*. Cultural focus: Western foundations, expanding global coverage in recent editions.
- **Irma Rombauer / Marion Rombauer Becker / Ethan Becker — *Joy of Cooking* (Scribner, 2019 ed. [verify])** — American home-cooking reference; technique sections are pedagogically substantive. Cultural focus: American + Western European inheritance + selective global.
- **Samin Nosrat — *Salt, Fat, Acid, Heat* (Simon & Schuster, 2017)** — Pairing through four-element balance principles (each element is a chapter). Style: principles-first, recipe-illustrated. Cultural focus: deliberately cross-cultural, flagging origins. Cross-reference strength: low for primary literature; high pedagogical clarity. **NutriMe value: framework-friendly principle structure** maps cleanly onto an audit-as-education format.
- **Diana Kennedy — *The Art of Mexican Cooking* (Bantam, 1989 [verify]); *The Cuisines of Mexico* (Harper, 1972 [verify])** — Authoritative regional Mexican reference; chile + masa + mole pairing logic. Cultural focus: regional Mexican (Oaxaca, Puebla, Yucatán). Cross-reference strength: low for science; very high for cultural-tradition authority.
- **Madhur Jaffrey — *An Invitation to Indian Cooking* (Knopf, 1973); *World Vegetarian* (Clarkson Potter, 1999)** — Foundational English-language Indian reference; regional masala + tadka logic. Cultural focus: pan-Indian with regional differentiation. Cross-reference strength: low for science; high for tradition.
- **Fuchsia Dunlop — *Land of Plenty* (Norton, 2003); *Every Grain of Rice* (Norton, 2012); *The Food of Sichuan* (Norton, 2019)** — Authoritative English-language Sichuan + regional Chinese reference. Cultural focus: regional Chinese, especially Sichuan. Cross-reference strength: low for science; very high for tradition + her Sichuan-Cuisine-Institute training adds institutional credibility.
- **Maangchi (Emily Kim) — *Maangchi's Real Korean Cooking* (Houghton Mifflin, 2015); *Maangchi's Big Book of Korean Cooking* (2019)** — Most-followed English-language Korean home-cooking reference. Cultural focus: Korean home + traditional. Cross-reference strength: low for science; high for cultural authority + accessibility.
- **Yotam Ottolenghi (with Sami Tamimi / Helen Goh / Ramael Scully) — *Plenty* (2010); *Jerusalem* (2012); *Simple* (2018); *Flavor* (2020)** — Mediterranean / Levantine pairing pedagogy with strong vegetable-forward emphasis. Cultural focus: Levantine + Mediterranean, deliberately cross-tradition. Cross-reference strength: low for science; very high for pairing-pedagogy clarity.
- **Claudia Roden — *The New Book of Middle Eastern Food* (Knopf, 2000); *The Book of Jewish Food* (Knopf, 1996)** — Scholarly-cookbook hybrid; foundational reference for Middle Eastern + North African + Sephardic. Cultural focus: pan-Middle Eastern + diaspora. Cross-reference strength: low for food-science, high for ethnographic authority.
- **Paula Wolfert — *The Cooking of the Eastern Mediterranean* (HarperCollins, 1994); *The Food of Morocco* (Ecco, 2011); *Mediterranean Clay Pot Cooking* (2009)** — Deep regional fieldwork. Cultural focus: Eastern Mediterranean + North African. Cross-reference strength: low for science; field-research-grade ethnographic authority.
- **Cheryl Sternman Rule — *Ripe* (2012); *Yogurt Culture* (2015)** — Pairing-focused works around single ingredients (produce, yogurt). Cultural focus: cross-cultural with explicit attribution.

#### Institutional culinary academy curricula on flavor pairing

Per [sweep #12 institutional list](../12-skills-by-cuisine/scope.md), the same institutions cross-reference here for pairing curriculum (where curriculum documents are accessible):

- **Le Cordon Bleu** — Western-classical pairing pedagogy; sauce-pairing tradition.
- **CIA** — *Professional Chef* + flavor-pairing electives; recently the *Flavor Course* (Briscione lineage).
- **Tsuji Culinary Institute (Osaka)** — Japanese flavor-pairing pedagogy (umami / dashi-centric).
- **Ferrandi (Paris)** — French-classical with contemporary additions.
- **ALMA (Parma)** — Italian regional pairing.
- **Hattori Nutrition College (Tokyo)** — nutrition + Japanese flavor pedagogy.
- **IHM India (Pusa, Mumbai, et al.)** — Indian regional masala pedagogy.
- **China Culinary Academy / regional cuisine institutes** — Chinese five-flavor + regional pairing.
- **Korean Food Foundation** — government-affiliated; Korean flavor pedagogy.
- **ICUM (Mexico)** — Mexican regional pairing pedagogy.

These are operational-tradition Tier supplementary basis (per [evidence-tiers.md](../00-meta/evidence-tiers.md#operational-tradition-as-supplementary-basis)) — institutional accountability, but typically not peer-reviewed.

### 4. Tier 3 — ingredient databases

- **FlavorDB** (Indian Institute of Science, Bangalore; Garg et al. 2018 *Nucleic Acids Research*) — Academic database mapping ~25,000 flavor molecules across ~900+ ingredients [verify counts]. Coverage: cross-cultural ingredients including Indian + Asian. License: academic / open for research; check current ToS. Access: web interface + downloadable data tables. **NutriMe value: cleanest academic substrate for compound-overlap pairing analysis**; pairs with Ahn et al. methodology; reproducible.
- **FoodPairing.com** (Sense for Taste / Bernard Lahousse, Belgium) — Commercial database based on aroma-compound-overlap hypothesis; commercial-API access; some content public, deeper API paid. Coverage: large but Western-skewed. License: commercial (ToS-restricted). Access: web UI + commercial API. **NutriMe value: useful as a comparator** but **must be flagged as commercial** + **based on a contested hypothesis**; not appropriate as primary corpus source.
- **Open Food Facts** (open collaborative; cross-references [sweep #2](../02-food-composition-databases/scope.md)) — Ingredient-level crowd-sourced database of packaged foods; ingredient-list parsing useful for substitution + composition. License: ODbL (Open Database License). Access: full data dumps + API. **NutriMe value: ingredient-identity authority for packaged-foods context**; cross-walked to USDA FoodData Central + other Tier 1 composition databases per sweep #2.

### 5. Tier 4 — informational / cultural / hypothesis-generating

- **Khymos** (Martin Lersch, Norwegian chemist; khymos.org) — Long-running food-science blog; well-sourced for a blog; archive includes the *Texture* PDF (free hydrocolloid reference) + technique experiments. **Use:** hypothesis-generating + practitioner-friendly chemistry framing. **Floor:** Tier 4 — cite for explanatory framing only; back substantive claims to Tier 1.
- **Serious Eats food-science articles** (Kenji López-Alt + Stella Parks + Daniel Gritzer + others) — Test-kitchen science journalism; well-sourced. **Use:** technique + pairing explanations cross-walked to McGee / primary literature; cross-references [sweep #11](../11-recipe-sourcing/scope.md). **Floor:** Tier 4 informational.
- **Cultural cookbook tradition** — region-specific cookbooks beyond the Tier 2 named list (community cookbooks, family cookbooks, chef memoirs) — valuable for **ingredient-pairing tradition** as cultural-historical fact. **Use:** cultural-historical surfacing only; no health claims; no scientific-mechanism claims without Tier 1/2/3 cross-walk.

### 6. The flavor-pairing controversy

**The hypothesis (Ahn et al. 2011 [verify]):** Yong-Yeol Ahn, Sebastian Ahnert, James Bagrow, Albert-László Barabási. *Flavor network and the principles of food pairing.* **Scientific Reports**, 1, 196 [verify volume / article number]. https://doi.org/10.1038/srep00196 [verify DOI]. Built a bipartite network of ingredients ↔ flavor compounds (drawing on Fenaroli's *Handbook of Flavor Ingredients* + similar databases) and analyzed shared-compound counts in real-world recipe corpora (Allrecipes + Epicurious + a Korean source [verify]).

**Headline finding:** **Western cuisines** (especially North American + Western European) tend to combine ingredients that **share more flavor compounds than expected by chance**; **East Asian cuisines** (especially Korean) tend to combine ingredients that **share fewer flavor compounds than chance** — a *contrasting-compound* tendency. Southern European + Latin American sat somewhere between but leaning Western in their analysis.

**Why this matters as a controversy:**

- The hypothesis was **adopted commercially** (FoodPairing.com, IBM Chef Watson, *The Flavor Matrix*) and presented in some popular venues as a **universal pairing principle**.
- It is **not a universal principle**; the Ahn et al. paper itself documents the East Asian counter-pattern.
- **Critiques in subsequent literature [verify specific authors]:** Recipe corpora are themselves Western-overrepresented (Allrecipes / Epicurious bias); aroma-compound databases are Western-volatile-skewed; "shared compound count" is a coarse metric (presence/absence not concentration); pairwise compound overlap is a weak proxy for human perception of pairing quality (which is multimodal — taste + texture + temperature + mouthfeel + cultural learning).
- **Where the field stands:** the compound-overlap hypothesis is **one signal among many**, useful for hypothesis generation but not a normative pairing rule. Sensory-science research consistently finds that **perception of pairing quality is multimodal + culturally learned**, not reducible to compound overlap. The contrasting-compound traditions of East / South / Southeast Asia are not aberrations; they are coherent alternative pairing logics.

**Implications for NutriMe:**

- Per **Rule 9 (geographic neutrality)**, both compound-overlap and contrasting-compound pairing logics are equal-weighted in the corpus.
- Per **audit-as-education**, when surfacing a pairing recommendation derived from compound-overlap reasoning, the system **declares the basis** ("compound-overlap analysis suggests...") rather than presenting it as universal.
- Per **Rule 7**, mechanistic pairing claims require Tier 1/2 backing; "Ahn et al. 2011 + critiques" is Tier 2 evidence with **explicit declaration of the universality limitation**.
- The corpus should index pairings by **multiple frameworks** — compound-overlap, contrasting-aromatic, balance-principle (Nosrat: salt/fat/acid/heat), flavor-element balance (Chinese five-flavor), umami-synergy, masala-construction — not commit to a single pairing theory.

### 7. Geographic + cuisine pairing-tradition coverage

For each tradition: foundational principle + canonical reference + distinctive logic.

#### Western (continental European + Anglo-American)

- **Foundational principle:** sauce-and-protein pairing tradition (Escoffier mother-sauces); regional ingredient-affinity (tomato + basil + olive oil; butter + cream + flour; mirepoix base).
- **Canonical references:** Escoffier *Le Guide Culinaire* (1903); *Larousse Gastronomique*; CIA *Professional Chef*; McGee.
- **Distinctive logic:** Compound-overlap tendency (per Ahn et al.); fat-vehicle for flavor; sauce-as-flavor-bridge; cooking technique often determines pairing (braise-pairings differ from roast-pairings).

#### Japanese (umami + dashi)

- **Foundational principle:** umami (Kikunae Ikeda, 1908 [verify]) as fifth taste; dashi (kombu + katsuobushi or shiitake) as foundational flavor base; *kasaneru* (layering) + restraint.
- **Canonical references:** Shizuo Tsuji *Japanese Cooking: A Simple Art* (1980); Nobuo Murata; *Washoku* (Elizabeth Andoh, 2005); Tsuji Culinary Institute pedagogy.
- **Distinctive logic:** **Umami synergy** — glutamate (kombu) + 5'-inosinate (katsuobushi) + 5'-guanylate (shiitake) — multiplicative not additive umami perception (Yamaguchi 1967 / 1979 [verify]). This is **peer-reviewed primary-literature pairing science**, distinct from practitioner-tradition. Restraint + ingredient-honoring; seasonality (*shun*).

#### Korean (gochugaru + jang base)

- **Foundational principle:** gochugaru + garlic + ginger + sesame + scallion as a recurrent base; the *jang* trio (doenjang, gochujang, ganjang) as fermented-flavor foundation; *banchan* as multi-dish balance.
- **Canonical references:** Maangchi works; Cecilia Hae-Jin Lee *Eating Korean*; Hooni Kim *My Korea*; Korean Food Foundation publications.
- **Distinctive logic:** Strong **contrasting-compound** tendency (per Ahn et al. headline finding); fermentation-derived umami + funk; balance across dishes rather than within a dish; medicinal-food (*yaksik*) tradition.

#### Chinese (five-flavor + regional)

- **Foundational principle:** five-flavor balance (sweet 甜 / sour 酸 / salty 咸 / bitter 苦 / spicy 辣 — note: spicy is colloquial 5th vs. classical 5th umami 鲜); cooling/warming TCM framing layered over pairing; regional differentiation (Sichuan: ma-la 麻辣; Cantonese: freshness + restraint; Shandong: vinegar; Hunan: dry-heat chili).
- **Canonical references:** Fuchsia Dunlop *Land of Plenty* + *Food of Sichuan*; Yan-Kit So *Classic Chinese Cookbook*; *Modern Art of Chinese Cooking* (Barbara Tropp, 1982 [verify]); China Culinary Academy.
- **Distinctive logic:** **ma-la** (Sichuan pepper-induced numbing + chili heat) is a multimodal pairing — TRPV1 (capsaicin) + a sanshool-driven oscillating-tactile sensation activating mechanoreceptors. This is **peer-reviewed pairing-pharmacology** (Hagura et al. 2013 *Proc R Soc B* [verify]). Five-flavor balance is **practitioner-tradition Tier 4** unless cross-walked.

#### Indian (masala construction + regional)

- **Foundational principle:** masala = layered spice combination, regionally + dish-specifically constructed; *tadka* / *chhaunk* / *baghar* (oil-tempered spice bloom) as flavor-extraction technique that **chemically extracts fat-soluble flavor compounds** before adding to dish.
- **Canonical references:** Madhur Jaffrey works; K.T. Achaya *Indian Food: A Historical Companion*; *Prashad* (J. Inder Singh Kalra); IHM curricula; Pushpesh Pant *India Cookbook* (Phaidon).
- **Distinctive logic:** Regional masala + tempering varies dramatically (North: garam masala-heavy + dairy fat; South: mustard + curry leaf + coconut + tamarind; East: panch phoron; West: kokum + jaggery; Northeast: bamboo-shoot + fermented). Tempering is **technique-mediated pairing** — the same spice in raw vs. tempered form behaves differently. **Cross-references [sweep #12 technique knowledge].**

#### Middle Eastern + North African

- **Foundational principle:** aromatic blends (za'atar, ras el hanout, dukkah, baharat, advieh) + sour-fruit + nut + herb pairing; preserved-lemon + olive + dried-fruit + spice; sumac as souring agent distinct from citrus.
- **Canonical references:** Claudia Roden; Paula Wolfert; Yotam Ottolenghi + Sami Tamimi; Anissa Helou *Feast*; Greg Malouf works.
- **Distinctive logic:** Sourness from non-citrus sources (sumac, pomegranate molasses, verjuice, tamarind) — gives different acid profile than vinegar / lemon. **Sweet-savory integration** (lamb + apricot, chicken + prune) is canonical. Spice blends are regionally + family-specific (no universal ras el hanout formula).

#### Latin American (sofrito + regional)

- **Foundational principle:** sofrito family — onion + garlic + (regionally) bell pepper / culantro / tomato / aji — as universal aromatic base, varying by country (Spanish vs. Puerto Rican vs. Cuban vs. Dominican vs. Brazilian *refogado*).
- **Canonical references:** Maricel Presilla *Gran Cocina Latina*; Daisy Martinez; Dora Stone; Sandra Gutierrez *The New Southern-Latino Table*.
- **Distinctive logic:** Aromatic-base + slow-cook pairing (similar logic to mirepoix but warmer-spectrum); extensive use of **acid + chile + herb** as finishing-pairing layer (chimichurri, salsa criolla, mojo).

#### Mexican specifically

- **Foundational principle:** chile-by-chile pairing science (each chile — ancho, guajillo, pasilla, mulato, chipotle, morita, árbol, habanero, poblano, serrano, jalapeño — has distinctive flavor + heat + smokiness profile and pairs differently); mole as canonical case study (20+ ingredient pairings); masa + lime-cooked corn (nixtamalization) as base; chocolate + chile + spice integration.
- **Canonical references:** Diana Kennedy works; Rick Bayless *Authentic Mexican* + *Mexico One Plate at a Time*; Patricia Quintana; Enrique Olvera *Mexico from the Inside Out*; ICUM.
- **Distinctive logic:** **Mole as case study in non-overlap pairing** — combines 20+ ingredients (nuts, seeds, chiles, chocolate, spices, fruit) with deliberate flavor-element balance, not compound overlap. Chile-pairing is its own deep tradition; chiles vary in capsaicinoid profile + non-pungent flavor compounds + smoke (chipotle = smoked jalapeño). Nixtamalization (alkaline-cooked corn) creates pairing opportunities (improved protein, aroma compounds, niacin bioavailability) — this is **Tier 1 peer-reviewed nutrition + chemistry**.

### 8. Scientific basis section — peer-reviewed food-science basis for pairings

- **Maillard reaction chemistry** — non-enzymatic browning between reducing sugars + amino acids; produces hundreds of aroma compounds (pyrazines, furanones, thiophenes) [Tier 1: McGee + *JAFC* literature]. Pairing implication: roasted / seared / browned ingredients pair via shared Maillard-volatile chemistry (roasted nuts + roasted meat + coffee + chocolate share pyrazine families). Mechanism is well-characterized and reproducible.
- **Volatile-compound profiles** — gas chromatography-mass spectrometry (GC-MS) characterization of ingredient aroma profiles is the substrate for compound-overlap pairing analysis. Major databases: *Fenaroli's Handbook of Flavor Ingredients*; FlavorDB; VCF (Volatile Compounds in Food). [Tier 1.] Limitation: **presence ≠ perceptual relevance** — odor-activity values (concentration ÷ threshold) matter more than count.
- **Capsaicin + TRPV1 + cooling pairings** — capsaicin (and capsaicinoids) activate TRPV1 (transient receptor potential vanilloid 1) on trigeminal nerves; perceived as heat / burn. **Cooling pairings** — dairy (casein binds capsaicin), starch (mechanical buffering), sugar, fat in general — reduce burn perception. [Tier 1: Caterina et al. 1997 *Nature* on TRPV1 cloning; Julius lab subsequent work; Nobel Prize 2021 to Julius + Patapoutian for TRPV1 + Piezo.] Cross-cultural pairing logic (yogurt with Indian curry, sour cream with Mexican spicy, milk + spicy snacks) is **mechanistically grounded peer-reviewed science**.
- **Umami synergy (glutamate + 5'-nucleotides)** — monosodium glutamate + inosinate (IMP) or guanylate (GMP) produce **synergistic** (multiplicative, not additive) umami perception. [Tier 1: Yamaguchi 1967 + 1979 [verify]; subsequent T1R1/T1R3 receptor work — Nelson et al. 2002 *Nature*, Li et al. 2002 *PNAS*.] This is the **mechanistic basis for** dashi (kombu + katsuobushi), ragù bolognese (tomato + meat + parmesan), French onion soup (onion + beef stock + cheese), and many cross-cultural "depth" combinations.
- **Acid-base balance** — acid (citric, acetic, lactic, malic, tartaric) brightens fat-rich + protein-rich + starch-heavy dishes by stimulating salivation + cutting fat perception + balancing sweetness. Mechanism: acid reduces perceived bitterness + sweetness intensity; activates trigeminal acid sensors. [Tier 1 sensory + pharmacology.] Sources of acid have **different secondary flavors** (lemon = limonene; vinegar = ethanoate + congeners; tamarind = tartaric + sugar-volatile complex; sumac = malic + tannins).
- **Texture + mouthfeel pairings (tannins + protein)** — tannins (in red wine, tea, persimmon, walnut) bind salivary proline-rich proteins → astringency. **Pairing implication:** protein-rich foods (red meat, hard cheese) **bind tannins**, reducing astringency and giving the wine-pairing tradition its biochemical basis. [Tier 1: Bate-Smith literature; Lesschaeve + Noble 2005 *AJCN* review on tannin perception.]
- **Fermentation chemistry** — lactic acid bacteria + yeast + mold (*Aspergillus oryzae* in koji; *Penicillium* in cheese; *Acetobacter* in vinegar) produce: lactic acid (sourness + preservation), short-chain fatty acids (cheesy / funky aromas), esters (fruity aromas), proteolytic peptides (umami + meaty notes), free glutamate (umami amplification). [Tier 1: Hornsey RSC volumes; Katz cross-walked.] **Pairing implication:** fermented ingredients (miso, kimchi, fish sauce, sauerkraut, parmesan, prosciutto, sourdough) provide umami + acid + funk in a single addition; pair via umami-synergy logic.
- **Capsaicin / piperine / sanshool / allyl isothiocyanate (mustard / wasabi) — trigeminal pungency** — different "heat" sensations activate different receptors (TRPV1 vs. TRPA1 vs. mechanoreceptor oscillation for sanshool). [Tier 1: chemosensory literature.] **Pairing implication:** Sichuan ma-la (sanshool + capsaicin) is a multimodal pungency pairing; wasabi (TRPA1) + soy sauce + raw fish is a different multimodal logic; black pepper (piperine, weak TRPV1 + TRPA1) bridges Western + Indian + Southeast Asian traditions.

### 9. Cross-references for integration pass

#### Sweep #2 (food composition databases)

- Authority table from sweep #2 must accept ingredient-pairing-corpus IDs as a sibling identifier alongside USDA FDC IDs.
- FlavorDB ↔ USDA FDC ↔ Open Food Facts ingredient mapping is a cross-cut (sweep #2 + sweep #14 + sweep #13).
- Composition-data ingredient-name authority resolves variant names (e.g., "scallion" / "spring onion" / "green onion") for pairing-corpus indexing.

#### Sweep #11 (recipe sourcing)

- Recipe corpus pairings should be **annotated with pairing-tradition tags** (Western / Japanese-umami / Sichuan-ma-la / Indian-tadka / Levantine / etc.) drawn from sweep #14.
- Serious Eats food-science articles cross-reference both ways (sweep #11 recipe source + sweep #14 Tier 4 informational).
- Cultural cookbook tradition is a shared source class.

#### Sweep #12 (skills-by-cuisine)

- Technique knowledge ↔ pairing knowledge are deeply intertwined — *tadka* is technique that **enables** Indian pairings; sofrito is technique that **enables** Latin pairings; dashi-extraction is technique that **enables** Japanese umami-synergy pairings. Sweep #12 documents the technique; sweep #14 documents the pairing logic; the corpus links them.
- Institutional culinary academy list is **shared** between sweeps #12 and #14; the same institutions appear with overlapping authority.

#### Sweep #13 (grocery infrastructure)

- Substitution logic in sweep #13 must consume sweep #14 pairing knowledge: a substitute is acceptable if it preserves the **pairing role** (acid / umami / aromatic / pungent / textural / fat-vehicle) the original played.
- Audit-as-education for substitutions ("we suggested rice vinegar instead of mirin because both contribute mild acid + sweetness + fermentation-derived complexity") draws directly from sweep #14 pairing science.

### 10. Answers to open questions in the scope

1. **Strongest peer-reviewed evidence on aroma-compound-overlap vs. contrasting-compound traditions?** Ahn et al. 2011 (*Scientific Reports*) is the most-cited primary paper on the question and itself documents both patterns (Western shared-compound tendency, East Asian contrasting-compound tendency). The hypothesis as a **universal pairing rule** is **not supported**; it is supported as a **descriptive observation about Western recipe corpora**. Subsequent food-science consensus treats compound overlap as **one signal among many** (alongside multimodal sensory + cultural learning). The field has not produced a successor "universal pairing theory" because pairing perception is increasingly understood as inherently multimodal + culturally embedded.
2. **Per-tradition canonical references:** see Section 7 above. Each tradition has a clearly-identifiable English-language canonical reference + (where available) institutional academy reference + (where available) primary food-science backing for specific mechanisms (umami synergy = peer-reviewed; five-flavor balance = practitioner-tradition).
3. **Tier 1 sources with strongest peer-reviewed citations:** **McGee** + **Modernist Cuisine** + **Hervé This** + **Barham** + **Hornsey** are best peer-reviewed-cross-referenced. **Corriher** + **López-Alt** + **Wolke** are practitioner-rigorous but lighter on primary citation. **Blumenthal** + **Adrià** + **Aduriz** are technique-documentation-rigorous but pairing-theoretical claims are practitioner-derived.
4. **FlavorDB vs. FoodPairing.com:** FlavorDB is **academic** (Garg et al. 2018 *NAR*), reproducible, ToS-friendly; FoodPairing.com is **commercial**, derived from the same compound-overlap hypothesis but with proprietary curation + commercial API. **What's reproducible from FlavorDB:** the compound-ingredient bipartite network; pairing-prediction analyses (with the universality limitation above). FlavorDB is the **preferred academic substrate**; FoodPairing.com is a comparator only.
5. **Best non-Western primary references:** Indian — Madhur Jaffrey + K.T. Achaya + IHM curricula + INRAE / Wageningen Indian-cuisine sensory work. Chinese — Fuchsia Dunlop + Sichuan Cuisine Institute + China Culinary Academy + Hong Kong PolyU food-science. Japanese — Tsuji + Murata + Andoh + Tsuji Institute + Kikkoman R&D publications. Korean — Korean Food Foundation + Maangchi + Cecilia Hae-Jin Lee + Hooni Kim. Mexican — Diana Kennedy + Rick Bayless + Enrique Olvera + ICUM + UNAM food-research. Middle Eastern — Roden + Wolfert + Ottolenghi + Helou.
6. **Cooking transformations of pairings:** This is **under-researched** in food-science literature. Tomato + basil pairing-chemistry **does change** between raw + cooked applications — raw tomato is dominated by hexenal + cis-3-hexenol (green / grassy notes); cooked tomato gains Maillard + caramelization compounds + degrades some volatiles + concentrates others. Basil similarly loses fresh top-notes (linalool, eucalyptol) on cooking and gains more eugenol-dominant character. **Pairing implication:** raw tomato + basil is one pairing; cooked is another; both work but for different chemical reasons. **This is a publishable gap** — systematic per-pairing volatile-profile-by-cooking-state would be a contribution.

## References

- **Ahn, Y.-Y., Ahnert, S.E., Bagrow, J.P., & Barabási, A.-L.** (2011). Flavor network and the principles of food pairing. *Scientific Reports*, 1, 196 [verify volume / article number]. https://doi.org/10.1038/srep00196 [verify DOI]. Accessed 2026-05-01.
- **McGee, H.** (2004). *On Food and Cooking: The Science and Lore of the Kitchen* (rev. ed.) [verify edition year]. Scribner. Accessed 2026-05-01.
- **López-Alt, J.K.** (2015). *The Food Lab: Better Home Cooking Through Science* [verify year]. W.W. Norton. Accessed 2026-05-01.
- **This, H.** (2006). *Molecular Gastronomy: Exploring the Science of Flavor*. Columbia University Press. Accessed 2026-05-01.
- **This, H.** (2009). *Building a Meal: From Molecular Gastronomy to Culinary Constructivism*. Columbia University Press. Accessed 2026-05-01.
- **This, H.** (2014). *Note-by-Note Cooking: The Future of Food*. Columbia University Press. Accessed 2026-05-01.
- **Myhrvold, N., Young, C., & Bilet, M.** (2011). *Modernist Cuisine: The Art and Science of Cooking* (5 vol. + kitchen manual) [verify volume count]. The Cooking Lab. Accessed 2026-05-01.
- **Myhrvold, N., & Migoya, F.** (2017). *Modernist Bread*. The Cooking Lab. Accessed 2026-05-01.
- **Myhrvold, N., & Migoya, F.** (2021). *Modernist Pizza*. The Cooking Lab. Accessed 2026-05-01.
- **Corriher, S.** (1997). *CookWise: The Hows and Whys of Successful Cooking*. William Morrow. Accessed 2026-05-01.
- **Corriher, S.** (2008). *BakeWise: The Hows and Whys of Successful Baking*. Scribner. Accessed 2026-05-01.
- **Barham, P.** (2001). *The Science of Cooking* [verify year]. Springer. Accessed 2026-05-01.
- **Davidson, A. (Jaine, T., ed.)** (2006). *The Oxford Companion to Food* (2nd ed.) [verify year]. Oxford University Press. Accessed 2026-05-01.
- **Hornsey, I.S.** (2003). *A History of Beer and Brewing* [verify year]. Royal Society of Chemistry. Accessed 2026-05-01.
- **Hornsey, I.S.** (2012). *Alcohol and its Role in the Evolution of Human Society* [verify year]. Royal Society of Chemistry. Accessed 2026-05-01.
- **Katz, S.E.** (2012). *The Art of Fermentation*. Chelsea Green. Accessed 2026-05-01.
- **Katz, S.E.** (2021). *Fermentation Journeys*. Chelsea Green. Accessed 2026-05-01.
- **Aduriz, A.L.** (2012). *Mugaritz: A Natural Science of Cooking* [verify year]. Phaidon. Accessed 2026-05-01.
- **Adrià, F., Soler, J., & Adrià, A.** (2008). *A Day at elBulli*. Phaidon [verify edition / year]. Accessed 2026-05-01.
- **Blumenthal, H.** (2008). *The Big Fat Duck Cookbook* [verify year]. Bloomsbury. Accessed 2026-05-01.
- **Blumenthal, H.** (2006). *In Search of Perfection* [verify year]. Bloomsbury. Accessed 2026-05-01.
- **Wolke, R.L.** (2002). *What Einstein Told His Cook: Kitchen Science Explained*. W.W. Norton. Accessed 2026-05-01.
- **Page, K., & Dornenburg, A.** (2008). *The Flavor Bible*. Little, Brown. Accessed 2026-05-01.
- **Page, K.** (2014). *The Vegetarian Flavor Bible*. Little, Brown. Accessed 2026-05-01.
- **Segnit, N.** (2010). *The Flavor Thesaurus*. Bloomsbury. Accessed 2026-05-01.
- **Segnit, N.** (2018). *Lateral Cooking*. Bloomsbury. Accessed 2026-05-01.
- **Briscione, J., & Parkhurst, B.** (2018). *The Flavor Matrix: The Art and Science of Pairing Common Ingredients to Create Extraordinary Dishes*. Houghton Mifflin Harcourt. Accessed 2026-05-01.
- **Herbst, S.T. (Peterson, J., rev.)** (multiple eds.). *The Food Lover's Companion*. Barron's. Accessed 2026-05-01.
- **Hamlyn (ed.)** (2009). *Larousse Gastronomique* (Eng. ed.) [verify year]. Hamlyn. Accessed 2026-05-01.
- **The Culinary Institute of America** (2011). *The Professional Chef* (9th ed.) [verify edition]. Wiley. Accessed 2026-05-01.
- **Labensky, S.R., & Hause, A.M.** (multiple eds.). *On Cooking: A Textbook of Culinary Fundamentals*. Pearson. Accessed 2026-05-01.
- **Rombauer, I.S., Becker, M.R., & Becker, E.** (2019). *Joy of Cooking* [verify year]. Scribner. Accessed 2026-05-01.
- **Nosrat, S.** (2017). *Salt, Fat, Acid, Heat: Mastering the Elements of Good Cooking*. Simon & Schuster. Accessed 2026-05-01.
- **Kennedy, D.** (1989). *The Art of Mexican Cooking* [verify year]. Bantam. Accessed 2026-05-01.
- **Kennedy, D.** (1972). *The Cuisines of Mexico* [verify year]. Harper & Row. Accessed 2026-05-01.
- **Jaffrey, M.** (1973). *An Invitation to Indian Cooking*. Knopf. Accessed 2026-05-01.
- **Jaffrey, M.** (1999). *World Vegetarian*. Clarkson Potter. Accessed 2026-05-01.
- **Dunlop, F.** (2003). *Land of Plenty: A Treasury of Authentic Sichuan Cooking*. W.W. Norton. Accessed 2026-05-01.
- **Dunlop, F.** (2012). *Every Grain of Rice: Simple Chinese Home Cooking*. W.W. Norton. Accessed 2026-05-01.
- **Dunlop, F.** (2019). *The Food of Sichuan*. W.W. Norton. Accessed 2026-05-01.
- **Kim, E. (Maangchi)** (2015). *Maangchi's Real Korean Cooking*. Houghton Mifflin Harcourt. Accessed 2026-05-01.
- **Kim, E. (Maangchi)** (2019). *Maangchi's Big Book of Korean Cooking*. Houghton Mifflin Harcourt. Accessed 2026-05-01.
- **Ottolenghi, Y.** (2010). *Plenty*. Chronicle Books. Accessed 2026-05-01.
- **Ottolenghi, Y., & Tamimi, S.** (2012). *Jerusalem*. Ten Speed Press. Accessed 2026-05-01.
- **Ottolenghi, Y., & Goh, H. with Wigley, T., & Howarth, V.** (2018). *Ottolenghi Simple*. Ten Speed Press. Accessed 2026-05-01.
- **Ottolenghi, Y., Belfrage, I., & Wigley, T.** (2020). *Flavor*. Ten Speed Press. Accessed 2026-05-01.
- **Roden, C.** (2000). *The New Book of Middle Eastern Food*. Knopf. Accessed 2026-05-01.
- **Roden, C.** (1996). *The Book of Jewish Food*. Knopf. Accessed 2026-05-01.
- **Wolfert, P.** (1994). *The Cooking of the Eastern Mediterranean*. HarperCollins. Accessed 2026-05-01.
- **Wolfert, P.** (2011). *The Food of Morocco*. Ecco. Accessed 2026-05-01.
- **Wolfert, P.** (2009). *Mediterranean Clay Pot Cooking*. John Wiley & Sons. Accessed 2026-05-01.
- **Sternman Rule, C.** (2012). *Ripe: A Fresh, Colorful Approach to Fruits and Vegetables*. Running Press. Accessed 2026-05-01.
- **Sternman Rule, C.** (2015). *Yogurt Culture*. Houghton Mifflin Harcourt. Accessed 2026-05-01.
- **Tsuji, S.** (1980). *Japanese Cooking: A Simple Art*. Kodansha. Accessed 2026-05-01.
- **Andoh, E.** (2005). *Washoku: Recipes from the Japanese Home Kitchen*. Ten Speed Press. Accessed 2026-05-01.
- **Achaya, K.T.** (1994). *Indian Food: A Historical Companion* [verify year]. Oxford University Press. Accessed 2026-05-01.
- **Pant, P.** (2010). *India: The Cookbook* [verify year]. Phaidon. Accessed 2026-05-01.
- **Bayless, R., & Bayless, D.G.** (1987). *Authentic Mexican: Regional Cooking from the Heart of Mexico* [verify year]. William Morrow. Accessed 2026-05-01.
- **Olvera, E.** (2015). *Mexico from the Inside Out* [verify year]. Phaidon. Accessed 2026-05-01.
- **Presilla, M.E.** (2012). *Gran Cocina Latina: The Food of Latin America*. W.W. Norton. Accessed 2026-05-01.
- **Helou, A.** (2018). *Feast: Food of the Islamic World* [verify year]. Ecco. Accessed 2026-05-01.
- **Garg, N., Sethupathy, A., Tuwani, R., NK, R., Dokania, S., Iyer, A., Gupta, A., Agrawal, S., Singh, N., Shukla, S., Kathuria, K., Badhwar, R., Kanji, R., Jain, A., Kaur, A., Nagpal, R., & Bagler, G.** (2018). FlavorDB: a database of flavor molecules. *Nucleic Acids Research*, 46(D1), D1210–D1216 [verify exact citation]. https://doi.org/10.1093/nar/gkx957 [verify DOI]. Accessed 2026-05-01.
- **FoodPairing.com** (Sense for Taste / Lahousse, B.). Commercial flavor-pairing database. https://www.foodpairing.com [verify URL]. Accessed 2026-05-01.
- **Open Food Facts** (collaborative). Open ingredient-level packaged-food database. https://world.openfoodfacts.org. License: ODbL. Accessed 2026-05-01.
- **Lersch, M.** *Khymos* food science blog. https://blog.khymos.org [verify URL]. Accessed 2026-05-01.
- **Serious Eats** (Dotdash Meredith). Food-science articles archive. https://www.seriouseats.com. Accessed 2026-05-01.
- **Caterina, M.J., Schumacher, M.A., Tominaga, M., Rosen, T.A., Levine, J.D., & Julius, D.** (1997). The capsaicin receptor: a heat-activated ion channel in the pain pathway. *Nature*, 389(6653), 816–824. https://doi.org/10.1038/39807 [verify DOI]. Accessed 2026-05-01.
- **Yamaguchi, S.** (1967). The synergistic taste effect of monosodium glutamate and disodium 5'-inosinate. *Journal of Food Science*, 32(4), 473–478 [verify exact citation]. Accessed 2026-05-01.
- **Yamaguchi, S.** (1979). The umami taste. In *Food Taste Chemistry* (ACS Symposium Series 115) [verify]. American Chemical Society. Accessed 2026-05-01.
- **Nelson, G., Chandrashekar, J., Hoon, M.A., Feng, L., Zhao, G., Ryba, N.J.P., & Zuker, C.S.** (2002). An amino-acid taste receptor. *Nature*, 416(6877), 199–202 [verify]. https://doi.org/10.1038/nature726 [verify DOI]. Accessed 2026-05-01.
- **Li, X., Staszewski, L., Xu, H., Durick, K., Zoller, M., & Adler, E.** (2002). Human receptors for sweet and umami taste. *Proceedings of the National Academy of Sciences*, 99(7), 4692–4696 [verify]. Accessed 2026-05-01.
- **Hagura, N., Barber, H., & Haggard, P.** (2013). Food vibrations: Asian spice sets lips trembling. *Proceedings of the Royal Society B*, 280(1770), 20131680 [verify]. Accessed 2026-05-01.
- **Lesschaeve, I., & Noble, A.C.** (2005). Polyphenols: factors influencing their sensory properties and their effects on food and beverage preferences. *American Journal of Clinical Nutrition*, 81(1 Suppl), 330S–335S [verify]. Accessed 2026-05-01.
- **Monell Chemical Senses Center.** Institutional publications + research outputs. https://monell.org. Accessed 2026-05-01.
- **Pangborn Sensory Science Symposium.** Biennial proceedings (Elsevier-affiliated). Accessed 2026-05-01.
- **Institute of Food Technologists (IFT).** *Food Technology* magazine; *Journal of Food Science*; *Comprehensive Reviews in Food Science and Food Safety*. https://www.ift.org. Accessed 2026-05-01.

> Note: per task instructions, this sweep does **not** edit `00-meta/sources.md`. Consolidation into the master sources aggregator runs as a separate integration pass.
