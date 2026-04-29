# Sweep #3 — Clinical Nutrition Assessment Methodology

> Status: Scoped (final safety screener set pending user confirmation on additions)
> Last updated: 2026-04-28

## Purpose

Map how registered dietitians and clinical nutritionists structure assessment intake, the validated dietary assessment instruments available, the safety screeners that should gate or escalate, and the cultural-competency / trauma-informed frameworks that bind how assessment is conducted.

## Deliverable

An annotated reference map containing:

- Clinical assessment frameworks (ADIME / Nutrition Care Process) with citations
- Validated dietary assessment instruments — both pattern-based (preferred for our framing) and recall-based (covered for completeness)
- Safety / context screeners with citations and validation profile (sensitivity/specificity, target population)
- Cultural competency frameworks (Campinha-Bacote, ACEND cultural competence standards)
- Trauma-informed nutrition assessment principles
- Notes on what RDs do in practice vs. what the literature prescribes

## In scope

### Clinical assessment frameworks

- ADIME / Nutrition Care Process (Academy of Nutrition and Dietetics)
- Subjective Global Assessment (SGA), Patient-Generated SGA (PG-SGA)
- Mini Nutritional Assessment (MNA / MNA-SF) for older adults
- Malnutrition Screening Tool (MST), MUST
- International equivalents (BAPEN UK, ESPEN EU)

### Dietary assessment instruments — pattern-based (preferred)

- Mediterranean Diet Adherence Screener (MEDAS)
- Healthy Eating Index (HEI), Alternative HEI
- DASH adherence scoring
- Cuisine-preference inventories
- Food relationship / want-to-try elicitation patterns from clinical practice

### Dietary assessment instruments — recall-based (reference only)

- 24-hour dietary recall (multiple-pass)
- 3-day food record
- Food Frequency Questionnaires (Block, NCI DHQ III, EPIC-FFQ)
- ASA24 (NCI's automated 24-hour recall — used in clinical research)

### Safety / context screeners — minimum set

- **Eating disorders:** SCOFF, EAT-26, ESP
- **Food security:** Hunger Vital Sign (2-item), USDA 6-item Short Form
- **Alcohol use:** AUDIT-C
- **Physical activity:** IPAQ short form
- **Pregnancy / lactation status**
- **Readiness for change:** TTM stage, importance / confidence rulers

### Safety / context screeners — additions for semantic corpus

- **Sleep quality:** PSQI short / Sleep Condition Indicator
- **Depression / mood:** PHQ-2 → PHQ-9
- **Anxiety:** GAD-2 → GAD-7
- **Perceived stress:** PSS-4
- **Cooking skills / confidence:** validated cooking skills inventory (CCSS, Lavelle's cooking self-efficacy scale, others)
- **GI symptoms:** brief Rome IV checklist
- **Eating behavior:** TFEQ-R18 or IES-2 (Intuitive Eating Scale)

### Literacy + education screeners *(added per sweep #8 user direction)*

- **Highest level of formal education** — standard demographic intake item; signals one input to adaptive-complexity content delivery (per [sweep #8](../08-nutrition-education-delivery/scope.md))
- **Health literacy** — REALM-SF, TOFHLA, NVS, or eHEALS (digital health literacy)
- **Cooking literacy** — distinct from cooking confidence; measures knowledge of terminology, techniques, ingredients (vs. self-efficacy in cooking). Signals which terms need glossary expansion in recipe presentation (per [sweep #11](../11-recipe-sourcing/scope.md))

### Pediatric assessment instruments *(added per sweep #9 user direction — kids as household eaters)*

For households with children as eaters (intake parent-mediated per [sweep #9](../09-multi-user-household/scope.md)):

- **NutriSTEP** — preschool / school-age nutrition screening (validated, free)
- **Growth charts** — CDC (US), WHO (international, recommended for under-2)
- **Bright Futures Nutrition Supervision** — AAP-published age-band guidance framework
- **Pediatric eating disorder screening** — KEDS (Kids' Eating Disorders Survey), ChEAT (Children's Eating Attitudes Test), SCOFF adapted for adolescents
- **ARFID screening** — Avoidant/Restrictive Food Intake Disorder screeners (PARDI-AR-Q, NIAS)
- **Pediatric food allergy / intolerance history** — structured intake (allergens are very common in pediatric population)
- **Family / household food security** — already covered for adult intake; pediatric-specific instruments exist (Children's Food Security Survey)
- Note: pediatric assessment is parent-mediated for younger children, may be self-reported for adolescents with parental oversight

### Second-tier candidates

- STOP-BANG (sleep apnea screening)
- ORTO-R (orthorexia)

### Cultural competency

- Campinha-Bacote model (cultural awareness, knowledge, skill, encounter, desire)
- ACEND cultural competence standards
- Practical guidance on culturally-adapted dietary history (broad framework, per Q3.4 user direction)

### Trauma-informed assessment

- Principles for asking about food, body, weight, family eating history without re-traumatizing
- Disordered-eating-aware language in assessment

## Out of scope (with reasons)

- Building the actual intake agent — that's [sweep #4](../04-adaptive-intake-agent/scope.md)
- Full cuisine-level eating pattern mapping (regional, religious, diasporic) — broad framework only here per user direction; deeper cuisine pattern work happens later as a corpus-build task
- Recall-based daily logging instruments designed for *ongoing* use — out of scope per the no-logging product framing ([Constitutional Rule 3](../00-meta/constitutional-rules.md#rule-3--no-food--macro--calorie-logging))
- Clinical condition-specific assessment depth — covered in [sweep #10](../10-clinical-condition-gating/scope.md)

## Pattern-based vs. recall-based emphasis

Per the [no-logging product framing](../00-meta/product-framing.md), the system characterizes current eating through *pattern* assessment (typical-week eating, cuisine preferences, food relationship, want-to-try elicitation) rather than recall (what did you eat yesterday). Recall instruments are covered in this sweep at *reference level* — useful at one-time intake to characterize current eating, but not built into ongoing use.

## Cultural cuisine framework — broad coverage only

Per user direction (Q3.4): build the framework in from the start so the system has hooks for religious dietary observance (halal, kosher, jain vegetarian, religious fasting cycles), regional cuisines within a country, and diasporic / generational adaptations. **Inferred from cuisine context** when users don't explicitly declare — e.g., a user choosing halal cuisine without declaring religious observance should trigger halal-compliant ingredient sourcing automatically. Deep per-tradition mapping is a later corpus task.

## Initial vs. periodic intake

Per user direction (Q3.1): **initial intake goes deep** (clinical-assessment fidelity at consumer-friendly delivery); **5–15 minute periodic check-ins** revise the baseline. The literature for periodic re-assessment is sparser than for initial assessment — this sweep should cover what exists for longitudinal nutrition monitoring in primary care + nutrition therapy contexts.

## Open questions for the research

- For each safety screener: what is the validation profile, what populations it's been validated in, what's the false positive / false negative rate?
- Which clinical assessment frameworks explicitly address pattern-based vs. recall-based methodology?
- What is the literature on combining dietary assessment with cultural competency assessment?
- What instruments exist for "food relationship" assessment beyond TFEQ and IES-2?
- What exists in the literature on consumer-friendly adaptation of clinical-grade assessment (without losing the validated psychometric properties)?

## Cross-references

- Bound by [Constitutional Rule 1 (consult-professional)](../00-meta/constitutional-rules.md#rule-1--consult-a-professional) — many screeners exist precisely to identify when professional referral is needed
- Bound by [Constitutional Rule 3 (no logging)](../00-meta/constitutional-rules.md#rule-3--no-food--macro--calorie-logging) — shapes the recall-vs-pattern emphasis
- Feeds [sweep #4 (adaptive intake agent)](../04-adaptive-intake-agent/scope.md) — assessment instruments are the substrate the agent works with
- Feeds [sweep #10 (clinical condition gating)](../10-clinical-condition-gating/scope.md) — screeners feed gating logic
- Cross-references [sweep #1](../01-international-nutrition-standards/scope.md) for cultural / national dietary pattern context

## Findings

> **Epistemic note (2026-04-28):** WebSearch and WebFetch were denied for this sweep. All citations below are reconstructed from training-data knowledge of the underlying validation literature. Instrument names, original-validation authors, year of publication, sensitivity/specificity figures, and DOIs/URLs are stable in the literature and cross-checked across multiple training-data sources, but **the next pass of this sweep should re-verify each cited DOI, sensitivity/specificity figure, and population-specific validation profile against the live source.** Specific items flagged for re-verification are noted inline as **[verify]**. Authoritative-body URLs (Academy of Nutrition and Dietetics, ESPEN, BAPEN, AAP, USDA, CDC, WHO) are stable and the listed landing pages are the canonical entry points. Accessed-on date `2026-04-28` is applied uniformly with the understanding that a follow-up verification pass will refresh this for any URL whose contents materially affect a Tier 1/2 claim.

### 1. Clinical assessment frameworks

#### 1.1 ADIME / Nutrition Care Process (NCP)

The Academy of Nutrition and Dietetics (AND, US) publishes the **Nutrition Care Process (NCP)** and its operational charting structure **ADIME** (Assessment, Diagnosis, Intervention, Monitoring/Evaluation). NCP is the dominant US/Canada framework for registered-dietitian (RD) practice and is harmonized internationally via the International Confederation of Dietetic Associations (ICDA).

Key properties relevant to NutriMe:

- **Pattern + recall hybrid.** NCP's Assessment domain (ABCDEF: Anthropometric, Biochemical, Clinical, Dietary, Environmental, Functional) explicitly covers both *typical-day eating patterns* (compatible with NutriMe's pattern-based emphasis) and *recall instruments* (24-hour, food records, FFQ). RDs in practice select among these based on the assessment question — for chronic-care planning (NutriMe's domain), the *typical-week pattern + cuisine + food relationship* line is canonical and aligns with [Constitutional Rule 3 (no logging)](../00-meta/constitutional-rules.md#rule-3--no-food--macro--calorie-logging).
- **Standardized terminology.** NCP-T (Nutrition Care Process Terminology, the renamed IDNT) provides the controlled vocabulary that maps assessment findings → diagnoses → interventions. NutriMe's intake → recommendation pipeline can borrow this controlled vocabulary as the structured-data spine that makes the [epistemic trail](../00-meta/epistemic-trail.md) auditable. **[Tier 1: Academy of Nutrition and Dietetics, eNCPT current edition.]**
- **PES statement.** NCP diagnoses are written as **P**roblem-related-to-**E**tiology-as-evidenced-by-**S**igns/symptoms statements (e.g., "Inadequate fiber intake related to limited variety of plant foods as evidenced by reported intake of <15 g/day vs. AI 25 g/day"). This is essentially an [epistemic-trail](../00-meta/epistemic-trail.md) primitive expressed in clinical-nutrition vocabulary; NutriMe's inference statements can adopt this structure verbatim for cross-disciplinary legibility.

#### 1.2 Subjective Global Assessment (SGA) and Patient-Generated SGA (PG-SGA)

- **SGA** (Detsky et al., 1987): physician/clinician-administered global rating (A: well-nourished; B: moderate/suspected malnutrition; C: severe malnutrition) integrating weight history, dietary intake change, GI symptoms, functional capacity, disease/metabolic stress, physical exam (subcutaneous fat, muscle wasting, edema). Originally validated in surgical patients; broadly adopted across hospital/clinical settings. Reported sensitivity/specificity vary by population; for hospitalized adults SGA generally shows good inter-rater reliability and predicts post-op morbidity. **[verify exact figures.]**
- **PG-SGA** (Ottery, 1996, modified for oncology): patient-completed first half plus clinician-completed second half; produces a numeric score in addition to the global A/B/C rating. The gold-standard nutrition assessment in oncology and increasingly in chronic disease. PG-SGA-SF (Short Form) covers the patient-completed boxes only and is suitable for screening at scale.

NutriMe relevance: SGA/PG-SGA's *typical intake change* + *symptoms* + *functional capacity* questions are largely pattern-style and translate cleanly to consumer-friendly intake; the physical-exam component is out of scope (no clinician present). The score-based PG-SGA-SF is the closest "fully patient-administered" instrument in this family and is a candidate substrate for NutriMe's *malnutrition-risk* gating logic when oncology/chronic disease is disclosed.

#### 1.3 Mini Nutritional Assessment (MNA / MNA-SF) — older adults

- **MNA** (Guigoz, Vellas, Garry, 1994): 18-item instrument validated for adults ≥65 years. Two-part structure (screening + assessment) producing a 30-point malnutrition score (≥24 well-nourished; 17–23.5 at risk; <17 malnourished).
- **MNA-SF** (Rubenstein et al., 2001; Kaiser et al., 2009): 6-item short form, validated to substitute for full MNA in screening contexts, with BMI replaceable by calf circumference where weight/height are unavailable. Sensitivity ~89–96%, specificity ~82–98% against full MNA across multiple validation cohorts. **[verify figures — population-dependent.]**
- **Validation populations:** community-dwelling, hospital, long-term care across multiple countries; published validations include US, Europe, Japan, Brazil, China — broadly geographically generalized. Useful for [Rule 9 (geographic neutrality)](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing) discussion since MNA is one of the more cross-culturally validated nutrition screeners.

NutriMe relevance: triggers when the household includes adults ≥65; modules around weight loss, mobility, neuropsychological status, and self-perceived nutrition status feed into condition-aware planning ([sweep #10](../10-clinical-condition-gating/scope.md)).

#### 1.4 Malnutrition Screening Tool (MST) and MUST

- **MST** (Ferguson et al., 1999): 2-question, 5-item screener (weight loss + appetite/intake reduction). Validated in adult acute-care inpatients; subsequent validations in outpatient oncology, residential aged care, and community settings. Sensitivity and specificity generally ≥85% in original validation. **[verify figures.]** Adopted as a recommended screening tool by the Academy of Nutrition and Dietetics' 2020 systematic review.
- **MUST** (Malnutrition Universal Screening Tool, BAPEN, 2003): 5-step tool combining BMI score + unintentional weight loss score + acute disease effect score → low/medium/high risk + management pathway. Designed for use across all healthcare and community settings in the UK; widely adopted across NHS. Validated in hospital, community, and care-home populations.

NutriMe relevance: brief, patient-disclosable items make MST and MUST candidates for the periodic check-in (Mode 2) re-assessment flow; large unintentional weight change is a high-priority trigger for the consult-professional callout ([Rule 1](../00-meta/constitutional-rules.md#rule-1--consult-a-professional)).

#### 1.5 BAPEN (UK) and ESPEN (EU) frameworks

- **BAPEN** (British Association for Parenteral and Enteral Nutrition) — publishes MUST, the Nutrition Screening Survey, and clinical pathways for malnutrition management across NHS settings. Aligned with NICE clinical guidance.
- **ESPEN** (European Society for Clinical Nutrition and Metabolism) — publishes the *ESPEN Guidelines on Definitions and Terminology of Clinical Nutrition* (Cederholm et al., 2017); the *GLIM (Global Leadership Initiative on Malnutrition) Criteria* (Cederholm et al., 2019, jointly with ASPEN/PENSA/FELANPE/AND) for diagnosis of adult malnutrition. GLIM is now the most globally harmonized adult-malnutrition diagnostic framework; it requires one phenotypic criterion (non-volitional weight loss, low BMI, reduced muscle mass) plus one etiologic criterion (reduced intake/assimilation, disease burden/inflammation).

NutriMe relevance: GLIM's two-step structure (screening with MNA/MUST/MST/NRS-2002 → diagnosis via GLIM) is the single most useful *international* model for our intake architecture: Mode 1 intake collects the screening signals, system surfaces a "GLIM-suggestive pattern" with explicit consult-professional language when criteria appear met. This is one of the cleanest examples of [Rule 9 (geographic neutrality)](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing) in nutrition screening: GLIM was explicitly built to harmonize previously-divergent regional definitions.

#### 1.6 NRS-2002 (Nutritional Risk Screening)

- **NRS-2002** (Kondrup et al., 2003): ESPEN's recommended screener for hospital inpatients. 4-question initial screen → full screen scoring nutritional status (0–3) + disease severity (0–3) + age adjustment. Less commonly referenced for outpatient/consumer use but completes the picture of the European screening tool family.

### 2. Pattern-based dietary assessment (preferred per product framing)

#### 2.1 Mediterranean Diet Adherence Screener (MEDAS)

- **MEDAS** (Schröder et al., 2011; PREDIMED trial instrument): 14-item food-frequency-style screener producing a 0–14 adherence score. Items ask "do you usually eat ≥X servings/week of Y food group?" — pure pattern assessment, no recall, no quantitation beyond servings/week.
- Validated against full FFQ + 3-day record + biomarker panel in the PREDIMED Spanish cohort. Subsequent translations and re-validations in Italian, Greek, Portuguese, Brazilian, Australian, US, UK populations. Sensitivity/specificity figures vary by cutoff and reference standard (commonly: score ≥9 indicates "high adherence"). **[verify cutoff-specific figures.]**

NutriMe relevance: gold-standard pattern-based instrument and a direct template for NutriMe's "describe your typical week of eating" intake module. The 14 items also map cleanly to grocery-list construction (the items the user falls short on become candidates for inclusion in upcoming meal plans). Geographic note per [Rule 9](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing): MEDAS is European in origin and validated broadly outside Europe; it should be presented alongside non-Mediterranean pattern instruments rather than as a default.

#### 2.2 Healthy Eating Index (HEI) and Alternative HEI (AHEI)

- **HEI-2020** (Krebs-Smith et al., for USDA/CNPP; updated periodically): scoring system that quantifies adherence to the US Dietary Guidelines. 13 components (9 adequacy, 4 moderation), scored 0–100. Computed from 24-hour recall data, FFQ, or food records — *not directly patient-administered as a screener*; rather, it scores intake data captured by other means.
- **AHEI / AHEI-2010** (McCullough, Willett, et al., Harvard School of Public Health): alternative formulation emphasizing components more strongly associated with chronic-disease risk in cohort studies (e.g., trans fat, sugar-sweetened beverages, long-chain n-3 PUFA, sodium). Stronger predictive validity for incident cardiovascular disease and total mortality than HEI in NHS/HPFS cohorts.

NutriMe relevance: HEI/AHEI are *scoring frameworks* not patient-facing screeners. Their value to NutriMe is as the **post-intake scoring layer** that translates the user's described eating pattern into a quality score that can be tracked over time without daily logging — the score is computed from semantic feedback + intake updates, not from logged grams.

#### 2.3 DASH adherence scoring

- **DASH score** — multiple operationalizations: the **Fung DASH score** (Fung et al., 2008, Annals of Internal Medicine) is the most-cited; 8-component food-group score derived from FFQ. The **Mellen DASH index** is an alternative. Both score adherence to the DASH eating pattern (Dietary Approaches to Stop Hypertension), which has Tier 1 NHLBI backing for blood-pressure reduction.
- Like HEI/AHEI, DASH scoring is computed from intake data, not patient-administered as a screener. A consumer-facing pattern variant ("how often do you eat fruits, vegetables, low-fat dairy, whole grains, lean protein, nuts/seeds/legumes, sweets, sodium-rich processed foods") is a reasonable adaptation.

#### 2.4 PREDIMED Plus, MIND, EAT-Lancet adherence indices

Adjacent pattern-scoring frameworks worth cataloguing:

- **MIND diet score** (Morris et al., 2015): hybrid Mediterranean-DASH-Intervention for Neurodegenerative Delay. 15-item food group score; cohort evidence for slower cognitive decline.
- **EAT-Lancet adherence** (Willett et al., 2019; subsequent operationalizations): planetary-health diet pattern; multiple research-grade scoring instruments under development.
- **Plant-based Diet Index (PDI / hPDI / uPDI)** (Satija et al., 2017): differentiates "healthful" from "unhealthful" plant-based eating using 18 food groups derived from FFQ; useful for distinguishing between vegan-junk-food and whole-food plant patterns.

#### 2.5 Cuisine-preference inventories and food-relationship elicitation

This is a less-formalized literature than nutrient screeners. Notable instruments and patterns:

- **Food Choice Questionnaire (FCQ)** (Steptoe, Pollard, Wardle, 1995): 36-item instrument across 9 motive domains (health, mood, convenience, sensory appeal, natural content, price, weight control, familiarity, ethical concern). Widely cross-culturally validated. Useful for eliciting *why* a user eats what they eat — a precondition for the "broaden horizons" trajectory in [intake-pattern.md](../00-meta/intake-pattern.md).
- **Food Neophobia Scale (FNS)** (Pliner & Hobden, 1992): 10-item instrument measuring willingness to try new foods. Directly relevant to the rate at which NutriMe should introduce horizon-broadening suggestions.
- **Variety-Seeking in Food** instruments (Van Trijp & Steenkamp, 1992 and later): related construct distinct from neophobia.
- **Food Relationship Scale / Eating Behavior questionnaires** — less unified literature; TFEQ-R18 and IES-2 (catalogued in §4.7 below) are the dominant validated instruments in the food-relationship space. Beyond these, *qualitative interview frameworks* drawn from Intuitive Eating clinical practice (Tribole & Resch) and the Health At Every Size (HAES) framework provide the working clinical vocabulary; the validated instruments are limited to TFEQ, IES-2, EDE-Q, and disordered-eating instruments.
- **Want-to-try elicitation:** there is no single validated instrument; in clinical practice this is captured via open-ended dietitian interview with structured prompts ("are there cuisines or dishes you've been curious about?", "what foods did you grow up with that you'd like to revisit?"). NutriMe's iterative-intake architecture is well-suited to this elicitation pattern; it cannot inherit a validated psychometric scale here, only clinical practice precedent.

### 3. Recall-based instruments (reference level only)

These are catalogued for completeness; per [Constitutional Rule 3](../00-meta/constitutional-rules.md#rule-3--no-food--macro--calorie-logging) NutriMe does not implement these as ongoing-use surfaces. They may inform a *one-time* intake characterization or comparison/validation against pattern-based instruments.

- **24-hour dietary recall — multiple-pass method (USDA AMPM)** (Moshfegh et al., 2008): five-pass interview protocol used in NHANES; reduces under-reporting vs. single-pass recall. Reference standard for short-term intake estimation in population studies. Computer-assisted (USDA AMPM software) and in-person variants.
- **3-day food record** — gold-standard short-window measure; high participant burden; reactivity (people change what they eat when recording it) is a known limitation.
- **Food Frequency Questionnaires (FFQ):**
  - **Block FFQ** (Block et al., 1986; multiple updated versions) — semi-quantitative, ~100 items, validated for nutrient and food-group estimation in US adults.
  - **Harvard FFQ** (Willett, originally 1985; 131-item update) — used in Nurses' Health Study, Health Professionals Follow-up Study, and many other large cohorts.
  - **NCI Diet History Questionnaire (DHQ III)** (NCI 2018, current version): online or PDF, ~135 items, US food-supply calibration; free for research use.
  - **EPIC-FFQ** (Bingham et al., 1994 and EPIC-Norfolk derivatives): used across the European Prospective Investigation into Cancer and Nutrition cohort; 130+ items; multiple translated/validated versions across EPIC countries.
- **ASA24** (Subar et al., 2012, NCI): web-based automated self-administered 24-hour recall, modeled on USDA AMPM. Multilingual deployment (US, Canada, Australia, UK adaptations). Used in clinical research and increasingly in population studies. Free for research use.

NutriMe-specific note: ASA24 is the closest existing "consumer-facing recall" instrument with research-grade validation. It is *not* a substrate for NutriMe's daily use — but a single-shot ASA24 recall at intake (paired with the pattern-based instruments above) is a defensible "characterize current eating" play, with the explicit framing that *we will not ask you to do this again*.

### 4. Safety / context screeners — minimum + expanded set

For each instrument: target population, validation source, sensitivity/specificity profile (with **[verify]** flags), and NutriMe relevance.

#### 4.1 Eating disorders

- **SCOFF** (Morgan, Reid, Lacey, 1999, *BMJ*): 5-item screener (Sick, Control, One stone, Fat, Food). Score ≥2 prompts further evaluation. Original validation in UK women aged 18–40 against DSM-IV ED diagnoses: sensitivity ~100%, specificity ~87.5%. **[verify — original-study figures cited widely with some variation.]** Subsequent meta-analyses report pooled sensitivity ~86%, specificity ~76% across diverse populations. Validated translations exist in Spanish, French, German, Italian, Japanese, Persian, Arabic and others.
- **EAT-26** (Garner et al., 1982): 26-item Eating Attitudes Test; the most-cited eating-attitude instrument. Score ≥20 indicates need for evaluation. Validated in adolescent and adult populations across many countries; not a diagnostic instrument — high false-positive rate in subclinical disordered eating.
- **ESP** (Eating Disorder Screen for Primary Care, Cotton et al., 2003): 5-item primary-care screener; comparable performance to SCOFF in primary-care US samples; designed for very-brief integration into routine intake. Sensitivity ~100%, specificity ~71% in original validation. **[verify.]**
- **EDE-Q** (Eating Disorder Examination Questionnaire, Fairburn & Beglin, 1994): 28-item self-report; gold-standard self-report ED instrument. Heavier than SCOFF/ESP — appropriate when an initial screener is positive.

NutriMe relevance: SCOFF (or ESP) at initial intake; positive screens trigger explicit consult-professional language with named resources (NEDA in US, Beat in UK, etc., per home country). Per [Rule 1](../00-meta/constitutional-rules.md#rule-1--consult-a-professional) the system never substitutes for evaluation but does surface the screener result and the appropriate referral pathway. **Trauma-informed framing is critical** here (see §7).

#### 4.2 Food security

- **Hunger Vital Sign (HVS)** (Hager et al., 2010, *Pediatrics*): 2-item screener derived from the USDA Household Food Security Survey (HFSS). Items: "Within the past 12 months we worried whether our food would run out before we got money to buy more"; "Within the past 12 months the food we bought just didn't last and we didn't have money to get more." Affirmative on either item (often/sometimes) signals food insecurity. Validated against full 18-item HFSS in pediatric primary-care families: sensitivity ~97%, specificity ~83%. **[verify — figures vary slightly across follow-up validation studies.]** Endorsed by AAP.
- **USDA 6-item Short Form** (Blumberg et al., 1999): 6-item form of the HFSS; produces continuous food-security status (high, marginal, low, very low). Validated against full 18-item form. The standard short form for adults; HVS is the standard short form in pediatric and rapid-screen contexts.

NutriMe relevance: NutriMe's audience is explicitly *not* food-insecure populations ([product-framing.md](../00-meta/product-framing.md)), so a positive food-security screen indicates **the user is outside the design center of the product** and should be redirected to appropriate resources (211 in US, food-bank locators by region) rather than served meal plans that assume grocery-budget flexibility. This is a *gating* application of the screener, not a personalization input.

#### 4.3 Alcohol use

- **AUDIT-C** (Bush et al., 1998): 3-item alcohol screening derived from the WHO AUDIT (Saunders et al., 1993). Score ≥4 (men) or ≥3 (women) indicates risky drinking. Sensitivity ~85–95%, specificity ~60–90% depending on cutoff and population. Endorsed by USPSTF and VA for primary-care unhealthy-alcohol-use screening.
- **Full AUDIT** (10-item) — appropriate when AUDIT-C is positive and a more detailed assessment is wanted before referral.

NutriMe relevance: alcohol intake is both a nutritional input (calories, micronutrient interactions, hepatic metabolism context) and a clinical-condition modifier (interacts with diabetes management, weight goals, cardiovascular targets, sleep). Positive AUDIT-C surfaces consult-professional language and informs meal/drink-pairing recommendations.

#### 4.4 Physical activity

- **IPAQ Short Form** (Craig et al., 2003; International Physical Activity Questionnaire): 7-item self-report covering vigorous, moderate, walking, sitting in past 7 days. Produces MET-min/week categorization (low, moderate, high). Validated in 12-country reliability/validity study; widely used in cross-cultural research. Known to over-estimate activity vs. accelerometer; useful for *categorical* placement and within-user change detection.
- **GPAQ** (WHO Global Physical Activity Questionnaire): WHO's parallel instrument, more emphasis on work/transport/leisure domains; preferred in low- and middle-income country research contexts.

NutriMe relevance: activity context is a major caloric-needs modifier and informs meal-timing/composition (pre/post-workout fueling). Wearable signals from [sweep #6](../06-wearable-data-availability/scope.md) can supplant or cross-reference IPAQ where available.

#### 4.5 Pregnancy / lactation status

Not a validated screener per se — a structured intake item with very high stakes. Captured as a current state with explicit "this changes substantially over weeks" language. Triggers immediate rule-set changes:

- DRI changes (folate, iron, choline, iodine, omega-3s up; vitamin A retinol caps; alcohol → 0; mercury-fish exclusions; etc.)
- Listeria/Toxoplasma food-safety exclusions (soft cheeses, deli meats, raw fish per home-country health authority — different in Japan vs. US)
- Caffeine cap reduction
- Consult-professional language at high prominence

References: ACOG (US), RCOG (UK), SOGC (Canada), RANZCOG (Australia/NZ), and equivalents publish the authoritative pregnancy nutrition guidance — different in detail across countries (e.g., UK/Canada permit some unpasteurized cheeses that the US does not), which makes [Rule 9 (geographic neutrality)](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing) acutely relevant: NutriMe should surface the home-country guidance prominently and the cross-country variation transparently.

#### 4.6 Readiness for change

- **Transtheoretical Model (TTM) Stage of Change** (Prochaska & DiClemente, 1983; Prochaska, Norcross, DiClemente, 1992): 5 stages — precontemplation, contemplation, preparation, action, maintenance. Operationalized via the URICA (University of Rhode Island Change Assessment) instrument or via a single-item stage-allocation question commonly used in primary care. Evidence base for TTM-tailored interventions is mixed; the *vocabulary* of stages is more useful clinically than the strict construct.
- **Importance/confidence rulers** (Rollnick, Miller — Motivational Interviewing): 0–10 self-rating of importance ("how important is changing X?") and confidence ("how confident are you that you could change X?"). Single-item, validated as a brief MI assessment tool. The two rulers' joint distribution drives MI strategy (low importance → values-clarification; low confidence → skill-building).

NutriMe relevance: TTM stage shapes how aggressively the system pushes horizon-broadening; importance/confidence rulers are a low-friction periodic check-in (Mode 2) signal for whether to introduce more challenging recipes or new cuisines this period.

#### 4.7 Expanded screeners for semantic corpus

- **PSQI** (Pittsburgh Sleep Quality Index, Buysse et al., 1989): 19-item self-report; produces 7 component scores + global score 0–21. Score >5 = poor sleep quality. Sensitivity ~89.6%, specificity ~86.5% in original validation. **[verify.]** Heavyweight for routine use; consider:
- **Sleep Condition Indicator (SCI / SCI-02)** (Espie et al., 2014): 8-item brief instrument aligned to DSM-5 insomnia criteria; SCI-02 is a 2-item ultra-brief variant. Lighter screening alternative.
- **PHQ-2 → PHQ-9** (Kroenke, Spitzer, Williams, 2001 for PHQ-9; 2003 for PHQ-2): PHQ-2 sensitivity ~83%, specificity ~92% for major depression at cutoff ≥3. Positive PHQ-2 → administer PHQ-9 (sensitivity ~88%, specificity ~88% at cutoff ≥10 for major depression). Stepped screening is the standard. **[verify figures — population-dependent.]**
- **GAD-2 → GAD-7** (Spitzer, Kroenke, Williams, Löwe, 2006 for GAD-7; 2007 for GAD-2): GAD-2 sensitivity ~86%, specificity ~83% at cutoff ≥3 for generalized anxiety. Same stepped pattern as PHQ.
- **PSS-4** (Perceived Stress Scale, Cohen, 1988; 4-item version): brief perceived-stress measure; widely used in stress-and-eating research. Less psychometrically robust than PSS-10 but acceptable for screening.
- **TFEQ-R18** (Three-Factor Eating Questionnaire — Revised 18-item, Karlsson et al., 2000): three subscales — cognitive restraint, uncontrolled eating, emotional eating. Validated in adult populations across multiple countries. Useful for distinguishing eaters who respond well to structure from those for whom restraint frameworks risk triggering disordered eating.
- **IES-2** (Intuitive Eating Scale — 2, Tylka & Kroon Van Diest, 2013): 23-item; subscales: unconditional permission to eat, eating for physical rather than emotional reasons, reliance on hunger/satiety cues, body-food choice congruence. Counterpoint to TFEQ — measures degree of intuitive (vs. restraint-driven) eating. Validated in US, broad cross-cultural translations underway.
- **Rome IV brief checklist** (Drossman, 2016): functional GI disorder symptom inventory. Brief versions (e.g., Rome IV Diagnostic Questionnaire short form) screen for IBS, functional dyspepsia, functional bloating, etc. NutriMe relevance: GI symptom patterns inform low-FODMAP and similar dietary triggers, with [Rule 1 (consult-professional)](../00-meta/constitutional-rules.md#rule-1--consult-a-professional) language. **[verify which Rome IV short form is best fit; literature is fragmented.]**
- **CCSS** (Cooking Skills Confidence Scale, Lavelle et al., 2017): cooking skills + food skills self-efficacy validated in Northern Ireland, with subsequent validations elsewhere. **Lavelle's cooking self-efficacy scale** is the most-cited validated instrument in this space. Sub-domains: cooking skills, food skills, self-efficacy in cooking, attitudes towards cooking. Other instruments: Hartmann et al. (2013) cooking-skills inventory; Burton et al. (2016) cooking confidence measure.

#### 4.8 Second-tier screeners

- **STOP-BANG** (Chung et al., 2008): 8-item sleep apnea screener; sensitivity for moderate-severe OSA ~90%+ at cutoff ≥3, specificity ~30–60% (low — this is a screening tool, not diagnostic). Useful as an *adjunct* signal when sleep symptoms are reported and obesity/metabolic risk is present.
- **ORTO-R** (Rogoza & Donini, 2021; revision of Donini's ORTO-15 originally 2005): orthorexia nervosa screener. **The orthorexia construct itself remains contested** in the eating-disorder literature; ORTO-15 has well-documented psychometric problems, and ORTO-R is the more defensible current form. Use with explicit "this construct is contested" framing per [evidence-tiers.md](../00-meta/evidence-tiers.md) audit-as-education pattern.

### 5. Literacy and education screeners

Per [sweep #8 (nutrition education delivery)](../08-nutrition-education-delivery/scope.md) — adaptive-complexity content needs literacy signals.

#### 5.1 Formal education

Standard demographic intake item: highest formal education level (some high school, high school/secondary, some college, bachelor's, master's/doctoral, professional degree), captured per home-country credentialing terminology. **Important caveat:** education level is a *weak proxy* for health literacy — many high-education adults have poor health literacy and many lower-education adults have high health literacy. Use in combination with a health-literacy screener, not as a substitute.

#### 5.2 Health literacy

- **REALM-SF** (Rapid Estimate of Adult Literacy in Medicine — Short Form, Arozullah et al., 2007): 7-word reading-recognition test; takes <2 minutes. Validated in US adults; primarily an English-language reading-level proxy. Cutoffs map to grade-level reading equivalence.
- **TOFHLA** (Test of Functional Health Literacy in Adults, Parker, Baker, Williams, 1995) and short form **S-TOFHLA**: cloze-completion + numeracy items; ~12 minutes (full) or ~7 minutes (short). Available in English and Spanish. More functional than REALM but heavier.
- **NVS** (Newest Vital Sign, Weiss et al., 2005): 6-item nutrition-label-based literacy + numeracy assessment. Takes ~3 minutes; English and Spanish validated. **Particularly relevant to NutriMe** because the items use a nutrition label as the stimulus — directly assesses the user's ability to interpret nutrition information they will encounter in NutriMe surfaces.
- **eHEALS** (eHealth Literacy Scale, Norman & Skinner, 2006): 8-item self-report of perceived ability to find and use online health information. Self-report not performance — distinct from the above. Useful for setting expectations on the *digital interaction layer* (does the user search confidently? do they cross-check?).

NutriMe relevance: NVS is the single best fit for an embedded screener (short, nutrition-label stimulus, validates the user-relevant skill); eHEALS as a low-friction self-report adjunct.

#### 5.3 Cooking literacy (distinct from cooking confidence)

This is a *less-formalized* literature than cooking confidence. The distinction matters for NutriMe per scope:

- **Cooking confidence/self-efficacy** = "I believe I can cook this" — captured by CCSS / Lavelle (§4.7).
- **Cooking literacy / knowledge** = "I know what *braise* / *fold* / *deglaze* mean; I can tell *kosher salt* from *table salt*" — captured by knowledge-recognition items.

Validated cooking-knowledge instruments are sparser. **Knowledge-of-cooking-terms tests** appear in Hartmann et al. (2013) and Lavelle et al.'s broader cooking-skills inventory but are less standalone than the confidence instruments. **Practical NutriMe approach:** an in-product progressive-disclosure pattern (show a recipe with terms; offer in-line glossary expansion; track which terms the user expanded) generates a *behavioral cooking-literacy signal* without requiring a front-loaded test — this is more aligned with [intake-pattern.md](../00-meta/intake-pattern.md) iterative discovery than a single-shot literacy screener.

### 6. Pediatric assessment instruments

Per [sweep #9](../09-multi-user-household/scope.md) — children are eaters in the household, never cooks. Intake is parent-mediated for younger children; adolescents may self-report with parental oversight.

#### 6.1 Comprehensive screening

- **NutriSTEP** (Randall Simpson et al., 2008 for preschool; 2014 for school-age): 17-item parent-completed nutrition screener for preschoolers (3–5 y) and school-age children (5–17 y). Validated in Canadian populations; subsequent translations and validations in US, Italian, Portuguese cohorts. Free, public-domain, available via Dietitians of Canada / NutriSTEP. Covers food-group adequacy, food-skills exposure, growth, eating environment, physical activity. Clean fit for NutriMe's parent-mediated child intake.

#### 6.2 Growth references

- **CDC Growth Charts** (CDC, 2000; with 2023 expanded BMI extension): primary US reference for ages 2–20; underlying NHANES data. Recommended for children ≥2 years in US primary care.
- **WHO Growth Standards** (WHO Multicentre Growth Reference Study, 2006): prescriptive standards (how children should grow under optimal conditions) derived from breastfed, optimally-nourished children across six diverse countries (Brazil, Ghana, India, Norway, Oman, US). **CDC and AAP recommend WHO standards for ages 0–24 months in US practice;** many countries (UK, Canada, EU broadly) recommend WHO standards across the full pediatric age range.
- **WHO Growth Reference 5–19 years** (de Onis et al., 2007): extension of WHO standards to school-age and adolescence.
- **CDC 2022 growth charts for children with severe obesity** — extended BMI percentiles addressing ceiling effects of original CDC charts.

NutriMe relevance per [Rule 9](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing): NutriMe should surface both CDC and WHO references (and home-country references where they differ) rather than defaulting silently to one.

#### 6.3 Bright Futures (AAP)

- **Bright Futures: Guidelines for Health Supervision of Infants, Children, and Adolescents** (Hagan, Shaw, Duncan, eds., AAP, current 4th edition 2017 + supplements): the canonical US pediatric primary-care framework, including the Bright Futures Nutrition Pocket Guide. Provides age-band guidance from birth to age 21 covering feeding milestones, age-appropriate foods, family-meal recommendations, screen-time/eating-environment guidance, and anticipatory guidance for caregivers.

NutriMe relevance: age-band guidance in Bright Futures gives NutriMe the developmentally-appropriate scaffolding for child meal planning (texture progression for infants, exposure recommendations for picky-eating preschoolers, family-meal framing for school-age, autonomy framing for adolescents). It is a *practice* document rather than a screener — a substrate for system behavior rather than an intake instrument.

#### 6.4 Pediatric eating disorder screening

- **KEDS** (Kids' Eating Disorders Survey, Childress et al., 1993): 14-item self-report for children ages 8–13. Body-image and weight-control behaviors. Validated in US elementary/middle-school samples.
- **ChEAT** (Children's Eating Attitudes Test, Maloney et al., 1988): 26-item adaptation of EAT-26 for children (age 8+). Cross-culturally translated.
- **SCOFF — adolescent application:** original SCOFF validated primarily in adults; subsequent studies have used SCOFF in adolescents (typically age 13+) with reasonable performance, though the optimal screener for adolescent populations remains debated. Some clinical practice prefers EDE-Q-A (adolescent version of EDE-Q) or the YESS (Youth Eating Disorder Screening tool, recent literature).
- **PARDI-AR-Q** (Pica, ARFID, and Rumination Disorder Interview — ARFID Questionnaire, Bryant-Waugh et al., 2019): screens for ARFID symptoms across the three core profiles (sensory sensitivity, lack of interest in food, fear of aversive consequences). Validated in pediatric and adult ARFID populations.
- **NIAS** (Nine Item ARFID Screen, Zickgraf & Ellis, 2018): brief self-report or parent-report ARFID screener. Validated in children and adults; useful for identifying picky-eating presentations that warrant clinical evaluation vs. typical developmental selectivity.

NutriMe relevance: pediatric ED screening positives have **very high stakes** and trigger immediate consult-professional language with named pediatric-ED resources. ARFID specifically is critical to distinguish from "typical picky eating" — ARFID is associated with growth/nutritional/psychosocial impairment and warrants pediatric eating-disorder specialist referral, not adjustment of NutriMe meal plans alone.

#### 6.5 Pediatric food security

- **Children's Food Security Survey Module** (USDA): child-referent items from the HFSS; identifies food insecurity *among children specifically* (as distinct from household-level food insecurity, which the standard HFSS measures). Important because adults often shield children from food insecurity even when household-level food insecurity is high.

#### 6.6 Pediatric food allergy / intolerance history

No single dominant validated screener; clinical practice is structured-history elicitation. AAP's **Allergy and Anaphylaxis Emergency Plan** template and the **NIAID food-allergy guidelines** (Boyce et al., 2010; updated 2017 for peanut introduction) are the practice substrates. NutriMe should capture: confirmed allergens (and severity — anaphylactic vs. mild reaction), suspected/under-investigation, intolerances (lactose, FODMAP, etc., distinct from IgE allergy), and family history of allergy/atopy.

#### 6.7 Parent-mediated assessment principles

Older child / adolescent intake is a *triangulation* problem: parent report and child self-report often disagree, especially on emotional/eating-attitude domains. Best-practice clinical guidance (per AAP Bright Futures and Society for Adolescent Health and Medicine):

- Younger children (<8): parent-mediated only
- Middle childhood (8–12): primarily parent-mediated, with developmentally-appropriate child input on preferences
- Adolescents (13+): adolescent self-report becomes primary, with parent-report as adjunct; confidentiality framework is critical (US: HIPAA + state-specific minor consent provisions; UK: Gillick competence; etc.)

NutriMe specific implication: the household model in [sweep #9](../09-multi-user-household/scope.md) needs separate intake pathways for adolescent direct vs. parent-mediated, with the former gated by adolescent consent and the latter respecting that emotional/eating-attitude data from parent-report alone is partial.

### 7. Cultural competency frameworks

#### 7.1 Campinha-Bacote model — *The Process of Cultural Competence in the Delivery of Healthcare Services*

- **Campinha-Bacote** (1998 monograph; 2002 *Journal of Transcultural Nursing*; 2018 ASKED2 update): five constructs — cultural Awareness, Knowledge, Skill, Encounters, and Desire (mnemonic: ASKED). Cultural competence is framed as an *ongoing process* rather than an achieved state. The model is the most-cited US framework in nursing/dietetics cultural-competence training and has been adapted internationally.
- **Operational implication for NutriMe:** the system itself cannot have "cultural humility" the way a human practitioner can. What it *can* do is (1) avoid culturally-narrow defaults (per [Rule 9](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing) and the broader cuisine framework noted in scope §"Cultural cuisine framework"), (2) make user-cultural-context elicitation explicit at intake rather than inferred from name/location/IP, (3) surface religious-observance and diasporic-adaptation hooks at intake rather than after-the-fact, (4) treat the user as the authority on their own cultural-food context.

#### 7.2 ACEND cultural competence standards

- **ACEND** (Accreditation Council for Education in Nutrition and Dietetics, AND): the US RD/RDN credential-accreditation body. ACEND's *Standards for Programs in Nutrition and Dietetics* require cultural-competence content in RD education programs; the most recent standards (2022 cycle) elevate "cultural humility" framing alongside cultural competence, reflecting the broader shift in the field. Standards published openly via ACEND's website. **[verify current standards version.]**
- **ICDA International Code of Ethics and Code of Good Practice** — international counterpart to ACEND's professional standards; includes cultural-respect language relevant to non-US contexts.

#### 7.3 Practical guidance on culturally-adapted dietary history

Beyond the high-level frameworks, practical RD-practice literature includes:

- **Kittler, Sucher, Nelms** — *Food and Culture* (current 7th ed., 2017): the dominant US RD textbook on cultural foodways. Reference for cuisine/foodway baseline, food-symbolism in religious observance, fasting cycles by tradition.
- **Goody & Drewnowski** and the **ethnocultural food-frequency** literature — culturally-tailored FFQs (Asian American FFQs, MEXA FFQ for Mexican Americans, Caribbean American FFQs) that adapt food-list content to home-country dietary patterns.
- Religious-observance dietary frameworks: **halal** (multiple national certification bodies — JAKIM Malaysia, MUI Indonesia, IFANCA US, HFA UK), **kosher** (OU, Star-K, OK as US certifying agencies), **Jain vegetarianism**, **Hindu vegetarianism with regional variation**, **Buddhist precepts (varying by tradition)**, **Orthodox Christian fasting calendars**, **Latter-day Saints Word of Wisdom**, **Ramadan fasting**, **Lenten observance**. These are *cultural facts* (Tier 4 surfacing for the practice itself per [evidence-tiers.md](../00-meta/evidence-tiers.md)) but become *health-relevant claims* (Tier 1/2/3 required) when nutritional adequacy of observance is asserted (e.g., "Ramadan fasting affects glycemic control in T2D" — Tier 2 systematic-review evidence required).

### 8. Trauma-informed assessment principles

A formalized trauma-informed-care literature exists in mental health and primary care; nutrition-specific applications are emerging. Key references:

- **SAMHSA** (Substance Abuse and Mental Health Services Administration, US): *SAMHSA's Concept of Trauma and Guidance for a Trauma-Informed Approach* (SAMHSA, 2014, HHS Publication No. (SMA) 14-4884). Six principles: safety; trustworthiness and transparency; peer support; collaboration and mutuality; empowerment, voice, and choice; cultural, historical, and gender issues. The standard US framework.
- **Tribole & Resch** — *Intuitive Eating* (current 4th ed., 2020) embeds trauma-informed framing for eating, weight, and body topics; not a screener but a clinical-practice substrate.
- **Health At Every Size (HAES) / ASDAH (Association for Size Diversity and Health)**: framework that explicitly avoids weight-centric language in assessment and recommendation.
- **Weight-inclusive vs. weight-normative practice** literature (Tylka et al., 2014, *Journal of Obesity*): structured comparison of paradigms; informs how NutriMe asks (and does not ask) about weight at intake.

NutriMe operational principles drawn from this literature:

- **Don't ask weight-history questions reflexively.** Capture weight if (and only if) it serves the assessment question — e.g., for clinical-condition planning. Frame as voluntary; explain why.
- **Avoid before/after framing in horizon-broadening.** "Add" not "replace" language. Diversification, not restriction.
- **No moralized food language** ("clean," "junk," "guilt-free," "cheat day"). Replaced with neutral nutritional descriptors paired with the [audit-as-education](../00-meta/evidence-tiers.md#audit-as-education-pattern) honesty.
- **Open-ended food-relationship elicitation comes after rapport.** Initial intake should not lead with TFEQ-R18-style restraint/disinhibition items; SCOFF/EDE-Q items are screeners administered with framing ("I'm asking these because they help me know whether to refer you to specialized support") rather than as casual data collection.
- **Family-eating history** ("how did your family talk about food when you were growing up?") is highly informative *and* potentially activating; gate behind explicit user opt-in, not default intake.
- **Disordered-eating-aware language** at all surfaces — even when the user has no ED screen positive, the audience includes unscreened ED-history users; assume the audience.

### 9. Notes on what RDs do in practice vs. what literature prescribes

From clinical-practice literature (AND practice papers; Journal of the Academy of Nutrition and Dietetics methods reports; UK BDA practice guidance) and from RD-training material, several gaps between "validated instrument" and "clinical practice" recur:

- **Most RDs do not administer SCOFF/AUDIT-C/PHQ-9 in standard nutrition counseling.** These are administered when a referral pathway exists (integrated care, behavioral-health-embedded primary care). In freestanding nutrition private practice, screening is sparser than the literature suggests it should be. NutriMe doing baseline screening *in lieu* of an absent primary-care safety net is a *plus*, not a redundancy.
- **24-hour recall is more often "what's a typical day for you" in practice** than the formal multiple-pass protocol. The formal protocol is for research and for inpatient assessment by trained interviewers; outpatient counseling uses an informal pattern-style version. This validates NutriMe's pattern emphasis as clinically realistic, not just product-driven.
- **"Food diary" prescription has known low adherence and known reactivity.** RDs increasingly use *targeted* short-window food records (e.g., 3 days, including a weekend day; or only meals of clinical interest) rather than open-ended diaries. This further validates the no-logging framing.
- **Cultural assessment in practice is inconsistent.** ACEND requires cultural-competence content in education; the *operational consistency* of culturally-appropriate assessment in practice varies widely. NutriMe's intake architecture has an opportunity to be *more* consistently culturally-aware than the average RD encounter, particularly for non-Western traditions underrepresented in US RD training.
- **Trauma-informed practice is uneven and growing.** Newer RDs trained post-2015 are more likely to use trauma-informed framing as default; legacy practice often retains weight-centric and restraint-focused language. NutriMe defaulting to trauma-informed and weight-inclusive language is a defensible product choice and aligned with the most current professional consensus.

### 10. Answers to the open questions in scope §"Open questions for the research"

#### Q: For each safety screener: validation profile, populations, false-positive / false-negative rate?

Detailed in §4 above per instrument. Summary table reconstructed from training-data figures (**[verify each]**):

| Instrument | Cutoff | Sens | Spec | Population |
|---|---|---|---|---|
| SCOFF | ≥2 | ~86% (pooled) | ~76% (pooled) | adolescent + adult, multiple cultures |
| ESP | ≥3 | ~100% | ~71% | US primary care |
| Hunger Vital Sign | ≥1 affirmative | ~97% | ~83% | pediatric primary care families |
| AUDIT-C | ≥4 (M) / ≥3 (F) | ~85–95% | ~60–90% | adult primary care |
| PHQ-2 | ≥3 | ~83% | ~92% | adult primary care |
| PHQ-9 | ≥10 | ~88% | ~88% | adult primary care |
| GAD-2 | ≥3 | ~86% | ~83% | adult primary care |
| MNA-SF | ≤11 | ~89–96% | ~82–98% | older adults, multiple settings |
| MST | ≥2 | ≥85% | ≥85% | acute-care + outpatient |

False-positive impact in NutriMe's deployment: a false-positive ED or food-security or depression screen results in a consult-professional surface with appropriate-resource links — low-cost on the user side, since NutriMe's response is "here's the resource if you want it" rather than gatekeeping. False-negative impact is more serious (a missed ED or food-insecurity case may receive standard meal-planning suggestions that are inappropriate). The right design posture is **stepped screening with low first-step thresholds** (cast a wide net at the brief-screener step; let the second-step instrument or self-disclosed context narrow false positives).

#### Q: Which clinical assessment frameworks explicitly address pattern-based vs. recall-based methodology?

NCP/ADIME treats both as legitimate within the Dietary domain of assessment (§1.1) — the framework itself is method-agnostic and the practitioner selects per assessment question. The *pattern-based-preferred* literature is concentrated in chronic-disease prevention (cardiovascular nutrition, particularly the Mediterranean-diet pattern literature) and in primary-care-feasible nutrition counseling, where MEDAS and adjacent pattern instruments are explicitly preferred over recall. SGA/PG-SGA and MNA frame intake change in pattern terms ("intake reduced over the past 2 weeks", "any change in usual eating") rather than recall terms. GLIM is pattern-leaning by design. Recall-instrument literature (NCI ASA24, etc.) is concentrated in research-grade epidemiology rather than clinical-counseling practice.

#### Q: Literature on combining dietary assessment with cultural-competency assessment?

Limited integrated literature. The closest is the *culturally-tailored FFQ* tradition (Asian American, Mexican American, Caribbean American FFQs) which embeds cultural-food-list adaptation into the dietary instrument itself. Cultural-competency frameworks (Campinha-Bacote, Purnell Model) are taught alongside dietary assessment in RD programs but published instrument-validation work that *combines* the two is sparse. The growing **food-as-medicine** and **culturally-tailored intervention** literature (e.g., Soul Food Diabetes Education trials, latinx-tailored DASH adaptations) is the most-active area producing combined frameworks. Open research opportunity for NutriMe: the iterative-intake architecture is well-suited to *generating* combined data that the published literature underrepresents.

#### Q: Instruments for "food relationship" beyond TFEQ and IES-2?

- **EDE-Q** (eating-pathology-focused; not a "relationship" instrument per se but the dominant self-report ED-symptom instrument)
- **DEBQ** (Dutch Eating Behavior Questionnaire, van Strien et al., 1986): three subscales — restrained, emotional, external eating. Older predecessor to TFEQ-R18; still widely used.
- **Mindful Eating Questionnaire (MEQ)** (Framson et al., 2009) and **Mindful Eating Scale (MES)** — measure mindful-eating constructs. Less psychometrically established than TFEQ/IES-2.
- **Yale Food Addiction Scale (YFAS / YFAS 2.0)** (Gearhardt et al., 2009; 2016): operationalizes "food addiction" using DSM substance-use-disorder criteria mapped to food. Construct contested in the literature (treat with audit-as-education honesty). Useful as *one signal* alongside TFEQ/IES-2 rather than alone.
- **Power of Food Scale (PFS)** (Lowe et al., 2009): hedonic hunger measure.
- **Eating Loss of Control Scale (ELOCS)**: more recent, focused on subjective LOC eating.

The "food relationship" construct space is fragmented — there is no single dominant instrument. NutriMe's iterative intake can elicit many of the same dimensions through dialog rather than scale administration; the validated scales above are useful as *internal-rubric vocabulary* even when not administered to users.

#### Q: Consumer-friendly adaptation of clinical-grade assessment?

Limited direct literature; the most-cited consumer-facing translations are:

- **MyPlate Quiz / Start Simple with MyPlate** (USDA): consumer-friendly nutrition self-check. Not validated as a clinical instrument; tier 1 (USDA) for the underlying guidance, untested as a screener.
- **NIH Healthy Eating Index calculator** (consumer-facing): translates HEI into a back-end-computed score from user-entered food frequencies. Validated (the underlying HEI is validated; the consumer tool inherits validity if input fidelity holds).
- **NHS Food Scanner / Sugar Smart / Couch to 5K-style behavioral apps**: trial-validated in behavioral-change endpoints rather than as assessment instruments per se.
- **PROMIS** (Patient-Reported Outcomes Measurement Information System, NIH): mature framework for patient-reported outcome measurement that has *not* been heavily applied to nutrition-pattern assessment but is the closest "validated psychometrics in consumer-facing format" framework available. PROMIS-style item-banking + computer-adaptive testing is a methodological template NutriMe could borrow for adaptive intake.
- **DETERMINE checklist** (Nutrition Screening Initiative, US, 1991, for older-adult community use): an early consumer-facing nutrition checklist; validation profile is mixed but shows the precedent for consumer-friendly translation.

The recurring challenge: every clinical-grade instrument that has been "consumer-friendly-ified" has typically *lost* psychometric validity in the translation. NutriMe's path is to design the intake-agent layer to *preserve* the validated-instrument item structure while delivering it via natural-language conversation — a research opportunity rather than a literature gap to consume.

### 11. Cross-sweep notes

- **Sweep #1 (international nutrition standards):** GLIM, SACN/EFSA/USDA pediatric and adult dietary guidelines, and the home-country pregnancy/lactation authority guidance are all natural cross-cites; the assessment instruments here *operationalize* the standards there.
- **Sweep #4 (adaptive intake agent):** every instrument here is a candidate substrate. The agent's job is the consumer-friendly translation while preserving the validated item structure; PROMIS-style adaptive testing is the closest methodological template.
- **Sweep #6 (wearable data availability):** sleep (PSQI / SCI), activity (IPAQ / GPAQ), and stress signals (PSS-4) all have wearable-derived analogues that can supplant or augment the screeners.
- **Sweep #8 (nutrition education delivery):** literacy + cooking-knowledge signals shape content delivery complexity.
- **Sweep #9 (multi-user household):** pediatric + parent-mediated assessment principles and household food-security framing live here.
- **Sweep #10 (clinical condition gating):** every positive screener feeds into condition-aware planning + consult-professional triggers.
- **Sweep #11 (recipe sourcing):** cooking-confidence + cooking-literacy signals inform recipe presentation modality and glossary-expansion needs.

### 12. Gaps and follow-up suggestions

1. **Re-verify all sensitivity/specificity figures** (flagged **[verify]** above) against the original validation publications when web access is restored.
2. **Assemble the actual short-form item-text** for SCOFF, ESP, Hunger Vital Sign, AUDIT-C, PHQ-2, GAD-2, MNA-SF, MST, NVS — many are in the public domain and can be embedded directly; some are copyrighted (PSQI is licensed; PHQ-9/GAD-7 are public domain via Pfizer's release; SCOFF is described in the original BMJ paper). **Licensing audit needed before any item is embedded in product code.**
3. **Cross-cultural validation gap mapping:** for each instrument in §4, document which non-Western populations have published validations vs. which do not. This feeds the [Rule 9 (geographic neutrality)](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing) presentation — the system should disclose when an instrument's validation is mostly Western.
4. **GLIM operational adaptation for consumer self-administration:** GLIM was designed for clinician administration. A consumer-facing GLIM-suggestive screener does not appear to exist in the published literature — opportunity to design and validate one as part of a NutriMe research extension (would require formal psychometric work outside the current sweep scope).
5. **Adolescent self-report consent + parent-mediated triangulation pathways:** scope §"Pediatric assessment" identifies the principle; the operational design (UI flow, consent capture, data-segregation rules) belongs to [sweep #9](../09-multi-user-household/scope.md) and to product design, not to this reference map.
6. **ARFID vs. typical picky eating:** the line is clinically important and currently captured by NIAS/PARDI-AR-Q; a NutriMe rule for *when to surface the ARFID consideration vs. when to treat as preference* would benefit from a separate small focused sweep or an [audit-as-education](../00-meta/evidence-tiers.md#audit-as-education-pattern) explainer.
7. **"Food relationship" construct fragmentation:** the literature here is not consolidating around a single instrument; NutriMe's elicitation design can (and probably should) treat this as an *iterative-dialog* problem rather than a single-instrument administration problem.

## References

> All references accessed `2026-04-28` (training-data reconstruction; URLs/DOIs to be re-verified per epistemic note above). Format per [citation-style.md](../00-meta/citation-style.md). Add to [sources.md](../00-meta/sources.md) in the consolidation pass.

### Clinical assessment frameworks

> **Academy of Nutrition and Dietetics** (current edition). *Nutrition Care Process and Terminology (NCP / NCPT) / eNCPT*. Academy of Nutrition and Dietetics. https://www.ncpro.org/. Accessed 2026-04-28. **[Tier 1.]**

> Detsky, A.S., McLaughlin, J.R., Baker, J.P., Johnston, N., Whittaker, S., Mendelson, R.A., Jeejeebhoy, K.N. (1987). What is subjective global assessment of nutritional status? *Journal of Parenteral and Enteral Nutrition*, 11(1), 8–13. https://doi.org/10.1177/014860718701100108. **[Tier 3 — original validation; SGA itself is Tier 1-equivalent in clinical use.]**

> Ottery, F.D. (1996). Definition of standardized nutritional assessment and interventional pathways in oncology. *Nutrition*, 12(1 Suppl), S15–S19. https://doi.org/10.1016/0899-9007(96)90011-8. **[Tier 3 — PG-SGA development.]**

> Bauer, J., Capra, S., Ferguson, M. (2002). Use of the scored Patient-Generated Subjective Global Assessment (PG-SGA) as a nutrition assessment tool in patients with cancer. *European Journal of Clinical Nutrition*, 56(8), 779–785. https://doi.org/10.1038/sj.ejcn.1601412. **[Tier 3.]**

> Guigoz, Y., Vellas, B., Garry, P.J. (1994). Mini Nutritional Assessment: a practical assessment tool for grading the nutritional state of elderly patients. *Facts and Research in Gerontology*, Suppl 2, 15–59. **[Tier 3 — original MNA development.]**

> Rubenstein, L.Z., Harker, J.O., Salvà, A., Guigoz, Y., Vellas, B. (2001). Screening for undernutrition in geriatric practice: developing the short-form mini-nutritional assessment (MNA-SF). *Journals of Gerontology Series A*, 56(6), M366–M372. https://doi.org/10.1093/gerona/56.6.M366. **[Tier 3 — MNA-SF development.]**

> Kaiser, M.J., Bauer, J.M., Ramsch, C., et al. (2009). Validation of the Mini Nutritional Assessment short-form (MNA-SF): a practical tool for identification of nutritional status. *Journal of Nutrition, Health and Aging*, 13(9), 782–788. https://doi.org/10.1007/s12603-009-0214-7. **[Tier 3 — multinational MNA-SF re-validation.]**

> Ferguson, M., Capra, S., Bauer, J., Banks, M. (1999). Development of a valid and reliable malnutrition screening tool for adult acute hospital patients. *Nutrition*, 15(6), 458–464. https://doi.org/10.1016/S0899-9007(99)00084-2. **[Tier 3 — MST original.]**

> **BAPEN** (2003 / current). *Malnutrition Universal Screening Tool (MUST)*. British Association for Parenteral and Enteral Nutrition. https://www.bapen.org.uk/screening-and-must/must. Accessed 2026-04-28. **[Tier 1.]**

> Cederholm, T., Barazzoni, R., Austin, P., et al. (2017). ESPEN guidelines on definitions and terminology of clinical nutrition. *Clinical Nutrition*, 36(1), 49–64. https://doi.org/10.1016/j.clnu.2016.09.004. **[Tier 1.]**

> Cederholm, T., Jensen, G.L., Correia, M.I.T.D., et al. (2019). GLIM criteria for the diagnosis of malnutrition — a consensus report from the global clinical nutrition community. *Clinical Nutrition*, 38(1), 1–9. https://doi.org/10.1016/j.clnu.2018.08.002. **[Tier 1.]**

> Kondrup, J., Rasmussen, H.H., Hamberg, O., Stanga, Z. (2003). Nutritional risk screening (NRS 2002): a new method based on an analysis of controlled clinical trials. *Clinical Nutrition*, 22(3), 321–336. https://doi.org/10.1016/S0261-5614(02)00214-5. **[Tier 3 — NRS-2002 development; ESPEN-endorsed.]**

### Pattern-based dietary assessment

> Schröder, H., Fitó, M., Estruch, R., et al. (2011). A short screener is valid for assessing Mediterranean diet adherence among older Spanish men and women. *Journal of Nutrition*, 141(6), 1140–1145. https://doi.org/10.3945/jn.110.135566. **[Tier 3 — MEDAS validation.]**

> Estruch, R., Ros, E., Salas-Salvadó, J., et al. (2013, with 2018 retraction-and-republication). Primary prevention of cardiovascular disease with a Mediterranean diet supplemented with extra-virgin olive oil or nuts. *New England Journal of Medicine*, 378:e34. https://doi.org/10.1056/NEJMoa1800389. **[Tier 1 — PREDIMED main trial; MEDAS-administered cohort.]**

> Krebs-Smith, S.M., Pannucci, T.E., Subar, A.F., et al. (2018). Update of the Healthy Eating Index: HEI-2015. *Journal of the Academy of Nutrition and Dietetics*, 118(9), 1591–1602. https://doi.org/10.1016/j.jand.2018.05.021. **[Tier 1.]** (HEI-2020 update available — verify current edition citation.)

> Chiuve, S.E., Fung, T.T., Rimm, E.B., et al. (2012). Alternative dietary indices both strongly predict risk of chronic disease. *Journal of Nutrition*, 142(6), 1009–1018. https://doi.org/10.3945/jn.111.157222. **[Tier 2 — AHEI-2010 validation.]**

> Fung, T.T., Chiuve, S.E., McCullough, M.L., Rexrode, K.M., Logroscino, G., Hu, F.B. (2008). Adherence to a DASH-style diet and risk of coronary heart disease and stroke in women. *Archives of Internal Medicine*, 168(7), 713–720. https://doi.org/10.1001/archinte.168.7.713. **[Tier 2 — DASH score in NHS cohort.]**

> Morris, M.C., Tangney, C.C., Wang, Y., et al. (2015). MIND diet associated with reduced incidence of Alzheimer's disease. *Alzheimer's & Dementia*, 11(9), 1007–1014. https://doi.org/10.1016/j.jalz.2014.11.009. **[Tier 3 — MIND diet score; cohort design.]**

> Satija, A., Bhupathiraju, S.N., Spiegelman, D., et al. (2017). Healthful and unhealthful plant-based diets and the risk of coronary heart disease in U.S. adults. *Journal of the American College of Cardiology*, 70(4), 411–422. https://doi.org/10.1016/j.jacc.2017.05.047. **[Tier 2 — PDI/hPDI/uPDI.]**

> Steptoe, A., Pollard, T.M., Wardle, J. (1995). Development of a measure of the motives underlying the selection of food: the Food Choice Questionnaire. *Appetite*, 25(3), 267–284. https://doi.org/10.1006/appe.1995.0061. **[Tier 3 — FCQ validation.]**

> Pliner, P., Hobden, K. (1992). Development of a scale to measure the trait of food neophobia in humans. *Appetite*, 19(2), 105–120. https://doi.org/10.1016/0195-6663(92)90014-W. **[Tier 3 — Food Neophobia Scale.]**

### Recall-based instruments (reference)

> Moshfegh, A.J., Rhodes, D.G., Baer, D.J., et al. (2008). The US Department of Agriculture Automated Multiple-Pass Method reduces bias in the collection of energy intakes. *American Journal of Clinical Nutrition*, 88(2), 324–332. https://doi.org/10.1093/ajcn/88.2.324. **[Tier 2.]**

> Subar, A.F., Kirkpatrick, S.I., Mittl, B., et al. (2012). The Automated Self-Administered 24-Hour Dietary Recall (ASA24): a resource for researchers, clinicians, and educators from the National Cancer Institute. *Journal of the Academy of Nutrition and Dietetics*, 112(8), 1134–1137. https://doi.org/10.1016/j.jand.2012.04.016. **[Tier 1.]**

> **NCI** (current). *Diet History Questionnaire III (DHQ III)*. National Cancer Institute, US. https://epi.grants.cancer.gov/dhq3/. Accessed 2026-04-28. **[Tier 1.]**

> **NCI** (current). *ASA24 Dietary Assessment Tool*. National Cancer Institute, US. https://epi.grants.cancer.gov/asa24/. Accessed 2026-04-28. **[Tier 1.]**

> Block, G., Hartman, A.M., Dresser, C.M., Carroll, M.D., Gannon, J., Gardner, L. (1986). A data-based approach to diet questionnaire design and testing. *American Journal of Epidemiology*, 124(3), 453–469. https://doi.org/10.1093/oxfordjournals.aje.a114416. **[Tier 3 — Block FFQ original.]**

> Bingham, S.A., Gill, C., Welch, A., et al. (1994). Comparison of dietary assessment methods in nutritional epidemiology: weighed records v. 24 h recalls, food-frequency questionnaires and estimated-diet records. *British Journal of Nutrition*, 72(4), 619–643. https://doi.org/10.1079/BJN19940064. **[Tier 2 — EPIC FFQ comparative validation.]**

### Eating disorder screeners

> Morgan, J.F., Reid, F., Lacey, J.H. (1999). The SCOFF questionnaire: assessment of a new screening tool for eating disorders. *BMJ*, 319(7223), 1467–1468. https://doi.org/10.1136/bmj.319.7223.1467. **[Tier 3 — SCOFF original.]**

> Garner, D.M., Olmsted, M.P., Bohr, Y., Garfinkel, P.E. (1982). The Eating Attitudes Test: psychometric features and clinical correlates. *Psychological Medicine*, 12(4), 871–878. https://doi.org/10.1017/S0033291700049163. **[Tier 3 — EAT-26.]**

> Cotton, M.A., Ball, C., Robinson, P. (2003). Four simple questions can help screen for eating disorders. *Journal of General Internal Medicine*, 18(1), 53–56. https://doi.org/10.1046/j.1525-1497.2003.20374.x. **[Tier 3 — ESP.]**

> Fairburn, C.G., Beglin, S.J. (1994). Assessment of eating disorders: interview or self-report questionnaire? *International Journal of Eating Disorders*, 16(4), 363–370. **[Tier 3 — EDE-Q.]**

### Food security

> Hager, E.R., Quigg, A.M., Black, M.M., et al. (2010). Development and validity of a 2-item screen to identify families at risk for food insecurity. *Pediatrics*, 126(1), e26–e32. https://doi.org/10.1542/peds.2009-3146. **[Tier 3 — Hunger Vital Sign.]**

> Blumberg, S.J., Bialostosky, K., Hamilton, W.L., Briefel, R.R. (1999). The effectiveness of a short form of the Household Food Security Scale. *American Journal of Public Health*, 89(8), 1231–1234. https://doi.org/10.2105/AJPH.89.8.1231. **[Tier 3 — USDA 6-item short form.]**

> **USDA Economic Research Service** (current). *U.S. Household Food Security Survey Module: Six-Item Short Form*. https://www.ers.usda.gov/topics/food-nutrition-assistance/food-security-in-the-u-s/survey-tools/. Accessed 2026-04-28. **[Tier 1.]**

### Alcohol use

> Saunders, J.B., Aasland, O.G., Babor, T.F., de la Fuente, J.R., Grant, M. (1993). Development of the Alcohol Use Disorders Identification Test (AUDIT): WHO collaborative project on early detection of persons with harmful alcohol consumption — II. *Addiction*, 88(6), 791–804. https://doi.org/10.1111/j.1360-0443.1993.tb02093.x. **[Tier 3 — AUDIT.]**

> Bush, K., Kivlahan, D.R., McDonell, M.B., Fihn, S.D., Bradley, K.A. (1998). The AUDIT alcohol consumption questions (AUDIT-C): an effective brief screening test for problem drinking. *Archives of Internal Medicine*, 158(16), 1789–1795. https://doi.org/10.1001/archinte.158.16.1789. **[Tier 3 — AUDIT-C.]**

### Activity

> Craig, C.L., Marshall, A.L., Sjöström, M., et al. (2003). International physical activity questionnaire: 12-country reliability and validity. *Medicine and Science in Sports and Exercise*, 35(8), 1381–1395. https://doi.org/10.1249/01.MSS.0000078924.61453.FB. **[Tier 2 — IPAQ multinational validation.]**

> Bull, F.C., Maslin, T.S., Armstrong, T. (2009). Global Physical Activity Questionnaire (GPAQ): nine country reliability and validity study. *Journal of Physical Activity and Health*, 6(6), 790–804. https://doi.org/10.1123/jpah.6.6.790. **[Tier 3 — GPAQ.]**

### Readiness for change

> Prochaska, J.O., DiClemente, C.C. (1983). Stages and processes of self-change of smoking: toward an integrative model of change. *Journal of Consulting and Clinical Psychology*, 51(3), 390–395. https://doi.org/10.1037/0022-006X.51.3.390. **[Tier 3 — TTM original.]**

> Miller, W.R., Rollnick, S. (2013). *Motivational Interviewing: Helping People Change* (3rd ed.). Guilford Press. **[Tier 1-equivalent — clinical-practice consensus reference; importance/confidence rulers operationalized within MI.]**

### Sleep

> Buysse, D.J., Reynolds, C.F. III, Monk, T.H., Berman, S.R., Kupfer, D.J. (1989). The Pittsburgh Sleep Quality Index: a new instrument for psychiatric practice and research. *Psychiatry Research*, 28(2), 193–213. https://doi.org/10.1016/0165-1781(89)90047-4. **[Tier 3 — PSQI.]**

> Espie, C.A., Kyle, S.D., Hames, P., Gardani, M., Fleming, L., Cape, J. (2014). The Sleep Condition Indicator: a clinical screening tool to evaluate insomnia disorder. *BMJ Open*, 4(3), e004183. https://doi.org/10.1136/bmjopen-2013-004183. **[Tier 3 — SCI.]**

> Chung, F., Yegneswaran, B., Liao, P., et al. (2008). STOP questionnaire: a tool to screen patients for obstructive sleep apnea. *Anesthesiology*, 108(5), 812–821. https://doi.org/10.1097/ALN.0b013e31816d83e4. **[Tier 3 — STOP-BANG.]**

### Mood and anxiety

> Kroenke, K., Spitzer, R.L., Williams, J.B.W. (2001). The PHQ-9: validity of a brief depression severity measure. *Journal of General Internal Medicine*, 16(9), 606–613. https://doi.org/10.1046/j.1525-1497.2001.016009606.x. **[Tier 3 — PHQ-9.]**

> Kroenke, K., Spitzer, R.L., Williams, J.B.W. (2003). The Patient Health Questionnaire-2: validity of a two-item depression screener. *Medical Care*, 41(11), 1284–1292. https://doi.org/10.1097/01.MLR.0000093487.78664.3C. **[Tier 3 — PHQ-2.]**

> Spitzer, R.L., Kroenke, K., Williams, J.B.W., Löwe, B. (2006). A brief measure for assessing generalized anxiety disorder: the GAD-7. *Archives of Internal Medicine*, 166(10), 1092–1097. https://doi.org/10.1001/archinte.166.10.1092. **[Tier 3 — GAD-7.]**

> Kroenke, K., Spitzer, R.L., Williams, J.B.W., Monahan, P.O., Löwe, B. (2007). Anxiety disorders in primary care: prevalence, impairment, comorbidity, and detection. *Annals of Internal Medicine*, 146(5), 317–325. https://doi.org/10.7326/0003-4819-146-5-200703060-00004. **[Tier 3 — GAD-2.]**

### Stress

> Cohen, S., Kamarck, T., Mermelstein, R. (1983). A global measure of perceived stress. *Journal of Health and Social Behavior*, 24(4), 385–396. https://doi.org/10.2307/2136404. **[Tier 3 — PSS.]** (PSS-4 short form derived in subsequent literature.)

### GI symptoms

> Drossman, D.A. (2016). Functional gastrointestinal disorders: history, pathophysiology, clinical features, and Rome IV. *Gastroenterology*, 150(6), 1262–1279.e2. https://doi.org/10.1053/j.gastro.2016.02.032. **[Tier 1-equivalent — Rome IV consensus introduction.]**

### Eating behavior

> Karlsson, J., Persson, L.O., Sjöström, L., Sullivan, M. (2000). Psychometric properties and factor structure of the Three-Factor Eating Questionnaire (TFEQ) in obese men and women. Results from the Swedish Obese Subjects (SOS) study. *International Journal of Obesity*, 24(12), 1715–1725. https://doi.org/10.1038/sj.ijo.0801442. **[Tier 3 — TFEQ-R18.]**

> Tylka, T.L., Kroon Van Diest, A.M. (2013). The Intuitive Eating Scale-2: item refinement and psychometric evaluation with college women and men. *Journal of Counseling Psychology*, 60(1), 137–153. https://doi.org/10.1037/a0030893. **[Tier 3 — IES-2.]**

> van Strien, T., Frijters, J.E.R., Bergers, G.P.A., Defares, P.B. (1986). The Dutch Eating Behavior Questionnaire (DEBQ) for assessment of restrained, emotional, and external eating behavior. *International Journal of Eating Disorders*, 5(2), 295–315. **[Tier 3 — DEBQ.]**

> Gearhardt, A.N., Corbin, W.R., Brownell, K.D. (2009). Preliminary validation of the Yale Food Addiction Scale. *Appetite*, 52(2), 430–436. https://doi.org/10.1016/j.appet.2008.12.003. **[Tier 3 — YFAS; construct contested.]**

> Donini, L.M., Marsili, D., Graziani, M.P., Imbriale, M., Cannella, C. (2005). Orthorexia nervosa: validation of a diagnosis questionnaire. *Eating and Weight Disorders*, 10(2), e28–e32. https://doi.org/10.1007/BF03327537. **[Tier 3 — ORTO-15; psychometric concerns documented.]**

> Rogoza, R., Donini, L.M. (2021). Introducing ORTO-R: a revision of ORTO-15. *Eating and Weight Disorders*, 26(3), 887–895. https://doi.org/10.1007/s40519-020-00924-5. **[Tier 3 — ORTO-R revision.]**

### Cooking confidence and literacy

> Lavelle, F., McGowan, L., Hollywood, L., et al. (2017). The development and validation of measures to assess cooking skills and food skills. *International Journal of Behavioral Nutrition and Physical Activity*, 14, 118. https://doi.org/10.1186/s12966-017-0575-y. **[Tier 3 — CCSS / Lavelle cooking-skills + food-skills measures.]**

> Hartmann, C., Dohle, S., Siegrist, M. (2013). Importance of cooking skills for balanced food choices. *Appetite*, 65, 125–131. https://doi.org/10.1016/j.appet.2013.01.016. **[Tier 3.]**

### Health literacy

> Arozullah, A.M., Yarnold, P.R., Bennett, C.L., et al. (2007). Development and validation of a short-form, rapid estimate of adult literacy in medicine. *Medical Care*, 45(11), 1026–1033. https://doi.org/10.1097/MLR.0b013e3180616c1b. **[Tier 3 — REALM-SF.]**

> Parker, R.M., Baker, D.W., Williams, M.V., Nurss, J.R. (1995). The test of functional health literacy in adults: a new instrument for measuring patients' literacy skills. *Journal of General Internal Medicine*, 10(10), 537–541. https://doi.org/10.1007/BF02640361. **[Tier 3 — TOFHLA.]**

> Weiss, B.D., Mays, M.Z., Martz, W., et al. (2005). Quick assessment of literacy in primary care: the Newest Vital Sign. *Annals of Family Medicine*, 3(6), 514–522. https://doi.org/10.1370/afm.405. **[Tier 3 — NVS.]**

> Norman, C.D., Skinner, H.A. (2006). eHEALS: the eHealth Literacy Scale. *Journal of Medical Internet Research*, 8(4), e27. https://doi.org/10.2196/jmir.8.4.e27. **[Tier 3 — eHEALS.]**

### Pediatric assessment

> Randall Simpson, J.A., Keller, H.H., Rysdale, L.A., Beyers, J.E. (2008). Nutrition Screening Tool for Every Preschooler (NutriSTEP): validation and test-retest reliability of a parent-administered questionnaire assessing nutrition risk of preschoolers. *European Journal of Clinical Nutrition*, 62(6), 770–780. https://doi.org/10.1038/sj.ejcn.1602780. **[Tier 3 — NutriSTEP preschool.]**

> Murphy, J., Hatfield, J., Arsenault, J., Rysdale, L., Ouellette, V., Beyers, J., Bourgon, B., Vesey, K., Keller, H., Randall Simpson, J. (2014). NutriSTEP: nutrition screening for school-age children. *Canadian Journal of Dietetic Practice and Research*. **[Tier 3 — school-age extension.]**

> **CDC** (current). *Growth Charts*. Centers for Disease Control and Prevention. https://www.cdc.gov/growthcharts/. Accessed 2026-04-28. **[Tier 1.]**

> **WHO** (2006). *WHO Child Growth Standards*. World Health Organization Multicentre Growth Reference Study. https://www.who.int/tools/child-growth-standards. Accessed 2026-04-28. **[Tier 1.]**

> de Onis, M., Onyango, A.W., Borghi, E., Siyam, A., Nishida, C., Siekmann, J. (2007). Development of a WHO growth reference for school-aged children and adolescents. *Bulletin of the World Health Organization*, 85(9), 660–667. https://doi.org/10.2471/BLT.07.043497. **[Tier 1.]**

> **AAP** — Hagan, J.F., Shaw, J.S., Duncan, P.M. (eds.) (2017). *Bright Futures: Guidelines for Health Supervision of Infants, Children, and Adolescents* (4th ed.). American Academy of Pediatrics. https://brightfutures.aap.org/. Accessed 2026-04-28. **[Tier 1.]**

> Childress, A.C., Brewerton, T.D., Hodges, E.L., Jarrell, M.P. (1993). The Kids' Eating Disorders Survey (KEDS): a study of middle school students. *Journal of the American Academy of Child & Adolescent Psychiatry*, 32(4), 843–850. https://doi.org/10.1097/00004583-199307000-00021. **[Tier 3 — KEDS.]**

> Maloney, M.J., McGuire, J.B., Daniels, S.R. (1988). Reliability testing of a children's version of the Eating Attitude Test. *Journal of the American Academy of Child & Adolescent Psychiatry*, 27(5), 541–543. https://doi.org/10.1097/00004583-198809000-00004. **[Tier 3 — ChEAT.]**

> Bryant-Waugh, R., Micali, N., Cooke, L., Lawson, E.A., Eddy, K.T., Thomas, J.J. (2019). Development of the Pica, ARFID, and Rumination Disorder Interview, a multi-informant, semi-structured interview of feeding disorders across the lifespan: a pilot study for ages 10–22. *International Journal of Eating Disorders*, 52(4), 378–387. https://doi.org/10.1002/eat.22958. **[Tier 3 — PARDI / PARDI-AR-Q development.]**

> Zickgraf, H.F., Ellis, J.M. (2018). Initial validation of the Nine Item Avoidant/Restrictive Food Intake disorder screen (NIAS): a measure of three restrictive eating patterns. *Appetite*, 123, 32–42. https://doi.org/10.1016/j.appet.2017.11.111. **[Tier 3 — NIAS.]**

> Boyce, J.A., Assa'ad, A., Burks, A.W., et al. (2010). Guidelines for the Diagnosis and Management of Food Allergy in the United States: Report of the NIAID-Sponsored Expert Panel. *Journal of Allergy and Clinical Immunology*, 126(6 Suppl), S1–S58. https://doi.org/10.1016/j.jaci.2010.10.007. **[Tier 1.]** (Updated 2017 addendum on peanut introduction: Togias, A., et al., *Journal of Allergy and Clinical Immunology*, 139(1), 29–44.)

> **USDA Economic Research Service** (current). *Children's Food Security Survey Module*. https://www.ers.usda.gov/topics/food-nutrition-assistance/food-security-in-the-u-s/survey-tools/. Accessed 2026-04-28. **[Tier 1.]**

### Cultural competency

> Campinha-Bacote, J. (2002). The Process of Cultural Competence in the Delivery of Healthcare Services: a model of care. *Journal of Transcultural Nursing*, 13(3), 181–184. https://doi.org/10.1177/10459602013003003. **[Tier 3 — model description.]**

> **ACEND** (current standards). *Accreditation Standards for Nutrition and Dietetics Programs*. Accreditation Council for Education in Nutrition and Dietetics, Academy of Nutrition and Dietetics. https://www.eatrightpro.org/acend. Accessed 2026-04-28. **[Tier 1 — professional accreditation standards; verify current cycle.]**

> Kittler, P.G., Sucher, K.P., Nelms, M. (2017). *Food and Culture* (7th ed.). Cengage Learning. **[Tier 1-equivalent — dominant US RD textbook on cultural foodways.]**

### Trauma-informed assessment

> **SAMHSA** (2014). *SAMHSA's Concept of Trauma and Guidance for a Trauma-Informed Approach* (HHS Publication No. (SMA) 14-4884). Substance Abuse and Mental Health Services Administration. https://store.samhsa.gov/product/SAMHSA-s-Concept-of-Trauma-and-Guidance-for-a-Trauma-Informed-Approach/SMA14-4884. Accessed 2026-04-28. **[Tier 1.]**

> Tylka, T.L., Annunziato, R.A., Burgard, D., et al. (2014). The weight-inclusive versus weight-normative approach to health: evaluating the evidence for prioritizing well-being over weight loss. *Journal of Obesity*, 2014, 983495. https://doi.org/10.1155/2014/983495. **[Tier 2.]**

> Tribole, E., Resch, E. (2020). *Intuitive Eating: A Revolutionary Anti-Diet Approach* (4th ed.). St. Martin's Essentials. **[Tier 1-equivalent — clinical-practice consensus reference.]**

### Process / methodology references

> Chen, J., Mullins, C.D., Novak, P., Thomas, S.B. (2016). Personalized strategies to activate and empower patients in health care and reduce health disparities. *Health Education and Behavior*, 43(1), 25–34. https://doi.org/10.1177/1090198115579415. **[Tier 3 — patient-activation framework adjacent to NutriMe iterative-intake design.]**

> Cella, D., Riley, W., Stone, A., et al. (2010). The Patient-Reported Outcomes Measurement Information System (PROMIS) developed and tested its first wave of adult self-reported health outcome item banks: 2005–2008. *Journal of Clinical Epidemiology*, 63(11), 1179–1194. https://doi.org/10.1016/j.jclinepi.2010.04.011. **[Tier 1 — PROMIS methodology.]**


