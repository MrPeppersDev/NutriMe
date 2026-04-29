# NutriMe — Evidence Tiers

> Every nutrition or health claim surfaced by NutriMe must be tagged with an explicit evidence tier. Weak peer-reviewed evidence may be surfaced with clear declaration of weakness; non-peer-reviewed content cannot serve as the basis for any health claim.

## The four tiers

| Tier | Evidence type | Use in product |
|------|---------------|----------------|
| **1** | Consensus authoritative bodies — NASEM/IOM DRIs, WHO, USDA Dietary Guidelines, ADA Standards of Care, AHA scientific statements, Cochrane reviews, EFSA DRVs, NICE guidelines | Defensible, prescriptive guidance |
| **2** | Systematic reviews / meta-analyses in indexed peer-reviewed journals — AJCN, BMJ, JAMA, Annals, NEJM, Cochrane individual reviews | Strong support for specific questions (protein per meal, meal timing, etc.) |
| **3** | Individual RCTs **and well-designed observational studies** (prospective cohort, case-control) in indexed peer-reviewed journals | Supporting evidence — surfaceable but weaker than Tier 1/2 |
| **4** | Mechanistic-only / wearable-vendor whitepapers / preprints / conference abstracts / blog posts / non-peer-reviewed content | Informational / cultural / historical context only — **cannot be the basis for any health claim** |

## The peer-reviewed floor (constitutional)

Per [Constitutional Rule 7](constitutional-rules.md#rule-7--peer-reviewed-evidence-floor), Tier 4 cannot be the sole basis for:

- Any system design decision (defaults, gating logic, recommendation algorithms)
- Any user-facing recommendation surface
- Any claim of effect, mechanism, or benefit

Tier 4 *may* appear as informational / cultural / historical content where no health claim is attached. Example: "This dietary pattern has been traditional in X region for centuries" is a cultural fact and may be surfaced; "...and is associated with longer lifespan" requires Tier 1/2/3 evidence to make the claim.

**Peer-reviewed (Tier 1, 2, or 3) is the minimum floor for anything that asserts effect, mechanism, or recommendation.**

## Surfacing rules

- **Tier 1:** Surface as recommendation. Cite the body and document version. Note when bodies disagree (per [sweep #1](../01-international-nutrition-standards/scope.md)).
- **Tier 2:** Surface as supporting recommendation. Cite the systematic review or meta-analysis. Note effect size and certainty rating (e.g., GRADE) where available.
- **Tier 3:** Surface with explicit declaration that the evidence is single-study or observational. The [consult-a-professional rule](constitutional-rules.md#rule-1--consult-a-professional) applies. Never as the sole basis for a strong recommendation.
- **Tier 4:** Surface only as cultural / historical / mechanistic context with no health claim attached, OR as educational "audit-as-education" content (see below). Visibly label evidence quality in both cases.

## Operational tradition as supplementary basis

Some domains where NutriMe operates have **thin peer-reviewed research support** but **strong institutional or professional operational tradition** behind a particular practice. Examples surfaced during research:

- **"Common base + per-plate deltas" household meal pattern** — thin family-meal-intervention research support; strong professional-kitchen tradition (Escoffier mother sauces, CIA mise en place, institutional foodservice production cooking). See [synthesis.md Tension #2](synthesis.md#tension-2--common-base--per-plate-deltas-evidence-basis-honesty).
- **Cooking skills + culinary technique** ([sweep #12](../12-skills-by-cuisine/scope.md)) — professional culinary curricula (CIA, Le Cordon Bleu, Tsuji, Ferrandi, ALMA, Hattori, IHM India, China Culinary Academy) provide structured, accountable, institutional skill enumeration; peer-reviewed culinary education research is sparser.

For these domains, **operational tradition counts as a legitimate supplementary evidence basis** — but it must be **flagged as such**, not presented as if it were peer-reviewed Tier 1/2/3 support. The user gets honest framing:

- *Where to use:* practices with established outcomes in production / institutional settings, accountable institutional sources, long-standing professional consensus
- *Where NOT to use:* health claims (those still need Tier 1/2/3 peer-reviewed support per [Rule 7](constitutional-rules.md#rule-7--peer-reviewed-evidence-floor)); operational tradition is for *operational patterns* and *technique knowledge*, not for nutrition / clinical claims

When the system surfaces an operationally-grounded pattern to the user, the framing names the basis honestly — e.g., *"we use the same approach professional kitchens use to serve diverse needs from a single base"* — rather than hiding the provenance or implying peer-reviewed nutrition research that doesn't strongly exist.

This is a sister pattern to [audit-as-education](#audit-as-education-pattern): both handle situations where the standard Tier 1–4 framework needs supplementary surfacing rules to stay honest.

## Audit-as-education pattern

Evidence audits perform double duty in NutriMe:

1. **System-behavior gating** — the audit determines whether a topic meets the peer-reviewed floor for driving recommendations or defaults
2. **Educational content** — the audit *itself* becomes content presented to the user

This applies especially to high-marketing / low-evidence topics like microbiome-based personalization, nutrigenomics, metabolomic testing, fad diets, supplement claims, and trendy biohacks. NutriMe covers these openly: explains what they claim, presents the evidence honestly with tier labeling, and explains why the system does or does not use them to drive recommendations.

Most consumer health products either uncritically endorse such topics (vendor marketing) or paternalistically hide them. NutriMe does neither — transparent presentation with honest evidence assessment is a first-class feature.

The audit-as-education pattern requires that the educational content itself is responsibly framed:

- Visibly tag every claim with its evidence tier
- Be explicit when something is being shared as "what's marketed" rather than "what's recommended"
- Apply [Constitutional Rule 1 (consult-professional)](constitutional-rules.md#rule-1--consult-a-professional) where appropriate

## What this means in practice

- Refuse to invent a number (calories, grams, mg) that isn't grounded in a retrievable Tier 1/2/3 source
- When two Tier 1 bodies disagree, show the range and explain why (see [sweep #1](../01-international-nutrition-standards/scope.md))
- Treat wearable-vendor marketing as Tier 4 — usable for "this device measures X" (a fact about the device) but not for "X helps you eat better" (a health claim)
- Apply the same tier discipline to behavioral / adherence claims — much of that literature is Tier 3 or 4
- Microbiome / nutrigenomic / metabolomic personalization claims that lack Tier 1/2 support should not drive system behavior, even when the underlying tests exist commercially (see [sweep #5](../05-personalized-nutrition-evidence/scope.md))

## Sources

- User instruction (2026-04-28, early discovery): "it's okay to surface that the evidence is weak. We don't mind surfacing weak evidence. All we care about is clarification of that evidence."
- User instruction (2026-04-28, sweep #4 scoping): "Because it's based in health sciences and directly related to the user's health, we want to make sure we have a way to ground every decision made here and everything we surface in the future in some sort of scientific understanding, at least peer reviewed at minimum."
