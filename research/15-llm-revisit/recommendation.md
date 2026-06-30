# 15-llm-revisit — Synthesis & Recommendation

**Date:** 2026-06-29
**Sources:** [T1-food-llms.md](T1-food-llms.md), [T2-oss-landscape.md](T2-oss-landscape.md), [T3-apple-silicon-inference.md](T3-apple-silicon-inference.md), [T4-capability-fit.md](T4-capability-fit.md)
**Scope:** Block A revision against four pieces of June-2026 primary-source research. What lands now (architecture-shape decisions). What defers to build (transport, hardware migration, license posture revisit).

---

## TL;DR — one line per Block A decision

- **A1 (deployment shape):** Local-first, Mac-Mini-as-home-server, multi-tenant from day one (family-of-4 baseline; eventual syndication to friends/family). HIPAA-discipline posture preserved; PHI never leaves the home network in the steady state.
- **A2 (application shell):** iPhone app as primary client; Mac Mini as the always-on server. Native macOS app demoted from "primary shell" to "optional admin/dev surface."
- **A3 (LLM provider + privacy):** OSS local LLM as primary substrate (Qwen3-32B baseline, Qwen3-72B / GLM-5 at the 128 GB tier), with Anthropic Claude Sonnet 4.x as a narrow cloud fallback for adversarial-robustness, long-context-above-64K, and rare-cuisine-language work. Gemini optional, not architectural.
- **A4 (data persistence):** **No change.** Hybrid SQLite + markdown stands. The new requirement is one additional schema axis: `tenant_id` on substrate/operational/corpus base columns (tracked as F9).

---

## 1. Primary LLM strategy

### The breakpoint structure (T4 §"Breakpoints by parameter class")

| Tier | Verdict for NutriMe |
|---|---|
| **7B / 8B** | Narrow leaf tasks only (ingredient name normalization, format conversion). NOT viable as orchestrator or tool-calling agent. NutriBench-class failures on carbohydrate estimation; high tool-call failure on multi-step chains. |
| **30B dense** | **Minimum viable tier for the reasoning core.** Qwen3-32B (Apache 2.0) is the strongest single choice. IFEval 95% at 27B (Qwen3.5); BFCL v4 68.5% at 27B; reliable multi-step dietary reasoning. |
| **70B+** | Full-stack OSS becomes genuinely viable. Qwen3-72B or GLM-5 (MIT). Near-parity on tool calling; modest gap on adversarial constitutional rules and faithful citation discipline. |

### Recommended primary model

**Qwen3-32B (Apache 2.0)** for MVP. Dense, 128K context, 119 languages, native tool use, 19 GB at Q4_K_M (T2 §3.2). Fits Mac Mini M4 Pro 64 GB comfortably with headroom for four concurrent KV caches at 8K context each (T3 §4).

**Graduation candidate:** Qwen3-72B or GLM-5.2 at the 128 GB tier when the constitutional-discipline gap becomes load-bearing.

### Explicit do-not-use

**DeepSeek V3.x as primary constitutional-rule agent.** T4 surfaced a 95/104 instruction-following ranking — a structural risk for NutriMe's 10 non-negotiable rules. R1-distill-32B is fine for math-heavy reasoning leaf tasks; the V3.x line should not own constitutional enforcement.

### Domain fine-tuning path (T1)

**FoodyLLM (MIT, Llama-3-8B-Instruct + LoRA, 225K QA pairs)** is the reference recipe. It reaches 0.91–0.97 nutrient-estimation accuracy vs ~0.43 zero-shot baseline — a domain-fine-tune **reverses the gap** against frontier cloud models on its narrow surface (T1 §1.2, T4 §Dim 7). NutriMe's nutrient-estimation, condition-gating, and food-entity-linking modules should be specialist fine-tunes on top of the primary substrate, not parametric-knowledge calls to the orchestrator.

**Adjacent reusable artifacts:** Epicure ingredient embeddings (CC BY 4.0, 2 MB, 1,790 ingredients × 300-d); FlavorDB2 chemical reference (25K molecules, non-commercial — fine for personal use); FoodSEM for FoodOn/SNOMED entity linking; USDA FDC as nutrient ground truth (CC0, REST API, MCP wrapper available).

---

## 2. Hardware substrate

### Recommended MVP target

**Mac Mini M4 Pro 64 GB (~$2,200).** Silent, ~30–40 W under inference, no lid-close problem, sustained-thermal headroom (T3 §5). Fits Qwen3-32B Q4_K_M (20 GB weights) + 4 concurrent 8K-context KV caches (~6–8 GB) + runtime/macOS (~10 GB) inside ~44 GB usable.

### Capacity envelope at 64 GB

- 1 user, 32B Q4_K_M, 8K context: comfortable
- 4 users concurrent, 32B Q4_K_M, 8K each: fits with 6–9 GB headroom; per-user ~23 tok/s at true simultaneous peak (above human reading speed) (T3 §4)
- 70B at this tier: marginal at Q4_K_M (~42 GB weights); not recommended

### Hardware decisions explicitly deferred to build

- Whether to start at 64 GB or jump straight to a Mac Studio 128 GB / 192 GB tier
- Hardware migration plan once the household pool exceeds 4 concurrent users
- Whether eventual syndication takes us off Apple Silicon entirely (Linux + NVIDIA per T3 §6 production graduation)

---

## 3. Inference stack

### MVP — Ollama 0.19+ with MLX backend

Ollama 0.19 (March 2026) switched to MLX on Apple Silicon. Reported decode speedup: 93% on M5 Max, 30–50% on M4. Lowest-friction path from zero to running with `OLLAMA_KEEP_ALIVE=-1` (keep model warm) + `caffeinate -s` via launchd plist (prevent sleep) + Open WebUI for the family interface (T3 §1.3, §6).

### V1 — graduate to vllm-mlx

vllm-mlx (arXiv 2601.19139, EuroMLSys '26) brings paged KV cache + prefix caching to Apple Silicon. **Prefix caching matters specifically for NutriMe:** the system prompt carrying constitutional rules + user dietary profile is shared across sessions; prefix-cached, it isn't recomputed per request — this is material for a shared-prefix nutrition assistant (T3 §6).

### Quantization floor

**Q4_K_M is the right default.** The quality cliff sits between Q3 and Q4 (T3 §2). Q5_K_M as a tactical bump if a specific model feels shaky at Q4 on nutrition reasoning. **Below Q4 is not safe** for multi-step dietary reasoning — 2–4 MMLU points lost at Q3_K_M; coherence degrades on multi-step chains.

### Honest caveat (T3 §7)

**Concurrent multi-tenant on Apple Silicon is a genuine weak spot.** No production-proven paged-attention Metal implementation exists as of June 2026. For family-of-4 scale this is not blocking. For >10 concurrent users it would force a platform shift. Tracked as a flag.

---

## 4. Cloud fallback strategy

Cloud is **not** the primary substrate. Cloud is invoked for three specific dimensions where the OSS gap is material (T4 §Gap assessments):

1. **Adversarial constitutional robustness.** Anthropic Claude Sonnet 4.x with Constitutional AI is meaningfully more robust to jailbreak attempts on rule-bound queries. For NutriMe's hardest condition-gates (e.g., a user systematically probing a clinically-restricted ingredient), route through Claude — combined with the hardcoded rule layer (§5).
2. **Long context above 64K.** OSS 70B reliable to ~64K; Gemini 3.1 Pro is the only model that maintains accuracy to 128K+. Use only when epistemic-trail context can't be summarized below 64K.
3. **Low-resource cuisine languages.** Qwen3 covers top-10 languages and reverses the gap on Chinese. For Central Asian / many African cuisines, Gemini or Claude may be the cleaner path.

PHI-decomposition (`phi-handling.md`) still governs every cloud crossing. The boundary discipline is unchanged; the routing trigger is now "narrow capability fallback," not "default substrate."

---

## 5. Hardcoded constitutional rule layer

T4's Gap 2 is the most consequential finding for safety posture: **adversarial constitutional robustness does not close with parameter count alone.** It requires explicit adversarial fine-tuning that OSS providers haven't yet matched to Anthropic Constitutional AI or OpenAI deliberative alignment.

**Implication:** the hardest non-negotiable rules — particularly condition-gating for clinical constraints under Rule 1 (defer to clinician) and Rule 7 (peer-reviewed evidence floor) — should be enforced by a **deterministic rule layer outside the LLM**, not by trusting any LLM (OSS or cloud) to instruction-follow under adversarial pressure.

This shape decision lands now. The specific rule DSL and check ordering defer to build.

---

## 6. License posture

T2 confirms a 2026 license landscape that is cleaner than the 2024 picture:

- **Apache 2.0 dominant** for the recommended stack: Qwen3 family, Mistral Large 3 / Small 4 / Ministral, Gemma 4 (pivoted from Gemma Terms of Use in April 2026), Cohere Command A+ (pivoted in May 2026), OLMo 2
- **MIT clean:** DeepSeek V3/R1/V3.2, GLM-4.5/5/5.2, Phi-4 family, Kimi K2.6 (threshold-modified MIT; below 100M MAU / $20M MRR it's standard MIT)
- **Yellow:** Llama 4 Community License (700M MAU cap + EU multimodal-deployer restriction); Gemma 3 Terms of Use (pre-April 2026)
- **Red — exclude:** Hunyuan (excludes EU/UK/SK + no-model-output-to-train-others); Command R/R+ (CC-BY-NC)

NutriMe Apache-2.0-or-MIT-only posture is consistent with E3 (code license). Re-confirm at build if scope changes; for personal-and-friends-and-family, the field is wide open.

**E3 (AGPL) revisit:** explicitly deferred. The current finding is "no need to revisit yet" — Apache 2.0 still fits the build.

---

## 7. Chinese-provider supply-chain posture

T2 §3.3 distinguishes license text from supply-chain risk. For NutriMe's actual context (US-based, personal-and-family, local-hosted weights, nutrition domain):

- License text (MIT, Apache 2.0) is fully clean.
- Locally-hosted weights mean none of the API-data-to-China concerns apply.
- RLHF baked-in political-topic refusal is irrelevant to nutrition.
- Huawei Ascend training stack (GLM-5) is opaque but doesn't affect the weight artifact's behavior on cooking.

Qwen3 is therefore the cleanest Chinese option (Apache 2.0, no geographic restrictions, 119 languages). For enterprise or government deployment the calculus shifts — for our scope it does not.

---

## 8. Multi-tenant — what lands now vs. what defers

### Lands now (shape)

- **`tenant_id` as new schema axis** added to substrate base columns, operational base columns, and corpus markdown frontmatter base contract. Tracked as **F9** in `schema.md`.
- Multi-tenant from day one (family-of-4 baseline) — the schema must support it; the MVP can scope to a single tenant.
- The Mac Mini server is the multi-tenant boundary. Tenants are *household members*; PHI between tenants is **not** shared by default (per A1 HIPAA discipline + T5 three-level sharing model).

### Defers to build

- Networking transport (Tailscale vs. local-LAN vs. mDNS-based discovery)
- Authentication mechanism (per-tenant API key vs. system-level identity vs. Sign-In-with-Apple-server-side)
- Concurrent KV pressure management beyond `OLLAMA_NUM_PARALLEL=4`
- Eventual-syndication scaling plan (when household exceeds the Mac Mini envelope)
- Specific row-level-security implementation details inside SQLite

---

## 9. Active flags carried forward to build

| Flag | What | Source |
|---|---|---|
| **F9** | `tenant_id` as new schema axis (substrate + operational + corpus base columns) | This sweep |
| **L1** | Adversarial-rule load test against hardcoded rule layer before MVP ship | T4 §Gap 2 |
| **L2** | Verify Ollama 0.19+ MLX-path supports the chosen Qwen3-32B variant; fall back to llama.cpp Metal if not | T3 §7 |
| **L3** | Build a domain-fine-tune harness for FoodyLLM-style LoRA on Llama-3-8B (or Qwen2.5-7B) for nutrient-estimation and condition-gating modules | T1 §3 |
| **L4** | Calibrate Q4_K_M vs Q5_K_M decision per primary-model selection at build time | T3 §2 |
| **L5** | Validate cloud fallback gating criteria (adversarial probe / long-context / low-resource-language detection) — automation vs. user-explicit | T4 §Strategic recommendation |
| **L6** | Monitor Apple Silicon paged-attention Metal maturity for V1 graduation decision (vllm-mlx, vllm-metal, llama.cpp prototype #21961) | T3 §7 |

---

## 10. Mapping back to existing Block A originals

| Original (April 2026) | Revision (June 2026) — production target | MVP host refinement (2026-06-29) |
|---|---|---|
| **A1.** Pure local-first, single-device, no LAN exposure, no cloud sync | **A1-v2.** Multi-tenant home server (Mac-class ≥64 GB), local-first, family-of-4 baseline. PHI never leaves the home network in steady state. Networking transport deferred. | MVP host = user's existing MacBook Pro M4 Pro 24 GB (also primary work machine). Multi-tenant schema lands now; MVP runs single-tenant. Migration trigger to production target deferred to build. |
| **A2.** Native macOS app as primary shell | **A2-v2.** iPhone app primary client; Mac server as the always-on server. Native macOS app demoted to optional admin/dev surface. | Unchanged. |
| **A3.** Anthropic Claude + Google Gemini as primary cloud LLM substrate; PHI decomposed at query level | **A3-v2.** OSS local LLM primary (Qwen3-32B baseline). Claude Sonnet 4.x as narrow cloud fallback for adversarial-robustness / long-context-above-64K / low-resource-language. Gemini optional. Hardcoded constitutional rule layer outside the LLM. PHI-handling discipline unchanged for any cloud crossing. | **MVP posture: cloud-primary on the MVP host.** 24 GB doesn't fit Qwen3-32B at Q4_K_M (~20 GB weights vs ~16–18 GB usable post-macOS). Cloud carries the reasoning core; local OSS runs narrow leaf tasks only (FoodyLLM-style fine-tunes on 7B/8B base). Hardcoded rule layer + PHI decomposition discipline stand independent of where the LLM runs. |
| **A4.** Hybrid SQLite + markdown vault | **A4.** Unchanged. New schema axis `tenant_id` tracked as F9. | Unchanged. |

---

## 11. What is explicitly NOT decided in this sweep

- Transport-layer mechanics (Tailscale, mTLS, Sign-In-with-Apple)
- Specific iPhone-server protocol (REST-on-Bonjour vs. WebSocket vs. SSE-stream)
- Hardware migration triggers and replacement plan
- E3 license revisit (AGPL vs. Apache 2.0 stays Apache 2.0 for now)
- Concrete fine-tune training stack (Unsloth vs. axolotl vs. MLX-native)
- Whether condition-gating eventually wants its own fine-tune or a hardcoded rule DSL

These are build-time decisions and per the engineering-calibration discipline they should not be forced into the architecture revision.

---

## Source map

- **T1-food-llms.md** — verified all six named projects (FoodSky, FoodyLLM, FoodPuzzle, FlavorDB2, Epicure, FoodEarth) and surveyed adjacent OSS food/nutrition ecosystem
- **T2-oss-landscape.md** — 17 OSS LLM providers (Chinese + Western) with license, hardware footprint, and Apple Silicon feasibility tables
- **T3-apple-silicon-inference.md** — inference runtime survey (MLX, llama.cpp, Ollama, vllm-mlx, LM Studio, MLC, Jan, MetalRT, Docker Model Runner), memory budgeting per Apple Silicon tier, concurrent-serving analysis
- **T4-capability-fit.md** — capability-gap analysis across 7 dimensions (tool use, RAG grounding, long context, instruction-following, multilingual, reasoning, medical/nutrition domain) at 7B / 30B / 70B tiers vs. cloud frontier
