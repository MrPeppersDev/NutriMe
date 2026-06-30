# NutriMe — LLM Provider Abstraction

> Architectural commitment: NutriMe is **LLM provider agnostic**. The system is built so any capable LLM provider can plug in via an adapter layer, with as few operational tweaks as possible. Today's choice (Anthropic Claude + Google Gemini) is a current default, not a baked-in dependency.

This is a foundational principle that cascades across [architecture.md](architecture.md) decisions — A3 (LLM provider + privacy posture), B1 (semantic RAG strategy + embedding providers), C1 (intake agent architecture), and forward.

## The principle

**The application addresses LLM capabilities, not LLM providers.** Code asks for "a provider that supports {reasoning, structured-output, ≥200k-context, low-latency-tier}" — the **capability vector** is the addressable unit. Providers register their capability vectors at the adapter layer; the routing layer matches request capability requirements against registered providers and selects one.

**Adding a new provider is dropping in an adapter, not refactoring the system.** When a new model emerges (better reasoning, better cost, better local-runnable, better PHI posture), the application doesn't need to know about it — it gets routed to automatically once the adapter is registered.

## What lives where

### Adapter layer

Provider-specific quirks live here, never in application code:

- System-prompt formats (Anthropic's `system`, Gemini's `systemInstruction`, OpenAI's `system` role)
- Tool-use schemas (Anthropic's `input_schema`, Gemini's `parameters`, OpenAI's `functions`)
- Thinking-mode flags (Anthropic's extended thinking, OpenAI's reasoning effort)
- Token counting (per-provider tokenizer)
- Rate-limit shapes (per-minute / per-day / per-tier)
- Streaming response shapes
- Error handling semantics (which errors retry, which fail-closed)
- PHI-handling capabilities (BAA-eligible? On-device?)
- Capability vector declaration

### Application layer

The application addresses LLM operations through a typed interface:

- Request capability requirements (vector)
- Structured input (typed against an internal schema)
- Expected structured output (typed against an internal schema)
- PHI category declaration (per [phi-handling.md](phi-handling.md))
- Failure tolerance (per [B3 cascade failure](architecture.md#b3--dynamic-research-expansion-infrastructure))

Application code never knows which provider handled a given call. Adapters map provider-specific response shapes to the internal schema.

## Capability vector — illustrative dimensions

Not exhaustive; final set defined in schema-design / agent-design phase:

- **Reasoning depth** — short / medium / deep / extended
- **Context window** — small (≤32k) / medium (≤200k) / large (≥1M)
- **Structured-output reliability** — basic / strict / strict-with-schema-validation
- **Tool-use** — none / single-tool / parallel-tools / nested-tools
- **Multimodal** — text-only / + images / + video / + audio
- **Search-grounded** — none / web-search / domain-search
- **Latency tier** — interactive (<2s) / standard (<10s) / batch (>10s)
- **Cost tier** — economy / standard / premium
- **PHI eligibility** — cloud-no-BAA / cloud-with-BAA / on-device
- **Deployment locus** *(added per A3-v2)* — local-OSS / cloud-fallback-only / cloud-permitted. Routing prefers local-OSS at production tier; cloud-fallback-only is reserved for the three A3-v2 dimensions (adversarial robustness / >64K context / low-resource cuisine language). MVP-host tier inverts the preference (cloud-permitted as primary) until production hardware lands.
- **Constitutional-enforcement eligibility** *(added per A3-v2)* — `enforces-constitutional-rules` (false for all current providers; constitutional enforcement lives in the hardcoded rule layer outside any LLM per A3-v2). DeepSeek V3.x explicitly do-not-use for any rule-following-dominant role.

## Current registered providers (as of 2026-06-29, post-Block-A-revision)

Captured for reference; subject to change as adapter implementations land. Per [A3-v2](architecture.md#a3-v2--llm-provider--privacy-posture-oss-local-primary--narrow-cloud-fallback):

- **OSS local primary** at production tier — Qwen3-32B (Apache 2.0) via Ollama 0.19+ MLX on Mac-class ≥64 GB. Graduation path: Qwen3-72B or GLM-5.2 (MIT) at the 128 GB hardware tier.
- **Anthropic Claude** family (Sonnet 4.x as named cloud fallback) — used narrowly for adversarial robustness on hardest condition-gated queries, long context above 64K tokens, and low-resource cuisine language work outside Qwen3's top-10 coverage.
- **Google Gemini** family — **optional, not architectural** under A3-v2. No multi-provider PHI-decomposition assumption baked in.
- **FoodyLLM-style domain fine-tunes** (Llama-3-8B or Qwen2.5-7B base + LoRA) for specialist modules (nutrient estimation, condition gating, food-entity linking). Per L3 build-time flag. **Stays MVP-relevant at the 24 GB tier.**
- **Local embedding models** for PHI lane (per B1 Q1.3) — `mxbai-embed-large` / `BGE-M3` / `nomic-embed-text` candidates.
- **Voyage** for non-PHI corpus embeddings.
- **DeepSeek V3.x** — flagged **do-not-use** as primary instruction-following / constitutional-rule-enforcement agent (T4 95/104 instruction-following ranking). R1-distill-32B variant is fine for math-heavy reasoning leaf tasks; V3.x line should not own constitutional enforcement.

**MVP-host refinement (A3-v2 refinement, 2026-06-29):** at the 24 GB MVP host tier, cloud handles the reasoning core (the original A3 Claude + Gemini posture). The provider-abstraction layer continues to look the same; the routing layer simply weights cloud-capable providers higher during the MVP-host phase. Once the production target lands (≥64 GB), the weighting flips to OSS-local-primary with cloud-as-narrow-fallback per A3-v2.

## Why this matters

- **Provider lock-in is a real risk.** Anthropic raises prices, Google deprecates a model, a new model from a third party leapfrogs both — the system shouldn't have to refactor to take advantage or to escape.
- **HIPAA posture may shift.** If we ever get BAA-eligible API access, a current PHI-lane local-LLM call should silently route to BAA-cloud-LLM with no application change.
- **Capability differentiation today is real but non-permanent.** Gemini's search grounding is unique today; tomorrow a different provider may ship better search grounding. The capability vector handles this transparently.
- **Local LLMs become first-class.** Per [B1 Q1.3](architecture.md#b1--semantic-rag-vs-structured-query-strategy), PHI-touching content already uses local embedding. Local LLMs (via Ollama or similar) can be first-class adapters for PHI-touching reasoning when capability matches — without the application caring.
- **Publication-ambition alignment.** Provider-agnosticism is a publishable architectural pattern — a real contribution to the field per [publication-ambitions.md](publication-ambitions.md). May feed publication target #2 (hybrid LLM + CAT + structured-instrument open agent).

## What this commits us to

- **Adapter-layer rigor from day one.** Cannot be retrofitted easily; designing-from-day-one is standard discipline per the publication-ambitions framing.
- **Internal schema discipline.** Application's typed interface to LLM responses must be defined cleanly + maintained. Schema drift = application drift.
- **Capability declarations on every LLM call.** Every call site declares its capability requirements; the routing layer enforces.
- **Test fixtures per-provider.** When a new provider's adapter lands, its outputs need to be tested against the internal schema in the same harness that tests existing providers.

## Source

User direction (2026-05-01, Stage 3 C1 dialogue):
> "One thing I wanna note is we should eventually be essentially LLM provider agnostic, be able to plug in whatever is capable and have it run with as few operational tweaks as possible."

## Related

- [architecture.md A3](architecture.md#a3--llm-provider--privacy-posture) — provider choice + PHI posture
- [architecture.md B1](architecture.md#b1--semantic-rag-vs-structured-query-strategy) — embedding provider split (Voyage + local) follows the same agnosticism pattern
- [architecture.md C1](architecture.md#c1--conversational-intake-agent-architecture) — intake agent topology + capability-vector routing
- [phi-handling.md](phi-handling.md) — PHI categories declared on every LLM call site
- [publication-ambitions.md](publication-ambitions.md) — provider-agnosticism is publishable architectural pattern
