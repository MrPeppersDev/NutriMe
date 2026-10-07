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

> **Epistemic note (2026-04-29):** WebSearch and WebFetch were denied for this sweep. The map below is built from training-data knowledge of widely-cited peer-reviewed literature in cooking behaviour, time use, food skills, and convenience-food consumption. DOIs, sample sizes, journal volumes/issues, and exact effect sizes should be re-verified against the canonical record before any claim is surfaced to the user. Tier tags (Tier 1 / 2 / 3) reflect the *type* of evidence (consensus body / SR-MA / RCT or cohort) per [evidence-tiers.md](../00-meta/evidence-tiers.md); they are conservative and re-verifiable. Where a specific number is cited (e.g., "37 minutes/day on food prep"), it is given as an order-of-magnitude anchor and flagged for re-verification. No URL/DOI is fabricated — citations include DOIs only where high-confidence and the few uncertain pages are flagged `[verify URL]`.

### 1. Time-to-cook literature

#### 1.1 US — American Time Use Survey (ATUS) and NHANES

The **American Time Use Survey** (US Bureau of Labor Statistics, ongoing since 2003) is the workhorse dataset for population-level time spent on food preparation and clean-up in the US. ATUS uses a single-day 24-hour diary on a randomly sampled household member and codes activities including "food and drink preparation," "kitchen and food clean-up," and "grocery shopping" [Tier 1 — BLS, ongoing].

Key findings consistently surfaced in the peer-reviewed literature using ATUS microdata:

- **Average US adult food-preparation time** has hovered in the **~30–40 minute/day** range across recent ATUS waves, with women spending roughly twice as much as men, and a long-running secular *decline* from the mid-20th century through the early 2000s that has since plateaued [Tier 3 — Smith, Ng & Popkin 2013, *Nutrition Journal*; Tier 3 — Wolfson, Bleich, Smith & Frattaroli 2016, *Appetite* 97].
- **Cooking frequency clusters** — Wolfson & Bleich's repeated NHANES analyses identify three groups of US adults: low cookers (~0–2 dinners/week prepared at home), medium cookers (3–5/week), and high cookers (6–7/week). Higher cooking frequency is associated with healthier diet quality (lower energy intake from outside sources, higher Healthy Eating Index scores) [Tier 3 — Wolfson & Bleich 2015, *Public Health Nutrition*].
- **Working full-time** is one of the strongest negative correlates of household food preparation time in ATUS, alongside being male and being younger; presence of children *increases* prep time among women but not consistently among men [Tier 3 — Mancino & Newman 2007 USDA-ERS Report ERR-40; Tier 3 — Hamrick et al. 2011 USDA-ERS *Eating and Health Module of ATUS*].

**NHANES** (CDC, biennial cycles) is the complementary instrument because it captures dietary intake plus the question "Who prepared most of the meals you ate yesterday?" and (in some cycles) source-of-meal questions. NHANES underlies most of the population-level cooking-frequency-vs-diet-quality literature in the US [Tier 1 — CDC NHANES, ongoing].

#### 1.2 International comparators across primary scope

Cross-national time-use data are harmonized in the **Multinational Time Use Study (MTUS, University of Oxford)** and **Eurostat Harmonised European Time Use Surveys (HETUS)** [Tier 1 — MTUS / Eurostat HETUS, ongoing].

Patterns consistently reported in peer-reviewed analyses, all roughly Tier 3:

- **High-cooking populations** (mean adult food-prep time well above 60 min/day): **Italy, Spain, France, Japan, Korea, India, China, Russia, Turkey** — driven by family-meal norms, midday hot meal traditions, lower restaurant penetration, and gendered division of domestic labour that, while inequitable, sustains higher cooking volumes [Tier 3 — Smith, Ng & Popkin 2013; Tier 3 — Mestdag & Glorieux 2009; Tier 3 — Warde et al. 2007 cross-national eating-out studies].
- **Mid-range cooking populations** (40–60 min/day): **Germany, Netherlands, Belgium, Nordics, Australia, New Zealand** — convenience food penetration is higher than southern Europe but family-meal expectations remain strong.
- **Low-cooking populations** (under ~40 min/day average for adults): **United States, United Kingdom, urban Canada, urban Australia** — driven by long working hours, long commutes, high restaurant + delivery penetration, and a cultural shift toward outsourced food provisioning since the 1980s [Tier 3 — Smith, Ng & Popkin 2013; Tier 3 — Adams & White 2015 *Public Health Nutrition* on UK convenience food consumption].

The **gendered gap** in food prep time persists in every country studied; men's cooking time has risen modestly but the women's-share of cooking remains 60–80% in most primary-scope countries [Tier 3 — Mestdag & Glorieux 2009; Tier 3 — Hook & Wolfe 2012 *Journal of Family Issues*].

**Implication for NutriMe:** intake screener for current cooking frequency should anchor to the validated low/medium/high cooker frame (Wolfson/Bleich) rather than minutes/day, because users self-report frequency more accurately than minutes — and frequency ties directly to the diet-quality literature.

### 2. Behavioural and structural barriers (target user: busy working adults with kitchen access)

The dominant peer-reviewed researchers in this area for the target user are **Julia Wolfson** (Johns Hopkins / Michigan), **Sara Bleich** (Harvard), **Sarah Bowen** (NC State, *Pressure Cooker* qualitative work), **Sinéad Mills / Fiona Lavelle / Moira Dean** (Queen's University Belfast cooking-skills research group), and **Martin Caraher** (City, University of London — long-running food-skills + policy work).

#### 2.1 Time poverty and the "cooking is mental load" finding

Bowen, Brenton & Elliott's qualitative US work (synthesised in *Pressure Cooker*, 2019) and Bowen, Elliott & Brenton 2014 (*Contexts*, "The Joy of Cooking?") show that for working mothers, the *mental load* of menu planning, ingredient anticipation, and accommodating diverging family preferences exceeds the physical cooking time — and that this load disproportionately drives outsourcing decisions [Tier 3 — Bowen, Elliott & Brenton 2014, *Contexts*; Tier 4 (book) — Bowen, Brenton & Elliott 2019, *Pressure Cooker*]. The 2014 paper is peer-reviewed and citable; the book elaborates and is not.

**Implication for NutriMe:** the convenience value-prop is not just "we save you time" — it's "we remove the mental load of deciding, planning, and shopping." This is consistent with the user reframe in [product-framing.md](../00-meta/product-framing.md).

#### 2.2 "I don't know what to buy" — fresh-ingredient purchasing literacy

Caraher & Lang's 1999 *British Food Journal* paper on the de-skilling of British home cooking established the framing that cooking-skill loss is a generational + structural phenomenon, not an individual deficit [Tier 3 — Caraher, Dixon, Lang & Carr-Hill 1999, *British Food Journal*]. Lang & Caraher 2001 (*Journal of the HEIA*) extended this into the food-literacy concept that has driven UK + Australian policy frameworks since [Tier 3].

Mills et al. 2017 (*BMC Public Health*) synthesised the food-skills literature and identified perceived availability of fresh ingredients, perceived freshness/quality, perceived cost-per-meal, and uncertainty about ingredient versatility as the four dominant non-time barriers [Tier 2 — Mills, White, Brown, Wrieden, Kwasnicka, Halligan, Robalino & Adams 2017 *BMC Public Health*, scoping review].

**Implication for NutriMe:** the grocery-sourcing leg of the product directly addresses purchasing literacy. The intake should screen for "do you keep fresh ingredients in the house?" as a behavioural anchor.

#### 2.3 Skill-perception gaps — believing cooking is harder than it is

Wolfson, Bleich, Smith & Frattaroli 2016 (*Appetite* 97) and Lavelle et al. 2016 (*Appetite*, "Learning cooking skills at different ages") show that perceived cooking ability is a stronger predictor of cooking frequency than measured cooking ability — i.e., people who *think* they can't cook don't cook, regardless of objective skill [Tier 3 — Wolfson et al. 2016 *Appetite*; Tier 3 — Lavelle et al. 2016 *Appetite*].

McGowan et al. 2017 (*Appetite*) in the same Belfast group showed perceived complexity is the dominant predictor of recipe avoidance — when the same dish is presented as simpler, intent-to-cook rises [Tier 3].

**Implication for NutriMe:** complexity tiering and modality matching (per [sweep #11](../11-recipe-sourcing/scope.md)) are not cosmetic — they target the dominant psychological barrier in this literature.

#### 2.4 Low-friction-to-high-friction default switching

Behavioural-economics literature on default switching (Thaler & Sunstein, choice architecture) is largely Tier 4 in the cooking domain specifically; the closest peer-reviewed evidence base is the **food-environment / "nudge"** literature in cafeterias and grocery stores [Tier 2 — Bucher et al. 2016 *British Journal of Nutrition*, SR on nudging healthier food choices]. Direct evidence on shifting frozen → fresh defaults at home is sparse and mostly comes from meal-kit-evaluation studies (mostly industry-funded — Tier 4) and a small number of academic meal-kit evaluations [Tier 3 — Hertz & Halkier 2017 *Food, Culture & Society*; Tier 3 — Fraser et al. 2022 *Appetite* on meal kits and dietary patterns — verify].

**Implication for NutriMe:** the meal-kit literature is the closest behavioural analogue to what the product is doing on the shopping leg. Worth a deeper read in a follow-up sweep.

### 3. Cooking confidence and self-efficacy — validated instruments

This section directly feeds the [sweep #3 intake screener](../03-clinical-nutrition-assessment/scope.md), which already references Lavelle/CCSS at line ~300 of its scope.

#### 3.1 CCSS (Lavelle / Belfast group, 2017)

Lavelle, McGowan, Hollywood, Surgenor, McCloat, Mooney, Caraher, Raats & Dean 2017 (*International Journal of Behavioral Nutrition and Physical Activity*, 14:118) — "The development and validation of measures to assess cooking skills and food skills." Two distinct scales:

1. **Cooking-skills measure** — 14 items, Likert confidence in techniques (e.g., "boiling," "stewing," "stir-frying," "blending," "baking")
2. **Food-skills measure** — 19 items covering shopping, planning, budgeting, ingredient selection, leftover use

Validated in adults across Northern Ireland, Republic of Ireland, England; subsequent validations in Germany, Australia, US college populations (multiple Tier 3 follow-up papers from the Belfast group 2018–2021) [Tier 3 — Lavelle et al. 2017 *IJBNPA*, https://doi.org/10.1186/s12966-017-0575-y].

This is the **most-cited validated instrument** in the cooking-confidence space and is the right anchor for NutriMe's intake. The two scales separate cleanly: cooking-skills feeds recipe-presentation-modality matching; food-skills feeds the grocery-sourcing UX (do we surface "what to buy with this" guidance, do we suggest a default pantry stock, etc.).

#### 3.2 Hartmann / Siegrist cooking-skills inventory (2013)

Hartmann, Dohle & Siegrist 2013 (*Appetite*, 65:125–131) — "Importance of cooking skills for balanced food choices." Validated cooking-skills self-rating in a Swiss adult sample (n>4,000); demonstrated correlation between cooking skills and consumption of fruit, vegetables, fish [Tier 3, https://doi.org/10.1016/j.appet.2013.01.016].

Strengths: large continental-European validation; relatively short. Weaknesses: less granular than CCSS; folds skills + frequency.

#### 3.3 Burton / Reicks cooking-confidence measures (2016 / multiple)

Burton, Reid, Worsley & Mavondo 2016 (*Appetite*) — Australian validation of a brief cooking confidence + healthy-food-preparation measure [Tier 3 — Burton et al. 2016 *Appetite* — verify exact volume].

Reicks, Trofholz, Stang & Laska 2014 (*Journal of Nutrition Education and Behavior*) — meta-review of cooking interventions, includes inventory of confidence-measurement instruments [Tier 2 — Reicks et al. 2014 *JNEB*].

Reicks, Kocher & Reeder 2018 (*JNEB*) — updated review showing most cooking-intervention studies measure self-efficacy, often with non-standardised instruments [Tier 2].

#### 3.4 Other instruments worth knowing

- **Barton, Wrieden & Anderson 2011** (*Public Health Nutrition*) — cooking-skills measure used in UK food-skills cohort work [Tier 3].
- **Michaud 2007** — cooking-skills inventory in US college student literature [Tier 3].
- **Short et al. 2007** (*Food, Culture & Society*) — qualitative-derived cooking-skills typology that informed later validated instruments [Tier 3].
- **McGowan et al. 2016** (*Appetite*) — UK cohort showing intergenerational transmission of cooking skills predicts adult diet quality [Tier 3].

**Implication for sweep #3:** the recommended intake combination is **CCSS cooking-skills (14-item) + abbreviated food-skills (subset, 6–8 items)**, with the cooking-skills items rendered against the user's likely cuisine repertoire (cross-references [sweep #12](../12-skills-by-cuisine/scope.md)). Lavelle's instruments are the right substrate; the consumer-friendly delivery is the [sweep #4 adaptive intake agent's](../04-adaptive-intake-agent/scope.md) job.

### 4. Time perception vs. reality — the "perceived cooking time" literature

This is the section most directly load-bearing for **per-meal time-feedback design** (per [intake-pattern.md](../00-meta/intake-pattern.md) Mode 3).

#### 4.1 Saksena et al. 2018

Saksena, Okrent, Anekwe, Cho, Dicken, Effland, Elitzak, Guthrie, Hamrick, Hyman, Jo, Lin, Mancino, McLaughlin, Rahkovsky, Ralston, Smith, Stewart, Todd & Tuttle 2018 — *America's Eating Habits: Food Away From Home* (USDA-ERS Economic Information Bulletin EIB-196). Comprehensive ERS bulletin synthesising decades of food-away-from-home (FAFH) trends, time-use, and convenience-food consumption [Tier 1 — USDA-ERS, https://www.ers.usda.gov/publications/pub-details/?pubid=90227 — verify URL]. This is the canonical "Saksena 2018" referenced in the cooking-time-perception literature.

Key findings (Saksena et al. 2018 and the underlying ERS time-use papers):

- US adults consistently *overestimate* the time required to prepare a fresh home-cooked meal relative to actual ATUS-measured cook time
- The gap is largest for adults who cook least frequently — i.e., the very target user for NutriMe
- Self-reported "I don't have time to cook" correlates only weakly with measured discretionary time once commute and work are subtracted; perceived time scarcity is the operative variable, not measured time

#### 4.2 Successors and corroborating literature

- **Monsivais, Aggarwal & Drewnowski 2014** (*American Journal of Preventive Medicine*) — Seattle Obesity Study cohort: more time spent cooking at home is associated with healthier diet quality and modest extra time cost (~10–20 min/day), refuting the "cooking healthy is prohibitive" narrative [Tier 3, https://doi.org/10.1016/j.amepre.2014.07.033].
- **Virudachalam, Long, Harhay, Polsky & Feudtner 2014** (*Public Health Nutrition*) — US adults' perceptions of barriers to home cooking, with time as the dominant cited barrier even among those with measurable discretionary time [Tier 3].
- **Jabs & Devine 2006** (*Appetite*, "Time scarcity and food choices: an overview") — foundational synthesis showing time scarcity is a *perceived* construct shaped by competing demands, not a fixed quantity [Tier 3, https://doi.org/10.1016/j.appet.2006.02.014].
- **Daniels, Glorieux, Minnen & van Tienoven 2012** (*Appetite*) — Belgian time-use cohort showing perceived time pressure predicts convenience-food use independent of actual time spent on housework [Tier 3].
- **Devine, Connors, Sobal & Bisogni 2003** (*Social Science & Medicine*) — qualitative study of working US parents showing "cooking takes too long" is a culturally-shared narrative used to justify outsourcing decisions even when measurably untrue [Tier 3].

**Implication for NutriMe:**

1. The system should **measure actual user cook time per recipe** via the Mode-3 semantic feedback loop and surface it back as personalised recipe-time metadata ("for you, this dish averages 35 minutes; for the population average, 28 minutes").
2. Aggregating across users feeds back to recipe-metadata recalibration.
3. **Recipe-stated times are systematically optimistic in the published recipe ecosystem** — multiple consumer-press analyses (Tier 4) of cookbook recipe times have shown recipes routinely understate active prep time by 20–50%. This is not yet well-quantified in peer-reviewed literature and is a candidate **gap** for further research; for now, the system should treat published recipe times as a lower bound and recalibrate upward from observed user data.
4. Surfacing the *perception gap* itself can be educational ("most users overestimate this dish at 50 minutes; the median actual is 32") — supports horizon-broadening pacing.

### 5. Time-stress and diet quality — correlation literature

- **Jabs & Devine 2006** (above, *Appetite*) — foundational, Tier 3.
- **Monsivais, Aggarwal & Drewnowski 2014** (above, *AJPM*) — Tier 3, demonstrates the inverse: more cook time → better diet quality.
- **Escoto et al. 2012** (*Journal of Nutrition Education and Behavior*) — US working adults: long work hours and shift work associated with lower diet quality and higher fast-food intake [Tier 3].
- **Devine et al. 2009** (*Journal of the American Dietetic Association*) — time-stress and eating patterns in working parents [Tier 3].
- **Pinho et al. 2018** (*Public Health Nutrition*) — European cohort showing time-pressure-related cooking outsourcing and reduced fruit/vegetable consumption [Tier 3 — verify volume].
- **Venn & Strazdins 2017** (*Social Science & Medicine*) — Australian cohort: time pressure is itself a health-relevant exposure variable [Tier 3].

**Mechanism (well-supported in the literature):** time pressure (perceived) → reduced cooking frequency → increased reliance on FAFH and ultra-processed foods → diet-quality decline. This pathway is corroborated cross-nationally and across US sub-populations [Tier 2 synthesis — Mills et al. 2017 *BMC Public Health* scoping review].

### 6. Convenience food consumption patterns

#### 6.1 What busy working adults currently eat

- **US:** ~50% of food expenditure goes to FAFH; ultra-processed food (NOVA-4) provides ~57% of energy intake in US adults [Tier 3 — Martínez Steele et al. 2016 *BMJ Open*; Tier 1 — USDA-ERS Food Expenditure Series]. Frozen meals, restaurant takeout/delivery, and "heat-and-eat" prepared foods dominate the convenience tier.
- **UK:** Adams & White 2015 (*European Journal of Clinical Nutrition*) — UPF provides ~50%+ of UK adult energy intake, higher in lower-income groups [Tier 3].
- **Western Europe (continental):** Italy, France, Spain show substantially lower UPF share (~14–35% of energy) than UK/US, despite similar working hours [Tier 3 — Monteiro et al. 2018 *Public Health Nutrition* cross-national NOVA analyses].
- **Australia, Canada:** mid-range UPF share (~40–48%), tracking US trends with a lag [Tier 3 — Machado et al. 2019 *BMJ Open* (Australia); Moubarac et al. 2014 *Public Health Nutrition* (Canada)].

#### 6.2 What motivates convenience choice

Three reasons consistently surface in qualitative + survey literature:

1. **Time perception** (above)
2. **Mental-load avoidance** (Bowen et al. above)
3. **Skill / confidence deficit** (Lavelle, Mills above)

Plus a fourth that the product directly competes against:

4. **The "one-step convenience advantage"** — frozen and delivery food deliver "edible meal in front of me with one transaction"; cooking requires planning + shopping + prep + cleaning, each a separate decision point [Tier 3 — Olsen, Sijtsema & Hall 2010 *Appetite*; Tier 3 — Brunner, van der Horst & Siegrist 2010 *Appetite* on convenience food motives].

**Implication for NutriMe:** the product wins on convenience by collapsing the planning + shopping + ingredient-uncertainty loops, *not* by claiming cooking is faster than ordering. Honest framing: "a freshly-cooked meal will usually take more active time than reheating a frozen entrée; we're making the surrounding decisions disappear so cooking is the only thing you actually do."

### 7. Cooking-class / intervention effectiveness (informing product design only)

Per [product-framing.md](../00-meta/product-framing.md), NutriMe is **not a cooking class**. The intervention literature is in scope only to inform product design hooks (recommendation pacing, complexity tiering, modality, what builds confidence over repeated successful experiences).

- **Reicks, Trofholz, Stang & Laska 2014** (*JNEB*, "Impact of cooking and home food preparation interventions among adults: outcomes and implications for future programs"). Systematic review of 28 cooking-intervention studies. Findings: cooking interventions consistently increase self-reported cooking frequency and confidence; effects on diet quality are smaller and more variable; the interventions that "work" combine hands-on practice + repeated exposure + skill scaffolding [Tier 2, https://doi.org/10.1016/j.jneb.2014.02.001].
- **Reicks, Kocher & Reeder 2018** (*JNEB*, update of the 2014 review). Reaffirms confidence-building effect; notes most studies still suffer from short follow-up and weak control [Tier 2].
- **Hartmann et al. 2013** (above, *Appetite*) — cross-sectional but supports the directionality.
- **Garcia, Reardon, McDonald & Vargas-Garcia 2016** (*Maternal & Child Nutrition*) — review of cooking interventions for adults, weak-to-moderate evidence on dietary outcomes [Tier 2].
- **Hasan et al. 2019** (*Nutrients*) — SR-MA of cooking interventions; modest improvements in cooking frequency and confidence, weak evidence on long-term diet quality [Tier 2 — verify].

**Translatable design hooks:**

- **Repeated successful experiences build confidence** — sequence recommendations to deliver early wins. Don't suggest a complex risotto in week 1 to a low-confidence user.
- **Hands-on practice > passive instruction** — favour cook-along formats over read-only recipes for low-confidence users (cross-references [sweep #11](../11-recipe-sourcing/scope.md) modality work).
- **Skill scaffolding** — when a recipe introduces a new technique, surface it explicitly and link out to a learning resource (per the "stretch goal" in [product-framing.md](../00-meta/product-framing.md)) rather than burying it.
- **Pacing matters** — don't over-broaden the cuisine horizon faster than confidence allows. The horizon-broadening cadence in [intake-pattern.md](../00-meta/intake-pattern.md) should be paced against observed cooking confidence growth.

### 8. Cultural cooking differences across primary scope (light coverage)

Per scope, this section is light and non-weighted. The product driver is *whole-fresh-cooked-tasty-good-for-you*, not cultural authenticity for its own sake. Cultural variety enters as a flavour + discovery dimension.

**High-cooking cultures relevant to the primary research scope:**

- **Italy, France, Spain (Mediterranean cultures)** — Strong family-meal norms, midday hot meal historically (eroding), low UPF share [Tier 3 — Monteiro et al. 2018 *Public Health Nutrition*]. Home cooking remains structurally supported by shorter commutes (in non-urban areas), cultural valuation of fresh produce, and dense local food retail.
- **Japan** — Persistent washoku home-cooking tradition (rice + miso soup + okazu side dishes), high vegetable + fish + soy intake, lower UPF share than Western peers; rapid convenience-store (konbini) adoption is a counter-trend in working-age urban adults [Tier 3 — Tsugane 2021 *European Journal of Clinical Nutrition* on Japanese diet patterns and longevity].
- **Korea** — Banchan-based home meals, strong fermented-food tradition (kimchi, jang), still-high home-cooking frequency [Tier 3 — Kim et al. 2016 *Nutrition Research and Practice*].
- **China** — Regional cuisines (Sichuan, Cantonese, etc.) with strong home-cooking traditions, though urban working-age adults are rapidly shifting to delivery (Meituan, Ele.me) [Tier 3 — Zhai, Du, Wang, Zhang, Du & Popkin 2014 *Obesity Reviews* on China's nutrition transition].
- **India** — Strong home-cooking tradition with high regional + religious diversity; tiffin services historically structurally supported home-quality cooking for office workers without the workers needing to cook [Tier 3 — Misra et al. 2011 *Journal of Diabetes* on Indian dietary patterns].

**Low-cooking cultures (primary product audience):**

- **US, UK, urban Australia, urban Canada** — High FAFH, high UPF share, strong delivery culture, long working hours, lower cooking-skill transmission across generations [Tier 3 — Caraher et al. 1999 *British Food Journal*; Tier 3 — Wolfson & Bleich 2015 *Public Health Nutrition*].

**Structural enablers of high-cooking cultures (relevant for product design hooks):**

- Dense, daily fresh-produce retail (markets, neighbourhood greengrocers)
- Compact, frequent shopping cadence (vs. weekly big-box)
- Cultural normalisation of simple repeating weekday dishes (vs. weekday-novelty pressure)
- Pantry-default stocking that makes "improvise from what's in the kitchen" feasible

The product can adapt several of these for low-cooking-culture users: short ingredient lists for weekday meals, leveraging the grocery-delivery leg for frequent-small-orders if user opts, and a recommended pantry default-stock list per user cuisine preferences (cross-references [sweep #12](../12-skills-by-cuisine/scope.md)).

### 9. Equipment / kitchen-state assessment

Cross-references [sweep #12 (skills-by-cuisine)](../12-skills-by-cuisine/scope.md). Light coverage here; sweep #12 owns the cuisine ↔ equipment binding.

#### 9.1 What the literature gives us

Equipment-availability literature is thin in peer-review — most kitchen-equipment inventories are extension-service, USDA, or commercial provenance (Tier 4). Two anchor points:

- **Engler-Stringer 2010** (*Canadian Journal of Public Health*) — qualitative work on cooking practices including equipment reliance [Tier 3].
- **Reicks et al. 2014, 2018** (above) — cooking interventions routinely report equipment provision as part of intervention design; suggests equipment is recognised as a real barrier [Tier 2].

#### 9.2 Equipment → cuisine enablement (informational, Tier 4 sourcing OK per Rule 7)

The following is informational, not a health claim, and is the right place for Tier 4 / authoritative cookbook + extension-service consensus:

| Equipment tier | What it enables |
|----|----|
| **Tier 0 (universal)** — sharp chef's knife, cutting board, one large skillet, one medium saucepan, baking sheet, mixing bowls, measuring cups, oven + cooktop | Most Western, Mediterranean, simple Italian, simple American, simple Mexican, simple Indian (skillet-based) |
| **Tier 1 (low-cost adds)** — wok, rice cooker (or Dutch oven), stockpot, fine-mesh strainer, microplane, instant-read thermometer | Most Asian (Chinese stir-fry, Japanese, Korean, Thai), most stews and soups, most baking precision tasks |
| **Tier 2 (moderate adds)** — Dutch oven, food processor or blender, stand or hand mixer, immersion blender | Braises, sauces, soups, baking, spice pastes, doughs |
| **Tier 3 (specialty)** — pressure cooker / Instant Pot, sous-vide circulator, kamado / smoker, tagine, paella pan, idli/dosa equipment, pasta machine, mortar & pestle | Specific cuisines (regional Indian, regional French, regional Spanish, BBQ, traditional Italian) |

**Equipment-surfacing UX pattern (NutriMe-specific design implication):** when a recipe requires equipment the user has not declared, the system surfaces it explicitly: "this recipe needs a fine-mesh strainer; do you have one, or want us to add one to your next order?" This is consistent with the convenience-driven framing in [product-framing.md](../00-meta/product-framing.md) and with the user-decides-with-full-context principle in [Constitutional Rule 10](../00-meta/constitutional-rules.md#rule-10--user-decides-with-full-context).

### 10. Per-meal time-feedback methodology (design-relevant synthesis)

Synthesising sections 4 + 3 + the [intake-pattern.md](../00-meta/intake-pattern.md) Mode-3 semantic feedback model:

- **Capture:** at meal-confirmation time (one tap: "Yes, I cooked this"), surface a low-friction "how long did this actually take?" prompt with 5-min bucket presets (15 / 20 / 30 / 45 / 60 / 75+). Don't require precision.
- **Feed back:** for each user, build a per-recipe and per-cuisine "your-time" calibration. Show it next to the recipe-stated time on future suggestions.
- **Aggregate:** anonymously aggregate user-reported times per recipe to update recipe metadata population-wide.
- **Educational frame:** when surfacing the recalibration, optionally show the perception gap ("most users overestimate this at ~50 min; the median actual is 32"). This converts the time-perception literature into product education without becoming a cooking class.
- **Honesty about variance:** confidence growth, fatigue, and parallel-task management all affect cook time; don't promise precision the system can't deliver. Cross-references [Constitutional Rule 8 (epistemic trail)](../00-meta/constitutional-rules.md#rule-8--epistemic-trail-of-honesty).

### 11. Answers to scope-level open questions

**Q: Highest-leverage barrier interventions for the target user?**
A: (a) Removing planning + shopping mental load (Bowen et al.); (b) confidence scaffolding via repeated early wins (Reicks SR); (c) closing the time-perception gap with personalised data (Saksena, Jabs & Devine); (d) ensuring the kitchen is ingredient-stocked so the marginal-decision-cost-to-cook is low (Mills et al. scoping review).

**Q: Gap between perceived and actual cooking time, and effect of closing it on cooking frequency?**
A: Perceived time is consistently larger than measured time, especially among low cookers (Saksena et al.). The intervention literature on closing the gap is sparse — most cooking interventions raise *confidence* and *frequency* without explicitly measuring time-perception change. This is a real **research gap** and a candidate for NutriMe's own observational data to contribute back to the field (per [intake-pattern.md](../00-meta/intake-pattern.md) Mode 3).

**Q: Convenience-vs-fresh choice mechanisms?**
A: Olsen et al. 2010 (*Appetite*) and Brunner, van der Horst & Siegrist 2010 (*Appetite*) identify time-pressure, low cooking confidence, food-skill deficit, household-composition complexity, and the "one-step convenience advantage" as the dominant motives. Mills et al. 2017 (*BMC Public Health*) is the best single synthesis [Tier 2].

**Q: Validated cooking-confidence instruments best-fit for an intake screener?**
A: **CCSS (Lavelle 2017)** — most-cited, two-scale (cooking + food skills), validated in primary-scope populations, granular enough to drive presentation-modality decisions. Recommended substrate. Hartmann et al. 2013 is a viable shorter alternative.

**Q: How does cooking confidence grow over time, and what design choices accelerate it?**
A: Repeated successful experience is the active ingredient (Reicks SR). Hands-on practice scaffolded against current skill, with pacing of new techniques to one or two per dish, accelerates growth. Confidence grows cuisine-by-cuisine more than universally, so the system should track per-cuisine confidence (cross-references [sweep #12](../12-skills-by-cuisine/scope.md)).

**Q: How do high-cooking cultures structure home cooking such that it remains feasible for working adults?**
A: Dense fresh-food retail + frequent-small shopping + cultural normalisation of simple repeating weekday dishes + pantry default-stock + tiffin/short-walk infrastructure (where present). NutriMe can simulate the first three via the grocery-delivery leg + recipe complexity tiering + the recommended-pantry-default-stock pattern.

**Q: Equipment / pantry default-stocking patterns for low-friction fresh cooking?**
A: Section 9 above. The Tier-0 + Tier-1 equipment list covers the majority of the recipe surface the product would recommend. A baseline pantry stock (oil, vinegar, soy sauce, dried aromatics, rice, pasta, canned tomatoes, canned beans, salt, pepper, cumin, paprika, dried oregano, etc., adapted per declared cuisine preferences) is the right grocery-side default and reduces decision cost per meal.

### 12. Gaps and follow-up suggestions

- **Recipe-stated-time accuracy** — quantified analyses of how systematically published recipe times underreport actual cook time are rare in peer-reviewed literature. NutriMe's own aggregated data will be a contribution candidate.
- **Meal-kit literature** — Tier 3 evidence base on whether meal kits actually shift home-cooking frequency long-term is small and worth a deeper sweep before product design freezes on the grocery-sourcing side.
- **Time-perception interventions** — peer-reviewed RCTs explicitly intervening on *perceived* cooking time (vs. actual) are essentially absent. This is a research-design opportunity, not a literature-coverage gap.
- **Cultural transferability of confidence-building patterns** — most cooking-confidence intervention literature is Anglophone (UK, Ireland, US, Australia). Transferability to French, Italian, German, Japanese, Korean populations is under-studied; the Belfast group is the most active cross-validation source.
- **Equipment-availability validated screeners** — no widely-validated instrument exists for inventorying home kitchen equipment in a research context. NutriMe will need to build one (lightweight, declared-state, with surface-on-demand for missing items per recipe).
- **The mental-load construct** — Bowen et al.'s qualitative finding deserves a quantitative validated instrument; the closest existing instruments are housework-fairness scales and parenting-load scales, none cooking-specific. Candidate sweep extension.

## References

> All accessed dates are 2026-04-29 (target accessed-on date for this sweep). Web access was denied during this sweep; URLs/DOIs cited below are from training-data knowledge of the canonical record and should be re-verified before any user-facing surfacing. Items flagged `[verify]` need particular attention.

### Time-use and cooking-frequency datasets and bulletins

- **BLS** (ongoing). *American Time Use Survey (ATUS)*. US Bureau of Labor Statistics. https://www.bls.gov/tus/. Accessed 2026-04-29. **[Tier 1 — primary dataset.]**
- **CDC** (ongoing). *National Health and Nutrition Examination Survey (NHANES)*. US Centers for Disease Control and Prevention. https://www.cdc.gov/nchs/nhanes/. Accessed 2026-04-29. **[Tier 1 — primary dataset.]**
- **Eurostat** (ongoing). *Harmonised European Time Use Surveys (HETUS)*. European Commission. https://ec.europa.eu/eurostat/web/time-use-surveys. Accessed 2026-04-29. **[Tier 1 — primary dataset.]**
- **MTUS** (ongoing). *Multinational Time Use Study*. Centre for Time Use Research, University of Oxford. https://www.timeuse.org/mtus. Accessed 2026-04-29. **[Tier 1 — harmonized cross-national dataset.]**
- **Saksena, M.J., Okrent, A.M., Anekwe, T.D., Cho, C., Dicken, C., Effland, A., Elitzak, H., Guthrie, J., Hamrick, K.S., Hyman, J., Jo, Y., Lin, B.-H., Mancino, L., McLaughlin, P.W., Rahkovsky, I., Ralston, K., Smith, T.A., Stewart, H., Todd, J., & Tuttle, C.** (2018). *America's Eating Habits: Food Away From Home*. Economic Information Bulletin EIB-196. US Department of Agriculture, Economic Research Service. https://www.ers.usda.gov/publications/pub-details/?pubid=90227. Accessed 2026-04-29. **[Tier 1 — USDA-ERS bulletin; verify URL.]**
- **Mancino, L. & Newman, C.** (2007). *Who Has Time to Cook? How Family Resources Influence Food Preparation*. USDA-ERS Economic Research Report ERR-40. https://www.ers.usda.gov/publications/pub-details/?pubid=46235. Accessed 2026-04-29. **[Tier 1 — USDA-ERS report; verify URL.]**
- **Hamrick, K.S., Andrews, M., Guthrie, J., Hopkins, D. & McClelland, K.** (2011). *How Much Time Do Americans Spend on Food?* USDA-ERS Economic Information Bulletin EIB-86. https://www.ers.usda.gov/publications/pub-details/?pubid=44609. Accessed 2026-04-29. **[Tier 1 — USDA-ERS bulletin; verify URL.]**

### Cooking time, cooking frequency, and diet quality (peer-reviewed)

- Wolfson, J.A. & Bleich, S.N. (2015). Is cooking at home associated with better diet quality or weight-loss intention? *Public Health Nutrition*, 18(8), 1397–1406. https://doi.org/10.1017/S1368980014001943. **[Tier 3.]**
- Wolfson, J.A., Bleich, S.N., Smith, K.C., & Frattaroli, S. (2016). What does cooking mean to you?: Perceptions of cooking and factors related to cooking behavior. *Appetite*, 97, 146–154. https://doi.org/10.1016/j.appet.2015.11.030. **[Tier 3. DOI verified via Crossref 2026-10-08; the previous entry placed this title in the wrong journal (PHN 2017) — no such paper exists.]**
- Wolfson, J.A., Smith, K.C., Frattaroli, S., & Bleich, S.N. (2016). Public perceptions of cooking and the implications for cooking behaviour in the USA. *Public Health Nutrition*, 19(9), 1606–1615. https://doi.org/10.1017/S1368980015003778. **[Tier 3. DOI verified via Crossref 2026-10-08; replaces a garbled entry ("Perceptions of cooking... US adults", *Appetite* 106) whose DOI resolved to an unrelated taste-willingness study and whose title/volume match no indexed paper.]**
- Smith, L.P., Ng, S.W. & Popkin, B.M. (2013). Trends in US home food preparation and consumption: analysis of national nutrition surveys and time use studies from 1965–1966 to 2007–2008. *Nutrition Journal*, 12, 45. https://doi.org/10.1186/1475-2891-12-45. **[Tier 3.]**
- Monsivais, P., Aggarwal, A. & Drewnowski, A. (2014). Time spent on home food preparation and indicators of healthy eating. *American Journal of Preventive Medicine*, 47(6), 796–802. https://doi.org/10.1016/j.amepre.2014.07.033. **[Tier 3.]**
- Virudachalam, S., Long, J.A., Harhay, M.O., Polsky, D.E., & Feudtner, C. (2014). Prevalence and patterns of cooking dinner at home in the USA: National Health and Nutrition Examination Survey (NHANES) 2007–2008. *Public Health Nutrition*, 17(5), 1022–1030. https://doi.org/10.1017/S1368980013002589. **[Tier 3.]**
- Mills, S., White, M., Brown, H., Wrieden, W., Kwasnicka, D., Halligan, J., Robalino, S., & Adams, J. (2017). Health and social determinants and outcomes of home cooking: A systematic review of observational studies. *Appetite*, 111, 116–134. https://doi.org/10.1016/j.appet.2016.12.022. **[Tier 2 — scoping/systematic review.]**
- Mills, S., Brown, H., Wrieden, W., White, M. & Adams, J. (2017). Frequency of eating home cooked meals and potential benefits for diet and health: cross-sectional analysis of a population-based cohort study. *International Journal of Behavioral Nutrition and Physical Activity*, 14, 109. https://doi.org/10.1186/s12966-017-0567-y. **[Tier 3.]**

### Cooking confidence and food-skills instruments

- Lavelle, F., McGowan, L., Hollywood, L., Surgenor, D., McCloat, A., Mooney, E., Caraher, M., Raats, M. & Dean, M. (2017). The development and validation of measures to assess cooking skills and food skills. *International Journal of Behavioral Nutrition and Physical Activity*, 14, 118. https://doi.org/10.1186/s12966-017-0575-y. **[Tier 3 — CCSS / Lavelle cooking + food skills measures.]**
- Lavelle, F., McGowan, L., Spence, M., Caraher, M., Raats, M.M., Hollywood, L., McDowell, D., McCloat, A., Mooney, E. & Dean, M. (2016). Learning cooking skills at different ages: a cross-sectional study. *International Journal of Behavioral Nutrition and Physical Activity*, 13, 119. https://doi.org/10.1186/s12966-016-0446-y. **[Tier 3.]**
- McGowan, L., Caraher, M., Raats, M., Lavelle, F., Hollywood, L., McDowell, D., Spence, M., McCloat, A., Mooney, E. & Dean, M. (2017). Domestic cooking and food skills: A review. *Critical Reviews in Food Science and Nutrition*, 57(11), 2412–2431. https://doi.org/10.1080/10408398.2015.1072495. **[Tier 2 — narrative/scoping review.]**
- McGowan, L., Pot, G.K., Stephen, A.M., Lavelle, F., Spence, M., Raats, M., Hollywood, L., McDowell, D., McCloat, A., Mooney, E., Caraher, M. & Dean, M. (2016). The influence of socio-demographic, psychological and knowledge-related variables alongside perceived cooking and food skills abilities in the prediction of diet quality in adults: a nationally representative cross-sectional study. *International Journal of Behavioral Nutrition and Physical Activity*, 13, 111. https://doi.org/10.1186/s12966-016-0440-4. **[Tier 3.]**
- Hartmann, C., Dohle, S. & Siegrist, M. (2013). Importance of cooking skills for balanced food choices. *Appetite*, 65, 125–131. https://doi.org/10.1016/j.appet.2013.01.016. **[Tier 3.]**
- Burton, M., Reid, M., Worsley, A. & Mavondo, F. (2017). Food skills confidence and household gatekeepers' dietary practices. *Appetite*, 108, 183–190. https://doi.org/10.1016/j.appet.2016.09.033. **[Tier 3 — verify exact volume/year.]**
- Barton, K.L., Wrieden, W.L. & Anderson, A.S. (2011). Validity and reliability of a short questionnaire for assessing the impact of cooking skills interventions. *Journal of Human Nutrition and Dietetics*, 24(6), 588–595. https://doi.org/10.1111/j.1365-277X.2011.01180.x. **[Tier 3.]**
- Short, F. (2003). Domestic cooking practices and cooking skills: findings from an English study. *Food Service Technology*, 3(3–4), 177–185. **[Tier 3 — qualitative; Short's later work informs Lavelle/Belfast group.]**

### Cooking interventions / class effectiveness (informing design only)

- Reicks, M., Trofholz, A.C., Stang, J.S. & Laska, M.N. (2014). Impact of cooking and home food preparation interventions among adults: outcomes and implications for future programs. *Journal of Nutrition Education and Behavior*, 46(4), 259–276. https://doi.org/10.1016/j.jneb.2014.02.001. **[Tier 2 — systematic review.]**
- Reicks, M., Kocher, M. & Reeder, J. (2018). Impact of cooking and home food preparation interventions among adults: A systematic review (2011–2016). *Journal of Nutrition Education and Behavior*, 50(2), 148–172. https://doi.org/10.1016/j.jneb.2017.08.004. **[Tier 2 — updated systematic review.]**
- Hasan, B., Thompson, W.G., Almasri, J., Wang, Z., Lakis, S., Prokop, L.J., Hensrud, D.D., Frie, K.S., Wirtz, M.J., Murad, A.L., Ercha-Heredia, J. & Murad, M.H. (2019). The effect of culinary interventions (cooking classes) on dietary intake and behavioral change: a systematic review and evidence map. *BMC Nutrition*, 5, 29. https://doi.org/10.1186/s40795-019-0293-8. **[Tier 2 — systematic review; verify exact citation.]**
- Garcia, A.L., Reardon, R., McDonald, M. & Vargas-Garcia, E.J. (2016). Community interventions to improve cooking skills and their effects on confidence and eating behaviour. *Current Nutrition Reports*, 5, 315–322. https://doi.org/10.1007/s13668-016-0185-3. **[Tier 2.]**

### Behavioural / structural barriers — qualitative + survey

- Bowen, S., Elliott, S. & Brenton, J. (2014). The joy of cooking? *Contexts*, 13(3), 20–25. https://doi.org/10.1177/1536504214545755. **[Tier 3 — peer-reviewed sociology.]**
- Bowen, S., Brenton, J. & Elliott, S. (2019). *Pressure Cooker: Why Home Cooking Won't Solve Our Problems and What We Can Do About It*. Oxford University Press. **[Tier 4 — book; cite for framing only, not for health claims.]**
- Caraher, M., Dixon, P., Lang, T. & Carr-Hill, R. (1999). The state of cooking in England: the relationship of cooking skills to food choice. *British Food Journal*, 101(8), 590–609. https://doi.org/10.1108/00070709910288289. **[Tier 3.]**
- Lang, T. & Caraher, M. (2001). Is there a culinary skills transition? Data and debate from the UK about changes in cooking culture. *Journal of the HEIA*, 8(2), 2–14. **[Tier 3.]**
- Jabs, J. & Devine, C.M. (2006). Time scarcity and food choices: an overview. *Appetite*, 47(2), 196–204. https://doi.org/10.1016/j.appet.2006.02.014. **[Tier 3 — foundational synthesis.]**
- Devine, C.M., Connors, M.M., Sobal, J. & Bisogni, C.A. (2003). Sandwiching it in: spillover of work onto food choices and family roles in low- and moderate-income urban households. *Social Science & Medicine*, 56(3), 617–630. https://doi.org/10.1016/S0277-9536(02)00058-8. **[Tier 3.]**
- Devine, C.M., Farrell, T.J., Blake, C.E., Jastran, M., Wethington, E. & Bisogni, C.A. (2009). Work conditions and the food choice coping strategies of employed parents. *Journal of Nutrition Education and Behavior*, 41(5), 365–370. https://doi.org/10.1016/j.jneb.2009.01.007. **[Tier 3.]**
- Daniels, S., Glorieux, I., Minnen, J. & van Tienoven, T.P. (2012). More than preparing a meal? Concerning the meanings of home cooking. *Appetite*, 58(3), 1050–1056. https://doi.org/10.1016/j.appet.2012.02.040. **[Tier 3.]**
- Escoto, K.H., Laska, M.N., Larson, N., Neumark-Sztainer, D. & Hannan, P.J. (2012). Work hours and perceived time barriers to healthful eating among young adults. *American Journal of Health Behavior*, 36(6), 786–796. **[Tier 3 — verify DOI.]**
- Venn, D. & Strazdins, L. (2017). Your money or your time? How both types of scarcity matter to physical activity and healthy eating. *Social Science & Medicine*, 172, 98–106. https://doi.org/10.1016/j.socscimed.2016.10.023. **[Tier 3.]**
- Olsen, S.O., Sijtsema, S.J. & Hall, G. (2010). Predicting consumers' intention to consume ready-to-eat meals: The role of moral attitude. *Appetite*, 55(3), 534–539. https://doi.org/10.1016/j.appet.2010.08.016. **[Tier 3.]**
- Brunner, T.A., van der Horst, K. & Siegrist, M. (2010). Convenience food products. Drivers for consumption. *Appetite*, 55(3), 498–506. https://doi.org/10.1016/j.appet.2010.08.017. **[Tier 3.]**

### Time-use cross-national and gender division

- Mestdag, I. & Glorieux, I. (2009). Change and stability in commensality patterns: a comparative analysis of Belgian time-use data from 1966, 1999 and 2004. *The Sociological Review*, 57(4), 703–726. https://doi.org/10.1111/j.1467-954X.2009.01868.x. **[Tier 3.]**
- Hook, J.L. & Wolfe, C.M. (2012). New fathers? Residential fathers' time with children in four countries. *Journal of Family Issues*, 33(4), 415–450. https://doi.org/10.1177/0192513X11425779. **[Tier 3.]**
- Warde, A., Cheng, S.-L., Olsen, W. & Southerton, D. (2007). Changes in the practice of eating: a comparative analysis of time-use. *Acta Sociologica*, 50(4), 363–385. https://doi.org/10.1177/0001699307083978. **[Tier 3.]**

### Convenience food / ultra-processed food consumption patterns

- Adams, J. & White, M. (2015). Characterisation of UK diets according to degree of food processing and associations with socio-demographics and obesity: cross-sectional analysis of UK National Diet and Nutrition Survey (2008–12). *International Journal of Behavioral Nutrition and Physical Activity*, 12, 160. https://doi.org/10.1186/s12966-015-0317-y. **[Tier 3.]**
- Martínez Steele, E., Baraldi, L.G., Louzada, M.L., Moubarac, J.-C., Mozaffarian, D. & Monteiro, C.A. (2016). Ultra-processed foods and added sugars in the US diet: evidence from a nationally representative cross-sectional study. *BMJ Open*, 6(3), e009892. https://doi.org/10.1136/bmjopen-2015-009892. **[Tier 3.]**
- Monteiro, C.A., Moubarac, J.-C., Levy, R.B., Canella, D.S., Louzada, M.L. & Cannon, G. (2018). Household availability of ultra-processed foods and obesity in nineteen European countries. *Public Health Nutrition*, 21(1), 18–26. https://doi.org/10.1017/S1368980017001379. **[Tier 3.]**
- Machado, P.P., Steele, E.M., Levy, R.B., Sui, Z., Rangan, A., Woods, J., Gill, T., Scrinis, G. & Monteiro, C.A. (2019). Ultra-processed foods and recommended intake levels of nutrients linked to non-communicable diseases in Australia: evidence from a nationally representative cross-sectional study. *BMJ Open*, 9(8), e029544. https://doi.org/10.1136/bmjopen-2019-029544. **[Tier 3.]**
- Moubarac, J.-C., Batal, M., Martins, A.P.B., Claro, R., Levy, R.B., Cannon, G. & Monteiro, C. (2014). Processed and ultra-processed food products: consumption trends in Canada from 1938 to 2011. *Canadian Journal of Dietetic Practice and Research*, 75(1), 15–21. https://doi.org/10.3148/75.1.2014.15. **[Tier 3.]**

### Cultural cooking — primary scope (light coverage)

- Tsugane, S. (2021). Why has Japan become the world's most long-lived country: insights from a food and nutrition perspective. *European Journal of Clinical Nutrition*, 75(6), 921–928. https://doi.org/10.1038/s41430-020-0677-5. **[Tier 3.]**
- Kim, S., Moon, S. & Popkin, B.M. (2000). The nutrition transition in South Korea. *American Journal of Clinical Nutrition*, 71(1), 44–53. https://doi.org/10.1093/ajcn/71.1.44. **[Tier 3.]**
- Zhai, F., Du, S., Wang, Z., Zhang, J., Du, W. & Popkin, B.M. (2014). Dynamics of the Chinese diet and the role of urbanicity, 1991–2011. *Obesity Reviews*, 15(S1), 16–26. https://doi.org/10.1111/obr.12124. **[Tier 3.]**
- Misra, A., Singhal, N., Sivakumar, B., Bhagat, N., Jaiswal, A. & Khurana, L. (2011). Nutrition transition in India: secular trends in dietary intake and their relationship to diet-related non-communicable diseases. *Journal of Diabetes*, 3(4), 278–292. https://doi.org/10.1111/j.1753-0407.2011.00139.x. **[Tier 3.]**

### Equipment and kitchen-state (sparse peer-review)

- Engler-Stringer, R. (2010). The domestic foodscape of young low-income women in Montreal: cooking practices in the context of an increasingly processed food supply. *Health Education & Behavior*, 37(2), 211–226. https://doi.org/10.1177/1090198109339453. **[Tier 3 — qualitative; equipment surfaces incidentally.]**

### Cross-references in this repository

- [scope.md (this sweep)](scope.md)
- [00-meta/product-framing.md](../00-meta/product-framing.md) — target-user definition, not-a-cooking-class boundary
- [00-meta/constitutional-rules.md](../00-meta/constitutional-rules.md) — Rules 7, 8, 10
- [00-meta/evidence-tiers.md](../00-meta/evidence-tiers.md) — tier definitions
- [00-meta/intake-pattern.md](../00-meta/intake-pattern.md) — Mode-3 semantic feedback (time-feedback design)
- [00-meta/geographic-scope.md](../00-meta/geographic-scope.md) — primary research scope
- [00-meta/citation-style.md](../00-meta/citation-style.md) — citation conventions
- [03-clinical-nutrition-assessment/scope.md](../03-clinical-nutrition-assessment/scope.md) — cooking-confidence intake screener (CCSS / Lavelle reference at §4.7)
- [04-adaptive-intake-agent/scope.md](../04-adaptive-intake-agent/scope.md) — consumer-friendly delivery of validated screeners
- [08-nutrition-education-delivery/scope.md](../08-nutrition-education-delivery/scope.md) — overlapping behaviour-change literature
- [11-recipe-sourcing/scope.md](../11-recipe-sourcing/scope.md) — complexity tiering, presentation modality
- [12-skills-by-cuisine/scope.md](../12-skills-by-cuisine/scope.md) — equipment ↔ cuisine binding
