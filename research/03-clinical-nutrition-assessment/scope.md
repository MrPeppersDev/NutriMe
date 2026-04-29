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

To be populated when research is run.

## References

To be populated. Add new sources to [sources.md](../00-meta/sources.md) when added.
