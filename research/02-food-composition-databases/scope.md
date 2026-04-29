# Sweep #2 — Food Composition Databases — Multi-Source Landscape

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Map the landscape of food composition databases worldwide, characterize coverage / quality / access / licensing, identify harmonization standards and known gaps, and surface the framework-level literature on cooking transformations (yield + retention factors).

## Deliverable

An annotated reference map containing:

- Per-database inventory (mirroring sweep #1's geographic scope of top 150 countries via FAO INFOODS):
  - Maintainer + license (public domain, ODbL, CC-BY, proprietary)
  - Access modality (free API, paid API, downloadable, PDF-only)
  - Coverage profile (whole foods, branded, prepared, restaurant)
  - Item count + nutrient panel breadth
  - Last update / version cadence
  - Known coverage gaps (e.g., USDA FDC weak on prepared international dishes)
- Branded / packaged product sub-section (Open Food Facts, USDA branded, GS1)
- Cooking transformation framework: yield factors and retention factors, citing the foundational literature (USDA Tables 12 & 13, EuroFIR factors, Bognar)
- Harmonization standards: INFOODS tagnames, LanguaL, FoodEx2

## In scope

- **Geographic scope:** top 150 countries (mirrors [sweep #1](../01-international-nutrition-standards/scope.md))
- **Major databases:** USDA FoodData Central (Foundation, SR Legacy, FNDDS, Branded), EuroFIR, McCance & Widdowson (UK CoFID), AUSNUT/NUTTAB, Canadian Nutrient File (CNF), INFOODS regional databases, Japan STFC, Indian Food Composition Tables, China FCT, Brazilian TBCA
- **Branded products:** Open Food Facts (3M+ items, ODbL), USDA FDC Branded, plus regional branded databases — handled as a *separate category* from whole/generic foods
- **Cooking transformations:** framework-level coverage of yield factors (mass change with cooking) and retention factors (nutrient survival through cooking) — references and literature pointers, not full tables
- **Access details:** API endpoints, rate limits, pricing, license terms, terms of use
- **Coverage gaps:** known weaknesses (international prepared dishes, regional/ethnic foods, traditional preparations)
- **Harmonization standards:** INFOODS tagnames, LanguaL food classification, FoodEx2

## Out of scope (with reasons)

- Restaurant / chain food databases (MenuStat, FastFoodNutrition) — deferred. Without a logging surface, the obvious use case disappears. Pending decision on whether traveler/eating-out *recommendations* justify keeping at reference level.
- Full ingestion of any database — deferred to later corpus-build phase
- Deep cooking transformation tables — deferred (frameworks cited here, full tables in a later corpus build)
- Micronutrient bioavailability literature — deferred (would warrant its own sweep if needed)
- Nutrient interaction modeling — deferred

## Branded vs. whole / generic foods

Per user direction: **whole, generic, from-scratch foods are the default surface**; branded packaged goods are in scope but treated as a separate category. Real cook-from-scratch users still buy branded staples (canned tomatoes, pasta, condiments). The data model should distinguish these but neither is excluded.

## Cooking transformations

Cooking changes nutrition substantially:

- Vitamin C losses in boiling
- B-vitamin losses across multiple methods
- Water and fat changes in roasting / frying
- Mineral leaching into discarded steaming water
- Fat absorption from frying oil

Framework-level coverage in this sweep means: cite the foundational literature and the standard tables (USDA Tables 12 & 13, EuroFIR factors, Bognar 2002), characterize what's available and how rigorous it is. Full table ingestion happens later.

## Open questions for the research

- Which databases have free, programmatic API access vs. download-only vs. paywalled?
- What are the licensing terms for downstream use (especially commercial, even though we're personal-first)?
- For the top 150 countries, how many have a maintained national food composition database, and how many rely on regional / WHO INFOODS aggregates?
- How do the major databases harmonize (or fail to harmonize) on units, nutrient definitions, and ingredient identifiers?
- What is the state of branded product coverage internationally — is Open Food Facts the global gold standard, or are there regional alternatives?
- How are cultural/religious-specific foods (halal, kosher, jain, ayurvedic, traditional preparations) covered?

## Cross-references

- Bound by [Evidence Tiers](../00-meta/evidence-tiers.md) — composition data quality varies; treat USDA Foundation Foods as authoritative, branded data as user-submitted (Open Food Facts) → Tier 4 unless verified
- Mirrors geographic scope of [sweep #1](../01-international-nutrition-standards/scope.md)
- Feeds [sweep #11 (recipe sourcing)](../11-recipe-sourcing/scope.md) — recipes need composition data to compute nutrition
- Feeds [sweep #10 (clinical condition gating)](../10-clinical-condition-gating/scope.md) — condition-relevant nutrient lookups (e.g., potassium for CKD)

## Findings

> **Methodological note (2026-04-28):** WebSearch and WebFetch were denied during this sweep. Findings below are populated from the agent's training-data knowledge of these well-documented public-sector databases and harmonization standards. Item counts, version numbers, and "last updated" dates should be treated as **as-of approximate** and re-verified against maintainer pages before any corpus build (this is a reference map, not an ingestion). All maintainer URLs are listed in `## References` for that re-verification pass. Where a value is sensitive to drift, it is flagged inline.

### A. Top-tier whole/generic food composition databases

#### A.1 USDA FoodData Central (FDC) — United States

- **Maintainer:** USDA Agricultural Research Service, Beltsville Human Nutrition Research Center, Nutrient Data Laboratory; co-administered with the Methods and Application of Food Composition Laboratory (MAFCL).
- **License:** US federal government work — public domain (17 U.S.C. § 105). No license restriction on downstream use, including commercial.
- **Access modality:** Free public REST API (api.nal.usda.gov/fdc; key required, generous rate limits — ~1,000 requests/hour per key as of last published policy); full CSV / JSON / Access database downloads; web search UI.
- **Five sub-datasets** (FDC unified them ~2019, replacing the legacy NDB):
  1. **Foundation Foods** — analytically derived, full provenance to lab method and sample design. Highest-quality tier. Item count low (low thousands) but growing; covers commodity / minimally processed items where USDA has run modern analyses. **Tier 1.**
  2. **SR Legacy (Standard Reference, Release 28, frozen 2018)** — the historical USDA SR series. ~7,800 items, ~150 nutrients per item where measured. Static — no further updates planned; superseded conceptually by Foundation Foods but still the workhorse for downstream apps because of breadth. **Tier 1.**
  3. **FNDDS (Food and Nutrient Database for Dietary Studies)** — built for NHANES dietary recall coding. Released biennially in NHANES cycle (e.g., FNDDS 2017–2018, 2019–2020, 2021–2023). ~7,000–8,000 items, includes prepared/mixed dishes ("chicken, fried, with skin", "lasagna with meat") with recipe-level decomposition to SR/Foundation ingredients. Critical for prepared-foods coverage in US context. **Tier 1.**
  4. **Branded Foods** — label-derived nutrient panels for packaged products, ingested via partnership with the food industry (GS1 US, Label Insight / IRI / Circana data feed). ~1.4M+ items as of recent releases (grows monthly). **Tier 1 for label fidelity, Tier 3–4 for analytical accuracy** — values are manufacturer-declared, not analytically verified by USDA. Staleness varies by manufacturer.
  5. **Experimental Foods** — research-stage entries with full provenance to PI/study; small.
- **Nutrient panel breadth:** Foundation/SR carry the full ~150-nutrient panel where measured (proximates, minerals, vitamins, individual fatty acids, individual amino acids, sugars, fiber components). FNDDS inherits ~65 nutrients computed via recipe decomposition. Branded carries the regulated US Nutrition Facts panel (~25 nutrients) plus whatever the manufacturer declared.
- **Cadence:** FDC release notes monthly; underlying datasets updated on their own cycles (Foundation rolling, SR frozen, FNDDS biennial, Branded near-continuous).
- **Coverage gaps:** weak on prepared international dishes outside the US dietary repertoire (Indian curries, Levantine mezze, Korean banchan, traditional African dishes); weak on regional/heritage US foods; Branded coverage skews to large national CPG brands and underrepresents private-label, regional, and small-producer items.
- **Inclusion of yield + retention factor tables:** USDA Tables 12 (yield) and 13 (retention) are published as separate PDFs/Excels distinct from FDC proper — see §C.

#### A.2 Canadian Nutrient File (CNF) — Canada

- **Maintainer:** Health Canada, Office of Nutrition Policy and Promotion / Bureau of Nutritional Sciences.
- **License:** Open Government Licence – Canada (OGL-Canada 2.0) — equivalent to CC-BY for practical purposes; commercial use permitted with attribution.
- **Access modality:** Web search UI (food-nutrition.canada.ca / canadiannutrientfile), downloadable ZIP of relational tables (CSV); no public REST API. Programmatic users typically download and self-host.
- **Coverage profile:** ~5,700 foods (CNF 2015 release; minor revisions since), ~150 nutrients possible per food. Heavy reuse of USDA SR values (Health Canada explicitly borrows where Canadian data not available) augmented with Canadian-specific items (poutine, bannock, regional fish, fortification reflecting Canadian regulation).
- **Cadence:** Major release 2015; incremental updates and label-update releases since. Slower than FDC.
- **Gaps:** prepared-food coverage thinner than FNDDS; Indigenous foods documented separately and incompletely (see Kuhnlein's work — referenced in §C).

#### A.3 McCance & Widdowson's Composition of Foods Integrated Dataset (CoFID) — United Kingdom

- **Maintainer:** Originally Royal Society of Chemistry / Medical Research Council (the "McCance & Widdowson" book lineage, first published 1940); now maintained by the UK Office for Health Improvement and Disparities (OHID, formerly Public Health England, formerly Food Standards Agency UK Nutrition).
- **License:** Open Government Licence v3.0 — equivalent to CC-BY for practical purposes; commercial use permitted with attribution.
- **Access modality:** Free downloadable Excel / CSV from gov.uk; the printed *McCance and Widdowson's The Composition of Foods* 8th summary edition (2021, RSC Publishing) is the book form. No public REST API. Some third parties (e.g., Nutritics, Dietplan) re-license CoFID inside paid software.
- **Coverage profile:** ~3,300 foods in the integrated dataset, ~50–60 nutrients per food. Strong on UK-typical generic foods including UK-specific prepared dishes (bangers and mash, shepherd's pie, treacle tart), UK fortification regimes (folic acid, vitamin D added per 2021 mandates).
- **Cadence:** Integrated dataset typically refreshed every 2–3 years; current CoFID release was 2021; supplementary special-topic tables (vegetables, meats, fish, milk products) appear between integrated releases.
- **Gaps:** non-UK ethnic dishes lighter than US FNDDS for those cuisines; fewer items overall than US datasets but higher per-item analytical quality (the McCance lineage is famously rigorous on lab method).

#### A.4 Australian Food Composition Database (AFCD; formerly NUTTAB) and AUSNUT — Australia / New Zealand

- **Maintainer:** Food Standards Australia New Zealand (FSANZ).
- **License:** Creative Commons Attribution 3.0 Australia (CC-BY 3.0 AU). Commercial use permitted with attribution.
- **Access modality:** Free downloadable Excel from foodstandards.gov.au; no public REST API.
- **Two distinct datasets:**
  - **AFCD (formerly NUTTAB)** — reference dataset of analytically measured Australian foods. Current release AFCD Release 2.0 (2022) supersedes NUTTAB 2010. ~1,600 foods, ~250 nutrients/components possible per food (broad panel including individual carotenoids, individual fatty acids, individual amino acids, alcohol).
  - **AUSNUT** — purpose-built for the Australian Health Survey (analogous to FNDDS for NHANES). Latest is AUSNUT 2011–13. ~5,700 items including prepared/mixed dishes with recipe decomposition.
- **New Zealand parallel:** **New Zealand Food Composition Database (NZFCD)** — maintained by Plant & Food Research / Manatū Hauora (Ministry of Health NZ); ~2,700 items; published as the *FOODfiles* dataset and through the *New Zealand Food Composition Tables* (Concise Tables); CC-BY-NC for some releases (NC restriction matters for commercial downstream use).
- **Gaps:** limited non-Australian/NZ ethnic prepared-dish coverage; AUSNUT 2011–13 is the most recent prepared-foods dataset (over a decade old).

#### A.5 CIQUAL — France

- **Maintainer:** ANSES (Agence nationale de sécurité sanitaire de l'alimentation, de l'environnement et du travail), Observatoire des aliments / CIQUAL.
- **License:** Etalab Open License 2.0 (compatible with CC-BY 4.0); commercial use permitted with attribution.
- **Access modality:** Free downloadable XLS/CSV; web search UI; no public REST API.
- **Coverage profile:** ~3,200 foods, ~70 nutrients per food (current Ciqual 2020 table). Strong on French/European generic foods, including French prepared dishes and the AGRIBALYSE life-cycle environmental data (linked to Ciqual food IDs — distinct sweep relevance for environmental footprints).
- **Notable feature:** uses FoodEx2 classification (see §D.3) — one of the cleanest implementations.
- **Cadence:** Major refresh 2020; incremental updates.

#### A.6 BLS (Bundeslebensmittelschlüssel) — Germany

- **Maintainer:** Max Rubner-Institut (MRI), federal research institute.
- **License:** Proprietary, paid license — the only major Western European national database that is not freely downloadable. Used heavily inside German clinical nutrition software (PRODI, NUT.S, Nutritio).
- **Access modality:** License purchase via MRI; no API.
- **Coverage:** ~13,000 foods, ~140 nutrients — among the broadest item counts in Europe; engineered for clinical/dietary-assessment use.
- **Implication for NutriMe:** if German coverage matters at corpus-build time, BLS is a paid dependency, not a free dataset; alternative is to fall back on Ciqual / CoFID / EuroFIR member data for German equivalents.

#### A.7 NEVO — Netherlands

- **Maintainer:** RIVM (Rijksinstituut voor Volksgezondheid en Milieu / National Institute for Public Health and the Environment).
- **License:** Free for non-commercial / research use; commercial use requires negotiated license.
- **Access modality:** Online viewer (nevo-online.rivm.nl), downloadable for research; no public API.
- **Coverage:** ~2,200 foods, ~135 nutrients. Strong on Dutch market items.

#### A.8 Frida — Denmark (representative Nordic instance)

- **Maintainer:** DTU National Food Institute (Fødevareinstituttet).
- **License:** Free public access; data use under attribution.
- **Access modality:** Web UI (frida.fooddata.dk) with structured downloads; no public REST API.
- **Coverage:** ~1,200 foods, ~125 nutrients. Each Nordic country has a parallel: **Fineli** (Finland — National Institute for Health and Welfare THL, free, has a documented REST API — among the few national databases with a real public API), **Matvaretabellen** (Norway — Mattilsynet/Norwegian Food Safety Authority + University of Oslo, free), **Livsmedelsdatabasen** (Sweden — Livsmedelsverket, free), **ÍSGEM** (Iceland — Matís).

#### A.9 BEDCA — Spain

- **Maintainer:** Spanish Food Composition Database consortium under AESAN (Agencia Española de Seguridad Alimentaria y Nutrición).
- **License:** Free for research with attribution; commercial license negotiated.
- **Coverage:** ~1,000+ foods; uses INFOODS tagnames; thinner than its European peers but methodologically clean.

#### A.10 IEO / INRAN / CREA — Italy

- **Maintainer:** Currently CREA Alimenti e Nutrizione (Council for Agricultural Research and Economics; absorbed the former INRAN). The IEO (Istituto Europeo di Oncologia) maintains a parallel composition database with strong polyphenol coverage used in epidemiology.
- **License:** Free for research use.
- **Coverage:** CREA tables ~900 foods; IEO database larger when phenolic compounds included.

#### A.11 Standard Tables of Food Composition in Japan (STFC) — Japan

- **Maintainer:** Ministry of Education, Culture, Sports, Science and Technology (MEXT), through the Council for Science and Technology Subdivision on Resources, Subcommittee on Food Composition.
- **License:** Government work — broadly reusable; English translation published with attribution requirements. Always cited as "Standard Tables of Food Composition in Japan — 2020 (Eighth Revised Edition)".
- **Access modality:** Free downloadable Excel/PDF in Japanese and English; no public API.
- **Coverage:** ~2,500 foods in the main table; supplementary tables for amino acids, fatty acids, available carbohydrates. Famously thorough on Japanese ingredients (multiple seaweed species, fermented soy products, individual fish species and parts, traditional preserved foods). Nutrient panel breadth comparable to USDA SR for the supplementary-table coverage.
- **Gaps:** non-Japanese prepared dishes; Japanese-only entries common in the main table even in the English release.

#### A.12 China Food Composition Tables (CFCT / CNFCT) — China

- **Maintainer:** National Institute for Nutrition and Health (NINH), Chinese Center for Disease Control and Prevention (China CDC).
- **License:** Published as books (Peking University Medical Press); the dataset is **not openly licensed** as a downloadable file. Some derivative tables circulate but the canonical source is the printed/electronic book.
- **Coverage:** Current edition is the *China Food Composition Tables, 6th edition* (Standard Edition Vol 1 + Vol 2, 2018–2019). ~2,200 foods, ~50+ nutrients per food. Strong on Chinese vegetables, fungi, traditional preparations, regional cuisines, dim sum items.
- **Gaps:** licensing is the practical blocker for inclusion in any open downstream system; English-language access is partial.

#### A.13 Indian Food Composition Tables (IFCT) — India

- **Maintainer:** National Institute of Nutrition (NIN), Indian Council of Medical Research (ICMR).
- **License:** Published as book (NIN); PDF widely accessible. Reuse terms not explicitly permissive — treat as research-fair-use until clarified.
- **Coverage:** *Indian Food Composition Tables 2017* (the modernization replacing Gopalan 1989) — ~540 foods, but each with extensive analytical coverage including individual fatty acids, individual carotenoids, oligosaccharides, polyphenol classes, antinutrient factors (phytate, oxalate). Methodologically excellent per food, narrower in breadth.
- **2025 supplement** (IFCT-2025 or supplementary tables) reportedly under development to expand prepared-dish coverage; verify against NIN release.
- **Gaps:** prepared / restaurant / regional thalis vary; Pan-Indian regional cuisine breadth (Bengali, Kerala, Punjabi, Gujarati, etc.) under-represented relative to the cuisine's actual diversity.

#### A.14 Tabela Brasileira de Composição de Alimentos (TBCA) — Brazil

- **Maintainer:** Food Research Center (FoRC), University of São Paulo (USP), in coordination with the Brazilian Ministry of Health and the Latinfoods regional INFOODS network.
- **License:** Free public access via web (tbca.net.br); attribution requested. Sometimes confused with **TACO** (Tabela Brasileira de Composição de Alimentos / NEPA-UNICAMP), an older parallel maintained by UNICAMP — TACO is now considered superseded by TBCA but still circulates.
- **Coverage:** ~2,000+ foods in TBCA v7.x, growing with each release. Strong on Brazilian ingredients (cassava varieties, açaí, tapioca preparations, Brazilian regional dishes, feijoada components).
- **Cadence:** Updated annually with version increments.
- **Gaps:** more whole/generic than prepared-mixed; nutrient panel narrower than USDA on micronutrients.

#### A.15 Other notable national/regional databases (briefly, by region)

- **Latin America (Latinfoods regional INFOODS network):** Mexico — INSP / Instituto Nacional de Salud Pública food composition database; Argentina — CENEXA / SARA; Chile — INTA, Universidad de Chile food composition tables; Costa Rica — INCIENSA; Cuba — INHA. Coordination via Latinfoods.
- **Africa (AFROFOODS regional INFOODS network):** South Africa — Medical Research Council South African Food Composition Database (SAFOODS / SAFCDB), maintained by SAMRC; West African Food Composition Table (FAO/INFOODS regional, 2019, English/French) — covers ~470 foods across West Africa; Kenya — Kenya Food Composition Tables 2018 (KAPAP/FAO collaboration).
- **Middle East (NEMEDIFOODS regional INFOODS network):** Iran — Iranian Food Composition Table (NNFTRI); Lebanon — AUB Lebanese composition database; coordination irregular; many countries rely on FAO regional aggregates.
- **South / Southeast Asia (ASEANFOODS):** Thailand — Institute of Nutrition Mahidol University INMU food composition; Vietnam — National Institute of Nutrition Vietnamese Food Composition Table; Philippines — DOST-FNRI Philippine Food Composition Tables; Malaysia — MyFCD (Ministry of Health). ASEANFOODS network publishes harmonized regional table.
- **Russia / former Soviet sphere:** Skurikhin tables (the historical Soviet reference, *Chemical Composition of Russian Food Products*) remain the working reference, periodically updated; no open digital release equivalent to FDC.
- **Korea:** Korea Food Composition Database — Rural Development Administration (RDA) National Institute of Agricultural Sciences; latest standard tables 10th revision (2021); free PDF/Excel; Korean-only nutrient definitions in places.

#### A.16 INFOODS regional databases and FAO aggregates

- **Maintainer:** FAO/INFOODS — International Network of Food Data Systems, hosted by the Food and Agriculture Organization of the United Nations.
- **Role:** Coordinates ~150 countries' worth of composition activity through regional networks (EuroFIR, NORFOODS, AFROFOODS, ASEANFOODS, LATINFOODS, NEMEDIFOODS, OCEANIAFOODS, CEECFOODS for Central/Eastern Europe, CHINAFOODS, NEASIAFOODS, SAARCFOODS).
- **FAO/INFOODS reference tables published directly:** the **FAO/INFOODS Global Food Composition Database for Fish and Shellfish (uFiSh)**, **for Pulses (uPulses)**, and **the West African Food Composition Table** (2019, 2nd ed.) — open downloads, used as harmonized regional fallbacks where national datasets are missing or thin.
- **Coverage gap pattern:** of the FAO INFOODS top-150 country list, perhaps 40–50 maintain a current (post-2010), publicly accessible national composition database; the remainder rely on regional aggregates, older tables, or borrowed values from neighboring countries / USDA.

### B. Branded / packaged-product databases (separate category per scope)

#### B.1 Open Food Facts

- **Maintainer:** Open Food Facts non-profit association (France-headquartered, global volunteer contributors). Independent of food industry.
- **License:** **Database under Open Database License (ODbL 1.0); contents under Database Contents License (DbCL); individual product images CC-BY-SA 3.0.** ODbL imposes share-alike on derivative *databases*, which has downstream design implications for any product redistributing the dataset.
- **Access modality:** Free public REST API (world.openfoodfacts.org/api); full database dumps (MongoDB, JSONL, CSV, Parquet) refreshed daily.
- **Coverage:** **~3.4M+ products** as of recent reporting (grew rapidly post-2022); global, with strongest density in France, Germany, US, UK, Spain, Italy. Includes barcode (GTIN/EAN), declared nutrition facts, ingredients, Nutri-Score, NOVA classification, eco-score, allergens, packaging.
- **Tier:** **Tier 4 by default** (user-submitted, photo-OCR, crowd-verified) **unless** the entry has been verified — Open Food Facts exposes a `data_quality` and `states` flag system that distinguishes complete/photo-verified entries from incomplete ones. Treat verified/complete entries as Tier 3-equivalent for label-fidelity purposes; never as Tier 1 for analytical accuracy.
- **Coverage gaps + quality variance:** declared values are manufacturer label values, with all the limitations that implies (rounding rules, "0 g trans fat" thresholds, missing micronutrients beyond regulated panel); user submissions vary in completeness; barcode duplication and product-version drift are known issues.

#### B.2 USDA FDC Branded (recap from §A.1)

- **Tier note:** Branded sub-dataset is the closest to Tier 1 branded data globally because of GS1/Label Insight feed integration, but values are still manufacturer-declared, not analytically verified — same caveat as Open Food Facts but with less crowdsourced noise.

#### B.3 Open Food Repo (Switzerland) / FoodRepo

- **Maintainer:** Digital Health team at EPFL / Swiss Data Science Center (status verify — project has had funding cycle uncertainty).
- **License:** CC-BY 4.0; free API.
- **Coverage:** Swiss-market focus, ~30,000+ products historically; relevance to broader audience modest given Open Food Facts overlap.

#### B.4 Regional / national branded sources (briefly)

- **UK:** FoodSwitch UK (George Institute) — branded packaged data with Food Standards Agency traffic-light data; commercial use restricted.
- **Australia:** FoodSwitch AU + the FSANZ Branded Foods program (pilot for Australian branded composition collection).
- **Canada:** Health Canada Branded Food Composition Database under development; no public API at sweep date.
- **Mexico, Brazil, Chile, India:** national front-of-pack labelling regulations have driven branded-data collection efforts (e.g., Mexico's NOM-051 driving INSP-collected data); access varies and is generally not openly distributed.
- **GS1 GDSN (Global Data Synchronization Network):** the underlying B2B identifier/attribute network for packaged products globally; not consumer-accessible, not openly licensed; commercial partnerships only — relevant only as the upstream feed many branded composition sources rely on.

### C. Cooking transformation framework — yield + retention factors

#### C.1 USDA Tables 12 and 13 (canonical reference set)

- **USDA Table 12 — Nutrient Retention Factors, Release 6 (2007).** Maintained by USDA ARS Nutrient Data Laboratory. Free PDF + Excel. Provides per-nutrient retention factors (proportion of nutrient remaining after cooking) by food group × cooking method × nutrient. Underlies most international retention-factor work.
- **USDA Table 13 — Yield Factors / Recipe Calculations** — companion table giving mass change (% weight retention) from raw to cooked per food and method; integrated into FNDDS recipe-decomposition logic.
- **Status:** Table 12 has not had a major revision since Release 6 (2007); cited as the reference foundation in essentially every international retention-factor work since.

#### C.2 EuroFIR retention factor work

- **Bognar, A. (2002).** *Tables on weight yield of food and retention factors of food constituents for the calculation of nutrient composition of cooked foods (dishes).* Berichte der Bundesforschungsanstalt für Ernährung, BFE-R-02-03, Karlsruhe. The European canonical text alongside USDA Table 12; broader European cuisine coverage (German preparation methods particularly).
- **Bell, S., Becker, W., Vásquez-Caicedo, A.L., Hartmann, B., Møller, A., Butriss, J. (2006).** Promoting food information exchange across Europe using food composition data — a review of food composition data quality. EuroFIR work feeding the harmonized European retention-factor methodology.
- **Vásquez-Caicedo, A.L., Bell, S., Hartmann, B. (2008).** *Report on collection of rules on use of recipe calculation procedures including the use of yield and retention factors for imputing nutrient values for composite foods.* EuroFIR Technical Report.

#### C.3 Broader retention-factor literature pointers

- **Bognar, A. & Piekarski, J. (2000).** Guidelines for recipe information and calculation of nutrient composition of prepared foods (dishes). *Journal of Food Composition and Analysis*, 13(4), 391–410.
- **Reinivuo, H., Bell, S., Ovaskainen, M-L. (2009).** Harmonisation of recipe calculation procedures in European food composition databases. *Journal of Food Composition and Analysis*, 22(5), 410–413. — methodological paper on cross-country harmonization, key for any multi-source ingestion approach.
- **Schakel, S.F., Buzzard, I.M., Gebhardt, S.E. (1997).** Procedures for estimating nutrient values for food composition databases. *Journal of Food Composition and Analysis*, 10(2), 102–114. — the foundational US methodology paper; still cited.
- **Kapsokefalou, M. et al. (2019).** Food composition at present: new challenges. *Nutrients*, 11(8), 1714. — recent review of the state of the field, challenges of branded/prepared coverage and harmonization.
- **Greenfield, H. & Southgate, D.A.T. (2003).** *Food composition data: production, management and use* (2nd ed.). FAO. The "textbook" on composition-database construction methodology — still the canonical reference.

#### C.4 Indigenous / traditional foods literature pointer

- **Kuhnlein, H.V., Erasmus, B., Spigelski, D., Burlingame, B. (2009/2013).** *Indigenous Peoples' food systems & well-being: interventions & policies for healthy communities.* FAO/CINE — methodological work on composition assessment for traditional foods that fall outside national database coverage. Relevant to any system claiming international scope.

### D. Harmonization standards

#### D.1 INFOODS tagnames

- **Maintainer:** FAO/INFOODS.
- **What it is:** Controlled vocabulary of nutrient identifiers (e.g., `PROCNT` = protein from nitrogen × factor, `FAT` = total fat, `FASAT` = saturated fatty acids, `VITC` = vitamin C, `NIA` = niacin, `NIAEQ` = niacin equivalents). Distinguishes analytical method, definition, and unit so that "protein" from one database can be matched to "protein" from another only when the tagname matches.
- **Why it matters for NutriMe:** without tagname-level matching, cross-database aggregation produces silent errors (e.g., "fiber" can be crude fiber, AOAC total dietary fiber, or AOAC 2009.01 — three different numbers for the same food).
- **Reference:** Klensin, J.C. (1992). *INFOODS Food Composition Data Interchange Handbook*. UNU; FAO INFOODS Tagnames documentation (current version maintained on FAO INFOODS website).

#### D.2 LanguaL

- **Maintainer:** LanguaL Technical Committee, multi-national; hosted historically via Danish Food Informatics + EuroFIR.
- **What it is:** "Langua aLimentaria" — multi-faceted thesaurus describing foods by ~14 facets (product type, food source, part of plant/animal, physical state, cooking method, preservation method, packaging, country of origin, etc.). Each food is described by a string of facet codes.
- **Adoption:** widely embedded inside European national databases (Ciqual, NEVO, BEDCA, others); USDA SR has LanguaL codes in legacy releases.
- **Use for NutriMe:** enables faceted search and cross-cuisine equivalence ("a steamed leafy green from East Asian cuisine" → recall set across databases).

#### D.3 FoodEx2

- **Maintainer:** EFSA (European Food Safety Authority).
- **What it is:** EFSA's standardized food classification and description system used in European food consumption surveys and contaminant monitoring. Hierarchical (broad to detailed) plus facet system. The de facto standard for European-level data exchange post-2015.
- **Status:** Active; EFSA publishes the FoodEx2 catalogue and revisions (currently in revision 2, with periodic updates).
- **Cross-walk:** Ciqual is one of the cleanest implementations; many European databases publish FoodEx2 codes alongside national codes.

#### D.4 Other relevant identifiers

- **GS1 GTIN / EAN-13 / UPC-A** — barcode standard for branded packaged goods; the join key for any branded dataset.
- **FoodOn** — open biomedical food ontology (OBO Foundry); machine-readable, growing adoption in academic/computational nutrition contexts; CC-BY 4.0.
- **SNOMED CT food hierarchy / ICD-11 food categories** — clinical-record-system food vocabularies; relevant if NutriMe ever interfaces with clinical EHR food/allergen data.

### E. Coverage-gap synthesis

- **Prepared international dishes** — every major Western database is weak here. FNDDS is the best for US-popular ethnic dishes but skews to "Americanized" versions; CoFID is similarly UK-skewed. National databases of the cuisine's home country (Japan STFC, IFCT, China CFCT, TBCA) are more authoritative for their own cuisine but may not cover diaspora variants. **Implication for NutriMe:** any cross-cuisine recommendation surface needs explicit fallback logic across multiple national databases, plus tagname-level harmonization (see §D.1) to avoid silent aggregation errors.
- **Branded coverage internationally** — Open Food Facts is the only globally consistent branded source, but Tier 4 by default and license-encumbered (ODbL share-alike). USDA FDC Branded is best-in-class within the US. Outside US/EU, branded coverage is sparse to nonexistent in open form.
- **EuroFIR fragmentation** — there is no single pan-European composition table. EuroFIR's FoodEXplorer aggregates ~25 national datasets behind a paid platform but does not produce a single harmonized table. Each country must be ingested separately.
- **Cultural / religious-specific foods** — halal/kosher status is a *certification* property, not a composition property; composition databases do not track it. Jain (no root vegetables, no onion/garlic) and Ayurvedic categorization (rasa/dosha) are dietary-classification systems without composition-database analogs. NutriMe must layer these as separate metadata, not expect them in composition data.
- **Traditional / heritage / Indigenous foods** — chronically under-represented; Kuhnlein/CINE work is the methodological reference, but coverage outside that program is patchy.
- **Cooking transformations** — well-characterized for major Western methods (boiling, baking, frying, roasting, steaming) via USDA Table 12 and Bognar 2002; less well-characterized for region-specific methods (tandoor, wok-hei high-heat stir-fry, slow-fermentation, banana-leaf steaming, charcoal grilling at the smoke point); essentially uncharacterized for novel methods (sous vide at non-standard temperatures, air frying — though some recent literature is appearing).

### F. Restaurant / chain food databases (brief, per scope decision)

Per scope, this is included at reference level only because the no-logging product framing reduces the use case to **traveler / eating-out recommendation surfaces** (e.g., "what's the best choice on this chain's menu while travelling"):

- **MenuStat** — NYC Department of Health menu calorie/nutrient project; ~100 large US chains; free download; updated through ~2018, status uncertain since.
- **Nutritionix** — commercial branded + restaurant database, ~1M+ items including ~700K restaurant items; freemium API with paid tiers; widely used by consumer food-logging apps; **not openly licensed** — paid commercial dependency.
- **FastFoodNutrition.org** — aggregator site; not authoritative; web-scraped manufacturer data; reference-only.
- **Chain manufacturer disclosures** — under US FDA menu-labeling rule (chains 20+ locations) and EU Food Information to Consumers Regulation (FIC, EU 1169/2011), large chains publish nutrition disclosures as PDFs/web pages; primary-source but not aggregated openly.
- **For NutriMe:** none of these are foundational; if traveler/eating-out recommendations stay scoped, Nutritionix would be the practical commercial choice and Open Food Facts + chain disclosures the open-data fallback.

### G. Answers to scope's "Open questions"

- **Free programmatic API access vs. download-only vs. paywalled:** Of the major national databases, only **USDA FDC**, **Fineli (Finland)**, and **Open Food Facts** offer first-class public REST APIs. Most others (CoFID, AFCD, Ciqual, NEVO, Frida, STFC Japan, TBCA, IFCT, CNF, Korea RDA) are **download-only** (Excel/CSV/PDF). **BLS (Germany)** is the major paid-license outlier among Western Europe. **China CFCT** is effectively book-only. Practical implication: for any multi-source corpus build, expect download + ETL workflow as the norm, with API access being the exception.
- **Licensing terms for downstream use:** USDA FDC (US public domain), CoFID (OGL v3.0 ≈ CC-BY), CNF (OGL Canada 2.0 ≈ CC-BY), AFCD/AUSNUT (CC-BY 3.0 AU), Ciqual (Etalab ≈ CC-BY), Frida/Fineli/Matvaretabellen (open with attribution) — all permit commercial use with attribution. NEVO (NL) restricts commercial use without negotiated license. BLS (DE) is paid-license. Open Food Facts is **ODbL** with share-alike on derivative databases — the most consequential constraint for any product redistributing the data. China CFCT, IFCT, STFC English: more restrictive / less explicit; treat as research-fair-use until clarified.
- **Top-150 country coverage via national database vs. regional aggregate:** Approximately **40–50 countries** (mostly OECD plus large emerging economies — China, India, Brazil, Mexico, Thailand, South Africa, Korea, Israel) maintain a current (post-2010), publicly identifiable national composition database. The remaining ~100 countries depend on FAO/INFOODS regional aggregates (West African FCT, ASEANFOODS regional table, LATINFOODS regional, NEMEDIFOODS regional), borrowed values from neighbors / former colonial-power tables, or USDA SR fallback. **For NutriMe, this is the dominant gap pattern** of the top-150 surface.
- **Harmonization on units, nutrient definitions, ingredient identifiers:** Genuinely problematic. Same-named nutrients have multiple analytical definitions (fiber: crude vs. AOAC vs. AOAC 2009.01; vitamin A: retinol activity equivalents vs. retinol equivalents vs. IU; folate: total folate vs. dietary folate equivalents; protein: Kjeldahl × 6.25 vs. species-specific factor). **INFOODS tagnames** (§D.1) are the canonical harmonization layer; **LanguaL** and **FoodEx2** address food-identity harmonization but are unevenly adopted. There is **no globally complete crosswalk** — building one is a non-trivial engineering deliverable.
- **State of branded product coverage internationally:** **Open Food Facts is the de facto global standard** by item count and geographic breadth, but Tier 4 by default and ODbL-encumbered. **USDA FDC Branded** is the best for US (and bleeds in some multinational items). EU has no consolidated equivalent — branded data lives inside national databases (CIQUAL has some), regulator label-monitoring programs, or commercial sources (GS1 GDSN, Label Insight, IRI/Circana, Mintel GNPD). **No regional gold standard exists** comparable to Open Food Facts' breadth.
- **Cultural / religious-specific food coverage:** Composition databases generally do **not** capture certification properties (halal, kosher) — these need to be layered as separate metadata sourced from certifying bodies. Traditional preparations (Ayurvedic six-tastes/dosha categorization, Jain restrictions on root vegetables and alliums, Buddhist vegetarian distinctions, Mediterranean/Greek Orthodox fasting calendars) are dietary-classification systems with no composition-database equivalent — they require independent metadata models. Indigenous food coverage is the deepest gap and is partially addressed by the Kuhnlein/CINE program (FAO publications) but remains chronically incomplete.

## References

> All accessed 2026-04-28 unless noted. URLs included for re-verification (this sweep was unable to use WebFetch/WebSearch — see methodological note at top of Findings).

### Primary database maintainer pages

- **USDA Agricultural Research Service** (2026). *FoodData Central*. United States Department of Agriculture. https://fdc.nal.usda.gov/. License: US federal public domain. Accessed 2026-04-28.
- **USDA Agricultural Research Service** (2026). *FoodData Central API*. https://fdc.nal.usda.gov/api-guide.html. Accessed 2026-04-28.
- **USDA ARS Nutrient Data Laboratory** (2007). *USDA Table of Nutrient Retention Factors, Release 6*. https://www.ars.usda.gov/northeast-area/beltsville-md-bhnrc/beltsville-human-nutrition-research-center/methods-and-application-of-food-composition-laboratory/mafcl-site-pages/retention-factors/. Accessed 2026-04-28.
- **Health Canada** (2015 + ongoing updates). *Canadian Nutrient File (CNF)*. Bureau of Nutritional Sciences. https://food-nutrition.canada.ca/cnf-fce/. License: Open Government Licence – Canada 2.0. Accessed 2026-04-28.
- **Office for Health Improvement and Disparities (OHID), UK** (2021). *McCance and Widdowson's Composition of Foods Integrated Dataset (CoFID)*. https://www.gov.uk/government/publications/composition-of-foods-integrated-dataset-cofid. License: Open Government Licence v3.0. Accessed 2026-04-28.
- **Roberts, H.M. (ed.)** (2021). *McCance and Widdowson's The Composition of Foods*, 8th summary edition. Royal Society of Chemistry. ISBN 978-1-83916-079-4.
- **Food Standards Australia New Zealand (FSANZ)** (2022). *Australian Food Composition Database, Release 2.0* (and *AUSNUT 2011–13*). https://www.foodstandards.gov.au/science-data/monitoringnutrients/afcd. License: CC-BY 3.0 AU. Accessed 2026-04-28.
- **Plant & Food Research / Manatū Hauora Ministry of Health New Zealand** (2024). *New Zealand Food Composition Database (NZFCD) — FOODfiles*. https://www.foodcomposition.co.nz/. Accessed 2026-04-28.
- **ANSES** (2020). *Table de composition nutritionnelle Ciqual*. Agence nationale de sécurité sanitaire de l'alimentation, de l'environnement et du travail. https://ciqual.anses.fr/. License: Etalab Open License 2.0. Accessed 2026-04-28.
- **Max Rubner-Institut** (current). *Bundeslebensmittelschlüssel (BLS)*. https://www.blsdb.de/. License: proprietary / paid. Accessed 2026-04-28.
- **RIVM** (current). *NEVO Online — Nederlands Voedingsstoffenbestand*. National Institute for Public Health and the Environment, Netherlands. https://nevo-online.rivm.nl/. Accessed 2026-04-28.
- **DTU National Food Institute** (current). *Frida — Food Data*. Technical University of Denmark. https://frida.fooddata.dk/. Accessed 2026-04-28.
- **Finnish Institute for Health and Welfare (THL)** (current). *Fineli — Finnish Food Composition Database* (with public REST API). https://fineli.fi/. Accessed 2026-04-28.
- **Norwegian Food Safety Authority + University of Oslo** (current). *Matvaretabellen*. https://www.matvaretabellen.no/. Accessed 2026-04-28.
- **Livsmedelsverket (Swedish Food Agency)** (current). *Livsmedelsdatabasen*. https://www.livsmedelsverket.se/livsmedel-och-innehall/naringsamne/livsmedelsdatabasen. Accessed 2026-04-28.
- **AESAN / BEDCA Consortium** (current). *Base de Datos Española de Composición de Alimentos (BEDCA)*. https://www.bedca.net/. Accessed 2026-04-28.
- **CREA Alimenti e Nutrizione** (current). *Tabelle di composizione degli alimenti*. https://www.crea.gov.it/-/tabelle-di-composizione-degli-alimenti. Accessed 2026-04-28.
- **MEXT Japan** (2020). *Standard Tables of Food Composition in Japan — 2020 (Eighth Revised Edition)*. Council for Science and Technology, Subcommittee on Resources. https://www.mext.go.jp/en/policy/science_technology/policy/title01/detail01/1374030.htm. Accessed 2026-04-28.
- **National Institute for Nutrition and Health (NINH), China CDC** (2018–2019). *China Food Composition Tables, 6th edition*, Standard Edition Vol. 1 & 2. Peking University Medical Press. ISBN 978-7-5659-1786-2 / 978-7-5659-1787-9.
- **Longvah, T., Ananthan, R., Bhaskarachary, K., Venkaiah, K.** (2017). *Indian Food Composition Tables*. National Institute of Nutrition, Indian Council of Medical Research, Hyderabad. https://www.ifct2017.com/. Accessed 2026-04-28.
- **Universidade de São Paulo, FoRC** (current). *Tabela Brasileira de Composição de Alimentos (TBCA)*. https://www.tbca.net.br/. Accessed 2026-04-28.
- **NEPA-UNICAMP** (2011). *Tabela Brasileira de Composição de Alimentos (TACO)*, 4th ed. http://www.nepa.unicamp.br/taco/. Accessed 2026-04-28.
- **South African Medical Research Council** (current). *South African Food Composition Database (SAFOODS)*. https://safoods.mrc.ac.za/. Accessed 2026-04-28.
- **FAO/INFOODS** (current). *International Network of Food Data Systems*. Food and Agriculture Organization of the United Nations. https://www.fao.org/infoods/infoods/en/. Accessed 2026-04-28.
- **FAO/INFOODS** (2019). *FAO/INFOODS Food Composition Table for Western Africa, 2nd ed.* https://www.fao.org/3/ca7779b/CA7779B.PDF. Accessed 2026-04-28.
- **FAO/INFOODS** (current). *FAO/INFOODS Global Food Composition Database for Fish and Shellfish (uFiSh) and for Pulses (uPulses)*. https://www.fao.org/infoods/infoods/tables-and-databases/faoinfoods-databases/en/. Accessed 2026-04-28.
- **EuroFIR AISBL** (current). *FoodEXplorer and member national food composition databases*. https://www.eurofir.org/. Accessed 2026-04-28.
- **Rural Development Administration, Korea** (2021). *Korean Food Composition Database, 10th revision*. National Institute of Agricultural Sciences. https://koreanfood.rda.go.kr/. Accessed 2026-04-28.

### Branded / packaged-product references

- **Open Food Facts** (current). *Open Food Facts global product database*. https://world.openfoodfacts.org/ and https://wiki.openfoodfacts.org/API. License: ODbL 1.0 (database) + DbCL (contents). Accessed 2026-04-28.
- **MenuStat** (project archive). NYC Department of Health and Mental Hygiene. https://www.menustat.org/. Accessed 2026-04-28.
- **Nutritionix** (current). *Nutritionix Branded and Restaurant Database API*. https://www.nutritionix.com/business/api. License: commercial / freemium. Accessed 2026-04-28.

### Harmonization standards

- **Klensin, J.C., Feskanich, D., Lin, V., Truswell, A.S., Southgate, D.A.T.** (1989). *Identification of Food Components for INFOODS Data Interchange*. United Nations University Press.
- **FAO/INFOODS** (current). *INFOODS Tagnames for Food Components*. https://www.fao.org/infoods/infoods/standards-guidelines/food-component-identifiers-tagnames/en/. Accessed 2026-04-28.
- **LanguaL Technical Committee** (current). *LanguaL — the international framework for food description*. https://www.langual.org/. Accessed 2026-04-28.
- **EFSA** (current). *FoodEx2 standardised food classification and description system*. European Food Safety Authority. https://www.efsa.europa.eu/en/data-report/food-classification-standards. Accessed 2026-04-28.
- **FoodOn Consortium** (current). *FoodOn — A Farm-to-Fork Ontology*. https://foodon.org/. License: CC-BY 4.0. Accessed 2026-04-28.

### Cooking transformation literature

- **USDA ARS** (2007). *USDA Table of Nutrient Retention Factors, Release 6*. Nutrient Data Laboratory, Beltsville Human Nutrition Research Center. (See URL above.)
- **Bognar, A.** (2002). *Tables on weight yield of food and retention factors of food constituents for the calculation of nutrient composition of cooked foods (dishes)*. Berichte der Bundesforschungsanstalt für Ernährung, BFE-R-02-03, Karlsruhe.
- **Bognar, A. & Piekarski, J.** (2000). Guidelines for recipe information and calculation of nutrient composition of prepared foods (dishes). *Journal of Food Composition and Analysis*, 13(4), 391–410. https://doi.org/10.1006/jfca.2000.0922
- **Bell, S., Becker, W., Vásquez-Caicedo, A.L., Hartmann, B., Møller, A., Butriss, J.** (2006). Promoting food information exchange across Europe using food composition data — a review of food composition data quality. *European Journal of Clinical Nutrition*, 60(11), 1308–1317. https://doi.org/10.1038/sj.ejcn.1602455
- **Vásquez-Caicedo, A.L., Bell, S., Hartmann, B.** (2008). *Report on collection of rules on use of recipe calculation procedures including the use of yield and retention factors for imputing nutrient values for composite foods*. EuroFIR Technical Report.
- **Reinivuo, H., Bell, S., Ovaskainen, M.-L.** (2009). Harmonisation of recipe calculation procedures in European food composition databases. *Journal of Food Composition and Analysis*, 22(5), 410–413. https://doi.org/10.1016/j.jfca.2009.04.001
- **Schakel, S.F., Buzzard, I.M., Gebhardt, S.E.** (1997). Procedures for estimating nutrient values for food composition databases. *Journal of Food Composition and Analysis*, 10(2), 102–114. https://doi.org/10.1006/jfca.1997.0527
- **Greenfield, H. & Southgate, D.A.T.** (2003). *Food composition data: production, management and use*, 2nd ed. Food and Agriculture Organization of the United Nations. https://www.fao.org/3/y4705e/y4705e00.htm. Accessed 2026-04-28.
- **Kapsokefalou, M., Roe, M., Turrini, A., Costa, H.S., Martinez-Victoria, E., Marletta, L., Berry, R., Finglas, P.** (2019). Food composition at present: new challenges. *Nutrients*, 11(8), 1714. https://doi.org/10.3390/nu11081714
- **Kuhnlein, H.V., Erasmus, B., Spigelski, D., Burlingame, B.** (eds.) (2013). *Indigenous Peoples' food systems & well-being: interventions & policies for healthy communities*. FAO and Centre for Indigenous Peoples' Nutrition and Environment (CINE). https://www.fao.org/3/i3144e/i3144e.pdf. Accessed 2026-04-28.
