# NutriMe — PHI Handling

> Operational doc capturing how NutriMe handles Protected Health Information (PHI) under a HIPAA-discipline-at-data-handling-level posture. Defines the query-decomposition principle that lets the system use cloud LLMs (Anthropic Claude, Google Gemini) without sending full health profiles in a single call.

## Posture

NutriMe operates to **HIPAA discipline at the data-handling level**, not at the formal compliance level. What this means:

**In scope:**
- "Handle this carefully because it's PHI" mindset throughout — no plain-text dumps of full health profiles, no casual logging of PHI to convenience locations, no shortcuts that bypass the query-decomposition principle (below)
- Audit logs of PHI access + crossings (so we know what PHI was used when, in which operation, against which provider — accountability without enterprise-scale compliance overhead)
- macOS-native security primitives (Keychain for secrets, App Sandbox + Hardened Runtime for app integrity, codesigning, filesystem-level encryption is sufficient)

**Out of scope (per user direction):**
- Breach notification readiness (no enterprise contract / no covered-entity status to notify)
- Formal key management infrastructure (Keychain is sufficient at this scale)
- Encryption-at-rest as a formal compliance posture (filesystem encryption is fine; no additional formal layers required)
- Formal access control infrastructure (single-device, single-household, single trust domain — local OS access controls suffice)

This posture is **HIPAA-discipline-as-culture**, not HIPAA-compliance-as-certification.

## Cloud LLM strategy: Anthropic + Google with query-level PHI anonymization

NutriMe uses cloud LLMs (Anthropic Claude, Google Gemini) as its primary inference substrate. The privacy boundary is **at the query level**, not at the local-vs-cloud level. The principle:

> **No single LLM query carries a full health profile.** Queries are decomposed so each crossing carries only the minimum demographic + clinical context required for that specific operation, and the composite of all queries does not trivially reconstruct the user.

### Query decomposition

For any operation that would naively benefit from "send the whole user profile to the LLM," NutriMe decomposes the operation into multiple queries, each carrying a fragment of context. Examples (illustrative; full design lives in Stage 3 Block C):

- **Recipe filtering by allergens** — query carries `{allergen list, cuisine preferences}`. Does not carry age, sex, weight, conditions, medications.
- **Nutrient computation against composition data** — query carries `{recipe ingredients, nutrient targets as numerics}`. Does not carry the user identity, condition list, or clinical data that produced the nutrient targets.
- **Condition-aware substitution** — query carries `{ingredient X is contraindicated for: 'low-glycemic constraint'}`. Does not carry the underlying T2D diagnosis, A1c value, or medication context.
- **Cuisine knowledge / technique explanation** — query carries `{cuisine + technique}`. Carries no user-specific PHI at all.

### De-identification by composition

Even though NutriMe is single-user (the user is identifiable to themselves), the system structures cloud calls so that **no single query, and no easily-reconstructible composite of queries, exposes a recognizable health profile** to the LLM provider. Different queries carry different fragmentary contexts. The composite, if intercepted at the provider level, doesn't paint a coherent picture of an individual.

### What stays local

- Full user profile (demographics + conditions + medications + history + intake screener results)
- Wearable / biometric / clinical data raw
- Knowledge model state (per-user + per-household)
- Inventory state
- Semantic feedback history
- Audit logs

### What can cross (in decomposed form)

- Per-operation minimum context (per the principle above)
- Recipe selection criteria stripped of user identity
- Computed nutrient targets as numerics, not as derived-from-X-condition framings
- Cuisine / technique / ingredient knowledge queries (zero PHI)

## Why both Anthropic AND Google

Open thread flagged for resolution during Block C (intake agent architecture). Plausible reasons under consideration:

- **Provider diversity** for redundancy / failover
- **Capability differentiation** per task — Claude for reasoning + long-context; Gemini for search-grounded queries / multimodal / specific tool-use patterns
- **Cost optimization** — route cheap-and-fast queries to one provider, deep-reasoning to another

Resolution deferred to Block C; affects orchestration architecture but doesn't block A1/A3 from settling.

## Audit log requirements

Every PHI-touching operation logs:

- Timestamp
- Operation type (recipe filter, nutrient compute, condition substitution, etc.)
- Provider (Anthropic, Google, local)
- PHI categories included in the query (allergens / conditions / labs / wearables / medications / etc.) — categories, not values
- Result categories returned

Logs stay local. Logs are appendable but not casually-readable across the codebase — a dedicated audit-log surface reads them when needed (e.g., user wants to see "what's the system done with my data this month").

## Provenance trail integration

Per [Rule 8 epistemic trail](constitutional-rules.md#rule-8--epistemic-trail-of-honesty), every inference surfaces its provenance to the user. Under PHI-handling discipline, the trail also captures:

- Which queries crossed to cloud LLMs in producing this inference
- What context (categorically — "allergens + cuisine preferences," not raw values) crossed in each query
- Which provider handled each query

The user can see not just *what reasoning produced this recommendation* but also *what data crossed where to produce it*.

## Boundary enforcement (architectural)

The query-decomposition principle has to be enforced at call time, not at design time. Architectural mechanism (specifics deferred to Block C):

- LLM call site has a typed interface that requires specifying allowed-PHI-categories per call
- A pre-call boundary check verifies the actual context being sent matches the declared allowed categories
- Violations fail closed (the call is rejected, the operation falls back to local handling or surfaces an error)
- Tests at the boundary specifically guard against accidental PHI bleed

The boundary enforcement is **typed, tested, and fails closed** — boundary mistakes shouldn't be possible by accident.

## Source

User direction (2026-04-29, Stage 3 Block A dialogue):
> "We're going to be leaning on Anthropic and Google. We're just going to be very carefully deciding when, what, and why we send any sort of health data... when we do send it, we are anonymizing it in such a way that you would necessarily be able to trace it back to this individual person. That's breaking up query intents to not include a full health profile, things like that... Yes, HIPAA discipline at a personal scale, I think, is the right move. I don't think we're going to go super, super in-depth on it. I'm not concerned about breach notification readiness or proper key management or encryption at rest or really access controls or any of that, but I think audit logs are something that would be good for... It's just more naming it so that we understand how we should be handling data a little bit more carefully than just putting it in plain text somewhere."

## Related

- [Constitutional Rule 6 (health data local)](constitutional-rules.md#rule-6--health-data-stays-local-where-possible) — strengthened by this doc
- [Rule 8 (epistemic trail)](constitutional-rules.md#rule-8--epistemic-trail-of-honesty) — provenance trail integrates PHI crossings
- [knowledge-model.md](knowledge-model.md) — abstracted constraint layer is one mechanism by which PHI stays per-user
- [stage3-plan.md](stage3-plan.md) — A1 + A2 + A3 settled; query-decomposition specifics deferred to Block C design
