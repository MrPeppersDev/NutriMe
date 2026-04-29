# Sweep #7 — Cooking Time, Food Skills, and Behavioral Barriers

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Map the literature on why busy working adults default to eating out / ordering in / frozen meals instead of cooking, what time and skill barriers actually exist (and how they're often misperceived), and what is known about cooking confidence, time-stress and diet quality, and convenience-driven food choice. Output directly informs (a) intake screeners for cooking confidence + time budget + equipment, (b) recipe complexity tiering and presentation modality matching, (c) per-meal time-accuracy feedback design, and (d) horizon-broadening pacing for the iterative intake model.

This sweep is **load-bearing for the product**, not auxiliary research — it characterizes the user-state surface that the system is designed to operate on.

## Deliverable

An annotated reference map containing:

- Time-to-cook literature (US ATUS, NHANES, international comparators across [primary geographic scope](../00-meta/geographic-scope.md))
- Behavioral / structural barriers research focused on the target user (Wolfson, Bleich, Bowen, Mills, Lavelle, Caraher) — relevant to busy working adults with kitchen access
- Cooking confidence + self-efficacy validated instruments (CCSS, Lavelle's cooking self-efficacy scale, others)
- Time perception vs. reality literature (Saksena 2018 and successors) — people consistently overestimate cooking time
- Time-stress and diet quality correlation (peer-reviewed Tier 2/3)
- Convenience food consumption patterns — what we're displacing, what motivates it
- Cooking class / intervention effectiveness (peer-reviewed) — for *informing* product design, not as the product itself
- Cultural cooking differences across [primary scope](../00-meta/geographic-scope.md) — high-cooking cultures (Italy, France, Japan, India, China, Korea) vs. low-cooking (US, UK, urban metros) — context, not weighted heavily
- Equipment / kitchen-state assessment — what hardware enables what cuisines (cross-references [sweep #12](../12-skills-by-cuisine/scope.md))
- Per-meal time feedback methodology — how to capture "this took me 45 not 25" non-intrusively

This is a **reference map**, not corpus build.

## In scope

### Target-user-relevant barriers

- Time poverty research (work hours, commute, caregiving load)
- Decision fatigue around food choice
- "I don't know what to buy" — fresh-ingredient purchasing literacy literature
- Skill-perception gaps — believing cooking is harder / longer / more complex than it actually is
- Low-friction-to-high-friction default switching (frozen meal → fresh cooking transitions)

### Cooking confidence + self-efficacy

- Validated instruments (CCSS, Lavelle, Mills, others) — feeds [sweep #3 intake screener](../03-clinical-nutrition-assessment/scope.md)
- Self-efficacy growth literature — what builds confidence through repeated successful cooking experiences
- Confidence-by-cuisine variation (cross-references [sweep #12](../12-skills-by-cuisine/scope.md))

### Time perception and accuracy

- People consistently overestimate cooking time (Saksena 2018 and successors)
- Discrepancy between recipe-stated time and actual cooking time
- How real-time + per-step time tracking changes perception
- Implications for product: per-meal time feedback ("this took 45 not 25") feeds future estimates per-user *and* aggregates across users to recalibrate recipe metadata

### Time-stress and diet quality

- Peer-reviewed correlation literature (Tier 2/3)
- How time-pressure shifts food choice toward UPF / convenience
- Interventions that reduce time-pressure perception around cooking

### Convenience food consumption

- What busy working adults currently eat (US + international context)
- Why frozen / takeout / delivery wins on the convenience axis
- What product design has to deliver to compete on convenience

### Cooking class / intervention literature

- For *informing* product design, not as the product. The system is not a cooking school per [product-framing.md](../00-meta/product-framing.md).
- Findings on what raises cooking frequency, what raises cooking confidence, what improves diet quality — translated into product hooks (recommendation pacing, complexity tiering, presentation modality)

### Cultural cooking differences (light coverage)

- Brief context across [primary scope](../00-meta/geographic-scope.md): which cultures cook more, why, structural factors
- Not weighted heavily — the driver is *whole-fresh-cooked-tasty-good-for-you*, not cultural authenticity for its own sake
- Cultural variety enters as a flavor + discovery dimension, not an organizing principle

### Equipment / kitchen-state assessment

- Inventories of basic kitchen equipment + what each enables
- "Equipment surfacing" UX pattern — when a recipe needs a piece the user doesn't have, system says so and asks if user can obtain it
- Cross-references [sweep #12](../12-skills-by-cuisine/scope.md) for equipment ↔ cuisine bindings

## Out of scope (with reasons)

- **Kitchen-less / food-insecure populations** — different product, not the target user. Per user direction (2026-04-28): assume kitchen access + basic equipment-purchasability.
- **Children + family cooking** — stretch goal at most. Target = 1 adult or 2 adults cooking together.
- **Cooking instruction / pedagogy as a product feature** — the system is not a cooking school per [product-framing.md](../00-meta/product-framing.md). Cooking class effectiveness literature is in scope for *informing design* but not for delivering classes.
- **Skills-by-cuisine mapping** — its own sweep, [#12](../12-skills-by-cuisine/scope.md)
- **Recipe presentation / modality / video sourcing** — covered in [sweep #11 (recipe sourcing)](../11-recipe-sourcing/scope.md)

## Open questions for the research

- For target user (busy working adults, kitchen access, low-frequency current cookers): what does the literature say are the highest-leverage barrier interventions?
- What is the gap between *perceived* cooking time and *actual* cooking time, and how does closing that gap affect cooking frequency?
- What is the published evidence on convenience-vs-fresh-cooking choice mechanisms?
- What validated cooking confidence instruments exist, and which are best-fit for an intake screener?
- What does peer-reviewed evidence say about how cooking confidence grows over time, and what design choices accelerate it?
- How do high-cooking cultures (Japan, India, Italy) structure home cooking such that it remains feasible for working adults?
- What patterns of equipment / pantry default-stocking enable low-friction fresh cooking?

## Cross-references

- Bound by [target-user definition in product-framing.md](../00-meta/product-framing.md#target-user)
- Bound by [Constitutional Rule 7 (peer-reviewed floor)](../00-meta/constitutional-rules.md#rule-7--peer-reviewed-evidence-floor)
- Feeds intake screener design in [sweep #3](../03-clinical-nutrition-assessment/scope.md) (cooking confidence)
- Feeds adaptive intake elicitation in [sweep #4](../04-adaptive-intake-agent/scope.md) (time budget, equipment, current frequency)
- Feeds [sweep #11 (recipe sourcing)](../11-recipe-sourcing/scope.md) — complexity tiering, presentation modality
- Cross-references [sweep #8 (nutrition education delivery)](../08-nutrition-education-delivery/scope.md) — overlapping behavior-change literature
- Sister to [sweep #12 (skills-by-cuisine mapping)](../12-skills-by-cuisine/scope.md) — confidence + equipment + skills bindings to cuisine selection
- See [geographic-scope.md](../00-meta/geographic-scope.md) for primary research scope

## Findings

To be populated when research is run.

## References

To be populated. Add new sources to [sources.md](../00-meta/sources.md) when added.
