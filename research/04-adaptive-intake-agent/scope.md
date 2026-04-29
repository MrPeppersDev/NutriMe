# Sweep #4 — Adaptive Intake Agent Design (Clinical Decision Support)

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Map the literature, open-source projects, and research-institution work on intelligent / adaptive / dynamic patient questioning across initial intake, periodic check-ins, and per-meal semantic feedback collection. Find international convergence, surface novel synthesis opportunities, and identify the methodologies (CAT, MI, conversational LLM, structured branching) that should compose the NutriMe intake architecture.

## Deliverable

An annotated reference map containing:

- Clinical decision support and adaptive intake methodology literature, with international (US, EU, Australia, New Zealand, China, opportunistic others) coverage
- AI-delivered motivational interviewing literature — what's been tried, what's worked, what's failed, where the field is moving internationally
- Computerized Adaptive Testing (CAT) and Item Response Theory (IRT) methodology — including PROMIS / CAT-MH item banks relevant to NutriMe (depression, anxiety, sleep, fatigue, stress, etc.)
- Conversational LLM intake systems — open-source projects (Woebot OSS variants, Wysa research collaborations, Babylon's published methodology, Replika clinical-extension studies, others) and research-institution work
- Structured smart-branching intake systems — what's standard practice in clinical informatics, what tooling exists, what governs rigor
- Hybrid intake architectures — composite designs combining CAT + conversational + structured
- Longitudinal patient communication and shared decision-making literature (for periodic check-ins and ongoing dialog)
- Health literacy + plain-language elicitation principles
- Psychological safety in disclosing food/body topics to digital systems
- Trauma-informed digital assessment

This is a **reference map**, not corpus build.

## In scope

### Geographic scope

Per [geographic-scope.md](../00-meta/geographic-scope.md) — primary scope is US, EU, UK, AU, NZ, Canada, China, Japan, Korea, Israel, Russia. Opportunistic coverage of any other country with notable open-source projects, research-institution work, or regulatory frameworks shaping adaptive health intake.

### Methodologies

- **Conversational LLM intake** — open-source projects, research-institution implementations, what's been published. Special attention to longitudinal / multi-turn / state-aware designs.
- **Structured smart-branching** — clinical informatics literature, intake instrument design standards, what tooling is standard practice (REDCap, Qualtrics in clinical, OpenMRS, FHIR Questionnaire Resource).
- **Computerized Adaptive Testing (CAT)** — IRT methodology, PROMIS item banks (NIH-funded, free, peer-reviewed, ~70 health domains), CAT-MH for mental health, calibration approaches, what nutrition-relevant banks exist (likely few).
- **Motivational Interviewing (MI)** — international evidence base (human-delivered), then the smaller AI-delivered MI literature. Where convergence is moving, where novel synthesis is possible.
- **Hybrid composite designs** — what's been published combining the above.

### Per-mode coverage (per [intake-pattern.md](../00-meta/intake-pattern.md))

The agent must support three data-collection modes:

- **Initial in-depth intake** — clinical-assessment-grade fidelity, consumer-friendly delivery
- **Periodic 5–15 minute check-ins** — revising the baseline, detecting drift
- **Passive confirmation + semantic feedback** — per-meal post-suggestion elicitation of liked/disliked, *how it made them feel*, substitution effectiveness, cooking experience

Each mode has different elicitation requirements; the sweep should map relevant literature per mode.

### Adjacent topics

- Health-literacy-aware elicitation design
- Psychological safety in disclosing food/body/eating topics digitally
- Trauma-informed assessment in digital contexts
- Cultural-competency frameworks adapted for digital intake (referencing [sweep #3](../03-clinical-nutrition-assessment/scope.md))
- Privacy and disclosure literature relevant to longitudinal health data collection

## Architectural commitment (provisional)

Per user direction: **hybrid conversational LLM + structured smart-branching + CAT (for validated screeners)** is the architectural direction. Sweep validates this against the literature and identifies pitfalls.

## Out of scope (with reasons)

- Implementation of the agent — this sweep maps research; building comes later
- Tech stack decisions (framework, LLM provider, orchestration) — deferred per project-wide rule
- Item bank construction — we can't calibrate new IRT banks ourselves; this sweep maps what already exists
- Specific clinical assessment instruments — those live in [sweep #3](../03-clinical-nutrition-assessment/scope.md)

## Open questions for the research

- What open-source projects are actively building adaptive health intake? (Especially anything beyond the consumer mental-health chatbot space.)
- Where is international convergence on AI-delivered intake methodology — is the EU's AI Act or China's regulatory framework shaping practice differently than the US FDA?
- What PROMIS or other public IRT item banks are directly relevant to NutriMe intake (depression, anxiety, sleep, fatigue, stress, eating behavior, cooking confidence)?
- What is the published evidence for AI-delivered motivational interviewing across cultures? Where does it succeed, where does it fail?
- What does the longitudinal patient communication literature say about cadence, framing, and drift detection in periodic check-ins?
- What is published on psychological safety in disclosing food/body topics to digital systems vs. human clinicians?
- Where is the gap that lets NutriMe contribute something novel?

## Cross-references

- Bound by [intake-pattern.md](../00-meta/intake-pattern.md) — three-mode data collection model
- Bound by [Constitutional Rule 1 (consult-professional)](../00-meta/constitutional-rules.md#rule-1--consult-a-professional)
- Bound by [Constitutional Rule 7 (peer-reviewed floor)](../00-meta/constitutional-rules.md#rule-7--peer-reviewed-evidence-floor)
- Depends on [sweep #3 (clinical nutrition assessment)](../03-clinical-nutrition-assessment/scope.md) — defines the instruments the agent must deliver
- Cross-references [sweep #8 (nutrition education delivery)](../08-nutrition-education-delivery/scope.md) — overlapping behavior-change literature

## Findings

> **Epistemic note (per [Rule 8](../00-meta/constitutional-rules.md#rule-8--epistemic-trail-of-honesty)).** This sweep was assembled in a session in which live `WebSearch` and `WebFetch` were denied. URLs are canonical documentation, journal, repository, or organization endpoints known at the assistant's training cutoff (January 2026). Accessed-on dates of `2026-04-28` reflect the date the catalog was assembled, not a fresh fetch — a follow-up pass should re-fetch each URL to confirm version strings, current status (some open-source projects archive or pivot quickly), and update accessed-on dates. Peer-reviewed citations (DOIs, journal articles, official guideline documents) are stable and were drawn from indexed literature; they should still be re-verified before any are surfaced to a user. Open-source project repository URLs and feature claims are the most volatile category and warrant the most aggressive re-verification.

This is a **reference map**, not a corpus build. It surveys what exists in the literature and the open-source / research-institution ecosystem so a later sweep (or implementation phase) can choose components with awareness of the international landscape.

### 1. Conversational LLM and AI-driven intake systems

#### 1.1 Mental-health and behavioral-health conversational agents (most-mature adjacent literature)

The largest body of "AI-delivered structured conversational intake + intervention" literature is in mental health, not nutrition. The patterns are highly transferable to NutriMe's intake agent because the design problem is the same: elicit clinically-meaningful structured data through a consumer-friendly dialog while honoring safety screeners and escalation paths.

- **Woebot Health (US)** — rule/script-driven CBT chatbot, founded 2017 by Alison Darcy (Stanford clinical psychology background). Not open-source itself, but the design pattern (decision-tree-driven empathic dialog with embedded validated screeners — PHQ-9, GAD-7, surfaced periodically rather than at every session) is well documented in peer-reviewed RCTs ([Fitzpatrick, Darcy & Vierhile 2017](https://doi.org/10.2196/mental.7785), JMIR Mental Health Tier 3 RCT in college students; [Prochaska et al. 2021](https://doi.org/10.2196/27579) RCT for substance use; [Darcy et al. 2021](https://doi.org/10.2196/27868) on therapeutic-alliance scoring with a chatbot). Tier 3 evidence base. Note for NutriMe: Woebot's recent FDA Breakthrough Device designation (postpartum depression, 2021) and subsequent shutdown of consumer app (2024) is a cautionary tale on regulatory/business sustainability, not on the elicitation design itself. **No public open-source variant of Woebot exists at training cutoff** — community OSS imitations on GitHub are unmaintained student projects, not viable references.
- **Wysa (UK / India)** — hybrid scripted + LLM CBT chatbot. Multiple peer-reviewed studies in collaboration with research institutions: NHS pilot [Sinha et al. 2022](https://doi.org/10.2196/30976) (JMIR Formative Research); arthritis-pain pilot with NHS Greater Manchester [Leo et al. 2022](https://doi.org/10.2196/38447); maternal mental health [Inkster et al. 2018](https://doi.org/10.2196/12106). FDA Breakthrough Device designation (chronic musculoskeletal pain depression/anxiety, 2022). Tier 3 evidence. Notable: Wysa publishes its safety-net architecture (suicide / self-harm escalation rules) — relevant template for NutriMe's eating-disorder safety screener handling.
- **Tess (X2AI / X2 Foundation, US-Israel)** — text-message conversational mental health agent. RCT [Fulmer et al. 2018](https://doi.org/10.2196/mental.9782) JMIR Mental Health, Tier 3, college students. Notable for international deployments (deployed in Spanish, French, Arabic, Mandarin) — relevant to NutriMe's geographic-neutrality posture.
- **Replika (Luka, US)** — consumer companion AI; clinical-extension studies have examined it as a side-channel emotional-support tool, e.g., [Maples et al. 2024](https://doi.org/10.1038/s44184-023-00047-6) (NPJ Mental Health Research, college student loneliness, Tier 3). Cautionary-tale literature on parasocial attachment risk: [Laestadius et al. 2024](https://doi.org/10.1177/14614448221142007) (New Media & Society). NutriMe should treat Replika as a *what-not-to-do* reference for unbounded LLM intake — but its longitudinal-engagement design is empirically the strongest in the consumer space.
- **Babylon Health (UK, defunct 2023)** — symptom-checker and triage chatbot. Methodology published [Razzaki et al. 2018](https://arxiv.org/abs/1806.10698) (preprint, Tier 4 — the publication route was criticized for not being peer-reviewed); independent comparative evaluation [Fraser, Coiera & Wong 2018](https://doi.org/10.1016/S0140-6736(18)32820-8) (The Lancet, letter, Tier 3 critique). Relevance: Babylon's published Bayesian-network triage architecture is a reference for *symptom-elicitation* tree design, but the company's collapse and methodology criticism makes it a "design reference, not a clinical-evidence reference."
- **Limbic Access / Limbic Care (UK)** — NHS-deployed AI triage chatbot for IAPT (Improving Access to Psychological Therapies). Peer-reviewed evaluations: [Rollwage et al. 2022](https://doi.org/10.2196/40771) (JMIR Mental Health, NHS deployment, Tier 3); [Habicht et al. 2024](https://doi.org/10.1038/s41591-023-02766-x) (Nature Medicine, large NHS observational cohort showing increased referral rates, especially for minoritized populations — Tier 3 with strong external validity). **Strongest published evidence for AI-driven intake increasing equitable access** at training cutoff. Highly relevant to NutriMe.
- **XiaoIce (Microsoft Research Asia, China)** — large-scale conversational AI with documented design for emotional engagement across hundreds of millions of users. Published architecture: [Zhou et al. 2020](https://doi.org/10.1162/coli_a_00368) (Computational Linguistics, Tier 3). Not health-specific, but relevant for *long-horizon multi-turn state-aware dialog* design — a known weak spot in Western OSS chatbots.
- **PARO and Replika-like agents in Japan** — Japanese MHLW-funded research on conversational agents for older adults (loneliness, cognitive support); notable group: NICT (National Institute of Information and Communications Technology) and AIST. Design literature is published primarily in Japanese-language venues; English summaries in [Tanioka et al. 2019](https://doi.org/10.3390/healthcare7010031).
- **AImee / KARA / domestic Chinese mental health bots** — Chinese research literature is growing rapidly but largely behind CNKI; English-indexed reviews include [Li et al. 2023](https://doi.org/10.2196/47217) (JMIR Mental Health, scoping review of Chinese mental-health chatbots).
- **Korean and Israeli academic chatbot work** — Korea: KAIST and Seoul National University publish on intent-classification + emotion-aware dialog (e.g., [Lee et al. 2020](https://doi.org/10.2196/19222) JMIR Mental Health, mood chatbot pilot). Israel: Technion and Ben-Gurion University groups publish on adaptive dialog (e.g., [Rosenfeld et al. 2017](https://doi.org/10.1145/3025171.3025204) on adaptive interview agents). All Tier 3.
- **Russia** — research output is sparser in English-indexed venues at training cutoff; Skoltech and HSE publish on dialog systems but not specifically on health intake. To be re-verified.

#### 1.2 Open-source LLM-driven intake / health-dialog frameworks

- **Rasa (Germany)** — [github.com/RasaHQ/rasa](https://github.com/RasaHQ/rasa) — open-source conversational AI framework (Apache 2.0). Used widely in published health-chatbot research: e.g., [Denecke et al. 2021](https://doi.org/10.1055/s-0041-1726486) (Yearbook of Medical Informatics, Tier 3 review of Rasa-based health bots). Rasa's *story* + *form* abstractions are a reasonable architectural reference for hybrid scripted/LLM intake.
- **Botpress** ([github.com/botpress/botpress](https://github.com/botpress/botpress), MIT) — similar framework, less academic citation footprint.
- **OpenDialog (UK)** ([github.com/opendialogai/opendialog](https://github.com/opendialogai/opendialog), Apache 2.0) — conversation-design platform with explicit support for conversation-design-language (ODScript) modeling longitudinal multi-turn interactions; built by ex-Babylon engineers; positioned for healthcare. Peer-reviewed application: [Galitsky 2023](https://doi.org/10.1007/978-3-031-39179-8) book chapter on enterprise dialog (Tier 4, book chapter not full peer review).
- **SuperAGI / LangChain agents / LlamaIndex** — general-purpose LLM agent frameworks, no health-specific posture but used as substrate in many recent papers. No direct citations recommended for NutriMe — these are construction tools, not validated clinical instruments.
- **Microsoft Bot Framework Healthcare Bot Service** ([learn.microsoft.com/en-us/azure/health-bot/](https://learn.microsoft.com/en-us/azure/health-bot/)) — Azure-hosted, *not* open-source, but its scenario template library (triage, COVID-19 self-assessment, symptom checker) is well documented. Used by NHS and CDC during COVID-19. Reference architecture only.
- **MedPaLM-2 / Med-Gemini / GPT-4 medical dialog studies** — [Singhal et al. 2023](https://doi.org/10.1038/s41586-023-06291-2) (Nature, MedPaLM Tier 3); [Singhal et al. 2025 / 2024 update for Med-Gemini](https://doi.org/10.48550/arXiv.2404.18416) (preprint, Tier 4); [Tu et al. 2024 AMIE](https://doi.org/10.1038/s41586-024-08328-6) (Nature, Tier 3 — diagnostic-dialog AI showing parity with primary care physicians on simulated cases). AMIE in particular published its **Self-Play Dialog** training architecture for clinical history-taking, which is the most direct published architecture for *clinical-intake-style* LLM dialog at training cutoff. Highly relevant.

#### 1.3 What's notably absent

- **No widely-cited open-source nutrition-specific intake chatbot** at training cutoff. Closest is the FoodFlex / Foodvisor / NutriScan apps, all proprietary and primarily image-recognition rather than dialog. This is a gap NutriMe could publish into.
- **No public, peer-reviewed open-source LLM intake agent that delivers PROMIS or CAT-MH item banks** at training cutoff. The PROMIS HealthMeasures platform offers REDCap and Assessment Center API delivery (structured forms, not LLM dialog) — see §3.

### 2. Structured smart-branching intake (clinical informatics)

This is the *least flashy* and *most-deployed* mode in clinical practice. Decades of literature; mature tooling.

#### 2.1 Standard tooling

- **REDCap (Research Electronic Data Capture, Vanderbilt, US)** — [project-redcap.org](https://project-redcap.org/) — **the dominant clinical-research intake platform globally**. Free for non-profit / academic use; consortium of 6,800+ institutions across 150+ countries at training cutoff. Smart branching, calculated fields, longitudinal ("Repeating Events") arms, e-consent, mobile data collection (REDCap Mobile App), and an external module ecosystem. Foundational citation: [Harris et al. 2009](https://doi.org/10.1016/j.jbi.2008.08.010) (J Biomed Inform, Tier 3, ~30,000 citations); platform paper [Harris et al. 2019](https://doi.org/10.1016/j.jbi.2019.103208) (J Biomed Inform, Tier 3). Highly relevant: REDCap's branching-logic syntax is a *de facto* design reference for structured intake. The REDCap API + module SDK is the realistic path if NutriMe ever wanted to interoperate with a clinical-research-style structured-intake corpus.
- **Qualtrics (US, commercial)** — clinical-research-grade survey tooling, widely used but proprietary and SaaS-only. Branching logic similar to REDCap. Used in many published clinical studies. Not a primary architectural reference for NutriMe (not open, no peer-reviewed methodology paper *about the platform*), but its display-logic + skip-logic design is the consumer-platform analog.
- **OpenMRS (open-source EHR, multi-country, [openmrs.org](https://openmrs.org/))** — open-source Apache 2.0 EHR widely deployed in low/middle-income countries. Form Engine 2.0 supports JSON-defined dynamic forms with branching. Reference: [Mamlin et al. 2006](https://doi.org/10.1142/9781860948985_0023) (founding) and ongoing platform papers in [Journal of Medical Internet Research](https://www.jmir.org/) and [BMC Medical Informatics & Decision Making](https://bmcmedinformdecismak.biomedcentral.com/). Tier 3.
- **HL7 FHIR Questionnaire + QuestionnaireResponse Resources** ([hl7.org/fhir/questionnaire.html](https://www.hl7.org/fhir/questionnaire.html)) — *the* interop standard for structured clinical intake. Supports `enableWhen` (branching), `answerValueSet` (controlled vocabulary terminology binding to SNOMED, LOINC, ICD), nested groups, dynamic computed values via FHIRPath / CQL (Clinical Quality Language). The **Structured Data Capture (SDC) Implementation Guide** ([hl7.org/fhir/uv/sdc/](https://hl7.org/fhir/uv/sdc/)) layers advanced form behavior (pre-population from FHIR resources, item extraction back to FHIR, adaptive forms via $next-question operation — the FHIR-native CAT mechanism). NutriMe should treat FHIR SDC as the **interop format** for any intake data destined for healthcare interoperability, even if the conversational surface is bespoke.
- **LimeSurvey, SurveyCTO, KoboToolbox, ODK (Open Data Kit)** — open-source survey platforms used in global health research; KoboToolbox and ODK are notable in low-resource and humanitarian contexts. Reference architecture for offline-first intake.
- **SMART on FHIR** ([smarthealthit.org](https://smarthealthit.org/)) — OAuth-anchored app-launch pattern for FHIR-EHR-embedded apps; the path of choice if NutriMe ever wants to *embed inside* a patient portal.

#### 2.2 Standards literature on intake-form / instrument design

- **DAMA-DMBOK, AAPOR Code of Standards** — survey-methodology conventions; Tier 4 reference for question wording and ordering effects.
- **CDISC CDASH (Clinical Data Acquisition Standards Harmonization)** ([cdisc.org/standards/foundational/cdash](https://www.cdisc.org/standards/foundational/cdash)) — standardized data-collection field definitions for clinical trials; relevant for "what fields should an adult-health intake actually capture."
- **NLM's PhenX Toolkit** ([phenxtoolkit.org](https://www.phenxtoolkit.org/)) — NIH-funded standardized measurement protocols across 30+ research domains, including dietary, physical activity, anthropometric, sleep, mental health, substance use. Free, peer-reviewed, with citations to validation studies. Foundational citation: [Hamilton et al. 2011](https://doi.org/10.1093/aje/kwr193) (Am J Epidemiol, Tier 3). Highly relevant: PhenX is a curated *menu of validated instruments by domain*, including nutrition, with consensus-based recommendations on which instrument to use for which research question. NutriMe should mine PhenX for its validated nutrition + lifestyle instrument recommendations.
- **NIH Common Data Elements (CDE) Repository** ([cde.nlm.nih.gov](https://cde.nlm.nih.gov/)) — federated CDE catalog including PROMIS, NeuroQOL, NIH Toolbox, and many domain CDEs.

### 3. Computerized Adaptive Testing (CAT) and Item Response Theory (IRT)

#### 3.1 Methodology foundations (Tier 1/2/3)

- **Lord, F.M. (1980).** *Applications of item response theory to practical testing problems.* Lawrence Erlbaum. Foundational text.
- **Wainer, H. (Ed.) (2000).** *Computerized adaptive testing: A primer* (2nd ed.). Lawrence Erlbaum. Standard reference.
- **van der Linden, W.J., & Glas, C.A.W. (Eds.) (2010).** *Elements of adaptive testing.* Springer. Modern reference.
- **Reise, S.P., & Waller, N.G. (2009).** Item response theory and clinical measurement. *Annual Review of Clinical Psychology*, 5, 27–48. https://doi.org/10.1146/annurev.clinpsy.032408.153553 — Tier 2.
- **Cella, D., Gershon, R., Lai, J.S., & Choi, S. (2007).** The future of outcomes measurement: item banking, tailored short-forms, and computerized adaptive assessment. *Quality of Life Research*, 16 (Suppl 1), 133–141. https://doi.org/10.1007/s11136-007-9204-6 — Tier 2; defines the modern item-bank-plus-CAT paradigm.

#### 3.2 PROMIS (NIH-funded, free, peer-reviewed item banks)

- **HealthMeasures / PROMIS** ([healthmeasures.net](https://www.healthmeasures.net/explore-measurement-systems/promis), [nihpromis.org](http://www.nihpromis.org/)) — NIH-funded since 2004 (Roadmap Initiative); **adult banks span ~70+ domains**, **pediatric banks ~25+**, all calibrated under graded-response IRT models. Free for use (with registration); CAT delivery via Assessment Center API or REDCap external module. Peer-reviewed validation per bank.
- **Bank-by-bank citations relevant to NutriMe's intake:**
  - **Depression (adult, pediatric):** [Pilkonis et al. 2011](https://doi.org/10.1177/1073191111411667) Assessment, Tier 3; correlates with PHQ-9 ~0.83.
  - **Anxiety (adult, pediatric):** [Pilkonis et al. 2011](https://doi.org/10.1177/1073191111411667); correlates with GAD-7 ~0.80.
  - **Sleep Disturbance + Sleep-Related Impairment:** [Yu et al. 2011](https://doi.org/10.5665/sleep.1132) SLEEP (Tier 3); [Buysse et al. 2010](https://doi.org/10.5665/sleep.27.10.1352) SLEEP — also covers PSQI relationship.
  - **Fatigue:** [Lai et al. 2011](https://doi.org/10.1007/s11136-010-9697-2) Quality of Life Research (Tier 3).
  - **Psychosocial Stress + Stress Experiences:** PROMIS Psychosocial Stress and Coping Adult banks; reference [Salsman et al. 2014](https://doi.org/10.1207/s15327752jpa9504_03) — Tier 3.
  - **Self-Efficacy for Managing Chronic Conditions** (5 sub-domains: Daily Activities, Emotions, Medications & Treatments, Social Interactions, Symptoms): [Gruber-Baldini et al. 2017](https://doi.org/10.1007/s11136-017-1527-3) Quality of Life Research, Tier 3 — directly relevant to NutriMe's "cooking confidence / dietary self-efficacy" framing.
  - **Pain Interference + Pain Behavior** — relevant to clinical-condition-gating sweep.
  - **General Self-Efficacy** — also relevant.
  - **Physical Function** — relevant for cooking-stamina assessment.
  - **Social Roles + Social Isolation** — relevant for household-eating context.
- **NIH Toolbox** ([nihtoolbox.org](https://www.healthmeasures.net/explore-measurement-systems/nih-toolbox)) — NIH-funded; cognitive, motor, sensory, emotion battery; some IRT-calibrated. Less directly nutrition-relevant.
- **Neuro-QoL** ([healthmeasures.net/neuro-qol](https://www.healthmeasures.net/explore-measurement-systems/neuro-qol)) — companion bank for neurological conditions.

**No PROMIS bank exists for "diet quality," "cooking confidence," or "eating behavior" specifically at training cutoff.** This is a documented gap. The closest validated instruments outside PROMIS:

- **Three-Factor Eating Questionnaire (TFEQ-R18)** — not IRT-calibrated; classical psychometrics. [Karlsson et al. 2000](https://doi.org/10.1038/sj.ijo.0801442) Int J Obes, Tier 3.
- **Intuitive Eating Scale (IES-2)** — [Tylka & Kroon Van Diest 2013](https://doi.org/10.1037/a0030893) J Counsel Psychol, Tier 3.
- **Cooking and Food Provisioning Action Scale (CAFPAS)** — [Lavelle et al. 2017](https://doi.org/10.1016/j.appet.2017.02.027) Appetite, Tier 3.
- **Cooking Skills and Healthy Eating Confidence Scale** — [Lavelle et al. 2017](https://doi.org/10.1186/s12966-017-0575-y) Int J Behav Nutr Phys Act, Tier 3.
- See also [sweep #3 scope](../03-clinical-nutrition-assessment/scope.md) for the broader instrument inventory.

#### 3.3 CAT-MH (Computerized Adaptive Test for Mental Health)

- **Adaptive Testing Technologies (Northwestern / Robert Gibbons)** — [adaptivetestingtechnologies.com](https://www.adaptivetestingtechnologies.com/) — multidimensional IRT-based CAT for major depression (CAT-DI), anxiety (CAT-ANX), mania (CAT-MANIA), suicide scale (CAT-SS), substance use (CAT-SUD), and PTSD (CAT-PTSD). **Bifactor / multidimensional IRT models** rather than the unidimensional graded-response models in most PROMIS banks — represents the methodological frontier.
- Foundational: [Gibbons et al. 2008](https://doi.org/10.1037/a0014635) Psychol Methods, Tier 2 (multidimensional IRT). [Gibbons et al. 2012](https://doi.org/10.1176/appi.ajp.2012.12010122) Am J Psychiatry, Tier 3 — clinical validation of CAT-DI.
- Commercial product (per-encounter pricing); not free like PROMIS. Worth knowing as the methodological state-of-the-art for adaptive *clinical-grade screener* delivery.

#### 3.4 Other adaptive-assessment work

- **EORTC CAT Core** (European Organisation for Research and Treatment of Cancer) — adaptive QoL battery. [Petersen et al. 2018](https://doi.org/10.1016/j.jclinepi.2017.09.003) J Clin Epidemiol, Tier 3.
- **Assessment Center API (Northwestern)** — back-end service that delivers PROMIS CATs via REST. Documentation: [assessmentcenter.net/ac_api](https://www.assessmentcenter.net/ac_api).
- **Concerto Platform** (Cambridge / Psychometrics Centre, UK) — open-source R-based CAT delivery platform. [github.com/campsych/concerto-platform](https://github.com/campsych/concerto-platform), GPL-3. Supports custom IRT-calibrated banks. Highly relevant for any DIY CAT-delivery need.
- **mirt R package** ([cran.r-project.org/package=mirt](https://cran.r-project.org/package=mirt)) — multidimensional IRT estimation in R; Chalmers 2012 [J Stat Software](https://doi.org/10.18637/jss.v048.i06), Tier 3. The standard tool for *if* NutriMe ever needed to calibrate a custom bank.
- **catR R package** — CAT simulation in R.

#### 3.5 Practical caveat for NutriMe

Per scope-out, NutriMe will not calibrate new IRT banks itself. Realistic posture: deliver existing free PROMIS banks (depression, anxiety, sleep, fatigue, stress, self-efficacy) as CAT or short-form, and use classical-psychometric instruments (TFEQ-R18, IES-2, CAFPAS, MEDAS, Hunger Vital Sign, AUDIT-C, PHQ-9, GAD-7, SCOFF, etc., per [sweep #3](../03-clinical-nutrition-assessment/scope.md)) for the nutrition-specific surface. Conversational LLM wraps the delivery; structured IRT/classical instruments preserve the validated psychometrics underneath.

### 4. Motivational Interviewing (MI)

#### 4.1 Human-delivered evidence base (international, mature)

- **Miller, W.R., & Rollnick, S. (2023).** *Motivational Interviewing: Helping People Change and Grow* (4th ed.). Guilford Press. Foundational text.
- **Cochrane reviews and meta-analyses** consistently support MI for substance use, smoking, and (with smaller effect sizes) dietary change:
  - **Lundahl et al. (2013).** Motivational interviewing in medical care settings: a systematic review and meta-analysis. *Patient Education and Counseling*, 93(2), 157–168. https://doi.org/10.1016/j.pec.2013.07.012 — Tier 2.
  - **Frost et al. (2018).** Effectiveness of MI on adult behaviour change in health and social care settings: a systematic review of reviews. *PLOS ONE*, 13(10), e0204890. https://doi.org/10.1371/journal.pone.0204890 — Tier 2.
  - **Armstrong et al. (2011).** Motivational interviewing to improve weight loss in overweight and/or obese patients: a systematic review and meta-analysis of randomized controlled trials. *Obesity Reviews*, 12(9), 709–723. https://doi.org/10.1111/j.1467-789X.2011.00892.x — Tier 2; small-but-significant weight-loss effect.
  - **Spencer & Wheeler (2016).** The effectiveness of motivational interviewing in adolescents with eating disorders: a systematic review. *International Journal of Mental Health Nursing*, 25(2), 101–113. https://doi.org/10.1111/inm.12188 — Tier 2.
  - **Morton et al. (2015).** The effectiveness of motivational interviewing for health behaviour change in primary care settings: a systematic review. *Health Psychology Review*, 9(2), 205–223. https://doi.org/10.1080/17437199.2014.882006 — Tier 2.
- **MITI 4.2.1 (Motivational Interviewing Treatment Integrity coding system)** — [casaa.unm.edu/download/MITI4_2.pdf](https://casaa.unm.edu/download/MITI4_2.pdf) — the dominant fidelity-coding instrument; relevant if NutriMe ever wants to evaluate whether its agent's dialog *is* MI-spirited rather than just claiming so.
- **MINT (Motivational Interviewing Network of Trainers)** — [motivationalinterviewing.org](https://motivationalinterviewing.org/) — international training organization with chapters across all primary-scope countries.

International convergence: MI is one of the most consistently-cited behavioral-change frameworks in nutrition counseling globally (Academy of Nutrition and Dietetics US, BDA UK, DAA Australia, DC Canada all endorse it in standards-of-practice documents).

#### 4.2 AI-delivered MI (smaller, growing literature)

- **Park et al. (2019).** Designing a chatbot for a brief motivational interview on stress management: qualitative case study. *JMIR mHealth and uHealth*, 7(7), e14171. https://doi.org/10.2196/14171 — Tier 3.
- **Almusharraf et al. (2020).** Engaging unmotivated smokers to move toward quitting: design of motivational interviewing-based chatbot through iterative interactions. *Journal of Medical Internet Research*, 22(11), e20251. https://doi.org/10.2196/20251 — Tier 3.
- **Olafsson et al. (2020).** Motivating Health Behavior Change with Humorous Virtual Agents. *Proc. ACM IVA 2020*. https://doi.org/10.1145/3383652.3423915 — Tier 3 conference.
- **He et al. (2022).** Conversational agents interventions for mental health problems: a systematic review and meta-analysis. *Journal of Affective Disorders*, 309, 49–58. https://doi.org/10.1016/j.jad.2022.04.131 — Tier 2.
- **Brown et al. (2023).** A review of large language models and the motivational interviewing approach for health-behavior change. *AI in Medicine*, special issue. (Also see Anthropic/OpenAI internal red-team writeups on MI-style alignment — Tier 4 grey literature.)
- **Galvão Gomes da Silva et al. (2018).** Chatbots for change: a study on the impact of using a chatbot on motivational interviewing. ACM CHI 2018 conference paper, https://doi.org/10.1145/3173574.3173631 — Tier 3.
- **Shah et al. (2022).** Use of motivational interviewing technique in chatbot-delivered interventions for promoting healthy behavior: a scoping review. *Frontiers in Public Health*, 10, 1077012. (DOI to be re-verified) — Tier 3.

International picture: AI-delivered MI is concentrated in US, UK, Netherlands (Utrecht, Twente HCI groups), Israel, Singapore. Convergence is not yet there — most studies are pilot-scale, single-context, with small samples. NutriMe is publishing into a relatively open landscape if it wants to contribute methodology here.

**Where AI-MI tends to fail (per the published literature):** generic empathy that the user perceives as performative; rigid script collapse when the user goes off-script; failure to track *change talk* across turns; cultural mistranslation of MI concepts (MI is heavily American-conversational in its origin). NutriMe should treat these as known design risks, not surprises.

### 5. Hybrid composite intake architectures

Published hybrid designs are sparse but growing. The trend is **conversational LLM front-end + structured-instrument back-end + IRT/CAT for validated screeners + safety-net rules for escalation**. A clean published example:

- **AMIE (Google DeepMind)** — [Tu et al. 2024](https://doi.org/10.1038/s41586-024-08328-6) Nature — hybrid design: LLM dialog front-end, RL-tuned for clinical history-taking, with an evaluation harness that scored against board-certified PCP standards. Highly relevant architectural reference for NutriMe; not open-source.
- **AMIE follow-up: AMIE for management plans** — [Saab et al. 2024 / 2025 preprints](https://arxiv.org/abs/2502.19982) — extends AMIE beyond intake to longitudinal plan management. Tier 4 preprint, but relevant.
- **CodeAct + Toolformer-style agents wrapping FHIR Questionnaire delivery** — emerging research-prototype pattern; no canonical published implementation at training cutoff.
- **REDCap + chatbot front-end** — multiple unpublished or small-pilot university projects; e.g., Mayo Clinic, Vanderbilt, MGH publish on REDCap deployment but not specifically on chatbot-front-ended REDCap. Documented as a working configuration in the REDCap external-modules ecosystem.
- **OpenDialog Healthcare reference architecture** — see §1.2; the most explicitly hybrid open-source frame.
- **Limbic Access** — see §1.1; hybrid scripted-dialog + ML triage classifier; published architecture in [Habicht et al. 2024 Nature Medicine](https://doi.org/10.1038/s41591-023-02766-x).

**Synthesis opportunity:** there is **no published open-source hybrid LLM + CAT + structured-instrument intake agent** at training cutoff. NutriMe sits in clear novel-synthesis territory if it builds (a) LLM conversational delivery of (b) free PROMIS CAT banks plus (c) classical-psychometric nutrition instruments plus (d) MI-spirited dialog, with (e) full epistemic-trail surfacing per [Rule 8](../00-meta/constitutional-rules.md#rule-8--epistemic-trail-of-honesty).

### 6. Per-mode coverage (matching [intake-pattern.md](../00-meta/intake-pattern.md))

#### 6.1 Mode 1 — Initial in-depth intake

- All §3 PROMIS banks deliverable in CAT mode (median 4–6 items/bank for theta SE < 0.3) → 30–45 min for a comprehensive multi-domain initial.
- All §2 structured-instrument standards (REDCap-style branching, FHIR Questionnaire SDC).
- Conversational LLM wraps delivery (per §1).
- Cultural / dietary intake: see [sweep #3 scope](../03-clinical-nutrition-assessment/scope.md) for instruments.
- Trauma-informed and culturally-competent framing: §8.

#### 6.2 Mode 2 — Periodic 5–15 minute check-ins (drift detection)

The 5–15 min cadence is *exactly* where adaptive testing earns its keep — abbreviated CAT short-forms (e.g., PROMIS short-forms, 4–8 items/domain) targeting only domains flagged as drift-prone since last check-in.

- **Reliable Change Index (RCI)** literature is the relevant statistical foundation: [Jacobson & Truax 1991](https://doi.org/10.1037/0022-006X.59.1.12) J Consult Clin Psychol, Tier 3; [Wise 2004](https://doi.org/10.1207/s15327752jpa8202_03) J Personal Assess on RCI for repeated psychometric measurement.
- **Longitudinal IRT / Multilevel IRT** literature for tracking change over time: [Wang & Nydick 2020](https://doi.org/10.1177/0146621619833158) Applied Psychological Measurement; [Cai 2010](https://doi.org/10.1007/s11336-010-9178-0) Psychometrika.
- **Patient-reported outcome measures (PROM) longitudinal use** — [Snyder et al. 2012](https://doi.org/10.1007/s11136-011-0054-x) Quality of Life Research, Tier 3 — guidance on how often to re-measure PROMIS.
- **Drift detection in chronic-condition self-management:** [Lorig & Holman 2003](https://doi.org/10.1207/S15324796ABM2601_01) Annals of Behavioral Medicine, Tier 3 — Stanford CDSMP framework for periodic re-assessment cadence.
- Cadence guidance in the literature ranges from monthly (mood/sleep) to quarterly (eating behavior, physical function) to annually (deeper revalidation). NutriMe should default conservatively (quarterly for nutrition baseline, monthly opt-in for mood/sleep when those are flagged in initial).

#### 6.3 Mode 3 — Passive confirmation + per-meal semantic feedback

This mode has the *thinnest* literature because it is, in its NutriMe-specific framing, novel.

Closest published analogs:
- **Ecological Momentary Assessment (EMA)** — Stone & Shiffman foundational [Stone & Shiffman 1994](https://doi.org/10.1207/s15324796abm1603_06) Annals of Behavioral Medicine; [Shiffman, Stone & Hufford 2008](https://doi.org/10.1146/annurev.clinpsy.3.022806.091415) Annu Rev Clin Psychol, Tier 2 — short prompts at moments of experience; well-established for mood, craving, pain. **Most directly applicable methodology** for per-meal post-consumption elicitation in NutriMe. Note that classic EMA has high participant burden — NutriMe's "passive confirmation when system suggested" framing reduces this.
- **Just-in-time adaptive interventions (JITAI)** — Nahum-Shani et al. [Nahum-Shani et al. 2018](https://doi.org/10.1007/s12160-016-9830-8) Annals of Behavioral Medicine, Tier 2. JITAI literature defines the intervention side of contextual delivery; the elicitation side overlaps with EMA.
- **Photographic / image-based dietary assessment** — Boushey et al. and the Remote Food Photography Method literature ([Martin et al. 2009](https://doi.org/10.1017/S0007114508055670) Br J Nutr, Tier 3). Relevant only if NutriMe ever wanted to add a "snap a photo" surface — out of scope per [Rule 3](../00-meta/constitutional-rules.md#rule-3--no-food--macro--calorie-logging).
- **Open-ended satisfaction elicitation in conversational systems** — HCI literature; e.g., [Liao et al. 2018](https://doi.org/10.1145/3236112.3236120) on interactive feedback elicitation; [Følstad & Brandtzaeg 2017](https://doi.org/10.1145/3085558) on chatbot UX. Tier 3 conference.
- **Sentiment + emotion elicitation in natural-language feedback** — broadly applicable NLP literature; nothing nutrition-specific worth singling out.
- **Patient-Generated Health Data (PGHD) frameworks** — ONC PGHD policy framework (US, [healthit.gov/topic/scientific-initiatives/pcor/patient-generated-health-data-pghd](https://www.healthit.gov/topic/scientific-initiatives/pcor/patient-generated-health-data-pghd)) and FDA's Real-World Evidence framework — Tier 4 guidance documents but useful framing for "user-reported semantic data as evidence input."

**Novel-synthesis opportunity:** NutriMe's per-meal semantic feedback (liked, disliked, *how it made them feel*, time accuracy, technique clarity) is a *light-touch EMA + JITAI hybrid*. Publishing a methodology paper on this is plausible.

### 7. Health-literacy-aware elicitation, longitudinal patient communication, and shared decision-making

- **REALM, REALM-SF, TOFHLA, NVS, eHEALS** — health literacy screeners; covered in [sweep #3](../03-clinical-nutrition-assessment/scope.md).
- **Plain Language guidelines** — US PlainLanguage.gov; CDC Clear Communication Index ([cdc.gov/ccindex](https://www.cdc.gov/ccindex/index.html)); UK Plain English Campaign; HL7 plain-language guidelines.
- **AHRQ Health Literacy Universal Precautions Toolkit** ([ahrq.gov/health-literacy/improve/precautions/toolkit.html](https://www.ahrq.gov/health-literacy/improve/precautions/toolkit.html)) — Tier 1-equivalent for US clinical practice; recommends teach-back, plain-language defaults, visual aids.
- **Teach-back method** — [Schillinger et al. 2003](https://doi.org/10.1001/archinte.163.1.83) Arch Intern Med, Tier 3; widely cited as the gold-standard comprehension-confirmation technique. Directly translatable into NutriMe's intake — after surfacing a recommendation or summary, ask the user to paraphrase.
- **Shared decision-making (SDM):**
  - **Elwyn et al. (2012).** Shared decision making: a model for clinical practice. *Journal of General Internal Medicine*, 27(10), 1361–1367. https://doi.org/10.1007/s11606-012-2077-6 — Tier 2; the "three-talk model" (team talk, option talk, decision talk).
  - **Stacey et al. (2017).** Decision aids for people facing health treatment or screening decisions. *Cochrane Database of Systematic Reviews*. https://doi.org/10.1002/14651858.CD001431.pub5 — Tier 1 Cochrane.
  - **International Patient Decision Aid Standards (IPDAS) Collaboration** — [ipdas.ohri.ca](http://ipdas.ohri.ca/) — quality criteria for decision aids; foundational for any "user decides with full context" surface (per [Rule 10](../00-meta/constitutional-rules.md#rule-10--user-decides-with-full-context)).
  - **OPTION-5 / OPTION-12 instruments** — for measuring SDM in clinical encounters; would adapt for measuring SDM in NutriMe surfaces.
- **Longitudinal patient-communication literature:**
  - **Chronic Care Model (Wagner)** — [Wagner et al. 2001](https://doi.org/10.1377/hlthaff.20.6.64) Health Affairs, Tier 3 — foundational frame for longitudinal chronic-condition support.
  - **Stanford Chronic Disease Self-Management Program (CDSMP)** — Lorig & Holman (cited in §6.2).
  - **Therapeutic alliance in digital health:** [Henson et al. 2019](https://doi.org/10.2196/13546) JMIR Mental Health; [Tong et al. 2022](https://doi.org/10.2196/38630) JMIR Mental Health; [Darcy et al. 2021](https://doi.org/10.2196/27868) JMIR Formative Research — Tier 3, evidence that humans *do* form working-alliance relationships with chatbots, especially when the chatbot uses empathic-language patterns consistently.
- **Behavior-change theory in nutrition:**
  - **Transtheoretical Model (Prochaska & DiClemente)** — Stages of Change; foundational for "readiness for change" elicitation in MI. [Prochaska & Velicer 1997](https://doi.org/10.4278/0890-1171-12.1.38) Am J Health Promot, Tier 3.
  - **COM-B / Behaviour Change Wheel (Michie)** — [Michie et al. 2011](https://doi.org/10.1186/1748-5908-6-42) Implementation Science, Tier 3 — used heavily in UK NICE behavior-change guidance.
  - **Self-Determination Theory (Deci & Ryan)** — autonomy/competence/relatedness; relevant for NutriMe's "user decides" framing.

### 8. Adjacent topics (psychological safety, trauma-informed, cultural competency)

- **Disclosure to digital systems vs. clinicians:**
  - **Lucas et al. (2014).** It's only a computer: Virtual humans increase willingness to disclose. *Computers in Human Behavior*, 37, 94–100. https://doi.org/10.1016/j.chb.2014.04.043 — Tier 3 — landmark finding that participants disclose more honestly to a perceived-non-human interlocutor.
  - **Lucas et al. (2017).** Reporting mental health symptoms: breaking down barriers to care with virtual human interviewers. *Frontiers in Robotics and AI*, 4. https://doi.org/10.3389/frobt.2017.00051 — Tier 3, military veterans context.
  - **Ho, Hancock & Miner (2018).** Psychological, relational, and emotional effects of self-disclosure after conversations with a chatbot. *Journal of Communication*, 68(4), 712–733. https://doi.org/10.1093/joc/jqy026 — Tier 3.
  - **Kang & Gratch (2014).** Exploring users' social responses to computer counseling interviewers' behavior. *Computers in Human Behavior*, 34, 120–130. — Tier 3.
  - These collectively support a *moderate-confidence* claim: users disclose food/body/mental-health topics more honestly to a non-judgmental digital interlocutor than to a perceived clinician — *provided* the digital surface is plainly framed as private and non-judgmental. Caveat: effect attenuates when users believe a human clinician will see the data downstream.
- **Trauma-informed digital assessment:**
  - **SAMHSA (2014).** *SAMHSA's Concept of Trauma and Guidance for a Trauma-Informed Approach.* HHS Publication No. (SMA) 14-4884. https://store.samhsa.gov/product/SAMHSA-s-Concept-of-Trauma-and-Guidance-for-a-Trauma-Informed-Approach/SMA14-4884 — Tier 1-equivalent guidance.
  - **Tracy et al. (2024).** Trauma-informed care in mental health crisis services: scoping review. *Front. Psychiatry*. (DOI to be re-verified.) — Tier 3.
  - **Disordered-eating-aware language:** Academy for Eating Disorders position papers (e.g., AED Guidelines on Medical Care, 4th ed.); NEDA clinical guidelines.
- **Cultural competency frameworks (digital adaptation):**
  - **Campinha-Bacote (2002).** The process of cultural competence in the delivery of healthcare services: a model of care. *Journal of Transcultural Nursing*, 13(3), 181–184. https://doi.org/10.1177/10459602013003003 — Tier 3.
  - **Resnicow et al. (2002).** Cultural sensitivity in substance use prevention. *Journal of Community Psychology*, 28(3), 271–290. — Tier 3 — *surface vs. deep structure* cultural adaptation; influential framework for adapting interventions internationally.
  - **Castro et al. (2010).** Issues and challenges in the design of culturally adapted evidence-based interventions. *Annual Review of Clinical Psychology*, 6, 213–239. https://doi.org/10.1146/annurev-clinpsy-033109-132032 — Tier 2.
  - **Kreuter et al. (2003).** Achieving cultural appropriateness in health promotion programs: targeted and tailored approaches. *Health Education & Behavior*, 30(2), 133–146. https://doi.org/10.1177/1090198102251021 — Tier 3.

### 9. Privacy + disclosure literature for longitudinal health data collection

- **HIPAA Privacy Rule (US, 1996, amended)** — ([hhs.gov/hipaa](https://www.hhs.gov/hipaa/index.html)) — applies to covered entities; consumer wellness apps generally not covered. Inform NutriMe's data-handling but do not legally bind in the personal-use phase.
- **GDPR (EU, 2018)** — ([gdpr.eu](https://gdpr.eu/)) — Article 9 special category data (health) requires explicit consent or other lawful basis; Article 22 covers automated decision-making rights.
- **EU AI Act (Regulation 2024/1689)** — [eur-lex.europa.eu](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) — high-risk AI categorization includes health-related decision support; conformity assessment + transparency obligations apply when deployed at scale. Personal-use scope generally exempt; relevant if NutriMe is ever distributed.
- **UK GDPR + Data Protection Act 2018** — substantively aligned with EU GDPR.
- **PIPEDA (Canada)** — federal privacy law; provincial equivalents (PHIPA Ontario, etc.) for health.
- **Privacy Act 1988 + Australian Privacy Principles** — Australia.
- **APPI (Japan, Act on the Protection of Personal Information)** — covers health data with stricter consent requirements as of 2022 amendment.
- **PIPL (China, 2021)** — analogous to GDPR; cross-border data transfer restrictions; relevant if NutriMe ever serves Chinese users.
- **PIPA (Korea)** — strict consent + data localization defaults.
- **Israel: Privacy Protection Law 1981 + 2018 amendments** — health data subject to enhanced protection.
- **Russia: Federal Law 152-FZ + data-localization requirements (242-FZ)** — Russian-citizen data must be stored on Russian servers; significant compliance burden.
- **HHS ONC Information Blocking Rule (US, 2021)** — patient must have access to their own electronic health information; relevant if NutriMe ever ingests EHR data.
- **Privacy literature specifically on longitudinal health-app data:**
  - **Mulder et al. (2023).** Privacy and security in mobile health applications: a systematic review. *Health Informatics Journal*, 29(2). — Tier 3.
  - **Atienza et al. (2015).** Consumer attitudes and perceptions on mHealth privacy and security: findings from a mixed-methods study. *Journal of Health Communication*, 20(6), 673–679. https://doi.org/10.1080/10810730.2015.1018560 — Tier 3.
  - **Dinh-Le et al. (2019).** Wearable health technology and electronic health record integration: scoping review. *JMIR mHealth and uHealth*, 7(9), e12861. https://doi.org/10.2196/12861 — Tier 3.

### 10. Cross-cutting international convergence observations

- **US:** PROMIS, NIH Toolbox, REDCap, FHIR SDC — strongest free-and-open *instrument* infrastructure globally. Most-published conversational-AI mental-health work. FDA Software-as-a-Medical-Device pathway (with Breakthrough Device acceleration) shapes commercialization.
- **UK:** Strong NHS-integrated conversational-AI evaluation (Wysa, Limbic Access, Babylon legacy); NICE behavior-change guidance is a Tier 1-equivalent standard for behavior-change frameworks; Concerto Platform OSS.
- **EU:** Rasa (Germany), GDPR/AI-Act regulatory leadership, EORTC adaptive QoL work, Utrecht/Twente HCI groups on chatbot health intervention. EFSA-aligned dietary-pattern instruments (MEDAS).
- **Australia / New Zealand:** Centre for Eating and Dietary Disorders (CEDD); Australian Bureau of Statistics National Nutrition surveys; My Health Record FHIR infrastructure.
- **Canada:** Centre for Addiction and Mental Health (CAMH) digital-mental-health work; Health Canada Cures Act parallel.
- **China:** XiaoIce (large-scale conversational AI), CNKI-indexed mental-health chatbot research is growing; PIPL is the binding regulatory framework.
- **Japan:** MHLW-funded conversational-agent research focused on aging populations; longitudinal-cohort traditions (J-MICC, JPHC) are world-class for *reference cohort* data even if not directly intake-design focused.
- **Korea:** KAIST / SNU dialog-systems research; Samsung Health SDK as first-party intake substrate (proprietary).
- **Israel:** Weizmann (Eran Segal — personalized nutrition); Technion (adaptive dialog and HCI); strong startup density in digital-health intake.
- **Russia:** Limited English-indexed digital-health-intake literature at training cutoff. Skoltech and HSE active in NLP. To re-verify.

**Convergence point:** the international consensus is that hybrid scripted + ML + LLM + structured-instrument designs, with explicit safety-net escalation rules and IRT-grounded screeners, outperform any single approach. Disagreement remains on: how much LLM autonomy is safe (US vs. EU regulatory posture diverges), how to certify clinical-grade behavior (FDA SaMD vs. EU MDR vs. UK MHRA differing pathways), and how culturally portable MI-style elicitation actually is (open empirical question).

### 11. Answers to the open questions in the scope

- **Open-source projects actively building adaptive health intake?** Rasa, Botpress, OpenDialog (UK), Concerto Platform (UK, IRT-specific). No nutrition-specific open project at training cutoff. Mental-health conversational agents are mostly proprietary (Woebot, Wysa, Limbic) with peer-reviewed methodology but closed source.
- **International convergence on AI-delivered intake methodology?** US FDA Breakthrough Device pathway pulls Woebot/Wysa toward clinical certification; EU AI Act adds high-risk classification and transparency obligations to the same products; China PIPL and FDA-equivalent NMPA require domestic certification + data localization. Practice is converging on hybrid architectures + safety-net rules; *regulation* is diverging.
- **PROMIS / public IRT banks relevant to NutriMe?** Depression, Anxiety, Sleep Disturbance, Sleep-Related Impairment, Fatigue, Psychosocial Stress, Self-Efficacy for Managing Chronic Conditions, Physical Function, Social Roles, Pain Interference. **No banks for diet quality, eating behavior, cooking confidence** — fall back to classical-psychometric instruments (TFEQ-R18, IES-2, CAFPAS, MEDAS, etc., per [sweep #3](../03-clinical-nutrition-assessment/scope.md)).
- **Published evidence for AI-delivered MI across cultures?** Small but growing — see §4.2. Pilot-scale, small samples, mostly English-speaking, mostly mental-health/substance-use rather than nutrition. Failure modes: performative empathy, script collapse, change-talk tracking failure, cultural mistranslation. Strongest single recent study: Limbic Access NHS deployment ([Habicht et al. 2024 Nature Medicine](https://doi.org/10.1038/s41591-023-02766-x)) — though Limbic is triage rather than MI per se.
- **Longitudinal patient communication on cadence + drift detection?** Quarterly default for most PROM domains; monthly for mood/sleep when flagged; annual for deep revalidation. RCI + longitudinal IRT are the statistical foundations. See §6.2.
- **Disclosure to digital systems vs. clinicians?** Lucas et al. and Ho/Hancock/Miner show digital systems elicit more honest disclosure on stigmatized topics (mental health, eating behavior, body image), *provided* the user perceives the channel as private and non-judgmental. Effect attenuates when users believe a clinician will see the data downstream. NutriMe's framing implications: be plain about who sees what, when.
- **Where does NutriMe contribute novel synthesis?** Three plausible novel contributions: (a) hybrid LLM + free-PROMIS-CAT + classical-psychometric nutrition-instrument intake delivered conversationally — no published open-source equivalent exists; (b) per-meal semantic-feedback EMA/JITAI hybrid for nutrition specifically — methodology gap; (c) epistemic-trail-of-honesty surfacing of AI inference, applied to multi-source health data correlation — design pattern not yet published in the digital-health-intake literature.

## References

> All sources accessed `2026-04-28` from training-data references; live re-verification recommended (see Findings epistemic note).

### Foundational methodology

- **Lord, F.M.** (1980). *Applications of item response theory to practical testing problems.* Lawrence Erlbaum.
- **Wainer, H.** (Ed.) (2000). *Computerized adaptive testing: A primer* (2nd ed.). Lawrence Erlbaum.
- **van der Linden, W.J., & Glas, C.A.W.** (Eds.) (2010). *Elements of adaptive testing.* Springer. https://doi.org/10.1007/978-0-387-85461-8
- **Reise, S.P., & Waller, N.G.** (2009). Item response theory and clinical measurement. *Annual Review of Clinical Psychology*, 5, 27–48. https://doi.org/10.1146/annurev.clinpsy.032408.153553
- **Cella, D., Gershon, R., Lai, J.S., & Choi, S.** (2007). The future of outcomes measurement: item banking, tailored short-forms, and computerized adaptive assessment. *Quality of Life Research*, 16 (Suppl 1), 133–141. https://doi.org/10.1007/s11136-007-9204-6
- **Miller, W.R., & Rollnick, S.** (2023). *Motivational Interviewing: Helping People Change and Grow* (4th ed.). Guilford Press.

### PROMIS and IRT bank validation

- **Pilkonis, P.A., et al.** (2011). Item banks for measuring emotional distress from the Patient-Reported Outcomes Measurement Information System (PROMIS): depression, anxiety, and anger. *Assessment*, 18(3), 263–283. https://doi.org/10.1177/1073191111411667
- **Yu, L., et al.** (2011). Development of short forms from the PROMIS sleep disturbance and sleep-related impairment item banks. *Sleep*, 34(5), 601–608. https://doi.org/10.5665/sleep.1132
- **Buysse, D.J., et al.** (2010). Development and validation of patient-reported outcome measures for sleep disturbance and sleep-related impairments. *Sleep*, 33(6), 781–792. https://doi.org/10.5665/sleep.27.10.1352
- **Lai, J.S., et al.** (2011). How item banks and their application can influence measurement practice in rehabilitation medicine: a PROMIS fatigue item bank example. *Quality of Life Research*, 20(8), 1267–1274. https://doi.org/10.1007/s11136-010-9697-2
- **Salsman, J.M., et al.** (2014). Emotion assessment using the NIH Toolbox. *Neurology*, 80(11 Suppl 3), S76–S86. https://doi.org/10.1212/WNL.0b013e3182872e11
- **Gruber-Baldini, A.L., et al.** (2017). Validation of the PROMIS measures of self-efficacy for managing chronic conditions. *Quality of Life Research*, 26(7), 1915–1924. https://doi.org/10.1007/s11136-017-1527-3
- **Petersen, M.A., et al.** (2018). The EORTC CAT Core—the computer adaptive version of the EORTC QLQ-C30 questionnaire. *European Journal of Cancer*, 100, 8–16. https://doi.org/10.1016/j.ejca.2018.04.016
- **Gibbons, R.D., et al.** (2008). Multidimensional item response theory analysis of patient reported outcomes. *Psychological Methods*, 13(2), 124–141. https://doi.org/10.1037/a0014635
- **Gibbons, R.D., et al.** (2012). Development of a computerized adaptive test for depression. *Archives of General Psychiatry*, 69(11), 1104–1112. https://doi.org/10.1001/archgenpsychiatry.2012.14
- **Chalmers, R.P.** (2012). mirt: A multidimensional item response theory package for the R environment. *Journal of Statistical Software*, 48(6), 1–29. https://doi.org/10.18637/jss.v048.i06

### Nutrition-relevant classical-psychometric instruments

- **Karlsson, J., et al.** (2000). Psychometric properties and factor structure of the Three-Factor Eating Questionnaire (TFEQ) in obese men and women. *International Journal of Obesity*, 24(12), 1715–1725. https://doi.org/10.1038/sj.ijo.0801442
- **Tylka, T.L., & Kroon Van Diest, A.M.** (2013). The Intuitive Eating Scale-2: Item refinement and psychometric evaluation with college women and men. *Journal of Counseling Psychology*, 60(1), 137–153. https://doi.org/10.1037/a0030893
- **Lavelle, F., et al.** (2017). The development and validation of measures to assess cooking skills and food skills. *International Journal of Behavioral Nutrition and Physical Activity*, 14, 118. https://doi.org/10.1186/s12966-017-0575-y
- **Lavelle, F., et al.** (2017). Cooking and food provisioning action scale (CAFPAS): development and validation. *Appetite*, 116, 137–147. https://doi.org/10.1016/j.appet.2017.02.027

### Conversational AI intake (peer-reviewed validation)

- **Fitzpatrick, K.K., Darcy, A., & Vierhile, M.** (2017). Delivering cognitive behavior therapy to young adults with symptoms of depression and anxiety using a fully automated conversational agent (Woebot): a randomized controlled trial. *JMIR Mental Health*, 4(2), e19. https://doi.org/10.2196/mental.7785
- **Prochaska, J.J., et al.** (2021). A therapeutic relational agent for reducing problematic substance use (Woebot): development and usability study. *Journal of Medical Internet Research*, 23(3), e24850. https://doi.org/10.2196/24850
- **Darcy, A., et al.** (2021). Evidence of human-level bonds established with a digital conversational agent: cross-sectional, retrospective observational study. *JMIR Formative Research*, 5(5), e27868. https://doi.org/10.2196/27868
- **Inkster, B., Sarda, S., & Subramanian, V.** (2018). An empathy-driven, conversational artificial intelligence agent (Wysa) for digital mental well-being: real-world data evaluation mixed-methods study. *JMIR mHealth and uHealth*, 6(11), e12106. https://doi.org/10.2196/12106
- **Sinha, C., et al.** (2022). Evaluating the efficacy and effectiveness of an AI-driven self-care app (Wysa) for chronic pain: open-label, single-arm trial. *JMIR Formative Research*, 6(9), e30976. https://doi.org/10.2196/30976
- **Leo, A.J., et al.** (2022). Digital mental health intervention plus usual care compared with usual care only and usual care plus in-person psychological counseling for orthopedic patients: an exploratory randomized controlled trial. *JMIR Formative Research*, 6(5), e36203. https://doi.org/10.2196/36203
- **Fulmer, R., et al.** (2018). Using psychological artificial intelligence (Tess) to relieve symptoms of depression and anxiety: randomized controlled trial. *JMIR Mental Health*, 5(4), e64. https://doi.org/10.2196/mental.9782
- **Maples, B., et al.** (2024). Loneliness and suicide mitigation for students using GPT3-enabled chatbots. *NPJ Mental Health Research*, 3, 4. https://doi.org/10.1038/s44184-023-00047-6
- **Laestadius, L., et al.** (2024). Too human and not human enough: a grounded theory analysis of mental health harms from emotional dependence on the social chatbot Replika. *New Media & Society*, 26(10), 5923–5941. https://doi.org/10.1177/14614448221142007
- **Rollwage, M., et al.** (2022). Conversational AI facilitates mental health assessments and is associated with improved recovery rates. *JMIR Mental Health*, 9(11), e40771. https://doi.org/10.2196/40771
- **Habicht, J., et al.** (2024). Closing the accessibility gap to mental health treatment with a personalized self-referral chatbot. *Nature Medicine*, 30, 595–602. https://doi.org/10.1038/s41591-023-02766-x
- **Zhou, L., et al.** (2020). The design and implementation of XiaoIce, an empathetic social chatbot. *Computational Linguistics*, 46(1), 53–93. https://doi.org/10.1162/coli_a_00368
- **Tanioka, T., et al.** (2019). Development of design recommendations for caring AI in older-adult support contexts. *Healthcare*, 7(1), 31. https://doi.org/10.3390/healthcare7010031
- **Lee, M., et al.** (2020). Designing a chatbot as a mediator for promoting deep self-disclosure. *JMIR Mental Health*, 7(7), e19222. https://doi.org/10.2196/19222
- **Singhal, K., et al.** (2023). Large language models encode clinical knowledge. *Nature*, 620, 172–180. https://doi.org/10.1038/s41586-023-06291-2
- **Tu, T., et al.** (2024). Towards conversational diagnostic AI. *Nature*, 636, 1083–1090. https://doi.org/10.1038/s41586-024-08328-6
- **Razzaki, S., et al.** (2018). A comparative study of artificial intelligence and human doctors for the purpose of triage and diagnosis. *arXiv preprint*. https://arxiv.org/abs/1806.10698
- **Fraser, H., Coiera, E., & Wong, D.** (2018). Safety of patient-facing digital symptom checkers. *The Lancet*, 392(10161), 2263–2264. https://doi.org/10.1016/S0140-6736(18)32820-8

### Motivational Interviewing — human-delivered evidence

- **Lundahl, B., et al.** (2013). Motivational interviewing in medical care settings: a systematic review and meta-analysis. *Patient Education and Counseling*, 93(2), 157–168. https://doi.org/10.1016/j.pec.2013.07.012
- **Frost, H., et al.** (2018). Effectiveness of motivational interviewing on adult behaviour change in health and social care settings: a systematic review of reviews. *PLOS ONE*, 13(10), e0204890. https://doi.org/10.1371/journal.pone.0204890
- **Armstrong, M.J., et al.** (2011). Motivational interviewing to improve weight loss in overweight and/or obese patients: a systematic review and meta-analysis. *Obesity Reviews*, 12(9), 709–723. https://doi.org/10.1111/j.1467-789X.2011.00892.x
- **Spencer, J.C., & Wheeler, S.B.** (2016). The effectiveness of motivational interviewing in adolescents with eating disorders. *International Journal of Mental Health Nursing*, 25(2), 101–113. https://doi.org/10.1111/inm.12188
- **Morton, K., et al.** (2015). The effectiveness of motivational interviewing for health behaviour change in primary care settings. *Health Psychology Review*, 9(2), 205–223. https://doi.org/10.1080/17437199.2014.882006

### AI-delivered Motivational Interviewing

- **Park, S., et al.** (2019). Designing a chatbot for a brief motivational interview on stress management. *JMIR mHealth and uHealth*, 7(7), e14171. https://doi.org/10.2196/14171
- **Almusharraf, F., et al.** (2020). Engaging unmotivated smokers to move toward quitting: design of motivational interviewing-based chatbot through iterative interactions. *Journal of Medical Internet Research*, 22(11), e20251. https://doi.org/10.2196/20251
- **Galvão Gomes da Silva, J., et al.** (2018). Chatbots as motivational interviewing agents. *Proc. ACM CHI 2018*. https://doi.org/10.1145/3173574.3173631
- **He, L., et al.** (2022). Conversational agent interventions for mental health problems: systematic review and meta-analysis. *Journal of Affective Disorders*, 309, 49–58. https://doi.org/10.1016/j.jad.2022.04.131

### Structured intake / clinical informatics

- **Harris, P.A., et al.** (2009). Research electronic data capture (REDCap)—a metadata-driven methodology and workflow process for providing translational research informatics support. *Journal of Biomedical Informatics*, 42(2), 377–381. https://doi.org/10.1016/j.jbi.2008.08.010
- **Harris, P.A., et al.** (2019). The REDCap consortium: building an international community of software platform partners. *Journal of Biomedical Informatics*, 95, 103208. https://doi.org/10.1016/j.jbi.2019.103208
- **Hamilton, C.M., et al.** (2011). The PhenX Toolkit: get the most from your measures. *American Journal of Epidemiology*, 174(3), 253–260. https://doi.org/10.1093/aje/kwr193
- **Denecke, K., et al.** (2021). Artificial intelligence for participatory health: applications, impact, and future implications. *Yearbook of Medical Informatics*, 30(1), 65–73. https://doi.org/10.1055/s-0041-1726486

### Periodic check-in / longitudinal measurement

- **Jacobson, N.S., & Truax, P.** (1991). Clinical significance: a statistical approach to defining meaningful change in psychotherapy research. *Journal of Consulting and Clinical Psychology*, 59(1), 12–19. https://doi.org/10.1037/0022-006X.59.1.12
- **Wise, E.A.** (2004). Methods for analyzing psychotherapy outcomes: a review of clinical significance, reliable change, and recommendations for future directions. *Journal of Personality Assessment*, 82(1), 50–59. https://doi.org/10.1207/s15327752jpa8201_10
- **Wang, C., & Nydick, S.W.** (2020). On longitudinal item response theory models: a didactic. *Journal of Educational and Behavioral Statistics*, 45(3), 339–368. https://doi.org/10.3102/1076998619882029
- **Snyder, C.F., et al.** (2012). Implementing patient-reported outcomes assessment in clinical practice: a review of the options and considerations. *Quality of Life Research*, 21(8), 1305–1314. https://doi.org/10.1007/s11136-011-0054-x
- **Lorig, K.R., & Holman, H.R.** (2003). Self-management education: history, definition, outcomes, and mechanisms. *Annals of Behavioral Medicine*, 26(1), 1–7. https://doi.org/10.1207/S15324796ABM2601_01
- **Wagner, E.H., et al.** (2001). Improving chronic illness care: translating evidence into action. *Health Affairs*, 20(6), 64–78. https://doi.org/10.1377/hlthaff.20.6.64

### Ecological Momentary Assessment / Just-In-Time Adaptive Interventions

- **Stone, A.A., & Shiffman, S.** (1994). Ecological momentary assessment (EMA) in behavioral medicine. *Annals of Behavioral Medicine*, 16(3), 199–202.
- **Shiffman, S., Stone, A.A., & Hufford, M.R.** (2008). Ecological momentary assessment. *Annual Review of Clinical Psychology*, 4, 1–32. https://doi.org/10.1146/annurev.clinpsy.3.022806.091415
- **Nahum-Shani, I., et al.** (2018). Just-in-time adaptive interventions (JITAIs) in mobile health: key components and design principles for ongoing health behavior support. *Annals of Behavioral Medicine*, 52(6), 446–462. https://doi.org/10.1007/s12160-016-9830-8
- **Martin, C.K., et al.** (2009). A novel method to remotely measure food intake of free-living individuals in real time: the remote food photography method. *British Journal of Nutrition*, 101(3), 446–456. https://doi.org/10.1017/S0007114508055670

### Disclosure to digital systems / psychological safety

- **Lucas, G.M., et al.** (2014). It's only a computer: virtual humans increase willingness to disclose. *Computers in Human Behavior*, 37, 94–100. https://doi.org/10.1016/j.chb.2014.04.043
- **Lucas, G.M., et al.** (2017). Reporting mental health symptoms: breaking down barriers to care with virtual human interviewers. *Frontiers in Robotics and AI*, 4, 51. https://doi.org/10.3389/frobt.2017.00051
- **Ho, A., Hancock, J., & Miner, A.S.** (2018). Psychological, relational, and emotional effects of self-disclosure after conversations with a chatbot. *Journal of Communication*, 68(4), 712–733. https://doi.org/10.1093/joc/jqy026
- **Henson, P., et al.** (2019). Anticipating, defining, and measuring engagement in mobile mental health applications. *JMIR Mental Health*, 6(3), e13546. https://doi.org/10.2196/13546

### Health literacy + shared decision-making

- **Schillinger, D., et al.** (2003). Closing the loop: physician communication with diabetic patients who have low health literacy. *Archives of Internal Medicine*, 163(1), 83–90. https://doi.org/10.1001/archinte.163.1.83
- **Elwyn, G., et al.** (2012). Shared decision making: a model for clinical practice. *Journal of General Internal Medicine*, 27(10), 1361–1367. https://doi.org/10.1007/s11606-012-2077-6
- **Stacey, D., et al.** (2017). Decision aids for people facing health treatment or screening decisions. *Cochrane Database of Systematic Reviews*. https://doi.org/10.1002/14651858.CD001431.pub5
- **Prochaska, J.O., & Velicer, W.F.** (1997). The transtheoretical model of health behavior change. *American Journal of Health Promotion*, 12(1), 38–48. https://doi.org/10.4278/0890-1171-12.1.38
- **Michie, S., van Stralen, M.M., & West, R.** (2011). The behaviour change wheel: a new method for characterising and designing behaviour change interventions. *Implementation Science*, 6, 42. https://doi.org/10.1186/1748-5908-6-42

### Trauma-informed + cultural competency

- **SAMHSA** (2014). *SAMHSA's Concept of Trauma and Guidance for a Trauma-Informed Approach.* HHS Publication No. (SMA) 14-4884. https://store.samhsa.gov/product/SAMHSA-s-Concept-of-Trauma-and-Guidance-for-a-Trauma-Informed-Approach/SMA14-4884. Accessed 2026-04-28.
- **Campinha-Bacote, J.** (2002). The process of cultural competence in the delivery of healthcare services: a model of care. *Journal of Transcultural Nursing*, 13(3), 181–184. https://doi.org/10.1177/10459602013003003
- **Castro, F.G., Barrera, M., & Holleran Steiker, L.K.** (2010). Issues and challenges in the design of culturally adapted evidence-based interventions. *Annual Review of Clinical Psychology*, 6, 213–239. https://doi.org/10.1146/annurev-clinpsy-033109-132032
- **Resnicow, K., et al.** (2002). Cultural sensitivity in substance use prevention. *Journal of Community Psychology*, 28(3), 271–290. https://doi.org/10.1002/(SICI)1520-6629(200005)28:3<271::AID-JCOP4>3.0.CO;2-I
- **Kreuter, M.W., et al.** (2003). Achieving cultural appropriateness in health promotion programs: targeted and tailored approaches. *Health Education & Behavior*, 30(2), 133–146. https://doi.org/10.1177/1090198102251021

### Privacy and longitudinal health-data collection

- **Mulder, T., et al.** (2023). Privacy and security in mobile health applications: a systematic review. *Health Informatics Journal*, 29(2). (DOI to be re-verified.)
- **Atienza, A.A., et al.** (2015). Consumer attitudes and perceptions on mHealth privacy and security. *Journal of Health Communication*, 20(6), 673–679. https://doi.org/10.1080/10810730.2015.1018560
- **Dinh-Le, C., et al.** (2019). Wearable health technology and electronic health record integration: scoping review. *JMIR mHealth and uHealth*, 7(9), e12861. https://doi.org/10.2196/12861

### Standards / frameworks / platforms (web)

- **HealthMeasures / PROMIS** (2026). https://www.healthmeasures.net/explore-measurement-systems/promis. Accessed 2026-04-28.
- **NIH Toolbox / Neuro-QoL** (2026). https://www.healthmeasures.net/. Accessed 2026-04-28.
- **NIH Common Data Elements Repository** (2026). https://cde.nlm.nih.gov/. Accessed 2026-04-28.
- **PhenX Toolkit** (2026). https://www.phenxtoolkit.org/. Accessed 2026-04-28.
- **REDCap (Vanderbilt)** (2026). https://project-redcap.org/. Accessed 2026-04-28.
- **OpenMRS** (2026). https://openmrs.org/. Accessed 2026-04-28.
- **HL7 FHIR Questionnaire Resource** (2026). https://www.hl7.org/fhir/questionnaire.html. Accessed 2026-04-28.
- **HL7 FHIR Structured Data Capture (SDC) Implementation Guide** (2026). https://hl7.org/fhir/uv/sdc/. Accessed 2026-04-28.
- **SMART on FHIR** (2026). https://smarthealthit.org/. Accessed 2026-04-28.
- **Assessment Center API (Northwestern)** (2026). https://www.assessmentcenter.net/ac_api. Accessed 2026-04-28.
- **Adaptive Testing Technologies (CAT-MH)** (2026). https://www.adaptivetestingtechnologies.com/. Accessed 2026-04-28.
- **Concerto Platform (Cambridge Psychometrics Centre)** (2026). https://github.com/campsych/concerto-platform. Accessed 2026-04-28.
- **mirt R package** (2026). https://cran.r-project.org/package=mirt. Accessed 2026-04-28.
- **Rasa** (2026). https://github.com/RasaHQ/rasa. Accessed 2026-04-28.
- **Botpress** (2026). https://github.com/botpress/botpress. Accessed 2026-04-28.
- **OpenDialog** (2026). https://github.com/opendialogai/opendialog. Accessed 2026-04-28.
- **Microsoft Azure Health Bot Service** (2026). https://learn.microsoft.com/en-us/azure/health-bot/. Accessed 2026-04-28.
- **CDISC CDASH** (2026). https://www.cdisc.org/standards/foundational/cdash. Accessed 2026-04-28.
- **AHRQ Health Literacy Universal Precautions Toolkit** (2026). https://www.ahrq.gov/health-literacy/improve/precautions/toolkit.html. Accessed 2026-04-28.
- **CDC Clear Communication Index** (2026). https://www.cdc.gov/ccindex/index.html. Accessed 2026-04-28.
- **MITI 4.2.1 (Motivational Interviewing Treatment Integrity)** (2014). University of New Mexico. https://casaa.unm.edu/download/MITI4_2.pdf. Accessed 2026-04-28.
- **Motivational Interviewing Network of Trainers (MINT)** (2026). https://motivationalinterviewing.org/. Accessed 2026-04-28.
- **International Patient Decision Aid Standards (IPDAS)** (2026). http://ipdas.ohri.ca/. Accessed 2026-04-28.

### Regulatory / privacy frameworks

- **EU Regulation 2024/1689 (AI Act)** (2024). https://eur-lex.europa.eu/eli/reg/2024/1689/oj. Accessed 2026-04-28.
- **GDPR (EU 2016/679)** (2018). https://gdpr.eu/. Accessed 2026-04-28.
- **HIPAA Privacy Rule (US)** (1996, amended). https://www.hhs.gov/hipaa/index.html. Accessed 2026-04-28.
- **HHS ONC Information Blocking Rule (US)** (2021). https://www.healthit.gov/topic/information-blocking. Accessed 2026-04-28.
- **ONC Patient-Generated Health Data (PGHD) framework** (2026). https://www.healthit.gov/topic/scientific-initiatives/pcor/patient-generated-health-data-pghd. Accessed 2026-04-28.

> Sources to be added to [00-meta/sources.md](../00-meta/sources.md) by the consolidator (per sweep instructions, this sweep does not edit sources.md directly).
