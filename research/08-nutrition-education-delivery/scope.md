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

To be populated when research is run.

## References

To be populated. Add new sources to [sources.md](../00-meta/sources.md) when added.
