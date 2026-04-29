# Sweep #8 — Nutrition Education and "Why" Delivery — What Changes Behavior

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Map the literature on health literacy, behavior change frameworks, nutrition education effectiveness, plain-language clinical communication, microlearning + spaced repetition, visual + uncertainty communication, and causal explanation depth in health communication. Establish what evidence supports specific delivery patterns over others.

This sweep is **uncommonly consequential** — the [audit-as-education pattern](../00-meta/evidence-tiers.md#audit-as-education-pattern), the [epistemic trail of honesty](../00-meta/epistemic-trail.md), evidence-tier transparency, and iterative horizon-broadening all depend on knowing how to deliver explanations that actually land with users.

## Deliverable

An annotated reference map containing:

- Comparative audit of major behavior change frameworks (COM-B, TTM, HBM, SDT, HAPA, TPB) — characterized for fit against NutriMe's iterative-broadening + autonomy-supportive + convenience-driven design
- Health literacy adaptation literature, with 8th-grade-baseline + adaptive-complexity-ramping framing
- Microlearning + spaced repetition for nutrition education
- Visual / graphical communication of nutrition concepts
- Uncertainty + confidence visualization (GRADE summary-of-findings, traffic-light certainty, hedged language patterns)
- Causal explanation depth in health communication — including its verification-mechanism role per [epistemic-trail.md](../00-meta/epistemic-trail.md)
- Adult learning theory (Knowles' andragogy + adaptations)
- Trust + credibility research in AI-mediated health information
- Plain-language clinical communication (Cochrane Plain Language Summaries, NICE patient decision aids, PLAIN movement)

This is a **reference map**, not corpus build.

## In scope

### Behavior change frameworks (comparative)

- **COM-B** (Capability, Opportunity, Motivation → Behavior; Michie et al.)
- **Transtheoretical Model (TTM)** — stages of change (Prochaska & DiClemente)
- **Health Belief Model (HBM)** — perceived susceptibility, severity, benefits, barriers
- **Self-Determination Theory (SDT)** — autonomy, competence, relatedness (Ryan & Deci)
- **Health Action Process Approach (HAPA)** — motivation phase + volition phase (Schwarzer)
- **Theory of Planned Behavior (TPB)** — attitude, subjective norm, perceived control (Ajzen)
- **Capability Approach to Nutrition** (Sen-influenced, less common but relevant for autonomy framing)

For each: characterize what the framework optimizes for, evidence base for nutrition-specific application, and fit with NutriMe's iterative-broadening + convenience-driven design. Synthesis later identifies which framework(s) best inform product design.

### Health literacy adaptation

- US Adult Health Literacy data (NAAL, NAHLS) — average reading level for medical text
- International adult health literacy data (HLS-EU, HLS-EU-Q consortium, Australian Health Literacy Survey, Korean adult health literacy research, Japanese health literacy research / Nakayama lab, Chinese national health literacy initiatives, Singapore Health Promotion Board work)
- Health literacy assessment instruments (REALM-SF, TOFHLA, NVS, eHEALS for digital health)
- 8th-grade-baseline content design + readability metrics (Flesch-Kincaid, SMOG, Gunning Fog, Dale-Chall)
- **Adaptive complexity ramping** — system reads engagement signals (time-on-content, follow-up questions, depth of feedback) and ramps content depth accordingly. Same principle as iterative intake horizon-broadening, applied to education
- Adding new intake screener items per user direction: **highest education level** and **cooking literacy** (distinct from cooking confidence — literacy = knowledge of terminology/techniques/ingredients) — see [sweep #3 update](../03-clinical-nutrition-assessment/scope.md)

### Microlearning + spaced repetition

- Microlearning literature in corporate training, adapted for consumer health
- Spaced repetition for nutrition concept retention (small but growing literature)
- **Dual-purpose framing per user direction:** microlearning serves both (a) user engagement + comprehension AND (b) system forcing function — structuring delivery as small, explicitly-connected chunks forces the system to articulate the connections, which improves the system's own correlation quality. User engagement + system rigor are coupled, not independent design choices.
- Scheduling cadences (Ebbinghaus-derived, Anki-derived, Duolingo-style streak design — for inspiration, not direct copy)

### Visual / graphical communication

- Plate models (USDA MyPlate, Harvard Healthy Eating Plate, Brazilian Dietary Guidelines plate variants, Japanese spinning top)
- Icon arrays and frequency framing (Spiegelhalter, Gigerenzer)
- Comparative visuals (size comparisons, equivalence visuals, time-to-cook visuals)
- Food-as-medicine infographics (CDC, NIH, ADA patient education)
- Nutrition labeling literature (front-of-pack labels, traffic light, Nutri-Score, Health Star Rating Australia, Chilean black-octagon warnings)

### Uncertainty + confidence visualization

- GRADE summary-of-findings tables — gold standard for evidence certainty communication
- Cochrane Plain Language Summary patterns
- Traffic-light certainty indicators (NICE, others)
- Hedged-language patterns ("evidence suggests" vs. "evidence shows")
- Probability-of-effect framing (icon arrays, conditional probability visuals)
- Bayesian / posterior-belief visualization (research-stage)
- The literature on uncertainty *erosion* — when uncertainty communication reduces trust vs. when it builds trust

### Causal explanation depth

- Mechanism-explanation literature (chain-of-causation framing in health communication)
- Comparison: mechanism vs. correlation vs. authority framing — what changes behavior vs. what produces "performance of learning"
- **Verification-mechanism role** per [epistemic-trail.md](../00-meta/epistemic-trail.md) — generating the causal chain surfaces inconsistencies (yes/no flips, off-by-one numbers, contradictory premises). Education and verification are produced by the same artifact.
- Avoiding "explanation theater" — deep explanations that look authoritative but cover hand-waved reasoning

### Adult learning theory

- Knowles' andragogy (adult learning principles)
- Self-directed learning theory
- Experiential learning (Kolb)
- Transformative learning (Mezirow) — relevant to horizon-broadening
- Adult learning research specifically applied to nutrition education

### Trust + credibility in AI-mediated health information

- Small but rapidly-growing literature (post-ChatGPT)
- Credibility cues that build trust (citations, hedging, source attribution, audit trail)
- Credibility cues that erode trust (overconfidence, inconsistency, lack of provenance)
- AI-disclosure framing (when to say "this was AI-generated" + how)

### Plain-language clinical communication

- Cochrane Plain Language Summaries (UK / international, gold standard)
- NICE patient decision aids
- PLAIN (Plain Language Action and Information Network, US)
- International Plain Language Federation
- Health Communication Capacity Collaborative (USAID / Johns Hopkins)
- WHO Health Literacy Development Framework

## Geographic scope

Per [geographic-scope.md](../00-meta/geographic-scope.md). Especially notable for this sweep: **UK** (Cochrane PLS, NICE), **EU** (HLS-EU consortium), **Japan** (Nakayama lab + Tokyo Univ), **Korea** (large adult health literacy literature), **China** (national health literacy programs since 2008), **Singapore** (Health Promotion Board often cited as model). Opportunistic: **Brazil** + **India** for diverse-literacy / linguistic-pluralism context.

## Out of scope (with reasons)

- Specific UI implementation — research informs design, not design itself
- Tech stack for content delivery — deferred per project-wide rule
- Children's nutrition education — not target user
- Cooking instruction (knife skills, technique tutorials) — per [product-framing "not a cooking class" boundary](../00-meta/product-framing.md#what-nutrime-is-explicitly-not). Surfacing where to learn a technique is in scope; delivering the lesson is not.

## Open questions for the research

- For each behavior change framework: what is the evidence base for nutrition-specific application, and where does it converge / diverge from frameworks for medication adherence, exercise, smoking cessation?
- What is the strongest evidence for adaptive-complexity content delivery vs. one-level-fits-all?
- What does spaced-repetition research say about optimal cadences for nutrition concept retention specifically?
- How do GRADE-style certainty indicators land with consumer audiences (vs. clinician audiences they were designed for)?
- What is the published evidence on causal explanation changing behavior vs. producing "performance of learning"?
- What credibility cues build vs. erode trust in AI-delivered health information?
- Where does international plain-language practice converge — what's a transferable baseline vs. culture-specific?

## Cross-references

- Bound by [Constitutional Rule 7 (peer-reviewed floor)](../00-meta/constitutional-rules.md#rule-7--peer-reviewed-evidence-floor)
- Bound by [Constitutional Rule 8 (epistemic trail)](../00-meta/constitutional-rules.md#rule-8--epistemic-trail-of-honesty) — causal explanation is part of verification
- Bound by [evidence-tiers.md](../00-meta/evidence-tiers.md), especially the [audit-as-education pattern](../00-meta/evidence-tiers.md#audit-as-education-pattern)
- Cross-references [sweep #7 (cooking behavioral barriers)](../07-cooking-behavioral-barriers/scope.md) — overlapping behavior change literature
- Cross-references [sweep #3 (clinical nutrition assessment)](../03-clinical-nutrition-assessment/scope.md) — new intake items (education level, cooking literacy) added there per user direction
- Cross-references [sweep #4 (adaptive intake agent)](../04-adaptive-intake-agent/scope.md) — same adaptive-complexity-ramping principle applied to a different surface
- See [geographic-scope.md](../00-meta/geographic-scope.md) for primary research scope

## Findings

> **Epistemic note (2026-04-28).** WebSearch and WebFetch were unavailable to this sweep. Findings below are drawn from training-data knowledge of foundational and widely-replicated peer-reviewed work in behavior change, health literacy, microlearning, risk/uncertainty communication, plain-language clinical communication, and AI-mediated health information. Where a finding cites a specific edition, year, or instrument version, it should be re-verified at implementation time against the publishing body's current page or the underlying DOI. Wave 2 items most likely to need refresh: HLS19 European data (publishing 2021–2024), the rapid AI-credibility literature (post-ChatGPT growth), and any Cochrane PLS / NICE template updates in the 2024–2026 window. All claims are tagged with evidence tiers per [evidence-tiers.md](../00-meta/evidence-tiers.md). Bodies that author guidelines (NICE, Cochrane, WHO, USDA, CDC, FAO, NHMRC, AHA, ADA) are themselves Tier 1 sources. Behavior-change frameworks discussed below are predominantly supported by Tier 2 (systematic reviews / meta-analyses) and Tier 3 (individual RCTs / well-designed observational) evidence in nutrition contexts; mechanism-level evidence is noted where it falls to Tier 4.

### A. Behavior change frameworks — comparative audit for NutriMe fit

> Each framework is characterized by what it optimizes for, the structure of its evidence base in nutrition contexts, and a fit assessment against NutriMe's three load-bearing properties: **iterative-broadening** (the user is on a journey, not in a one-shot intervention), **autonomy-supportive** (Constitutional Rule 10 — user decides with full context), and **convenience-driven** (the user signs up to remove friction, not to enroll in a program).

#### A.1 COM-B / Behaviour Change Wheel (Michie et al.)

- **What it optimizes for:** A diagnostic model. COM-B asserts that any behavior B is the joint product of physical and psychological **C**apability, physical and social **O**pportunity, and reflective and automatic **M**otivation [Tier 2: Michie, van Stralen & West 2011, *Implementation Science*]. The Behaviour Change Wheel (BCW) extends COM-B with nine intervention functions (education, persuasion, incentivisation, coercion, training, restriction, environmental restructuring, modelling, enablement) and seven policy categories. The Behaviour Change Technique Taxonomy v1 (BCTTv1) operationalises 93 specific techniques cross-referenced into the wheel [Tier 2: Michie et al. 2013, *Annals of Behavioral Medicine*].
- **Nutrition-specific evidence base:** Multiple systematic reviews of dietary interventions classified using BCTTv1 demonstrate that **goal-setting (BCT 1.1), self-monitoring of behaviour (2.3), feedback on behaviour (2.2), action planning (1.4), and problem-solving (1.2)** correlate most consistently with measurable dietary change [Tier 2: Cradock et al. 2017, *International Journal of Behavioral Nutrition and Physical Activity*; Samdal et al. 2017, IJBNPA; Hankonen et al. 2015]. COM-B has been used to design dietary interventions targeting fruit/vegetable intake, sodium reduction, fibre increase, and ultra-processed food displacement.
- **Fit with NutriMe:**
  - *Strong fit on diagnostic structure.* COM-B is a frame to ask "what's blocking the user from doing this — capability gap, opportunity gap, or motivation gap?" — directly maps onto intake screeners (cooking literacy = capability; equipment + budget + time = opportunity; goals + readiness = motivation).
  - *Strong fit with audit-as-education.* "Education" and "enablement" are explicit BCW intervention functions; transparent provenance is a recognised education BCT.
  - *Caveat:* COM-B is **descriptive of an intervention design space**, not a theory of change in itself. NutriMe needs to pair it with a directional model (SDT or HAPA) for the "how do we move the user" question.
- **Recommended use in NutriMe:** Adopt as the **diagnostic framework** for the system's reasoning about why a user isn't adopting a given behaviour, and as the **taxonomy** for tagging system-side interventions. Pair with SDT (motivation quality) and HAPA (action timing).

#### A.2 Self-Determination Theory (SDT) — Ryan & Deci

- **What it optimizes for:** A theory of motivation quality. SDT distinguishes **autonomous motivation** (intrinsic + identified regulation — "I do this because it matters to me") from **controlled motivation** (introjected + external regulation — "I do this because I'd feel guilty if I didn't / because someone told me to") and posits that satisfying three basic psychological needs — **autonomy, competence, relatedness** — produces internalisation of behaviour change that persists beyond the intervention [Tier 2: Deci & Ryan 2000; Ryan & Deci 2017, *Self-Determination Theory*, Guilford].
- **Nutrition-specific evidence base:** SDT-based dietary interventions (e.g., Williams et al. on weight loss; Pelletier et al. on regulation of eating behaviours; the *Regulation of Eating Behaviours Scale*, REBS) consistently show that autonomous motivation predicts **maintenance** of dietary change over 12+ months, where controlled motivation predicts initial compliance but relapse [Tier 2: Teixeira et al. 2012 systematic review, IJBNPA; Ng et al. 2012 meta-analysis of SDT in health contexts]. SDT-based interventions outperform purely informational interventions on long-term adherence.
- **Fit with NutriMe:**
  - *Highest fit of any framework.* NutriMe's "user decides with full context" is verbatim autonomy support. The audit-as-education pattern builds competence. Iterative dialog and household / shared-meal awareness build relatedness.
  - *Direct design implications:* avoid prescriptive language ("you should…"), prefer informational framing ("evidence suggests…"); offer rationales for every recommendation (the audit-as-education pattern delivers this); offer meaningful choice (multiple recipes that meet the same nutritional goal); minimise control language and contingent rewards.
- **Recommended use in NutriMe:** Adopt as the **motivational philosophy** governing tone, choice architecture, and how the system frames recommendations. Use SDT's *autonomy-supportive communication* literature ([Tier 2: Su & Reeve 2011 meta-analysis of autonomy-supportive interventions]) to constrain copy patterns.

#### A.3 Health Action Process Approach (HAPA) — Schwarzer

- **What it optimizes for:** A two-phase model bridging the **intention–behaviour gap.** Phase 1 (motivational) builds intention via risk perception, outcome expectancies, and self-efficacy. Phase 2 (volitional) translates intention into action via planning (action plans + coping plans), action control, and recovery from lapses [Tier 2: Schwarzer 2008, *Applied Psychology*; Schwarzer & Luszczynska 2008].
- **Nutrition-specific evidence base:** HAPA has been applied to fruit/vegetable intake, dietary fat reduction, and dietary self-management in chronic disease. Action planning (specifying *when, where, how* I will do the behaviour) and coping planning (specifying *what I will do if* a barrier appears) consistently outperform intention-only interventions [Tier 2: Carraro & Gaudreau 2013 meta-analysis; Hagger & Luszczynska 2014 review of implementation intentions].
- **Fit with NutriMe:**
  - *Strong fit.* The whole "boom, shows up at my door" stack is essentially a **giant coping plan** — the system removes opportunity barriers (no ingredients in the house, no plan, no time to cook) before the user has to confront them.
  - The semantic-feedback loop after a planned meal maps onto HAPA's **action control / recovery from lapses** phase — when a meal failed (taste, time, gut response), the system uses that to recalibrate rather than the user being left in self-blame.
- **Recommended use in NutriMe:** Adopt as the **operational framework** for the "user has decided to do this — now make it happen and keep it happening" half of the product. Pair with COM-B (diagnostic) and SDT (motivational quality).

#### A.4 Transtheoretical Model (TTM) — Prochaska & DiClemente

- **What it optimizes for:** A stage model — Precontemplation → Contemplation → Preparation → Action → Maintenance, with stage-specific intervention strategies [Tier 2: Prochaska & DiClemente 1983; Prochaska & Velicer 1997, *American Journal of Health Promotion*].
- **Nutrition-specific evidence base:** Used heavily in behavioural nutrition counselling (e.g., dietitian motivational-interviewing protocols). **Mixed evidence for the stage construct's predictive validity.** A widely-cited Cochrane review of TTM-tailored interventions for smoking cessation found "limited evidence" of effect over non-tailored interventions [Tier 2: Cahill, Lancaster & Green 2010, Cochrane]. In nutrition specifically, stage-tailored fruit/vegetable interventions show modest effects [Tier 2: Bridle et al. 2005 systematic review of TTM across health behaviours, found generally weak evidence].
- **Fit with NutriMe:**
  - *Useful as an intake construct, not as the system's structuring frame.* "Readiness for change" maps cleanly to a screener question and is referenced in [intake-pattern.md](../00-meta/intake-pattern.md) and [sweep #3 scope](../03-clinical-nutrition-assessment/scope.md). The system can adapt tone and depth to a user reporting low readiness.
  - *Caveat:* TTM treats behaviour change as discrete stages; NutriMe treats it as iterative + horizon-broadening. The continuous progression model is closer to HAPA's volitional spiral than to TTM's staircase.
- **Recommended use in NutriMe:** **Light adoption** — capture readiness-for-change as an intake signal that adjusts tone and pacing, but do not architect the whole product around stage transitions.

#### A.5 Health Belief Model (HBM)

- **What it optimizes for:** Behaviour is predicted by **perceived susceptibility, perceived severity, perceived benefits, perceived barriers**, with **cues to action** and **self-efficacy** added in later revisions [Tier 2: Rosenstock 1974; Janz & Becker 1984, *Health Education Quarterly*; Champion & Skinner 2008].
- **Nutrition-specific evidence base:** HBM-based interventions for diabetes self-management, sodium reduction, and osteoporosis-prevention dietary calcium have shown small-to-moderate effects in observational and quasi-experimental literature [Tier 3: Jones et al. 2014 review of HBM in dietary contexts]. HBM is generally considered **better at predicting one-shot preventive behaviours** (vaccination, screening) than sustained dietary change.
- **Fit with NutriMe:**
  - *Limited direct fit.* HBM's threat-appraisal core (susceptibility × severity) sits awkwardly next to NutriMe's autonomy-supportive, non-fear-driven framing. Threat-based health communication often backfires (defensive avoidance, reactance) and is contraindicated for SDT-style autonomy support.
  - *Useful for one specific surface:* the audit-as-education content for high-marketing low-evidence claims (microbiome tests, nutrigenomics) can responsibly note where unmitigated risk exists, without leaning on fear.
- **Recommended use in NutriMe:** **Reference only.** Do not adopt as a structuring frame. Aware of HBM constructs to avoid accidentally invoking threat-based framing.

#### A.6 Theory of Planned Behavior (TPB) — Ajzen

- **What it optimizes for:** Behavioural intention is the proximal predictor of behaviour, predicted by **attitude, subjective norm, and perceived behavioural control** [Tier 2: Ajzen 1991, *Organizational Behavior and Human Decision Processes*]. Background factors (demographics, knowledge, personality) operate distally.
- **Nutrition-specific evidence base:** Heavily applied to fruit/vegetable consumption, breastfeeding, sugar-sweetened beverage reduction, organic food choice. Meta-analyses find TPB constructs explain ~30% of variance in dietary intention and ~20% in dietary behaviour [Tier 2: McEachan et al. 2011 meta-analysis, *Health Psychology Review*; Riebl et al. 2015 nutrition-specific review].
- **Fit with NutriMe:**
  - *Moderate fit as a measurement frame, weak fit as an intervention frame.* TPB is good for predicting whether a user will form intention; weaker on the intention–behaviour gap (which HAPA explicitly addresses).
  - The "subjective norm" construct is directly relevant to multi-user-household and cultural-cuisine surfaces — what the user perceives "people like me" to eat shapes uptake of horizon-broadening suggestions.
- **Recommended use in NutriMe:** **Reference only for measurement;** prefer HAPA for intervention-side modelling.

#### A.7 Capability Approach to Nutrition (Sen-influenced)

- **What it optimizes for:** Sen's capability approach reframes well-being as the freedom to achieve valued **functionings** rather than as resources or utilities [Tier 2: Sen 1985, *Commodities and Capabilities*; Sen 1999, *Development as Freedom*]. Applied to food, the focus shifts to the **capability to eat well** — encompassing knowledge, time, money, equipment, social opportunity, cultural fit, and the freedom to choose differently.
- **Nutrition-specific evidence base:** Smaller, more theoretical literature than the other frameworks. Notable applications include Burchi & De Muro on food security as a capability question [Tier 2: Burchi & De Muro 2016, *Food Policy*] and Anand et al. on operationalising capabilities for food and nutrition. Used in food-justice and food-policy literature more than in behaviour-change intervention design.
- **Fit with NutriMe:**
  - *Conceptually resonant with NutriMe's autonomy-supportive framing.* The audit-as-education pattern is, in capability terms, **expanding the user's capability to make informed food choices.** Iterative horizon-broadening expands the *opportunity set* the user has to choose from.
  - *Operationally limited.* Doesn't yield a discrete intervention design as cleanly as COM-B + HAPA + SDT.
- **Recommended use in NutriMe:** **Philosophical anchor**, especially useful when articulating the product's framing in user-facing copy or in product positioning ("we expand your capability to eat well; you decide what to do with it").

#### A.8 Synthesis — recommended framework stack for NutriMe

Frameworks layer well; no single framework should be picked exclusively.

- **Diagnostic frame:** **COM-B** + **BCTTv1** — to reason about what's blocking a behaviour and to tag the system's interventions in a published taxonomy.
- **Motivational philosophy:** **SDT** — to govern tone, choice architecture, autonomy-supportive copy, and the framing of every recommendation.
- **Operational frame for "make it happen":** **HAPA** — action plans + coping plans + lapse-recovery; maps directly onto the convenience-delivery stack and the semantic-feedback loop.
- **Light intake signals:** **TTM readiness-for-change** + **TPB subjective norm** — used as screener-derived signals that adjust system pacing, not as structuring frames.
- **Philosophical anchor:** **Capability approach** — for product framing and the audit-as-education narrative.
- **Avoid:** **HBM threat-appraisal framing** — incompatible with SDT autonomy support.

This stack has precedent: large UK behavioural-science programmes (e.g., the Behavioural Insights Team / Cabinet Office guidance, NHS digital prevention programmes) routinely combine COM-B as diagnostic with SDT or HAPA as directional [Tier 2: Michie & West 2014, BMJ; Public Health England 2018 *Behaviour Change Guide for Local Government and Partners*].

### B. Health literacy adaptation

#### B.1 Population-level adult health literacy data

- **United States — NAAL 2003.** The National Assessment of Adult Literacy (NAAL, Department of Education / NCES, 2003) included a health literacy component administered to ~19,000 adults. Headline finding: **only ~12% of US adults are at "Proficient" health literacy**, ~53% at "Intermediate," ~22% at "Basic," and ~14% at "Below Basic" [Tier 1: Kutner et al. 2006, NCES 2006-483]. The often-quoted "average US adult reads at the 8th-grade level" derives from related literacy work, not NAAL directly; NAAL itself uses task-based proficiency rather than grade-level metrics.
- **United States — HLS-19 / NAHLS update.** The original NAAL has not been re-fielded. The HHS Office of Disease Prevention and Health Promotion's *Healthy People 2030* explicitly redefined health literacy in 2020 to include **organizational health literacy** alongside personal health literacy [Tier 1: HHS / ODPHP 2020 *Healthy People 2030 Health Literacy Definition*], reframing it as a property of systems serving people, not just of people.
- **European Union — HLS-EU (2011) and HLS-19 (2019–2021).** The HLS-EU consortium (Sørensen et al.) developed the HLS-EU-Q (47-item, also short forms HLS-EU-Q16, HLS-EU-Q12, HLS-EU-Q6) measuring health literacy across **healthcare, disease prevention, and health promotion** domains × **access, understand, appraise, apply** information processing steps [Tier 2: Sørensen et al. 2012 *BMC Public Health* "Health literacy and public health: a systematic review and integration of definitions and models"; HLS-EU Consortium 2012 *Comparative Report on Health Literacy in Eight EU Member States*]. Original 8-country survey (Austria, Bulgaria, Germany, Greece, Ireland, Netherlands, Poland, Spain) found **47% of EU adults had limited (inadequate or problematic) health literacy.** HLS-19 expanded to 17 European countries (M-POHL network coordinated by Austrian National Public Health Institute) and re-confirmed broadly similar prevalence with country-level variation [Tier 1: WHO Europe / M-POHL 2021 *International Report on the Methodology, Results, and Recommendations of the European Health Literacy Population Survey 2019–2021*].
- **Australia — Australian Health Literacy Survey (ABS 2006, 2018).** Australian Bureau of Statistics applied the Health Literacy Skills Framework. 2018 Health Literacy National Statement and the Australian Commission on Safety and Quality in Health Care's *National Statement on Health Literacy* (2014) frame health literacy as both individual capacity and system responsiveness [Tier 1: ACSQHC 2014].
- **Korea — KHLA / KHLI.** Korean adult health literacy literature includes Lee et al.'s Korean Health Literacy Assessment Tool (KHLAT) and subsequent KHLI scales. Population studies repeatedly find **>40% of Korean adults at limited health literacy**, with steeper age gradients than EU [Tier 2: Lee, Kang, et al. 2009, *Asian Nursing Research*; Park & Hwang 2014; Suka et al. cross-national comparisons].
- **Japan — Nakayama lab (Kyoto University).** Nakayama and colleagues translated and validated the Japanese HLS-EU-Q47, finding **Japan with the highest proportion of "limited" health literacy across the surveyed countries** in their original cross-national comparison (~85% inadequate or problematic) — a finding partly attributable to translation calibration and to Japanese cultural reluctance to self-report capability, but also plausibly reflecting genuine system complexity [Tier 2: Nakayama et al. 2015 *BMC Public Health*; Suka et al. 2013 development of the Communicative and Critical Health Literacy scale, BMC Public Health].
- **China — National Health Literacy Initiative.** The National Health Commission has run a national health literacy monitoring survey annually since 2008, using a domestically-developed 50-item instrument. Headline: health literacy prevalence rose from **6.5% in 2008 to ~27.8% in 2022** as a national policy target under *Healthy China 2030* [Tier 1: National Health Commission of the PRC, *China Citizens' Health Literacy Monitoring Reports* 2008–2023].
- **Singapore — Health Promotion Board.** Singapore HPB applies a multi-channel health literacy framework, including the Healthier Choice Symbol (since 2001, ~5,000+ products certified), Nutri-Grade beverage labels (mandatory since 2022), and the My Healthy Plate visual model. HPB's organizational design is widely cited as a model for state-led health literacy programmes [Tier 1: Singapore Ministry of Health / HPB *War on Diabetes* programme 2016 onward].
- **Brazil & India (opportunistic).** Brazil's *Guia Alimentar para a População Brasileira* (Ministry of Health 2014, NOVA classification author Carlos Monteiro et al.) is internationally recognised as a low-literacy-friendly dietary guideline, eschewing nutrient targets in favour of food-and-meal-pattern guidance ("avoid ultra-processed foods", "make natural and minimally-processed foods the basis of your diet") [Tier 1: Brazilian Ministry of Health 2014]. India's ICMR-NIN *Dietary Guidelines for Indians* (2024) uses food-pyramid + plate visuals with English / Hindi / Telugu translation.

#### B.2 Health literacy assessment instruments

- **REALM-SF** (Rapid Estimate of Adult Literacy in Medicine — Short Form). 7 medical-word recognition items; 1–2 minute administration. Developed from the original 66-item REALM (Davis et al. 1991). Predicts grade-level reading ability in clinical contexts [Tier 2: Arozullah et al. 2007, *Medical Care*]. Limited to English; a Spanish adaptation (SAHLSA) exists.
- **TOFHLA** (Test of Functional Health Literacy in Adults). Comprehension (cloze procedure on health-related passages) + numeracy items. ~22 minutes for full version, ~7 for S-TOFHLA short form [Tier 2: Parker et al. 1995, *Journal of General Internal Medicine*; Baker et al. 1999 short form]. Available in English and Spanish.
- **NVS** (Newest Vital Sign). Six items based on a nutrition label (ice-cream container) — directly relevant to NutriMe. ~3 minutes. Validated against TOFHLA. Cut-points: 0–1 high likelihood of limited literacy, 2–3 possible limited literacy, 4–6 adequate literacy [Tier 2: Weiss et al. 2005, *Annals of Family Medicine*]. Available in multiple language versions.
- **eHEALS** (eHealth Literacy Scale). 8-item self-report measure of perceived ability to use the internet for health information [Tier 2: Norman & Skinner 2006, *Journal of Medical Internet Research*]. Critiqued for measuring confidence rather than competence; **eHLS** (Sudbury-Riley et al.) and **DHLI** (van der Vaart & Drossaert 2017) are more recent multi-domain digital health literacy instruments.
- **HLS-EU-Q** (47, 16, 12, 6-item versions). Population-level health literacy survey instrument covering the Sørensen et al. 4×3 matrix (access/understand/appraise/apply × healthcare/prevention/promotion). Now the de facto European standard [Tier 2: Sørensen et al. 2013, *BMC Public Health*; Pelikan et al. 2014 short-form validation].
- **HLQ** (Health Literacy Questionnaire). 44 items across 9 domains (Osborne et al. — Australian-developed); designed for system-level diagnostics rather than individual screening [Tier 2: Osborne, Batterham, Elsworth, Hawkins & Buchbinder 2013, *BMC Public Health*].

#### B.3 Readability metrics

- **Flesch–Kincaid Grade Level (FKGL).** Most widely adopted; standard in US clinical communication guidance. Formula based on average sentence length and syllables per word. Ubiquitous in word processors and content tools.
- **SMOG** (Simple Measure of Gobbledygook). McLaughlin 1969. Counts polysyllabic words across 30 sentences. Often preferred for health contexts because it predicts 100% comprehension grade level rather than the 50–75% predicted by FKGL [Tier 3: Wang et al. 2013 readability comparison in patient education materials].
- **Gunning Fog Index.** Sentence length × % complex words; produces a grade-level estimate. Simple to compute; less calibrated for health text than SMOG.
- **Dale–Chall Readability Formula.** Uses a list of 3,000 common words; words outside the list are "difficult." Updated 1995 (New Dale–Chall). Stronger correlation with empirical comprehension than FKGL or Fog in some validation studies.
- **Practical caveat.** All these formulas are **necessary but not sufficient.** They miss conceptual difficulty, word ambiguity, cultural unfamiliarity, and visual / structural complexity. Patient-education research routinely finds materials at "appropriate" FKGL grade level that still fail comprehension testing because of jargon, density, or layout [Tier 2: Stossel et al. 2012 review of patient-education materials readability vs. comprehension; Eltorai et al. 2014 systematic review].
- **Recommended baseline.** US AMA (1999) and NIH guidance recommend patient-facing materials at **6th–8th grade reading level**; CDC's *Clear Communication Index* (2014) extends this with a 20-item content checklist beyond raw readability [Tier 1: CDC 2014 *Clear Communication Index*; AMA 1999 *Health Literacy: Help Your Patients Understand*]. NHS England's content design guidance targets reading age 9 (UK roughly equivalent to US 4th–5th grade) for general health content.

#### B.4 Adaptive complexity ramping

- **Tailored health communication literature.** Adaptive content delivery — where the system reads engagement signals (time-on-content, follow-up question depth, vocabulary used in user input, prior content recall) and adjusts complexity — has Tier 2 evidence in tailored print and computer-tailored interventions [Tier 2: Noar, Benac & Harris 2007 meta-analysis of tailored print health behavior change interventions, *Psychological Bulletin*; Krebs, Prochaska & Rossi 2010 meta-analysis of computer-tailored interventions]. Tailored interventions show **modest but consistent effect-size advantages over generic interventions** (~d = 0.07–0.25 for dietary outcomes).
- **The "ramping" extension.** Less direct evidence specifically for *progressive* complexity ramping (start simple, ramp up as the user shows engagement) vs. one-time tailoring. Adjacent literatures: **scaffolding** in educational psychology (Wood, Bruner & Ross 1976; Vygotsky's Zone of Proximal Development); **adaptive learning** in intelligent tutoring systems (VanLehn 2011 meta-analysis of intelligent tutoring effects, *Educational Psychologist*). NutriMe's iterative-broadening model is a close cousin of educational scaffolding applied to consumer health.
- **Risk:** adaptive complexity must avoid becoming **engagement-optimized rather than learning-optimized.** The Duolingo / TikTok-style attention loop is the failure mode. NutriMe's "convenience-driven, but substantively grounded" framing implies content-quality-first adaptation.

### C. Microlearning + spaced repetition

#### C.1 Microlearning literature

- **Definition and corporate-training origin.** Microlearning is short-form (typically 2–10 minute), single-objective learning content, usually delivered in a sequence and often mobile-first. Originating in corporate L&D in the late 2000s and accelerating with mobile in the 2010s [Tier 3: Hug 2005 *Didactics of Microlearning*; Buchem & Hamelmann 2010].
- **Evidence base for retention.** Microlearning has a smaller peer-reviewed evidence base than spaced repetition. Meta-analyses are starting to emerge: **De Gagne et al. 2019** systematic review of microlearning in health professions education found generally positive but heterogeneous effects on knowledge acquisition [Tier 2: De Gagne, Park, Hall, Woodward, Yamane & Kim 2019, *Journal of Medical Internet Research*]. **Hesse et al. 2019** review in nursing education similarly positive. The strongest claim is that microlearning is **non-inferior to longer-form content for knowledge acquisition**, with modest superiority for engagement and completion rates.
- **Consumer health adaptation.** Direct evidence for nutrition microlearning is thinner. **Diabetes Prevention Program (DPP) digital adaptations** — including Omada, Noom-style content delivery — are essentially microlearning + behavioural-coaching hybrids; the National DPP-recognised digital programmes show modest weight-loss outcomes that are comparable to in-person DPP for engaged users [Tier 2: Sepah et al. 2014 *Journal of Medical Internet Research*; Castro Sweet et al. 2018 review of digital DPP outcomes]. The DPP literature is the closest published analogue to NutriMe-style asynchronous, microlearning-shaped consumer health content.

#### C.2 Spaced repetition literature

- **Foundational evidence.** Ebbinghaus's original forgetting-curve work (1885) and subsequent replications consistently show **distributed practice outperforms massed practice** for long-term retention [Tier 2: Cepeda, Pashler, Vul, Wixted & Rohrer 2006 meta-analysis of distributed practice in verbal learning, *Psychological Bulletin*; Dunlosky et al. 2013 *Improving Students' Learning With Effective Learning Techniques*, *Psychological Science in the Public Interest* — graded distributed practice as among the *most* effective learning techniques studied].
- **Optimal scheduling.** The expanding-interval (Leitner / SuperMemo / Anki) family of algorithms uses ~1-day, 3-day, 7-day, 14-day, 30-day initial intervals, expanding by a difficulty-adjusted factor (commonly ~2.5×) on each successful recall. Empirically the *exact* schedule matters less than the *fact* of distribution, with ratios of 10–30% of retention interval cited as broadly optimal [Tier 2: Cepeda et al. 2008 *Psychological Science*]. Modern algorithms (FSRS, the open algorithm now used in Anki 2.7+) are statistically calibrated rather than rule-based.
- **Application to medical education.** Spaced repetition has substantial Tier 2 evidence in medical-student knowledge retention (Anki use among USMLE candidates, ABEM adoption); evidence specifically in *patient* / *consumer* health education is much smaller [Tier 2: Larsen, Butler & Roediger 2009 medical-resident knowledge retention; Kerfoot et al. 2007–2014 series on spaced education in clinicians and patients].
- **Direct nutrition application.** Sparse. **Kerfoot et al. 2010** *American Journal of Preventive Medicine* tested spaced education for prostate cancer screening knowledge; subsequent applications by the same group covered hypertension and other patient-education topics. No major spaced-repetition nutrition RCT in the consumer-facing literature as of training-data cutoff.
- **Streak-design / Duolingo inspiration.** Duolingo and similar gamified-learning products have not published peer-reviewed evidence on nutrition-specific outcomes, but the broader habit-formation literature ([Tier 2: Lally et al. 2010 *European Journal of Social Psychology* — "How are habits formed: modelling habit formation in the real world", median ~66 days for habit formation in a daily-eating context]) supports the cadence concept. **Caveat per [intake-pattern.md](../00-meta/intake-pattern.md):** NutriMe is explicitly *not* a daily check-in product; streak mechanics that punish missed days conflict with the "no daily logging" premise. Inspiration should focus on the *spaced-repetition cadence* and *micro-content unit*, not the streak-loss mechanic.

#### C.3 Dual-purpose framing (per user direction)

The microlearning structure serves **two coupled purposes** in NutriMe, and these are inseparable design constraints:

- **(a) User comprehension + engagement.** Small chunks delivered with explicit connections increase retention vs. monolithic content blocks (the spaced-repetition + microlearning evidence above).
- **(b) System rigor — forcing-function for explicit articulation.** Structuring content as small, explicitly-connected chunks **forces the system to articulate the connection between any two pieces of content.** A monolithic "here's why fibre matters" essay can elide reasoning gaps; a sequence of micro-units (definition → mechanism → evidence → recommendation → application) cannot — each unit has to be coherent on its own terms and the connections between units have to be explicit. This is the same principle as the [causal-explanation-as-verification](../00-meta/epistemic-trail.md) pattern at content scale.

This is the "education and verification produced by the same artifact" property of [epistemic-trail.md](../00-meta/epistemic-trail.md), instantiated at the content layer.

### D. Visual / graphical communication

#### D.1 Plate models and food-group visuals

- **USDA MyPlate (2011).** Replaced the MyPyramid (2005) and the original Food Guide Pyramid (1992). Five food groups (fruits, vegetables, grains, protein, dairy) on a plate visual. ChooseMyPlate.gov. Backed by the *Dietary Guidelines for Americans* update cycle (5-year). [Tier 1: USDA / HHS 2010 *Dietary Guidelines for Americans*; USDA 2011 MyPlate launch].
- **Harvard Healthy Eating Plate (2011).** Harvard T.H. Chan School of Public Health response to MyPlate, with explicit critiques: replaces "dairy" with "water," adds "healthy oils" component, distinguishes whole grains, distinguishes healthy proteins (de-emphasises red meat), adds physical activity icon. Not a government guide; widely cited as the evidence-aligned alternative to MyPlate [Tier 2: Willett & Stampfer 2013 commentary on plate models].
- **Eatwell Guide (UK, 2016).** Replaced the eatwell plate (2007) and Balance of Good Health (1994). Five food groups with proportional area sizing derived via linear-programming optimisation by Public Health England [Tier 1: PHE 2016 Eatwell Guide].
- **Canada's Food Guide plate (2019).** ½ vegetables and fruits, ¼ whole grains, ¼ protein foods (including plant proteins). Major shift from prior Canadian guidance (which used numerical food-group servings) [Tier 1: Health Canada 2019].
- **Brazilian Dietary Guidelines (2014).** Eschews plate / pyramid; uses NOVA processing-classification and "golden rules" plus meal-pattern guidance. Internationally cited as the most low-literacy-friendly format, optimised for populations where nutrient-target guidance is unhelpful [Tier 1: Brazilian Ministry of Health 2014].
- **Japanese Spinning Top (食事バランスガイド, 2005, revised 2010).** Inverted-cone visual organised by recommended servings; runner figure for activity. Co-developed by MHLW and MAFF [Tier 1: MHLW / MAFF 2005/2010].
- **Chinese Food Pagoda (2022 revision).** Six tiers with a Food Plate and a children-oriented Food Abacus as supplementary visuals [Tier 1: CNS 2022].
- **Singapore My Healthy Plate (2014, HPB).** ¼ wholegrain carbs, ¼ protein, ½ fruits and vegetables, plus water and physical-activity callouts.
- **General evidence base.** Plate models outperform pyramid models for comprehension by general adult populations [Tier 2: Levine et al. 2012 plate-vs-pyramid comprehension; FAO 2018 review of food-based dietary guidelines visualisation]. Plate models also outperform numeric serving counts for low-literacy populations.

#### D.2 Icon arrays and frequency framing

- **Foundational work.** Gerd Gigerenzer (Max Planck Institute for Human Development, Berlin) and David Spiegelhalter (Cambridge / Royal Statistical Society) have led the **frequency-format** and **icon-array** literature [Tier 2: Gigerenzer & Hoffrage 1995 *Psychological Review* "How to improve Bayesian reasoning without instruction: frequency formats"; Gigerenzer et al. 2007 *Psychological Science in the Public Interest* "Helping doctors and patients make sense of health statistics"; Spiegelhalter 2017 *Annual Review of Statistics and Its Application* "Risk and uncertainty communication"; Spiegelhalter, Pearson & Short 2011 *Science* "Visualizing Uncertainty about the Future"].
- **Key empirical finding.** Natural-frequency formats ("10 out of 1,000 people") are reliably better understood than equivalent probability formats ("1%") by general adult audiences across literacy levels. **Icon arrays** (e.g., 1,000-person figures with 10 highlighted) further improve comprehension, particularly for low-numeracy individuals [Tier 2: Galesic, Garcia-Retamero & Gigerenzer 2009; Garcia-Retamero & Cokely 2017 review].
- **Application to nutrition.** Less direct than to medical risk communication, but applicable to: probability-of-effect framing ("if 1,000 people eat this much fibre daily, ~X experience improved bowel function within Y weeks"), comparative-portion visuals, and uncertainty bars on nutrient-target ranges.

#### D.3 Front-of-pack nutrition labels

- **Traffic-light label (UK, 2013 voluntary).** Red / amber / green per nutrient per portion, on UK packaged foods. Voluntary scheme led by FSA / DH. Modest but consistent evidence for steering purchases toward "greener" products [Tier 2: Sacks et al. 2009; Crockett et al. 2018 Cochrane review *Nutritional labelling for healthier food or non-alcoholic drink purchasing and consumption*].
- **Nutri-Score (France, 2017).** A→E composite letter score combining favourable (fibre, protein, fruits/vegetables/legumes/nuts) and unfavourable (energy, saturated fat, sugars, sodium) components into a single letter + colour. Adopted across Belgium, Germany, Luxembourg, Netherlands, Spain, Switzerland (voluntary in most, with cross-EU debate over harmonisation). Extensive validation literature [Tier 2: Julia & Hercberg 2017 Nutri-Score validation; Egnell et al. 2018 *PLOS ONE* cross-country comparison; Hercberg et al. 2022 update].
- **Health Star Rating (Australia / NZ, 2014).** ½–5 star scale on packaged foods. Industry-led with government oversight. Mixed but generally positive evidence for purchase steering [Tier 2: Mhurchu et al. 2017 RCT; 5-year review by mpconsulting 2019 published by AU government].
- **Chilean black-octagon warnings (2016).** Mandatory black-octagon warning labels for products exceeding thresholds in calories, sugars, saturated fat, sodium, plus a school marketing ban. The strongest evidence base for any FOP scheme — multiple natural-experiment studies showed substantial reformulation by industry and reduction in purchases of warned products [Tier 2: Taillie, Reyes, Colchero, Popkin & Corvalán 2020 *PLOS Medicine*; Kanter et al. 2019 evaluation series; Corvalán et al. 2019].
- **Nutri-Grade (Singapore, 2022 mandatory for beverages).** A→D grade with mandatory display on sweetened beverages plus advertising restrictions on D-grade products [Tier 1: Singapore HPB 2022].
- **General finding.** Mandatory + interpretive (colour/letter, not just numeric) FOP labels consistently outperform voluntary or numeric-only labels for steering both consumer choice and industry reformulation [Tier 2: Crockett et al. 2018 Cochrane; Croker et al. 2020 systematic review; WHO Europe 2020 *Action plan for the prevention and control of NCDs*].

#### D.4 Comparative and food-as-medicine visuals

- **CDC, NIH, ADA, AHA patient-education infographics.** Long-standing tradition of comparative and equivalence visuals (e.g., teaspoons-of-sugar visualizations, plate-vs-takeout-portion comparisons). Less peer-reviewed evidence for any specific format than for plate models, but the genre is widely deployed across authoritative bodies.
- **Sugar-sweetened beverage spoon-of-sugar imagery.** Originating in NYC DOH "Pouring on the Pounds" campaign (2009) and replicated widely. Quasi-experimental evidence for purchase reduction [Tier 3: Bleich, Wolfson, Jarlenski & Block 2014 *American Journal of Public Health*].

### E. Uncertainty + confidence visualization

#### E.1 GRADE Summary-of-Findings tables

- **GRADE working group.** *Grading of Recommendations Assessment, Development and Evaluation*. Now used by >100 organizations including WHO, Cochrane, NICE, BMJ Best Practice, UpToDate, ACP, AHA. Rates evidence certainty as **High / Moderate / Low / Very Low** based on study design, risk of bias, inconsistency, indirectness, imprecision, publication bias, and (for observational evidence) magnitude of effect, dose-response, residual confounding [Tier 1: Guyatt et al. 2008 *BMJ* "GRADE: an emerging consensus on rating quality of evidence and strength of recommendations"; Guyatt et al. 2011 *Journal of Clinical Epidemiology* multi-paper GRADE methodology series].
- **Summary-of-Findings (SoF) tables.** Standard Cochrane review output; 6–8 outcomes × certainty rating × number of participants/studies × absolute effect with 95% CI × certainty rating with reason for downgrading. Now produced via GRADEpro GDT software [Tier 1: Schünemann et al. 2008 *BMJ*; Cochrane Handbook chapter 14].
- **Consumer adaptation evidence.** GRADE SoF tables were designed for clinicians; consumer comprehension of certainty ratings is mixed. The **iSoF (interactive Summary of Findings)** project at Cochrane has tested layered, plain-language adaptations with reasonable comprehension by lay users when paired with explanatory text [Tier 2: Rosenbaum et al. 2010 *Journal of Clinical Epidemiology*; Vandvik et al. 2020 MAGICapp evaluation; Jain et al. 2024 iSoF user-testing].

#### E.2 Cochrane Plain Language Summary patterns

- **Standard structure.** Cochrane PLS template (most recent revision 2019, with minor updates since): a single page covering "What is the aim of this review? — Key messages — What was studied? — What are the main results? — How up-to-date is this evidence?". Target reading age: ~14 years (US ~9th grade, UK reading age 14) [Tier 1: Cochrane *Methodological Expectations of Cochrane Intervention Reviews* (MECIR) plain-language standards; Cochrane Norway / Glenton et al. 2010 *Cochrane Database Methodology* PLS development].
- **Evidence on PLS comprehension.** Published evaluations (Glenton et al., Santesso et al.) show PLS structure substantially improves lay comprehension of systematic-review findings vs. unstructured abstracts [Tier 2: Santesso et al. 2015 systematic review of plain-language summary formats].
- **NutriMe relevance.** PLS structure is a transferable template for any audit-as-education content delivering systematic-review-quality evidence on a specific topic ("microbiome personalization", "intermittent fasting", "specific cuisine-disease association"). The five-element template maps directly onto NutriMe's evidence-tier-tagged content blocks.

#### E.3 NICE patient decision aids and certainty signalling

- **NICE patient decision aids.** National Institute for Health and Care Excellence (UK) develops decision aids paired with clinical guidelines. Format includes plain-language framing, option grids, and explicit benefit/harm presentation in natural frequencies and icon arrays [Tier 1: NICE patient decision aid library, ongoing].
- **NICE certainty traffic-light.** NICE guidance distinguishes **strong recommendations** ("offer", "do not offer") from **weak / conditional recommendations** ("consider"), tied to underlying GRADE certainty. This binary is more interpretable for general audiences than the four-level GRADE certainty scale [Tier 1: NICE 2014 *Developing NICE Guidelines: The Manual* (PMG20)].
- **MAGICapp.** Multi-Layered guideline consumption format developed by the MAGIC Evidence Ecosystem Foundation, used by the BMJ Rapid Recommendations series. Clinician-facing top layer with consumer-facing layer accessible via the same evidence trail [Tier 2: Vandvik, Brandt, Alonso-Coello et al. 2013 onward in *BMJ*].

#### E.4 Hedged-language patterns

- **Standardised hedge language.** Cochrane's GRADE-aligned plain-language hedges:
  - High certainty → "X reduces / improves Y"
  - Moderate certainty → "X probably reduces / improves Y"
  - Low certainty → "X may reduce / improve Y"
  - Very low certainty → "It is uncertain whether X reduces / improves Y"
  [Tier 1: Cochrane / GRADE plain-language guide 2019 update; Glenton, Santesso, Rosenbaum et al.]
- **Empirical evidence on hedge interpretation.** Adults interpret these hedges with reasonable consistency when the calibration phrase is presented adjacent ("'may' means we are not very certain"). Without calibration, "may" is widely misinterpreted as more certain than intended [Tier 2: Buchter, Fechtelpeter, Knelangen, Ehrlich & Waltering 2014 *BMC Medical Research Methodology*; Glenton et al. 2010].
- **NutriMe application.** Hedge language is the verbal complement to the evidence-tier badge — both pieces should always travel together per [evidence-tiers.md](../00-meta/evidence-tiers.md) surfacing rules.

#### E.5 Probability-of-effect framing

See D.2 above on icon arrays + frequency formats. The Spiegelhalter / Gigerenzer line of research is the canonical evidence base for probability presentation — natural frequencies dominate percentages dominate raw probabilities. Bayesian / posterior-belief visualisation (e.g., Spiegelhalter's *Visualising Uncertainty* work, the *Microsoft Research Hypothetical Outcome Plot* literature) is research-stage for consumer audiences and not yet a standard pattern.

#### E.6 Uncertainty-erosion literature

- **The "trust paradox" of uncertainty disclosure.** Multiple lines of research find uncertainty disclosure can **either** build or erode trust depending on framing. **Building trust:** when uncertainty disclosure is structural (paired with evidence-base explanation, alternatives, and a "what to do anyway" recommendation). **Eroding trust:** when uncertainty disclosure is bare ("we don't know") without context, or when it appears inconsistent with prior confident communication [Tier 2: van der Bles, van der Linden, Freeman, Mitchell, Galvao, Zaval & Spiegelhalter 2020 *PNAS* "The effects of communicating uncertainty on public trust in facts and numbers"; Gustafson & Rice 2020 systematic review of uncertainty effects in environmental and health communication].
- **Relevant finding for NutriMe.** Uncertainty disclosure in *numerical* form (95% CI, percentage estimates) was generally found *not* to substantially erode trust in source competence in van der Bles et al.'s large pre-registered experiments; verbal hedge language ("we don't know") had a stronger trust-eroding effect when not paired with structural context. **Implication for NutriMe:** prefer numerical uncertainty (where available) plus explicit context over bare verbal hedging.

### F. Causal explanation depth

#### F.1 Mechanism vs. correlation vs. authority framing

- **Mechanism explanations build durable behaviour change more than authority appeals.** Health-communication and education literatures both find that **mechanism explanations** ("fibre slows gastric emptying, which lowers the postprandial glucose spike") produce better retention and more durable behaviour change than **authority claims** ("the AHA says you should eat 25g fibre daily") in adult learners [Tier 2: Petty & Cacioppo 1986 *Communication and Persuasion: Central and Peripheral Routes to Attitude Change* — the elaboration likelihood model is the canonical theoretical frame; Lombrozo 2006 *Trends in Cognitive Sciences* "The structure and function of explanations"; Williams & Lombrozo 2010 *Cognitive Science* — mechanism-seeking facilitates category learning].
- **Mechanism explanations risk "explanation theater."** Deep-feeling explanations can produce **illusion of understanding** without actual comprehension — Rozenblit & Keil's "illusion of explanatory depth" [Tier 2: Rozenblit & Keil 2002 *Cognitive Science*]. Asking learners to *generate* the explanation (not just receive it) is the mitigation — the act of generation surfaces gaps. This is mirrored by NutriMe's [causal-explanation-as-verification](../00-meta/epistemic-trail.md) pattern: the system generates the chain, which surfaces inconsistencies.
- **The "performance of learning" failure mode.** When health-communication content optimises for *appearing* educational rather than *being* educational, users complete content with high subjective comprehension and low objective retention. Counter-measures: spaced retrieval-practice questions, micro-applications ("try this", "compare to your last meal"), reflective prompts that surface the user's own model. **Retrieval practice** (Roediger & Karpicke 2006 *Psychological Science* "Test-enhanced learning") consistently outperforms re-study even when learners subjectively prefer re-study [Tier 2].

#### F.2 Verification-mechanism role per epistemic-trail.md

Per [epistemic-trail.md](../00-meta/epistemic-trail.md) §3, the same causal explanation that surfaces to the user serves as the system's verification artifact. Generating "input X → mechanism Y → conclusion Z" articulates assumptions and chain-links that opaque LLM reasoning would elide. This pattern is grounded in:

- **Chain-of-thought / explanation-based verification.** Multiple lines in the explainable-AI / interpretability literature find that requiring explicit reasoning chains increases the rate at which inconsistencies are caught before output [Tier 3: Wei et al. 2022 *Chain-of-thought prompting elicits reasoning in large language models*, NeurIPS — note Tier 3 pre-print provenance, peer-reviewed conference proceedings now exist; Lampinen et al. 2022; subsequent literature on self-consistency and verification].
- **Mechanism-elicitation as deception detection in expert communication.** Forcing mechanism articulation surfaces fabrication in expert testimony (Vrij et al. cognitive-load deception detection literature) — a parallel useful for AI-generated explanations [Tier 3: Vrij, Granhag & Porter 2010 *Psychological Science in the Public Interest*].
- **NutriMe's specific operationalisation.** The causal chain is the deliverable for both education (user sees the why) and verification (system catches off-by-one numerical errors, yes/no flips, contradictory premises). Education and verification are coupled, which prevents drift between what the system did internally and what it told the user externally.

### G. Adult learning theory

#### G.1 Knowles' andragogy

- **Five core andragogical principles** [Tier 2: Knowles 1980 *The Modern Practice of Adult Education: From Pedagogy to Andragogy*; Knowles, Holton & Swanson 2015 *The Adult Learner* (8th ed.)]:
  1. Adults need to know **why** they need to learn something
  2. Adults are **self-directed** in their learning
  3. Adults bring **prior experience** as a learning resource
  4. Adults are **ready to learn** what they need to deal with real-life situations
  5. Adults are **motivated by internal factors** more than external rewards (overlaps with SDT)
- **Direct fit with NutriMe.** Every principle maps cleanly. The "need to know why" is the entire audit-as-education pattern. Self-direction maps to the user-decides framework. Prior experience is captured by intake. Real-life situational readiness is captured by HAPA-style coping plans. Internal motivation is SDT.

#### G.2 Experiential learning (Kolb)

- **Kolb's cycle:** Concrete Experience → Reflective Observation → Abstract Conceptualization → Active Experimentation, returning to Concrete Experience [Tier 2: Kolb 1984 *Experiential Learning: Experience as the Source of Learning and Development*; Kolb & Kolb 2017 update].
- **NutriMe fit.** The semantic-feedback loop is essentially a Kolb cycle: meal cooked (CE) → "how did it make me feel" (RO) → system articulates the pattern (AC) → next-meal recommendation incorporating the lesson (AE).

#### G.3 Transformative learning (Mezirow)

- **Disorienting dilemmas → critical reflection → perspective transformation** [Tier 2: Mezirow 1991 *Transformative Dimensions of Adult Learning*; Mezirow 2000 *Learning as Transformation*].
- **NutriMe fit.** Iterative horizon-broadening is an explicit application of transformative learning. The user starting on chicken nuggets encountering a well-fitted, evidence-grounded suggestion from a different culinary tradition is precisely the disorienting-dilemma → reflection → perspective-shift mechanism, applied gently and over time.

#### G.4 Self-directed learning (Tough, Knowles, Brookfield)

- Tough's foundational survey (1971) of adult learning projects established that the majority of adult learning is self-initiated and informal [Tier 3: Tough 1971 *The Adult's Learning Projects*]. Brookfield's *Understanding and Facilitating Adult Learning* (1986) operationalises self-directed learning as both a process and a goal [Tier 2].
- **NutriMe fit.** The product is a *facilitator* of self-directed learning rather than an instructor. Its job is to surface the right next thing at the right time, not to deliver a curriculum.

#### G.5 Adult learning research applied to nutrition specifically

- Sparser literature than general adult learning. Notable strands:
  - **Cooking Matters** (Share Our Strength) and **EFNEP** (USDA Expanded Food and Nutrition Education Program) curriculum evaluations, mostly low-income population focus [Tier 2: Bensley et al. evaluation series; Dollahite et al. EFNEP outcome reviews].
  - **Health coaching literature** in chronic disease (T2D, CVD), with motivational-interviewing-grounded protocols showing modest dietary outcome effects [Tier 2: Wolever et al. 2011 *Diabetes Educator*; Hill et al. 2015 health coaching meta-analysis].
  - **Cooperative Extension nutrition education** in the US — long-running, mixed-strength evaluation evidence.

### H. Trust + credibility in AI-mediated health information

> Rapidly-evolving literature post-2022 (ChatGPT release). Findings here drawn from training-data knowledge of pre-cutoff peer-reviewed work; re-verification recommended at implementation given the pace of new publication.

#### H.1 Credibility cues that build trust

- **Explicit citations + source provenance.** When AI-generated medical content is presented with explicit, verifiable citations to peer-reviewed sources, lay-user trust ratings increase substantially, **even when** the AI's accuracy is unchanged [Tier 2: Studies in *JAMA Network Open* 2023–2024 series on ChatGPT in patient question-answering; Ayers et al. 2023 *JAMA Internal Medicine* on chatbot vs. physician responses to patient questions].
- **Calibrated hedging.** Per E.4 above — appropriate verbal hedging paired with calibration phrases builds rather than erodes trust.
- **Audit trail / show-your-work.** The "epistemic trail of honesty" pattern aligns with the explainable-AI literature finding that *contrastive* and *causal* explanations build user trust more than *feature-importance* explanations [Tier 2: Miller 2019 *Artificial Intelligence* "Explanation in artificial intelligence: insights from the social sciences"].
- **Consistency across sessions.** When the same question yields broadly the same answer, trust increases; inconsistency is a strong erosion signal.
- **Domain-appropriate humility.** Explicit deferral to clinician for clinical-adjacent questions ([Constitutional Rule 1](../00-meta/constitutional-rules.md#rule-1--consult-a-professional)) increases rather than decreases user trust in the AI's general competence.

#### H.2 Credibility cues that erode trust

- **Overconfidence / lack of hedging.** Confident statements on topics with weak evidence are particularly trust-eroding when the user later discovers the weak base.
- **Hallucinated citations.** A documented failure mode of consumer LLM use in health: invented author names, invented DOIs, invented journal titles. Disastrous for trust when caught. Rule 7's peer-reviewed floor + the source-provenance requirement of [Constitutional Rule 8](../00-meta/constitutional-rules.md#rule-8--epistemic-trail-of-honesty) directly counter this.
- **Generic disclaimers in place of substantive engagement.** "I'm just an AI, please consult your doctor" without addressing the question is widely perceived as evasion. Pair the consult-professional referral with substantive evidence presentation per [Rule 1](../00-meta/constitutional-rules.md#rule-1--consult-a-professional) ("transparency plus appropriate redirection").
- **Inconsistency** — same question, different sessions, materially different answers.

#### H.3 AI-disclosure framing

- **Disclosing AI authorship.** Best-practice consensus emerging across peer-reviewed editorial guidance (ICMJE 2023; WAME 2023; JAMA 2023) requires AI-generated content to be disclosed and to not be listed as an author. **Consumer-facing analog** is less codified but converging — disclose AI-mediated synthesis prominently, not in a footer.
- **The "AI assistant" framing** (vs. "AI doctor" or "AI nutritionist") is consistently cited as more honest and less trust-fragile when limitations are encountered. NutriMe's positioning as a "research-and-recommendation collaborator" per [epistemic-trail.md](../00-meta/epistemic-trail.md) §"Why this exists" is consistent with this framing.

### I. Plain-language clinical communication

#### I.1 Cochrane Plain Language Summaries — international gold standard

See E.2 above. Cochrane's PLS template (5-section, ~14-year reading age target) is the international reference standard, used or adapted by NICE, the BMJ, and many national guideline producers.

#### I.2 NICE patient decision aids and information

NICE produces a parallel patient-information stream alongside every clinical guideline. Patient decision aids use option grids, natural-frequency benefit/harm tables, and plain-language framing [Tier 1: NICE patient information programme, ongoing].

#### I.3 PLAIN movement (Plain Language Action and Information Network — US)

- **Plain Writing Act of 2010** (US federal). Mandates that federal agencies write "in plain writing the public can understand and use." Implementation guidance via plainlanguage.gov, maintained by PLAIN, an inter-agency group.
- **Five core principles:** write for the audience, organise for the reader, use plain words, use short sentences, design for ease of reading.
- **NutriMe relevance.** US federal patient-facing health content (CDC, NIH MedlinePlus, FDA) is bound by Plain Writing Act guidance — these sources are model patterns for plain-language NutriMe content [Tier 1: Plain Writing Act 2010, Pub.L. 111–274; PLAIN guidelines maintained at plainlanguage.gov].

#### I.4 International Plain Language Federation (IPLF)

- IPLF (founded 2007) coordinates the **Center for Plain Language** (US), **Clarity** (international, lawyer-focused), and **PLAIN** (international plain-language network — distinct from US PLAIN above). Publishes the **ISO 24495-1:2023 *Plain Language — Part 1: Governing Principles and Guidelines*** [Tier 1: ISO 24495-1:2023], which provides the first international standard for plain-language communication. ISO 24495 was developed substantially by IPLF members.
- **NutriMe relevance.** ISO 24495-1's four principles (relevant, findable, understandable, usable) are a usable governance frame for content standards.

#### I.5 Health Communication Capacity Collaborative (HC3 — USAID / Johns Hopkins CCP)

- HC3 (2012–2017) and its successor **Breakthrough ACTION** (2017 onward) at Johns Hopkins Center for Communication Programs publish freely-available **Strategic Communication for Behavior Change** frameworks and toolkits, predominantly used in low-and-middle-income-country (LMIC) public-health programs. The **Health COMpass** (healthcompass.org) library aggregates 1,000+ vetted health-communication resources [Tier 1: USAID / JHU CCP, ongoing].
- **NutriMe relevance.** Demonstrates international convergence around the SBCC (Social and Behavior Change Communication) frame; particularly relevant when NutriMe encounters horizon-broadening recommendations from cuisines and cultural patterns prevalent in LMIC settings (e.g., West African, South Asian, Mesoamerican).

#### I.6 WHO Health Literacy Development Framework

- **WHO Europe 2013** *Health Literacy: The Solid Facts* (Kickbusch, Pelikan, Apfel, Tsouros eds.) established the WHO Europe framing that health literacy is a determinant of health [Tier 1: WHO Europe 2013].
- **WHO 2022** *Towards a Global Health Literacy Strategy* and the **WHO Health Literacy Development for the Prevention and Control of Noncommunicable Diseases** series (WHO 2022, 4-volume) extend the framing to a global agenda, with explicit attention to digital health literacy [Tier 1: WHO 2022 Global Health Literacy Strategy series].
- **NutriMe relevance.** WHO's framing of health literacy as a system-and-individual-property complement directly mirrors HHS's *Healthy People 2030* re-definition (B.1 above). Together they justify NutriMe's design responsibility for **organizational health literacy** — the system itself must be literacy-friendly, not place the literacy burden on the user.

### J. Open-questions section — answers as best available

> Per the scope's *Open questions for the research* prompt, brief direct answers based on the above synthesis.

- **Q1: Evidence base for each behavior-change framework, and divergence from medication-adherence / exercise / smoking literatures?** *Answered in §A.* COM-B and BCTTv1 are the most directly transferable across behavioural domains; SDT has equally strong evidence in dietary, exercise, and academic contexts; HAPA was originally developed for sun-protection behaviour and has transferred well to dietary; TTM was developed in smoking and is weaker in dietary; HBM was developed in vaccination and is weaker in sustained dietary change; TPB explains dietary intention better than dietary behaviour. The strongest cross-domain finding: **frameworks emphasizing the volitional / planning phase (HAPA, COM-B's "Opportunity") consistently outperform purely motivational frameworks (HBM, TPB) for sustained behaviour.**
- **Q2: Strongest evidence for adaptive-complexity content vs. one-level-fits-all?** *Answered in §B.4.* Tailored health-communication meta-analyses (Noar et al. 2007; Krebs et al. 2010) provide Tier 2 evidence for tailoring outperforming generic; explicit *progressive ramping* has weaker direct evidence and borrows from intelligent-tutoring scaffolding literature.
- **Q3: Optimal cadences for spaced repetition in nutrition retention?** *Answered in §C.2.* General spaced-repetition literature supports expanding intervals (~1, 3, 7, 14, 30 days initial); ratio of 10–30% of intended retention interval is broadly optimal; nutrition-specific empirical evidence is sparse — the Kerfoot et al. spaced-education series is the closest analogue. **Open empirical gap** in nutrition-specific cadence research.
- **Q4: How do GRADE-style certainty indicators land with consumer audiences?** *Answered in §E.1, E.2.* The four-level GRADE certainty scale is poorly understood by lay users without explanation; the binary "strong / conditional" recommendation language used by NICE works better; iSoF (interactive Summary of Findings) work shows lay comprehension is achievable with layered, plain-language adaptation. **Implication for NutriMe:** simplify the certainty rating to a 2- or 3-level user-facing display (not the full 4-level GRADE) while preserving the underlying GRADE rating in the audit trail for transparency.
- **Q5: Causal explanation changing behavior vs. "performance of learning"?** *Answered in §F.1.* Mechanism explanations build durable change more than authority appeals (elaboration-likelihood, retrieval-practice literatures); but mechanism explanations also produce illusion of explanatory depth (Rozenblit & Keil) when received passively. Mitigation: **require generation, not just reception** — micro-applications, retrieval-practice prompts, "what would you do in this scenario."
- **Q6: Credibility cues that build vs. erode trust in AI-delivered health information?** *Answered in §H.* Build: explicit verifiable citations, calibrated hedging, audit trail, consistency, domain-appropriate humility. Erode: overconfidence, hallucinated citations, generic disclaimers in place of engagement, inconsistency.
- **Q7: International plain-language convergence — transferable baseline vs. culture-specific?** *Answered in §I.* The transferable baseline is now codified in **ISO 24495-1:2023** plus the Cochrane PLS template plus WHO Health Literacy Development Framework. Culture-specific adaptations dominate at the **example, idiom, and visual-metaphor** layer (e.g., plate vs. pyramid vs. spinning-top vs. pagoda), not at the structural-template layer. NutriMe should standardise on the structural baseline (PLS-style template + ISO 24495 principles) and localise at the example/visual layer.

## References

> Citations follow [citation-style.md](../00-meta/citation-style.md). All accessed-on dates 2026-04-28 unless noted; web-source citations should be re-verified at implementation given WebFetch unavailability during this sweep.

### Behavior change frameworks

- Ajzen, I. (1991). The theory of planned behavior. *Organizational Behavior and Human Decision Processes*, 50(2), 179–211. https://doi.org/10.1016/0749-5978(91)90020-T
- Bridle, C., Riemsma, R.P., Pattenden, J., Sowden, A.J., Mather, L., Watt, I.S., & Walker, A. (2005). Systematic review of the effectiveness of health behavior interventions based on the transtheoretical model. *Psychology and Health*, 20(3), 283–301. https://doi.org/10.1080/08870440512331333997
- Burchi, F., & De Muro, P. (2016). From food availability to nutritional capabilities: Advancing food security analysis. *Food Policy*, 60, 10–19. https://doi.org/10.1016/j.foodpol.2015.03.008
- Cahill, K., Lancaster, T., & Green, N. (2010). Stage-based interventions for smoking cessation. *Cochrane Database of Systematic Reviews*, (11), CD004492. https://doi.org/10.1002/14651858.CD004492.pub4
- Carraro, N., & Gaudreau, P. (2013). Spontaneous and experimentally induced action planning and coping planning for physical activity: A meta-analysis. *Psychology of Sport and Exercise*, 14(2), 228–248. https://doi.org/10.1016/j.psychsport.2012.10.004
- Champion, V.L., & Skinner, C.S. (2008). The Health Belief Model. In K. Glanz, B.K. Rimer & K. Viswanath (Eds.), *Health Behavior and Health Education: Theory, Research, and Practice* (4th ed., pp. 45–65). Jossey-Bass.
- Cradock, K.A., ÓLaighin, G., Finucane, F.M., Gainforth, H.L., Quinlan, L.R., & Ginis, K.A. (2017). Behaviour change techniques targeting both diet and physical activity in type 2 diabetes: A systematic review and meta-analysis. *International Journal of Behavioral Nutrition and Physical Activity*, 14(1), 18. https://doi.org/10.1186/s12966-016-0436-0
- Deci, E.L., & Ryan, R.M. (2000). The "what" and "why" of goal pursuits: Human needs and the self-determination of behavior. *Psychological Inquiry*, 11(4), 227–268. https://doi.org/10.1207/S15327965PLI1104_01
- Hagger, M.S., & Luszczynska, A. (2014). Implementation intention and action planning interventions in health contexts: State of the research and proposals for the way forward. *Applied Psychology: Health and Well-Being*, 6(1), 1–47. https://doi.org/10.1111/aphw.12017
- Hankonen, N., Sutton, S., Prevost, A.T., Simmons, R.K., Griffin, S.J., Kinmonth, A.L., & Hardeman, W. (2015). Which behavior change techniques are associated with changes in physical activity, diet and body mass index in people with recently diagnosed diabetes? *Annals of Behavioral Medicine*, 49(1), 7–17. https://doi.org/10.1007/s12160-014-9624-9
- Janz, N.K., & Becker, M.H. (1984). The Health Belief Model: A decade later. *Health Education Quarterly*, 11(1), 1–47. https://doi.org/10.1177/109019818401100101
- McEachan, R.R.C., Conner, M., Taylor, N.J., & Lawton, R.J. (2011). Prospective prediction of health-related behaviours with the theory of planned behaviour: A meta-analysis. *Health Psychology Review*, 5(2), 97–144. https://doi.org/10.1080/17437199.2010.521684
- Michie, S., van Stralen, M.M., & West, R. (2011). The behaviour change wheel: A new method for characterising and designing behaviour change interventions. *Implementation Science*, 6, 42. https://doi.org/10.1186/1748-5908-6-42
- Michie, S., Richardson, M., Johnston, M., Abraham, C., Francis, J., Hardeman, W., Eccles, M.P., Cane, J., & Wood, C.E. (2013). The behavior change technique taxonomy (v1) of 93 hierarchically clustered techniques: Building an international consensus for the reporting of behavior change interventions. *Annals of Behavioral Medicine*, 46(1), 81–95. https://doi.org/10.1007/s12160-013-9486-6
- Michie, S., & West, R. (2014). Behaviour change theory and evidence: A presentation to government. *British Medical Journal*, 349, g6168. https://doi.org/10.1136/bmj.g6168
- Ng, J.Y.Y., Ntoumanis, N., Thøgersen-Ntoumani, C., Deci, E.L., Ryan, R.M., Duda, J.L., & Williams, G.C. (2012). Self-determination theory applied to health contexts: A meta-analysis. *Perspectives on Psychological Science*, 7(4), 325–340. https://doi.org/10.1177/1745691612447309
- Prochaska, J.O., & DiClemente, C.C. (1983). Stages and processes of self-change of smoking: Toward an integrative model of change. *Journal of Consulting and Clinical Psychology*, 51(3), 390–395. https://doi.org/10.1037/0022-006X.51.3.390
- Prochaska, J.O., & Velicer, W.F. (1997). The transtheoretical model of health behavior change. *American Journal of Health Promotion*, 12(1), 38–48. https://doi.org/10.4278/0890-1171-12.1.38
- Public Health England (2018). *Behaviour Change Guide for Local Government and Partners*. https://www.gov.uk/government/publications/behaviour-change-guide-for-local-government-and-partners. Accessed 2026-04-28.
- Riebl, S.K., MacDougal, C., Hill, C., Estabrooks, P.A., Dunsmore, J.C., Savla, J., Frisard, M.I., Dietrich, A.M., Peng, Y., Zhang, X., & Davy, B.M. (2015). Beverage choices of adolescents and their parents using the theory of planned behavior: A mixed-methods analysis. *Journal of the Academy of Nutrition and Dietetics*, 115(2), 226–239. https://doi.org/10.1016/j.jand.2014.08.030
- Rosenstock, I.M. (1974). Historical origins of the Health Belief Model. *Health Education Monographs*, 2(4), 328–335. https://doi.org/10.1177/109019817400200403
- Ryan, R.M., & Deci, E.L. (2017). *Self-Determination Theory: Basic Psychological Needs in Motivation, Development, and Wellness*. Guilford Press.
- Samdal, G.B., Eide, G.E., Barth, T., Williams, G., & Meland, E. (2017). Effective behaviour change techniques for physical activity and healthy eating in overweight and obese adults: Systematic review and meta-regression analyses. *International Journal of Behavioral Nutrition and Physical Activity*, 14, 42. https://doi.org/10.1186/s12966-017-0494-y
- Schwarzer, R. (2008). Modeling health behavior change: How to predict and modify the adoption and maintenance of health behaviors. *Applied Psychology: An International Review*, 57(1), 1–29. https://doi.org/10.1111/j.1464-0597.2007.00325.x
- Sen, A. (1985). *Commodities and Capabilities*. North-Holland.
- Sen, A. (1999). *Development as Freedom*. Knopf.
- Su, Y.L., & Reeve, J. (2011). A meta-analysis of the effectiveness of intervention programs designed to support autonomy. *Educational Psychology Review*, 23(1), 159–188. https://doi.org/10.1007/s10648-010-9142-7
- Teixeira, P.J., Carraça, E.V., Markland, D., Silva, M.N., & Ryan, R.M. (2012). Exercise, physical activity, and self-determination theory: A systematic review. *International Journal of Behavioral Nutrition and Physical Activity*, 9, 78. https://doi.org/10.1186/1479-5868-9-78

### Health literacy

- ACSQHC — Australian Commission on Safety and Quality in Health Care (2014). *National Statement on Health Literacy: Taking Action to Improve Safety and Quality*. https://www.safetyandquality.gov.au/. Accessed 2026-04-28.
- Arozullah, A.M., Yarnold, P.R., Bennett, C.L., Soltysik, R.C., Wolf, M.S., Ferreira, R.M., et al. (2007). Development and validation of a short-form, rapid estimate of adult literacy in medicine. *Medical Care*, 45(11), 1026–1033. https://doi.org/10.1097/MLR.0b013e3180616c1b
- Baker, D.W., Williams, M.V., Parker, R.M., Gazmararian, J.A., & Nurss, J. (1999). Development of a brief test to measure functional health literacy. *Patient Education and Counseling*, 38(1), 33–42. https://doi.org/10.1016/S0738-3991(98)00116-5
- HHS / ODPHP (2020). *Healthy People 2030 Health Literacy Definition*. US Department of Health and Human Services, Office of Disease Prevention and Health Promotion. https://health.gov/healthypeople/priority-areas/health-literacy-healthy-people-2030. Accessed 2026-04-28.
- Kutner, M., Greenberg, E., Jin, Y., & Paulsen, C. (2006). *The Health Literacy of America's Adults: Results from the 2003 National Assessment of Adult Literacy* (NCES 2006-483). US Department of Education, National Center for Education Statistics. https://nces.ed.gov/pubs2006/2006483.pdf. Accessed 2026-04-28.
- Lee, S.Y., Tsai, T.I., Tsai, Y.W., & Kuo, K.N. (2009). Development and validation of the Korean Health Literacy Assessment Tool. *Asian Nursing Research*, 3(3), 109–117.
- Nakayama, K., Osaka, W., Togari, T., Ishikawa, H., Yonekura, Y., Sekido, A., & Matsumoto, M. (2015). Comprehensive health literacy in Japan is lower than in Europe: A validated Japanese-language assessment of health literacy. *BMC Public Health*, 15, 505. https://doi.org/10.1186/s12889-015-1835-x
- National Health Commission of the People's Republic of China (annual since 2008). *China Citizens' Health Literacy Monitoring Reports*. http://en.nhc.gov.cn/. Accessed 2026-04-28.
- Norman, C.D., & Skinner, H.A. (2006). eHEALS: The eHealth Literacy Scale. *Journal of Medical Internet Research*, 8(4), e27. https://doi.org/10.2196/jmir.8.4.e27
- Osborne, R.H., Batterham, R.W., Elsworth, G.R., Hawkins, M., & Buchbinder, R. (2013). The grounded psychometric development and initial validation of the Health Literacy Questionnaire (HLQ). *BMC Public Health*, 13, 658. https://doi.org/10.1186/1471-2458-13-658
- Parker, R.M., Baker, D.W., Williams, M.V., & Nurss, J.R. (1995). The test of functional health literacy in adults: A new instrument for measuring patients' literacy skills. *Journal of General Internal Medicine*, 10(10), 537–541. https://doi.org/10.1007/BF02640361
- Pelikan, J.M., Röthlin, F., & Ganahl, K. (2014). *Comparative Report on Health Literacy in Eight EU Member States: The European Health Literacy Survey HLS-EU* (Second revised and extended version). HLS-EU Consortium.
- Sørensen, K., Van den Broucke, S., Fullam, J., Doyle, G., Pelikan, J., Slonska, Z., Brand, H., & (HLS-EU) Consortium Health Literacy Project European (2012). Health literacy and public health: A systematic review and integration of definitions and models. *BMC Public Health*, 12, 80. https://doi.org/10.1186/1471-2458-12-80
- Sørensen, K., Van den Broucke, S., Pelikan, J.M., Fullam, J., Doyle, G., Slonska, Z., et al. (2013). Measuring health literacy in populations: Illuminating the design and development process of the European Health Literacy Survey Questionnaire (HLS-EU-Q). *BMC Public Health*, 13, 948. https://doi.org/10.1186/1471-2458-13-948
- Suka, M., Odajima, T., Kasai, M., Igarashi, A., Ishikawa, H., Kusama, M., et al. (2013). The 14-item health literacy scale for Japanese adults (HLS-14). *Environmental Health and Preventive Medicine*, 18(5), 407–415. https://doi.org/10.1007/s12199-013-0340-z
- Weiss, B.D., Mays, M.Z., Martz, W., Castro, K.M., DeWalt, D.A., Pignone, M.P., Mockbee, J., & Hale, F.A. (2005). Quick assessment of literacy in primary care: The Newest Vital Sign. *Annals of Family Medicine*, 3(6), 514–522. https://doi.org/10.1370/afm.405
- WHO Europe / M-POHL (2021). *International Report on the Methodology, Results, and Recommendations of the European Health Literacy Population Survey 2019–2021 (HLS19) of M-POHL*. Austrian National Public Health Institute. https://m-pohl.net/. Accessed 2026-04-28.
- WHO Europe (2013). *Health Literacy: The Solid Facts*. (Kickbusch, I., Pelikan, J.M., Apfel, F., & Tsouros, A.D., eds.) WHO Regional Office for Europe. https://www.who.int/europe/publications/i/item/9789289000154. Accessed 2026-04-28.
- WHO (2022). *Health Literacy Development for the Prevention and Control of Noncommunicable Diseases* (4-volume series). World Health Organization. https://www.who.int/publications/i/item/9789240055339. Accessed 2026-04-28.

### Readability and content design

- AMA — American Medical Association (1999). *Health Literacy: Help Your Patients Understand* (Manual for Clinicians).
- CDC (2014). *CDC Clear Communication Index: A Tool for Developing and Assessing CDC Public Communication Products*. US Centers for Disease Control and Prevention. https://www.cdc.gov/ccindex/. Accessed 2026-04-28.
- Eltorai, A.E., Ghanian, S., Adams, C.A., Born, C.T., & Daniels, A.H. (2014). Readability of patient education materials on the American Association for Surgery of Trauma website. *Archives of Trauma Research*, 3(1), e18161. https://doi.org/10.5812/atr.18161
- McLaughlin, G.H. (1969). SMOG grading — a new readability formula. *Journal of Reading*, 12(8), 639–646.
- Stossel, L.M., Segar, N., Gliatto, P., Fallar, R., & Karani, R. (2012). Readability of patient education materials available at the point of care. *Journal of General Internal Medicine*, 27(9), 1165–1170. https://doi.org/10.1007/s11606-012-2046-0

### Tailored / adaptive content

- Krebs, P., Prochaska, J.O., & Rossi, J.S. (2010). A meta-analysis of computer-tailored interventions for health behavior change. *Preventive Medicine*, 51(3–4), 214–221. https://doi.org/10.1016/j.ypmed.2010.06.004
- Noar, S.M., Benac, C.N., & Harris, M.S. (2007). Does tailoring matter? Meta-analytic review of tailored print health behavior change interventions. *Psychological Bulletin*, 133(4), 673–693. https://doi.org/10.1037/0033-2909.133.4.673
- VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems. *Educational Psychologist*, 46(4), 197–221. https://doi.org/10.1080/00461520.2011.611369
- Wood, D., Bruner, J.S., & Ross, G. (1976). The role of tutoring in problem solving. *Journal of Child Psychology and Psychiatry*, 17(2), 89–100. https://doi.org/10.1111/j.1469-7610.1976.tb00381.x

### Microlearning and spaced repetition

- Cepeda, N.J., Pashler, H., Vul, E., Wixted, J.T., & Rohrer, D. (2006). Distributed practice in verbal recall tasks: A review and quantitative synthesis. *Psychological Bulletin*, 132(3), 354–380. https://doi.org/10.1037/0033-2909.132.3.354
- Cepeda, N.J., Vul, E., Rohrer, D., Wixted, J.T., & Pashler, H. (2008). Spacing effects in learning: A temporal ridgeline of optimal retention. *Psychological Science*, 19(11), 1095–1102. https://doi.org/10.1111/j.1467-9280.2008.02209.x
- De Gagne, J.C., Park, H.K., Hall, K., Woodward, A., Yamane, S., & Kim, S.S. (2019). Microlearning in health professions education: Scoping review. *Journal of Medical Internet Research / JMIR Medical Education*, 5(2), e13997. https://doi.org/10.2196/13997
- Dunlosky, J., Rawson, K.A., Marsh, E.J., Nathan, M.J., & Willingham, D.T. (2013). Improving students' learning with effective learning techniques: Promising directions from cognitive and educational psychology. *Psychological Science in the Public Interest*, 14(1), 4–58. https://doi.org/10.1177/1529100612453266
- Hug, T. (Ed.) (2005). *Didactics of Microlearning: Concepts, Discourses and Examples*. Waxmann.
- Kerfoot, B.P., DeWolf, W.C., Masser, B.A., Church, P.A., & Federman, D.D. (2007). Spaced education improves the retention of clinical knowledge by medical students: A randomised controlled trial. *Medical Education*, 41(1), 23–31. https://doi.org/10.1111/j.1365-2929.2006.02644.x
- Kerfoot, B.P., Lawler, E.V., Sokolovskaya, G., Gagnon, D., & Conlin, P.R. (2010). Durable improvements in prostate cancer screening from online spaced education a randomized controlled trial. *American Journal of Preventive Medicine*, 39(5), 472–478. https://doi.org/10.1016/j.amepre.2010.07.016
- Lally, P., van Jaarsveld, C.H.M., Potts, H.W.W., & Wardle, J. (2010). How are habits formed: Modelling habit formation in the real world. *European Journal of Social Psychology*, 40(6), 998–1009. https://doi.org/10.1002/ejsp.674
- Larsen, D.P., Butler, A.C., & Roediger, H.L. (2009). Repeated testing improves long-term retention relative to repeated study: A randomised controlled trial. *Medical Education*, 43(12), 1174–1181. https://doi.org/10.1111/j.1365-2923.2009.03518.x
- Roediger, H.L., & Karpicke, J.D. (2006). Test-enhanced learning: Taking memory tests improves long-term retention. *Psychological Science*, 17(3), 249–255. https://doi.org/10.1111/j.1467-9280.2006.01693.x
- Sepah, S.C., Jiang, L., & Peters, A.L. (2014). Translating the Diabetes Prevention Program into an online social network: Validation against CDC standards. *The Diabetes Educator*, 40(4), 435–443. https://doi.org/10.1177/0145721714531339

### Visual / graphical communication

- Brazilian Ministry of Health (2014). *Dietary Guidelines for the Brazilian Population* (English translation). https://bvsms.saude.gov.br/bvs/publicacoes/dietary_guidelines_brazilian_population.pdf. Accessed 2026-04-28.
- Bleich, S.N., Wolfson, J.A., Jarlenski, M.P., & Block, J.P. (2014). Restaurants with calories displayed on menus: Calorie amounts and content of foods. *American Journal of Public Health*, 104(11), e94–e95. https://doi.org/10.2105/AJPH.2014.302039
- Crockett, R.A., King, S.E., Marteau, T.M., Prevost, A.T., Bignardi, G., Roberts, N.W., Stubbs, B., Hollands, G.J., & Jebb, S.A. (2018). Nutritional labelling for healthier food or non-alcoholic drink purchasing and consumption. *Cochrane Database of Systematic Reviews*, (2), CD009315. https://doi.org/10.1002/14651858.CD009315.pub2
- Egnell, M., Talati, Z., Hercberg, S., Pettigrew, S., & Julia, C. (2018). Objective understanding of front-of-package nutrition labels: An international comparative experimental study across 12 countries. *Nutrients*, 10(10), 1542. https://doi.org/10.3390/nu10101542
- Galesic, M., Garcia-Retamero, R., & Gigerenzer, G. (2009). Using icon arrays to communicate medical risks: Overcoming low numeracy. *Health Psychology*, 28(2), 210–216. https://doi.org/10.1037/a0014474
- Garcia-Retamero, R., & Cokely, E.T. (2017). Designing visual aids that promote risk literacy: A systematic review of health research and evidence-based design heuristics. *Human Factors*, 59(4), 582–627. https://doi.org/10.1177/0018720817690634
- Gigerenzer, G., Gaissmaier, W., Kurz-Milcke, E., Schwartz, L.M., & Woloshin, S. (2007). Helping doctors and patients make sense of health statistics. *Psychological Science in the Public Interest*, 8(2), 53–96. https://doi.org/10.1111/j.1539-6053.2008.00033.x
- Gigerenzer, G., & Hoffrage, U. (1995). How to improve Bayesian reasoning without instruction: Frequency formats. *Psychological Review*, 102(4), 684–704. https://doi.org/10.1037/0033-295X.102.4.684
- Hercberg, S., Touvier, M., & Salas-Salvado, J. on behalf of the Group of European scientists supporting the implementation of Nutri-Score in Europe (2022). The Nutri-Score nutrition label. *International Journal for Vitamin and Nutrition Research*, 92(3-4), 147–157. https://doi.org/10.1024/0300-9831/a000722
- Mhurchu, C.N., Eyles, H., Choi, Y.H. (2017). Effects of a voluntary front-of-pack nutrition labelling system on packaged food reformulation: The Health Star Rating system in New Zealand. *Nutrients*, 9(8), 918. https://doi.org/10.3390/nu9080918
- Public Health England (2016). *The Eatwell Guide*. https://www.gov.uk/government/publications/the-eatwell-guide. Accessed 2026-04-28.
- Sacks, G., Rayner, M., & Swinburn, B. (2009). Impact of front-of-pack 'traffic-light' nutrition labelling on consumer food purchases in the UK. *Health Promotion International*, 24(4), 344–352. https://doi.org/10.1093/heapro/dap032
- Singapore Health Promotion Board (2022). *Nutri-Grade Beverages Industry Guide*. https://www.hpb.gov.sg/. Accessed 2026-04-28.
- Spiegelhalter, D. (2017). Risk and uncertainty communication. *Annual Review of Statistics and Its Application*, 4, 31–60. https://doi.org/10.1146/annurev-statistics-010814-020148
- Spiegelhalter, D., Pearson, M., & Short, I. (2011). Visualizing uncertainty about the future. *Science*, 333(6048), 1393–1400. https://doi.org/10.1126/science.1191181
- Taillie, L.S., Reyes, M., Colchero, M.A., Popkin, B., & Corvalán, C. (2020). An evaluation of Chile's Law of Food Labeling and Advertising on sugar-sweetened beverage purchases from 2015 to 2017: A before-and-after study. *PLOS Medicine*, 17(2), e1003015. https://doi.org/10.1371/journal.pmed.1003015
- USDA / HHS (2020). *Dietary Guidelines for Americans, 2020–2025* (9th ed.). https://www.dietaryguidelines.gov/. Accessed 2026-04-28.
- Willett, W.C., & Stampfer, M.J. (2013). Current evidence on healthy eating. *Annual Review of Public Health*, 34, 77–95. https://doi.org/10.1146/annurev-publhealth-031811-124646

### Uncertainty and confidence visualization

- Buchter, R.B., Fechtelpeter, D., Knelangen, M., Ehrlich, M., & Waltering, A. (2014). Words or numbers? Communicating risk of adverse effects in written consumer health information: A systematic review and meta-analysis. *BMC Medical Research Methodology*, 14, 76. https://doi.org/10.1186/1471-2288-14-76
- Cochrane Norway / Glenton, C., Santesso, N., Rosenbaum, S., Nilsen, E.S., Rader, T., Ciapponi, A., & Dilkes, H. (2010). Presenting the results of Cochrane Systematic Reviews to a consumer audience: A qualitative study. *Medical Decision Making*, 30(5), 566–577. https://doi.org/10.1177/0272989X10375853
- Guyatt, G.H., Oxman, A.D., Vist, G.E., Kunz, R., Falck-Ytter, Y., Alonso-Coello, P., Schünemann, H.J. (2008). GRADE: An emerging consensus on rating quality of evidence and strength of recommendations. *British Medical Journal*, 336(7650), 924–926. https://doi.org/10.1136/bmj.39489.470347.AD
- Gustafson, A., & Rice, R.E. (2020). A review of the effects of uncertainty in public science communication. *Public Understanding of Science*, 29(6), 614–633. https://doi.org/10.1177/0963662520942122
- NICE (2014). *Developing NICE Guidelines: The Manual* (PMG20). National Institute for Health and Care Excellence. https://www.nice.org.uk/process/pmg20. Accessed 2026-04-28.
- Rosenbaum, S.E., Glenton, C., & Oxman, A.D. (2010). Summary-of-findings tables in Cochrane reviews improved understanding and rapid retrieval of key information. *Journal of Clinical Epidemiology*, 63(6), 620–626. https://doi.org/10.1016/j.jclinepi.2009.12.014
- Santesso, N., Rader, T., Nilsen, E.S., Glenton, C., Rosenbaum, S., Ciapponi, A., et al. (2015). A summary-of-findings table for Cochrane reviews improved understanding and accessibility of information: A randomized trial. *Journal of Clinical Epidemiology*, 68(2), 182–190. https://doi.org/10.1016/j.jclinepi.2014.04.009
- Schünemann, H.J., Oxman, A.D., Higgins, J.P.T., Vist, G.E., Glasziou, P., Akl, E., & Guyatt, G.H. (2019). Chapter 14: Completing 'Summary of findings' tables and grading the certainty of the evidence. In Higgins, J.P.T., et al. (eds.) *Cochrane Handbook for Systematic Reviews of Interventions*. https://training.cochrane.org/handbook. Accessed 2026-04-28.
- van der Bles, A.M., van der Linden, S., Freeman, A.L.J., Mitchell, J., Galvao, A.B., Zaval, L., & Spiegelhalter, D.J. (2020). The effects of communicating uncertainty on public trust in facts and numbers. *Proceedings of the National Academy of Sciences*, 117(14), 7672–7683. https://doi.org/10.1073/pnas.1913678117
- Vandvik, P.O., Brandt, L., Alonso-Coello, P., Treweek, S., Akl, E.A., Kristiansen, A., et al. (2013). Creating clinical practice guidelines we can trust, use, and share: A new era is imminent. *Chest*, 144(2), 381–389. https://doi.org/10.1378/chest.13-0746

### Causal explanation depth

- Lombrozo, T. (2006). The structure and function of explanations. *Trends in Cognitive Sciences*, 10(10), 464–470. https://doi.org/10.1016/j.tics.2006.08.004
- Miller, T. (2019). Explanation in artificial intelligence: Insights from the social sciences. *Artificial Intelligence*, 267, 1–38. https://doi.org/10.1016/j.artint.2018.07.007
- Petty, R.E., & Cacioppo, J.T. (1986). The elaboration likelihood model of persuasion. *Advances in Experimental Social Psychology*, 19, 123–205. https://doi.org/10.1016/S0065-2601(08)60214-2
- Rozenblit, L., & Keil, F. (2002). The misunderstood limits of folk science: An illusion of explanatory depth. *Cognitive Science*, 26(5), 521–562. https://doi.org/10.1207/s15516709cog2605_1
- Williams, J.J., & Lombrozo, T. (2010). The role of explanation in discovery and generalization: Evidence from category learning. *Cognitive Science*, 34(5), 776–806. https://doi.org/10.1111/j.1551-6709.2010.01113.x
- Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., Chi, E.H., Le, Q.V., & Zhou, D. (2022). Chain-of-thought prompting elicits reasoning in large language models. *Advances in Neural Information Processing Systems*, 35, 24824–24837. https://proceedings.neurips.cc/paper_files/paper/2022/hash/9d5609613524ecf4f15af0f7b31abca4-Abstract-Conference.html. Accessed 2026-04-28.

### Adult learning theory

- Brookfield, S.D. (1986). *Understanding and Facilitating Adult Learning: A Comprehensive Analysis of Principles and Effective Practices*. Jossey-Bass.
- Knowles, M.S. (1980). *The Modern Practice of Adult Education: From Pedagogy to Andragogy* (Revised and updated). Cambridge Adult Education.
- Knowles, M.S., Holton, E.F., & Swanson, R.A. (2015). *The Adult Learner: The Definitive Classic in Adult Education and Human Resource Development* (8th ed.). Routledge.
- Kolb, D.A. (1984). *Experiential Learning: Experience as the Source of Learning and Development*. Prentice Hall.
- Kolb, A.Y., & Kolb, D.A. (2017). *The Experiential Educator: Principles and Practices of Experiential Learning*. EBLS Press.
- Mezirow, J. (1991). *Transformative Dimensions of Adult Learning*. Jossey-Bass.
- Mezirow, J. (Ed.) (2000). *Learning as Transformation: Critical Perspectives on a Theory in Progress*. Jossey-Bass.
- Tough, A. (1971). *The Adult's Learning Projects: A Fresh Approach to Theory and Practice in Adult Learning*. Ontario Institute for Studies in Education.

### Trust + credibility in AI-mediated health information

- Ayers, J.W., Poliak, A., Dredze, M., Leas, E.C., Zhu, Z., Kelley, J.B., Faix, D.J., Goodman, A.M., Longhurst, C.A., Hogarth, M., & Smith, D.M. (2023). Comparing physician and artificial intelligence chatbot responses to patient questions posted to a public social media forum. *JAMA Internal Medicine*, 183(6), 589–596. https://doi.org/10.1001/jamainternmed.2023.1838
- ICMJE — International Committee of Medical Journal Editors (2023). *Recommendations for the Conduct, Reporting, Editing, and Publication of Scholarly Work in Medical Journals* — AI authorship statement. https://www.icmje.org/recommendations/. Accessed 2026-04-28.

### Plain-language clinical communication

- Cochrane (2019). *Plain Language Summaries — Standards and Guidance*. Cochrane Library Editorial Office. https://community.cochrane.org/help/tools-and-software/revman/plain-language-summary-standards. Accessed 2026-04-28.
- ISO — International Organization for Standardization (2023). *ISO 24495-1:2023 Plain Language — Part 1: Governing Principles and Guidelines*. https://www.iso.org/standard/78907.html. Accessed 2026-04-28.
- Plain Writing Act of 2010, Pub.L. 111-274, 124 Stat. 2861. https://www.govinfo.gov/app/details/PLAW-111publ274. Accessed 2026-04-28.
- Plain Language Action and Information Network. *Federal Plain Language Guidelines*. https://www.plainlanguage.gov/guidelines/. Accessed 2026-04-28.
- USAID / Johns Hopkins Center for Communication Programs. *Health COMpass — Strategic Communication for Behavior Change Resources*. https://www.thehealthcompass.org/. Accessed 2026-04-28.

> Add new sources to [sources.md](../00-meta/sources.md) when added (separate consolidation pass — do not edit during this sweep).
