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

To be populated when research is run.

## References

To be populated. Add new sources to [sources.md](../00-meta/sources.md) when added.
