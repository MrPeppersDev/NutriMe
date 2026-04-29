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

To be populated when research is run.

## References

To be populated. Add new sources to [sources.md](../00-meta/sources.md) when added.
