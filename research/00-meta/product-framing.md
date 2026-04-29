# NutriMe — Product Framing

> Status: living document. Updated as discovery clarifies scope.

## What NutriMe is

A **convenience-driven, holistic diet understanding, planning, and execution** product for busy working adults. The user describes themselves at intake (then iteratively over time); the system explains what a healthy diet looks like for someone like them across multiple cultural traditions, plans the meals, sources/orders the groceries, and walks them through cooking with timing, technique, and expectation-setting.

The single sentence: *NutriMe brings convenience to the mentally repetitive task of feeding yourself well, while building genuine understanding of what you're eating, why, and how it's affecting you.*

Concretely, NutriMe spans:

- **Intelligent intake** that elicits who the user is, what they like, what they want to try, and the clinical / cultural / behavioral context that shapes what good food looks like for them
- **Holistic dietary education** rooted in international science, surfaced transparently with evidence tiers and the [audit-as-education pattern](evidence-tiers.md#audit-as-education-pattern)
- **Meal planning** that honors who the user is, what they like, what they want to try, and progressively broadens their culinary horizons over time
- **Grocery sourcing and ordering** ("boom, shows up at my door")
- **Guided cooking execution** — when to start, how to cook, how long it takes, what to expect — with recipes presented in formats matched to the user's confidence level
- **Passive confirmation + semantic feedback** loop that captures whether meals worked, how they made the user feel, whether time estimates were accurate, and what to adjust going forward
- **Epistemic trail of honesty** for any inference combining clinical / wearable / feedback data ([epistemic-trail.md](epistemic-trail.md))

## Target user

**Busy working adults** who currently default to eating out, ordering in, or eating frozen / convenience meals because:

- They don't have the time
- They don't know any better
- The whole process of planning + shopping + cooking takes too much energy
- They reach a state where they don't even have fresh ingredients in the house because they never knew what to buy in the first place

**Constraints assumed about the target user:**

- Has access to a functioning kitchen
- Can acquire basic cooking equipment when a recipe requires it (the system surfaces equipment needs and confirms with the user)
- Cooks for one adult, OR for two adults cooking together
- **Children may be in the household as eaters but never as cooks.** The system plans meals that accommodate child dietary needs (allergens, growth requirements, age-appropriate foods, age-appropriate portions). Cooking remains an adult activity. Intake for child household members is done by a parent on the child's behalf.

**Primary product audience:**

US, Canada, Western Europe (UK, France, Germany, Netherlands, Belgium, Nordics, Iberia, Ireland, Switzerland, Austria) — households sharing general Western dietary conventions. Research draws from a much broader international scope (see [geographic-scope.md](geographic-scope.md)) so the system can offer Western users horizon-broadening suggestions from global culinary and nutrition traditions — especially relevant to younger generations more open to international cuisines.

**Cooking ability — design center:**

- *Default user is pretty good at cooking and can follow a recipe precisely.*
- The system accommodates a wide range below this center by adapting recipe presentation modality (video for lower confidence, structured text for the middle, cookbook-style prose for the higher end), inline terminology / technique lookup, and complexity-tier filtering — but does not teach cooking from scratch.

## What NutriMe is explicitly NOT

- A food / macro / calorie **logging app** ([Constitutional Rule 3](constitutional-rules.md#rule-3--no-food--macro--calorie-logging))
- A "did I hit my targets today" tracker
- A daily user-initiated check-in product
- A weight-loss or aesthetic-focused product
- A clinical replacement for a doctor or licensed nutritionist ([Constitutional Rule 1](constitutional-rules.md#rule-1--consult-a-professional))
- **A cooking class.** NutriMe provides *recipes paired with health guidance*. It does not teach knife skills, technique, or cooking fundamentals. A stretch goal is to surface *where to learn* a missing skill (link out, not deliver lessons).
- A product for food-insecure or kitchen-less populations — that's a different product
- A children's cooking education product (children are eaters in households, never cooks in this product)

## Personalization sources

Personalization comes from:

1. **In-depth initial intake** at onboarding (clinical-assessment-grade, consumer-friendly delivery)
2. **Periodic 5–15 minute check-ins** that revise the baseline + ongoing dialog that broadens horizons
3. **Wearable + biometric + clinical data** — labs, doctor-portal data, consumer wearables ([sweep #6](../06-wearable-data-availability/scope.md)), interpreted under the [epistemic trail](epistemic-trail.md)
4. **Passive confirmation + semantic feedback** — when the system *suggests* a meal and the user confirms cooked + ate, it captures: liked/disliked, how it made them feel, time-estimate accuracy, substitution effectiveness, cooking experience. The user never opens a logging form. Data is semantic, not numeric.

It does NOT come from continuous food tracking.

## Iterative intake — the defining property

The user describes themselves continuously, not once:

- Initial intake is in-depth (clinical assessment fidelity, consumer-friendly delivery)
- Periodic check-ins (5–15 min) revise the clinical baseline
- Ongoing dialog discovers preferences and progressively introduces nutritional + cultural breadth
- Example progression: a user starting on chicken nuggets and chicken fingers should, over time, be exposed to a wider variety of culinary options at increasing nutritional depth — not be told "no" but be taken on a journey

This shifts every system design downstream — see also [intake-pattern.md](intake-pattern.md).

## Convenience-driven framing

The product premise is convenience first. The user signs up because they want food decisions removed from their daily life. The system delivers convenience by:

- Removing planning effort (the system plans)
- Removing shopping effort (groceries arrive)
- Removing decision fatigue (here's tonight's meal, here's how long it takes)
- Removing skill-acquisition burden (recipes presented at the user's confidence level; what they don't know, they can look up)

Underneath the convenience surface, the substantive value prop is grounded scientific understanding + body-data correlation + iterative discovery — but the convenience is what gets the user in the door and keeps them.

## Source

- User reframe (2026-04-28): "this is not a logging app. I just want this to lean into understanding what creates a holistic diet for different people, how that's reflected across different cultures and food varieties and food cultures... boom, it shows up at my door and I have everything fed to me"
- User reframe (2026-04-28) on iterative intake: "the user doesn't describe themselves just once. I think this is a back-and-forth process to discover continuously what the user likes, broaden their horizons, and incorporate more nutritious, holistic foods over time"
- User reframe (2026-04-28) on semantic feedback: "When we suggest it and the user confirms that they cooked the thing and used the ingredients, we should be logging that and getting feedback on not just how the user liked the food but also how it made them feel"
- User reframe (2026-04-28) on target user (sweep #7): "The target of this is very busy working adults who normally would eat out or eat frozen meals because they either don't know any better or don't have the time. The whole process takes up too much time, so they get to a point where they don't even have fresh ingredients in their house because they never knew what to get in the first place."
- User reframe (2026-04-28) on cooking confidence (sweep #7): "I would consider initial users of this to be pretty darn good at cooking, able to follow recipes pretty precisely, but that's not going to be everybody, so that needs to be kind of met in the middle"
- User reframe (2026-04-28) on not-a-cooking-class boundary (sweep #7): "This isn't a cooking class; this is providing recipes in relation to health guidance. We are not cooking teachers; we are not teaching them how to cook. We're not teaching them how to use a knife."
- User reframe (2026-04-28) on convenience as core driver (sweep #7): "this is convenience driven. This is about bringing convenience to, you know, a mentally repetitive task where most people performing it actually lack a really basic understanding of what they're putting in their body, how it affects them and what their underlying needs might be"

## Related docs

- [Constitutional rules](constitutional-rules.md) — safety and disclosure rules that bind the product
- [Evidence tiers](evidence-tiers.md) — evidence grading framework
- [Intake pattern](intake-pattern.md) — the iterative intake + semantic feedback model in detail
- [Epistemic trail](epistemic-trail.md) — show-your-work principle for AI-correlated inferences
- [Geographic scope](geographic-scope.md) — default research scope across sweeps
