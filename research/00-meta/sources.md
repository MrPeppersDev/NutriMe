# NutriMe — Master Sources Index

> Navigational index of research source coverage across sweeps. Per-sweep `## References` sections are the source of truth for full citations; this doc summarizes what was sourced, organizes by domain, and surfaces cross-cutting sources.

## How this doc works

Each domain section contains:

- **What we sourced:** a brief (1–3 sentence) summary of the kinds of sources catalogued for the domain.
- **Sweep coverage:** which sweep(s) own the domain, with links to their `## References` sections (the canonical full citations).
- **Cross-cutting sources** (where applicable): sources cited in 2+ sweeps, briefly noted with which sweeps cite them and why. No full citations — those live in the per-sweep References.

This file is a navigation aid, not a citation aggregator. Do not duplicate the content of per-sweep References here.

## How to add to this doc

When a new sweep is researched:

1. Add a one-paragraph summary of what was sourced under the appropriate domain section (or create a new domain section if needed).
2. Link to the new sweep's `## References` section.
3. If the sweep cites a source that already appears in another sweep, add it (or update its entry) under the **Cross-cutting sources** subsection of the relevant domain.
4. Update the `## Aggregation notes` section at the bottom: total sweeps covered, notable cross-cutting sources, observed gaps, consolidation date.

Sweep References live in:

- Sweep #1: [01-international-nutrition-standards/scope.md#references](../01-international-nutrition-standards/scope.md#references)
- Sweep #2: [02-food-composition-databases/scope.md#references](../02-food-composition-databases/scope.md#references)
- Sweep #3: [03-clinical-nutrition-assessment/scope.md#references](../03-clinical-nutrition-assessment/scope.md#references)
- Sweep #4: [04-adaptive-intake-agent/scope.md#references](../04-adaptive-intake-agent/scope.md#references)
- Sweep #5: [05-personalized-nutrition-evidence/scope.md#references](../05-personalized-nutrition-evidence/scope.md#references)
- Sweep #6: [06-wearable-data-availability/scope.md#references](../06-wearable-data-availability/scope.md#references)
- Sweep #7: [07-cooking-behavioral-barriers/scope.md#references](../07-cooking-behavioral-barriers/scope.md#references)
- Sweep #8: [08-nutrition-education-delivery/scope.md#references](../08-nutrition-education-delivery/scope.md#references)
- Sweep #9: [09-multi-user-household/scope.md#references](../09-multi-user-household/scope.md#references)
- Sweep #10: [10-clinical-condition-gating/scope.md#references](../10-clinical-condition-gating/scope.md#references)
- Sweep #11: [11-recipe-sourcing/scope.md#references](../11-recipe-sourcing/scope.md#references)
- Sweep #12: [12-skills-by-cuisine/scope.md#references](../12-skills-by-cuisine/scope.md#references)
- Sweep #13: [13-grocery-infrastructure/scope.md#references](../13-grocery-infrastructure/scope.md#references)

---

## International nutrition standards bodies + dietary patterns

**What we sourced:** National and supranational nutrient-requirement frameworks (NASEM DRI, EFSA DRV, WHO, FAO/WHO/UNU technical reports, SACN, NHMRC, Health Canada, Nordic Council NNR2023, MHLW Japan, ICMR-NIN India, Chinese Nutrition Society, Brazil/DGE/PNNS/Netherlands/Belgium/Switzerland/Korea/Israel/Russia, Codex Alimentarius), USDA/HHS Dietary Guidelines + MyPlate, NHLBI DASH, the foundational pattern trials (DASH 1997, DASH-Sodium 2001, PREDIMED 2013/2018, MIND 2015/2023), the EAT-Lancet Commission, and major secondary-pattern references (Harvard Healthy Eating Plate, Eatwell Guide, UNESCO Mediterranean ICH, PROT-AGE, Te Morenga sugars SR).

**Sweep coverage:**

- [Sweep #1 — international nutrition standards](../01-international-nutrition-standards/scope.md#references) — canonical owner; ~55 sources
- [Sweep #5 — personalized nutrition evidence](../05-personalized-nutrition-evidence/scope.md#references) — re-cites the population-pattern baseline against which personalization is measured
- [Sweep #9 — multi-user household](../09-multi-user-household/scope.md#references) — cites Mediterranean / EAT-style pattern literature in the commensality + household-meal context

**Cross-cutting sources:**

- *WHO healthy-diet guidance + sugars/sodium/fats guidelines* — sweeps #1, #5, #8, #10. Population-level nutrient targets feed both education content and clinical-condition gating.
- *USDA/HHS Dietary Guidelines for Americans 2020–2025* — sweeps #1, #5, #8, #9 (B-24 chapter). Anchors US-context defaults across multiple domains.
- *PREDIMED (Estruch et al. 2013/2018)* — sweeps #1, #3 (MEDAS administered cohort), #5, #9. The dominant Mediterranean RCT.
- *DASH (Appel 1997 + Sacks 2001)* — sweeps #1, #5. Foundational pattern trials.
- *MIND diet (Morris 2015 + Barnes 2023)* — sweeps #1, #3 (pattern-screener context). Cohort + RCT evidence for cognition.
- *EAT-Lancet (Willett 2019)* — sweeps #1, #9. Planetary-health diet framework.
- *PROT-AGE (Bauer 2013)* — sweeps #1, #10 (geriatric ESPEN context). Older-adult protein recommendation.
- *UNESCO Mediterranean Diet ICH inscription* — sweeps #1, #11. Cultural-heritage framing.
- *NHMRC Australian Dietary Guidelines* + *Health Canada Food Guide* + *NHS Eatwell* — sweeps #1, #5, #8. Multi-jurisdiction dietary-guideline anchors.

---

## Food composition databases

**What we sourced:** National food composition tables (USDA FDC + API, Health Canada CNF, OHID McCance & Widdowson CoFID, FSANZ + AUSNUT, NZFCD, ANSES CIQUAL, BLS Germany, NEVO Netherlands, Frida Denmark, Fineli Finland, Matvaretabellen Norway, Livsmedelsverket Sweden, BEDCA Spain, CREA Italy, MEXT Japan, China FCT, Indian Food Composition Tables, TBCA Brazil, TACO legacy, SAFOODS South Africa, Korean FCT) plus harmonization standards (FAO/INFOODS, EuroFIR, LanguaL, FoodEx2, FoodOn), brand-product datasets (Open Food Facts + API, MenuStat, Nutritionix), and the methods literature (Bognar retention factors, EuroFIR recipe-calculation guidelines, Greenfield & Southgate, INFOODS tagnames, Schakel et al.).

**Sweep coverage:**

- [Sweep #2 — food composition databases](../02-food-composition-databases/scope.md#references) — canonical owner; ~72 sources
- [Sweep #13 — grocery infrastructure](../13-grocery-infrastructure/scope.md#references) — re-cites USDA FDC and EuroFIR as reference layers for product↔ingredient mapping

**Cross-cutting sources:**

- *USDA FoodData Central (FDC) + API* — sweeps #2, #11 (recipe-side use), #13 (product-side use).
- *Open Food Facts (data + API)* — sweeps #2, #13. ODbL brand-product dataset used for both composition and grocery-product matching.
- *EuroFIR* — sweeps #2, #13. European composition-data harmonization layer.
- *FAO/INFOODS regional tables and tagnames* — sweep #2 (primary), referenced in #1 for geographic scope.

---

## Wearable + biometric data sources

**What we sourced:** Vendor APIs and SDKs (Apple HealthKit + Health Records + Heart Study; Garmin, Whoop, Oura, Fitbit/Google, Health Connect, Polar AccessLink + BLE, Coros, Withings, Wahoo, Suunto, Zepp/Amazfit, Samsung Health, Strava, Dexcom, Abbott LibreView), clinical-data standards (HL7 FHIR R4 US Core, FHIR IPS, ONC Cures Act, Epic / Oracle Health / Athenahealth / LabCorp / Quest portals), open-source / patient-controlled stacks (Nightscout, xDrip+, Tidepool, OpenAPS, Home Assistant, Gadgetbridge, OpenScale, OpenmHealth, openEHR, Solid), aggregator APIs (Terra, Vital, Spike, Validic, 1upHealth), national health portals (NHS App + GP Connect, My Health Record, MyHealthWay), and a privacy-regulation panel (HIPAA, Cures Act / info-blocking, FTC Health Breach Notification, GDPR, EHDS, PIPEDA, OAIC APPs, NZ Code, PIPL, APPI, PIPA, LGPD, Israel PPL, Russia 152-FZ, EU MDR), plus device-validation literature (Apple Heart Study, optical-HR-by-skin-tone, Oura sleep, WHOOP sleep, Fitbit SR, Dexcom G7, Aktiia BP, Withings Sleep Analyzer, Bandodkar sweat, CORE temperature, Lumen).

**Sweep coverage:**

- [Sweep #6 — wearable data availability](../06-wearable-data-availability/scope.md#references) — canonical owner; ~61 sources
- [Sweep #4 — adaptive intake agent](../04-adaptive-intake-agent/scope.md#references) — re-cites HL7 FHIR Questionnaire/SDC + SMART on FHIR for structured-intake persistence
- [Sweep #5 — personalized nutrition evidence](../05-personalized-nutrition-evidence/scope.md#references) — references Dexcom Stelo + Abbott Lingo as OTC-CGM context for n-of-1 nutrition
- [Sweep #9 — multi-user household](../09-multi-user-household/scope.md#references) — wearable-data sharing flagged as a privacy-design intersection (cross-link, not duplicated)

**Cross-cutting sources:**

- *HL7 FHIR family (R4 US Core, IPS, Questionnaire, SDC, SMART on FHIR)* — sweeps #4, #6. Interoperability backbone for both device data and structured-intake persistence.
- *HIPAA Privacy Rule + ONC Cures Act / info-blocking* — sweeps #4, #6, #10. Cited for both PHR/PGHD framing and CDS regulatory context.
- *GDPR (EU 2016/679)* — sweeps #4, #6, #10. Pan-domain data-protection anchor.
- *EU AI Act (Regulation 2024/1689)* — sweeps #4, #10. Governs AI-mediated health features (intake, CDS).
- *Dexcom + Abbott CGM platforms* — sweeps #5 (Stelo/Lingo OTC), #6 (Dexcom developer portal + LibreView).

---

## Recipe sources, IP, and standards

**What we sourced:** Recipe APIs and aggregators (Spoonacular, Edamam, TheMealDB, Samsung Food/Whisk), major culinary publishers (NYT Cooking, Bon Appétit, Epicurious, Serious Eats, ATK, Eater, Food52, King Arthur, BBC Good Food, NHS Eat Well, Marmiton, 750g, Chefkoch, EatSmarter, GialloZafferano, El Comidista, AllerHande, Health Canada Recipes, Hansik, MAFF Shokuiku), recipe datasets (RecipeNLG, Recipe1M+, Food.com on Kaggle, OpenRecipes, Common Crawl, schema.org/Recipe), historical archives (Project Gutenberg, HathiTrust, Internet Archive, LoC rare books, Schlesinger Library, MSU Feeding America, Gallica, DDB, Europeana, Wellcome) plus canonical historical works (Apicius, La Varenne, Beeton, Farmer, Carême, Glasse, Escoffier, al-Warraq, Yuan Mei, Eumsik Dimibang), modern community/curation platforms (Eat Your Books, ckbk, Cookpad, Kitchen Stories), Slow Food / NATIFS / First Nations indigenous-food bodies, and the recipe-IP literature (Publications International v. Meredith, Tomaydo-Tomahhdo, Feist, 17 USC §102, EU Database/InfoSoc Directives, Infopaq, Painer, CCH Canadian, IceTV, plus national copyright acts), and recipe interchange formats (Cooklang, hRecipe, h-recipe, RecipeML, Open Recipe Format).

**Sweep coverage:**

- [Sweep #11 — recipe sourcing](../11-recipe-sourcing/scope.md#references) — canonical owner; ~50 sources
- [Sweep #9 — multi-user household](../09-multi-user-household/scope.md#references) — references recipe corpora supporting common-base + per-plate-deltas architecture (cross-link)
- [Sweep #13 — grocery infrastructure](../13-grocery-infrastructure/scope.md#references) — references recipe-to-cart open-source prior art (Mealie, Tandoor, Grocy, OurGroceries, AnyList, Bring!, Paprika)

**Cross-cutting sources:**

- *schema.org/Recipe* — sweep #11 (interchange standard); de facto recipe interop backbone touched by anything ingesting web recipes.
- *Cooklang* — sweep #11. LLM-friendly DSL of interest beyond recipe sourcing per se.
- *USDA FDC + EuroFIR* — sweeps #2, #11, #13 (see Food composition).

---

## Culinary technique + culinary education references

**What we sourced:** Professional curricula and culinary academies (CIA, ICE, Le Cordon Bleu, Institut Paul Bocuse / Lyfe, Ferrandi Paris, Ducasse ENSP, ALMA, ICIF, Tsuji Culinary Institute, Hattori Nutrition College, Indian Culinary Institute, NCHM IHM Network, NIN India, ICAR, China Cuisine Association, ICUM Mexico, CONABIO, Johnson & Wales, Leiths, University of Gastronomic Sciences Pollenzo), canonical technique reference texts (CIA *Professional Chef*; Larousse Gastronomique; Labensky & Hause *On Cooking*; *Joy of Cooking*; McGee *On Food and Cooking*; Modernist Cuisine; Pépin *La Technique*), cuisine-specific authoritative texts (Tsuji, Andoh, Dunlop, Hazan, Wolfert, D. Kennedy, Bayless, Iyer, Jaffrey, Maangchi, Ricker, Thompson, Nguyen, Ottolenghi/Tamimi, Roden, Meyer, Edge, Lewis), skill-domain specialists (Forkish, Robertson, Ruhlman/Polcyn, Katz, Redzepi/Zilber, Friberg, Weinstein, J. Kenji López-Alt, Nosrat), and academic culinary-education research (Caraher/Lang/Dixon/Carr-Hill, Vidgen & Gallegos food literacy, Mills et al. SR, Engler-Stringer review), plus subscription/online platforms (MasterClass, Rouxbe, ATK Cooking School, King Arthur Baking School, ChefSteps).

**Sweep coverage:**

- [Sweep #11 — recipe sourcing](../11-recipe-sourcing/scope.md#references) — owns the technique-reference canon
- [Sweep #12 — skills by cuisine](../12-skills-by-cuisine/scope.md#references) — owns the culinary-curriculum and cuisine-text enumeration

**Cross-cutting sources:**

- *CIA *The Professional Chef** — sweeps #11, #12, #9 (mise-en-place / station-modular framing).
- *McGee *On Food and Cooking** — sweeps #11, #12. Cross-cuisine science-of-cooking reference.
- *Larousse Gastronomique (Montagné)* — sweeps #11, #12, #13 (substitution reference).
- *Modernist Cuisine (Myhrvold)* — sweeps #11, #12.
- *Labensky & Hause *On Cooking** — sweeps #11, #12.
- *Escoffier *Le Guide Culinaire** — sweeps #11, #9 (mother-sauce / common-base architecture).

---

## Clinical nutrition assessment instruments

**What we sourced:** Clinical assessment frameworks (NCP/NCPT, SGA, PG-SGA, MNA + MNA-SF, MST, BAPEN MUST, ESPEN clinical-nutrition definitions, GLIM, NRS-2002), pattern-based dietary screeners (MEDAS, HEI-2015/2020, AHEI-2010, DASH score, MIND, PDI/hPDI/uPDI, Food Choice Questionnaire, Food Neophobia Scale), recall-based instruments (USDA AMPM, ASA24, NCI DHQ III, Block FFQ, EPIC FFQ comparative work), eating-disorder screeners (SCOFF, EAT-26, ESP, EDE-Q), food-security tools (Hunger Vital Sign, USDA 6-item HFSSM, Children's FSSM), AUDIT / AUDIT-C, IPAQ / GPAQ, TTM and Motivational Interviewing references (Prochaska & DiClemente; Miller & Rollnick), sleep (PSQI, SCI, STOP-BANG), mood/anxiety (PHQ-9/PHQ-2, GAD-7/GAD-2), PSS, Rome IV functional GI, eating-behavior scales (TFEQ, IES-2, DEBQ, YFAS, ORTO-15/-R), cooking confidence (CCSS / Lavelle), health literacy (REALM-SF, TOFHLA, NVS, eHEALS), pediatric instruments (NutriSTEP preschool + school-age, CDC + WHO growth charts, AAP Bright Futures, KEDS, ChEAT, NIAS, PARDI, NIAID food-allergy guidelines, USDA Children's FSSM), cultural competency (Campinha-Bacote, ACEND standards, Kittler/Sucher/Nelms textbook), trauma-informed approaches (SAMHSA, Tylka et al. weight-inclusive, Tribole & Resch *Intuitive Eating*), and process/methodology references (Chen et al. patient activation, PROMIS).

**Sweep coverage:**

- [Sweep #3 — clinical nutrition assessment](../03-clinical-nutrition-assessment/scope.md#references) — canonical owner; ~95 unique sources
- [Sweep #4 — adaptive intake agent](../04-adaptive-intake-agent/scope.md#references) — references the same instrument bank as candidates for IRT/CAT delivery
- [Sweep #7 — cooking behavioral barriers](../07-cooking-behavioral-barriers/scope.md#references) — re-cites Lavelle CCSS + cooking-confidence instruments
- [Sweep #9 — multi-user household](../09-multi-user-household/scope.md#references) — cites pediatric instruments and Bisogni/Sobal qualitative work

**Cross-cutting sources:**

- *PROMIS / HealthMeasures (Cella et al.)* — sweeps #3, #4. Item-bank methodology for CAT-based intake.
- *Lavelle et al. (2017) cooking + food skills measures* — sweeps #3, #4, #7. Validated cooking-confidence screener used across assessment, intake, and behavioral-barrier work.
- *Miller & Rollnick *Motivational Interviewing*** — sweeps #3, #4, #8. MI as the cross-cutting behavior-change clinical framework.
- *SAMHSA Trauma-Informed Approach (2014)* — sweeps #3, #4. Cross-references to trauma-informed assessment + chatbot design.
- *Campinha-Bacote (2002)* — sweeps #3, #4, #8. Cultural-competence model.
- *AAP Bright Futures (2017)* — sweeps #3, #9, #10. Pediatric primary-care framework.
- *CDC + WHO Growth Standards* — sweeps #3, #10. Child-growth reference layer.
- *NIAID food-allergy guidelines (Boyce 2010, Togias 2017) + LEAP (Du Toit 2015)* — sweeps #3, #9, #10. Pediatric allergen-introduction evidence base.

---

## Adaptive intake / conversational agent + clinical informatics

**What we sourced:** Foundational psychometric methodology for adaptive testing (Lord IRT; Wainer CAT primer; van der Linden & Glas; Reise & Waller; Cella; Gibbons multi-dimensional + CAT for depression; Chalmers mirt R package), PROMIS / IRT bank validation (Pilkonis distress; Yu sleep; Buysse PROs; Lai fatigue; Salsman NIH Toolbox; Gruber-Baldini self-efficacy; Petersen EORTC CAT), conversational AI intake validation (Woebot RCT, Wysa, Tess, Replika harms work, Maples GPT3 chatbot, Habicht 2024 *Nature Medicine* self-referral chatbot, Singhal LLMs encode clinical knowledge, Tu *Towards conversational diagnostic AI*, Razzaki AI triage, Fraser symptom-checker safety), human MI evidence (Lundahl 2013, Frost 2018, Armstrong 2011, Spencer & Wheeler, Morton 2015), AI-MI (Park, Almusharraf, Galvão Gomes da Silva, He), structured intake / informatics (REDCap, PhenX Toolkit, Denecke), longitudinal measurement (Jacobson & Truax reliable change, longitudinal IRT, PRO implementation, Lorig & Holman self-management, Wagner chronic-care model), EMA/JITAI (Stone & Shiffman, Shiffman 2008, Nahum-Shani 2018, Martin RFPM), disclosure/psych safety with virtual humans (Lucas; Ho/Hancock/Miner; Henson engagement), shared decision-making (Schillinger, Elwyn, Stacey Cochrane, Behaviour Change Wheel), trauma-informed and cultural adaptation (SAMHSA, Campinha-Bacote, Castro/Barrera/Steiker, Resnicow, Kreuter), platforms/standards (HealthMeasures, NIH CDE, REDCap, OpenMRS, FHIR Questionnaire + SDC, SMART on FHIR, Assessment Center API, CAT-MH, Concerto, mirt, Rasa, Botpress, OpenDialog, Azure Health Bot, CDISC CDASH, AHRQ Health Literacy Universal Precautions Toolkit, CDC Clear Communication Index, MITI 4.2.1, MINT, IPDAS), and regulatory frameworks (EU AI Act, GDPR, HIPAA, ONC info-blocking, ONC PGHD framework).

**Sweep coverage:**

- [Sweep #4 — adaptive intake agent](../04-adaptive-intake-agent/scope.md#references) — canonical owner

**Cross-cutting sources:** see the cross-cutting notes under *Clinical nutrition assessment instruments* (PROMIS, MI, SAMHSA, Campinha-Bacote, Lavelle), *Wearable + biometric data sources* (FHIR family, HIPAA, Cures Act, GDPR, AI Act), and *Behavior change frameworks + health literacy + plain language* (Behaviour Change Wheel, BCT taxonomy v1).

---

## Behavior change frameworks + health literacy + plain language

**What we sourced:** Behavior-change theory canon (Theory of Planned Behavior — Ajzen, McEachan; TTM — Prochaska & DiClemente, Bridle SR, Cahill smoking-cessation Cochrane; Health Belief Model — Janz & Becker, Rosenstock; Self-Determination Theory — Deci & Ryan, Ng meta-analysis, Teixeira PA SR; HAPA — Schwarzer; Behaviour Change Wheel — Michie et al. 2011; BCT taxonomy v1 — Michie et al. 2013; Implementation intentions — Hagger & Luszczynska, Carraro & Gaudreau; PHE behaviour-change guide; Cradock T2D BCT SR; Hankonen diabetes BCTs; Samdal SR meta-regression; Sen capabilities + Burchi & De Muro food-capabilities), health-literacy assessment + frameworks (REALM-SF, TOFHLA, NVS, eHEALS, HLQ, HLS-EU + HLS19, Korean/Japanese/Chinese national instruments, WHO health-literacy series, ACSQHC Australia, HHS/ODPHP Healthy People 2030), readability/content design (AMA manual, CDC Clear Communication Index, SMOG, Eltorai/Stossel readability studies), tailored / adaptive content (Krebs computer-tailored meta-analysis, Noar tailored print meta-analysis, VanLehn tutoring, Wood/Bruner/Ross scaffolding), microlearning / spaced-repetition (Cepeda spacing, Dunlosky learning techniques, Hug microlearning, Kerfoot spaced-education RCTs, Roediger & Karpicke testing effect, Larsen, De Gagne, Lally habit formation, Sepah DPP-online), visual / graphical communication (Crockett labelling Cochrane, Egnell front-of-pack, Galesic icon arrays, Garcia-Retamero & Cokely visual aids SR, Gigerenzer numeracy, Hercberg Nutri-Score, NZ Health Star Rating, PHE Eatwell Guide, Sacks traffic-light, Singapore Nutri-Grade, Spiegelhalter uncertainty, Taillie Chile law, USDA/HHS DGA, Willett & Stampfer), uncertainty/confidence visualization (Buchter words-vs-numbers SR, Cochrane plain-language summary work, GRADE — Guyatt et al., Gustafson & Rice, NICE manual, Rosenbaum/Santesso summary-of-findings, Schünemann Cochrane handbook, van der Bles uncertainty-trust, Vandvik clinical-guideline trust), causal-explanation depth (Lombrozo, Miller XAI, Petty & Cacioppo ELM, Rozenblit & Keil illusion of explanatory depth, Wei chain-of-thought), adult learning (Knowles, Brookfield, Kolb, Mezirow, Tough), trust/credibility in AI-mediated info (Ayers JAMA-IM physician-vs-chatbot, ICMJE AI-authorship), and plain-language standards (Cochrane PLS standards, ISO 24495-1:2023, Plain Writing Act 2010, plainlanguage.gov, Health COMpass).

**Sweep coverage:**

- [Sweep #8 — nutrition education delivery](../08-nutrition-education-delivery/scope.md#references) — canonical owner; ~120 sources
- [Sweep #4 — adaptive intake agent](../04-adaptive-intake-agent/scope.md#references) — re-cites BCW, MI, AHRQ Health Literacy Universal Precautions, CDC Clear Communication Index
- [Sweep #7 — cooking behavioral barriers](../07-cooking-behavioral-barriers/scope.md#references) — overlaps in BCT / habit-formation / time-scarcity literature
- [Sweep #9 — multi-user household](../09-multi-user-household/scope.md#references) — cites BCT taxonomy v1 + dyadic-intervention SR

**Cross-cutting sources:**

- *Behaviour Change Wheel (Michie, van Stralen & West 2011) + BCT Taxonomy v1 (Michie 2013)* — sweeps #4, #7, #8, #9. The shared behavior-change vocabulary.
- *TTM (Prochaska & DiClemente 1983; Prochaska & Velicer 1997)* — sweeps #3, #4, #8.
- *Lally et al. (2010) habit formation* — sweeps #7, #8.
- *AHRQ Health Literacy Universal Precautions Toolkit + CDC Clear Communication Index* — sweeps #4, #8.
- *PHE Eatwell Guide + USDA/HHS DGA* — sweeps #1, #5, #8.
- *Cochrane plain-language standards + GRADE* — sweep #8 (anchors the plain-language and uncertainty layer that all education content inherits).

---

## Personalized nutrition evidence + n-of-1 / precision-nutrition vendors

**What we sourced:** Personalized-nutrition RCTs and cohorts (Food4Me — Celis-Morales 2017; PREDIMED — Estruch 2018; DASH — Appel 1997; DASH-Sodium — Sacks 2001; DIETFITS — Gardner 2018; ZOE PREDICT-1 — Berry 2020, Asnicar microbiome 2021, Bermingham METHOD 2024; Personalized Nutrition Project — Zeevi 2015 + Mendes-Soares 2019; DPP — Knowler 2002; DiRECT — Lean 2018; WHI — Beresford 2006; Jinnette personalized-nutrition SR), n-of-1 methodology (Schork *Nature*; Vohra CENT 2015), program/initiative context (NIH Nutrition for Precision Health, Food4Me + Stance4Health Cordis, NHS Eatwell, USDA/HHS DGA, NHMRC, Health Canada, WHO healthy diet, UK Biobank, China Kadoorie Biobank, OCEBM levels of evidence), and vendor / commercial sources cited only for what they market (ZOE, Viome, DayTwo, DNAFit, Nutrigenomix, InsideTracker, Levels Health, Nutrisense, Dexcom Stelo, Abbott Lingo, 23andMe).

**Sweep coverage:**

- [Sweep #5 — personalized nutrition evidence](../05-personalized-nutrition-evidence/scope.md#references) — canonical owner

**Cross-cutting sources:**

- *PREDIMED, DASH, DASH-Sodium, MIND* — see *International nutrition standards bodies + dietary patterns* cross-cutting notes; sweep #5 re-cites these as the population-level baseline.
- *Dexcom + Abbott CGM platforms* — sweeps #5, #6.

---

## Cooking behavior + time-use / convenience-food literature

**What we sourced:** Time-use datasets (BLS ATUS, CDC NHANES, Eurostat HETUS, Oxford MTUS) + USDA-ERS bulletins (Saksena, Mancino & Newman, Hamrick); cooking-time / cooking-frequency / diet-quality peer-review (Wolfson & Bleich 2015, Wolfson 2016/2017, Smith/Ng/Popkin 2013, Monsivais 2014, Virudachalam NHANES 2007–08, Mills SR 2017 + Mills cohort 2017); cooking-confidence and food-skills instruments (Lavelle 2017 CCSS, Lavelle 2016 cooking-skills-by-age, McGowan SR + 2016 socio-demographic-prediction, Hartmann 2013, Burton, Barton/Wrieden, Short); cooking-intervention SRs (Reicks 2014 + 2018, Hasan 2019, Garcia 2016); behavioural / structural barriers — qualitative + survey (Bowen *Pressure Cooker* + *The Joy of Cooking?*; Caraher; Lang & Caraher; Jabs & Devine time-scarcity; Devine spillover + work-conditions; Daniels meanings of cooking; Escoto work-hours; Venn & Strazdins time-vs-money; Olsen RTE; Brunner convenience drivers); time-use cross-national / gender (Mestdag & Glorieux Belgium, Hook & Wolfe fathers, Warde changes-in-eating); ultra-processed-food consumption (Adams & White UK NDNS, Martínez Steele BMJ Open, Monteiro 19-country, Machado Australia, Moubarac Canada); cultural cooking light coverage (Tsugane Japan, Kim Korea, Zhai China, Misra India); equipment/kitchen-state (Engler-Stringer).

**Sweep coverage:**

- [Sweep #7 — cooking behavioral barriers](../07-cooking-behavioral-barriers/scope.md#references) — canonical owner

**Cross-cutting sources:**

- *Lavelle et al. cooking + food skills measures* — sweeps #3, #4, #7. See *Clinical nutrition assessment instruments*.
- *Bowen, Brenton & Elliott (Pressure Cooker + The joy of cooking?)* — sweeps #7, #9. Cooking-labor sociology.
- *Engler-Stringer (2010)* — sweeps #7, #12 (cooking skills review).
- *Monteiro / Martínez Steele UPF literature* — sweep #7 (also referenced loosely in #5 framing).

---

## Couple + household research

**What we sourced:** Couple-based dietary-intervention research (Burke 1999 health promotion in couples; Hartmann-Boyce OxFAB; Carr dyadic PA SR; Hagger & Hamilton TPB; Lewis & Butterfield social control; Pachucki spousal concordance Framingham; Michie BCT taxonomy v1); household-meal patterns by region (Mediterranean — Trichopoulou 2003, PREDIMED, Fischler commensality; East Asian — Kurotani JPHC, Du China, Lee Korea; Nordic + nuclear-family — Sayer time-use, Mäkelä Nordic meals, Holm Nordic eating-context, Hammons & Fiese family-meals meta-analysis, Project EAT, HOME Plus RCT, Larson breakfast/dinner-together; South Asian — Misra, Daniel regional patterns); US "second shift" / cooking-labor sociology (Hochschild & Machung, DeVault, Bowen Pressure Cooker, Bowen The joy of cooking?, Daminger cognitive labor); RD practice / behavior change (Spahn ADA review; Whitney/Rolfes RD textbook; Academy of Nutrition and Dietetics Evidence Analysis Library); Bisogni / Sobal food-choice process and household roles (identity + food choice; food-choice process model; healthy-eating interpretation; commensal careers; family-meals + body weight); common-base + per-plate-deltas in operational kitchens (Escoffier *Le Guide Culinaire*; CIA *Professional Chef*; Spears & Gregoire *Foodservice Organizations*); pediatric inclusion (AAP Bright Futures; WHO Complementary Feeding; USDA/HHS DGA Birth-24; LEAP — Du Toit 2015; NIAID 2017 addendum; Mennella flavor learning; Birch & Fisher; Wardle vegetable RCT; Cooke exposure review; Savage parental-influence review); privacy / shared EHR / family portals (Ancker patient-portal; Wolff OpenNotes; Latulipe proxy older-adult; Bourgeois pediatric/adolescent; Anoshiravani pediatric portal; Carlson teen/parent; Steitz long-term pediatric; Patel HIE/PHR; Levetown AAP); default-design (Thaler & Sunstein *Nudge*; Johnson & Goldstein defaults).

**Sweep coverage:**

- [Sweep #9 — multi-user household](../09-multi-user-household/scope.md#references) — canonical owner

**Cross-cutting sources:**

- *AAP Bright Futures*, *NIAID food-allergy guidelines + LEAP*, *CDC + WHO growth standards* — sweeps #3, #9, #10. See *Clinical nutrition assessment instruments*.
- *Michie BCT Taxonomy v1* — sweeps #4, #7, #8, #9.
- *Bowen Pressure Cooker / The joy of cooking?* — sweeps #7, #9.
- *Escoffier + CIA Professional Chef* — sweeps #9, #11, #12.
- *PREDIMED, EAT-Lancet* — sweeps #1, #5, #9.

---

## Clinical condition gating + drug-nutrient + regulatory frameworks

**What we sourced:** Cardiovascular guidelines (ACC/AHA hypertension 2017; ESC hypertension 2024; AHA/ACC/HFSA HF 2022); metabolic / endocrine (ADA Standards of Care 2025; ADA-EASD T2D 2022; AACE T2D algorithm 2023; AASLD MASLD 2023; PCOS 2023 international guideline); renal (KDOQI nutrition CKD 2020; KDIGO CKD 2024); GI (ACG IBS 2021; BSG IBS 2021; Monash FODMAP; ACG celiac 2023; ESPEN IBD nutrition 2023; AGA/JTF EoE 2022); hepatic (Tapper & Parikh AASLD cirrhosis; EASL decompensated cirrhosis 2022); autoimmune (ACR RA 2021; EULAR lifestyle 2023); eating disorders (APA 2023; NICE NG69; AED Medical Care Standards); oncology (WCRF/AICR Cancer Prevention Recommendations + CUP; ACS survivors 2022 — Rock; ESPEN cancer nutrition); bariatric (ASMBS/AACE/TOS/ASA 2019; BOMSS 2020); allergies / gout / osteoporosis (NIAID food-allergy guidelines; EAACI anaphylaxis 2022; ACR gout 2020; Endocrine Society osteoporosis 2019; LEAP 2015; AAP atopic-disease 2019); pediatric (AAP childhood-obesity 2023 — Hampl; NASPGHAN/ESPGHAN pediatric IBD 2022; ESPGHAN celiac 2020; ISPAD 2022; Ellyn Satter Division of Responsibility; WHO + CDC growth charts); life-stage (ACOG nutrition in pregnancy; WHO ANC 2016; NICE NG201; EFSA DRV; AAP breastfeeding 2022; NIH LactMed; WHO IYCF; Bright Futures Nutrition Pocket Guide; SAHM eating disorders adolescents 2022; ESPEN geriatrics 2022; PROT-AGE; IDDSI dysphagia framework v2.0; ACSM/AND/DC Athletic Performance 2016; IOC supplements 2018; IOC RED-S 2023); regulatory landscape (FDA General Wellness, FDA CDS, EU MDR 2017/745, MDCG 2019-11, EU AI Act 2024, MHRA SaMD programme, TGA software MDs, Health Canada SaMD, NMPA, PMDA, MFDS, IMDRF SaMD definitions, Israel AMAR, Roszdravnadzor); drug-nutrient interactions + alert fatigue (NLM DailyMed; openFDA; EMA EPAR/SmPCs; MHRA emc; NIH ODS supplement fact sheets; NHS food/drink/medicines; van der Sijs alert override; Ancker 2017 alert fatigue; Phansalkar high-priority DDIs; Co CDS appropriateness); pregnancy + lactation comparative (FDA fish advice; CDC Listeria; EFSA caffeine 2015 + mercury 2012; NHS / FSANZ / MHLW Japan / NHMRC / Health Canada / WHO / CDC breastfeeding meds).

**Sweep coverage:**

- [Sweep #10 — clinical condition gating](../10-clinical-condition-gating/scope.md#references) — canonical owner

**Cross-cutting sources:**

- *PROT-AGE (Bauer 2013)* — sweeps #1, #10.
- *NIAID food-allergy guidelines + LEAP (Du Toit 2015)* — sweeps #3, #9, #10.
- *AAP Bright Futures + CDC + WHO growth standards* — sweeps #3, #9, #10.
- *EFSA DRV* — sweeps #1, #10.
- *EU MDR 2017/745, EU AI Act, GDPR, HIPAA, ONC Cures Act* — sweeps #4, #6, #10. The shared regulatory perimeter for any health-software feature.
- *FDA fish advice, MHLW Japan mercury, FSANZ pregnancy* — sweeps #1 (food-safety adjacent), #10 (life-stage gating).

---

## Grocery infrastructure + retailer APIs

**What we sourced:** Instacart (Developer Platform docs + API reference, Connect partner program, fees, Instacart+, ToS, Canada); US grocers / delivery (Kroger Developer Portal + Cart API; Amazon PA-API 5.0, Amazon Fresh, Whole Foods, Subscribe & Save; Walmart Developer Portal + Walmart+, affiliate; Target Drive Up + Shipt; FreshDirect; Misfits Market; Wegmans Meals 2GO; Publix; H-E-B; Trader Joe's; Aldi US; Lidl US; DoorDash for Developers); UK + Ireland (Tesco Grocery + Tesco Labs; Sainsbury's; Ocado + Ocado Smart Platform; Asda; Morrisons; Waitrose; Instacart UK with Aldi; SuperValu; Dunnes); Canada (Loblaws / PC Express, Voilà by Sobeys, Metro, Walmart Canada); France (Carrefour, Auchan, Leclerc Drive, Monoprix, Casino); Germany (Rewe, Edeka, Lidl, Bringmeister, Picnic DE); Netherlands (Albert Heijn, Jumbo, Picnic, Crisp); Iberia (Mercadona, El Corte Inglés, Carrefour España, Continente, Glovo); Nordics (ICA, Coop Sverige, Mathem, Axfood/Willys, K-Ruoka, Salling/Bilka, Oda); Switzerland + Austria (Migros, LeShop, Coop Schweiz, Billa, Spar Österreich); open-source recipe-to-cart prior art (Mealie, Tandoor, Grocy, Open Food Facts, OurGroceries, AnyList, Bring!, Paprika); substitution + culinary references (Cook's Thesaurus; Joachim *Food Substitutions Bible*; CIA *Professional Chef* + *Garde Manger*; Davidson *Oxford Companion to Food*; Larousse Gastronomique); food composition + product data (USDA FDC, EuroFIR).

**Sweep coverage:**

- [Sweep #13 — grocery infrastructure](../13-grocery-infrastructure/scope.md#references) — canonical owner

**Cross-cutting sources:**

- *Open Food Facts* — sweeps #2, #13.
- *USDA FDC, EuroFIR* — sweeps #2, #11, #13.
- *Mealie, Tandoor, Grocy* — sweep #13 (also relevant to #11 recipe-software ecosystem).
- *CIA Professional Chef, Larousse Gastronomique* — sweeps #11, #12, #13.

---

## Privacy + data-protection regulatory bodies (cross-domain)

**What we sourced:** This is not a sweep-owned domain but a cross-cutting set of regulatory anchors that recur across multiple sweeps. Coverage includes HIPAA (US), ONC 21st Century Cures Act + info-blocking (US), FTC Health Breach Notification Rule (US), GDPR (EU 2016/679), European Health Data Space, PIPEDA (Canada), OAIC Australian Privacy Principles, NZ Health Information Privacy Code, PIPL (China), APPI (Japan), PIPA (Korea), LGPD (Brazil), Israel Privacy Protection Law, Russia Federal Law 152-FZ, EU MDR 2017/745, MDCG 2019-11, EU AI Act 2024/1689, MHRA / TGA / Health Canada / NMPA / PMDA / MFDS SaMD frameworks, IMDRF SaMD definitions.

**Sweep coverage:**

- [Sweep #6 — wearable data availability](../06-wearable-data-availability/scope.md#references) — owns the privacy/data-protection panel
- [Sweep #4 — adaptive intake agent](../04-adaptive-intake-agent/scope.md#references) — re-cites HIPAA, GDPR, EU AI Act, ONC info-blocking, ONC PGHD framework
- [Sweep #10 — clinical condition gating](../10-clinical-condition-gating/scope.md#references) — owns the SaMD / CDS regulatory landscape
- [Sweep #11 — recipe sourcing](../11-recipe-sourcing/scope.md#references) — owns the recipe-IP regulatory landscape (separate sub-domain)

**Cross-cutting sources:** see notes under *Wearable + biometric data sources* and *Clinical condition gating + drug-nutrient + regulatory frameworks*.

---

## Aggregation notes

**Total sweeps covered:** 13 (#1–#13).

**Consolidation date:** 2026-04-29 (lean restructure replacing the 2629-line full-citation aggregator with a navigational index that defers to per-sweep `## References` sections as the source of truth).

**Most notable cross-cutting sources** (high-frequency citations across the corpus):

- *HL7 FHIR family (R4 US Core, IPS, Questionnaire, SDC, SMART on FHIR)* — sweeps #4, #6. The shared interop layer for both wearable data and structured intake.
- *HIPAA, GDPR, EU AI Act, ONC Cures Act / info-blocking* — sweeps #4, #6, #10. The shared regulatory perimeter.
- *USDA FoodData Central + Open Food Facts + EuroFIR* — sweeps #2, #11, #13. Composition-data backbone.
- *Behaviour Change Wheel (Michie 2011) + BCT Taxonomy v1 (Michie 2013)* — sweeps #4, #7, #8, #9. Shared behavior-change vocabulary.
- *Lavelle et al. (2017) cooking + food skills measures* — sweeps #3, #4, #7. The validated cooking-confidence screener.
- *Miller & Rollnick *Motivational Interviewing*** — sweeps #3, #4, #8.
- *PREDIMED, DASH, DASH-Sodium, MIND* — sweeps #1, #3, #5, #9. Foundational pattern-trial canon.
- *AAP Bright Futures + CDC/WHO growth standards + NIAID food-allergy + LEAP* — sweeps #3, #9, #10. Pediatric anchor set.
- *CIA *The Professional Chef* + Larousse Gastronomique + McGee* — sweeps #9, #11, #12, #13. Culinary-canon backbone.
- *PROMIS / HealthMeasures (Cella et al.)* — sweeps #3, #4. Item-bank methodology shared by assessment + adaptive intake.

**Observed gaps:**

- Peer-reviewed literature on recipe sourcing and culinary standards remains sparse (primarily technical-format and IP-law references). Wave 3's culinary-curriculum canvas (sweep #12) helps, but bottom-up canonical-dish-set → required-skills validation is still queued.
- Wearable validation literature skews cardiovascular / sleep; less coverage of metabolic or nutrition-relevant sensor validation outside CGM.
- Non-English recipe-source documentation is uneven; diaspora creators noted but individual canonical URLs not enumerated.
- Indigenous and traditional food composition remains under-represented despite CINE/Kuhnlein and NATIFS citations.
- Several wave 3 sweeps (#5, #7, #9, #10) explicitly note `[verify]` flags for URLs/DOIs reconstructed from training data without live fetch — these need re-verification before user-facing surfacing.
- No live HTTP verification was performed for sweep #12 culinary-curriculum URLs (queued for follow-up).
- Pricing / access-tier specifics in sweep #13's grocery-API references are time-sensitive and require re-verification at adoption.

**Notable patterns:**

- Food composition databases divide cleanly by geography and licensing (OGL/CC-BY dominant in public sector; proprietary or negotiated in Germany and China).
- Wearable APIs are fragmented across vendors with no unified standard; HL7 FHIR is the emerging interoperability layer.
- Recipe interchange uses schema.org/Recipe as the de facto standard; Cooklang is technically superior but niche.
- The behavior-change literature consolidates around the BCW + BCT v1 vocabulary; sweeps that touch behavior change (#3, #4, #7, #8, #9) all anchor on it.
- The regulatory perimeter for any AI-mediated health feature is consistent across sweeps #4, #6, #10: HIPAA + GDPR + ONC Cures + EU AI Act + (jurisdiction-specific) SaMD framework.
- Pediatric content is genuinely cross-domain: every sweep that touches families (#3, #9, #10) lands on the same anchor set (Bright Futures + WHO/CDC growth + NIAID/LEAP).
