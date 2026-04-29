# Sweep #10 — Clinical Condition Gating + Safety Surface

> Status: Scoped (refuse-vs-gate behavior assignments noted as needing second pass once full enumeration is complete)
> Last updated: 2026-04-28

## Purpose

Map the conditions, drug-nutrient interactions, life-stage states, and regulatory landscapes that determine when NutriMe must refuse, gate, or proceed-with-disclaimer. Establish the framework for refer-out (generic doctor + specialty surfacing — no provider integration). Operationalize [Constitutional Rule 1 (consult-professional)](../00-meta/constitutional-rules.md#rule-1--consult-a-professional) and [Rule 9 (geographic neutrality)](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing) in this domain.

## Deliverable

An annotated reference map containing:

- **Condition enumeration** — globally-recognized top conditions in scope, with gating behavior framework. Less-prevalent or specialty conditions captured at higher level with [dynamic-research-expansion](../00-meta/dynamic-research-expansion.md) hook for deeper data.
- **Behavior assignment per condition** — refuse / gate / proceed-with-disclaimer. Where collected data inherently suggests a gate (e.g., disclosed T1D → carb-counting gate), write it in. Where assignment is ambiguous, mark needs-second-pass at the condition's entry.
- **Pediatric conditions** — comprehensive proposed list; **assume-add** posture toward additional pediatric conditions surfaced by research. Backend pruning pass later, not during the research sweep.
- **Refer-out specialty mapping** — for each condition class, the specialties that "work to solve these issues" so the system can surface them in referral language. NO provider directory integration, NO telehealth partnerships.
- **Regulatory landscape** — global wellness-app + medical-device-line analysis across all primary research scope countries, equal-weighted per Rule 9. Surface where regulatory positions differ and *why* (region + population context).
- **Drug-nutrient interactions** — base framework + dynamic-research-expansion hook for drugs not in base
- **Pregnancy + lactation safety** — comprehensive global avoidance lists with comparative surfacing of country-by-country differences

This is a **reference map**, not corpus build.

## Behavior framework — three behaviors

For each condition, the system can:

- **Refuse** — system declines to act ("I can't plan meals for active eating disorder recovery — please work with your treatment team"). Reserved for conditions where unauthorized intervention is harmful (active EDs, post-bariatric early phase, oncology nutrition during active treatment, severe CKD, T1D without endocrinologist coordination).
- **Gate** — system proceeds with strict rails. The collected intake / clinical data inherently suggests the rails (e.g., T1D + endocrinologist's carb framework → carb-counting gate; CKD stage + nephrologist → potassium / phosphorus / protein gates).
- **Proceed with disclaimer** — system proceeds with conventional consult-professional callout. Default for most conditions where evidence-based meal planning is well-established and non-harmful (uncomplicated T2D, hypertension, GERD, IBS, common autoimmune in stable phase, etc.).

Behavior assignments are first-pass during this sweep; final assignments require a second design pass once full condition enumeration is complete.

## Conditions in scope (initial)

### Adult conditions (globally common)

- Cardiovascular — hypertension, dyslipidemia, post-MI, heart failure
- Metabolic — T2D (multiple stages), prediabetes, metabolic syndrome, NAFLD / MASLD, obesity-related
- Endocrine — T1D, thyroid (hyper / hypo), PCOS, adrenal
- Renal — CKD (stages 1–5), dialysis-specific, transplant
- GI — GERD, IBS, IBD (UC, Crohn's), celiac, diverticular disease, gastroparesis
- Hepatic — NAFLD / MASLD (also above), cirrhosis, hepatitis-specific
- Autoimmune — celiac (also above), Hashimoto's, lupus, RA
- Gut microbiome / functional — SIBO, food sensitivities (non-IgE)
- Eating disorders — AN, BN, BED, OSFED, ARFID — generally **refuse** category in active phase
- Oncology nutrition — active treatment (refuse / strict gate); survivorship (gate)
- Post-bariatric — early (refuse), maintenance (gate)
- Cardiovascular — beyond above, atrial fibrillation, peripheral vascular
- Allergies + intolerances (general adult)
- Gout
- Osteoporosis / osteopenia

### Pediatric conditions (per sweep #9 — kids as eaters)

Per user direction: assume-add posture. Initial proposed list:

- Pediatric food allergies (US Big 9: peanut, tree nut, milk, egg, soy, wheat, fish, shellfish, sesame; international equivalents — gates surface allergen-avoidance protocols)
- Pediatric celiac
- Pediatric T1D (refuse without endocrinologist coordination; gate with)
- ARFID + pediatric eating disorders (refuse / strict gate)
- Growth concerns (failure to thrive, picky eating with growth impact — gate, surface pediatrician + pediatric RD)
- Pediatric IBD
- Pediatric kidney conditions
- Autism-related dietary patterns + ARFID overlap
- Pediatric food intolerances (lactose, FODMAP-relevant)
- Pediatric obesity (gate, surface pediatrician)
- Pediatric eosinophilic esophagitis (EoE)

Additional conditions surfaced during research = assume-add.

### Life-stage states (always-honored physiological tier per [sweep #9](../09-multi-user-household/scope.md))

- Pregnancy — multiple trimesters, complications (gestational diabetes, hyperemesis, preeclampsia history, etc.)
- Lactation
- Adolescent growth + nutrient needs
- Older adult — sarcopenia risk, swallowing issues, polypharmacy
- Athletic / training high-load (not pathology, but distinct nutrient and energy needs)

## Refer-out specialty mapping

For each condition class, surface the specialties that work on these issues. No provider directory, no integration — purely surfacing knowledge of what specialty types exist and align to what conditions:

- Endocrinology (diabetes, thyroid, PCOS, adrenal)
- Nephrology (CKD, transplant)
- GI / hepatology (IBD, IBS, GERD, celiac, NAFLD, hepatic conditions)
- Cardiology (CV conditions)
- Oncology + oncology nutrition
- Allergy / immunology (food allergies, autoimmune)
- Eating disorder specialists (psychiatry + RDN, often team-based)
- Pediatric versions of all above
- Registered Dietitian Nutritionist (RDN) — broadly indicated across most conditions
- Certified Diabetes Care and Education Specialist (CDCES)
- Bariatric surgery + bariatric RDN
- Maternal-fetal medicine (high-risk pregnancy)
- Geriatrician (older adult complex cases)
- Sports nutrition (training high-load)
- Mental health specialists (where relevant — EDs, food-trauma, body image)

Surface as: "Conditions like yours are typically managed by [specialty]. We're not provider-affiliated; this is awareness so you know who to look for."

## Regulatory framing — global, B + C levels per Rule 9

**Distribution context:** Per [product-framing.md](../00-meta/product-framing.md), current distribution intent is **personal use** (user + family + possibly a few friends). This means regulatory analysis is **informational** — we map the landscape so we know where lines are, not so we can certify compliance at scale. If distribution intent broadens later (tracked in [roadmap.md](../00-meta/roadmap.md)), this analysis becomes the substrate for actual compliance work.

For each primary research scope country:

- **Wellness-app classification** — what makes an app a "wellness" tool vs. a regulated device in this jurisdiction
- **Medical-device-line analysis** — where would NutriMe cross the medical-device line if it offered (e.g.) carb-counting for diabetics, BP-targeted meal planning, oncology nutrition? Useful regardless of distribution intent because it tells us where to be careful.

Bodies covered (equal-weighted per Rule 9):

- US — FDA general wellness guidance, FTC Act
- Canada — Health Canada
- UK — MHRA (post-Brexit)
- EU — EU MDR + national equivalents
- Australia — TGA
- New Zealand — Medsafe
- China — NMPA
- Japan — PMDA
- Korea — MFDS
- Israel — Ministry of Health Medical Device Branch
- Russia — Roszdravnadzor

Surface where regulatory positions materially differ + the regional / population reasons behind those differences.

## Drug-nutrient interactions

Base framework: globally-recognized common interactions plus dynamic expansion per [dynamic-research-expansion.md](../00-meta/dynamic-research-expansion.md) for drugs not in base.

Common interactions to cover at depth:

- Warfarin / vitamin K (leafy greens, vitamin K consistency)
- MAO inhibitors / tyramine (aged cheeses, cured meats, fermented foods)
- Statins / grapefruit (CYP3A4 inhibition)
- SSRIs / St John's Wort (serotonin syndrome risk)
- Levothyroxine / calcium / iron / fiber (timing-sensitive absorption)
- ACE inhibitors / potassium (hyperkalemia risk)
- Metformin / B12 (long-term depletion)
- PPIs / B12, magnesium, calcium (long-term absorption)
- Diuretics / electrolyte balance
- Lithium / sodium consistency

Sources to map: drug labels, Lexicomp, NHS Drug-Food Interactions, USDA Dietary Interactions, EMA SmPCs, regional pharmacopoeia.

UX patterns from clinical decision support literature: how to surface drug-nutrient warnings without alert fatigue.

## Pregnancy + lactation safety — comparative global

Food-avoidance lists vary substantially by country:

- US (FDA / ACOG / CDC) — listeria + mercury focus
- EU (EFSA + national bodies) — different listeria protocols, different fish guidance
- UK (NHS) — different soft-cheese guidance, different liver guidance
- Japan (MHLW) — raw fish handled differently given cultural context
- Australia / NZ (FSANZ) — listeria-focused
- China (regional bodies) — TCM-influenced overlays in some guidance

Surface comparatively per Rule 9 — show all positions equal-weighted, explain why they differ.

Cover lactation-specific guidance in parallel (alcohol, caffeine, fish, allergens for breastfed infants, supplement guidance).

## Out of scope (with reasons)

- **Provider directory integration / partnerships / telehealth** — explicitly out per user direction
- **Cooking instruction for condition management** — covered in [sweep #11 (recipe sourcing)](../11-recipe-sourcing/scope.md) if needed; we are not teachers per [product-framing.md](../00-meta/product-framing.md#what-nutrime-is-explicitly-not)
- **Diagnosis suggestion** — system never suggests a diagnosis; conditions are user-disclosed or clinically-documented
- **Medication management** — system surfaces drug-nutrient interactions but never advises medication changes
- **Mental health primary intervention** — mental health screeners (per [sweep #3](../03-clinical-nutrition-assessment/scope.md)) gate to refer-out; system does not provide therapy

## Open questions for the research

- For each condition class: what's the published evidence base for the gating behavior we should adopt?
- Where do regulatory positions on wellness-vs-medical-device cross internationally? Are there harmonization efforts?
- For the dynamic-research-expansion pattern applied to drug-nutrient interactions: which authoritative sources are reliably accessible for fetch + verification?
- For pediatric conditions: how does the literature handle parent-mediated intake for clinical data quality?
- What is the published evidence on "alert fatigue" in drug-nutrient warning systems and how to surface warnings without it?

## Cross-references

- Centrally bound by [Constitutional Rule 1 (consult-professional)](../00-meta/constitutional-rules.md#rule-1--consult-a-professional)
- Bound by [Constitutional Rule 7 (peer-reviewed floor)](../00-meta/constitutional-rules.md#rule-7--peer-reviewed-evidence-floor)
- Bound by [Constitutional Rule 8 (epistemic trail)](../00-meta/constitutional-rules.md#rule-8--epistemic-trail-of-honesty) — condition-driven inferences carry full trail
- Bound by [Constitutional Rule 9 (geographic neutrality)](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing) — regulatory + guidance equal-weighted globally
- Implements [dynamic-research-expansion.md](../00-meta/dynamic-research-expansion.md) for drugs and conditions not in base corpus
- Receives screener signals from [sweep #3 (clinical nutrition assessment)](../03-clinical-nutrition-assessment/scope.md) — including the new pediatric instruments
- Cross-references [sweep #2 (food composition databases)](../02-food-composition-databases/scope.md) — condition-relevant nutrient lookups
- Cross-references [sweep #9 (multi-user household)](../09-multi-user-household/scope.md) — household conflict prioritization tier 2 (medical + life-stage)

## Findings

> **Epistemic note (2026-04-29):** WebSearch and WebFetch were denied for this sweep. The findings below are assembled from training-data knowledge of authoritative bodies, peer-reviewed literature, and regulatory frameworks current through January 2026. Every URL/DOI cited in `## References` is a stable canonical address whose *content* should be re-verified by a future sweep with live web access — particularly: (a) regulatory guidance documents that frequently revise (FDA wellness policy, EU MDR/MDCG guidance, MHRA SaMD guidance, TGA software exclusion order); (b) drug labels (FDA, EMA, MHRA SmPCs); (c) pregnancy/lactation lists (FDA, NHS, EFSA, FSANZ, MHLW). Items flagged with **[VERIFY]** are most-likely to have drifted. The condition behavior assignments (refuse/gate/proceed-with-disclaimer) are first-pass per the sweep brief and explicitly noted as second-pass design work where ambiguous.

### 1. Condition enumeration — adult (assume-add posture)

For each condition: prevalence + recognition basis, behavior assignment (refuse / gate / proceed-with-disclaimer), gating data points the system needs from intake (per [sweep #3](../03-clinical-nutrition-assessment/scope.md)), and refer-out specialty.

#### 1.1 Cardiovascular

| Condition | Behavior | Gating data | Refer-out |
|-----------|----------|-------------|-----------|
| Hypertension (essential, stage 1–2) | Proceed-with-disclaimer | DASH-eligibility, sodium target, comorbid CKD/diabetes flags | Primary care, cardiology, RDN |
| Resistant / secondary hypertension | Gate | BP control status, K-sparing diuretic use → potassium gate | Cardiology, nephrology, RDN |
| Dyslipidemia | Proceed-with-disclaimer | Statin use → grapefruit gate; familial hypercholesterolemia flag | Cardiology, lipidologist, RDN |
| Post-MI / stable CAD | Gate (Mediterranean / DASH rails) | Cardiac rehab status, antiplatelet/anticoagulant list | Cardiology, cardiac rehab RDN |
| Heart failure (HFrEF / HFpEF) | Gate | Fluid restriction status, sodium target (1.5–2 g/d typical), diuretic + K | Cardiology / HF clinic, RDN |
| Atrial fibrillation | Gate if anticoagulated → vitamin K consistency rail | Warfarin vs DOAC, thyroid history | Cardiology, EP, RDN |
| Peripheral arterial disease | Proceed-with-disclaimer | CV risk profile | Vascular, primary care, RDN |
| Cerebrovascular disease / stroke survivor | Gate | Dysphagia screen (IDDSI level), sodium target | Neurology, SLP, RDN |
| Cardiac arrhythmias on antiarrhythmics (amiodarone, etc.) | Gate | Drug list → grapefruit gate, thyroid monitoring | Cardiology / EP |

Sources: [ACC/AHA 2017 BP Guideline](https://doi.org/10.1161/HYP.0000000000000065); [ESC/ESH 2024 Hypertension Guideline](https://doi.org/10.1093/eurheartj/ehae178); [Heidenreich et al. 2022 AHA/ACC HF Guideline](https://doi.org/10.1161/CIR.0000000000001063).

#### 1.2 Metabolic / endocrine

| Condition | Behavior | Gating data | Refer-out |
|-----------|----------|-------------|-----------|
| Prediabetes | Proceed-with-disclaimer (DPP-aligned content) | A1C, BMI, FH-DM | Primary care, RDN, CDCES |
| T2D (uncomplicated, oral agents only) | Proceed-with-disclaimer + carb-awareness rails | A1C, agents (metformin → B12; GLP-1 → portion + GI), comorbid CKD | Endocrinology / primary care, CDCES, RDN |
| T2D (insulin-treated) | Gate (carb-counting rail; hypoglycemia awareness) | Insulin regimen (basal-bolus vs mixed), CGM use | Endocrinology, CDCES |
| T1D | **Refuse without** endocrinologist coordination; **gate with** (carb-counting + ICR/ISF rail) | ICR, ISF, CGM data, pump vs MDI | Endocrinology, CDCES, RDN |
| DKA-prone / brittle diabetes | Refuse — refer to specialist team | — | Endocrinology |
| Gestational diabetes | Gate (carb-distribution rail; pregnancy life-stage stack) | GDM regimen, OB/MFM coordination | OB/MFM, RDN, CDCES |
| Hyper-/hypothyroidism | Proceed-with-disclaimer + levothyroxine timing rail (Ca/Fe/fiber/coffee separation) | Drug timing, soy intake context | Endocrinology |
| Hashimoto's | Proceed-with-disclaimer | TPO+, comorbid celiac flag | Endocrinology, RDN |
| Graves' disease | Proceed-with-disclaimer; iodine context | Treatment phase (ATD, RAI, post-thyroidectomy) | Endocrinology |
| PCOS | Proceed-with-disclaimer (insulin-sensitizing rails: low-GI, Mediterranean) | Metabolic phenotype, fertility goals | Endocrinology, gynecology, RDN |
| Adrenal insufficiency / Addison's | Gate — sodium/fluid rails; sick-day stress dosing context (refer) | Steroid regimen, sodium baseline | Endocrinology |
| Cushing's | Gate | Treatment status | Endocrinology |
| Pheochromocytoma (active) | Refuse — defer to endocrine team (tyramine context if MAOI-like) | — | Endocrinology |
| Metabolic syndrome | Proceed-with-disclaimer | Component count | Primary care, RDN |
| NAFLD / MASLD | Proceed-with-disclaimer (Mediterranean rail) | Fibrosis stage, alcohol use | Hepatology / GI, RDN |
| Obesity (uncomplicated, BMI 30–39.9) | Proceed-with-disclaimer; **no aesthetic / weight-loss framing per product-framing.md** | Anti-obesity meds (GLP-1, naltrexone-bupropion) → GI/portion + tyramine context | Primary care, obesity medicine, RDN |
| Class III obesity (BMI ≥ 40) | Gate — surface bariatric + obesity-medicine referral; coordinate | Surgical/medical plan | Bariatric MD, RDN |

Sources: [ADA Standards of Care 2025](https://doi.org/10.2337/dc25-SINT); [EASD/ADA Consensus 2022](https://doi.org/10.2337/dci22-0034); [AACE Clinical Practice Guideline Diabetes 2023](https://doi.org/10.1016/j.eprac.2023.02.001); [AASLD MASLD Practice Guidance 2023](https://doi.org/10.1097/HEP.0000000000000323); [PCOS International Evidence-based Guideline 2023](https://doi.org/10.1093/humrep/dead156).

#### 1.3 Renal

| Condition | Behavior | Gating data | Refer-out |
|-----------|----------|-------------|-----------|
| CKD stage 1–2 | Proceed-with-disclaimer | eGFR, albuminuria, BP, diabetes status | Primary care, nephrology |
| CKD stage 3a | Proceed-with-disclaimer + protein/sodium awareness | Recent K, P, bicarbonate | Nephrology, renal RDN |
| CKD stage 3b–4 | Gate (protein 0.55–0.6 g/kg if non-DM, 0.6–0.8 if DM; K, P, Na rails) | Labs (K, P, HCO3), renal RDN involvement | Nephrology, renal RDN |
| CKD stage 5 / dialysis (HD, PD) | Refuse without renal RDN coordination; gate with (protein 1.0–1.2 g/kg, individualized K/P/fluid) | Modality, dry weight, labs, phosphate binders | Nephrology, renal RDN |
| Renal transplant (post-op, stable) | Gate — immunosuppressant interactions (tacrolimus/cyclosporine + grapefruit), food-safety rails | Immunosuppressant list, time since transplant | Transplant nephrology, RDN |
| Nephrolithiasis (Ca-oxalate, uric acid, struvite, cystine) | Proceed-with-disclaimer (stone-type-specific rails) | Stone type, 24-h urine | Urology, nephrology, RDN |
| Acute kidney injury | Refuse during acute phase | — | Inpatient team |

Sources: [KDOQI Clinical Practice Guideline for Nutrition in CKD 2020 update](https://doi.org/10.1053/j.ajkd.2020.05.006); [KDIGO 2024 CKD Guideline](https://doi.org/10.1016/j.kint.2023.10.018).

#### 1.4 Gastrointestinal

| Condition | Behavior | Gating data | Refer-out |
|-----------|----------|-------------|-----------|
| GERD | Proceed-with-disclaimer (trigger-food + meal-timing rails) | PPI use → B12/Mg/Ca context, Barrett's flag | Primary care, GI |
| Functional dyspepsia | Proceed-with-disclaimer | Symptom pattern | GI |
| IBS (subtypes IBS-C/D/M) | Proceed-with-disclaimer (low-FODMAP framework optional, time-limited) | Subtype, prior diet trials, ED screen (IBS + ARFID overlap) | GI, RDN with FODMAP training |
| IBD — Crohn's disease | Proceed-with-disclaimer in remission; gate in flare or stricturing disease | Disease phase, surgical history (short bowel, ostomy), biologics + nutrient deficiencies (B12, Fe, vit D) | GI, IBD RDN |
| IBD — Ulcerative colitis | Proceed-with-disclaimer in remission; gate in flare | As above | GI, IBD RDN |
| Celiac disease | Gate — strict gluten-free rail, cross-contamination | Diagnosis confirmation (TTG-IgA + biopsy or HLA), associated AI conditions | GI, celiac-specialized RDN |
| Non-celiac gluten sensitivity | Proceed-with-disclaimer (audit-as-education on evidence quality — Tier 3) | Symptom pattern | GI, RDN |
| Diverticular disease | Proceed-with-disclaimer (high-fiber rail in non-acute) | Acute diverticulitis history | GI |
| Gastroparesis | Gate — small frequent meals, low-fat/low-fiber rail in symptomatic | Etiology (DM, idiopathic, post-surgical), severity | GI, motility specialist, RDN |
| Eosinophilic esophagitis (adult) | Gate — six-food / four-food / two-food elimination protocols | Allergist coordination, biopsy schedule | GI, allergy, RDN |
| Microscopic colitis | Proceed-with-disclaimer | Drug triggers (NSAIDs, PPIs) | GI |
| SIBO | Proceed-with-disclaimer (audit-as-education — Tier 3 framework, contested testing) | Breath test result, underlying cause | GI, RDN |
| Pancreatic insufficiency (chronic pancreatitis, CF, post-surgical) | Gate — PERT timing, fat-soluble vitamins, MCT rails | PERT regimen, etiology | GI, pancreas clinic, RDN |
| Short bowel syndrome | Refuse without specialist team; gate with | Anatomy, parenteral support | GI / nutrition support team |
| Bile acid diarrhea | Proceed-with-disclaimer | SeHCAT or trial of sequestrant | GI |

Sources: [ACG Clinical Guideline IBS 2021](https://doi.org/10.14309/ajg.0000000000001036); [BSG IBS Guidelines 2021](https://doi.org/10.1136/gutjnl-2021-324598); [Monash Low FODMAP literature](https://www.monashfodmap.com/about-fodmap-and-ibs/); [ACG Celiac Guideline 2023](https://doi.org/10.14309/ajg.0000000000002075); [ECCO/ESPEN IBD Nutrition Guidelines 2023](https://doi.org/10.1016/j.clnu.2022.12.004); [ACG/AGA EoE Guidelines](https://doi.org/10.1053/j.gastro.2022.05.045).

#### 1.5 Hepatic

| Condition | Behavior | Gating data | Refer-out |
|-----------|----------|-------------|-----------|
| MASLD / MASH | Proceed-with-disclaimer (Mediterranean, weight-reduction context) | Fibrosis stage (FIB-4), comorbid metabolic | Hepatology, RDN |
| Alcohol-associated liver disease | Gate — alcohol abstinence framing; refer hepatology + addiction medicine | AUDIT-C result | Hepatology, addiction medicine |
| Cirrhosis (compensated) | Gate — protein 1.2–1.5 g/kg, sodium ≤ 2 g/d if ascites, late-evening snack | Child-Pugh, MELD, ascites status | Hepatology, hepatology RDN |
| Cirrhosis (decompensated) — HE, ascites, varices | Refuse without specialist; gate with | Lactulose/rifaximin, paracentesis frequency | Hepatology, transplant team |
| Viral hepatitis (B, C — treated/untreated) | Proceed-with-disclaimer | Treatment status, fibrosis | Hepatology / ID |
| Wilson's disease | Gate — copper restriction rail (refer specialist for actual copper-content lists) | Treatment regimen | Hepatology |
| Hemochromatosis | Gate — iron, vitamin C (cofactor), avoid raw shellfish (Vibrio risk in iron overload) | Phlebotomy schedule | Hepatology / hematology |
| α1-antitrypsin liver disease | Gate | Hepatology coordination | Hepatology |

Sources: [AASLD Cirrhosis Practice Guidance 2021](https://doi.org/10.1002/hep.32049); [EASL Clinical Practice Guidelines on Decompensated Cirrhosis 2022](https://doi.org/10.1016/j.jhep.2021.12.022).

#### 1.6 Autoimmune

| Condition | Behavior | Gating data | Refer-out |
|-----------|----------|-------------|-----------|
| Hashimoto's | Proceed-with-disclaimer (see endocrine) | — | Endocrinology |
| Lupus (SLE) | Proceed-with-disclaimer; alfalfa-sprout caution; corticosteroid bone health | Renal involvement → CKD overlay | Rheumatology |
| Rheumatoid arthritis | Proceed-with-disclaimer (Mediterranean evidence base — Tier 2) | DMARDs (MTX → folate; biologics → food safety) | Rheumatology |
| Psoriasis / psoriatic arthritis | Proceed-with-disclaimer | Comorbid metabolic | Dermatology / rheumatology |
| Multiple sclerosis | Proceed-with-disclaimer (vit D context) | Bowel/bladder issues | Neurology |
| Sjögren's | Proceed-with-disclaimer (dental + dry-mouth food prep adaptations) | — | Rheumatology |
| Type 1 diabetes (autoimmune) | See endocrine | — | Endocrinology |
| Inflammatory myopathies | Proceed-with-disclaimer; dysphagia screen | — | Rheumatology, SLP |
| Vasculitides | Proceed-with-disclaimer | Steroid rail | Rheumatology |
| Autoimmune hepatitis | See hepatic | — | Hepatology |
| Type 1 / 2 autoimmune thyroid | See endocrine | — | Endocrinology |

Sources: [ACR RA management 2021](https://doi.org/10.1002/art.41752); [EULAR lifestyle recommendations RA/spondyloarthritis 2023](https://doi.org/10.1136/ard-2022-223260).

#### 1.7 Eating disorders — refuse posture in active phase

| Condition | Behavior | Notes |
|-----------|----------|-------|
| Anorexia nervosa | **Refuse** — defer to ED treatment team; system surfaces refer-out language only | Refeeding syndrome risk |
| Bulimia nervosa | **Refuse** | — |
| Binge eating disorder | **Refuse** for "ED-specific intervention"; may proceed-with-disclaimer for general planning if treating clinician approves and ED screen below threshold | — |
| OSFED | **Refuse** in active phase | — |
| ARFID (adult or pediatric) | **Refuse** — co-treat with feeding team | Common autism overlap |
| Orthorexia (proposed; not in DSM-5-TR) | Proceed-with-disclaimer + audit-as-education on evidence | ORTO-R validity contested |
| Diabulimia (T1D + ED) | **Refuse** — high-mortality | — |
| In stable recovery with treating-team sign-off | Gate with team-defined rails | Needs second pass |

Sources: [APA Practice Guideline for the Treatment of Patients with Eating Disorders 2023](https://doi.org/10.1176/appi.books.9780890424865); [NICE NG69 Eating Disorders](https://www.nice.org.uk/guidance/ng69); [AED Medical Care Standards 4th ed.](https://www.aedweb.org/publications/medical-care-standards).

#### 1.8 Oncology nutrition

| Phase | Behavior | Notes |
|-------|----------|-------|
| Active treatment (chemotherapy, RT, immunotherapy, surgery prep/recovery) | **Refuse without** oncology-nutrition (CSO RDN) coordination; **gate with** (neutropenic-diet evidence is now contested — Tier 2 supports food-safety practices over strict neutropenic diet) | Drug interactions extensive (e.g., grapefruit + many oral oncologics; St John's Wort + many regimens); HER2/CDK4/6/TKI/AI lists per regimen |
| Survivorship (post-treatment, NED) | Gate (initial), Proceed-with-disclaimer (long-term) | ACS Nutrition for Cancer Survivors 2022 |
| Palliative / end-of-life | Refuse / defer to palliative team | Hospice nutrition is its own discipline |
| Cancer cachexia | Refuse without specialist; gate with | — |
| Pediatric oncology | Refuse — pediatric oncology RDN | — |

Sources: [WCRF/AICR Cancer Prevention Recommendations 2018 + updates](https://www.wcrf.org/diet-activity-and-cancer/cancer-prevention-recommendations/); [Rock et al. 2022 ACS Nutrition and Physical Activity Guideline for Cancer Survivors](https://doi.org/10.3322/caac.21719); [ESPEN guidelines on nutrition in cancer patients 2021](https://doi.org/10.1016/j.clnu.2021.02.005).

#### 1.9 Post-bariatric

| Phase | Behavior |
|-------|----------|
| Pre-op (LCD/VLCD) | Refuse — surgical team manages |
| Early post-op (0–6 mo, stage progression) | **Refuse** — surgical team / bariatric RDN |
| Maintenance (6 mo+, stable) | Gate — protein floor, micronutrient supplementation, avoid carbonation/sliders, dumping management | RYGB vs VSG vs OAGB vs DS-specific rails |

Sources: [ASMBS/AACE Nutritional Guidelines 2019](https://doi.org/10.1016/j.soard.2019.10.025); [BOMSS UK Nutritional Guidelines 2020](https://bomss.org/wp-content/uploads/2022/10/BOMSS-Nutritional-Guidance.pdf).

#### 1.10 Allergies, intolerances, gout, osteoporosis

| Condition | Behavior | Gating data |
|-----------|----------|-------------|
| IgE food allergy (Big 9 + sesame, mustard, lupin, etc.) | Gate — strict avoidance + cross-contact + label-reading | Reaction history (anaphylaxis = hard rail), epinephrine prescribed |
| Oral allergy / PFAS | Proceed-with-disclaimer (cooked-form often tolerated) | Cross-reactivity profile |
| Non-IgE food allergy (FPIES, EoE, FPIAP) | Gate — allergist + RDN coordination | — |
| Lactose intolerance | Proceed-with-disclaimer | Tolerance threshold |
| Histamine intolerance | Proceed-with-disclaimer + audit-as-education (Tier 3 evidence) | — |
| FODMAP intolerance | Proceed-with-disclaimer (under IBS framework) | — |
| Gout (hyperuricemia) | Proceed-with-disclaimer (purine, fructose, alcohol context) | ULT (allopurinol/febuxostat) status |
| Osteoporosis / osteopenia | Proceed-with-disclaimer (Ca, vit D, protein, K, Mg rails) | Fracture history, bisphosphonates / denosumab / romosozumab; PPI long-term |

Sources: [NIAID Food Allergy Guidelines 2010 + 2017 update](https://www.niaid.nih.gov/diseases-conditions/food-allergy-guidelines); [EAACI Food Allergy and Anaphylaxis Guidelines 2014/2022](https://doi.org/10.1111/all.15032); [ACR Gout Guideline 2020](https://doi.org/10.1002/art.41247); [Endocrine Society Osteoporosis Postmenopausal Women 2019/2020](https://doi.org/10.1210/clinem/dgaa048).

#### 1.11 Other globally-prevalent (assume-add)

- COPD (nutrition + sarcopenia overlay) — proceed-with-disclaimer
- Cystic fibrosis (high-energy, PERT, fat-soluble vitamins) — refuse without CF team / gate with
- Migraine (trigger-food evidence is Tier 3 mixed; tyramine context if MAOI) — proceed-with-disclaimer
- Epilepsy on ketogenic / modified Atkins (medical KD) — refuse without neuro-keto team
- Mental health: depression / anxiety — proceed-with-disclaimer (Mediterranean → SMILES trial Tier 3); MAOI flag = tyramine gate
- Schizophrenia + antipsychotic-related metabolic syndrome — gate (metabolic + drug interactions)
- HIV (stable on ART) — proceed-with-disclaimer; food safety; drug-food (e.g., rilpivirine with meal, integrase inhibitors + Ca/Mg/Fe binding)
- Tuberculosis on therapy — proceed-with-disclaimer; isoniazid + tyramine + B6
- Sickle cell disease — proceed-with-disclaimer; hydration, folate
- Hereditary metabolic disorders (PKU, MSUD, MCAD, urea-cycle) — refuse — metabolic-disease team only
- Lipid disorders (familial hypercholesterolemia, lipoprotein lipase deficiency) — gate
- Hyperoxaluria (primary, enteric) — gate
- Chronic kidney transplant immunosuppression — see renal
- Lyme post-treatment / chronic fatigue / long COVID — proceed-with-disclaimer + audit-as-education

> **needs second pass:** depression/anxiety boundary between proceed-with-disclaimer and gate; SIBO; histamine intolerance; non-celiac gluten sensitivity; orthorexia; long COVID nutrition rails.

### 2. Pediatric conditions (kids as eaters per [sweep #9](../09-multi-user-household/scope.md))

Parent-mediated intake; **assume-add posture** for additional pediatric conditions surfaced by research.

| Condition | Behavior | Gating data | Refer-out |
|-----------|----------|-------------|-----------|
| Pediatric food allergies — US Big 9 (peanut, tree nut, milk, egg, soy, wheat, fish, shellfish, sesame) | Gate — strict avoidance + cross-contact + label-reading + EpiPen flag | Reaction history, allergist-confirmed, IgE/SPT, OFC results | Pediatric allergy, pediatric RDN |
| Pediatric food allergies — international equivalents (EU 14 allergens incl. celery, mustard, lupin, sulfites, molluscs, gluten-containing cereals; AU/NZ FSANZ "Big 10" incl. lupin; Japan 8 specified + 20 recommended incl. buckwheat; Canada Priority Allergens incl. mustard) | Gate (region-aware label vocabulary) | Region | As above |
| Pediatric celiac | Gate — strict GF rail + cross-contact + nutrient adequacy (Fe, fiber, B-vitamins) | Diagnosis confirmation, growth chart | Pediatric GI, pediatric RDN |
| Pediatric T1D | **Refuse without** pediatric endocrinologist coordination; **gate with** (carb-counting, ICR/ISF, hypoglycemia treatment) | Insulin regimen, pump/CGM | Pediatric endo, CDCES, pediatric RDN |
| Pediatric T2D (rising globally) | Gate | A1C, agents (metformin, GLP-1) | Pediatric endo |
| ARFID (pediatric — DSM-5-TR) | **Refuse** — feeding team only | PARDI-AR-Q score, growth trajectory | Feeding team (pediatrician, OT/SLP, RDN, psych) |
| Pediatric anorexia / bulimia / OSFED / atypical AN | **Refuse** — adolescent ED team (FBT) | EDE-Q / SCOFF adapted, growth, vitals | Adolescent medicine, pediatric ED program |
| Failure to thrive / faltering growth | Gate — pediatric RDN coordination; high-energy plan rails | Growth chart trajectory, intake history | Pediatrics, pediatric RDN |
| Picky eating (typical, no growth impact) | Proceed-with-disclaimer; Satter Division of Responsibility framing | Sensory profile, age | Pediatrician |
| Pediatric IBD | **Refuse without** pediatric GI; gate with (consider EEN evidence Tier 1 for Crohn's induction) | Disease phase, biologics, nutrient deficits | Pediatric GI, pediatric IBD RDN |
| Pediatric kidney conditions — CKD, nephrotic syndrome, congenital anomalies | **Refuse without** pediatric nephrology + renal RDN; gate with | Stage, K/P/protein targets, growth | Pediatric nephrology, pediatric renal RDN |
| Autism spectrum + dietary patterns (food selectivity, ARFID overlap, GI comorbidity) | Gate — feeding team if ARFID; otherwise proceed-with-disclaimer with selectivity-aware framing | Sensory profile, OT/SLP involvement | Pediatrician, developmental pediatrics, feeding team |
| Pediatric food intolerances (lactose, fructose, sucrase-isomaltase) | Proceed-with-disclaimer | Tolerance threshold | Pediatric GI |
| Pediatric obesity (BMI ≥ 95th %ile) | Gate per AAP 2023 — coordinate with pediatrician; **no aesthetic framing** | Comorbidities (NAFLD, T2D, OSA) | Pediatrician, pediatric obesity medicine, pediatric RDN |
| Pediatric eosinophilic esophagitis | **Refuse without** pediatric GI + allergy coordination; gate with (six/four/two-food elimination) | Endoscopy/biopsy schedule | Pediatric GI, pediatric allergy, pediatric RDN |
| Cow's milk protein allergy / FPIES | Gate — formula choice (eHF, AAF), introduction protocol | Symptom pattern, OFC results | Pediatric allergy, pediatric GI |
| Pediatric inborn errors of metabolism (PKU, MSUD, OA, UCD, GSD, fatty acid oxidation disorders, galactosemia) | **Refuse** — metabolic-disease team only | — | Metabolic / genetics |
| Pediatric chronic liver disease | Refuse without pediatric hepatology | — | Pediatric hepatology |
| Pediatric cystic fibrosis | Refuse without CF team; gate with (high-energy, PERT, CFTR-modulator considerations) | — | Pediatric pulm, CF center |
| Pediatric oncology | **Refuse** — pediatric oncology RDN | — | Pediatric oncology |
| Pediatric short bowel / intestinal failure | Refuse — intestinal rehab team | — | Pediatric GI, intestinal failure team |
| Pediatric ketogenic diet for refractory epilepsy | **Refuse** — keto team only | — | Pediatric neurology, keto RDN |
| Pediatric eating skill / sensory feeding disorders (non-ARFID) | Proceed-with-disclaimer with feeding-team referral | OT/SLP involvement | Feeding team |
| Adolescent menstrual / amenorrhea + RED-S | Gate — sports medicine + ED screen | Training load, menses, BMD if available | Adolescent medicine, sports medicine, RDN |
| Pediatric celiac + T1D combined | Gate — combined rails | Both teams | Pediatric endo + GI + RDN |
| Pediatric food protein-induced allergic proctocolitis (FPIAP) | Gate — maternal-elimination if breastfeeding, formula choice if bottle | Symptom pattern | Pediatric allergy / GI |
| Pediatric MIH / orofacial / cleft palate / dysphagia | Gate — feeding team, IDDSI texture levels | SLP assessment | Feeding team |

> **assume-add:** any pediatric condition surfaced during research is added; pruning is a later pass. Examples encountered during scoping but not central: pediatric Crohn's-related growth failure, pediatric Alagille, biliary atresia post-Kasai, pediatric NAFLD, pediatric chronic constipation, juvenile idiopathic arthritis nutrition.

> **needs second pass:** boundary between "feeding-team refer-out" and "proceed with cautious gate" for high-functioning ASD without ARFID; behavior assignment for pediatric obesity given AAP 2023 update controversy.

Sources: [AAP Clinical Practice Guideline Childhood Obesity 2023 (Hampl et al.)](https://doi.org/10.1542/peds.2022-060640); [NASPGHAN Pediatric IBD Position Paper](https://doi.org/10.1097/MPG.0000000000003222); [Pediatric Celiac ESPGHAN 2020](https://doi.org/10.1097/MPG.0000000000002497); [ISPAD Clinical Practice Consensus Guidelines 2022 (Pediatric T1D)](https://doi.org/10.1111/pedi.13428); [Satter Division of Responsibility](https://www.ellynsatterinstitute.org/how-to-feed/the-division-of-responsibility-in-feeding/); [WHO Growth Standards (under 2)](https://www.who.int/tools/child-growth-standards); [CDC Growth Charts (≥ 2)](https://www.cdc.gov/growthcharts/).

### 3. Life-stage states (always-honored physiological tier per [sweep #9](../09-multi-user-household/scope.md))

Life-stage is **always honored** — regardless of the user's primary clinical condition list, life-stage rails stack on top.

#### 3.1 Pregnancy (by trimester + complications)

- **First trimester:** folate (400–600 mcg DFE), nausea/HG-aware planning, listeria + Toxoplasma + Hg avoidance, alcohol abstinence, caffeine ≤ 200 mg/d (most bodies). Hyperemesis gravidarum → refuse meal-planning that ignores liquid/calorie tolerability; coordinate with OB.
- **Second trimester:** iron emphasis, calcium, iodine, choline (often under-met), continued food-safety rail.
- **Third trimester:** iron (anemia screen-driven), continued protein, GI/heartburn/constipation accommodations.
- **GDM:** carb-distribution rails, monitoring coordination → gate.
- **Pre-eclampsia / hypertensive disorders:** sodium not restricted per ACOG (contrary to lay belief); coordinate with OB/MFM → gate.
- **Pre-existing T1D/T2D in pregnancy:** refuse without endocrine + MFM; gate with.
- **Multiples:** higher energy and micronutrient targets; gate.
- **History of bariatric surgery + pregnancy:** gate — bariatric RDN + MFM.
- **Cholestasis of pregnancy:** gate.

Sources: [ACOG Nutrition During Pregnancy FAQ + Practice Bulletins](https://www.acog.org/womens-health/faqs/nutrition-during-pregnancy); [WHO Antenatal Care Recommendations 2016/2025](https://www.who.int/publications/i/item/9789241549912); [NICE NG201 Antenatal Care 2021](https://www.nice.org.uk/guidance/ng201); [EFSA DRVs for pregnancy](https://www.efsa.europa.eu/en/topics/topic/dietary-reference-values).

#### 3.2 Lactation

- Energy +330–400 kcal/d (variable by body composition + nursing intensity)
- Iodine (often under-met in many populations)
- Choline, DHA
- Alcohol — timing-based guidance (CDC: avoid until single drink fully metabolized ~2 hr/standard drink)
- Caffeine ≤ 200–300 mg/d typically
- Fish/Hg same as pregnancy lists
- Allergens — current consensus (US 2017 LEAP-derived guidance): **do not restrict** maternal diet to prevent infant allergy; introduce common allergens to infant from ~4–6 mo per allergen-introduction guidance
- Maternal dietary triggers for infant fuss / colic / FPIAP — limited evidence (Tier 3); proceed-with-disclaimer with allergist input if FPIAP suspected
- Galactagogues — Tier 3/4 evidence; surface with audit-as-education

Sources: [AAP Breastfeeding & Use of Human Milk 2022](https://doi.org/10.1542/peds.2022-057988); [WHO Infant and Young Child Feeding](https://www.who.int/news-room/fact-sheets/detail/infant-and-young-child-feeding); [LactMed (NIH)](https://www.ncbi.nlm.nih.gov/books/NBK501922/).

#### 3.3 Adolescent growth

- Pubertal energy + protein + calcium + iron + zinc + vit D requirements
- Female adolescents: iron + bone-accrual window
- Athletes: RED-S risk
- Sleep × growth interaction
- ED screening floor (per [sweep #3](../03-clinical-nutrition-assessment/scope.md))

Sources: [Bright Futures Nutrition Pocket Guide 4th ed.](https://brightfutures.aap.org/materials-and-tools/nutrition-pocket-guide/Pages/default.aspx); [SAHM Position Paper Adolescent Eating Disorders 2022](https://doi.org/10.1016/j.jadohealth.2022.05.012).

#### 3.4 Older adult

- Sarcopenia: protein 1.0–1.2 g/kg (or 1.2–1.5 if catabolic / chronic disease) per ESPEN/PROT-AGE; distribute across meals
- Dysphagia: IDDSI levels for texture/thickness; SLP referral
- Polypharmacy: drug-nutrient stack (warfarin, levothyroxine, PPIs, diuretics, statins, anticoagulants, anticholinergics)
- Vitamin D + calcium + B12 (often deficient)
- Hydration risk
- Dementia-related feeding changes
- Frailty / unintentional weight loss → MNA-SF; gate

Sources: [ESPEN Practical Guideline Clinical Nutrition and Hydration in Geriatrics 2022](https://doi.org/10.1016/j.clnu.2022.01.024); [PROT-AGE Position 2013](https://doi.org/10.1016/j.jamda.2013.05.021); [IDDSI Framework 2.0](https://iddsi.org/framework/).

#### 3.5 Athletic / training high-load

- Endurance: carbohydrate periodization (3–12 g/kg/d), training-day carb intra-workout, fluid + electrolyte
- Strength: protein 1.6–2.2 g/kg/d, distribution 0.3–0.4 g/kg per meal
- Combat / weight-class: caution-flagged — RED-S risk
- Female athlete triad / RED-S — gate
- Vegetarian/vegan athlete: B12, Fe, Zn, EPA/DHA, creatine considerations
- Supplement landscape audit-as-education (creatine Tier 1; beta-alanine, caffeine Tier 1; many others Tier 3/4)

Sources: [Thomas et al. 2016 ACSM/AND/Dietitians of Canada Joint Position](https://doi.org/10.1016/j.jand.2015.12.006); [IOC Consensus on Dietary Supplements 2018](https://doi.org/10.1136/bjsports-2018-099027); [IOC RED-S Consensus 2023 Update](https://doi.org/10.1136/bjsports-2023-106994).

### 4. Refer-out specialty mapping (no provider integration)

Knowledge surface only — system says "conditions like yours are typically managed by [specialty]; we're not provider-affiliated."

| Condition class | Primary specialty | Allied / nutrition specialty | Mental health where relevant |
|-----------------|-------------------|------------------------------|--------------------------------|
| Diabetes (all types) | Endocrinology / primary care | CDCES, RDN (CDR-credentialed in DM); peds: pediatric endo + pediatric CDCES | Diabetes distress / depression — health psych |
| Thyroid / adrenal / pituitary / PCOS | Endocrinology | RDN | — |
| CKD / dialysis / transplant | Nephrology / transplant nephrology | Renal RDN (CSR in US) | Transplant social work |
| GI / IBD / IBS / GERD / EoE / celiac | Gastroenterology / hepatology | RDN with GI focus, Monash-trained for FODMAP | — |
| Hepatic | Hepatology | Hepatology RDN | Addiction medicine for ALD |
| Cardiovascular | Cardiology / cardiac rehab / EP / vascular | Cardiac rehab RDN, CV nurse educator | — |
| Oncology | Medical / surgical / radiation oncology | CSO RDN (Board Certified Specialist in Oncology Nutrition) | Oncology social work, psycho-oncology |
| Allergy / immunology | Allergy/immunology | RDN with allergy training | — |
| Eating disorders | Adolescent medicine / psychiatry / ED-specialty MD | CEDRD / CEDS-S / ED-credentialed RDN | LCSW / PhD / PsyD with ED training; FBT therapist for adolescents |
| Bariatric / obesity medicine | Bariatric surgery / obesity medicine (ABOM) | Bariatric RDN | Bariatric psych eval |
| Pregnancy (low-risk) | OB/GYN / midwife | RDN; lactation consultant (IBCLC) | Perinatal mental health |
| Pregnancy (high-risk) | MFM | RDN; CDCES if GDM | — |
| Older adult complex | Geriatrician | RDN; SLP for dysphagia; PT/OT | Geropsych |
| Athletes | Sports medicine | CSSD RDN (Board Certified Specialist in Sports Dietetics) | Sport psych |
| Pediatrics broadly | Pediatrician | Pediatric RDN; SLP/OT for feeding | Child / adolescent psych |
| Pediatric specialty needs | Pediatric subspecialist mirror of adult | Pediatric RDN with subspecialty focus | Child psych |
| Mental health | Psychiatry / psychology | RDN with MH co-treatment training | LCSW, LPC, PhD/PsyD |

Refer-out language pattern (per [user-decision-framework.md](../00-meta/user-decision-framework.md)): *"This is typically managed in coordination with [specialty]. NutriMe is not provider-affiliated; this is so you know who to look for."*

### 5. Regulatory landscape — global, B + C levels per Rule 9 (informational, not compliance-driven)

Personal-use distribution context per [product-framing.md](../00-meta/product-framing.md). Map informs where lines are.

#### 5.1 Cross-jurisdictional pattern

The dominant axis across all 11 jurisdictions is **intended use + claim language**: an app that *plans meals according to general healthy-eating guidance* and surfaces evidence-based educational information sits in **wellness / general-purpose health** in most jurisdictions. The same app crosses into **medical device** territory when it (a) **diagnoses** a disease, (b) **prevents, monitors, treats, or alleviates** a specific disease through automated analysis (e.g., calculates insulin doses, computes a CKD-specific potassium prescription, automated pre-eclampsia risk alerts), or (c) **modifies a body function** as primary purpose. Decision-support carve-outs (US 21st Century Cures Act § 520(o)(1)(E)) generally require a clinician (not lay user) be the user, and that the basis of the recommendation be transparent and independently reviewable.

**Harmonization efforts:** [IMDRF SaMD framework](http://www.imdrf.org/working-groups/software-medical-device-samd) (categorizes by criticality of decision + state of healthcare situation/condition); WHO SaMD work; ISO 14971 risk management adopted broadly. No jurisdiction has fully harmonized a "wellness app" definition.

#### 5.2 Per-jurisdiction summary

| Jurisdiction | Body | Wellness vs medical device line |
|--------------|------|----------------------------------|
| US | FDA (CDRH); FTC for advertising | FDA "General Wellness: Policy for Low Risk Devices" (2019) excludes products that promote a *general state of health* without disease references. Disease-specific claims (diabetes management, BP management, oncology nutrition) push into medical device. § 520(o)(1)(E) decision-support carve-out narrow. FTC Act + Health Breach Notification Rule (updated 2024) regulate advertising claims + data breaches for non-HIPAA health apps. |
| Canada | Health Canada (TPD); Innovation, Science and Economic Development Canada | Health Canada Guidance on SaMD (2019, refreshed 2022) follows IMDRF risk-based classification. Wellness/lifestyle apps not making diagnostic/therapeutic claims sit outside Class I–IV device framework. PIPEDA + provincial health-info laws apply. |
| UK | MHRA | Post-Brexit MHRA "Software and AI as a Medical Device Change Programme" (ongoing). UK MDR 2002 (as amended) still references EU classification rules; MHRA crafting UK-specific framework (consultation outcomes 2024–2025). Wellness apps not making diagnostic/therapeutic claims fall outside. **[VERIFY]** post-2025 UKCA marking timeline and CE-recognition extensions. |
| EU | EU MDR (Regulation 2017/745) + national competent authorities; MDCG | EU MDR Rule 11 reclassified much SaMD higher (most clinical-decision SaMD now Class IIa/IIb). MDCG 2019-11 on SaMD qualification + classification is the canonical guidance. EU AI Act (2024) layered on top — high-risk AI for health adds requirements. Wellness apps that don't qualify as medical device under MDR Rule 11 still subject to GDPR + national wellness-product law. |
| Australia | TGA | TGA "Regulation of software based medical devices" (2021 framework + 2022 reforms). "Excluded" software (consumer health information, fitness/wellness with no diagnostic/therapeutic intent) sits outside. Therapeutic Goods (Excluded Goods) Determination 2018 + amendments lists exclusions. Carb-counting / diabetes management apps generally Class IIa or higher. |
| New Zealand | Medsafe | Medical Devices regulated under Medicines Act 1981; less mature SaMD framework than TGA, often references TGA + IMDRF. Therapeutic Products Bill (2023) status **[VERIFY]** — was paused 2024. |
| China | NMPA (formerly CFDA) | NMPA SaMD classification framework (2017, updated 2022) — three classes by risk. Wellness apps generally outside; any app processing patient data for diagnosis/treatment is in scope. PIPL + Cybersecurity Law + Data Security Law create layered data regime. Cross-border data transfer requires CAC review for sensitive personal info. TCM context: NMPA also regulates TCM dietary advice claims separately. |
| Japan | PMDA / MHLW | PMDA + Pharmaceutical Affairs Law (PMD Act). SaMD classification per IMDRF lines; "Program" devices added 2014. METI–MHLW joint guidance (2018, updated) distinguishes wellness from regulated medical software. Strong cultural integration of food + health (Tokuho/FOSHU + Foods with Function Claims) — but those regulate the food, not the app. |
| Korea | MFDS | MFDS SaMD classification + Innovative Medical Device Act (2020). Wellness apps not making diagnostic claims outside scope; "Digital Therapeutics" pathway exists for treatment-claim apps (e.g., insomnia DTx approvals 2023–2024). PIPC + PIPA data law. |
| Israel | Ministry of Health, Medical Device Branch (Aman) | AMAR (Ministry registration) for medical devices; SaMD generally aligns with IMDRF. Wellness apps not making diagnostic claims outside. Privacy Protection Law + 2024 amendments. |
| Russia | Roszdravnadzor | SaMD regulated under Federal Law 323-FZ + Government Decree 1416 (2012, amended). Wellness apps without diagnostic intent outside. Foreign apps subject to data-localization (Federal Law 242-FZ) — copies of personal data of Russian citizens must be on Russian servers. **[VERIFY]** sanctions-era operational impacts on foreign device approval. |

#### 5.3 Where positions materially differ + why

- **Decision-support carve-outs**: US has the most explicit (Cures Act § 520(o)(1)(E)); EU has largely eliminated comparable carve-outs under MDR Rule 11. Reason: post-Poly Implant Prothèse + metal-on-metal hip scandals, EU tightened device oversight; US prioritized digital-health innovation pathway.
- **Cultural-traditional dietary advice**: China's NMPA + TCM Administration regulate health claims of TCM food therapy; Japan's MHLW handles raw-fish guidance reflecting cultural context (sushi/sashimi widely consumed during pregnancy with specific safe-handling guidance, distinct from US blanket avoidance).
- **Soft cheese in pregnancy**: UK NHS distinguishes pasteurised vs unpasteurised soft cheese (allowing pasteurised brie/camembert when others restrict); US/CDC blanket-avoid soft cheese unless labeled pasteurised. Reason: local supply chain assumptions about pasteurisation defaults differ.
- **Mercury / fish guidance**: Japan MHLW gives species-specific quantitative limits per week reflecting high-fish dietary baseline; US FDA/EPA + EU EFSA give "best choices / good choices / avoid" lists; AU/NZ FSANZ aligns to local species. Reason: dietary baseline + local species mix.
- **Listeria advisories**: EU EFSA + national bodies have higher tolerance for some artisanal cheese categories (raw-milk traditional cheeses culturally important); US blanket-restricts. Reason: regulatory culture + culinary heritage protection.
- **Data-residency**: Russia + China have strict data-localization; EU GDPR allows transfer with adequacy/SCCs; US has sectoral patchwork. Reason: sovereignty posture + state security framing.

Sources: [FDA General Wellness Guidance 2019](https://www.fda.gov/media/90652/download); [FDA Cures Act Software Functions Guidance 2022](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software); [EU MDR Reg. 2017/745](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32017R0745); [MDCG 2019-11 SaMD Qualification & Classification](https://health.ec.europa.eu/system/files/2020-09/md_mdcg_2019_11_guidance_qualification_classification_software_en_0.pdf); [EU AI Act 2024](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689); [MHRA Software and AI as a Medical Device Change Programme](https://www.gov.uk/government/publications/software-and-ai-as-a-medical-device-change-programme); [TGA Regulation of Software-Based Medical Devices](https://www.tga.gov.au/resources/resource/guidance/regulation-software-based-medical-devices); [Health Canada SaMD Guidance](https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/application-information/guidance-documents/software-medical-device-guidance.html); [NMPA Classification of Medical Device Software 2022](https://www.nmpa.gov.cn/); [PMDA Medical Device Regulation](https://www.pmda.go.jp/english/review-services/regulatory-info/0001.html); [MFDS Innovative Medical Device Act](https://www.mfds.go.kr/eng/index.do); [IMDRF SaMD Framework N12](http://www.imdrf.org/sites/default/files/docs/imdrf/final/technical/imdrf-tech-131209-samd-key-definitions-140901.pdf).

### 6. Drug-nutrient interactions — base framework + dynamic-expansion hook

#### 6.1 Source qualification framework (per [dynamic-research-expansion.md](../00-meta/dynamic-research-expansion.md))

Tier 1: regulatory drug labels (FDA prescribing information / EMA SmPC / MHRA SPC / Health Canada Product Monograph / TGA PI / PMDA package insert / NMPA prescribing information).
Tier 1–2: clinical-pharmacology databases (Lexicomp, Micromedex, Stockley's Drug Interactions, BNF/BNFc, Martindale, AHFS DI, Natural Medicines Database).
Tier 1–2: peer-reviewed clinical pharmacology literature (Clin Pharmacol Ther, Br J Clin Pharmacol, Drugs, Clinical Pharmacokinetics, Annals of Pharmacotherapy).
Tier 1: official patient-facing food-interaction lists (FDA "Avoid Food–Drug Interactions" booklet, NHS Drug-Food Interactions, USDA/NIH Office of Dietary Supplements).

#### 6.2 Common interactions — depth coverage

| Drug / class | Nutrient / food | Mechanism | Behavior |
|--------------|-----------------|-----------|----------|
| Warfarin | Vitamin K (leafy greens, green tea, natto, some oils) | VKOR inhibition; vitamin K reverses | **Consistency** rail — system targets stable daily vitamin K; surfaces high-K foods + asks about INR monitoring cadence. Natto effectively contraindicated. Avoid St John's Wort (induces CYP). |
| MAO inhibitors (phenelzine, tranylcypromine, isocarboxazid; selegiline at high dose; linezolid; methylene blue) | Tyramine (aged cheese, cured/fermented meats, soy sauce, miso, sauerkraut, fava beans, broad beans, draft/unpasteurised beer, aged wines, marmite/vegemite) | MAO inhibition → tyramine pressor crisis | Hard gate — strict avoidance list; surfaces low-tyramine alternatives |
| Statins (simvastatin, lovastatin, atorvastatin to lesser extent) | Grapefruit / pomelo / Seville orange | CYP3A4 inhibition → ↑ statin → rhabdo risk | Avoidance rail (or dose-timing per prescriber). Pravastatin + rosuvastatin minimally affected. |
| SSRIs / SNRIs / triptans / tramadol / linezolid | St John's Wort | Serotonin syndrome | Avoidance + audit-as-education on supplement evidence |
| Levothyroxine | Calcium, iron, fiber, soy, coffee, PPIs | Absorption interference (chelation + stomach pH) | Timing rail — take 30–60 min before food / 4 hr from Ca/Fe/PPI/soy/coffee |
| ACE inhibitors / ARBs / K-sparing diuretics (spironolactone, eplerenone) / amiloride | Potassium (K-rich foods + salt substitutes which are KCl) | ↑ serum K | Awareness rail; avoid potassium chloride salt substitutes; coordinate with prescriber on high-K foods |
| Metformin | Vitamin B12 | Long-term ileal absorption ↓ | Periodic B12 surveillance (prescriber); B12-rich foods + supplementation if low |
| PPIs (long-term) | B12, Mg, Ca (non-citrate), Fe (non-heme) | ↓ acidity → ↓ absorption | Awareness + Ca-citrate option; Mg monitoring on long-term; bone density context |
| Loop / thiazide diuretics | Sodium, potassium, magnesium (loops + thiazides), calcium (thiazides ↑ retention; loops ↑ loss) | Renal handling | Awareness rail; coordinate with prescriber |
| Lithium | Sodium consistency, fluid consistency, caffeine | Renal Li handling tracks Na | **Consistency** rail (do not crash-diet sodium); avoid abrupt changes in caffeine/fluid |
| Antibiotics — tetracyclines, fluoroquinolones | Calcium, iron, magnesium, zinc, dairy, antacids | Chelation | Time separation (2 hr before / 6 hr after dairy/cation supplements) |
| Bisphosphonates (oral — alendronate, risedronate) | Any food, beverages other than plain water, calcium, coffee | Absorption ↓ | Strict timing rail (30–60 min fasting plain water only) |
| HIV — integrase inhibitors (dolutegravir, bictegravir, raltegravir) | Polyvalent cations (Ca, Fe, Mg, Al, Zn) | Chelation | Time separation |
| HIV — efavirenz | High-fat meals | ↑ absorption → CNS side effects | Avoid high-fat dosing |
| HIV — rilpivirine | Meal required | ↑ absorption | Take with meal |
| Tacrolimus, cyclosporine, sirolimus, everolimus, lomitapide, many oral oncologics (e.g., nilotinib, dasatinib, ibrutinib, palbociclib, venetoclax, lapatinib) | Grapefruit / Seville orange / pomelo | CYP3A4 inhibition | Avoidance rail |
| Anticoagulants (DOACs — apixaban, rivaroxaban, edoxaban, dabigatran) | Generally less food-dependent than warfarin; rivaroxaban 15/20 mg taken with food | — | Mostly proceed-with-disclaimer + St John's Wort avoidance |
| Sulfonylureas / insulin | Carbohydrate quantity + alcohol | Hypoglycemia risk | Carb-counting rail; alcohol context; prescriber coordination |
| GLP-1 RAs / GIP-GLP1 (semaglutide, tirzepatide, dulaglutide) | High-fat / large-volume meals → GI symptoms; gastroparesis risk | Slowed gastric emptying | Portion + meal-composition rails |
| Isoniazid (TB) | Tyramine (less than MAOI but reported), histamine (cured fish), B6 (depletion) | MAO weak inhibition + B6 antagonism | Awareness; B6 supplementation per prescriber; tyramine moderate avoidance |
| Allopurinol / azathioprine / mercaptopurine | — | Allopurinol ↑ thiopurine toxicity (drug-drug, not nutrient) | Out of scope here |
| Chemotherapy oral agents broadly | Grapefruit, St John's Wort, high-dose vitamin C/E (varies), specific food–drug pairs per regimen | CYP, antioxidant interference (contested), absorption | Refer-out to oncology-pharmacy + CSO RDN |
| Carbidopa/levodopa | High-protein meals (LNAA competition) | ↓ absorption | Distribute protein away from doses; coordinate with neurology |
| Phenytoin | Enteral nutrition, folate, vitamin D | Absorption + chronic depletion | Timing rail with EN; folate/D context |
| Cholestyramine / bile-acid sequestrants | Fat-soluble vitamins (A, D, E, K), folate | Binding | Timing separation; supplementation context |
| Orlistat | Fat-soluble vitamins | Inhibits lipase → ↓ absorption | Multivitamin timing rail |
| Aluminum/magnesium antacids | Phosphate, fluoride, iron, tetracyclines | Binding | Timing separation |
| Methotrexate | Folate | Antagonism | Folate supplementation per rheum |
| Calcineurin inhibitors (tacrolimus, cyclosporine) | Grapefruit, pomegranate, St John's Wort | CYP3A4 | Avoidance |
| Beta-blockers (some) | Food (some labeled "with food" for tolerability) | — | Per label |
| Erythromycin / clarithromycin | Grapefruit minimally; many drug-drug | CYP3A4 | Mostly drug-drug |
| Fluoroquinolones | Caffeine (slowed metabolism), dairy/cations | CYP1A2 + chelation | Caffeine awareness; cation timing |
| Theophylline | Caffeine, charbroiled foods (PAH induction), high-protein/low-carb diets | CYP1A2 | Awareness; narrow therapeutic index |
| Antiretrovirals beyond above | Per regimen | — | Per label |
| Iron supplements | Calcium, coffee/tea (tannins), phytates, dairy | Absorption ↓ | Timing rail; vitamin C cofactor |
| Calcium supplements | Iron, levothyroxine, fluoroquinolones, tetracyclines, bisphosphonates | Chelation | Timing |
| Aspirin (chronic) | Vitamin C, folate | Mild absorption interactions | Awareness |
| Spironolactone | K + licorice (glycyrrhizin contradicts spironolactone effect) | Pharmacodynamic | Avoidance of licorice in heart failure / hypertension |

#### 6.3 Dynamic-expansion hook

When a user reports a drug not in the base, the system invokes the [dynamic-research-expansion](../00-meta/dynamic-research-expansion.md) pipeline against the qualification framework above. Verification step requires (a) a regulatory label match for the drug, (b) at least one Tier 1–2 confirmation of the food/nutrient interaction, (c) cross-check against pharmacopoeia. If interaction is contested in literature, surface the contest per Rule 8.

#### 6.4 Alert-fatigue UX evidence base

Clinical decision-support literature consistently finds that >90 % override rates of drug-allergy/interaction alerts indicate alert fatigue ([van der Sijs et al. 2006](https://doi.org/10.1197/jamia.M1809); [Ancker et al. 2017](https://doi.org/10.1186/s12911-017-0430-8)). Design implications for NutriMe:

- **Tier alerts by severity** — "consistency" rails ≠ "hard avoidance" rails ≠ "consult-prescriber" rails; visual + interaction differentiation
- **Contextualize, don't repeat** — if user has acknowledged grapefruit/statin once at intake, do not re-alert on every recipe; surface in audit-trail
- **Action-link the alert** — "swap this ingredient" / "show alternatives" rather than alert-only
- **Suppress consensus-low-severity, surface consensus-high-severity**
- **Aggregate at meal level**, not ingredient level, to reduce burst alerts
- **Provide an explicit, accessible "show me everything" view** for users who want depth

Sources: [van der Sijs et al. 2006](https://doi.org/10.1197/jamia.M1809); [Ancker et al. 2017 BMC Med Inform Decis Mak](https://doi.org/10.1186/s12911-017-0430-8); [Phansalkar et al. 2010 JAMIA](https://doi.org/10.1136/jamia.2009.000257); [Co et al. 2020 systematic review](https://doi.org/10.1093/jamia/ocaa098).

### 7. Pregnancy + lactation safety — comparative global

Comparative table of food-avoidance positions equal-weighted per Rule 9. Surface differences honestly with regional/population reasons.

#### 7.1 Comparative pregnancy avoidance — high-evidence categories

| Category | US (FDA / ACOG / CDC) | EU (EFSA + national) | UK (NHS) | AU/NZ (FSANZ) | Japan (MHLW) | China |
|----------|----------------------|----------------------|----------|---------------|--------------|-------|
| Listeria — soft cheeses | Avoid all unless labeled pasteurised; avoid Brie, Camembert, blue, queso fresco/blanco unless pasteurised | National variation; many EU bodies allow pasteurised soft + restrict raw-milk | NHS allows pasteurised soft cheeses; restricts raw-milk + mould-ripened soft (brie/camembert) **unless cooked thoroughly** | Avoid all soft, semi-soft, surface-ripened, soft blue cheeses (cooked OK) | Avoid raw-milk soft cheeses | Generally aligned with WHO + national variation |
| Deli meats / cold cuts | Heat to steaming (CDC) | National variation; EFSA listeria position similar | NHS: pâté avoid; cured meats — "small risk" Toxoplasma, low risk if cured properly, optional reheat | Avoid pre-prepared deli meats | Reheat | Reheat |
| Raw/undercooked fish & sushi | Avoid (FDA/CDC) | Avoid raw (EFSA) | NHS: cold-smoked fish OK pasteurised; sushi OK if previously frozen | Avoid raw seafood | **Allowed with safe-handling guidance** — cultural integration of sushi/sashimi during pregnancy; MHLW gives species-specific Hg limits | Mixed; coastal vs inland norms differ |
| Mercury — fish species | FDA/EPA "Best/Good/Avoid": avoid king mackerel, marlin, orange roughy, shark, swordfish, tilefish, bigeye tuna; limit albacore | EFSA TWI 1.3 µg/kg bw; species lists per country | NHS: avoid shark, swordfish, marlin; limit tuna (≤ 2 fresh / 4 cans medium) | FSANZ: similar list adapted to AU species; orange roughy, marlin, swordfish, shark limit | MHLW: detailed species table with weekly gram limits — bluefin/bigeye/swordfish ≤ 80 g/wk, etc. | National/regional fish guidance |
| Liver / vitamin A | Avoid liver products (high vitamin A) per ACOG | Avoid (EFSA UL retinol pregnancy 3000 µg/d) | NHS: avoid all liver/liver products | Avoid | Avoid | Avoid |
| Alcohol | Abstain (US Surgeon General + ACOG) | Abstain (most national bodies) | Abstain (NHS / RCOG 2016 update) | Abstain (NHMRC) | Abstain (MHLW) | Abstain |
| Caffeine | ≤ 200 mg/d (ACOG) | ≤ 200 mg/d (EFSA) | ≤ 200 mg/d (NHS) | ≤ 200 mg/d (FSANZ) | ≤ 200–300 mg/d (MHLW) | ≤ 200 mg/d typical |
| Raw eggs | Avoid; or use pasteurised | Lion-mark eggs in UK now considered safe raw (NHS 2017 update) | NHS: British Lion eggs OK runny/raw in pregnancy | Avoid raw | Cultural raw-egg use in some dishes; advisory toward avoidance in pregnancy | Generally avoid |
| Toxoplasma — undercooked meat, soil/cat litter, unwashed produce | Avoid (CDC) | Avoid (EFSA) | NHS detailed guidance | Avoid | Avoid | Avoid |
| Sprouts (alfalfa, mung, clover) | Avoid raw (FDA) | Avoid raw | Avoid raw | Avoid raw | Avoid raw | Avoid raw |
| Unpasteurised milk / juices | Avoid | Avoid (some traditional raw-milk products culturally protected) | Avoid raw milk; pasteurised OK | Avoid | Avoid | Avoid |
| Herbal teas / TCM herbs | "Caution; not well studied" | National variation | NHS: "fine in moderation"; specific avoid list (e.g., raspberry leaf 3rd trim only) | Caution | — | TCM-specific extensive avoidance lists during pregnancy (some TCM herbs contraindicated; others traditionally indicated by phase — surface comparatively per Rule 9) |
| Soy isoflavones / soy products | No restriction | No restriction | No restriction | No restriction | Cultural staple — no restriction | Cultural staple — no restriction |

Why differences:
- **Raw-milk cheese**: EU heritage cheese protections; UK pasteurisation defaults; US blanket-restriction reflects supply-chain variability.
- **Sushi**: Japan's deep cultural integration + freezing/handling infrastructure → conditional acceptance with safe-handling; Western bodies blanket-avoid.
- **Eggs**: UK 2017 reclassification (Lion mark) shifted from blanket-avoid to conditional-OK; US has not adopted parallel reclassification.
- **TCM herbs**: China's MoH coordinates with TCM bodies; phase-based pregnancy use (some indicated, some contraindicated) reflects traditional pharmacopoeia integrated into modern guidance.
- **Caffeine**: convergent at 200 mg/d across major bodies — strong harmonization point.

Sources: [ACOG Nutrition During Pregnancy FAQ](https://www.acog.org/womens-health/faqs/nutrition-during-pregnancy); [FDA Advice About Eating Fish 2022](https://www.fda.gov/food/consumers/advice-about-eating-fish); [CDC Listeria + Pregnancy](https://www.cdc.gov/listeria/prevention/pregnant-women.html); [EFSA Scientific Opinion on Caffeine 2015](https://doi.org/10.2903/j.efsa.2015.4102); [EFSA Scientific Opinion on Methylmercury Tolerable Weekly Intake 2012](https://doi.org/10.2903/j.efsa.2012.2985); [NHS Foods to Avoid in Pregnancy](https://www.nhs.uk/pregnancy/keeping-well/foods-to-avoid/); [FSANZ Food Safety in Pregnancy](https://www.foodstandards.gov.au/consumer/generalissues/pregnancy); [MHLW Mercury in Fish Pregnancy Advisory (Japanese)](https://www.mhlw.go.jp/topics/bukyoku/iyaku/syoku-anzen/suigin/); [NHMRC Australian Pregnancy Care Guidelines](https://www.health.gov.au/resources/pregnancy-care-guidelines); [Health Canada Safe Food Handling for Pregnant Women](https://www.canada.ca/en/health-canada/services/food-safety-vulnerable-populations.html); [WHO Guideline on Healthy Diet During Pregnancy](https://www.who.int/health-topics/maternal-health).

#### 7.2 Lactation-specific guidance

| Topic | US (CDC / AAP) | UK (NHS) | EU / EFSA | AU (NHMRC) | Japan (MHLW) |
|-------|----------------|----------|-----------|------------|--------------|
| Alcohol | Up to 1 std/d after metabolism (~2 hr per std drink); express-and-discard not required | Same general guidance | Similar | Similar | Caution-leaning |
| Caffeine | ≤ 200–300 mg/d | ≤ 200 mg/d | EFSA: 200 mg/d single dose, 200 mg/d total in lactating | ≤ 200 mg/d | ≤ 200–300 mg/d |
| Fish / mercury | Same as pregnancy lists | Same | Same | Same | Species-specific MHLW table |
| Allergens in maternal diet | **Do not restrict** to prevent infant allergy (post-LEAP consensus) | Same | Same | Same | Generally aligned |
| Maternal vegan/vegetarian | B12 supplementation essential; iodine, omega-3 attention | Same | Same | Same | Same |
| Galactagogues (fenugreek, blessed thistle, domperidone) | Tier 3/4 evidence; AAP cautions on domperidone US off-label | Domperidone used in UK with caution | EMA restrictions on domperidone | Used with caution | Limited use |
| Spicy / "gassy" foods | No avoidance recommendation; case-by-case | Same | Same | Same | Same |
| Infant FPIAP (blood/mucus stool) | Maternal elimination of cow's milk ± soy if confirmed | Same | Same | Same | Same |
| Drug compatibility | LactMed first-line resource | BNF + UKDILAS | Hale's reference | Same as US | Local pharmacopoeia + LactMed |

Sources: [AAP Breastfeeding 2022](https://doi.org/10.1542/peds.2022-057988); [LactMed (NIH)](https://www.ncbi.nlm.nih.gov/books/NBK501922/); [CDC Vaccinations + Medications While Breastfeeding](https://www.cdc.gov/breastfeeding/breastfeeding-special-circumstances/index.html); [NHS Breastfeeding and Diet](https://www.nhs.uk/conditions/baby/breastfeeding-and-bottle-feeding/breastfeeding-and-lifestyle/diet/); [Du Toit et al. 2015 LEAP NEJM](https://doi.org/10.1056/NEJMoa1414850); [Greer et al. 2019 AAP Clinical Report on Allergen Introduction](https://doi.org/10.1542/peds.2019-0281).

### 8. Answers to "Open questions for the research"

**Q1. For each condition class — what's the published evidence base for the gating behavior we should adopt?**

The gating-behavior evidence base differs sharply by class:
- **T1D, oncology active treatment, post-bariatric early phase, decompensated cirrhosis, severe CKD/dialysis, active EDs, pediatric IEM**: strong Tier 1 specialty-society guidance (ADA/ISPAD, ASCO/ESMO/ASMBS, AASLD/EASL, KDOQI/KDIGO, APA/AED/NICE) supports refuse-without-team posture for unsupported lay-tooling. Evidence basis = standard-of-care safety, not RCTs of "app-only intervention."
- **Uncomplicated T2D / hypertension / dyslipidemia / GERD / IBS / stable autoimmune / NAFLD / gout / osteoporosis**: Tier 1/2 evidence supports defined dietary patterns (Mediterranean, DASH, low-FODMAP-time-limited, etc.) — proceed-with-disclaimer is supportable.
- **Microbiome / nutrigenomic personalization, SIBO testing, food-sensitivity IgG, NCGS without celiac**: Tier 3/4 evidence at best — audit-as-education posture.
- **Pediatric obesity AAP 2023**: contested guidance; behavior assignment requires second pass.
- **Pediatric ARFID, pediatric T1D, pediatric oncology**: Tier 1 evidence supports refuse-without-team.

**Q2. Where do regulatory positions on wellness-vs-medical-device cross internationally? Are there harmonization efforts?**

Convergent on intent-and-claim axis (IMDRF SaMD risk framework adopted broadly). Divergent on (a) decision-support carve-outs (US wide, EU narrow post-MDR), (b) traditional/cultural advice integration (China TCM, Japan FOSHU), (c) data-residency overlay (Russia, China strict; EU GDPR; US sectoral). Harmonization efforts: IMDRF (active), WHO (advisory), ISO 14971/IEC 62304/IEC 82304-1. EU AI Act (2024) layers a new high-risk-AI regime on top.

**Q3. For dynamic-research-expansion applied to drug-nutrient interactions — which authoritative sources are reliably accessible for fetch + verification?**

Reliably available:
- DailyMed (NLM — US drug labels, structured product labeling) — robust API
- openFDA — drug + label endpoints, robust API
- EMA SmPCs — accessible per product
- MHRA emc — accessible per product
- Health Canada Drug Product Database
- NLM LactMed (free) — lactation
- NIH ODS Fact Sheets — supplement / nutrient interactions
- NHS website food-drug interaction pages
- Less freely accessible (institutional license): Lexicomp, Micromedex, Stockley's, Natural Medicines, BNF/BNFc digital
- Peer-reviewed: PubMed for verification; can confirm but not always download full text
Recommendation: build DailyMed + openFDA + EMA SmPC + LactMed + NIH ODS as primary fetch path; cross-confirm via PubMed abstract; surface licensed-database citations as references when system has access.

**Q4. For pediatric conditions — how does the literature handle parent-mediated intake for clinical data quality?**

Pediatric assessment instruments are designed for parent-proxy reporting in younger children with explicit attention to known biases (recall, social desirability, parent-child dietary mismatch in school-aged). Validated instruments (NutriSTEP, ChEAT, KEDS, PARDI-AR-Q) report psychometrics specifically in parent-proxy use. For adolescents, self-report with parent corroboration is standard; growth chart trajectory + biomarkers are the objective backstop. Implications for NutriMe: (a) clearly attribute intake to reporter, (b) allow parent + adolescent dual-input where age-appropriate, (c) treat growth trajectory as a verification signal in epistemic trail, (d) gate behavior on confirmed clinical data (allergist OFC, GI biopsy, endocrinologist regimen) over self-reported diagnoses.

**Q5. Published evidence on alert fatigue in drug-nutrient warning systems — how to surface without it?**

See § 6.4 above. Core findings:
- Override rates >90 % for non-tiered alerts (van der Sijs 2006)
- Tiered severity, action-linked alerts, suppression of low-value alerts, aggregation, and contextual relevance reduce fatigue without compromising safety (Phansalkar 2010, Ancker 2017, Co 2020)
- "Just-in-time" alerts at decision point outperform passive lists
- User customization of alert thresholds within a safety floor improves engagement
- Clinical decision-support guidelines (CPOE literature) translate well to consumer-facing nutrition decision support

### 9. Cross-sweep observations

- **Sweep #3 screener → gating signal map**: SCOFF/EAT-26/PARDI-AR-Q positive → ED gating; Hunger Vital Sign positive → resource-aware planning + refer-out (not refuse); AUDIT-C high → ALD context + pregnancy alcohol gate; pregnancy/lactation status → life-stage stack; PSQI poor → caffeine timing context; PHQ-9/GAD-7 high → MH refer-out, no system "treatment" framing; cooking confidence low → recipe-modality adjustment (per [sweep #11](../11-recipe-sourcing/scope.md)).
- **Sweep #2 lookup needs**: condition-relevant nutrients (K, P, Na for CKD; vitamin K for warfarin; tyramine for MAOI; fiber for gastroparesis; oxalate for stones; purines for gout; iodine for thyroid + pregnancy/lactation; choline for pregnancy; iron + B12 for many) require composition-database fields not always available in base USDA FNDDS — flag for [sweep #2](../02-food-composition-databases/scope.md).
- **Sweep #9 priority tier**: conditions resolved at tier 2 (medical + life-stage) per household-conflict prioritization; this sweep populates the tier 2 corpus.
- **Sweep #11 recipe filter**: condition gating produces filter predicates (allergen-avoidance, low-FODMAP, low-K, low-Na, GF, etc.) that recipe sourcing must support.

## References

> Per [citation-style.md](../00-meta/citation-style.md). Accessed-on date `2026-04-29` for all web sources. Add to [sources.md](../00-meta/sources.md) in the consolidation pass (do not edit here per sweep instructions).

### Cardiovascular
- **Whelton et al.** (2017). *2017 ACC/AHA/AAPA/ABC/ACPM/AGS/APhA/ASH/ASPC/NMA/PCNA Guideline for the Prevention, Detection, Evaluation, and Management of High Blood Pressure in Adults*. Hypertension. https://doi.org/10.1161/HYP.0000000000000065. Accessed 2026-04-29.
- **McEvoy et al.** (2024). *2024 ESC Guidelines for the management of elevated blood pressure and hypertension*. European Heart Journal. https://doi.org/10.1093/eurheartj/ehae178. Accessed 2026-04-29.
- **Heidenreich et al.** (2022). *2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure*. Circulation. https://doi.org/10.1161/CIR.0000000000001063. Accessed 2026-04-29.

### Metabolic / endocrine
- **ADA** (2025). *Standards of Care in Diabetes—2025*. Diabetes Care 48(Suppl 1). https://doi.org/10.2337/dc25-SINT. Accessed 2026-04-29.
- **Davies et al.** (2022). *Management of hyperglycaemia in type 2 diabetes, 2022 — A consensus report by the ADA and EASD*. Diabetes Care. https://doi.org/10.2337/dci22-0034. Accessed 2026-04-29.
- **AACE** (2023). *Comprehensive Type 2 Diabetes Management Algorithm*. Endocrine Practice. https://doi.org/10.1016/j.eprac.2023.02.001. Accessed 2026-04-29.
- **Rinella et al.** (2023). *AASLD Practice Guidance on the clinical assessment and management of MASLD*. Hepatology. https://doi.org/10.1097/HEP.0000000000000323. Accessed 2026-04-29.
- **Teede et al.** (2023). *Recommendations from the 2023 International Evidence-based Guideline for PCOS*. Human Reproduction. https://doi.org/10.1093/humrep/dead156. Accessed 2026-04-29.

### Renal
- **KDOQI** (2020). *Clinical Practice Guideline for Nutrition in CKD: 2020 Update*. AJKD. https://doi.org/10.1053/j.ajkd.2020.05.006. Accessed 2026-04-29.
- **KDIGO** (2024). *KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of CKD*. Kidney International. https://doi.org/10.1016/j.kint.2023.10.018. Accessed 2026-04-29.

### Gastrointestinal
- **Lacy et al.** (2021). *ACG Clinical Guideline: Management of Irritable Bowel Syndrome*. AJG. https://doi.org/10.14309/ajg.0000000000001036. Accessed 2026-04-29.
- **Vasant et al.** (2021). *British Society of Gastroenterology guidelines on the management of irritable bowel syndrome*. Gut. https://doi.org/10.1136/gutjnl-2021-324598. Accessed 2026-04-29.
- **Monash University** (n.d.). *About FODMAPs and IBS*. https://www.monashfodmap.com/about-fodmap-and-ibs/. Accessed 2026-04-29.
- **Rubio-Tapia et al.** (2023). *American College of Gastroenterology Guidelines: Diagnosis and Management of Celiac Disease*. AJG. https://doi.org/10.14309/ajg.0000000000002075. Accessed 2026-04-29.
- **Bischoff et al.** (2023). *ESPEN guideline on Clinical Nutrition in Inflammatory Bowel Disease*. Clinical Nutrition. https://doi.org/10.1016/j.clnu.2022.12.004. Accessed 2026-04-29.
- **Dellon et al.** (2022). *AGA/JTF Clinical Practice Guideline on the Management of Eosinophilic Esophagitis*. Gastroenterology. https://doi.org/10.1053/j.gastro.2022.05.045. Accessed 2026-04-29.

### Hepatic
- **Tapper & Parikh** (2021). *Diagnosis and management of cirrhosis and its complications: AASLD Practice Guidance*. Hepatology. https://doi.org/10.1002/hep.32049. Accessed 2026-04-29.
- **EASL** (2022). *Clinical Practice Guidelines on the Management of Patients with Decompensated Cirrhosis*. Journal of Hepatology. https://doi.org/10.1016/j.jhep.2021.12.022. Accessed 2026-04-29.

### Autoimmune
- **Fraenkel et al.** (2021). *2021 ACR Guideline for the Treatment of Rheumatoid Arthritis*. Arthritis Care & Research. https://doi.org/10.1002/art.41752. Accessed 2026-04-29.
- **Gwinnutt et al.** (2023). *2021 EULAR recommendations regarding lifestyle behaviours and work participation*. ARD. https://doi.org/10.1136/ard-2022-223260. Accessed 2026-04-29.

### Eating disorders
- **APA** (2023). *Practice Guideline for the Treatment of Patients with Eating Disorders, 4th ed.* APA Publishing. https://doi.org/10.1176/appi.books.9780890424865. Accessed 2026-04-29.
- **NICE** (2017, updated 2020). *NG69 Eating Disorders: recognition and treatment*. https://www.nice.org.uk/guidance/ng69. Accessed 2026-04-29.
- **Academy for Eating Disorders** (2021). *Medical Care Standards Guide, 4th ed.* https://www.aedweb.org/publications/medical-care-standards. Accessed 2026-04-29.

### Oncology
- **WCRF/AICR** (2018, ongoing CUP updates). *Diet, Nutrition, Physical Activity and Cancer: a Global Perspective + Cancer Prevention Recommendations*. https://www.wcrf.org/diet-activity-and-cancer/cancer-prevention-recommendations/. Accessed 2026-04-29.
- **Rock et al.** (2022). *American Cancer Society nutrition and physical activity guideline for cancer survivors*. CA Cancer J Clin. https://doi.org/10.3322/caac.21719. Accessed 2026-04-29.
- **Muscaritoli et al.** (2021). *ESPEN practical guideline: Clinical Nutrition in cancer*. Clinical Nutrition. https://doi.org/10.1016/j.clnu.2021.02.005. Accessed 2026-04-29.

### Bariatric
- **Mechanick et al.** (2019). *Clinical Practice Guidelines for the Perioperative Nutrition, Metabolic, and Nonsurgical Support of Patients Undergoing Bariatric Procedures — 2019 Update: ASMBS/AACE/TOS/ASA*. SOARD. https://doi.org/10.1016/j.soard.2019.10.025. Accessed 2026-04-29.
- **BOMSS** (2020). *British Obesity & Metabolic Surgery Society Nutritional Guidance*. https://bomss.org/wp-content/uploads/2022/10/BOMSS-Nutritional-Guidance.pdf. Accessed 2026-04-29.

### Allergies / gout / osteoporosis
- **NIAID** (2010, 2017 update on peanut). *Guidelines for the Diagnosis and Management of Food Allergy in the United States*. https://www.niaid.nih.gov/diseases-conditions/food-allergy-guidelines. Accessed 2026-04-29.
- **Muraro et al.** (2022). *EAACI Guidelines: Anaphylaxis (2021 update) + Food allergy and anaphylaxis*. Allergy. https://doi.org/10.1111/all.15032. Accessed 2026-04-29.
- **FitzGerald et al.** (2020). *2020 ACR Guideline for the Management of Gout*. Arthritis Care & Research. https://doi.org/10.1002/art.41247. Accessed 2026-04-29.
- **Eastell et al.** (2019, updated 2020). *Pharmacological Management of Osteoporosis in Postmenopausal Women: An Endocrine Society Clinical Practice Guideline*. JCEM. https://doi.org/10.1210/clinem/dgaa048. Accessed 2026-04-29.
- **Du Toit et al.** (2015). *Randomized Trial of Peanut Consumption in Infants at Risk for Peanut Allergy (LEAP)*. NEJM. https://doi.org/10.1056/NEJMoa1414850. Accessed 2026-04-29.
- **Greer et al.** (2019). *The Effects of Early Nutritional Interventions on the Development of Atopic Disease in Infants and Children: AAP Clinical Report*. Pediatrics. https://doi.org/10.1542/peds.2019-0281. Accessed 2026-04-29.

### Pediatric
- **Hampl et al.** (2023). *AAP Clinical Practice Guideline for the Evaluation and Treatment of Children and Adolescents with Obesity*. Pediatrics. https://doi.org/10.1542/peds.2022-060640. Accessed 2026-04-29.
- **NASPGHAN/ESPGHAN** (2022). *Position paper on management of pediatric IBD*. JPGN. https://doi.org/10.1097/MPG.0000000000003222. Accessed 2026-04-29.
- **Husby et al.** (2020). *ESPGHAN Guidelines for the Diagnosis of Coeliac Disease 2020*. JPGN. https://doi.org/10.1097/MPG.0000000000002497. Accessed 2026-04-29.
- **ISPAD** (2022). *ISPAD Clinical Practice Consensus Guidelines 2022*. Pediatric Diabetes. https://doi.org/10.1111/pedi.13428. Accessed 2026-04-29.
- **Satter, E.** (n.d.). *The Division of Responsibility in Feeding*. Ellyn Satter Institute. https://www.ellynsatterinstitute.org/how-to-feed/the-division-of-responsibility-in-feeding/. Accessed 2026-04-29.
- **WHO** (2006). *Child Growth Standards*. https://www.who.int/tools/child-growth-standards. Accessed 2026-04-29.
- **CDC** (2022 extended). *CDC Growth Charts*. https://www.cdc.gov/growthcharts/. Accessed 2026-04-29.

### Life-stage
- **ACOG** (n.d., updated). *Nutrition During Pregnancy*. https://www.acog.org/womens-health/faqs/nutrition-during-pregnancy. Accessed 2026-04-29.
- **WHO** (2016, ongoing). *WHO recommendations on antenatal care for a positive pregnancy experience*. https://www.who.int/publications/i/item/9789241549912. Accessed 2026-04-29.
- **NICE** (2021). *NG201 Antenatal care*. https://www.nice.org.uk/guidance/ng201. Accessed 2026-04-29.
- **EFSA** (n.d.). *Dietary Reference Values*. https://www.efsa.europa.eu/en/topics/topic/dietary-reference-values. Accessed 2026-04-29.
- **AAP** (2022). *Breastfeeding and the Use of Human Milk*. Pediatrics. https://doi.org/10.1542/peds.2022-057988. Accessed 2026-04-29.
- **NIH** (n.d., continually updated). *LactMed Database*. https://www.ncbi.nlm.nih.gov/books/NBK501922/. Accessed 2026-04-29.
- **WHO** (n.d.). *Infant and Young Child Feeding*. https://www.who.int/news-room/fact-sheets/detail/infant-and-young-child-feeding. Accessed 2026-04-29.
- **AAP Bright Futures** (2021, 4th ed.). *Nutrition Pocket Guide*. https://brightfutures.aap.org/materials-and-tools/nutrition-pocket-guide/Pages/default.aspx. Accessed 2026-04-29.
- **SAHM** (2022). *Eating Disorders in Adolescents: Position Paper*. J Adolesc Health. https://doi.org/10.1016/j.jadohealth.2022.05.012. Accessed 2026-04-29.
- **Volkert et al.** (2022). *ESPEN practical guideline: Clinical nutrition and hydration in geriatrics*. Clinical Nutrition. https://doi.org/10.1016/j.clnu.2022.01.024. Accessed 2026-04-29.
- **Bauer et al.** (2013). *Evidence-based recommendations for optimal dietary protein intake in older people: PROT-AGE position*. JAMDA. https://doi.org/10.1016/j.jamda.2013.05.021. Accessed 2026-04-29.
- **IDDSI** (2019, framework v2.0). *International Dysphagia Diet Standardisation Initiative*. https://iddsi.org/framework/. Accessed 2026-04-29.
- **Thomas et al.** (2016). *Nutrition and Athletic Performance: ACSM/AND/Dietitians of Canada Joint Position*. JAND. https://doi.org/10.1016/j.jand.2015.12.006. Accessed 2026-04-29.
- **Maughan et al.** (2018). *IOC consensus statement: dietary supplements and the high-performance athlete*. BJSM. https://doi.org/10.1136/bjsports-2018-099027. Accessed 2026-04-29.
- **Mountjoy et al.** (2023). *2023 International Olympic Committee's (IOC) consensus statement on Relative Energy Deficiency in Sport (REDs)*. BJSM. https://doi.org/10.1136/bjsports-2023-106994. Accessed 2026-04-29.

### Regulatory landscape
- **FDA** (2019). *General Wellness: Policy for Low Risk Devices — Guidance*. https://www.fda.gov/media/90652/download. Accessed 2026-04-29.
- **FDA** (2022). *Clinical Decision Support Software — Guidance*. https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software. Accessed 2026-04-29.
- **EU** (2017). *Regulation (EU) 2017/745 on medical devices (MDR)*. https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32017R0745. Accessed 2026-04-29.
- **MDCG** (2019). *MDCG 2019-11: Guidance on Qualification and Classification of Software in Regulation (EU) 2017/745*. https://health.ec.europa.eu/system/files/2020-09/md_mdcg_2019_11_guidance_qualification_classification_software_en_0.pdf. Accessed 2026-04-29.
- **EU** (2024). *Regulation (EU) 2024/1689 (AI Act)*. https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689. Accessed 2026-04-29.
- **MHRA** (ongoing). *Software and AI as a Medical Device Change Programme*. https://www.gov.uk/government/publications/software-and-ai-as-a-medical-device-change-programme. Accessed 2026-04-29.
- **TGA** (2021, updated). *Regulation of software-based medical devices*. https://www.tga.gov.au/resources/resource/guidance/regulation-software-based-medical-devices. Accessed 2026-04-29.
- **Health Canada** (2019, updated). *Software as a Medical Device (SaMD): Definition and Classification*. https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/application-information/guidance-documents/software-medical-device-guidance.html. Accessed 2026-04-29.
- **NMPA** (2022). *Classification of Medical Device Software*. https://www.nmpa.gov.cn/. Accessed 2026-04-29. **[VERIFY]**
- **PMDA** (n.d., updated). *Regulatory Information for Medical Devices*. https://www.pmda.go.jp/english/review-services/regulatory-info/0001.html. Accessed 2026-04-29.
- **MFDS** (n.d.). *Innovative Medical Device Act portal*. https://www.mfds.go.kr/eng/index.do. Accessed 2026-04-29.
- **IMDRF** (2014). *Software as a Medical Device (SaMD): Key Definitions, IMDRF/SaMD WG/N12FINAL:2013*. http://www.imdrf.org/sites/default/files/docs/imdrf/final/technical/imdrf-tech-131209-samd-key-definitions-140901.pdf. Accessed 2026-04-29.
- **Israeli MoH Medical Device Branch (Aman)** (n.d.). *Medical Device Registration (AMAR)*. https://www.health.gov.il/English/Topics/MedicalDevices/Pages/default.aspx. Accessed 2026-04-29.
- **Roszdravnadzor** (n.d.). *Medical Device Registration*. https://roszdravnadzor.gov.ru/en. Accessed 2026-04-29. **[VERIFY]**

### Drug-nutrient interactions + alert fatigue
- **NLM DailyMed** (n.d.). *Drug Label Repository*. https://dailymed.nlm.nih.gov/dailymed/. Accessed 2026-04-29.
- **openFDA** (n.d.). *Drug Label and Adverse Event APIs*. https://open.fda.gov/. Accessed 2026-04-29.
- **EMA** (n.d.). *European public assessment reports (EPAR) and SmPCs*. https://www.ema.europa.eu/en/medicines. Accessed 2026-04-29.
- **MHRA emc** (n.d.). *Electronic Medicines Compendium*. https://www.medicines.org.uk/emc. Accessed 2026-04-29.
- **NIH ODS** (n.d.). *Dietary Supplement Fact Sheets*. https://ods.od.nih.gov/factsheets/list-all/. Accessed 2026-04-29.
- **NHS** (n.d.). *Food, drink and your medicines*. https://www.nhs.uk/conditions/medicines-information/. Accessed 2026-04-29.
- **van der Sijs et al.** (2006). *Overriding of drug safety alerts in computerized physician order entry*. JAMIA. https://doi.org/10.1197/jamia.M1809. Accessed 2026-04-29.
- **Ancker et al.** (2017). *Effects of workload, work complexity, and repeated alerts on alert fatigue in a clinical decision support system*. BMC Med Inform Decis Mak. https://doi.org/10.1186/s12911-017-0430-8. Accessed 2026-04-29.
- **Phansalkar et al.** (2010). *High-priority drug-drug interactions for use in electronic health records*. JAMIA. https://doi.org/10.1136/jamia.2009.000257. Accessed 2026-04-29.
- **Co et al.** (2020). *Effect of clinical decision support on appropriateness of advanced imaging use among physicians-in-training*. JAMIA. https://doi.org/10.1093/jamia/ocaa098. Accessed 2026-04-29.

### Pregnancy + lactation comparative
- **FDA** (2022). *Advice About Eating Fish*. https://www.fda.gov/food/consumers/advice-about-eating-fish. Accessed 2026-04-29.
- **CDC** (n.d.). *Listeria + Pregnancy*. https://www.cdc.gov/listeria/prevention/pregnant-women.html. Accessed 2026-04-29.
- **EFSA** (2015). *Scientific Opinion on the Safety of Caffeine*. EFSA Journal. https://doi.org/10.2903/j.efsa.2015.4102. Accessed 2026-04-29.
- **EFSA** (2012). *Scientific Opinion on the risk for public health related to the presence of mercury and methylmercury in food*. EFSA Journal. https://doi.org/10.2903/j.efsa.2012.2985. Accessed 2026-04-29.
- **NHS** (n.d.). *Foods to avoid in pregnancy*. https://www.nhs.uk/pregnancy/keeping-well/foods-to-avoid/. Accessed 2026-04-29.
- **FSANZ** (n.d.). *Food safety during pregnancy*. https://www.foodstandards.gov.au/consumer/generalissues/pregnancy. Accessed 2026-04-29.
- **MHLW Japan** (n.d.). *Mercury in Fish — Pregnancy Advisory*. https://www.mhlw.go.jp/topics/bukyoku/iyaku/syoku-anzen/suigin/. Accessed 2026-04-29.
- **NHMRC / Australian Department of Health** (n.d.). *Pregnancy Care Guidelines*. https://www.health.gov.au/resources/pregnancy-care-guidelines. Accessed 2026-04-29.
- **Health Canada** (n.d.). *Safe Food Handling for Pregnant Women*. https://www.canada.ca/en/health-canada/services/food-safety-vulnerable-populations.html. Accessed 2026-04-29.
- **WHO** (n.d.). *Maternal Health — Healthy Diet During Pregnancy*. https://www.who.int/health-topics/maternal-health. Accessed 2026-04-29.
- **CDC** (n.d.). *Vaccinations and Medications While Breastfeeding*. https://www.cdc.gov/breastfeeding/breastfeeding-special-circumstances/index.html. Accessed 2026-04-29.
- **NHS** (n.d.). *Breastfeeding and diet*. https://www.nhs.uk/conditions/baby/breastfeeding-and-bottle-feeding/breastfeeding-and-lifestyle/diet/. Accessed 2026-04-29.
