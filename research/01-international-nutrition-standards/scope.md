# Sweep #1 — International Nutrition Reference Standards

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Build a comparative reference map of nutrition reference standards (DRIs / NRVs / RNIs / DRVs) across the top 150 countries' authoritative bodies, plus dietary pattern guidance and public-health additions. Characterize where bodies agree, where they diverge, why, and how the system should present those divergences to users.

## Deliverable

An annotated reference map containing:

- Per-body inventory: bodies covering ~150 countries' worth of standards (per FAO INFOODS membership), key publications, current versions, publication / next-revision dates
- Comparative table for major nutrients (energy, protein, fat distribution, carbohydrate, fiber, key vitamins, key minerals, water, sodium ceiling) showing where bodies agree and where they materially diverge
- Dietary pattern guidance per body — Mediterranean, Nordic NNR, Japanese spinning top, Brazilian dietary guidelines, EAT-Lancet planetary, US DGA, etc. — with links and current versions
- Public-health additions: added sugar, sodium, alcohol, ultra-processed foods, trans fat thresholds, where each body publishes them
- Methodology notes: how each body derives its numbers (basal needs, EAR/RDA model, AI/UL framing, age-sex stratification approach)

This is a **reference map**, not a corpus build. Actual data ingestion happens in a later phase.

## In scope

- **Geographic scope:** top 150 countries (effectively FAO INFOODS coverage)
- **Standards bodies (representative):**
  - US — NASEM/IOM DRIs, USDA Dietary Guidelines
  - EU — EFSA Dietary Reference Values
  - UK — SACN, Public Health England RNIs
  - Australia / New Zealand — NHMRC NRVs
  - Canada — Health Canada DRIs (uses US NASEM)
  - Nordic — NNR (Nordic Nutrition Recommendations)
  - WHO / FAO — global recommendations and EAR ranges
  - Japan — DRI-J (MHLW)
  - India — ICMR-NIN
  - China — Chinese Nutrition Society DRIs
  - Brazil — Ministry of Health Dietary Guidelines
  - Other countries surveyed at minimum at the dietary-guidelines level
- **Nutrient panel:** full DRI panel (energy, macros, micros, fatty acids, amino acids, fiber, water)
- **Population subgroups:** full matrix (age × sex × life stage including pregnancy / lactation)
- **Dietary patterns:** Mediterranean (multiple national variants), Nordic, Japanese spinning top, Brazilian, EAT-Lancet, DASH, MIND, Okinawan, traditional Andean, traditional Sub-Saharan, etc.
- **Public-health additions:** added-sugar limits, sodium ceilings, alcohol guidance, UPF warnings, trans fat thresholds
- **Recency tracking:** publication date, last revision, currently-under-revision status (e.g., US DGA 2025–2030 cycle)

## Out of scope (with reasons)

- Bulk ingestion of DRI tables — deferred to a later corpus-build phase (see Principle B in [README](../README.md))
- Food composition data — covered in [sweep #2](../02-food-composition-databases/scope.md)
- How recommendations should be communicated to users (the "why" delivery question) — covered in [sweep #8](../08-nutrition-education-delivery/scope.md)
- Cuisine-level eating patterns finer than national (regional / religious / diasporic) — partially covered in [sweep #3](../03-clinical-nutrition-assessment/scope.md), broad framework only

## Conflict resolution philosophy (for product surface)

When bodies disagree, the system uses **option C with geographic neutrality** (per [Constitutional Rule 9](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing)):

- Show the range of recommendations across bodies, **equal-weighted** regardless of country of origin
- Explain why bodies differ (methodology, population reference, evidence interpretation)
- **Do not default to or prioritize the user's home-country body.** Geographic location is a logistics data point, not a content filter.
- Always surface alternative dietary patterns and recommendations so the user understands their home country is one option among many — *"everybody's body is different, and they're going to handle these things differently, so we want to give them the options"*
- Apply [Constitutional Rule 1](../00-meta/constitutional-rules.md#rule-1--consult-a-professional): direct the user to a doctor or licensed nutritionist where authoritative bodies materially disagree

The presentation challenge — surfacing a multi-source global menu without overwhelming the user — is researched in [sweep #8](../08-nutrition-education-delivery/scope.md) (progressive disclosure, synthesis-with-expansion, comparative tables for depth-seeking users).

## Open questions for the research

- Which non-Western standards bodies have publicly accessible English-language documentation? Which require translation?
- Where do bodies materially disagree (>15–20% difference) on macronutrient or micronutrient targets, and what is the scientific basis for the disagreement?
- Which bodies have the most current evidence reviews vs. which are working off decades-old assumptions?
- Which bodies publish dietary pattern guidance vs. only nutrient-level DRIs?
- How do bodies handle sub-populations not well-represented in their underlying evidence base (e.g., older adults in DRI panels derived from younger-adult data)?

## Cross-references

- Bound by [Constitutional Rule 5 — international by default](../00-meta/constitutional-rules.md#rule-5--international-by-default-geographically-respectful)
- Bound by [Evidence Tiers](../00-meta/evidence-tiers.md) — DRIs from authoritative bodies are Tier 1
- Feeds [sweep #2 (food composition databases)](../02-food-composition-databases/scope.md) — geographic and body-publishing overlaps
- Feeds [sweep #3 (clinical nutrition assessment)](../03-clinical-nutrition-assessment/scope.md) — DRIs are referenced in dietary assessment
- Feeds [sweep #8 (nutrition education / why delivery)](../08-nutrition-education-delivery/scope.md) — explanations rely on these standards
- Feeds [sweep #10 (clinical condition gating)](../10-clinical-condition-gating/scope.md) — condition-specific DRIs exist for many bodies

## Findings

> All claims about nutrient intake values, dietary patterns, or public-health thresholds in this section are tagged with an evidence tier per [evidence-tiers.md](../00-meta/evidence-tiers.md). Bodies that publish DRIs/NRVs/RNIs/DRVs are themselves Tier 1 sources. Wikipedia, where used, is treated as a navigation aid only — every Wikipedia-sourced number is corroborated against the relevant body's own publication.

> **Stage 5 verification — 2026-06-30 (DRI publication versions, upfront cross-cutting per S4-Q4):** Baseline (2006 IOM DRI summary tables + NASEM 2019 Sodium/Potassium + NASEM 2023 Energy) is still current for numeric values. Two deltas since the original sweep: (1) **NASEM 2024 letter report "Rethinking the AMDR for the 21st Century"** (Nov 12, 2024) — a framework/process change recommending the Acceptable Macronutrient Distribution Range be retired as a formal DRI value type; does **not** issue new numeric values for protein/fat/carbohydrate yet. Treat as a process flag — AMDR values may be deprecated in the next macronutrient release. (2) **Macronutrient full consensus committee review actively in progress** (protein, fat, carbohydrate, fiber, amino acids, fatty acids); no publication date publicly confirmed. Vitamin D/Calcium re-review not currently announced. Health Canada continues to co-publish using NASEM numeric values with no known Canada-specific variances. **MVP corpus target:** 2006 IOM tables (micronutrient backbone) + NASEM 2019 (Sodium/Potassium) + NASEM 2023 (Energy); note AMDR letter report as a deprecation flag. Canonical access: NIH ODS HTML/PDF + NCBI Bookshelf (no purpose-built machine-readable DRI dataset surfaced; ODS API at `ods.od.nih.gov/api/` covers nutrient fact sheets, not DRI tables). *Verification caveat: direct WebFetch on the NIH ODS DRI page was denied in this session; format details are from search-result descriptions, not first-hand inspection.* Sources accessed 2026-06-30: [NASEM macronutrient project page](https://www.nationalacademies.org/our-work/dietary-reference-intakes-for-macronutrients) · [NASEM AMDR letter report (Nov 2024)](https://www.nationalacademies.org/publications/27957) · [NASEM DRI process updates](https://www.nationalacademies.org/news/updates-and-innovation-opportunities-for-the-dietary-reference-intakes-process) · [NIH ODS nutrient recommendations](https://ods.od.nih.gov/HealthInformation/nutrientrecommendations.aspx) · [NCBI Bookshelf DRI summary tables](https://www.ncbi.nlm.nih.gov/books/NBK545442/) · [Health Canada DRI](https://www.canada.ca/en/health-canada/services/food-nutrition/healthy-eating/dietary-reference-intakes.html) · [ODPHP macronutrients review](https://odphp.health.gov/our-work/nutrition-physical-activity/dietary-guidelines/dietary-reference-intakes/review-macronutrients-and-energy).

### A. Per-body inventory

#### A.1 NASEM (US/Canada) — Dietary Reference Intakes (DRIs)

- **Body:** US National Academies of Sciences, Engineering, and Medicine (formerly the Institute of Medicine, IOM). The Food and Nutrition Board, under the Health and Medicine Division, convenes the standing DRI committee.
- **Joint authorship:** US/Canada — Health Canada participates in DRI committees and adopts NASEM values directly (see Health Canada, A.5).
- **Foundational series (1997–2005):** Eight DRI volumes covering: Calcium / Vitamin D / Phosphorus / Magnesium / Fluoride (1997); Thiamin / Riboflavin / Niacin / Vitamin B6 / Folate / Vitamin B12 / Pantothenic acid / Biotin / Choline (1998); Vitamin C / Vitamin E / Selenium / Carotenoids (2000); Vitamin A / Vitamin K / Arsenic / Boron / Chromium / Copper / Iodine / Iron / Manganese / Molybdenum / Nickel / Silicon / Vanadium / Zinc (2001); Energy / Carbohydrate / Fiber / Fat / Fatty Acids / Cholesterol / Protein / Amino Acids (2002, reprinted 2005); Water / Potassium / Sodium / Sulfate (2004) [Tier 1: NASEM/IOM 1997–2005].
- **Consolidated reference:** *Dietary Reference Intakes: The Essential Reference for Dietary Planning and Assessment* (2006). Replaced the 1989 RDA 10th edition and 1990 Canadian Nutrition Recommendations.
- **Major recent revision:** *Dietary Reference Intakes for Sodium and Potassium* (NASEM 2019) — introduced the Chronic Disease Risk Reduction Intake (CDRR) for sodium (2,300 mg/day for adults) and revised AIs (potassium AI lowered to 3,400 mg/day for adult men, 2,600 mg/day for adult women; sodium AI 1,500 mg/day retained for adults). Replaced the 2004 sodium UL framework; the new sodium DRI explicitly does **not** set a UL [Tier 1: NASEM 2019].
- **Methodology:** EAR / RDA / AI / UL framework. RDA defined as EAR + 2 SD (covers ~97.5% of healthy population). AI used where EAR cannot be derived. CDRR introduced 2019 for sodium specifically. Stratified by life stage: 0–6 mo, 7–12 mo, 1–3 y, 4–8 y, 9–13 y, 14–18 y, 19–30 y, 31–50 y, 51–70 y, >70 y; sex-disaggregated from age 9; pregnancy and lactation by maternal age band.
- **Currently under revision:** NASEM is convening committees on protein (workshop announced) and on the DRI process itself ("The Dietary Reference Intakes Process: A Webinar"). No comprehensive macronutrient DRI revision since 2002–2005; vitamin D/calcium last fully revised 2011.
- **Documentation accessibility:** All DRI volumes are open-access PDFs on nap.nationalacademies.org. English; selected materials available in French via Health Canada.

#### A.2 EFSA (European Union) — Dietary Reference Values (DRVs)

- **Body:** European Food Safety Authority, Panel on Dietetic Products, Nutrition and Allergies (NDA Panel). Predecessor: Scientific Committee on Food (SCF), which set the 1993 EU values that EFSA subsequently replaced.
- **Foundational work:** 34 scientific opinions completed 2009–2019. Coverage: water, fats, carbohydrates and dietary fibre, protein, energy, plus 14 vitamins and 15 minerals. Final opinion (sodium and chloride) published September 2019, marking 10 years of work [Tier 1: EFSA 2009–2019].
- **Consolidated reference:** EFSA Journal special issue on DRVs (2018) plus the *DRV Finder* interactive tool (launched November 2018).
- **Methodology:** AR / PRI / AI / RI / UL framework. **Average Requirement (AR)** = 50% of healthy population (EFSA equivalent of US EAR). **Population Reference Intake (PRI)** = covers ~97.5% (equivalent to US RDA but often numerically different). **Adequate Intake (AI)** where AR cannot be derived. **Reference Intake range (RI)** for macronutrient distribution. **Tolerable Upper Intake Level (UL)** for safety ceiling. Detailed in EFSA NDA Panel 2010 opinion on general principles for deriving and applying DRVs.
- **Currently under revision:** Active UL re-evaluation programme covering vitamin A, vitamin B6, vitamin D, vitamin E, beta-carotene, iron, manganese, folate/folic acid, and selenium. Notable recent ULs: vitamin B6 UL lowered from 30 mg/day (2000) to 12.5 mg/day (May 2023) for adults; selenium UL set at 255 µg/day (Jan 2023); manganese 8 mg/day (Dec 2023); folate UL retained at 1,000 µg/day (Nov 2023); vitamin D UL retained at 100 µg/day (Aug 2023); iron safe level 40 mg/day for adults (June 2024); vitamin E UL retained (Aug 2024) [Tier 1: EFSA 2023–2024]. EFSA has explicitly concluded that intake of added and free sugars should be "as low as possible" (January 2022 opinion, requested by five Nordic countries).
- **Documentation accessibility:** All opinions open-access in English on efsa.europa.eu, indexed in EFSA Journal with DOIs.

#### A.3 SACN / OHID (United Kingdom) — Dietary Reference Values (DRVs) and Eatwell Guide

- **Body:** Scientific Advisory Committee on Nutrition (SACN), an independent advisory committee to the UK Office for Health Improvement and Disparities (OHID, within DHSC), and to the four UK health departments. SACN succeeded the Committee on Medical Aspects of Food and Nutrition Policy (COMA) in 2000.
- **Foundational reference:** *Dietary Reference Values for Food Energy and Nutrients for the United Kingdom* (COMA, 1991). RNI / EAR / LRNI framework: RNI covers ~97.5%, EAR covers ~50%, LRNI covers ~2.5% (lower threshold below which intake is almost certainly inadequate).
- **Major SACN revisions / topic reports:** Energy DRVs (SACN 2011); Carbohydrates and Health (SACN 2015 — set free-sugars target ≤5% of total energy and fibre at 30 g/day for adults aged 16+) [Tier 1: SACN 2015]; Saturated Fats and Health (SACN 2019 — recommended saturated fat ≤10% of total energy); Vitamin D (SACN 2016 — RNI 10 µg/day for everyone aged 4+); Salt (SACN/COMA 2003 — adult target 6 g/day salt = 2.4 g/day sodium, retained); Feeding in the First Year of Life (SACN 2018); Lower Carbohydrate Diets for Adults with Type 2 Diabetes (SACN 2021).
- **Public-facing food model:** *Eatwell Guide* (March 2016), succeeding the eatwell plate (2007) and Balance of Good Health (1994). Published by Public Health England (now OHID) using a linear-programming optimisation. No update since 2016 because SACN has not advised the underlying evidence has changed.
- **Methodology framework:** SACN's *Framework and methods for the evaluation of evidence that relates food and nutrients to health* (last updated October 2024). Code of Practice updated September 2025.
- **Currently under revision (as of April 2026):** Active SACN working groups on plant-based drinks; complementary feeding; ultra-processed foods (horizon-scanning); maternal nutrition (SMCN subgroup); infant feeding. 2026 main meeting dates: 12 March, 17–18 June, 19 November.
- **Documentation accessibility:** All SACN reports open-access in English on gov.uk.

#### A.4 NHMRC (Australia / New Zealand) — Nutrient Reference Values (NRVs) and Australian Dietary Guidelines

- **Body:** National Health and Medical Research Council (NHMRC, Australia) jointly with the New Zealand Ministry of Health.
- **Foundational reference:** *Nutrient Reference Values for Australia and New Zealand* (NHMRC/MoH 2006). Coverage: full DRI panel (energy, macronutrients, water, fibre, all vitamins and minerals) for all life stages and sexes including pregnancy and lactation. Methodology: EAR / RDI / AI / UL — the NRV uses **Recommended Dietary Intake (RDI)** as the equivalent of US RDA / EU PRI; EAR, AI, UL match US definitions but numerical values differ from NASEM in several places (e.g., iron, vitamin D) [Tier 1: NHMRC/MoH 2006].
- **Targeted updates:** Sodium and potassium values reviewed 2017 — adult sodium AI 460–920 mg/day, Suggested Dietary Target (SDT) 2,000 mg/day for adults to reduce chronic disease risk (analogous to but lower than the NASEM 2019 CDRR of 2,300 mg).
- **Public-facing dietary guidelines:** *Australian Dietary Guidelines* — 4th edition published February 2013 by NHMRC. Five core recommendations + companion *Infant Feeding Guidelines* (2012). Visual: Australian Guide to Healthy Eating plate. Per the FAO country profile, the next revision was scheduled for 2021; that revision is in progress but has slipped (no replacement edition published as of April 2026, making the active edition over a decade old).
- **Documentation accessibility:** Hosted at eatforhealth.gov.au and nrv.gov.au. English. (Note: the AU government domains were intermittently unreachable from the research environment on 2026-04-28; details corroborated via FAO country profile.)

#### A.5 Health Canada — Dietary Reference Intakes and Canada's Food Guide

- **Body:** Health Canada (federal department).
- **DRIs:** Health Canada formally adopts the NASEM/IOM DRIs (1997–2019, including the 2019 sodium/potassium update) as the Canadian reference. No independent Canadian DRI table; Canadian–US joint authorship via Health Canada participation on NASEM committees.
- **Public-facing food model:** *Canada's Food Guide* — completely revised January 2019, replacing the 2007 Eating Well with Canada's Food Guide. Major change: abandoned numerical food-group serving counts and the "milk products" group; adopted a plate visual (½ vegetables and fruits, ¼ whole grains, ¼ protein foods including plant proteins) and behavioural guidance ("Be mindful of your eating habits", "Cook more often", "Limit highly processed foods"). Underlying evidence: *Evidence Review for Dietary Guidance* (Health Canada 2015) and *Food, Nutrients and Health: Interim Evidence Update 2018* [Tier 1: Health Canada 2019].
- **Companion document:** *Canada's Dietary Guidelines* (2019) — a longer companion intended for health professionals and policymakers.
- **Documentation accessibility:** Open-access at food-guide.canada.ca and canada.ca, in English and French.

#### A.6 NNR (Nordic + Baltic) — Nordic Nutrition Recommendations 2023

- **Body:** Nordic Council of Ministers via the NNR project (national nutrition authorities of Denmark, Finland, Iceland, Norway, Sweden, plus the Faroe Islands, Greenland, Åland; in 2023 expanded to include Estonia, Latvia, Lithuania).
- **Current edition:** *Nordic Nutrition Recommendations 2023 — Integrating Environmental Aspects* (NNR2023). Predecessor: NNR 2012 (5th edition).
- **Coverage:** Full DRI panel (energy, macronutrients, fluid/water, fibre, 13 vitamins, 14 minerals) plus dedicated chapters on choline, antioxidants/phytochemicals, fluoride. Plus food-group-level recommendations: cereals, vegetables/fruits/berries, potatoes, fruit juices, pulses/legumes, nuts/seeds, fish/seafood, red meat, white meat, dairy, eggs, fats/oils, sweets, alcohol, beverages, breastfeeding, complementary feeding, dietary patterns, meal patterns, ultra-processed foods.
- **Methodology innovations:** First major DRI body to formally integrate environmental sustainability (carbon, biodiversity, planetary boundaries) into food-based dietary guidelines via science-advice papers. Required all underlying systematic reviews to be qualified per a modified AMSTAR 2 protocol. Distinct chapters on principles for setting DRVs vs. principles for FBDGs [Tier 1: NNR 2023].
- **Notable headline values:** Adult protein PRI 0.83 g/kg/day (in line with EFSA; explicit emphasis on plant-protein shift); red meat ≤350 g/week (cooked) with processed meat "as little as possible"; saturated fat <10% energy; added/free sugars <10% energy; salt 5–6 g/day (sodium ≤2 g/day for adults).
- **Documentation accessibility:** Open-access at pub.norden.org/nord2023-003 and norden.org. English (primary), with national translations via member states.

#### A.7 WHO and FAO — global recommendations

- **Bodies:** World Health Organization (Geneva); Food and Agriculture Organization of the UN (Rome); jointly via the Codex Alimentarius Commission.
- **Foundational nutrient requirements:** *FAO/WHO/UNU Human Energy Requirements* (2001/2004); *FAO/WHO Vitamin and Mineral Requirements in Human Nutrition* (2nd ed., 2004); *Protein and Amino Acid Requirements in Human Nutrition* (FAO/WHO/UNU 2007); *Fats and Fatty Acids in Human Nutrition* (FAO 2010); *Carbohydrates in Human Nutrition* (FAO/WHO 1998, with updates) [Tier 1].
- **Active WHO guideline series — public-health additions:**
  - **Free sugars:** *Guideline: Sugars intake for adults and children* (WHO 2015, ISBN 978-92-4-154902-8). Strong recommendation: ≤10% of total energy intake from free sugars; conditional further reduction to <5% [Tier 1: WHO 2015].
  - **Sodium:** *Guideline: Sodium intake for adults and children* (WHO 2012). Adults <2,000 mg/day sodium (<5 g/day salt). Updated WHO sodium fact sheet 2025 reports global mean adult intake ≈4,310 mg/day, more than double the recommendation [Tier 1: WHO 2012/2025].
  - **Potassium:** *Guideline: Potassium intake for adults and children* (WHO 2012). Adults ≥3,510 mg/day (90 mmol).
  - **Saturated and trans fat:** WHO 2023 guideline — saturated fat <10% energy, trans fat <1% energy, and an explicit goal to eliminate industrially-produced trans fat globally (REPLACE initiative, 2018–2025) [Tier 1: WHO 2023].
  - **Carbohydrate intake:** WHO 2023 carbohydrate guideline — adults and children should consume ≥400 g fruits and vegetables per day and ≥25 g naturally-occurring dietary fibre per day; carbohydrate primarily from whole grains, vegetables, fruits, and pulses [Tier 1: WHO 2023].
  - **Non-sugar sweeteners:** WHO 2023 conditional recommendation against use of non-sugar sweeteners for weight control or NCD prevention.
  - **Total fat:** ≥15% energy minimum, ≤30% energy for adults to prevent unhealthy weight gain.
  - **Healthy diet four-principle framework:** adequacy, balance, moderation, diversity (WHO 2026 revision of healthy-diet fact sheet, 26 January 2026).
- **Codex Alimentarius:** Sets internationally harmonised Nutrient Reference Values – Requirements (NRVs-R) and Nutrient Reference Values – Non-communicable Disease (NRVs-NCD) used for food labelling globally; jointly governed by FAO and WHO.
- **Documentation accessibility:** All WHO guidelines open-access at who.int in English plus the six WHO official languages (Arabic, Chinese, French, Russian, Spanish; Portuguese for many).

#### A.8 MHLW (Japan) — Dietary Reference Intakes for Japanese (DRI-J)

- **Body:** Ministry of Health, Labour and Welfare (MHLW).
- **Current edition:** *Dietary Reference Intakes for Japanese, 2025 Edition* (released 2024 for the 2025–2029 quinquennium). Previous editions: 2010, 2015, 2020. Quinquennial revision cycle is the most regular among major bodies.
- **Methodology:** EAR / RDA / AI / UL framework analogous to NASEM, plus a Japanese-specific **DG (Tentative Dietary Goal for Preventing Lifestyle-Related Diseases)** and **EER (Estimated Energy Requirement)** stratified by physical-activity level. Notable Japan-specific considerations: lower body weight reference standards than Western references; sodium DG aggressively low (2024 edition 6.5 g salt/day for adult women, 7.0 g for adult men, lower for hypertensive populations) reflecting Japan's high-salt cuisine baseline; protein PRI accounts for plant-protein-heavy patterns.
- **Public-facing food model:** *Japanese Food Guide Spinning Top* (食事バランスガイド) — co-developed by MHLW and the Ministry of Agriculture, Forestry and Fisheries (MAFF), published 2005, revised 2010 in lockstep with the DRI revision. Inverted-cone visual organised by recommended servings: grains > vegetables > fish/eggs/meat > milk and fruit. Includes a runner figure to denote physical activity. Companion: *Dietary Guidelines for Japanese* (食生活指針), 10 messages, originally 2000, revised 2016 [Tier 1: MHLW 2010/2016/2024].
- **Documentation accessibility:** MHLW publishes in Japanese (primary). The DRI-J 2020 has been published in English by Tokyo University Press; 2025 English translation forthcoming. FAO maintains an English summary on its country FBDG page.

#### A.9 ICMR-NIN (India) — RDA / EAR and Dietary Guidelines

- **Body:** Indian Council of Medical Research – National Institute of Nutrition (Hyderabad). The 1925-founded NIN is India's premier nutrition research institute.
- **Current DRI publication:** *Nutrient Requirements for Indians — Recommended Dietary Allowances (RDA) and Estimated Average Requirements (EAR)* (ICMR-NIN 2020), with summary updates in 2024.
- **Public-facing:** *Dietary Guidelines for Indians* — 2024 edition released (ICMR-NIN, May 2024), replacing the 2011 edition (which itself replaced the 1998 first edition). Visual: food pyramid (cereals/legumes base → vegetables/fruits → animal foods/oils → highly-processed foods at apex) plus *My Plate for the Day*. Published in English, Hindi, and Telugu.
- **Methodology:** EAR / RDA / TUL framework. Indian-specific reference body weights (lower than Western references); explicit accommodation of vegetarian dietary patterns common in India (separate iron/zinc bioavailability factors for vegetarian vs. non-vegetarian patterns); calcium RDA notably higher than EFSA (1,000 mg/day for adults) due to low dairy intake patterns; protein RDA of 0.83–1.0 g/kg/day with adjustments for cereal-pulse digestibility.
- **Companion outputs:** *What India Eats* (national dietary intake report); *Indian Food Composition Tables (IFCT) 2017*; nutrient atlas; *Let's Fix Our Food* policy brief; sugar/fat consumption surveys (NNMB) [Tier 1: ICMR-NIN 2020/2024].
- **Documentation accessibility:** Open-access at nin.res.in. English (primary), Hindi, Telugu.

#### A.10 Chinese Nutrition Society — DRIs and Chinese Dietary Guidelines

- **Body:** Chinese Nutrition Society (CNS), authorised by the National Health Commission of the People's Republic of China and the Ministry of Agriculture and Rural Affairs.
- **Current DRI publication:** *Chinese Dietary Reference Intakes* (CDRI) — 2023 edition (CNS 2023), revising the 2013 edition. Methodology uses EAR / RNI / AI / UL plus China-specific **PI-NCD (Proposed Intake for Preventing Non-Communicable Disease)** and **SPL (Specific Proposed Level)** for nutrients with chronic-disease relevance — analogous in spirit to NASEM's CDRR.
- **Public-facing:** *Dietary Guidelines for Chinese 2022* (5th edition; previous editions 1989, 1997, 2007, 2016). Eight core recommendations published in popular and professional editions. Visuals: Chinese Food Pagoda (six tiers), supplementary Food Plate, and a children-oriented Food Abacus. The CNS published technical reports on the revision process and on dietary guidelines from other countries, explicitly drawing on FAO/WHO and other national bodies' approaches [Tier 1: CNS 2022/2023].
- **Public-health priority:** China's National Nutrition Plan 2017–2030 includes salt-reduction targets aligned with WHO (<5 g/day) and explicit edible-oil reduction targets.
- **Documentation accessibility:** Mandarin (primary). Selected materials translated into English for the FAO repository and academic publishing. Underlying CDRI 2023 not yet released in full English translation; English summaries in indexed nutrition journals.

#### A.11 Brazilian Ministry of Health — Dietary Guidelines for the Brazilian Population

- **Body:** Brazilian Ministry of Health (Ministério da Saúde) in partnership with the Center for Epidemiological Research in Nutrition and Health of the University of São Paulo (NUPENS/USP) and PAHO/Brazil.
- **Current edition:** *Guia alimentar para a população brasileira* (2nd edition, 2014; first edition 2006). Companion: *Guia alimentar para crianças brasileiras menores de 2 anos* (2019).
- **Methodology innovation — globally influential:** First national dietary guideline to organise advice around degree of food processing rather than nutrient targets, using the **NOVA classification** (unprocessed/minimally processed; processed culinary ingredients; processed foods; ultra-processed foods). Core recommendation: make natural or minimally-processed foods the basis of the diet; avoid ultra-processed foods. Includes explicit advice on cooking, eating environment, eating in company, and resisting food advertising — making it the first major guideline to formally integrate the social and behavioural determinants of eating into authoritative guidance [Tier 1: Ministry of Health Brazil 2014]. The NOVA-based framing has since been cited by FAO, WHO, and informed Canada's 2019 guide and Uruguay's 2016 guide.
- **Brazil does not publish a numerical food-group plate or pyramid;** the guidance is qualitative and behavioural ("Ten Steps to a Healthy Diet").
- **Documentation accessibility:** Portuguese (primary) and English translation available via Ministry of Health and PAHO.

#### A.12 Other notable bodies (opportunistic)

- **Germany — DGE (German Nutrition Society / Deutsche Gesellschaft für Ernährung):** *Eat and Drink Well — DGE Recommendations* (Gut essen und trinken — Die DGE-Empfehlungen) revised 2024 (the 18th revision since 1955). Major methodological innovation: the 2024 revision used a mathematical optimisation model that explicitly incorporates environmental sustainability dimensions for the first time. DGE Nutrition Circle (Ernährungskreis) is the visual food guide [Tier 1: DGE 2024].
- **France — ANSES + Santé Publique France:** PNNS *Recommandations alimentaires* — 2019 revision for adults; 2021 for children/adolescents; 2022 for elderly and pregnant. Underlying scientific reports from ANSES (2016) and HCSP (2017). First French guidelines to incorporate environmental sustainability (encouraging local, seasonal, organic where possible; reducing meat).
- **Netherlands — Health Council (Gezondheidsraad):** *Guidelines for a healthy diet 2015* (Richtlijnen goede voeding 2015), with biennial topic updates; underpins the *Schijf van Vijf* (Wheel of Five) public food guide from the Voedingscentrum.
- **Belgium — Conseil Supérieur de la Santé / Hoge Gezondheidsraad:** *Food-Based Dietary Guidelines for the Belgian Adult Population* (2019) with Food Triangle (Voedingsdriehoek).
- **Switzerland — Federal Food Safety and Veterinary Office (FSVO/BLV):** Swiss Food Pyramid (Schweizer Lebensmittelpyramide), most recent update 2024, jointly with Swiss Society for Nutrition (SGE/SSN). DACH reference values shared with Germany and Austria.
- **Austria — Austrian Nutrition Society (ÖGE):** Austrian Food Pyramid (Österreichische Ernährungspyramide). Uses DACH reference values jointly with Germany and Switzerland.
- **Ireland — FSAI / Department of Health:** *Healthy Eating Guidelines* and *Food Pyramid* (Department of Health 2016, retained).
- **Spain — SENC (Sociedad Española de Nutrición Comunitaria):** Spanish Dietary Guidelines (Guías alimentarias) and Mediterranean-pattern Healthy Eating Pyramid (latest 2022).
- **Italy — CREA (Council for Agricultural Research and Economics):** *Linee Guida per una sana alimentazione* (Italian Dietary Guidelines) — 2018 revision; underlies the Italian Mediterranean pyramid. CREA also publishes LARN (Livelli di Assunzione di Riferimento di Nutrienti) — Italian DRIs, latest 4th revision 2014.
- **Portugal — DGS (Directorate-General of Health):** Portuguese Mediterranean Food Wheel (Roda dos Alimentos Mediterrânica), 2016.
- **Greece — Ministry of Health:** Greek National Dietary Guidelines (latest comprehensive set 2014) using a Mediterranean pyramid; foundational source for Mediterranean-diet definitions.
- **Korea — Ministry of Health and Welfare + Korean Nutrition Society:** *Dietary Reference Intakes for Koreans (KDRIs)* — most recent edition 2020. *Dietary Guidelines for Koreans* 2021.
- **Israel — Ministry of Health:** Israeli Nutritional Recommendations and the *Israeli Mediterranean Plate* (2019).
- **Russia — Federal Service for Surveillance on Consumer Rights Protection (Rospotrebnadzor):** *Norms of Physiological Requirements in Energy and Nutrients for Various Population Groups of the Russian Federation* (MR 2.3.1.0253-21, 2021 revision).
- **Mexico — Secretaría de Salud:** *Guías Alimentarias y de Actividad Física* (latest 2023) with Plato del Bien Comer; pioneered front-of-pack warning labels for sugar/sodium/saturated-fat (2020).
- **Argentina — Ministerio de Salud:** *Guías Alimentarias para la Población Argentina* (GAPA, 2016) with food-group oval graphic.
- **Uruguay — Ministerio de Salud Pública:** Dietary Guidelines for the Uruguayan Population (2016) — second NOVA-based guideline globally after Brazil.
- **Chile — Ministerio de Salud:** Dietary Guidelines (2013) plus pioneering 2016 front-of-pack warning labels (high in sugar / sodium / saturated fat / calories).
- **South Africa — Department of Health + NDoH:** South African Food Based Dietary Guidelines (FBDG) 2013, with Food Guide.
- **Singapore — Health Promotion Board:** *Recommended Dietary Allowances* and *My Healthy Plate*.
- **Caribbean — CARPHA (Caribbean Public Health Agency):** *Caribbean Food-Based Dietary Guidelines* (regional, 2017).
- **FAO global repository:** FAO maintains country-by-country FBDG profiles for ~100 countries (Africa, Asia/Pacific, Europe, Latin America/Caribbean, Near East, North America). This repository is the practical starting point for any country not enumerated above [Tier 1: FAO 2026].

### B. Comparative notes — where bodies materially diverge

Caveats: ranges below summarise adult, non-pregnant, non-lactating values for the most-cited reference age band (typically 19–50 y, sometimes ≥18 or ≥19). All values are tagged Tier 1 (authoritative-body publication). Material divergence is defined as ≥15–20% gap or qualitatively different framing.

| Nutrient / target | NASEM (US/Can) | EFSA (EU) | SACN (UK) | NHMRC (AU/NZ) | NNR 2023 | WHO/FAO | MHLW (Japan) | ICMR-NIN (India) | CNS (China) | Material divergence note |
|---|---|---|---|---|---|---|---|---|---|---|
| Protein, adult | RDA 0.8 g/kg | PRI 0.83 g/kg | RNI 0.75 g/kg | RDI 0.84 g/kg M, 0.75 g/kg F | PRI 0.83 g/kg | safe intake 0.83 g/kg | RDA ≈0.9 g/kg | RDA 0.83 g/kg (with quality factor for cereal-pulse diets) | RNI 0.9 g/kg | Largely converged 0.75–0.9 g/kg. The "should be higher for older adults" debate (Bauer et al., PROT-AGE) is partially absorbed by some bodies (NNR2023, MHLW) and not by NASEM. |
| Carbohydrate, % energy | AMDR 45–65% | RI 45–60% | ~50% | 45–65% | 45–60% | ~45–75% | ~50–65% | 50–60% | 50–65% | WHO range is widest (especially upper bound). Low-carb framing differs: SACN 2021 acknowledges therapeutic low-carb for T2D; NASEM does not. |
| Total fat, % energy | AMDR 20–35% | RI 20–35% | ≤35% | 20–35% | 25–40% | 15–30% (adults) | 20–30% | 20–30% | 20–30% | NNR 2023 upper bound 40%; WHO upper 30%. >10 percentage-point gap. |
| Saturated fat | <10% | "as low as possible" | ≤10% (≤11% pop avg) | ≤10% | <10% | <10% | <7% (DG) | ≤10% | <10% | Japan most aggressive; EFSA explicitly avoids a numerical UL. |
| Trans fat | minimise | "as low as possible" | ≤2% | minimise | minimise | <1% (industrial: eliminate) | minimise | minimise | minimise | All converge directionally; WHO's REPLACE elimination target is the most action-oriented. |
| Free / added sugars | ≤10% (DGA 2020-25); not formally a DRI | "as low as possible" (EFSA 2022) | ≤5% (SACN 2015) | ≤10% (SDT) | <10% | ≤10% (cond. <5%) | ≤10% (target) | ≤5–10% | ≤10% | UK strictest at 5%; EFSA most cautious framing; NASEM has no formal DRI for added sugars (2010 DGAC recommended ≤10%, codified in DGA). |
| Fibre, adult | AI 38 g M / 25 g F | AI 25 g | 30 g | AI 30 g M / 25 g F | 25–35 g | ≥25 g | 21 g M / 18 g F | 40 g/2000 kcal | 25–30 g | NASEM is the outlier high (38 g for men); MHLW Japan and EFSA cluster lower. >50% spread. |
| Sodium, adult ceiling | CDRR 2,300 mg (NASEM 2019) | safe range cap not set; AI 2,000 mg | 2,400 mg (6 g salt) | SDT 2,000 mg | <2,000 mg | <2,000 mg | DG 2,600 mg M / 2,000 mg F | <2,000 mg | <2,000 mg | NASEM CDRR 2,300 is the highest "ceiling" published; most other bodies converge at 2,000 mg WHO target. Japan accepts higher male target reflecting cuisine baseline. |
| Potassium, adult AI | 3,400 mg M / 2,600 mg F (NASEM 2019; lowered from 4,700) | AI 3,500 mg | 3,500 mg | AI 3,800 M / 2,800 F | 3,500 mg | ≥3,510 mg | DG ≥3,000 mg | 3,500 mg | 2,000 mg EAR | NASEM 2019 substantially lowered prior 4,700 mg AI based on absence of high-quality evidence supporting the higher target — a notable methodological reset. |
| Calcium, adult | RDA 1,000 mg (19–50) / 1,200 mg (>50 F, >70 M) | PRI 950 mg | RNI 700 mg | RDI 1,000–1,300 mg | 950 mg | 1,000 mg | RDA 650–800 mg | RDA 1,000 mg | RNI 800 mg | UK RNI is the lowest at 700 mg; NASEM and India highest at 1,000 mg. >40% spread reflects different bioavailability assumptions and bone-disease evidence interpretation. |
| Iron, premenopausal F | RDA 18 mg | PRI 16 mg | RNI 14.8 mg | RDI 18 mg | PRI 15 mg | 19.6 mg (15% bioavail.) | RDA 10.5 mg | RDA 21 mg (vegetarian) / 15 mg (mixed) | RNI 18 mg | India highest reflecting low-bioavailability vegetarian baseline; Japan lowest reflecting menstrual-loss assumptions and population data. |
| Vitamin D, adult | RDA 15 µg (600 IU) | AI 15 µg | RNI 10 µg (year-round) | AI 5 µg (sun-exposed) | 10 µg | adequate sun + 5–15 µg | AI 8.5 µg | RDA 15 µg (limited sun) | RNI 10 µg | NASEM/EFSA at 15 µg; UK lowered to 10 µg year-round 2016; AU/NZ assumes sun exposure. ~3× spread. |
| Vitamin B6 UL, adult | 100 mg | 12.5 mg (EFSA 2023, lowered from 30) | not set | 50 mg | 25 mg | not set | 60 mg | 100 mg | not set | EFSA 2023 lowered UL by ~60% citing peripheral-neuropathy evidence — an 8× divergence from NASEM. |
| Iron UL, adult | 45 mg | 40 mg "safe level" (EFSA 2024) | not set | 45 mg | 25–40 mg | not set | 40–55 mg | not set | not set | EFSA shifted from UL to "safe level" framing in 2024. |
| Zinc UL, adult | 40 mg | 25 mg | 25 mg | 40 mg | 25 mg | not set | 35–45 mg | not set | 40 mg | NASEM and AU/NZ 60% higher than EFSA/UK. |

Material divergences worth surfacing in the product (per Constitutional Rule 9 and Rule 1):
- **Fibre:** NASEM (38 g M) vs MHLW (21 g M) is a >75% spread. Significant for product defaults.
- **Free sugars:** SACN 5% vs WHO conditional 5% vs DGA 10% vs EFSA "as low as possible" — the same evidence base, different interpretive thresholds.
- **Calcium:** UK RNI 700 mg vs NASEM RDA 1,000 mg vs India 1,000 mg — bioavailability + bone-evidence interpretation gap.
- **Sodium:** NASEM 2019 explicitly walked back from a UL to a CDRR (2,300 mg) and rejected setting a hard sodium UL because it could not establish a no-adverse-effect level — a methodological position other bodies have not adopted.
- **Vitamin B6 UL:** EFSA 2023 12.5 mg vs NASEM 100 mg — an 8× spread reflecting differential weighting of peripheral-neuropathy evidence.
- **Total fat upper bound:** NNR 40% vs WHO 30% — driven by Mediterranean/Nordic dietary-pattern evidence (high MUFA/PUFA acceptable) vs WHO weight-gain prevention framing.

### C. Dietary pattern guidance per body

Patterns published as authoritative (Tier 1) named patterns:

- **US — DGA 2020–2025:** Three named patterns: (i) Healthy U.S.-Style; (ii) Healthy Mediterranean-Style; (iii) Healthy Vegetarian. Each modelled at multiple energy levels with food-group serving recommendations. Companion: **MyPlate** (USDA, 2011 and ongoing) graphical tool [Tier 1: USDA-HHS 2020].
- **US (academic + clinical) — DASH:** *Dietary Approaches to Stop Hypertension* — NHLBI clinical eating plan, last updated to current site Feb 2026. 2,000 kcal modelled day with sodium 2,300 mg (lower target 1,500 mg). Underlying RCTs published 1997–2001; supported as Tier 1 by AHA, ACC, JNC blood pressure guidelines [Tier 1: NHLBI 2026; underlying Tier 2: Appel et al. NEJM 1997, Sacks et al. NEJM 2001].
- **US (academic) — MIND diet:** Mediterranean-DASH Intervention for Neurodegenerative Delay. Originated with Morris et al. 2015 Rush University. Not endorsed by USDA but cited in DGA-2020 dietary-pattern review and AHA materials. 15 dietary components scored; intervention RCT (MIND-NIH) results published 2023. [Tier 2/3: Morris et al. Alzheimers Dement 2015; Barnes et al. NEJM 2023].
- **Mediterranean diet — multiple national pyramids:** Greek (Ministry of Health 2014), Italian (CREA + Mediterranean Diet Foundation 2009 / 2014), Spanish (SENC 2022), Portuguese (Mediterranean Wheel 2016). UNESCO Intangible Cultural Heritage 2010 (Cyprus, Croatia, Greece, Italy, Morocco, Portugal, Spain). Underlying clinical trial: PREDIMED (Estruch et al. NEJM 2013, retracted/republished 2018).
- **Nordic diet pattern — NNR 2023:** A Nordic-specific healthy diet pattern (whole grains especially rye/oats/barley, root vegetables, berries, fish, rapeseed oil, low-fat dairy, game/lean meats, low red/processed meat). RCT support: Nordic Diet (NORDIET, SYSDIET). Distinct from Mediterranean.
- **Japanese spinning top (Shokuji Balance Guide):** MHLW + MAFF 2005, revised 2010. Quantitative servings per food group on a spinning-top visual.
- **Brazilian guidelines (NOVA-based):** Qualitative pattern centred on minimally-processed foods; discourages ultra-processed foods. Not pyramid/plate; behavioural ten-step format [Tier 1].
- **EAT-Lancet Planetary Health Diet (2019; updated 2025):** Willett et al., *Food in the Anthropocene*, Lancet 2019. Quantitative reference diet (~2,500 kcal): emphasises plant foods, allows modest animal products. 2025 EAT-Lancet Commission report released (Willett et al., Lancet 2025) updating science and noting food systems now breach planetary boundaries [Tier 1 for the Commission outputs as authoritative scientific consensus; Tier 2 for the underlying RCTs/cohorts].
- **Healthy Eating Plate (Harvard T.H. Chan School of Public Health, 2011):** Explicitly differentiates from MyPlate (no dairy default; whole grains; healthy oils; activity). Academic, not government — Tier 1-adjacent based on Harvard NHS/HPFS cohort base [Tier 2 for cohort evidence; Tier 4 for the plate graphic alone].
- **Eatwell Guide (UK PHE/OHID 2016):** Five food groups by proportion (fruit/veg 39%, starchy carbs 37%, dairy/alternatives 8%, protein foods 12%, oils/spreads 1%, plus "eat less" segment). Linear-programming derived from UK DRVs.
- **Canada's Food Guide plate (Health Canada 2019):** Half plate vegetables/fruits, quarter whole grains, quarter protein foods (plant proteins explicitly equal to animal proteins). Behavioural elements: cook more often, eat with others, be mindful, limit ultra-processed.
- **DACH (Germany/Austria/Switzerland):** DGE Nutrition Circle (Ernährungskreis) 7-segment circle (Germany 2024 update); Swiss Food Pyramid (2024); Austrian Food Pyramid.
- **Indian food pyramid (ICMR-NIN 2024):** Four-tier (cereals/legumes base → vegetables/fruits → animal foods/oils → highly-processed apex) plus *My Plate for the Day*.
- **Chinese Food Pagoda (CNS 2022):** Six-tier pagoda + Food Plate + Food Abacus (children).
- **Okinawan diet:** Traditional regional pattern, not formally codified as a guideline by Japanese MHLW; characterised by sweet potato as staple, low caloric density, high vegetable/legume intake, low animal protein. Cohort evidence: Willcox et al., Okinawa Centenarian Study [Tier 3 cohort evidence for longevity associations; Tier 4 for popular diet-book versions of the pattern].
- **Mediterranean variants outside Mediterranean:** PREDIMED, Lyon Diet Heart Study cohorts. Several non-Mediterranean countries (UK, US DGA, Canada, Australia) endorse Mediterranean-style as one option among several.
- **Traditional Andean, Sub-Saharan, South Asian patterns:** Not currently codified as pattern-level authoritative guidance by WHO/FAO; descriptions exist in academic literature [Tier 3].

### D. Public-health additions per body

| Topic | NASEM/USDA | EFSA | SACN/PHE | NHMRC | NNR 2023 | WHO | MHLW | ICMR-NIN | CNS |
|---|---|---|---|---|---|---|---|---|---|
| Added/free sugars cap | DGA 10% energy | "as low as possible" (2022) | ≤5% energy (2015) | SDT, ≤10% | <10% | ≤10% (cond. <5%) | ≤10% target | ≤5-10% | ≤10% (50 g/day) |
| Sodium ceiling adults | CDRR 2,300 mg | AI 2,000 mg / no UL | 2,400 mg (6 g salt) | SDT 2,000 mg | <2,000 mg (5–6 g salt) | <2,000 mg | DG 6.5–7 g salt | <2,000 mg | <2,000 mg (Healthy China 2030) |
| Alcohol guidance | DGA: men ≤2 / women ≤1 drink/day; no recommendation to start | EFSA: AR not set, no safe level | UK CMO: ≤14 units/week (2016) | NHMRC 2020: ≤10 std drinks/wk and ≤4/day | NNR 2023: as low as possible; ≤10 g/day if at all | WHO 2023: no safe level (Lancet Public Health 2023) | DG: ≤20 g ethanol/day M, less F | Avoid (cited in 2024 guidelines) | ≤25 g/day M, ≤15 g F |
| Ultra-processed foods | DGA 2020-25 acknowledges; not a formal target | Watching brief | SACN 2023 horizon scan; UPF working group active | Not explicit category | NNR 2023: dedicated UPF chapter (limit) | WHO/PAHO recommend reducing | Not explicit | 2024 DGI: explicit "minimise UPF" advice | 2022: "limit UPF" |
| Trans fat | DGA: minimise; FDA banned PHO 2018 | EFSA 2009: <1%; EU regulation 2% cap (2021) | <2% energy (2007 onward) | minimise | <1% energy | <1% energy; REPLACE (eliminate by 2025) | minimise | minimise; 2% industrial cap | minimise; PHO restrictions |
| Saturated fat | <10% energy (DGA) | "as low as possible" (no UL) | ≤10% (SACN 2019) | ≤10% | <10% | <10% | <7% target | ≤10% | <10% |
| Front-of-pack labels | FDA voluntary "Facts up Front"; warning labels not adopted federally | EU Nutri-Score recommended in some MS (FR/BE/DE/NL/ES/CH/LU); Italy opposes (NutrInform Battery) | UK voluntary traffic-light label (FSA 2013) | AU/NZ Health Star Rating (voluntary, 2014) | Nordic Keyhole (Keyhole label, since 1989) | WHO supports FoP labelling | Nutrient labelling mandatory; no warning system | FoPL in development (FOPNL pilot, 2024) | Voluntary nutrient declaration |

### E. Documentation accessibility — English-language coverage matrix

| Body | Primary language | English availability | Translation needed for ingestion |
|---|---|---|---|
| NASEM | English | Native | None |
| EFSA | English | Native (EU multilingual summaries) | None |
| SACN/PHE | English | Native | None |
| NHMRC AU/NZ | English | Native | None |
| Health Canada | English/French | Native both | None |
| NNR 2023 | English (Nordic) | Native English (with national translations) | None |
| WHO/FAO | English (six UN languages) | Native | None |
| MHLW Japan | Japanese | Partial — DRI-J 2020 English ed. via Tokyo Univ Press; FAO summary in English; 2025 ed. forthcoming in EN | Yes for current edition + supporting tables |
| ICMR-NIN | English/Hindi/Telugu | Native English (primary scientific publication) | None |
| Chinese Nutrition Society | Mandarin | Limited; FAO summary + journal articles | Yes for full CDRI 2023 tables |
| Brazilian MoH | Portuguese | English translation available (2014 guideline, PAHO) | None for guidelines; partial for technical annexes |
| DGE Germany | German | Limited (FAO summary + DGE English fact sheets) | Yes for full 2024 derivation report |
| ANSES / Santé Publique France | French | Limited | Yes for technical reports |
| KDRIs (Korea) | Korean | Limited (English summary in journals) | Yes |
| Russia (Rospotrebnadzor) | Russian | Limited | Yes |
| Mexico / Argentina / Chile / Uruguay | Spanish | Variable; PAHO publishes some in English | Partial |
| FAO country FBDG repository | English | Native; covers ~100 countries | None for the FAO summary; original-language for the underlying national document |

### F. Answers to the open research questions

**Q1: Which non-Western standards bodies have publicly accessible English-language documentation? Which require translation?**

- **English natively or strong English mirror:** ICMR-NIN (India), MHLW (partial — DRI-J 2020 in English, 2025 forthcoming), Brazilian MoH (full English translation of the 2014 guideline), KDRIs (English summary), ANZ NHMRC (English).
- **English summary via FAO + national-language original:** Chinese Nutrition Society, DGE (Germany), ANSES (France), most Latin American bodies, Nordic national bodies (where NNR 2023 in English replaces national-language detail).
- **Translation needed for full ingestion:** Chinese CDRI 2023 detailed tables; MHLW DRI-J 2025 (until English edition); German DGE 2024 derivation tables; Russian MR 2.3.1.0253-21; full national tables for many smaller-population bodies tracked only in FAO summaries.

**Q2: Where do bodies materially disagree on macronutrient or micronutrient targets, and what is the scientific basis for disagreement?**

Documented in section B comparative table. Key materially divergent positions:
- **Fibre 21 g (Japan) vs 38 g (NASEM):** NASEM derived from cardiovascular outcomes in US/Canadian cohorts (Pereira et al.), MHLW from Japanese intake-distribution data and lower body weight references.
- **Vitamin B6 UL 12.5 mg (EFSA 2023) vs 100 mg (NASEM 2010):** EFSA re-weighted peripheral-neuropathy case reports and observational studies; NASEM has not re-opened the UL.
- **Sodium CDRR 2,300 mg (NASEM 2019) vs 2,000 mg (WHO/most others):** NASEM rejected setting a hard UL because the chronic-disease evidence shows continuous risk reduction with no clear inflection — a different evidentiary stance, not a different value preference.
- **Calcium RNI 700 mg (UK) vs 1,000 mg (NASEM/India):** UK SACN re-evaluated bone-fracture evidence and concluded higher intakes don't deliver proportional benefit; NASEM retained the higher value based on bone density as primary indicator.
- **Total fat 30% (WHO) vs 40% (NNR):** WHO weight-gain prevention framing vs NNR Mediterranean/Nordic dietary-pattern modelling allowing higher MUFA/PUFA.
- **Free sugars 5% (SACN, WHO conditional) vs 10% (NASEM, most others):** Same Cochrane/Te Morenga 2013 evidence base; different threshold for "strong" vs "conditional" recommendation.
- **Iron premenopausal women 10.5 mg (Japan) vs 21 mg (India vegetarian):** Bioavailability assumptions differ by population dietary pattern (heme/non-heme split).

**Q3: Which bodies have the most current evidence reviews vs. decades-old assumptions?**

- **Most current (2023–2025 cycle):** NNR 2023 (full revision); EFSA UL re-evaluation programme (2023–2024 active); ICMR-NIN 2024 dietary guidelines; CNS 2022 dietary guidelines + 2023 CDRI; MHLW 2025 DRI-J; DGE Germany 2024.
- **Mid-currency (2018–2022):** Brazil (2014 + 2019 child supplement); Health Canada (2019); EAT-Lancet 2019 + 2025; SACN topic reports (sat fat 2019, T2D 2021).
- **Aging substantially (>10 years for primary tables):** NASEM macronutrient DRIs (2002–2005, no update); NHMRC NRV (2006 with 2017 sodium/K patch — overall framework now 20 years old); Mediterranean national pyramids (mostly 2009–2016).

**Q4: Which bodies publish dietary pattern guidance vs. only nutrient-level DRIs?**

- **Both (nutrient + pattern):** USDA-HHS DGA, Health Canada, NHMRC, MHLW (DRI-J + Spinning Top), CNS, ICMR-NIN, NNR 2023 (most integrated example), DGE Germany, French PNNS, all Mediterranean national bodies.
- **Nutrient-level only:** NASEM (DRIs only — pattern guidance is delegated to USDA via DGA); EFSA (DRVs only — pattern guidance is delegated to EU Member States); SACN (DRVs only — pattern guidance is delegated to OHID via Eatwell Guide).
- **Pattern-only or pattern-led:** Brazilian Ministry of Health (NOVA-based, intentionally not nutrient-led); EAT-Lancet (planetary pattern; not a national authority).

**Q5: How do bodies handle sub-populations not well-represented in their underlying evidence base?**

- **Older adults (>70):** Most bodies use the 51–70 / >70 stratification but base values on younger-adult studies extrapolated. NNR 2023 explicitly notes evidence gaps for >75. PROT-AGE 2013 advocates raising older-adult protein to 1.0–1.2 g/kg; partially adopted by NNR 2023 and MHLW; not by NASEM.
- **Pregnant/lactating:** All major bodies stratify by pregnancy trimester and lactation stage; values typically extrapolated from non-pregnant + factorial increments, not direct trial evidence.
- **Children:** Most bodies stratify by age band; vitamin D and iron are most actively re-evaluated (EFSA 2018 vit D in infants; iron in infants 2024).
- **Race/ethnicity:** Generally not explicitly stratified by major bodies. NASEM 2019 sodium DRI explicitly noted Black populations may be more salt-sensitive but did not set a separate value. WHO recommends no race-based DRIs.
- **Vegetarians/vegans:** ICMR-NIN explicitly publishes vegetarian-specific iron and zinc; CNS publishes vegetarian-specific advice; Health Canada 2019 treats plant proteins as equivalent without separate values; most other bodies note bioavailability adjustments without separate tables.
- **Body-size / weight reference:** MHLW and ICMR-NIN use lower reference body weights than NASEM/EFSA/NHMRC, producing systematically lower per-day intake values; a structural source of divergence.

### G. Out-of-scope finds worth noting (deferred to other sweeps)

- **Codex Alimentarius NRVs (FAO/WHO joint):** International labelling reference values used for nutrition fact panels in countries without their own — relevant to sweep #4 (regulatory) and sweep #2 (food composition / labelling).
- **NOVA classification controversies:** Active scientific debate (Forde et al., Hall et al., Monteiro et al.) about the definition and health-attribution of UPF as a category — relevant to sweep #4 (evidence audits) and the audit-as-education pattern.
- **EAT-Lancet pushback:** Substantial scientific critique of EAT-Lancet 2019 nutrient adequacy especially iron/B12/calcium for children and pregnant women (Beal et al., Adesogan et al.) — relevant to sweep #4 and sweep #10 (clinical condition gating).
- **Personalised-nutrition challenge to population DRIs:** Zoe/PREDICT (Berry et al., Asnicar et al. Nat Med 2020), Israeli Personalised Nutrition Project (Zeevi et al., Cell 2015) argue population DRIs miss inter-individual response variance — defer to sweep #5 (personalized nutrition evidence audit).
- **DRI-vs-USDA-DGA divergence within the US:** The DGA does not always align with NASEM DRIs (e.g., added sugars 10% in DGA, not in DRI; sodium 2,300 in DGA, CDRR in DRI) — informational note for sweep #8.

## References

> All references accessed 2026-04-28 unless otherwise noted. Tier labels per [evidence-tiers.md](../00-meta/evidence-tiers.md).

### Authoritative bodies — DRIs / DRVs / NRVs / RNIs

> **NASEM** (1997–2005). *Dietary Reference Intakes (eight-volume series)*. National Academies of Sciences, Engineering, and Medicine, Food and Nutrition Board. https://www.nationalacademies.org/our-work/summary-report-of-the-dietary-reference-intakes. Accessed 2026-04-28. [Tier 1]

> **NASEM** (2006). *Dietary Reference Intakes: The Essential Reference for Dietary Planning and Assessment*. National Academies of Sciences, Engineering, and Medicine. https://www.nationalacademies.org/our-work/summary-report-of-the-dietary-reference-intakes. Accessed 2026-04-28. [Tier 1]

> **NASEM** (2019). *Dietary Reference Intakes for Sodium and Potassium*. National Academies of Sciences, Engineering, and Medicine. https://nap.nationalacademies.org/catalog/25353/dietary-reference-intakes-for-sodium-and-potassium. Accessed 2026-04-28. [Tier 1]

> **EFSA** (2010–2019). *Scientific opinions on Dietary Reference Values* (34-opinion series). European Food Safety Authority Panel on Dietetic Products, Nutrition and Allergies (NDA). https://www.efsa.europa.eu/en/topics/topic/dietary-reference-values. Accessed 2026-04-28. [Tier 1]

> **EFSA** (2017). *Dietary Reference Values for nutrients: Summary report*. EFSA Supporting Publication 2017:e15121. https://doi.org/10.2903/sp.efsa.2017.e15121. [Tier 1]

> **EFSA** (2022). *Scientific opinion on the tolerable upper intake level for dietary sugars*. EFSA Journal 20(2):7074. https://doi.org/10.2903/j.efsa.2022.7074. [Tier 1]

> **EFSA** (2023). *Scientific opinion on the tolerable upper intake level for vitamin B6*. EFSA Journal 21(5):8006. https://doi.org/10.2903/j.efsa.2023.8006. [Tier 1]

> **EFSA** (2023). *Scientific opinion on the tolerable upper intake level for selenium*. EFSA Journal 21(1):7704. https://doi.org/10.2903/j.efsa.2023.7704. [Tier 1]

> **EFSA** (2024). *Scientific opinion on the tolerable upper intake level for iron*. EFSA Journal 22(6):8819. https://doi.org/10.2903/j.efsa.2024.8819. [Tier 1]

> **SACN** (1991). *Dietary Reference Values for Food Energy and Nutrients for the United Kingdom* (Report of the Panel on Dietary Reference Values of COMA). HMSO. [Tier 1]

> **SACN** (2015). *Carbohydrates and Health*. The Stationery Office. https://www.gov.uk/government/publications/sacn-carbohydrates-and-health-report. Accessed 2026-04-28. [Tier 1]

> **SACN** (2016). *Vitamin D and Health*. https://www.gov.uk/government/publications/sacn-vitamin-d-and-health-report. Accessed 2026-04-28. [Tier 1]

> **SACN** (2019). *Saturated Fats and Health*. https://www.gov.uk/government/publications/saturated-fats-and-health-sacn-report. Accessed 2026-04-28. [Tier 1]

> **SACN** (2024, October update). *Framework and methods for the evaluation of evidence that relates food and nutrients to health*. https://www.gov.uk/government/groups/scientific-advisory-committee-on-nutrition. Accessed 2026-04-28. [Tier 1]

> **NHMRC and Ministry of Health (NZ)** (2006, with 2017 sodium/potassium update). *Nutrient Reference Values for Australia and New Zealand*. National Health and Medical Research Council. https://www.nrv.gov.au/. [Tier 1]

> **NHMRC** (2013). *Australian Dietary Guidelines* (4th ed.). https://www.eatforhealth.gov.au/guidelines. [Tier 1]

> **Health Canada** (2019). *Canada's Food Guide* and *Canada's Dietary Guidelines*. https://food-guide.canada.ca/en/. Accessed 2026-04-28. [Tier 1]

> **Nordic Council of Ministers** (2023). *Nordic Nutrition Recommendations 2023 — Integrating Environmental Aspects*. NORD 2023:003. https://pub.norden.org/nord2023-003/. Accessed 2026-04-28. [Tier 1]

> **WHO** (2015). *Guideline: Sugars intake for adults and children*. World Health Organization. ISBN 978-92-4-154902-8. https://www.who.int/publications/i/item/9789241549028. Accessed 2026-04-28. [Tier 1]

> **WHO** (2012). *Guideline: Sodium intake for adults and children*. World Health Organization. ISBN 978-92-4-150483-6. https://www.who.int/publications/i/item/9789241504836. [Tier 1]

> **WHO** (2012). *Guideline: Potassium intake for adults and children*. World Health Organization. ISBN 978-92-4-150482-9. https://www.who.int/publications/i/item/9789241504829. [Tier 1]

> **WHO** (2023). *Saturated fatty acid and trans-fatty acid intake for adults and children: WHO guideline*. https://www.who.int/publications/i/item/9789240073630. [Tier 1]

> **WHO** (2023). *Carbohydrate intake for adults and children: WHO guideline*. https://www.who.int/publications/i/item/9789240073593. [Tier 1]

> **WHO** (2023). *Use of non-sugar sweeteners: WHO guideline*. https://www.who.int/publications/i/item/9789240073616. [Tier 1]

> **WHO** (2025). *Salt reduction* (fact sheet, last updated February 2025). https://www.who.int/news-room/fact-sheets/detail/salt-reduction. Accessed 2026-04-28. [Tier 1]

> **WHO** (2026, January 26). *Healthy diet* (fact sheet). https://www.who.int/news-room/fact-sheets/detail/healthy-diet. Accessed 2026-04-28. [Tier 1]

> **WHO** (2018–2025). *REPLACE — eliminating industrially-produced trans-fatty acids* (initiative). https://www.who.int/teams/nutrition-and-food-safety/replace-trans-fat. [Tier 1]

> **FAO/WHO/UNU** (2004). *Human Energy Requirements*. FAO Food and Nutrition Technical Report Series No. 1. https://www.fao.org/3/y5686e/y5686e00.htm. [Tier 1]

> **FAO/WHO** (2004). *Vitamin and Mineral Requirements in Human Nutrition* (2nd ed.). https://iris.who.int/handle/10665/42716. [Tier 1]

> **FAO/WHO/UNU** (2007). *Protein and Amino Acid Requirements in Human Nutrition*. WHO Technical Report Series 935. https://iris.who.int/handle/10665/43411. [Tier 1]

> **FAO** (2010). *Fats and Fatty Acids in Human Nutrition: Report of an Expert Consultation*. FAO Food and Nutrition Paper 91. https://www.fao.org/4/i1953e/i1953e00.pdf. [Tier 1]

> **FAO** (2026). *Food-based dietary guidelines* (country repository). https://www.fao.org/nutrition/education/food-dietary-guidelines/home/en/. Accessed 2026-04-28. [Tier 1]

> **MHLW** (2024). *Dietary Reference Intakes for Japanese, 2025 Edition* (食事摂取基準 2025年版). Ministry of Health, Labour and Welfare. https://www.mhlw.go.jp/. [Tier 1]

> **MHLW & MAFF** (2005, rev. 2010). *Japanese Food Guide Spinning Top* (食事バランスガイド). Ministry of Health, Labour and Welfare; Ministry of Agriculture, Forestry and Fisheries. https://www.maff.go.jp/j/balance_guide/. [Tier 1]

> **ICMR-NIN** (2020). *Nutrient Requirements for Indians — Recommended Dietary Allowances and Estimated Average Requirements*. Indian Council of Medical Research – National Institute of Nutrition. https://www.nin.res.in/. [Tier 1]

> **ICMR-NIN** (2024). *Dietary Guidelines for Indians*. ICMR-National Institute of Nutrition, Hyderabad. https://www.nin.res.in/. Accessed 2026-04-28. [Tier 1]

> **Chinese Nutrition Society** (2022). *Dietary Guidelines for Chinese 2022* (5th ed., popular and professional editions). https://www.cnsoc.org/. [Tier 1]

> **Chinese Nutrition Society** (2023). *Chinese Dietary Reference Intakes 2023*. People's Medical Publishing House. [Tier 1]

> **Ministry of Health Brazil** (2014). *Dietary Guidelines for the Brazilian Population* (2nd ed.). Ministério da Saúde, Secretaria de Atenção à Saúde / NUPENS-USP / PAHO. https://bvsms.saude.gov.br/bvs/publicacoes/dietary_guidelines_brazilian_population.pdf. Accessed 2026-04-28. [Tier 1]

> **Ministry of Health Brazil** (2019). *Guia alimentar para crianças brasileiras menores de 2 anos*. Ministério da Saúde. [Tier 1]

> **DGE** (2024). *Eat and Drink Well — DGE Recommendations* (Gut essen und trinken — Die DGE-Empfehlungen). Deutsche Gesellschaft für Ernährung. https://www.dge.de/. [Tier 1]

> **Santé Publique France / ANSES / HCSP** (2019, 2021, 2022). *Recommandations alimentaires du Programme national nutrition santé* (PNNS). https://www.santepubliquefrance.fr/. [Tier 1]

> **Health Council of the Netherlands (Gezondheidsraad)** (2015). *Guidelines for a healthy diet 2015*. https://www.gezondheidsraad.nl/. [Tier 1]

> **Conseil Supérieur de la Santé / Hoge Gezondheidsraad** (2019). *Food-Based Dietary Guidelines for the Belgian Adult Population*. https://www.health.belgium.be/. [Tier 1]

> **Schweizerische Gesellschaft für Ernährung (SGE/SSN)** (2024). *Swiss Food Pyramid*. https://www.sge-ssn.ch/. [Tier 1]

> **Korean Ministry of Health and Welfare + Korean Nutrition Society** (2020). *Dietary Reference Intakes for Koreans (KDRIs) 2020*. https://www.mohw.go.kr/. [Tier 1]

> **Israeli Ministry of Health** (2019). *Israeli Mediterranean Plate / Nutritional Recommendations*. https://www.gov.il/en/departments/ministry_of_health. [Tier 1]

> **Rospotrebnadzor** (2021). *Norms of Physiological Requirements in Energy and Nutrients for Various Population Groups of the Russian Federation* (MR 2.3.1.0253-21). Federal Service for Surveillance on Consumer Rights Protection and Human Wellbeing. [Tier 1]

> **Codex Alimentarius Commission** (FAO/WHO). *Guidelines on Nutrition Labelling* (CAC/GL 2-1985, with updates including NRVs-R and NRVs-NCD). https://www.fao.org/fao-who-codexalimentarius/en/. [Tier 1]

### Dietary patterns

> **USDA & HHS** (2020). *Dietary Guidelines for Americans, 2020–2025* (9th ed.). https://www.dietaryguidelines.gov/. [Tier 1]

> **USDA** (2011, ongoing). *MyPlate*. https://www.myplate.gov/. [Tier 1]

> **NHLBI** (2026, last updated February 25, 2026). *DASH Eating Plan*. National Heart, Lung, and Blood Institute, NIH. https://www.nhlbi.nih.gov/education/dash-eating-plan. Accessed 2026-04-28. [Tier 1]

> Appel, L.J., Moore, T.J., Obarzanek, E. et al. (1997). A clinical trial of the effects of dietary patterns on blood pressure (DASH). *New England Journal of Medicine*, 336(16), 1117–1124. https://doi.org/10.1056/NEJM199704173361601. [Tier 2]

> Sacks, F.M., Svetkey, L.P., Vollmer, W.M. et al. (2001). Effects on blood pressure of reduced dietary sodium and the Dietary Approaches to Stop Hypertension (DASH) diet. *NEJM*, 344(1), 3–10. https://doi.org/10.1056/NEJM200101043440101. [Tier 2]

> Morris, M.C., Tangney, C.C., Wang, Y. et al. (2015). MIND diet associated with reduced incidence of Alzheimer's disease. *Alzheimer's & Dementia*, 11(9), 1007–1014. https://doi.org/10.1016/j.jalz.2014.11.009. [Tier 3]

> Barnes, L.L., Dhana, K., Liu, X. et al. (2023). Trial of the MIND diet for prevention of cognitive decline in older persons. *NEJM*, 389(7), 602–611. https://doi.org/10.1056/NEJMoa2302368. [Tier 2 — RCT]

> Estruch, R., Ros, E., Salas-Salvadó, J. et al. (2018, republished from 2013). Primary prevention of cardiovascular disease with a Mediterranean diet supplemented with extra-virgin olive oil or nuts (PREDIMED). *NEJM*, 378(25):e34. https://doi.org/10.1056/NEJMoa1800389. [Tier 2 — RCT]

> Willett, W., Rockström, J., Loken, B. et al. (2019). Food in the Anthropocene: the EAT-Lancet Commission on healthy diets from sustainable food systems. *The Lancet*, 393(10170), 447–492. https://doi.org/10.1016/S0140-6736(18)31788-4. [Tier 1 — Commission]

> EAT-Lancet Commission (2019, summary). *Healthy Diets From Sustainable Food Systems — Summary Report*. https://eatforum.org/eat-lancet-commission/eat-lancet-commission-summary-report/. Accessed 2026-04-28. [Tier 1]

> EAT-Lancet Commission (2025). *Report on Healthy, Sustainable, and Just Food Systems*. https://eatforum.org/eat-lancet-commission/. Accessed 2026-04-28. [Tier 1]

> Harvard T.H. Chan School of Public Health (2011, ongoing). *Healthy Eating Plate*. https://www.hsph.harvard.edu/nutritionsource/healthy-eating-plate/. [Tier 2-equivalent — academic]

> Public Health England (2016). *The Eatwell Guide*. https://www.gov.uk/government/publications/the-eatwell-guide. [Tier 1]

> UNESCO (2010, expanded 2013). *Mediterranean Diet — Intangible Cultural Heritage*. https://ich.unesco.org/en/RL/mediterranean-diet-00884. [Tier 4 — cultural inscription, no health claim]

> Willcox, B.J., Willcox, D.C., Suzuki, M. (2017). The Okinawa Centenarian Study: Investigating Healthy Aging among the World's Longest-Lived People. *Mechanisms of Ageing and Development*. [Tier 3 — cohort] **[verify — the cited DOI (10.1016/j.mad.2016.05.004) is an unrelated NOX2/doxorubicin paper, and no *Mech Ageing Dev* article has this title; it matches a Springer encyclopedia entry (Suzuki, Willcox & Willcox 2016, https://doi.org/10.1007/978-981-287-080-3_74-1). Candidates for the §265 diet claim: Willcox, Willcox, Todoriki & Suzuki 2009, *The Okinawan diet: health implications of a low-calorie, nutrient-dense, antioxidant-rich dietary pattern low in glycemic load*, J Am Coll Nutr 28(sup4), https://doi.org/10.1080/07315724.2009.10718117 (narrative review); or Willcox, Willcox & Suzuki 2017, *Mech Ageing Dev* 165:75–79, https://doi.org/10.1016/j.mad.2016.11.001 (descriptive cohort).]**

### Cross-body comparative and methodology references

> Bauer, J., Biolo, G., Cederholm, T. et al. (2013). Evidence-based recommendations for optimal dietary protein intake in older people: a position paper from the PROT-AGE Study Group. *J Am Med Dir Assoc*, 14(8), 542–559. https://doi.org/10.1016/j.jamda.2013.05.021. [Tier 2]

> Te Morenga, L., Mallard, S., Mann, J. (2013). Dietary sugars and body weight: systematic review and meta-analyses of randomised controlled trials and cohort studies. *BMJ*, 346:e7492. https://doi.org/10.1136/bmj.e7492. [Tier 2]

> Phillips, S.M., Chevalier, S., Leidy, H.J. (2016). Protein "requirements" beyond the RDA. *Applied Physiology, Nutrition, and Metabolism*, 41(5), 565–572. https://doi.org/10.1139/apnm-2015-0550. [Tier 2/3]

### Navigation references (Wikipedia — Tier 4, used only for cross-body terminology mapping; no health claim sourced from these)

> Wikipedia. *Dietary Reference Intake*. https://en.wikipedia.org/wiki/Dietary_Reference_Intake. Accessed 2026-04-28. [Tier 4 — navigation only]

> Wikipedia. *Dietary Reference Value*. https://en.wikipedia.org/wiki/Dietary_Reference_Value. Accessed 2026-04-28. [Tier 4 — navigation only]

