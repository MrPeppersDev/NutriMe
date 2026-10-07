# Sweep #5 — Personalized Nutrition — Evidence Audit

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Honest tier-by-claim audit of personalized nutrition science across the major commercial and academic strands: PREDICT / ZOE, Food4Me, microbiome-based personalization, nutrigenomics, metabolomics, and CGM-for-non-diabetics. Establish what evidence supports each claim vs. what vendors market. Output serves dual purpose: (1) gates which personalization mechanisms can drive system behavior under the [peer-reviewed floor](../00-meta/constitutional-rules.md#rule-7--peer-reviewed-evidence-floor), and (2) becomes "audit-as-education" content per [evidence-tiers.md](../00-meta/evidence-tiers.md#audit-as-education-pattern).

## Deliverable

A per-domain evidence audit table with:

- Domain (e.g., "CGM-driven meal personalization for non-diabetics")
- Best Tier 1 evidence (if any)
- Best Tier 2 evidence (systematic reviews, meta-analyses)
- Representative Tier 3 evidence (RCTs, cohort studies)
- Tier 4 marketing-vs-evidence gap (vendors, marketed claims)
- **Steel-man counter-evidence** — strongest published case that the personalization mechanism adds little over good population-level guidance
- Verdict against NutriMe's evidence floor: drives system behavior? Educational-content-only? Excluded?
- Notes on n-of-1 study designs relevant to NutriMe's [semantic feedback loop](../00-meta/intake-pattern.md#mode-3--passive-confirmation--semantic-feedback)

Format is flexible — research findings may justify expansion (additional domains, methodological subsections, international initiative summaries).

This is a **reference map**, not corpus build. Audit produces the evidence summaries; ingestion of underlying datasets/studies happens later.

## Domains in scope

- **PREDICT / ZOE** — large cohort with CGM, gut microbiome, postprandial response measurement
- **Food4Me** — EU-funded RCT of personalization based on questionnaires + biomarkers + genetics
- **Microbiome-based personalization** — Viome, ZOE microbiome component, DayTwo, academic literature
- **Nutrigenomics** — DNAFit, Nutrigenomix, 23andMe-derived diets, academic literature
- **Metabolomics-based personalization** — InsideTracker (blood biomarkers), commercial blood-test-driven diets
- **CGM-for-non-diabetics** — Levels, Nutrisense, Stelo (Dexcom OTC), academic literature on glucose response variability — **stretch goal at reference level**, not primary
- **N-of-1 study designs in nutrition** — small but growing literature; relevant to how the semantic feedback loop is designed
- **Steel-man literature** — strongest published evidence that personalization adds little over good population guidance (Beresford 2006, others)
- **International initiatives** — UK NHS personalized nutrition pilots, EU Horizon programs, Chinese precision-nutrition initiatives, Israeli Weizmann work (Segal lab — major center)

## Geographic scope

Per [geographic-scope.md](../00-meta/geographic-scope.md) — primary is US, EU, UK, AU, NZ, Canada, China, Japan, Korea, Israel, Russia. Opportunistic inclusion of Nordic countries, India, Brazil, Singapore, and others where notable work surfaces. Per user direction this list is not a hyperfocus — research follows the evidence wherever it's strong.

## Audit-as-education framing

Per user direction: even where personalization mechanisms fail the evidence floor and cannot drive system behavior, the audit itself becomes educational content presented to users. Topics that fall into this category (microbiome, nutrigenomics, metabolomics, fad-diet personalization) are covered honestly: what they claim, what the evidence actually shows, why NutriMe does or does not use them.

This dual purpose shapes how findings should be written — accessible enough to become user-facing educational copy, rigorous enough to back system-behavior decisions.

## Out of scope (with reasons)

- Implementation of personalization mechanisms — that's later phase
- Wearable / biometric *data availability* — covered in [sweep #6](../06-wearable-data-availability/scope.md). Sweep #6 = "what data exists and is reliable"; sweep #5 = "should we act on it"
- General population-level dietary guidance — covered in [sweep #1](../01-international-nutrition-standards/scope.md)
- Bulk ingestion of trial data — deferred

## Open questions for the research

- For each domain: what is the best Tier 2 evidence? Is there ANY Tier 1 evidence?
- What is the strongest published steel-man against personalization adding meaningful value over population guidance?
- For CGM-driven personalization, what does the evidence say about whether postprandial glucose variability translates to meaningful long-term outcomes?
- What does the n-of-1 design literature in nutrition look like, and how could it inform the semantic feedback loop?
- Where are international initiatives moving — is the EU's Horizon precision-nutrition work converging with US/UK approaches, or diverging?
- For microbiome / nutrigenomic / metabolomic testing, where exactly does the marketing diverge from the evidence?

## Cross-references

- Sister sweep to [sweep #6 (wearable data availability)](../06-wearable-data-availability/scope.md) — #6 = data substrate, #5 = should-we-act-on-it evidence
- Bound by [Constitutional Rule 7 (peer-reviewed floor)](../00-meta/constitutional-rules.md#rule-7--peer-reviewed-evidence-floor)
- Bound by [evidence-tiers.md](../00-meta/evidence-tiers.md), especially the [audit-as-education pattern](../00-meta/evidence-tiers.md#audit-as-education-pattern)
- N-of-1 findings cross-reference [intake-pattern.md](../00-meta/intake-pattern.md) — semantic feedback loop design
- Cross-references [sweep #1 (international nutrition standards)](../01-international-nutrition-standards/scope.md) — population-level baseline against which personalization is measured

## Findings

> **Epistemic note (per Rule 8).** This audit was assembled in a session in which live `WebSearch` and `WebFetch` were unavailable. Every citation below is drawn from indexed peer-reviewed literature or canonical organizational documentation known at the assistant's training cutoff (January 2026). DOIs and URLs are stable identifiers. Accessed-on dates of `2026-04-29` reflect the date the catalog was assembled, not a live fetch — a follow-up pass should re-fetch each URL to confirm the published version, any post-publication corrections, and current vendor marketing language (Tier 4 vendor claims drift fastest). Where a specific effect-size number could not be re-checked against the source, the prose says "approximately" or omits the number rather than fabricate one. Per [Rule 7](../00-meta/constitutional-rules.md#rule-7--peer-reviewed-evidence-floor), no Tier 4 claim drives a verdict in this audit; vendor claims are explicitly tagged and audited against published evidence.

### Reading guide

Each domain block has the same shape:

- **What it claims** — one or two sentences in plain language
- **Best Tier 1 evidence** — consensus-body position if any exists
- **Best Tier 2 evidence** — systematic reviews / meta-analyses
- **Representative Tier 3 evidence** — RCTs, prospective cohorts
- **Tier 4 marketing-vs-evidence gap** — what vendors say vs. what the published literature supports
- **Steel-man counter-evidence** — strongest published case the mechanism adds little over good population guidance
- **Verdict against the NutriMe evidence floor** — Drives system behavior / Educational-content-only / Excluded
- **N-of-1 / semantic-feedback-loop relevance** — what (if anything) this domain teaches about how the [semantic feedback loop](../00-meta/intake-pattern.md#mode-3--passive-confirmation--semantic-feedback) should be designed

The **verdict ladder** used throughout:

- **Drives system behavior** — peer-reviewed Tier 1/2 evidence directly supports a default, gate, or recommendation
- **Educational-content-only (audit-as-education)** — evidence does not meet the floor for system behavior, but the topic is high-marketing / high-user-interest enough to warrant honest coverage per [evidence-tiers.md](../00-meta/evidence-tiers.md#audit-as-education-pattern)
- **Excluded** — neither the mechanism nor the marketing rises to the level of warranting coverage at all (rare; reserved for outright pseudo-science)

### A. PREDICT / ZOE

**What it claims.** Postprandial glucose, triglyceride, and insulin responses to identical meals vary substantially between individuals; combining habitual diet, anthropometrics, gut-microbiome composition, and continuous-glucose / postprandial-lipid measurement allows prediction of an individual's response to specific foods, and steering the individual toward "good for me" foods improves cardiometabolic markers.

**Best Tier 1 evidence.** None. No consensus body (NASEM, EFSA, WHO, NHS, NHMRC) currently endorses microbiome-and-postprandial-response-driven personalized meal recommendation as standard care for the general adult population. WHO and NHS communications continue to recommend population-level dietary patterns (Mediterranean / DASH / Eatwell Guide). PREDICT is referenced in academic precision-nutrition position papers but is not yet in clinical guidelines.

**Best Tier 2 evidence.** Limited. The personalized-nutrition field has no Cochrane review supporting commercial postprandial-response personalization as superior to good general guidance. Several scoping / narrative reviews summarize the PREDICT findings (e.g., Bermingham et al. on the ZOE Method study, Berry et al. as a representative cohort) but systematic-review-grade evidence with hard outcomes (CVD events, T2D incidence, mortality) does not yet exist.

**Representative Tier 3 evidence.**

- [Berry et al. 2020 (PREDICT 1)](https://doi.org/10.1038/s41591-020-0934-0) — n ~1,000 (UK adults + US replication twin cohort), characterized large between-person variability in postprandial glucose, triglyceride, and insulin responses to identical standardized meals; meal macros explained a minority of the variance, with person-level factors (microbiome, meal context, sleep, exercise, prior meal) explaining substantially more. Tier 3 (large prospective cohort, well-controlled standardized-meal design).
- [Asnicar et al. 2021 (Nature Medicine)](https://doi.org/10.1038/s41591-020-01183-8) — PREDICT-cohort microbiome paper identifying gut-microbe panels associated with cardiometabolic markers and habitual diet. Tier 3 (cross-sectional + diet-correlation; not an outcomes RCT).
- [Bermingham et al. 2024, Nature Medicine](https://doi.org/10.1038/s41591-024-02951-6) — "ZOE METHOD" RCT: a personalized-nutrition program based on ZOE's predictions vs. general healthy-eating advice in adults with mild metabolic dysregulation. Reported improvements in self-reported energy, hunger, and some lipid markers in the personalized arm; modest absolute effect sizes; behavior-change confounding (intensive coaching arm) is a known limitation. Tier 3 (single RCT, vendor-affiliated authors disclosed).

**Tier 4 marketing-vs-evidence gap.** ZOE's consumer marketing has at times implied that following its scores improves long-term cardiometabolic outcomes (CVD risk, weight, energy). Published evidence supports between-person variability (well-established), correlation with cardiometabolic markers (cross-sectional), and short-term self-reported and biomarker improvement in a single RCT (Bermingham 2024). It does **not** yet support long-term hard-endpoint claims (CVD events, T2D prevention, mortality). The personalized-coaching arm of the trial confounds the score-personalization mechanism with intensive behavioral support — a confound the vendor's marketing typically does not foreground.

**Steel-man counter-evidence.** Standardized population-level dietary patterns (Mediterranean, DASH) have decades of Tier 1 / Tier 2 RCT and meta-analytic support including hard endpoints — most prominently [PREDIMED (Estruch et al. 2018, NEJM)](https://doi.org/10.1056/NEJMoa1800389). The marginal benefit of personalization on top of "follow Mediterranean / DASH well" has not been demonstrated against a hard-outcome control. The honest reading: personalization may improve adherence and biomarkers; whether it beats *adhered-to* population guidance is unproven.

**Verdict.** **Educational-content-only.** The between-person-variability finding is robust enough to acknowledge in user-facing education ("identical meals can produce different glucose responses in different people"). NutriMe does not implement ZOE-style scoring as a system gate or default because the outcome evidence does not yet meet the Tier 1/2 floor for prescriptive behavior. The audit-as-education framing is direct: explain what PREDICT showed, what ZOE's RCT did and did not show, why population guidance remains the foundation, and where the user can pursue personalized testing if curious (with [Rule 1 consult-professional](../00-meta/constitutional-rules.md#rule-1--consult-a-professional) language).

**N-of-1 / feedback-loop relevance.** PREDICT is the strongest empirical demonstration that the same food produces different postprandial responses in different people — the conceptual basis for treating each user as their own experiment. This validates the *premise* of the semantic feedback loop ("how did this meal make you feel" is a meaningful per-person signal), even when the *mechanism* (CGM scoring) is not adopted. NutriMe's loop captures cheaper, semantic, lived-experience equivalents (energy, fullness, digestion, sleep that night) without requiring instrumented postprandial measurement.

### B. Food4Me

**What it claims.** Personalized dietary advice based on individualized phenotype (questionnaire-based diet + anthropometrics ± biomarkers ± genetics) produces greater dietary improvement than general population advice.

**Best Tier 1 evidence.** None. Food4Me is referenced in EU position papers on precision nutrition but has not produced consensus-body adoption.

**Best Tier 2 evidence.** Several systematic reviews of personalized-nutrition trials include Food4Me as a major contributor; conclusions are typically "modest, short-term improvement in dietary quality vs. generic advice, with limited evidence on hard outcomes" (e.g., Jinnette et al. 2021 *Advances in Nutrition*, a systematic review of personalized nutrition interventions on dietary behavior).

**Representative Tier 3 evidence.**

- [Celis-Morales et al. 2017, *International Journal of Epidemiology*](https://doi.org/10.1093/ije/dyw186) — Food4Me proof-of-principle European RCT, n ≈ 1,600 across 7 EU countries. Three personalization tiers (L1 diet, L2 diet+phenotype, L3 diet+phenotype+genotype) vs. control (general advice). Personalized arms produced larger improvements in dietary score than general advice; **adding genotype information did not improve outcomes beyond phenotype + diet personalization.** Six-month follow-up. Tier 3 (RCT, internet-delivered intervention, self-reported dietary outcomes).
- Follow-on Food4Me papers analyzed subgroups (response by APOE genotype, MTHFR, FTO) — generally found subgroup signal too weak to ground prescriptive personalization.

**Tier 4 marketing-vs-evidence gap.** Vendors selling genotype-driven diet plans (DNAFit, Nutrigenomix) implicitly invoke the broader personalization-works narrative. Food4Me's actual finding — **genetics did not add value beyond phenotype-based personalization** — is the opposite of the marketing implication of these products.

**Steel-man counter-evidence.** Same as PREDICT: PREDIMED, DASH-Sodium, and other population-level RCTs on Mediterranean / DASH demonstrate hard-outcome benefit; no Food4Me arm demonstrated hard endpoints. Modest dietary-score change at 6 months is not a clinical outcome.

**Verdict.** **Educational-content-only**, with one important load-bearing finding for system design: **the Food4Me result that genotype did not add value over phenotype-based personalization is itself useful evidence to surface to users curious about nutrigenomic testing.** It is one of the cleanest published refutations of the "DNA-based diet" marketing claim.

**N-of-1 / feedback-loop relevance.** Food4Me validates that **structured iterative phenotype intake** (current diet + anthropometrics + goals) is sufficient to drive personalization that improves dietary behavior — without requiring genotype, microbiome, or CGM. This is closely aligned with NutriMe's intake-driven personalization approach. The feedback-loop implication: rich semantic intake + iterative refinement is empirically defensible as the personalization substrate.

### C. Microbiome-based personalization

**What it claims.** Stool-derived microbiome composition predicts individual food responses or health outcomes, and consumer microbiome tests (Viome, ZOE, DayTwo, uBiome before its collapse) can recommend foods to add or avoid based on microbial composition.

**Best Tier 1 evidence.** None. The American Gastroenterological Association (AGA) and similar bodies have published positions urging caution on direct-to-consumer microbiome testing for clinical decision-making outside specific contexts (FMT for *C. difficile*).

**Best Tier 2 evidence.** Systematic reviews and umbrella reviews on diet–microbiome interactions (e.g., reviews in *Gut*, *Nature Reviews Gastroenterology & Hepatology*) consistently find: (1) diet shapes the microbiome; (2) the microbiome modulates host metabolism; (3) **the predictive accuracy of consumer-test microbial signatures for individual food recommendations is not yet validated to the level required for clinical or commercial recommendation.**

**Representative Tier 3 evidence.**

- [Zeevi et al. 2015, *Cell*](https://doi.org/10.1016/j.cell.2015.11.001) — n = 800 Israeli adults, demonstrated that an algorithm combining microbiome + clinical + dietary features predicted postprandial glucose responses substantially better than carbohydrate counting. Validation cohort n = 100. Foundational Weizmann / Segal-lab paper. Tier 3 (cohort + intervention sub-study). Strong evidence for *predictive variability*; weaker evidence that following the algorithm's recommendations improves long-term outcomes.
- [Mendes-Soares et al. 2019, *JAMA Network Open*](https://doi.org/10.1001/jamanetworkopen.2018.8102) — US replication of Zeevi-style postprandial glucose prediction (Mayo Clinic + Segal collaboration), n = 327, replicated the model's improvement over carbohydrate counting in a US population. Tier 3 (cohort).
- [Asnicar et al. 2021](https://doi.org/10.1038/s41591-020-01183-8) — see PREDICT block; identifies microbiome panels associated with cardiometabolic markers cross-sectionally.

**Tier 4 marketing-vs-evidence gap.** Substantial.

- **Viome** markets "food-as-medicine" recommendations derived from gut microbial RNA sequencing, including condition-specific claims (oral health, immunity, longevity). Independent peer-reviewed validation of Viome's specific food-recommendation engine against hard outcomes is sparse; most published Viome work is Tier 4 (vendor whitepapers, conference abstracts) or analytical-validation papers about the assay itself rather than clinical-outcome RCTs.
- **DayTwo** (commercial spin-out from the Zeevi/Segal work) has stronger upstream science but consumer-facing predictive performance for outcomes beyond postprandial glucose is less established. DayTwo's commercial focus has shifted toward T2D management contexts in partnership with payers.
- **uBiome** ceased operations after federal investigations (2019), illustrating both the regulatory fragility of the consumer-microbiome category and the gap between marketed clinical utility and validated evidence.
- General gap: vendor marketing implies actionable per-food recommendations; published evidence supports *predictive variability* (Zeevi, Mendes-Soares) but not *long-term outcome benefit from following the recommendations*.

**Steel-man counter-evidence.** Microbiome composition is highly variable day-to-day, person-to-person, and across collection methods; reproducibility of consumer-test outputs across vendors is poor. Reviews comparing the recommendations from different consumer microbiome services for the same person have repeatedly found contradictory recommendations — strong evidence the per-food advice is not yet reliable. Population-level fiber and plant-diversity guidance (which all consumer microbiome tests effectively converge on at the population level) is well-supported by Tier 1/2 evidence without any test required.

**Verdict.** **Educational-content-only.** Microbiome-based per-food personalization does not meet the floor for system behavior. NutriMe surfaces the topic honestly: the underlying Zeevi/Mendes-Soares glucose-prediction work is real Tier 3 science; consumer-product extension to "eat these foods, avoid those" outpaces the evidence; the population-level recommendation that emerges from the science (eat diverse plants, plenty of fiber, fermented foods within reason) does not require a stool test.

**N-of-1 / feedback-loop relevance.** The Zeevi/Mendes-Soares findings reinforce that **postprandial response is individual** — same lesson as PREDICT, derived from a different substrate. Reinforces that semantic feedback ("this meal made me feel sluggish / energized") is a defensible per-person signal even where instrumented postprandial measurement is not in scope.

### D. Nutrigenomics (DNAFit, Nutrigenomix, 23andMe-derived diets)

**What it claims.** Common genetic variants (FTO, MTHFR, APOE, MCM6/LCT, CYP1A2, etc.) predict individual dietary needs at sufficient effect size to ground prescriptive food recommendations.

**Best Tier 1 evidence.** None. Lactase persistence (MCM6 / LCT) and a small number of inborn errors of metabolism (PKU, hereditary fructose intolerance) are the well-established cases where a genetic variant has direct dietary implications — these are clinical, monogenic, and not what consumer nutrigenomics products primarily address. For the common variants the consumer products test (FTO obesity-association, APOE saturated-fat-response, MTHFR folate metabolism, CYP1A2 caffeine metabolism), no consensus body recommends genotype-based diet personalization for the general population.

**Best Tier 2 evidence.** Several systematic reviews / meta-analyses have specifically examined whether common-variant nutrigenomic personalization changes outcomes. Findings are consistently underwhelming. The Food4Me result (Celis-Morales 2017) — that adding genotype information did not improve outcomes beyond phenotype-based personalization — is the load-bearing finding here. Subsequent reviews on FTO-genotype-tailored diets (e.g., re analyses pooling weight-loss trials) generally find no gene-by-diet interaction at clinically meaningful effect sizes for the FTO × macronutrient question.

**Representative Tier 3 evidence.** Many small RCTs of genotype-guided diets exist; effect sizes are typically small and inconsistent. Notable example: [Gardner et al. 2018, *JAMA* (DIETFITS)](https://doi.org/10.1001/jama.2018.0245) — pre-specified analysis of whether a small genotype panel (FTO, PPARG, ADRB2) predicted weight loss on low-fat vs. low-carb diets in n = 609 adults over 12 months; **no significant gene-by-diet interaction** was found.

**Tier 4 marketing-vs-evidence gap.** Large.

- **DNAFit, Nutrigenomix, and "DNA diet" services** market personalized macro splits, food sensitivities, and exercise-type recommendations from genotype panels. Independent peer-reviewed validation of clinical outcome benefit is sparse to absent.
- **23andMe-derived diet apps** repackage 23andMe raw data into food recommendations using algorithms whose construct validity is rarely externally audited.
- The marketing premise — your DNA tells you what to eat — collides with the published evidence (Food4Me, DIETFITS) that for common variants, the effect sizes are too small and the personalization adds little to phenotype-based advice.

**Steel-man counter-evidence.** Food4Me (Celis-Morales 2017) and DIETFITS (Gardner 2018) are the steel-men. Both are well-designed studies that explicitly tested whether common-variant genotype information added value, and both found it did not. Population-level dietary guidance does not require a genotype panel and produces equivalent or better outcomes in head-to-head comparison.

**Verdict.** **Educational-content-only**, leaning toward strongly cautionary framing. NutriMe surfaces the topic honestly: monogenic clinical conditions where genetics matters dietarily exist (and are under clinical care, not consumer-product care); for common variants and the general population, the evidence does not support genotype-driven food recommendations beyond phenotype-based personalization. NutriMe never gates or defaults on consumer-nutrigenomic data.

**N-of-1 / feedback-loop relevance.** Limited direct relevance. Indirectly: the nutrigenomics literature is the strongest cautionary example in the audit of marketing outpacing evidence — it informs the audit-as-education tone NutriMe takes throughout.

### E. Metabolomics-based personalization (InsideTracker, blood-biomarker-driven diets)

**What it claims.** Routine and extended blood biomarker panels (lipids, glucose, HbA1c, vitamins, ferritin, hsCRP, hormones, sometimes broader metabolomics) can be combined into per-user "optimal range" targets that drive personalized food and supplement recommendations.

**Best Tier 1 evidence.** Population-level reference ranges and clinical decision thresholds for individual biomarkers (LDL-C, HbA1c, ferritin, 25(OH)D, etc.) are Tier 1 — these come from ATP/AHA, ADA, NICE, NASEM, and similar bodies. **The Tier 1 evidence supports the individual biomarker thresholds; it does not endorse vendor algorithms that combine many biomarkers into composite "optimization" recommendations.**

**Best Tier 2 evidence.** Systematic reviews on broad-panel "wellness" blood testing in asymptomatic adults (multiple sources, including CTFPHC and USPSTF guidance on screening) generally find limited evidence of net benefit and meaningful risk of false positives, overdiagnosis, and downstream cascades. The clinical biomarker → dietary intervention chain is well-established for specific deficiencies (iron, B12, vitamin D in deficient individuals); the broad-panel "InsideTracker-style optimization" pattern lacks systematic-review-grade evidence of long-term benefit.

**Representative Tier 3 evidence.** Specific individual chains are well-supported (e.g., iron supplementation and dietary heme iron in confirmed deficiency anemia; B12 in confirmed deficiency; vitamin D intervention trials). Composite "optimize all biomarkers via foods + supplements" recommendations as a unified intervention have minimal RCT support at the algorithm level.

**Tier 4 marketing-vs-evidence gap.** InsideTracker and similar services package legitimate biomarker thresholds (Tier 1) inside proprietary "optimization zones" and food-recommendation engines whose algorithm-level validation is largely Tier 4 (vendor whitepapers). The Tier 1 underpinnings give the products a veneer of medical legitimacy that the algorithm layer has not earned.

**Steel-man counter-evidence.** For asymptomatic adults, the evidence base for repeated broad-panel biomarker testing driving food choices is thin. Population-level dietary patterns address most micronutrient adequacy without requiring individual biomarker testing for the average user. Where deficiencies are clinically suspected, standard medical workup (which NutriMe defers to via [Rule 1](../00-meta/constitutional-rules.md#rule-1--consult-a-professional)) is the appropriate path — not a consumer wellness algorithm.

**Verdict.** **Educational-content-only for vendor algorithms; component biomarker thresholds (Tier 1) drive system behavior in the limited cases where the user uploads clinically obtained labs and a Tier 1 threshold is implicated.** NutriMe does not order, recommend, or interpret broad consumer-grade biomarker panels. Where a user provides clinically validated labs (via doctor portal, user upload), system response is grounded in the Tier 1 reference range for that specific biomarker, with [Rule 1](../00-meta/constitutional-rules.md#rule-1--consult-a-professional) language directing the user back to their clinician for interpretation.

**N-of-1 / feedback-loop relevance.** Limited. Reinforces that *clinically obtained* biomarker data, when present, is a higher-fidelity input than consumer-test biomarker panels — a useful distinction for the [epistemic trail](../00-meta/epistemic-trail.md) (provenance: "lab obtained via clinician via accredited lab" is treated differently from "consumer panel ordered from website").

### F. CGM-for-non-diabetics (Levels, Nutrisense, Stelo / Dexcom OTC, Lingo)

> Stretch goal at reference level only — included because it overlaps PREDICT/ZOE and because the consumer category has expanded since FDA OTC clearance of Stelo (2024) and Lingo (2024).

**What it claims.** Continuous glucose monitoring in non-diabetic adults reveals "glucose spikes" that vary individual to individual; minimizing spikes via meal personalization improves metabolic health, energy, and long-term outcomes.

**Best Tier 1 evidence.** None for CGM use in non-diabetics for general wellness or weight management. ADA and similar bodies endorse CGM for diabetes (T1D, T2D on insulin, gestational diabetes in specific contexts). No consensus body endorses CGM for healthy adults to drive food choices.

**Best Tier 2 evidence.** Systematic reviews on CGM for non-diabetic adults consistently find: (1) glucose response variability between individuals to identical meals is real (PREDICT etc.); (2) evidence that minimizing postprandial glucose excursions in non-diabetic adults improves long-term cardiometabolic outcomes is weak to absent; (3) potential harms include disordered-eating reinforcement, false-positive worry, and unnecessary food restriction.

**Representative Tier 3 evidence.** PREDICT-1 (Berry 2020), Zeevi 2015, Mendes-Soares 2019, Hall et al. (Stanford CGM-in-prediabetes work) characterize the variability. RCTs of "follow your CGM" interventions in non-diabetic adults with hard-outcome (CVD events, T2D incidence, mortality) endpoints are essentially nonexistent at training cutoff. Self-reported energy and behavior outcomes from short trials (e.g., parts of the ZOE METHOD trial) exist; long-term metabolic-disease prevention does not.

**Tier 4 marketing-vs-evidence gap.** Substantial. Levels, Nutrisense, Stelo (Dexcom's OTC Stelo, FDA-cleared 2024 for non-diabetic adults), Lingo (Abbott's wellness CGM, FDA OTC 2024) all market metabolic-health benefits, energy, weight management, and longevity narratives that outpace published evidence. The vendors generally reference PREDICT-style variability findings as a foundation, then make claims about long-term outcomes that the variability findings do not support.

**Steel-man counter-evidence.** Non-diabetic glucose excursions remain in narrow physiological ranges; equating non-diabetic post-meal spikes with the pathological excursions of diabetes is a category error. Several published commentaries (e.g., in *BMJ*, *JAMA Internal Medicine*) have warned about CGM-as-wellness-product overreach and disordered-eating risk. Population-level guidance (fiber, whole foods, regular meals, physical activity, sleep) addresses postprandial glycemic stability without requiring instrumentation.

**Verdict.** **Educational-content-only.** NutriMe does not gate or default on CGM data, even where users present it. Where users opt to share CGM data, the system treats it under the [epistemic trail](../00-meta/epistemic-trail.md) as a [Rule 6 local-where-possible](../00-meta/constitutional-rules.md#rule-6--health-data-stays-local-where-possible) input with explicit low-confidence framing for any inference, and applies [Rule 1](../00-meta/constitutional-rules.md#rule-1--consult-a-professional) language. **For users with diagnosed diabetes, CGM interpretation is firmly out-of-scope** — that is medical care, not wellness app territory. Specific [sweep #10 (clinical condition gating)](../10-clinical-condition-gating/scope.md) considerations apply.

**N-of-1 / feedback-loop relevance.** CGM-driven personalization is in some respects the instrumented version of NutriMe's semantic feedback loop — both treat the individual as their own experiment. The CGM literature's main lesson for NutriMe: instrumented per-meal measurement may give precise per-meal data, but the long-term outcome evidence for following that data is weak. This *strengthens* the case for NutriMe's semantic-feedback approach — cheaper, less invasive, less likely to drive disordered eating, and not making any stronger outcome claim than the instrumented version can support.

### G. N-of-1 study designs in nutrition

**What it claims.** Single-subject (n-of-1) trial designs — repeated within-person crossover of dietary or behavioral exposures with washout periods and pre-specified outcomes — can produce per-person inference where between-person heterogeneity makes group-level trials insensitive.

**Best Tier 1 evidence.** N-of-1 trials are recognized as a valid evidence type in the OCEBM levels of evidence and in CONSORT extensions ([CONSORT Extension for N-of-1 Trials, CENT 2015](https://doi.org/10.1136/bmj.h1738)). Guidance documents exist for design and reporting.

**Best Tier 2 evidence.** Systematic reviews of n-of-1 trials in nutrition specifically are sparse but growing (e.g., Schork and Goetz on personalized medicine and n-of-1; Potter, Vlaev, and others on behavior-change n-of-1 designs). The methodology is more developed in pharmacology and chronic-pain management than in nutrition — but the conceptual and statistical apparatus transfers.

**Representative Tier 3 evidence.**

- [Schork 2015, *Nature*](https://doi.org/10.1038/520609a) — landmark commentary arguing for n-of-1 trials as personalized-medicine infrastructure.
- Series of n-of-1 papers in chronic disease management (sleep, pain, hypertension) that demonstrate the methodology.
- Nutrition-specific n-of-1 work is emerging in postprandial-glucose response (using CGM as repeated within-person measurement), in IBS / FODMAP elimination–reintroduction protocols (which are essentially structured n-of-1 designs in clinical practice), and in food-symptom journaling with statistical aggregation.

**Tier 4 / methodological gap.** Most consumer wellness apps run de facto n-of-1 experiments without the design rigor (no washout, no pre-specified outcome, no blinding, no statistical aggregation). The result is causal claims ("dairy makes me bloated") that may be correct but are not validated to a level that would survive an n-of-1 design audit.

**Steel-man counter-evidence.** For most dietary questions of interest (long-term cardiovascular health, T2D prevention, cognitive aging), n-of-1 designs are infeasible because the outcomes are slow and the reversibility assumption is violated. N-of-1 is well-suited to *symptomatic* outcomes (energy, digestion, sleep that night, headache, joint pain) and poorly suited to *long-term disease* outcomes. This is a real boundary on its applicability.

**Verdict.** **Drives system behavior at the design-philosophy level**, not as a clinical claim. NutriMe's [semantic feedback loop](../00-meta/intake-pattern.md#mode-3--passive-confirmation--semantic-feedback) is essentially an informal n-of-1 framework. The n-of-1 literature provides:

- Methodological guardrails (need washout / repeat-exposure for confident inference)
- Honest framing about which outcomes the loop can and cannot support inference about (energy, fullness, digestion: yes; CVD risk: no)
- Statistical context for how many "exposures" are needed before a per-person pattern is more than anecdote (typically 3+ matched repeats)
- A vocabulary for the [epistemic trail](../00-meta/epistemic-trail.md) when surfacing per-user inferences ("this is suggestive based on N matched exposures, not conclusive")

This domain is unique in the audit: **the methodology drives system behavior even where its commercial extensions do not.**

**N-of-1 / feedback-loop relevance.** Direct and load-bearing — this is the formal grounding for the entire semantic feedback loop. Recommended follow-on: a sub-sweep on n-of-1 statistical aggregation and pre-specification, particularly the CENT reporting guideline, to inform feedback-loop design specifics.

### H. Steel-man counter-evidence (the case that personalization adds little over good population guidance)

**What the steel-man claims.** Adherence to well-validated population-level dietary patterns (Mediterranean, DASH, Nordic, Eatwell Guide, prudent omnivorous diets) produces the bulk of attainable cardiometabolic and longevity benefit. Personalization mechanisms — microbiome, genotype, biomarker, CGM — add at most modest incremental benefit, and may distract from adherence to the population-level basics.

**Best Tier 1 evidence.** Population-level dietary pattern evidence is the strongest in nutrition.

- **PREDIMED** (Estruch et al., NEJM) — Mediterranean diet plus extra-virgin olive oil or nuts produced ~30% reduction in major CVD events vs. low-fat control in primary CVD-prevention RCT.
- **DASH** trials (Appel et al. 1997 NEJM; Sacks et al. 2001 NEJM) — DASH dietary pattern reduces blood pressure substantially.
- **DPP** (Diabetes Prevention Program, Knowler et al. 2002 NEJM) — lifestyle intervention (general dietary guidance + activity) reduces T2D incidence by 58% in high-risk adults.
- These are flagship population-level dietary intervention trials with hard endpoints.

**Best Tier 2 evidence.**

- [Beresford et al. 2006, *JAMA*](https://doi.org/10.1001/jama.295.6.643) — Women's Health Initiative dietary modification trial (low-fat dietary pattern), n = 48,835 postmenopausal women, 8.1 years follow-up. **Did not significantly reduce invasive breast cancer, colorectal cancer, or CVD events.** Frequently cited as evidence that even large, well-resourced dietary interventions struggle to demonstrate hard-endpoint benefit when (a) the intervention dietary pattern is suboptimally chosen and (b) baseline diet quality is already moderate. Important context: WHI tested a *low-fat* pattern, not a Mediterranean / DASH pattern — its negative result is more an indictment of the specific tested pattern than of dietary intervention generally. Cited in the scope as a steel-man against personalization-on-top-of-anything; honest reading is closer to "even big trials of the wrong pattern don't move hard endpoints, so be humble about claiming hard-endpoint benefit from personalization layered on top."
- Cochrane reviews of Mediterranean-pattern interventions (Rees et al., updated multiple times) show consistent intermediate-marker and event benefit.
- Systematic reviews of personalized-nutrition interventions (Jinnette 2021 *Adv Nutr* and similar) consistently find personalization improves *short-term dietary score adherence* but evidence of long-term hard-outcome benefit beyond population guidance is lacking.

**Representative Tier 3 evidence.** Many; the population-pattern evidence base is the deepest in the field.

**Tier 4 dimension.** Vendor marketing in personalized nutrition rarely engages with the population-pattern steel-man head-on. The honest synthesis is that *adherence is the bottleneck*, and personalization may help adherence — but the claim is "personalization helps adherence to good guidance," not "personalization replaces good guidance."

**Verdict.** **Drives system behavior** — population-level patterns (Mediterranean, DASH, Nordic, prudent / culturally adapted equivalents) are the foundation of NutriMe's recommendations. Personalization mechanisms not meeting the floor are surfaced as audit-as-education content, with the steel-man framing made explicit.

**N-of-1 / feedback-loop relevance.** The steel-man clarifies what the feedback loop is and is not for. The loop is for: per-person symptomatic and preference signal that informs *what specific foods within a good pattern to surface*. The loop is not for: claiming personalized cardiovascular benefit beyond what adherence to a Mediterranean / DASH / Nordic pattern would produce.

### I. International initiatives

#### I.1 European Union — Horizon programs (Food4Me, NutriTech, Stance4Health, PROMINENT, others)

EU-funded research has been the engine of much published personalized-nutrition science:

- **Food4Me** (FP7) — see Section B.
- **NutriTech** (FP7) — methodological work on combining biomarker, metabolomic, and dietary-assessment technologies.
- **Stance4Health** (Horizon 2020) — personalized nutrition + microbiome + mobile-app delivery, including for special populations (children with obesity, celiac, lactose-intolerant).
- **PROMINENT** (Horizon Europe) — multi-omic personalized nutrition for non-communicable disease prevention.
- The European Nutrigenomics Organization (NuGO) coordinates much of this work academically.

Trajectory: EU work emphasizes (a) multi-modal personalization (not just one omic layer), (b) public-funding rigor with phenotype-vs-genotype comparison built in (Food4Me's null-on-genotype finding is characteristic), and (c) outcome breadth (dietary behavior, biomarkers, eventually long-term disease).

#### I.2 United Kingdom — NHS, NIHR, Biobank, ZOE PREDICT collaboration

- **PREDICT** is a UK-Israel-US collaboration with major UK academic involvement (King's College London / Tim Spector group).
- **UK Biobank** (n ≈ 500,000) provides the substrate for many genotype × diet × outcome studies, including replication of nutrigenomic and gene-by-diet interaction findings (typically null at meaningful effect size for common variants).
- **NHS personalized nutrition pilots** are limited and tend to focus on specific clinical contexts (T2D remission via low-energy diets, e.g., DiRECT and Counterweight-Plus) rather than consumer-grade personalization. **DiRECT** (Lean et al. *Lancet* 2018 / 2019) demonstrated T2D remission via population-level intervention (low-energy total-diet replacement followed by structured food reintroduction) — notable for being a non-personalized intervention with strong individual outcomes.
- The UK Government's Office for Science published a personalized-nutrition foresight report (mid-2020s) calling for stronger evidence before NHS adoption.

#### I.3 Israel — Weizmann Institute, Eran Segal lab

- The Segal/Elinav group at Weizmann is the originating center for the microbiome-driven postprandial-glucose-prediction line of work ([Zeevi 2015](https://doi.org/10.1016/j.cell.2015.11.001)) and a major collaborator on PREDICT and the Mendes-Soares Mayo replication.
- Spinout: **DayTwo** (commercial application of the Segal-lab algorithms for T2D management).
- Continues to publish foundational microbiome-and-metabolism work; lab output is among the most-cited in the personalized-nutrition field.

#### I.4 United States — NIH "Nutrition for Precision Health" (2022–2030)

- The NIH **Nutrition for Precision Health (NPH)** program, funded under the *All of Us* Research Program, is a ~$170M, 10,000-participant initiative (announced 2022, recruitment ongoing through the late 2020s) to study individual responses to dietary intervention combining multi-omic, microbiome, CGM, wearable, and dietary-pattern data. Results will materialize across the late 2020s and into the 2030s.
- USDA's **2020–2025 Dietary Guidelines** took the population-level view; precision nutrition acknowledged as research-stage, not policy-stage. The **2025–2030 edition was released 2026-01-07** (realfood.gov) — it keeps the population-level posture (no precision-nutrition shift) but departs substantially from the 2020–2025 patterns elsewhere (protein emphasis 1.2–1.6 g/kg/d, full-fat dairy, new pyramid graphic); its advisory-committee report was partly set aside in the final document, so pattern-level claims sourced to "the current DGA" need rechecking against the 2025–2030 text.

#### I.5 China — Chinese Nutrition Society precision-nutrition initiatives

- The **Chinese Nutrition Society** has published precision-nutrition position statements emphasizing integration with traditional Chinese medicine constitutional typing and large-cohort phenomics.
- Chinese cohorts (China Kadoorie Biobank, n ≈ 500,000) are increasingly used for nutrigenomic and gene-by-diet analyses, with growing Chinese-language and bilingual publications.
- BGI and related Chinese biotech players have entered the consumer microbiome space; published outcome evidence is comparable to the global state of the art (i.e., variability findings, weak outcome evidence).

#### I.6 Japan, Korea — population-cohort work

- Japan's long-running cohorts (JPHC, Hisayama, Ohsaki) inform nutrient intake-disease association evidence at population scale; precision-nutrition consumer products are present but smaller than the cohort-driven academic work.
- Korea's Samsung Health ecosystem and KoGES cohort similarly contribute population-cohort precision-nutrition evidence; consumer personalized-nutrition product market is comparatively small.

#### I.7 Australia, New Zealand, Canada

- **NHMRC** (Australia) and **Health Canada** treat personalized nutrition similarly to NHS / NASEM — research-stage, not standard-of-care.
- Australian work on precision-nutrition for athletic populations and indigenous-population dietary patterns is notable but scoped narrowly.

**Convergence vs. divergence.** Across regions, the broad picture is **converging**: large public-funded cohorts characterize per-person variability; outcome RCTs are sparse and modest; consensus bodies hold the population-pattern line; consumer-vendor marketing globally outpaces evidence by similar margins. EU work is the most methodologically rigorous in directly comparing personalization tiers (Food4Me's phenotype-vs-genotype comparison is the global standard). US NPH will be the next major outcome-evidence inflection point in the late 2020s / early 2030s.

**Verdict (international).** Equal-weighted under [Rule 9](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing): the global state of evidence is reasonably homogeneous across regions and supports the same audit-as-education framing.

### Summary table

| Domain | Best Tier 1 | Best Tier 2 | Representative Tier 3 | Marketing gap | Steel-man | Verdict |
|---|---|---|---|---|---|---|
| PREDICT / ZOE | None | Limited; no Cochrane | Berry 2020; Asnicar 2021; Bermingham 2024 | Long-term outcome claims unproven | PREDIMED Mediterranean evidence | Educational-content-only |
| Food4Me | None | Jinnette 2021 *Adv Nutr* | Celis-Morales 2017 | "DNA tells you what to eat" — Food4Me showed it didn't | PREDIMED, DASH | Educational-content-only |
| Microbiome (Viome/ZOE/DayTwo) | None | Diet-microbiome reviews; cautionary AGA | Zeevi 2015; Mendes-Soares 2019 | Per-food recs outpace evidence; cross-vendor disagreement | Population fiber/diversity guidance | Educational-content-only |
| Nutrigenomics (DNAFit/Nutrigenomix/23andMe diets) | Monogenic only (PKU, lactase) | Reviews finding null gene-by-diet | Celis-Morales 2017; Gardner DIETFITS 2018 | Genotype-driven recs without effect | Food4Me, DIETFITS null findings | Educational-content-only (cautionary) |
| Metabolomics (InsideTracker etc.) | Individual biomarker thresholds Tier 1 | USPSTF / CTFPHC on broad screening | Specific deficiency-correction RCTs | Algorithm-level claims unvalidated | Asymptomatic broad-panel screening risk | Component thresholds drive behavior; vendor algorithms educational-only |
| CGM-non-diabetics (Levels/Nutrisense/Stelo/Lingo) | None for non-diabetics | Reviews finding weak outcome evidence + harm risk | Berry 2020; Hall et al.; Zeevi 2015 | Long-term claims, energy/longevity narratives | Non-diabetic excursions are physiological; disordered-eating risk | Educational-content-only |
| N-of-1 design | CENT 2015 reporting standard | Schork commentary; methodological reviews | Domain-specific n-of-1 RCT series | Consumer "experiments" without rigor | Long-term outcomes not addressable | Drives feedback-loop design philosophy |
| Steel-man (population-pattern) | PREDIMED, DASH, DPP | Cochrane Mediterranean reviews | Many | Vendors avoid this comparison | Adherence is the bottleneck | Drives system behavior (population patterns are the floor) |
| International initiatives | Per region | Per region | Food4Me, PREDICT, NPH (forthcoming) | Vendor marketing global, similar gap | Population-pattern evidence equally global | Equal-weighted per Rule 9 |

### Open questions, answered

> *For each domain: best Tier 2 evidence? Any Tier 1?*

Detailed per domain above. Headline: **no Tier 1 consensus-body endorsement of any consumer-grade personalization mechanism for general adults.** Tier 2 systematic-review evidence is mostly limited to short-term dietary-score improvement, not hard endpoints.

> *Strongest published steel-man against personalization?*

The combination of: (a) PREDIMED / DASH / DPP demonstrating large effects from population-pattern adherence with hard endpoints; (b) Food4Me (Celis-Morales 2017) showing genotype information did not add value beyond phenotype; (c) Gardner DIETFITS (2018) showing no gene-by-diet interaction for FTO/PPARG/ADRB2 on weight loss. Together these argue: most attainable benefit comes from adherence to known-good patterns; personalization improves adherence at best, does not replace the patterns, and does not yet have hard-endpoint validation of incremental benefit.

> *Does CGM-driven personalization translate to meaningful long-term outcomes in non-diabetics?*

At training cutoff: **not demonstrated.** Variability is real (PREDICT, Zeevi, Mendes-Soares); short-term self-reported and biomarker improvements exist (ZOE METHOD); long-term hard-endpoint RCTs in non-diabetic adults are essentially absent. Specific harm signals (disordered-eating reinforcement, false-positive worry) are documented in commentary literature.

> *N-of-1 designs and the semantic feedback loop?*

The CENT 2015 reporting standard provides design guardrails. Key transfers to NutriMe's loop: (a) need for repeat exposures before claiming a per-person pattern (typically 3+); (b) explicit acknowledgement that the loop can support inference about symptomatic / experiential outcomes (energy, fullness, sleep that night, digestion) but not long-term disease outcomes; (c) the loop must be honest that "this is suggestive based on N matched exposures" is not a clinical finding. Recommend follow-on micro-sweep on CENT and n-of-1 statistical aggregation specifically for feedback-loop design.

> *EU Horizon trajectory — converging or diverging from US/UK?*

Converging on the methodological frame (multi-modal personalization, phenotype-as-baseline-comparator, public-funded cohort substrate). The biggest difference: EU has historically been more willing to publish null findings on genotype-based personalization; US consumer market is more vendor-driven. US NPH (under *All of Us*) will be the convergence point for the late-2020s / 2030s evidence base.

> *Where exactly does microbiome / nutrigenomic / metabolomic marketing diverge from evidence?*

- **Microbiome:** vendors claim per-food actionable recommendations; published evidence supports per-person variability and population-level fiber/diversity guidance, not vendor-specific per-food rules. Cross-vendor disagreement on the same stool sample is the cleanest indictment.
- **Nutrigenomics:** vendors claim genotype-driven diet plans; Food4Me and DIETFITS specifically tested this and found no incremental value beyond phenotype-based personalization for common variants.
- **Metabolomics:** Tier 1 individual biomarker thresholds get repackaged in Tier 4 vendor "optimization" algorithms whose composite recommendations lack independent validation. Asymptomatic broad-panel testing in healthy adults is itself questioned by guideline bodies.

### Implications for NutriMe system design

1. **Population-level dietary patterns** (Mediterranean, DASH, Nordic, prudent / culturally adapted equivalents) are the recommendation foundation. Personalization layers *on top of* this floor; it does not replace it.
2. **Phenotype-based personalization** (rich iterative intake + preferences + clinical history + semantic feedback) is empirically defensible per Food4Me as the personalization substrate — and is what NutriMe already does.
3. **Genotype, microbiome, broad metabolomic, and CGM data** do not gate or default any system behavior. Where users present such data, it is treated as context under the [epistemic trail](../00-meta/epistemic-trail.md) with explicit low-confidence framing and [Rule 1](../00-meta/constitutional-rules.md#rule-1--consult-a-professional) language.
4. **Audit-as-education content** for each of these mechanisms is a first-class deliverable — explaining what they claim, what the evidence shows, why NutriMe does or does not use them. The Findings above are structured to be source material for that user-facing content.
5. **The semantic feedback loop is grounded in n-of-1 methodology** — formally enough that CENT reporting principles (washout, repeated exposures, pre-specified outcomes, honest confidence framing) should inform its detailed design in a follow-on sweep.
6. **Hard-endpoint claims** are reserved for population-pattern Tier 1 evidence; personalization claims at the system level are limited to "improves preference fit, supports adherence, surfaces lived-experience patterns" — never to long-term disease-outcome claims.

## References

> Citations follow [citation-style.md](../00-meta/citation-style.md). Accessed-on date `2026-04-29` reflects this audit's assembly date; URLs are stable identifiers (DOI / canonical journal landing pages) verified against the assistant's training corpus rather than re-fetched live in this session — see epistemic note at the top of Findings.

### Peer-reviewed literature (Tier 1, 2, 3)

- Appel, L.J., Moore, T.J., Obarzanek, E., Vollmer, W.M., Svetkey, L.P., Sacks, F.M., Bray, G.A., Vogt, T.M., Cutler, J.A., Windhauser, M.M., Lin, P.H., & Karanja, N. (1997). A clinical trial of the effects of dietary patterns on blood pressure (DASH). *New England Journal of Medicine*, 336(16), 1117–1124. https://doi.org/10.1056/NEJM199704173361601. Accessed 2026-04-29.
- Asnicar, F., Berry, S.E., Valdes, A.M., Nguyen, L.H., Piccinno, G., Drew, D.A., Leeming, E., Gibson, R., Le Roy, C., Khatib, H.A., Francis, L., Mazidi, M., Mompeo, O., Valles-Colomer, M., Tett, A., Beghini, F., Dubois, L., Bazzani, D., Thomas, A.M., Mirzayi, C., ... Segata, N., & Spector, T.D. (2021). Microbiome connections with host metabolism and habitual diet from 1,098 deeply phenotyped individuals. *Nature Medicine*, 27(2), 321–332. https://doi.org/10.1038/s41591-020-01183-8. Accessed 2026-04-29.
- Beresford, S.A.A., Johnson, K.C., Ritenbaugh, C., Lasser, N.L., Snetselaar, L.G., Black, H.R., Anderson, G.L., Assaf, A.R., Bassford, T., Bowen, D., Brunner, R.L., Brzyski, R.G., Caan, B., Chlebowski, R.T., Gass, M., Harrigan, R.C., Hays, J., Heber, D., Heiss, G., ... Prentice, R.L. (2006). Low-fat dietary pattern and risk of colorectal cancer: the Women's Health Initiative randomized controlled dietary modification trial. *JAMA*, 295(6), 643–654. https://doi.org/10.1001/jama.295.6.643. Accessed 2026-04-29.
- Bermingham, K.M., Linenberg, I., Polidori, L., Asnicar, F., Arrè, A., Wolf, J., Badri, F., Bernard, H., Capdevila, J., Bulsiewicz, W.J., Gardner, C.D., Ordovas, J.M., Davies, R., Hadjigeorgiou, G., Hall, W.L., Delahanty, L.M., Valdes, A.M., Segata, N., Spector, T.D., & Berry, S.E. (2024). Effects of a personalized nutrition program on cardiometabolic health: a randomized controlled trial (the ZOE METHOD study). *Nature Medicine*, 30(7), 1888–1897. https://doi.org/10.1038/s41591-024-02951-6. Accessed 2026-04-29.
- Berry, S.E., Valdes, A.M., Drew, D.A., Asnicar, F., Mazidi, M., Wolf, J., Capdevila, J., Hadjigeorgiou, G., Davies, R., Al Khatib, H., Bonnett, C., Ganesh, S., Bakker, E., Hart, D., Mangino, M., Merino, J., Linenberg, I., Wyatt, P., Ordovas, J.M., ... Spector, T.D. (2020). Human postprandial responses to food and potential for precision nutrition. *Nature Medicine*, 26(6), 964–973. https://doi.org/10.1038/s41591-020-0934-0. Accessed 2026-04-29.
- Celis-Morales, C., Livingstone, K.M., Marsaux, C.F.M., Macready, A.L., Fallaize, R., O'Donovan, C.B., Woolhead, C., Forster, H., Walsh, M.C., Navas-Carretero, S., San-Cristobal, R., Tsirigoti, L., Lambrinou, C.P., Mavrogianni, C., Moschonis, G., Kolossa, S., Hallmann, J., Godlewska, M., Surwiłło, A., ... Mathers, J.C. (Food4Me Study). (2017). Effect of personalized nutrition on health-related behaviour change: evidence from the Food4Me European randomized controlled trial. *International Journal of Epidemiology*, 46(2), 578–588. https://doi.org/10.1093/ije/dyw186. Accessed 2026-04-29.
- Estruch, R., Ros, E., Salas-Salvadó, J., Covas, M.I., Corella, D., Arós, F., Gómez-Gracia, E., Ruiz-Gutiérrez, V., Fiol, M., Lapetra, J., Lamuela-Raventos, R.M., Serra-Majem, L., Pintó, X., Basora, J., Muñoz, M.A., Sorlí, J.V., Martínez, J.A., Fitó, M., Gea, A., ... Martínez-González, M.A. (PREDIMED Study Investigators). (2018). Primary prevention of cardiovascular disease with a Mediterranean diet supplemented with extra-virgin olive oil or nuts. *New England Journal of Medicine*, 378(25), e34. https://doi.org/10.1056/NEJMoa1800389. Accessed 2026-04-29.
- Gardner, C.D., Trepanowski, J.F., Del Gobbo, L.C., Hauser, M.E., Rigdon, J., Ioannidis, J.P.A., Desai, M., & King, A.C. (2018). Effect of low-fat vs low-carbohydrate diet on 12-month weight loss in overweight adults and the association with genotype pattern or insulin secretion: the DIETFITS randomized clinical trial. *JAMA*, 319(7), 667–679. https://doi.org/10.1001/jama.2018.0245. Accessed 2026-04-29.
- Jinnette, R., Narita, A., Manning, B., McNaughton, S.A., Mathers, J.C., & Livingstone, K.M. (2021). Does personalized nutrition advice improve dietary intake in healthy adults? A systematic review of randomized controlled trials. *Advances in Nutrition*, 12(3), 657–669. https://doi.org/10.1093/advances/nmaa144. Accessed 2026-04-29.
- Knowler, W.C., Barrett-Connor, E., Fowler, S.E., Hamman, R.F., Lachin, J.M., Walker, E.A., & Nathan, D.M. (Diabetes Prevention Program Research Group). (2002). Reduction in the incidence of type 2 diabetes with lifestyle intervention or metformin. *New England Journal of Medicine*, 346(6), 393–403. https://doi.org/10.1056/NEJMoa012512. Accessed 2026-04-29.
- Lean, M.E., Leslie, W.S., Barnes, A.C., Brosnahan, N., Thom, G., McCombie, L., Peters, C., Zhyzhneuskaya, S., Al-Mrabeh, A., Hollingsworth, K.G., Rodrigues, A.M., Rehackova, L., Adamson, A.J., Sniehotta, F.F., Mathers, J.C., Ross, H.M., McIlvenna, Y., Stefanetti, R., Trenell, M., Welsh, P., Kean, S., Ford, I., McConnachie, A., Sattar, N., & Taylor, R. (2018). Primary care-led weight management for remission of type 2 diabetes (DiRECT): an open-label, cluster-randomised trial. *Lancet*, 391(10120), 541–551. https://doi.org/10.1016/S0140-6736(17)33102-1. Accessed 2026-04-29.
- Mendes-Soares, H., Raveh-Sadka, T., Azulay, S., Edens, K., Ben-Shlomo, Y., Cohen, Y., Ofek, T., Bachrach, D., Stevens, J., Colibaseanu, D., Segal, E., Kashyap, P., & Nelson, H. (2019). Assessment of a personalized approach to predicting postprandial glycemic responses to food among individuals without diabetes. *JAMA Network Open*, 2(2), e188102. https://doi.org/10.1001/jamanetworkopen.2018.8102. Accessed 2026-04-29.
- Sacks, F.M., Svetkey, L.P., Vollmer, W.M., Appel, L.J., Bray, G.A., Harsha, D., Obarzanek, E., Conlin, P.R., Miller, E.R. 3rd, Simons-Morton, D.G., Karanja, N., Lin, P.H. (DASH-Sodium Collaborative Research Group). (2001). Effects on blood pressure of reduced dietary sodium and the Dietary Approaches to Stop Hypertension (DASH) diet. *New England Journal of Medicine*, 344(1), 3–10. https://doi.org/10.1056/NEJM200101043440101. Accessed 2026-04-29.
- Schork, N.J. (2015). Personalized medicine: time for one-person trials. *Nature*, 520(7549), 609–611. https://doi.org/10.1038/520609a. Accessed 2026-04-29.
- Vohra, S., Shamseer, L., Sampson, M., Bukutu, C., Schmid, C.H., Tate, R., Nikles, J., Zucker, D.R., Kravitz, R., Guyatt, G., Altman, D.G., & Moher, D. (CENT Group). (2015). CONSORT extension for reporting N-of-1 trials (CENT) 2015 statement. *BMJ*, 350, h1738. https://doi.org/10.1136/bmj.h1738. Accessed 2026-04-29.
- Zeevi, D., Korem, T., Zmora, N., Israeli, D., Rothschild, D., Weinberger, A., Ben-Yacov, O., Lador, D., Avnit-Sagi, T., Lotan-Pompan, M., Suez, J., Mahdi, J.A., Matot, E., Malka, G., Kosower, N., Rein, M., Zilberman-Schapira, G., Dohnalová, L., Pevsner-Fischer, M., ... Segal, E. (2015). Personalized nutrition by prediction of glycemic responses. *Cell*, 163(5), 1079–1094. https://doi.org/10.1016/j.cell.2015.11.001. Accessed 2026-04-29.

### Programs, initiatives, and consensus-body context

- **NIH** (2022). *Nutrition for Precision Health, powered by the All of Us Research Program*. National Institutes of Health, Office of Nutrition Research. https://commonfund.nih.gov/nutritionforprecisionhealth. Accessed 2026-04-29.
- **European Commission** (rolling). *Cordis — Food4Me project (FP7, grant 265494)*. European Commission Community Research and Development Information Service. https://cordis.europa.eu/project/id/265494. Accessed 2026-04-29.
- **European Commission** (rolling). *Cordis — Stance4Health project (Horizon 2020, grant 816303)*. https://cordis.europa.eu/project/id/816303. Accessed 2026-04-29.
- **NHS / Public Health England** (2016, periodically updated). *The Eatwell Guide*. https://www.nhs.uk/live-well/eat-well/food-guidelines-and-food-labels/the-eatwell-guide/. Accessed 2026-04-29.
- **USDA & HHS** (2020). *Dietary Guidelines for Americans, 2020–2025* (9th ed.). U.S. Department of Agriculture and U.S. Department of Health and Human Services. https://www.dietaryguidelines.gov. Accessed 2026-04-29. **[Superseded by the 2025–2030 edition, released 2026-01-07 (realfood.gov); #59 audit note 2026-10-08.]**
- **NHMRC** (2013, under update). *Australian Dietary Guidelines*. National Health and Medical Research Council. https://www.eatforhealth.gov.au. Accessed 2026-04-29.
- **Health Canada** (2019). *Canada's Food Guide*. https://food-guide.canada.ca. Accessed 2026-04-29.
- **WHO** (2020). *Healthy diet fact sheet*. World Health Organization. https://www.who.int/news-room/fact-sheets/detail/healthy-diet. Accessed 2026-04-29.
- **UK Biobank** (rolling). https://www.ukbiobank.ac.uk. Accessed 2026-04-29.
- **China Kadoorie Biobank** (rolling). https://www.ckbiobank.org. Accessed 2026-04-29.
- **OCEBM Levels of Evidence Working Group** (2011). *The Oxford 2011 Levels of Evidence*. https://www.cebm.ox.ac.uk/resources/levels-of-evidence/ocebm-levels-of-evidence. Accessed 2026-04-29.

### Vendor / commercial sources (Tier 4 — context only, not basis for any health claim)

> Per [Rule 7](../00-meta/constitutional-rules.md#rule-7--peer-reviewed-evidence-floor), these citations document what the vendors market. They do **not** ground any claim of effect, mechanism, or benefit. They appear here so that audit-as-education content can be honest about marketed-vs-evidenced positions.

- **ZOE Ltd.** *ZOE personalized nutrition program*. https://zoe.com. Accessed 2026-04-29. (Tier 4 — vendor; for marketed claims only. Peer-reviewed evidence is in Berry 2020, Asnicar 2021, Bermingham 2024.)
- **Viome Life Sciences**. *Viome Full Body Intelligence and food recommendations*. https://www.viome.com. Accessed 2026-04-29. (Tier 4 — vendor; independent peer-reviewed outcome validation of food-recommendation engine is sparse.)
- **DayTwo, Inc.** *DayTwo personalized nutrition for metabolic health*. https://www.daytwo.com. Accessed 2026-04-29. (Tier 4 vendor; upstream science published as Zeevi 2015 / Mendes-Soares 2019.)
- **DNAFit (a Prenetics company)**. *DNAFit nutrition and fitness reports*. https://dnafit.com. Accessed 2026-04-29. (Tier 4 vendor; effect-size and outcome evidence for genotype-driven recommendations is limited per Food4Me / DIETFITS.)
- **Nutrigenomix Inc.** *Nutrigenomix genetic test for personalized nutrition*. https://www.nutrigenomix.com. Accessed 2026-04-29. (Tier 4 vendor.)
- **InsideTracker (Segterra Inc.)**. *InsideTracker blood biomarker analysis*. https://www.insidetracker.com. Accessed 2026-04-29. (Tier 4 algorithm layer; underlying biomarker thresholds are Tier 1.)
- **Levels Health**. *Levels metabolic health program*. https://www.levelshealth.com. Accessed 2026-04-29. (Tier 4 vendor; CGM-for-non-diabetic-wellness category.)
- **Nutrisense, Inc.** *Nutrisense CGM and nutrition coaching*. https://www.nutrisense.io. Accessed 2026-04-29. (Tier 4 vendor.)
- **Dexcom, Inc.** *Stelo by Dexcom — over-the-counter glucose biosensor* (FDA cleared 2024 for adults not on insulin). https://www.dexcom.com/stelo. Accessed 2026-04-29. (Tier 4 for any wellness claim; Tier 1 device-clearance fact via FDA 510(k) record.)
- **Abbott**. *Lingo continuous glucose biosensor* (FDA cleared 2024 OTC, U.S.). https://www.hellolingo.com. Accessed 2026-04-29. (Same framing as Stelo.)
- **23andMe, Inc.** *23andMe Health + Ancestry service* (raw data subsequently used by third-party diet apps). https://www.23andme.com. Accessed 2026-04-29. (Tier 4 for downstream "DNA diet" derivations.)

### Cross-references within this repository

- [Sweep #1 (international nutrition standards)](../01-international-nutrition-standards/scope.md) — population-level pattern guidance against which personalization is measured.
- [Sweep #6 (wearable data availability)](../06-wearable-data-availability/scope.md) — sister sweep; what data exists and is reliable (substrate) vs. should-we-act-on-it (this sweep).
- [Sweep #10 (clinical condition gating)](../10-clinical-condition-gating/scope.md) — where clinical-grade biomarker / CGM use intersects with diagnosed conditions.
- [intake-pattern.md](../00-meta/intake-pattern.md) — semantic feedback loop, conceptually informed by the n-of-1 literature in this audit.
- [evidence-tiers.md](../00-meta/evidence-tiers.md) — audit-as-education pattern operationalized throughout this audit.
- [epistemic-trail.md](../00-meta/epistemic-trail.md) — provenance / verification framing applied to user-supplied biomarker, microbiome, genotype, and CGM data.
- [constitutional-rules.md](../00-meta/constitutional-rules.md) — Rules 1, 2, 6, 7, 9, 10 all bind specific verdicts in this audit.
