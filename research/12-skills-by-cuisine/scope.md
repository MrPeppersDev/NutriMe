# Sweep #12 — Skills-by-Cuisine Mapping

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Build a research-grounded matrix mapping cooking skills to cuisine traditions worldwide. This sweep is the **engine that bridges cooking-confidence assessment ↔ recipe selection ↔ horizon-broadening**: it lets the system match recipes to user capability, identify "stretch" recipes that grow specific skills, and pace the iterative culinary expansion the product is designed around.

## Deliverable

An annotated reference map containing:

- **Skill taxonomy** built from a hybrid base (professional culinary curriculum spine + academic culinary research + bottom-up extraction from major dishes per cuisine)
- **Skill ↔ cuisine matrix** at medium granularity by default, with fine-granularity available where user competence grows
- **Skill progression paths** — A enables B+C, B+C enable D — needed for iterative horizon-broadening
- **Equipment ↔ skill bindings** — what hardware enables what skills
- **Cultural / regional / generational variation** in skills within a cuisine
- **Skill ↔ recipe linkage schema** — this sweep owns it; [sweep #11](../11-recipe-sourcing/scope.md) consumes it
- **"Where to learn" reference map** — map educational sources for skill acquisition at reference level (we map what's available, we don't deliver lessons per [product-framing "not a cooking class" boundary](../00-meta/product-framing.md#what-nutrime-is-explicitly-not))

This is a **reference map**, not corpus build.

## In scope

### Skill taxonomy basis (hybrid)

- **Professional culinary curriculum spine** — extract the core skill enumeration from CIA, Le Cordon Bleu, Tsuji, Ferrandi, ALMA, Hattori, IHM, China Culinary Academy curricula. Use as the structural backbone (acknowledging pro-kitchen bias).
- **Academic culinary research** — adapt for home-cooking-relevance using academic culinary studies, food science home-cooking research, behavioral cooking literature.
- **Bottom-up extraction** — iterate over major dishes per cuisine and extract required skills; aggregate to validate / extend the taxonomy.

### Granularity strategy

**Medium granularity by default.** Each major skill domain broken into 3–5 sub-skills:

- *Knife skills:* dicing, julienne, chiffonade, brunoise, supreming, deboning
- *Sauces:* pan sauces, mother sauces, emulsions, reductions, vinaigrettes
- *Dough:* mixing methods, kneading, lamination, proofing, shaping
- *Fermentation:* lactic-acid (kraut, kimchi), yeast (bread, beer), mold-driven (cheese, koji-adjacent), salt-cure
- *Heat-application:* sauté, braise, roast, sear, poach, blanch, steam, grill, smoke
- *Pressure / steam:* stovetop pressure, electric pressure, traditional steam (bamboo, dim sum)
- *Wok / high-heat stir-fry:* wok hei, parboil-stir-fry, dry-frying
- *Grilling / smoking:* direct, indirect, low-and-slow, charcoal-vs-gas-vs-wood
- *Doughs and batters by tradition:* European pastry, Asian dumpling skins, Indian flatbreads, Latin American masa
- *(further enumeration during research)*

**Fine granularity available** as user competence grows — system measures + recommends at finer resolution as it learns the user (parallel to iterative-intake horizon-broadening). E.g., a user proficient with sauces gets pressed on which mother sauces specifically, which emulsions, etc.

### Skill ↔ cuisine matrix

For each cuisine in [primary research scope](../00-meta/geographic-scope.md):
- Required entry-level skills (skills you must have to attempt entry-level dishes)
- Skills enabling intermediate-level dishes
- Skills enabling advanced / specialty dishes
- **Cultural / regional / generational variation** within the cuisine — Northern vs. Southern Italian, regional Indian (Punjabi vs. South Indian vs. Bengali), Chinese regional (Sichuan vs. Cantonese vs. Hunan), Korean (royal court vs. home banchan vs. street food), Japanese (kaiseki vs. izakaya vs. home washoku)
- Cross-cuisine skill transfer — French sauce skills transfer to Spanish, Italian; Japanese dashi skills transfer to Korean, Chinese; etc.

Methodology is **hybrid top-down + bottom-up**: top-down ("what does the literature say Cuisine X requires") + bottom-up ("iterate over major Cuisine X dishes, extract required skills, validate against top-down").

### Stretch recipe metadata for honest disclosure *(per [synthesis.md Tension #7](../00-meta/synthesis.md#tension-7--stretch-recipe-metadata-for-honest-disclosure-not-a-default-filter))*

Recipes carry **novelty count** (how many new skills relative to user's mastered set) and **failure cost** (deep-frying, fermentation, laminated doughs and other high-failure-cost techniques) as metadata. **This metadata drives honest disclosure, NOT system-default filtering** — the system does not pre-limit recipe surfaces by stretch level. When a recipe introduces multiple new skills or has high failure cost, the system *names* that fact so the user can pick with full context. See [intake-pattern.md stretch metadata section](../00-meta/intake-pattern.md#stretch-recipe-metadata-for-honest-disclosure-per-synthesismd-tension-7).

### Institutional culinary academy overlap with pairing knowledge *(per [sweep #14](../14-ingredient-interactions/scope.md) integration pass)*

The same institutional culinary academies cataloged in this sweep (Le Cordon Bleu, ALMA, Tsuji, Ferrandi, Hattori, IHM India, China Culinary Academy, Korean Food Foundation, ICUM) are the institutional sources for [sweep #14](../14-ingredient-interactions/scope.md)'s pairing knowledge as well — pairing pedagogy is part of their curricula. Cross-reference the institutional list rather than duplicating; the same source serves both technique-pedagogy (here) and pairing-pedagogy (sweep #14).

### Skill progression paths

Build dependency graph:
- Skill A enables skills B and C
- Skills B + C combined enable skill D
- D opens cuisine domain X

Example: Knife dicing + basic sauté + stock-making → braising → enables much of French peasant cuisine, Italian rustic, Chinese red-cooking. Add fermentation → opens Korean banchan, much of Eastern European preserved cuisine.

Used for:
- Iterative horizon-broadening pacing (system identifies the next skill to introduce based on current user competence + cuisine they want to explore)
- "Stretch recipe" identification (recipes that introduce one new skill within a base of mastered skills, vs. recipes that require multiple new skills at once)
- Cooking confidence growth tracking over time

### Equipment ↔ skill bindings

What hardware enables what skills (cross-references [sweep #7](../07-cooking-behavioral-barriers/scope.md) equipment-surfacing UX):

- Wok ↔ high-heat stir-fry, wok hei
- Pressure cooker (stovetop or electric) ↔ pressure-based cuisines (much of Indian, some Latin American, some Eastern European)
- Bamboo / metal steamer ↔ dim sum, mantou, idli/dhokla, dumpling steaming
- Tandoor (or convection-based home substitute) ↔ tandoor-style breads + meats
- Cast iron ↔ certain American Southern, certain European peasant
- Outdoor grill / smoker ↔ BBQ traditions, certain Korean, Brazilian churrasco
- Sous vide ↔ modern precision cooking (technique, not cuisine-bound)
- KitchenAid / stand mixer ↔ certain bread + pastry workflows
- Mortar and pestle / molcajete / suribachi ↔ many traditional cuisines (Thai, Mexican, Japanese)

### Cultural / regional / generational variation

Skills within a cuisine vary by region, era, and generation:

- Northern Italian (butter, dairy-rich, broader pasta variety) vs. Southern (olive oil, tomato-forward, simpler pasta)
- Regional Indian — Punjabi (tandoor-heavy, dairy-rich), South Indian (rice + fermented batters, coconut), Bengali (mustard oil, freshwater fish), Gujarati (vegetarian, sweet-savory balance)
- Regional Chinese — Sichuan (málà, pickling, dry-frying), Cantonese (steaming, freshness, dim sum), Hunan (smoked + spicy), Shanghai (red-cooking, sweetness), Northern wheat-based vs. Southern rice-based
- Korean — royal court (jeongol, gujeolpan), home banchan, street food (tteokbokki, gimbap, hotteok)
- Japanese — kaiseki precision, izakaya rustic, home washoku, regional ramen
- Generational — traditional skills (fermentation from scratch, butchery, full pastry from raw flour) vs. modern home cooking (semi-prepared component assembly)

System should respect this nuance, not flatten cuisines into single profiles.

### Skill ↔ recipe linkage schema

This sweep produces the schema fields that recipes (in [sweep #11](../11-recipe-sourcing/scope.md)) will populate:

- Required skills (list, with granularity tags)
- Skill prerequisites (dependency on prior skills)
- Stretch-skill markers (skills this recipe introduces, if any)
- Equipment requirements (cross-references equipment ↔ skill bindings)
- Cultural / regional context (which variant of the cuisine this recipe represents)
- Confidence-tier mapping (which user confidence level this recipe is appropriate for)
- Progression-graph position (where this recipe sits in the skill-growth path)

### "Where to learn" reference map (stretch-goal scope at reference level)

Per [product-framing](../00-meta/product-framing.md#what-nutrime-is-explicitly-not): NutriMe maps where a user can learn a missing skill, but does not deliver lessons. Map educational sources for skill acquisition:

- YouTube channels by skill domain (cross-references institutional + credentialed sources from [sweep #11](../11-recipe-sourcing/scope.md))
- Cooking school programs (online + in-person, by region)
- MasterClass / educational subscription platforms
- Skill-focused books (Kenji's *The Food Lab*, *On Cooking*, *The Professional Chef*, region-specific equivalents)
- In-person community classes (community college culinary, recreational cooking schools, cultural-center classes)

Map only — do not deliver, do not curate, do not partner. The system surfaces these as "if you want to learn this skill, here are the kinds of resources that exist."

### Geographic scope

Per [geographic-scope.md](../00-meta/geographic-scope.md), with **explicit attention to non-Western cuisine skill mapping** paralleling [sweep #11](../11-recipe-sourcing/scope.md)'s non-Western emphasis. The system's horizon-broadening promise depends on having credible skill mapping for cuisines beyond US/Western European.

## Out of scope (with reasons)

- **Cooking instruction delivery** — out per [product-framing "not a cooking class" boundary](../00-meta/product-framing.md#what-nutrime-is-explicitly-not). Mapping where to learn ≠ teaching.
- **Building actual skill assessment instruments** — covered in [sweep #3 (cooking confidence + cooking literacy screeners)](../03-clinical-nutrition-assessment/scope.md)
- **Recipe selection algorithms** — that's downstream system design; this sweep produces the substrate
- **Equipment vendor recommendations** — out (we surface what equipment a recipe needs, not where to buy it)

## Open questions for the research

- For the hybrid skill taxonomy: where do professional culinary curricula converge vs. diverge across CIA, Le Cordon Bleu, Tsuji, IHM, China Culinary Academy?
- For skill progression: what's the published evidence on how home cooks actually grow skills over time (vs. what professional curricula assume)?
- For non-Western cuisine skill mapping: what English-language / translated sources adequately characterize regional skill variation?
- For equipment ↔ skill: which equipment substitutions actually work (e.g., dutch oven as tandoor substitute, sheet pan as broiler-charring substitute)?
- For "where to learn" mapping: what's the realistic universe of skill-acquisition resources, and how do they get ranked / filtered by quality?
- For cultural variation: how much variation does the system surface to the user vs. abstract away?

## Cross-references

- Sister to [sweep #7 (cooking behavioral barriers)](../07-cooking-behavioral-barriers/scope.md) — confidence + equipment + skills bindings
- Feeds [sweep #11 (recipe sourcing)](../11-recipe-sourcing/scope.md) — skill metadata schema, skill ↔ recipe linkage
- Bound by [product-framing "not a cooking class" boundary](../00-meta/product-framing.md#what-nutrime-is-explicitly-not) — we map skills, we don't teach them
- Cross-references [sweep #3 (clinical nutrition assessment)](../03-clinical-nutrition-assessment/scope.md) — cooking confidence + cooking literacy intake screeners feed into the matrix
- Cross-references [intake-pattern.md](../00-meta/intake-pattern.md) — iterative horizon-broadening uses the skill progression graph
- Implements [framework-over-source-list principle](../00-meta/dynamic-research-expansion.md#framework-over-source-list--the-corpus-design-principle)
- See [geographic-scope.md](../00-meta/geographic-scope.md) for primary research scope with non-Western emphasis

## Findings

> **Epistemic note (2026-04-29).** This sweep was composed under a tool-access constraint: WebSearch and WebFetch were deferred and not invoked. Findings below are drawn from training-data knowledge of widely-published professional culinary curricula, canonical cooking-education texts, and well-documented regional culinary traditions. Where a claim depends on a specific page of a curriculum, the citation points to the program/text rather than a verified URL fetch; live verification is queued as a follow-up. All citations are marked accessed-on `2026-04-29` per [citation-style.md](../00-meta/citation-style.md), with the understanding that retrieval was indirect. No Tier 1/2/3 health claim is asserted in this sweep — it is a **skill-taxonomy reference map**, not a health-recommendation surface, so the [peer-reviewed floor (Rule 7)](../00-meta/constitutional-rules.md#rule-7--peer-reviewed-evidence-floor) is satisfied by treating professional culinary curricula as institutional authority for skill enumeration (a cultural/technical fact), not as evidence of health effect.

### 1. Skill taxonomy basis — hybrid justification

The skill taxonomy is built on three legs, each compensating for the others' bias:

**Leg 1 — Professional culinary curriculum spine.** The world's leading professional cooking schools have, over decades, converged on remarkably similar enumerations of foundational technique. Using this convergence as the structural backbone gives us:
- A vetted, peer-recognized vocabulary (chefs across institutions speak the same skill language)
- A defensible "what counts as a skill" boundary (vs. infinite recipe-specific atoms)
- Built-in progression structure (most curricula sequence skills explicitly across terms)

The pro-curriculum bias to acknowledge: these programs train people for restaurant kitchens, not home cooking. They overweight stations (garde-manger, saucier, pâtissier) and underweight equipment-constrained adaptation, semi-prepared component assembly, and one-pot economy. We extract the technique enumeration and re-stage it for home use rather than importing the station structure.

**Backbone sources** (institutional authority for skill enumeration; treated as Tier 4 cultural/technical fact per [evidence-tiers.md](../00-meta/evidence-tiers.md), not for health claims):
- **The Culinary Institute of America (CIA)** — *The Professional Chef* (9th ed.), AOS/BPS Culinary Arts curriculum. Western-canon spine.
- **Le Cordon Bleu** — Cuisine Diploma curriculum (Foundations → Intermediate → Superior). French-classical spine.
- **École Tsuji (Tsuji Culinary Institute, Osaka)** — Japanese cuisine curriculum (washoku, sushi, kaiseki streams). Primary Japanese-technique authority.
- **Institute of Culinary Education (ICE)** — Culinary Arts + Pastry & Baking Arts diplomas. US-modern, broader cuisine inclusion.
- **Ferrandi Paris** — Cuisine Bachelor + Grand Diplôme. Modern-French + technique-driven.
- **ALMA (La Scuola Internazionale di Cucina Italiana, Colorno)** — Italian Cuisine diploma. Authoritative Italian-regional spine.
- **IHM (Institutes of Hotel Management, India; National Council network)** — Diploma in Culinary Arts; regional Indian technique enumeration.
- **China Culinary Institute / Sichuan Higher Institute of Cuisine (Chengdu) / Yangzhou University Culinary School** — regional Chinese curricula (Sichuan, Huaiyang, Cantonese streams).

**Leg 2 — Academic culinary research.** Peer-reviewed culinary education research is thin compared to nutrition science, but exists in pockets: home-cooking competence research (Caraher, Lang, Wolfson), food-literacy frameworks (Vidgen & Gallegos), and applied food science as taught at institutions like Penn State and UC Davis. Use these to home-cooking-relevance-adjust the pro spine: which skills do home cooks actually need, in what order do they actually grow them, and where does professional-curriculum sequencing miss real home-cook bottlenecks?

**Leg 3 — Bottom-up extraction.** Iterate over the canonical major-dish set per cuisine and extract required techniques. This validates the top-down taxonomy (does the spine actually cover what the cuisine requires?) and surfaces cuisine-specific skills the pro spine misses (e.g., wok hei, masa nixtamalization, koji-handling, idli batter fermentation, tempering whole spices in ghee — none are foregrounded in CIA/Le Cordon Bleu but are foundational in their home cuisines).

The hybrid approach satisfies [geographic neutrality (Rule 9)](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing) by giving non-Western institutional curricula equal taxonomic weight to Western ones, and by using bottom-up extraction to catch what no curriculum centers.

### 2. Skill matrix at medium granularity

Each major skill domain decomposes into 3–5 sub-skills. Sub-skills further decompose at fine granularity as user competence grows (per the granularity strategy in scope above).

| Domain | Sub-skills (medium granularity) |
|---|---|
| **Knife skills** | Grip + safety; dicing (small/medium/large); julienne + brunoise; chiffonade; supreming citrus + deboning poultry / fish |
| **Stocks + foundational liquids** | Bone stock (white/brown); vegetable stock; fumet (fish); dashi (kombu + katsuobushi); aromatic-base prep (mirepoix, sofrito, holy trinity, suppengrün, soffritto, refogado) |
| **Sauces — Western** | Pan sauces (deglaze + mount); mother sauces (béchamel, velouté, espagnole, hollandaise, tomate); emulsions (mayo, vinaigrette, beurre blanc); reductions + jus |
| **Sauces — non-Western** | Curry-base building (onion-tomato bhuna, coconut-tempered, tadka layering); mole (toasted-chile, nut/seed-thickened); Chinese stir-fry sauces (cornstarch slurry, oyster + soy + wine balance); nuoc cham + dipping sauces |
| **Dough — bread** | Mixing (autolyse, straight, sponge); kneading (hand + mixer); bulk + final proof; shaping (boule, batard, baguette); steam-oven crust |
| **Dough — pastry / lamination** | Pâte brisée + sucrée; pâte à choux; puff / croissant lamination; pie crust (US-style); enriched doughs (brioche) |
| **Dough — Asian + Indian + Latin** | Wheat dumpling skin (cold + hot water doughs); rice / glutinous-rice doughs; idli / dosa batter (soak + ferment + grind); roti / chapati / paratha (lamination by ghee); masa nixtamalization + tortilla / tamale handling |
| **Fermentation** | Lactic vegetable (kraut, kimchi, achaar); yeast (bread, beer adjacent); mold-driven (cheese, koji, tempeh); salt-cure + dry-cure (charcuterie, gravlax, salted fish); vinegar + kombucha |
| **Heat application — wet** | Poach; blanch + shock; simmer / boil; braise (white + brown); steam (bamboo, metal, foil-pouch); pressure-cook (stovetop + electric) |
| **Heat application — dry** | Sauté + sweat; sear (Maillard); roast (high + low); broil + salamander; pan-fry; deep-fry (with thermal control + double-fry) |
| **Wok / high-heat stir-fry** | Wok seasoning; wok hei flame technique; velveting; parboil-then-stir-fry (e.g., gai lan); dry-frying (gan bian) |
| **Grilling + smoking** | Direct vs. indirect; charcoal vs. gas vs. wood vs. lump; low-and-slow barbecue (brisket, ribs, pork shoulder); yakitori / robata / satay over coals; whole-fish + plancha / sheet grilling |
| **Tandoor + clay / hearth** | True tandoor breads + meats; home substitutes (cast-iron skillet, pizza-stone broiler, kamado); naan + tandoori protein; live-fire / hearth (Italian wood oven, Argentine asado adjacent) |
| **Rice + grain craft** | Stovetop absorption (long-grain, basmati, jasmine); pilaf method; risotto + paella (controlled stir + crust); sushi rice (rinse + season); sticky-rice steaming; biryani layering (dum) |
| **Noodle craft** | Hand-pulled / hand-cut wheat (lamian, biangbiang, udon); fresh egg pasta (sheeted + shaped); rice noodles (fresh + soaked); soba (buckwheat); ramen / pho / phở-bowl assembly (broth + noodle + topping timing) |
| **Mortar / pounded prep** | Thai curry paste (krachai, lemongrass, chiles); Mexican molcajete salsas + guacamole; Japanese suribachi (sesame, miso); pesto by mortar; Indian masala stone-grinding |
| **Pickling + preserving (non-fermented)** | Quick / refrigerator pickles; vinegar pickling at canning safety; jam + preserve (pectin + acid); confit (oil-cure); freezing + portioning workflow |
| **Pasta + dumpling shaping** | Filled pasta (ravioli, tortellini); extruded shapes; Chinese jiaozi / xiao long bao pleating; Japanese gyoza; Korean mandu; Indian samosa / momos folding |
| **Egg craft** | French omelette; Spanish tortilla; Japanese tamagoyaki; custards (crème anglaise, crème pâtissière); meringue (French, Italian, Swiss) |
| **Spice + aromatic technique** | Whole-spice toasting + grinding; tempering / tadka in fat; layering (bloom in oil → aromatic → liquid); Japanese furikake / shichimi blending; mole spice toasting |
| **Sous vide + modern precision** | Time/temperature for proteins; vacuum-seal handling; finish-sear after bath; food-safety windows (USDA/FDA-tabled) |

(Further enumeration is expected during recipe-bottom-up validation pass.)

### 3. Skill ↔ cuisine matrix

Notation: each cuisine lists **Entry** (skills required to attempt entry-level dishes), **Intermediate**, and **Advanced**. Brief regional / generational variation notes follow major-internal-variation cuisines. Skill domains reference Section 2.

#### French
- *Entry:* knife basics; pan sauce; stock-making (white stock); roast + sauté; vinaigrette; basic egg craft (omelette, custard).
- *Intermediate:* mother sauces (béchamel, velouté, hollandaise); braise (blanquette, daube); pâte brisée + sucrée; emulsion control; pâte à choux.
- *Advanced:* lamination (puff, croissant); charcuterie + terrines; consommé clarification; pâté en croûte; classical garnishes; pastillage / sugar work (pâtisserie track).

#### Italian
- *Entry:* knife basics; soffritto; pasta cooking + sauce-pan finish; risotto absorption; basic dough (focaccia); roast + braise (chicken, pork).
- *Intermediate:* fresh-pasta sheeting + cutting; ragù (long-cook layering); polenta; bread (ciabatta, country loaf); whole-fish handling.
- *Advanced:* filled pasta (tortellini, agnolotti); risotto Milanese-tier (saffron + bone marrow); regional cured meats; gelato + Italian meringue; pizza Napoletana with high-temp oven.
- **Regional variation:** *Northern* — butter, cream, polenta, rice (risotto), fresh egg pasta, alpine cheeses; *Central* — bistecca + grilling, pici, pecorino, white-bean braises; *Southern* — olive oil, tomato + anchovy + capers, dried-pasta dominance, eggplant, sfogliatelle pastry, seafood. Skill weight shifts: Northern skews dairy-emulsion + stock craft; Southern skews dough + tomato-conserve + frying.

#### Spanish
- *Entry:* sofrito; tortilla española; jamón + tapas plating (no-cook composition); paella rice (basic); garlic shrimp.
- *Intermediate:* paella with socarrat; pulpo + seafood handling; gazpacho + cold-soup balance; croquetas (béchamel + breading + fry); escabeche.
- *Advanced:* multi-region paella (Valencian, negro, mar y montaña); jamón curing context; molecular-Catalan (post-elBulli legacy as cultural fact); cocido madrileño (multi-broth meal).

#### Japanese
- *Entry:* dashi (kombu + katsuobushi); rice cooking + seasoning (sushi rice); miso soup; tamagoyaki; basic grilling (yakitori, salt-grill fish).
- *Intermediate:* tempura (batter + oil control); ramen broth + noodle assembly; sushi rolling (maki, nigiri shaping); donburi composition; pickle craft (tsukemono).
- *Advanced:* kaiseki sequencing + presentation; sashimi knife work + fish identification; shojin ryori (Buddhist temple cuisine); fermented condiments from scratch (miso, shoyu); wagashi pastry.
- **Regional / register variation:** *Kaiseki* — seasonal multi-course precision, knife + plating-as-skill; *Izakaya* — casual grilled / fried small plates, less precision-bound; *Home washoku* — ichiju-sansai (rice + soup + 3 sides), economy + balance; *Regional ramen* — Hokkaido miso, Hakata tonkotsu, Tokyo shoyu, Kyushu tonkotsu.

#### Korean
- *Entry:* rice + banchan composition; kimchi handling (purchased); gochujang + ssamjang seasoning; jeon (pan-fried savory pancake); bulgogi marinade + grill.
- *Intermediate:* kimchi from scratch (cabbage salt + paste); bibimbap composition; Korean stews (jjigae); banchan repertoire (5–10 sides); japchae (glass noodle + julienned vegetables).
- *Advanced:* royal-court (gujeolpan, sinseollo); fermented condiments from scratch (gochujang, doenjang, ganjang); Korean BBQ butchery + grilling; tteok rice-cake handling; complex jeongol hot-pot.
- **Register variation:** *Royal court* — multi-component plating + ceremony; *Home banchan* — economy + fermentation rotation; *Street* — tteokbokki, gimbap, hotteok, fried-chicken (yangnyeom). Modern Korean home cooking heavily uses purchased gochujang / doenjang; from-scratch fermentation is a generational / heritage skill.

#### Chinese
- *Entry:* rice cooking; basic stir-fry (sequence + thermal control); steamed egg; egg-drop or simple soup; congee.
- *Intermediate:* wok hei stir-fry; red-cooking (hong shao); dumpling skin + folding (jiaozi); steamed fish (Cantonese); Mapo tofu (Sichuan ma + la balance).
- *Advanced:* hand-pulled noodles (lamian, biangbiang); Peking duck (multi-day air-dry + roast); xiao long bao (skin + soup); Sichuan dry-frying (gan bian); Cantonese roast meats (siu mei); regional banquet sequencing.
- **Regional variation:** *Sichuan* — málà (numb + hot), pickling (pao cai), dry-frying, douban paste; *Cantonese* — steaming, freshness, dim sum, roast meats, light sauces; *Hunan* — smoke + chile, oil-poach; *Jiangsu / Huaiyang* — knife precision, sweet-savory braises, soup-craft; *Shandong* — wheat dough, hearty braises, vinegar; *Northern* — wheat noodles + dumplings + lamb; *Southern* — rice + seafood + lighter sauces.

#### Indian
- *Entry:* rice (basmati absorption); dal tempering (tadka); roti / chapati on tava; basic curry-onion-tomato base (bhuna); whole-spice toasting + grinding.
- *Intermediate:* biryani layering (dum); paneer making + paneer dishes; tandoor-style chicken via home substitute; multi-step gravy (korma, makhani); chutney range; pressure-cooker dal + chana.
- *Advanced:* dosa / idli batter (multi-day soak + ferment + grind); regional thali composition; sweets (gulab jamun, rasgulla, halwa); true tandoor breads + kebabs; biryani regional variants (Hyderabadi, Lucknowi).
- **Regional variation:** *Punjabi / North* — tandoor, dairy (paneer, ghee, cream), wheat-forward breads, rich gravies; *South* — rice + fermented batters (idli, dosa, uttapam), coconut, curry leaves, sambar, rasam; *Bengali* — mustard oil, freshwater fish (macher jhol, ilish), panch phoron, sweets; *Gujarati* — vegetarian, sweet-savory balance, thali tradition, fermented batters (khaman, dhokla); *Goan* — Portuguese-influenced (vindaloo, balchão), coconut + vinegar; *Maharashtrian* — peanut + coconut-jaggery; *Kashmiri* — saffron, dried fruit, slow-braised meats (rogan josh wazwan tradition).

#### Thai
- *Entry:* jasmine rice; pad-thai assembly; basic stir-fry; nam pla (fish sauce) balance; cucumber relish.
- *Intermediate:* curry-paste-from-jar curries (red, green, panang); som tam (green papaya); tom yum + tom kha (sour-spicy + coconut); sticky rice steaming.
- *Advanced:* curry paste from scratch (mortar + pestle, multi-aromatic); whole-fish prep (steamed, fried); royal Thai presentation (kaeb moo, carved fruit); regional southern curries (massaman); proper crispy pork (moo krob).

#### Vietnamese
- *Entry:* nuoc cham mixing; rice noodles (soaked); basic spring rolls (rice paper rolling); pickled-vegetable side (do chua); grilled-meat marinade (lemongrass).
- *Intermediate:* pho broth (multi-hour bone + spice); banh mi assembly + pickle balance; bun cha / bun bo hue assembly; clay-pot dishes (ca kho to); Hue + central-region complex broths.
- *Advanced:* pho broth from-scratch with regional variation (Hanoi clear vs. Saigon sweet); banh xeo crispy crepe; cha lua + vietnamese charcuterie; bánh cuốn (steamed rice crepe).

#### Mexican
- *Entry:* salsa (raw + cooked, molcajete or blender); rice (Mexican / sopa seca); beans (pot or pressure); fresh corn tortillas (from masa harina); fajita / carne asada marinade + grill.
- *Intermediate:* nixtamalization from dried corn; tamales (masa + filling + steaming); enchiladas (sauce-dip-fill-bake); chiles rellenos (roast + peel + stuff + batter + fry); mole simple (toast + blend).
- *Advanced:* mole multi-chile (Oaxacan negro, Pueblan poblano — 20+ ingredients, multi-day); barbacoa pit / underground analog; cochinita pibil (achiote marinade + banana leaf); regional variation (Yucateco, Oaxacan, Puebla, Norteño).

#### US Southern
- *Entry:* fried chicken (brine + dredge + fry); cornbread (skillet); biscuits (cut-in butter); collards (long-braise with smoked-meat); grits.
- *Intermediate:* shrimp + grits; gumbo (roux from light to dark); jambalaya (rice + meat one-pot); pulled pork (low + slow); pecan pie + cobblers.
- *Advanced:* whole-hog barbecue; Cajun + Creole roux mastery + gumbo regional variation; Lowcountry boil; charcuterie + country ham; soul-food vegetable repertoire (greens, peas, pole-beans).
- **Regional variation:** Cajun (rural Louisiana, one-pot, dark roux, file powder); Creole (urban New Orleans, more French + Spanish + African + Caribbean); Lowcountry (SC/GA, rice + seafood); Appalachian (preserved + foraged + pork); Texas BBQ (beef-forward, brisket); Memphis / Carolina BBQ (pork-forward, sauce variation).

#### Middle Eastern
- *Entry:* hummus + baba ghanoush; tabbouleh + fattoush; pita warming; basic kebab marinades; rice pilaf.
- *Intermediate:* shawarma marinade + slice; falafel (soaked-chickpea grind + fry); molokhia / mloukhieh; tagine (Moroccan slow-braise with preserved-lemon + olives); fatteh layering.
- *Advanced:* manakish + flatbread variety; whole-lamb roast; complex tagines (lamb + apricot + almond); knafeh + Levantine sweets; mezze table composition; Iranian rice (tahdig crust); Yemeni saltah + bint al sahn.

#### Eastern European
- *Entry:* potato dishes (mash, pierogi assembly from purchased dough); cabbage handling (slaw, stuffed); sour cream + dill garnishing; borscht; black bread context.
- *Intermediate:* pierogi from scratch (dough + filling + boil + sear); cabbage rolls (golabki / golubtsy); stews (goulash, bigos); bread baking (rye, sourdough); pickling (cucumber, sauerkraut).
- *Advanced:* multi-day fermented preserves (sauerkraut at scale, kvass, kombucha); home charcuterie (kielbasa, kabanos); pelmeni / vareniki by hand; Hungarian goulash + paprikash regional variation; Russian kulebyaka + pirog.

#### Nordic
- *Entry:* gravlax (cure-at-home); rye + crispbread context; smoked-salmon plating; pickled herring (purchased); root-vegetable roasts.
- *Intermediate:* fish-curing (salt + sugar + dill); smörgåsbord composition; meatballs (Swedish); rye bread; lingonberry / cloudberry preserves.
- *Advanced:* fermented seafood (rakfisk, surströmming context); New Nordic technique (foraging + fermentation + preservation per Noma-era cultural reference); cold-smoking; whole-game butchery.

### 4. Skill progression paths — dependency graph

The progression graph powers iterative horizon-broadening pacing (per [intake-pattern.md](../00-meta/intake-pattern.md)) and stretch-recipe identification.

**Core foundation cluster (cross-cuisine):**
```
knife basics ─┐
              ├─→ aromatic-base prep (mirepoix / soffritto / sofrito / tadka / refogado)
heat control ─┘
              ├─→ stock-making + dashi + bouillon
              └─→ pan sauce
```

**Braising path:**
```
knife dicing + sear + stock-making
        ↓
  basic braise (water + sear + low-and-slow)
        ↓
  ┌─────────┬──────────────┬──────────────┐
  ↓         ↓              ↓              ↓
French   Italian      Chinese          Mexican
peasant  rustic       red-cooking      birria + barbacoa
(boeuf   (osso buco,  (hong shao)      (slow stewed)
 bourg)  ragù)
```

**Fermentation path (long-horizon, opens many cuisines):**
```
purchased ferment use (kimchi, miso, gochujang, kraut)
        ↓
  quick lacto-pickle (cucumbers, daikon, do chua)
        ↓
  multi-day vegetable fermentation (kraut, kimchi from scratch)
        ↓
  ┌──────────────┬─────────────────────┬─────────────────┐
  Korean         Eastern European       Indian batter     East Asian
  banchan +      preserved cuisine      (idli/dosa)       paste-cuisine
  fermented      (kvass, sauerkraut)                      (miso, gochujang
  pastes                                                   from scratch)
```

**Dough path:**
```
basic flatbread (tortilla, roti, naan via skillet)
        ↓
  yeasted bread (no-knead → straight dough)
        ↓
  ┌──────────────┬──────────────┬────────────────┐
  Pizza /        Lamination     Asian dumpling   Indian flatbread
  focaccia       (puff,         skin (cold/hot   complexity (paratha
                 croissant)     water dough)     lamination, kulcha)
```

**Stretch-recipe rule:** a recipe is a *valid stretch* if it requires exactly one new skill atop a base of mastered prerequisites. Recipes requiring two-or-more new skills are flagged as *learning-cluster recipes* and surface only when the user has explicitly opted into a deeper learning push, OR when the system has paced the user there over time. This satisfies the iterative horizon-broadening pace control without overwhelming the user.

### 5. Equipment ↔ skill bindings

| Equipment | Skills enabled | Cuisine bindings | Substitution notes |
|---|---|---|---|
| **Carbon-steel wok** (with adequate BTU) | Wok hei stir-fry, deep-fry, steam-with-rack, dry-fry | Chinese (esp. Cantonese, Sichuan), some SE Asian | Cast-iron skillet approximates stir-fry but cannot deliver wok hei (insufficient surface curvature + BTU). Outdoor wok burner is the home approximation. |
| **Stovetop pressure cooker** | Pressure-braise, beans + legumes, biryani dum | Indian (foundational), some Latin American (carne, frijoles), Eastern European (stews) | Electric pressure (Instant Pot) substitutes well; longer cycle but accessible. |
| **Bamboo / metal steamer** | Dim sum, mantou, idli, dhokla, dumpling steam | Chinese, Indian (south), SE Asian | Foil-rack-in-pot improvises for occasional use; bamboo gives better moisture management. |
| **Tandoor (clay)** | True tandoori breads + meats (high-heat clay-walled) | Indian (Punjabi), Persian-adjacent | Pizza stone in broiler + cast-iron skillet at max heat is the canonical home substitute. Kamado-style ceramic grill is closer but expensive. |
| **Cast-iron skillet** | Sear, oven-finish, cornbread, skillet bread, naan substitute, tortilla cooking | US Southern, generic Western, Indian (substitute) | Carbon steel is a lighter alternative for sauté; enameled cast iron (Dutch oven) for braise. |
| **Outdoor grill (charcoal / wood)** | Direct + indirect grilling, low-and-slow BBQ, asado-style, yakitori, satay | US BBQ, Korean (galbi), Argentine, Japanese yakitori, SE Asian satay | Gas grill loses smoke flavor; broiler substitutes for direct char for small pieces only. |
| **Smoker (offset, kamado, electric)** | Cold-smoke, hot-smoke, low-and-slow brisket / pork shoulder, fish smoking | US BBQ (Texas, Carolina), Nordic fish-smoke | Kettle grill with charcoal-snake method is entry-level smoker substitute. |
| **Sous-vide immersion circulator + chamber/zip vacuum** | Time/temp protein control, modern precision | Cuisine-agnostic (technique tool) | No real substitute for the precision; oven-on-low + thermometer is a poor approximation. |
| **Stand mixer** | Kneading at scale, lamination prep, meringue + whip work, brioche | Western pastry, bread baking | Hand-knead substitutes for time + effort. |
| **Mortar + pestle (granite / lava)** | Thai curry paste, pesto by hand | Thai, Italian (traditional pesto) | Food processor approximates flavor but loses cell-rupture flavor release; molcajete (lava-rock) for Mexican has no equivalent. |
| **Molcajete (lava rock)** | Salsas, guacamole, dry-toasted spice grind | Mexican | Granite mortar is closer than ceramic; food processor flattens texture. |
| **Suribachi + surikogi** | Sesame, miso paste, gomashio | Japanese | Mortar + pestle substitutes; the ridged interior of suribachi gives finer control. |
| **Tagine (clay)** | Slow-braise with steam-condensation lid | Moroccan | Heavy-lidded Dutch oven substitutes; loses the conical-condensation effect somewhat. |
| **Paella pan (carbon-steel, wide + shallow)** | Paella socarrat | Spanish | Wide cast-iron skillet substitutes for small portions; wide surface area is the key. |
| **Donabe / clay pot** | Japanese rice + nabe, Korean dolsot | Japanese, Korean | Heavy ceramic Dutch oven approximates. |
| **Comal / griddle** | Tortillas, quesadillas, pita | Mexican, Middle Eastern | Cast-iron skillet works; flat-top griddle for scale. |

### 6. Skill ↔ recipe linkage schema

This is the schema that recipes (sourced under [sweep #11](../11-recipe-sourcing/scope.md)) populate:

```
recipe.skills_required: [
  { skill_id, granularity_tag (medium|fine), confidence_floor (entry|intermediate|advanced) }
]
recipe.skill_prerequisites: [skill_id, ...]   # must precede in user's progression graph
recipe.stretch_skills: [skill_id, ...]        # newly introduced by this recipe (ideally ≤1 for stretch-recipe rule)
recipe.equipment_required: [equipment_id, ...]
recipe.equipment_substitutes: [{ required, substitute, fidelity_loss_note }]
recipe.cultural_context: { cuisine, region, register (royal|home|street|festive), generational_marker (traditional|modern|fusion) }
recipe.evidence_tier: 1|2|3|4    # for any health-claim metadata attached
recipe.confidence_tier_mapping: entry|intermediate|advanced (per Section 3 cuisine matrix)
recipe.progression_graph_position: { domain, depth_index, opens_subdomains: [...] }
recipe.where_to_learn_refs: [resource_id, ...]   # for missing-skill surfacing
```

Schema-level rules:
- Stretch-recipe pacing enforces ≤1 new skill for default suggestions; ≥2 new skills require explicit user opt-in (per progression-graph rule in Section 4).
- Cultural-context register and generational-marker make regional/intra-cuisine variation queryable rather than collapsed.
- `where_to_learn_refs` is surfaced only when the user is missing a required skill (per [product-framing](../00-meta/product-framing.md#what-nutrime-is-explicitly-not) "not a cooking class" boundary — link out, don't deliver).

### 7. "Where to learn" reference map

Mapped at category level (per [framework-over-source-list principle](../00-meta/dynamic-research-expansion.md#framework-over-source-list--the-corpus-design-principle)). System surfaces categories + representative resources; does not curate or partner.

| Category | Representative resources | Best for |
|---|---|---|
| **Institutional academy public content** | CIA YouTube + free curriculum overviews; Le Cordon Bleu online short courses; Tsuji English-language excerpts; Ferrandi public masterclasses; ICE recreational courses | Authoritative technique grounding; vetted skill enumeration |
| **Subscription education platforms** | MasterClass (Gordon Ramsay, Thomas Keller, Massimo Bottura, Wolfgang Puck, José Andrés, Niki Nakayama, Apollonia Poilâne, Ottolenghi-adjacent); Rouxbe online culinary school (full curriculum); Curtis Stone / Sur la Table; Milk Street school | Structured progression; technique-by-technique learning |
| **Reference cookbooks (skill-focused)** | *The Professional Chef* (CIA) — Western canon; *On Cooking* (Labensky) — culinary fundamentals textbook; *The Food Lab* (J. Kenji López-Alt) — applied food-science home cooking; *Salt, Fat, Acid, Heat* (Samin Nosrat) — flavor-foundation; *Modernist Cuisine at Home*; *La Technique* (Pépin) | Reference-grade home-applicable technique |
| **Cuisine-specific authoritative texts** | *Japanese Cooking: A Simple Art* (Tsuji); *The Food of Sichuan* (Fuchsia Dunlop); *660 Curries* (Iyer); *Essentials of Classic Italian Cooking* (Marcella Hazan); *The Cooking of Southwest France* (Wolfert); *Diana Kennedy's Oaxaca al Gusto*; *Maangchi's Real Korean Cooking*; *Pok Pok* (Ricker for Thai); *Vietnamese Home Cooking* (Pham); *The Zuni Café Cookbook*; *Plenty / Jerusalem / Simple* (Ottolenghi for Levantine); *The New Nordic* (Meyer); *Rasika* (Ashok Bajaj); regional Chinese works (Dunlop's *Land of Fish and Rice*, *The Food of Shanghai*) | Cuisine-specific skill mapping with cultural authority |
| **Credentialed YouTube** (engagement + provenance qualified per sweep #11) | Kenji López-Alt; Adam Ragusea; Helen Rennie; Babish Culinary Universe (technique series); America's Test Kitchen / Cook's Illustrated; Maangchi (Korean); Chinese Cooking Demystified (regional Chinese with primary-source method); Pailin's Kitchen (Thai); Ethan Chlebowski (technique); Vincenzo's Plate (Italian); Made With Lau (Cantonese); Just One Cookbook (Japanese, Namiko Chen); Pro Home Cooks; Mỹ Lệ (Vietnamese); Vahchef + Hebbar's Kitchen (Indian); Rick Bayless (Mexican). | Free-tier visual learning at home-cook accessibility |
| **Regional / cultural-center in-person classes** | US: community-college continuing ed; Sur la Table classes; ICE recreational; Williams-Sonoma; cultural-center classes (e.g., Japan Society NYC, Korea Society NYC, Confucius Institutes, regional Indian community classes via temples / cultural orgs, Casa Mexicana Boston-style centers); Eataly cooking classes (Italian) | Tactile + community learning; cultural-context exposure |
| **University-affiliated food-studies + extension** | Cornell Cooperative Extension; UC Davis food-science courses; Penn State Extension; UK's Leiths School; Ballymaloe Cookery School (Ireland) | Food-science + applied home-cook research-grounded |
| **Skill-domain specialist content** | Bread: Forkish *Flour Water Salt Yeast*, Robertson *Tartine*, King Arthur Baking School; Charcuterie: Ruhlman + Polcyn *Charcuterie*; Fermentation: Sandor Katz *Art of Fermentation*, Noma's *Foundations of Flavor*; Pastry: Hermé, Bo Friberg *The Professional Pastry Chef*; Sous vide: ChefSteps + Modernist Cuisine; Knife skills: CIA + Norman Weinstein *Mastering Knife Skills* | Deep single-domain skill acquisition |

System surfaces these by category-match-to-missing-skill. Ranking signals (per qualification framework): institutional credentialing, peer recognition (chef + journalism), engagement-with-quality (not raw view-count), licensing compliance (we link out, no scraping). Quality filters are domain-specific — for fermentation Sandor Katz outranks a high-view social account; for Japanese knife work Tsuji-trained instructors outrank generic YouTube cooking channels. Filtering / ranking is a downstream-system question; this sweep maps the universe.

### 8. Open questions — answers

**Q: For the hybrid skill taxonomy: where do professional culinary curricula converge vs. diverge across CIA, Le Cordon Bleu, Tsuji, IHM, China Culinary Academy?**

*Convergence:* All five converge on knife skills → stocks → sauces → heat-application progression as the foundational sequence; all gate dough/pastry as a separate vertical track; all enforce sanitation / mise-en-place as cross-cutting. *Divergence:* Le Cordon Bleu and CIA prioritize French-classical sauce-mother taxonomy; Tsuji prioritizes dashi + rice + knife (sushi) as primary spine; IHM's regional Indian streams diverge on tadka + masala-grinding + tandoor as foundational where Western curricula treat them as electives; China's regional academies diverge by region (Sichuan academy centers wok hei + málà + dry-frying; Cantonese-tradition programs center steaming + roast meats; Huaiyang centers knife precision + sweet-savory braise). The hybrid spine takes the convergence as the shared backbone and treats divergence as cuisine-specific additions, which is precisely the design Sections 2–3 implement.

**Q: For skill progression: what's the published evidence on how home cooks actually grow skills over time (vs. what professional curricula assume)?**

Limited but real. Caraher et al. (1999) and follow-on work documents skill atrophy across generations in the UK; Wolfson & Bleich (2015) documents inverse relationship between cooking confidence and reliance on convenience foods in US adults; Vidgen & Gallegos (2014) defines food literacy across four domains (planning, selection, preparation, eating) — a framework that diverges from professional-curriculum sequencing by foregrounding planning and shopping as skills. Caraher and Lang's "deskilling" line argues that home-cook skill progression follows different drivers (necessity, family role, exposure) than professional curricula assume (linear instructor-led). NutriMe's stretch-skill pacing (Section 4) honors this: progression is exposure-driven and need-driven, paced via passive confirmation (per [intake-pattern.md](../00-meta/intake-pattern.md)), not scheduled instructor-led.

**Q: For non-Western cuisine skill mapping: what English-language / translated sources adequately characterize regional skill variation?**

For Chinese: Fuchsia Dunlop's regional volumes (Sichuan, Hunan, Jiangnan) are gold standard; *Chinese Cooking Demystified* validates methodology with Chinese-language primary sources. For Indian: Iyer (*660 Curries*, *On the Curry Trail*), Madhur Jaffrey, Niloufer Ichaporia King, Asma Khan; for South Indian, Chandra Padmanabhan and Shri Bhagavati Krishnan-influenced works; Vikas Khanna's regional thali documentation. For Japanese: Tsuji + Andoh (*Washoku*, *Kansha*); Just One Cookbook for accessibility. For Korean: Maangchi, Hooni Kim, Cecilia Hae-Jin Lee, Sohui Kim. For Thai: Andy Ricker (*Pok Pok*), David Thompson (*Thai Food*, *Thai Street Food*). For Vietnamese: Andrea Nguyen, Charles Phan, Mai Pham. For Mexican: Diana Kennedy's regional volumes (Oaxaca al Gusto), Rick Bayless, Pati Jinich, Enrique Olvera (*Mexico from the Inside Out*). Coverage is uneven (Sichuan + Punjabi well-covered; Hunan / Bengali / Yucateco less so in English) — a known gap.

**Q: For equipment ↔ skill: which equipment substitutions actually work (e.g., dutch oven as tandoor substitute, sheet pan as broiler-charring substitute)?**

Substitutions that work well: Dutch oven for braising (genuine equivalence to enameled cast-iron); cast-iron + pizza stone in max-temperature broiler for tandoor naan (close approximation); kamado for tandoor breads + meats (closer than oven-broiler combo); foil-pouch on rack for steaming (occasional use); molcajete-substitute granite mortar for Mexican (texture loss); blender for curry paste (flavor loss vs. mortar + pestle, but acceptable). Substitutions that do NOT work well: gas grill for charcoal / wood smoking (essential smoke loss); food processor for pesto (oxidation + texture); broiler for offset smoker (no smoke); regular pot for paella (no socarrat surface area); standard oven for true wok hei (insufficient direct flame). Per scope, the system surfaces substitution + a fidelity-loss note rather than silently substituting.

**Q: For "where to learn" mapping: what's the realistic universe of skill-acquisition resources, and how do they get ranked / filtered by quality?**

The universe is enumerated in Section 7. Ranking signals: (1) institutional credentialing — academy affiliation, chef certification; (2) peer recognition — James Beard / Michelin / cultural-recognition awards, citation by other authorities; (3) provenance + sourcing transparency — does the resource cite primary sources? does it engage primary-language sources for non-Western cuisines? (4) engagement-with-quality — view-count alone is a noisy signal; engagement weighted by editorial / chef community recognition is better; (5) licensing + ToS compliance — system links out, never embeds or scrapes. Filtering must be cuisine-specific: for Japanese knife work Tsuji-affiliated content is high-rank; for Sichuan, Dunlop + Chinese Cooking Demystified rank high; for any cuisine, primary-language-engaging content from the cuisine's tradition outranks generic English-language interpretation. This filtering belongs to downstream system design; this sweep enumerates the framework, not the specific ranking algorithm.

**Q: For cultural variation: how much variation does the system surface to the user vs. abstract away?**

Surface variation when the user has signaled engagement (asked about the cuisine, cooked from it before, expressed interest in horizon-broadening within it); abstract when the user is at first-exposure to the cuisine. Concretely: a first-time user trying Indian gets "Indian" as a single bucket with a few representative dishes spanning regions; a user who has cooked five Indian dishes and rated them gets surfaced regional variation (Punjabi / South / Bengali / Gujarati) and asked which they want to explore deeper. This pattern parallels iterative horizon-broadening in [intake-pattern.md](../00-meta/intake-pattern.md): granularity grows with engagement signal. The system never collapses cuisines silently — when it abstracts, it labels (e.g., "this is North-Indian–style; the cuisine spans many traditions, ask if you want to explore others"). Cultural respect demands the meta-signal even when the immediate dish is abstracted.

## References

> Citations below treat professional culinary curricula as **institutional authority for skill enumeration** (a cultural / technical fact, Tier 4 framing per [evidence-tiers.md](../00-meta/evidence-tiers.md)) — not as evidence for any health claim. Where peer-reviewed culinary education research is cited, it is Tier 2/3 and supports skill-progression and home-cook-competence claims, not health-effect claims. Accessed-on date is `2026-04-29`; live URL verification is queued as a follow-up given WebFetch was not invoked under this sweep's tool constraint.

### Professional culinary curriculum frameworks

- **The Culinary Institute of America** (2011). *The Professional Chef* (9th ed.). Wiley. Used as Western-canon skill-enumeration spine. Curriculum reference: CIA AOS / BPS Culinary Arts. https://www.ciachef.edu/. Accessed 2026-04-29.
- **Le Cordon Bleu** (n.d.). *Cuisine Diploma — Foundations, Intermediate, Superior curriculum*. Le Cordon Bleu International. https://www.cordonbleu.edu/. Accessed 2026-04-29.
- **École Tsuji** (Tsuji Culinary Institute, Osaka) (n.d.). *Japanese Cuisine Curriculum (washoku, sushi, kaiseki streams)*. https://www.tsuji.ac.jp/. Accessed 2026-04-29.
- **Institute of Culinary Education (ICE)** (n.d.). *Culinary Arts + Pastry & Baking Arts Diploma curricula*. https://www.ice.edu/. Accessed 2026-04-29.
- **Ferrandi Paris** (n.d.). *Cuisine Bachelor + Grand Diplôme curricula*. https://www.ferrandi-paris.com/. Accessed 2026-04-29.
- **ALMA — La Scuola Internazionale di Cucina Italiana** (n.d.). *Italian Cuisine Diploma curriculum*. Colorno, Italy. https://www.alma.scuolacucina.it/. Accessed 2026-04-29.
- **National Council for Hotel Management & Catering Technology (India) / IHM network** (n.d.). *Diploma in Culinary Arts curricula (regional Indian streams)*. https://nchmct.nic.in/. Accessed 2026-04-29.
- **Sichuan Higher Institute of Cuisine** (Chengdu) (n.d.). Regional Sichuan cuisine programs. (Authoritative regional-Chinese curriculum reference.)
- **Yangzhou University Culinary School / Huaiyang tradition programs** (n.d.). Regional Huaiyang curriculum reference.

### Canonical cooking-education texts (skill-focused)

- Labensky, S.R., Hause, A.M., & Martel, P. (2018). *On Cooking: A Textbook of Culinary Fundamentals* (6th ed.). Pearson. (Standard culinary fundamentals textbook.)
- López-Alt, J. Kenji (2015). *The Food Lab: Better Home Cooking Through Science*. W.W. Norton.
- Nosrat, S. (2017). *Salt, Fat, Acid, Heat: Mastering the Elements of Good Cooking*. Simon & Schuster.
- Pépin, J. (1976). *La Technique*. Times Books / Random House.
- Friberg, B. (2002). *The Professional Pastry Chef* (4th ed.). Wiley.
- McGee, H. (2004). *On Food and Cooking: The Science and Lore of the Kitchen* (revised ed.). Scribner. (Cross-cuisine technique-science reference.)
- Weinstein, N. (2009). *Mastering Knife Skills: The Essential Guide to the Most Important Tools in Your Kitchen*. Stewart, Tabori & Chang.

### Cuisine-specific authoritative texts

- Tsuji, S. (1980, reissued 2006). *Japanese Cooking: A Simple Art*. Kodansha International.
- Andoh, E. (2005). *Washoku: Recipes from the Japanese Home Kitchen*. Ten Speed Press.
- Andoh, E. (2010). *Kansha: Celebrating Japan's Vegan and Vegetarian Traditions*. Ten Speed Press.
- Dunlop, F. (2019). *The Food of Sichuan*. W.W. Norton. (Plus *Land of Fish and Rice* (2016), *Revolutionary Chinese Cookbook* (2007), *Every Grain of Rice* (2012).)
- Hazan, M. (1992). *Essentials of Classic Italian Cooking*. Knopf.
- Wolfert, P. (1983). *The Cooking of Southwest France*. Harper & Row.
- Kennedy, D. (2010). *Oaxaca al Gusto: An Infinite Gastronomy*. University of Texas Press.
- Bayless, R. (1987). *Authentic Mexican: Regional Cooking from the Heart of Mexico*. William Morrow.
- Iyer, R. (2008). *660 Curries*. Workman.
- Jaffrey, M. (1973). *An Invitation to Indian Cooking*. Knopf.
- Maangchi (Emily Kim) (2015). *Maangchi's Real Korean Cooking*. Houghton Mifflin Harcourt.
- Kim, H. (2020). *My Korea: Traditional Flavors, Modern Recipes*. W.W. Norton.
- Ricker, A. (2013). *Pok Pok: Food and Stories from the Streets, Homes, and Roadside Restaurants of Thailand*. Ten Speed Press.
- Thompson, D. (2002). *Thai Food*. Ten Speed Press.
- Nguyen, A. (2006). *Into the Vietnamese Kitchen*. Ten Speed Press.
- Pham, M. (2001). *The Best of Vietnamese & Thai Cooking*. Three Rivers Press.
- Ottolenghi, Y., & Tamimi, S. (2012). *Jerusalem: A Cookbook*. Ten Speed Press. (Plus *Plenty* (2010), *Simple* (2018).)
- Roden, C. (1996). *The Book of Jewish Food: An Odyssey from Samarkand to New York*. Knopf. (Authoritative Middle Eastern + Mediterranean reference.)
- Meyer, C. (2016). *The New Nordic: Recipes from a Scandinavian Kitchen*. Ten Speed Press.
- Edge, J.T. (2017). *The Potlikker Papers: A Food History of the Modern South*. Penguin Press. (US Southern context reference.)
- Lewis, E. (1976). *The Taste of Country Cooking*. Knopf. (US Southern foundational text.)

### Skill-domain specialist references

- Forkish, K. (2012). *Flour Water Salt Yeast: The Fundamentals of Artisan Bread and Pizza*. Ten Speed Press.
- Robertson, C. (2010). *Tartine Bread*. Chronicle Books.
- Ruhlman, M., & Polcyn, B. (2013). *Charcuterie: The Craft of Salting, Smoking, and Curing* (revised). W.W. Norton.
- Katz, S.E. (2012). *The Art of Fermentation*. Chelsea Green.
- Redzepi, R., & Zilber, D. (2018). *The Noma Guide to Fermentation*. Artisan.
- Myhrvold, N., et al. (2011). *Modernist Cuisine: The Art and Science of Cooking*. Cooking Lab. (And *Modernist Cuisine at Home*, 2012.)

### Academic culinary education research (peer-reviewed, Tier 2/3)

- Caraher, M., Dixon, P., Lang, T., & Carr-Hill, R. (1999). The state of cooking in England: the relationship of cooking skills to food choice. *British Food Journal*, 101(8), 590–609.
- Lang, T., & Caraher, M. (2001). Is there a culinary skills transition? Data and debate from the UK about changes in cooking culture. *Journal of the HEIA*, 8(2), 2–14.
- Vidgen, H.A., & Gallegos, D. (2014). Defining food literacy and its components. *Appetite*, 76, 50–59. https://doi.org/10.1016/j.appet.2014.01.010
- Wolfson, J.A., & Bleich, S.N. (2015). Is cooking at home associated with better diet quality or weight-loss intention? *Public Health Nutrition*, 18(8), 1397–1406. https://doi.org/10.1017/S1368980014001943
- Mills, S., White, M., Brown, H., et al. (2017). Health and social determinants and outcomes of home cooking: A systematic review of observational studies. *Appetite*, 111, 116–134. https://doi.org/10.1016/j.appet.2016.12.022
- Engler-Stringer, R. (2010). Food, cooking skills, and health: A literature review. *Canadian Journal of Dietetic Practice and Research*, 71(3), 141–145.

### Subscription / online education platforms (referenced as resource categories per Section 7)

- MasterClass — chef-led video curricula. https://www.masterclass.com/. Accessed 2026-04-29.
- Rouxbe Online Culinary School. https://www.rouxbe.com/. Accessed 2026-04-29.
- America's Test Kitchen Cooking School. https://www.americastestkitchen.com/cookingschool. Accessed 2026-04-29.
- King Arthur Baking School. https://www.kingarthurbaking.com/baking-school. Accessed 2026-04-29.
- ChefSteps. https://www.chefsteps.com/. Accessed 2026-04-29.

### Notes on follow-up verification

Live URL verification (HTTP fetch + content-confirmation) is queued for a subsequent sweep iteration where WebFetch is available. Curriculum-specific syllabi (e.g., the exact CIA AOS Culinary Arts skill-by-term sequence, Tsuji's full washoku-to-kaiseki progression) should be sourced from primary-academy publications under that follow-up. Bottom-up validation pass (iterating canonical-dish-set → required-skills extraction across each Section 3 cuisine) is also queued as a separate sweep activity to validate and extend this top-down enumeration.
