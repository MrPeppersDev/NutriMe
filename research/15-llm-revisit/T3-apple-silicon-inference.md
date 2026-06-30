# T3 — Apple Silicon LLM Inference Infrastructure (June 2026)

**Topic:** Local LLM inference runtimes for Apple Silicon — current state, concurrent-serving characteristics, memory budgeting, and a recommended stack for NutriMe's family-of-4 home server scenario.

**Scope:** Frameworks as of June 2026. Primary sources: framework GitHub repos, official blogs, arXiv 2601.19139, llama.cpp discussion #21961, Ollama blog, benchmark community sites.

---

## 1. Framework Survey

### 1.1 MLX + mlx-lm (Apple)

**Currency.** MLX is Apple's open-source ML framework, released late 2023 and reaching production maturity through 2025. As of June 2026 it is the acknowledged performance leader on Apple Silicon. mlx-lm is the companion text-generation library. The MLX team published "Exploring LLMs with MLX and the Neural Accelerators in the M5 GPU" on Apple Machine Learning Research (2026), signalling sustained first-party investment. At WWDC 2025 Apple ran three dedicated sessions establishing MLX as the preferred on-device LLM path.

**Apple Silicon support.** Native. MLX talks directly to the Metal compute shaders and — critically — is the first framework to exploit the M5's dedicated Neural Accelerators, giving a reported 4x time-to-first-token advantage over llama.cpp's Metal backend on M5 hardware. On M4 Max it beats llama.cpp decode speed by roughly 30–50% in independent benchmarks.

**Multi-tenant / concurrent.** mlx-lm exposes a `BatchGenerator` with configurable `--max-concurrent-requests`. It does not implement paged attention natively, but vllm-mlx (see §1.4) is built on top of MLX and does. Plain mlx-lm server is best described as sequential-with-batching: requests are batched within a single forward pass rather than interleaved through continuous batching. For NutriMe's low-QPS family scenario this is probably sufficient at 1–4 sessions, but head-of-line blocking is possible when a long-context prefill is in flight.

**Streaming.** Token-level streaming supported via SSE (Server-Sent Events) on the OpenAI-compatible `/v1/chat/completions` endpoint.

**KV cache.** Standard per-sequence KV cache. No paged attention in base mlx-lm; prefix caching is present for repeated system prompts in newer releases.

**Quantization.** MLX native 4-bit (int4) and 8-bit (int8) formats, plus mixed-precision (some layers at higher bit-width). MLX models are not interchangeable with GGUF — they run on Apple Silicon only.

**API surface.** OpenAI-compatible REST (`/v1/chat/completions`, `/v1/completions`). Python SDK.

**Model loading.** Weights loaded from Hugging Face MLX-format repos. No hot-swap of multiple models; one model per process. Loading a 32B Q4 model takes 10–20 seconds on M3/M4 Max (SSD read speed gating).

**Memory transparency.** MLX reports peak memory via `mlx.core.metal.get_peak_memory()`. No built-in dashboard; requires scripting.

**Production readiness.** High for single-instance deployment. No built-in reconnect/retry; must be wrapped. Actively maintained by Apple engineers.

**Community.** Apple-backed, rapidly growing. GitHub stars in the tens of thousands, weekly releases.

---

### 1.2 llama.cpp (Georgi Gerganov) — Metal backend

**Currency.** Extremely active: multiple commits per day, broad contributor base. The `ggml-org` organisation took over the repo in 2024. Metal backend is mature and ships as default on macOS.

**Apple Silicon support.** Metal acceleration is well-established and tested. All layers offloaded to GPU by default. Bandwidth utilisation is good but — as the Ollama MLX switch demonstrated — leaves 30–50% throughput on the table vs. MLX on M4 hardware, and more on M5.

**Multi-tenant / concurrent.** llama.cpp server supports `--parallel N` (number of concurrent decode slots) backed by a shared KV cache pool. Continuous batching (dynamic batching) is enabled by default and reportedly improves aggregate throughput 4x at the cost of ~18% higher p99 latency. However, the KV cache is a **unified, pre-allocated pool** — you set `--ctx-size` = max_tokens_per_sequence × N_parallel at startup. This wastes memory if sessions don't fill their slots and cannot grow dynamically. **PagedAttention is in active design** (discussion #21961): a working prototype on CUDA shows paged scales to 9× more concurrent sequences than unified before OOM, with ~3% throughput parity at lower concurrencies. Metal support for the paged scheduler is not yet merged as of June 2026.

**Streaming.** Token-level streaming via SSE. Well supported and stable.

**KV cache.** Unified pool today. Prefix caching available (`--cache-prompt`): if a system prompt or conversation prefix matches, llama.cpp reuses cached K/V values, cutting TTFT on repeated calls. Session-persistent KV cache documented in discussion #20572.

**Quantization.** Full GGUF family: Q8_0, Q6_K, Q5_K_M, Q5_K_S, Q4_K_M, Q4_K_S, Q3_K_M, Q3_K_S, Q2_K, IQ4_XS, IQ3_M, IQ3_XXS, IQ2_XXS, etc. Best ecosystem of community-quantized models via Hugging Face (Bartowski, TheBloke successors).

**API surface.** OpenAI-compatible REST via `llama-server`. JSON-schema-constrained generation (`--grammar`). gRPC not native.

**Model loading.** Weights loaded on startup; hot-swap requires process restart. `--model-alias` aliasing exists but no live reload.

**Memory transparency.** `llama-server` exposes `/v1/health` and metrics. Third-party dashboards (Open WebUI) add observability.

**Production readiness.** Very high for single-model always-on. Battle-tested, broad platform support, widely deployed. Reconnect: the HTTP server keeps listening; clients reconnect normally.

**Community.** Largest local-inference community. 70k+ GitHub stars (ggml-org total), issues typically triaged within days.

---

### 1.3 Ollama

**Currency.** Ollama 0.19 shipped in March 2026 with the MLX backend for Apple Silicon. Ollama 0.19+ is the current recommended release. Actively maintained, weekly point releases.

**Apple Silicon support.** As of 0.19+, Ollama uses MLX as the inference engine on Apple Silicon (preview, opt-in in 0.19, becoming default). Reported decode speed on Qwen3.5-35B-A3B: 58 → 112 tok/s on M5 Max (93% improvement). On M4 and M3, gains are 40–70% decode and a large TTFT improvement due to MLX's Neural Accelerator use. Prior versions used llama.cpp Metal; the GGUF path is retained as fallback for models not yet supported in MLX.

**Multi-tenant / concurrent.** `OLLAMA_NUM_PARALLEL` controls decode slots (default 4 in recent versions). `OLLAMA_MAX_LOADED_MODELS` defaults to 3× GPU count. Continuous batching is inherited from the underlying inference engine. On the MLX path, batching semantics follow mlx-lm. For 4 concurrent sessions on a 32B model and 64GB machine, `OLLAMA_NUM_PARALLEL=4` is documented as safe, with an expected 20–40% per-session latency increase vs. serial but 3–4× total throughput. At high parallelism, KV cache pressure causes swap jitter and p99 tail latency spikes — the main documented failure mode.

**Streaming.** Full token-level streaming. Ndjson and SSE.

**KV cache.** Delegated to the backend engine. With the GGUF/llama.cpp backend, unified pool as above. With MLX backend, mlx-lm batching semantics.

**Quantization.** GGUF formats (all variants) on the llama.cpp path. MLX 4-bit / 8-bit on the MLX path. Model library at ollama.com carries pre-quantized variants.

**API surface.** OpenAI-compatible REST (`/api/chat`, `/v1/chat/completions`). Native Ollama JSON API also available. No gRPC.

**Model loading.** `OLLAMA_KEEP_ALIVE` (default 5 min) keeps models warm; `OLLAMA_KEEP_ALIVE=-1` keeps them resident forever. Multi-model: LRU eviction when memory pressure hits. Near-instantaneous switch between already-loaded models in unified memory — no VRAM swap cost.

**Memory transparency.** No built-in memory dashboard. `ollama ps` shows loaded models. Third-party: Open WebUI, Ollama-UI.

**Production readiness.** High for home server. `systemctl`/`launchd` service available. HTTP server auto-restarts on failure. Wake-from-sleep: Ollama process survives; model reload after deep sleep may take 5–15 seconds.

**Community.** Largest end-user community. Best documentation of any local inference tool. 130k+ GitHub stars.

---

### 1.4 vLLM / vllm-mlx / vllm-metal

**Currency.** Upstream vLLM (Linux/CUDA) is the production gold standard for high-throughput serving, releasing 0.x versions frequently. Apple Silicon support exists through two separate community paths:

- **vllm-metal** (`vllm-project/vllm-metal`) — official community plugin. v0.2.0 released April 2026. Uses MLX as compute backend within vLLM's engine. Achieves unified paged varlen Metal kernel. 83× TTFT and 3.6× throughput improvement over v0.1.0.
- **vllm-mlx** (`waybarrios/vllm-mlx`) — independent project accepted at EuroMLSys '26. OpenAI + Anthropic compatible. Continuous batching, paged KV cache, prefix caching, SSD-tiered KV offload. Reaches 525 tok/s on M4 Max for small models. 3.4× throughput improvement at 5 concurrent requests; 4.3× at 16 concurrent requests (arXiv 2601.19139).

**Apple Silicon support.** Not native vLLM — Apple Silicon is not a supported first-class platform for the upstream project. Both Metal plugins are community-maintained and architecturally younger than the CUDA path.

**Multi-tenant / concurrent.** vllm-mlx is the most sophisticated Apple Silicon option for concurrent serving: it ports vLLM's paged attention and continuous batching to MLX. Block-based KV cache with Copy-on-Write prefix sharing. Two-tier KV offload: hot blocks in unified RAM, cold blocks to SSD (oMLX variant). This is the only Apple Silicon runtime with production-grade multi-session KV management as of June 2026.

**Streaming.** OpenAI-compatible SSE streaming.

**Quantization.** MLX format. GGUF support depends on the specific plugin variant.

**API surface.** OpenAI-compatible REST. Anthropic-compatible REST (vllm-mlx). Docker Model Runner (Docker Desktop 4.40+) wraps vllm-metal with GGUF support via llama.cpp fallback.

**Production readiness.** Early production. EuroMLSys '26 acceptance is a good signal but neither vllm-metal nor vllm-mlx has the operational track record of Ollama or llama.cpp. Issue response time: moderate (smaller maintainer teams).

**Community.** Growing rapidly. Backed by the credibility of the upstream vLLM project. Docker's official integration of vllm-metal is a significant adoption signal.

---

### 1.5 LM Studio

**Currency.** LM Studio 0.4.x (0.4.2 current as of mid-2026). Closed-source desktop application with active release cadence.

**Apple Silicon support.** Excellent UI polish and Apple Silicon optimisation. Supports both llama.cpp Metal and MLX backends selectable per-model.

**Multi-tenant / concurrent.** Continuous batching added in 0.4.0 (llama.cpp) and 0.4.2 (MLX). Headless deployment via `lms` CLI and "llmster" server mode (added January 2026). OpenAI-compatible local API on port 1234. Suitable for 1–4 concurrent sessions in a home setting.

**Quantization.** GGUF (all variants) and MLX format.

**API surface.** OpenAI-compatible REST. Local server mode.

**Production readiness.** Good for personal use. Closed-source limits observability and scripted management. No `launchd` integration out of the box.

**Community.** Large end-user community, active Discord. Closed-source limits community contributions.

---

### 1.6 MLC LLM / mlc-chat

**Currency.** GitHub `mlc-ai/mlc-llm` remains active (2024–2026 commits). TVM-based compilation approach: models are compiled for a target device before deployment.

**Apple Silicon support.** Metal support via compiled kernels. The compilation step is a barrier — models must be compiled for each target architecture. iOS app (MLC Chat) available on App Store.

**Multi-tenant / concurrent.** MLCEngine exposes an OpenAI-compatible REST server. Concurrent request handling is present but not documented to the depth of llama.cpp or vllm-mlx. No evidence of paged attention on the Metal path.

**Quantization.** 3-bit, 4-bit, 8-bit quantization via TVM compilation. Not GGUF-compatible.

**API surface.** OpenAI-compatible REST, Python SDK, JavaScript SDK, iOS/Android SDK.

**Production readiness.** Niche for Mac serving. The compilation step and non-GGUF model format mean the ecosystem is smaller. Best suited for iOS on-device deployment (NutriMe's iPhone client path) rather than Mac server.

**Community.** Moderate. Primarily research-oriented. Less active for Mac server use cases than Ollama or mlx-lm.

---

### 1.7 Jan

**Currency.** Jan 0.7.9 (March 2026), 42,000+ GitHub stars, 5.3M+ downloads. Apache 2.0 license.

**Apple Silicon support.** MLX backend added in v0.7.7. Metal via llama.cpp as fallback. Both supported.

**Multi-tenant / concurrent.** OpenAI-compatible API on `localhost:1337`. Primarily a desktop application; concurrent request handling is functional but not the focus. Not designed for headless always-on server operation.

**Quantization.** GGUF and MLX.

**API surface.** OpenAI-compatible REST. MCP integration for agentic use.

**Production readiness.** Personal use grade. GUI-dependent process lifecycle. Not recommended as the primary always-on server daemon.

**Community.** Very large end-user community. Open source with responsive maintainers.

---

### 1.8 MetalRT (RunAnywhere)

**Currency.** Emerging player (2026). Written in C++ against Apple's Metal API directly — no Python overhead, no framework abstraction.

**Apple Silicon support.** First-class and native. Claims 1.10–1.19× faster decode than mlx-lm and 1.35–2.14× faster than llama.cpp across benchmarks. Also supports Speech-to-Text and TTS, making it the only unified LLM + audio inference engine for Apple Silicon.

**Multi-tenant / concurrent.** Not yet documented at the depth of Ollama or vllm-mlx. Positioned as a speed benchmark target, not yet a full serving stack.

**API surface.** OpenAI-compatible REST.

**Production readiness.** Very early. Worth watching for NutriMe V1+, especially if the audio pipeline matters (meal logging via voice).

---

### 1.9 Docker Model Runner

**Currency.** Docker Desktop 4.40+ (February 2026). Official Docker product.

**Apple Silicon support.** llama.cpp Metal as default GGUF backend. vllm-metal as optional backend for higher-throughput scenarios.

**Multi-tenant.** Inherits from the underlying backend (llama.cpp or vllm-metal). Adds Docker networking and OCI-image-style model distribution (`docker model pull`).

**Production readiness.** Solid ops story: familiar tooling, container isolation, restart policies. Model storage via Docker Hub OCI registry. Good fit if the NutriMe server team prefers Docker-native operations.

---

## 2. Analysis A — Quantization Quality Tradeoffs

### GGUF K-Quants and I-Quants

The quality data below reflects community benchmarks on Llama-3-class 8B models vs. FP16 baseline. Larger models (30B+) generally show smaller relative perplexity increases at the same bit-width because more parameters give the quantizer more headroom.

| Format | Bits/weight | Perplexity delta (8B Llama-3) | MMLU delta | Notes |
|--------|-------------|-------------------------------|------------|-------|
| Q8_0 | 8.0 | ~0.01 (negligible) | <0.2 pp | Near-lossless; recommended for fine-tuning evaluation |
| Q6_K | 6.6 | +0.03 (7.35 vs 7.32 FP16) | <0.3 pp | Practically indistinguishable from FP16 |
| Q5_K_M | 5.7 | +0.05–0.10 | <0.5 pp | "High quality": below human-perceptible threshold for chat |
| Q4_K_M | 4.8 | +0.24 (7.56 vs 7.32) / +3.3% | ~1.1 pp | **Community default**; excellent size/quality tradeoff |
| Q3_K_M | 3.9 | +0.8–1.2 | 2–4 pp | Noticeable degradation on reasoning tasks |
| Q2_K | 2.6 | +2.5–4.0 | 5–10 pp | Severe quality loss; not recommended |
| IQ4_XS | ~4.25 | Similar to Q4_K_M, sometimes better | ~1.0 pp | I-quant with importance matrix; better quality per byte |
| IQ3_M | ~3.7 | Between Q3_K_M and Q4_K_M | ~2 pp | With good imatrix, recovers ~0.5 pp vs Q3_K_M |
| IQ2_XXS | ~2.2 | Severe; worse than Q2_K | 8–15 pp | Only viable for very large models (70B+) where size forces it |

**Quality cliff.** The cliff sits between Q3 and Q4. Going from Q5_K_M to Q4_K_M costs roughly 1 MMLU point and 3% perplexity — recoverable. Going from Q4_K_M to Q3_K_M costs 2–4 MMLU points and starts to degrade coherence on multi-step reasoning. Below Q3, degradation accelerates sharply. The I-quant series (IQ3_M, IQ3_S with importance matrix) recover roughly half the quality lost at Q3_K_M, but decode slower on consumer hardware.

For NutriMe (nutrition Q&A, meal planning, food safety): **Q4_K_M is the right default**. Q5_K_M if the target model's nutrition reasoning feels shaky at Q4.

### MLX Quantization

MLX 4-bit (int4) is roughly equivalent to Q4_K_M in quality — both hover around 1–1.5 MMLU points below FP16. MLX 8-bit (int8) is roughly equivalent to Q6_K: near-lossless in practice. MLX mixed-precision (some attention/MLP layers at 8-bit, others at 4-bit) can match Q5_K_M quality at Q4-class memory footprint. On Apple Silicon, MLX 4-bit runs 15–40% faster than GGUF Q4_K_M at equivalent quality — this is the main argument for using MLX-format models when ecosystem compatibility is not required.

### AWQ vs GPTQ vs GGUF

- **AWQ** (Activation-aware Weight Quantization): best 4-bit quality for CUDA targets (~95% quality retention vs FP16). Does **not** run on Apple Silicon natively.
- **GPTQ**: older 4-bit method, slightly lower quality than AWQ (~90% retention), CUDA-only.
- **GGUF Q4_K_M**: ~92% retention, runs on Apple Silicon, CPU, and CUDA. Mixed-precision within layers (K and V matrices kept at higher precision) is why it beats naive 4-bit.
- **MLX 4-bit**: ~93% retention, Apple Silicon only, faster than GGUF on Apple Silicon.

**For NutriMe's Apple Silicon server: GGUF Q4_K_M for Ollama/llama.cpp deployment; MLX 4-bit for vllm-mlx or direct mlx-lm deployment.** The quality difference between them is negligible for the task domain.

---

## 3. Analysis B — Memory Budgeting by Apple Silicon Tier

**Rule of thumb:** Usable unified memory for inference = total RAM × 0.70 (macOS + runtime + swap headroom consume ~30%). KV cache at 8K context ≈ 1–2 GB per session for a 32B model (varies by architecture and batch size).

**Model weight memory at Q4_K_M:**
- 7B → ~4.5 GB
- 13B → ~8.5 GB
- 32B → ~20 GB
- 70B → ~40 GB
- 405B → ~230 GB

### M3 / M4 base, 16 GB

Usable ~11 GB. Maximum: 7B Q4_K_M (4.5 GB weights + 1 GB KV + runtime fits). 13B is marginal; 32B is impossible. **1 concurrent session**: 7B only. **4 concurrent sessions**: 7B only with minimal context (2K). This tier is not viable for a shared family server.

### M3 Pro / M4 Pro, 32 GB

Usable ~22 GB. Maximum at Q4_K_M: 13B comfortably, 14B at squeeze. **1 concurrent session at 8K context**: 13B Q4_K_M fits (8.5 + 2 + runtime ≈ 14 GB — comfortable). **4 concurrent sessions**: 13B with 4 × 2K context ≈ 8.5 + 8 GB KV = 16.5 GB — tight but feasible. 32B: does not fit. This tier is viable for a family assistant using a 13B model, which is already quite capable (Mistral-Nemo-12B, Llama-3.2-11B range).

### M3 Max / M4 Max, 64 GB

Usable ~44 GB. **1 concurrent session at 8K context**: 32B Q4_K_M (20 + 2 + runtime ≈ 25 GB — comfortable). **4 concurrent sessions at 8K context each**: 32B + 4 × 2 GB KV = 28 GB — fits. 70B: weight alone is 40 GB; with runtime and any context, exceeds 44 GB usable. 70B at Q3_K_M (~26 GB) is technically possible but below recommended quality. **This is the sweet spot for NutriMe's described use case (32B-class, 4 sessions)** — provided memory is tightly managed.

### M3 Max / M4 Max, 96–128 GB

Usable ~65–90 GB. **1 session at 8K**: 70B Q4_K_M fits comfortably (40 + 2 + runtime ≈ 45 GB). **4 sessions at 8K**: 70B Q4_K_M + 4 × 2 GB KV ≈ 48 GB — fits in 65 GB usable. At 128 GB there is generous headroom. This tier can serve 70B class models to 4 family members simultaneously. Decode speed on 70B: 8–15 tok/s on M4 Max — slower than human reading speed, but plausible for async app use.

### Mac Studio M2 Ultra / M3 Ultra, 192 GB+

Usable ~135+ GB. Can run 70B Q4_K_M (40 GB) with large KV cache, or 105B+ models. M3 Ultra achieves ~41 tok/s on Gemma-3 27B and proportionally higher bandwidth vs M3 Max. For NutriMe scale this is significant overkill, but it is the only local Apple Silicon platform that can run 70B-class models at high-throughput concurrent use. Approximate 70B decode: 20–30 tok/s on M2 Ultra, faster on M3 Ultra due to higher memory bandwidth.

---

## 4. Analysis C — Concurrent Serving Feasibility for Family-of-4

**Scenario:** 4 simultaneous chat sessions, 32B Q4_K_M model, 64 GB M-series machine (M3 Max or M4 Max).

**Memory check:** 32B Q4_K_M ≈ 20 GB weights. KV cache at 8K context per session ≈ ~1.5–2 GB per session × 4 = 6–8 GB. Runtime + macOS ≈ 8–10 GB. Total: ~35–38 GB against ~44 GB usable. This fits with 6–9 GB to spare.

**Throughput.** Bandwidth ceiling for 32B Q4 decode: approximately 94 tok/s on M4 Max (400 GB/s ÷ ~4.2 GB/token for 32B weights). With 4 concurrent decode streams all competing for the same bandwidth, aggregate throughput ≈ 94 tok/s shared across 4 users ≈ **~23 tok/s per user** (at full utilisation). In practice, not all 4 users decode simultaneously (conversational back-and-forth), so per-user interactive throughput is likely 30–50 tok/s most of the time, dropping to 15–25 tok/s at true simultaneous peak. This is **above human reading speed** (~12–15 tok/s) even at worst-case peak. Feasibility: yes.

**KV-cache bottleneck.** The primary constraint is not memory bandwidth but KV cache inflation. If any session uses a long context (32K+), one session's KV cache alone (≈6–8 GB) can crowd out another session's headroom. Practical mitigation: cap context at 8K per session in the server configuration.

**Prompt processing (TTFT) latency.** Prefill is compute-bound, not bandwidth-bound. A 1K-token system prompt prefill on a 32B model takes 1–4 seconds on M4 Max with a single user. With 4 concurrent prefills, TTFT could be 4–12 seconds for the last-queued request. This is the most noticeable UX problem. Mitigation: prefix caching (system prompt cached after first use), and routing all 4 users through a shared system prompt.

**Bottleneck ranking for this scenario:**
1. KV cache memory under long contexts — hardest to manage
2. Prefill latency at true simultaneous session start — noticeable but rare
3. Decode bandwidth saturation — acceptable at family scale (4 users ≠ continuous decode)

**Conclusion:** 4 concurrent sessions on a 32B Q4_K_M model on 64 GB M4 Max is **realistic** for a family of 4 with conversational, low-QPS use. It is not comfortable for sustained simultaneous streaming (e.g., 4 long document summarisations running in parallel). For that, step up to 96 GB.

---

## 5. Analysis D — Always-On Home Server Practicalities

### Sleep / Wake / Lid-Close

macOS aggressively sleeps laptops on lid close and after idle timeout. For an always-on server:

- **`caffeinate -s`** (system sleep prevention): simplest fix. Keeps the Mac awake indefinitely. Runs in the terminal or as a `launchd` job. Power cost: continuous inference-ready idle draws 8–15 W on M-series (vs 2–4 W deep sleep).
- **`caffeinate -i`** (prevent idle sleep without blocking display sleep): better if you want the screen to sleep but the CPU/GPU to stay ready.
- **Programmatic power assertions via IOKit** (pmset/IOPMAssertionCreateWithName): allows inference servers to hold awake while requests are queued and release when idle. This is the production pattern.
- **Lid close on laptop**: macOS enters "clamshell sleep" unless connected to external display and power. A headless laptop server therefore requires either an external display (or HDMI dummy plug) and AC power, or `pmset -a disablesleep 1` (requires SIP partial disable — not recommended).
- **Mac Studio / Mac Mini**: no lid; ignores this problem entirely. `systemsetup -setcomputersleep Never` is sufficient.

### Power Draw

| State | M4 Pro Mac Mini | M3 Max Laptop | M2 Ultra Mac Studio |
|-------|-----------------|---------------|---------------------|
| Idle (macOS only) | ~4 W | ~5 W | ~10 W |
| Inference (moderate) | ~30–40 W | ~40–60 W | ~80–120 W |
| Peak inference | ~65 W (max rated) | ~90 W (peak) | ~200 W |

Electricity cost at $0.15/kWh: a Mac Mini M4 Pro doing moderate LLM inference for 8 hours/day costs roughly $1.30–1.75/month. A Mac Studio M2 Ultra at ~100 W average: ~$11/month. Both are negligible.

### Thermal Behavior

Mac Studio and Mac Mini use active cooling with sufficient thermal headroom for sustained inference. In practice, a Mac Mini M4 Pro running continuous LLM inference stays cool; the M3 Ultra Mac Studio was reported to run hot in some Apple Community threads but within spec.

**Laptop chassis**: sustained inference at 40–90 W on a MacBook Pro in a closed/clamshell setup is not recommended. The chassis is designed for burst workloads. Sustained load at 100% GPU for hours causes throttling and fan noise. For a true always-on inference server, a laptop is a poor choice vs. Mac Mini or Mac Studio.

### Model Reload Overhead on Cold Start

Loading a 32B Q4_K_M model (~20 GB from NVMe SSD):
- Mac Mini M4 Pro (internal SSD ~5 GB/s): ~4–5 seconds
- Mac Studio (similar SSD speed): ~4–6 seconds
- Ollama keeps models warm via `OLLAMA_KEEP_ALIVE` — with `-1` setting, the model stays loaded across client disconnects indefinitely, so cold-load only happens on daemon restart.

### Recovery from OS Sleep Mid-Session

When macOS sleeps and wakes:
- Ollama HTTP server survives wake (process stays alive).
- In-flight requests that were streaming when sleep occurred: the client TCP connection drops; the client must retry. Well-designed clients (with exponential backoff + retry) handle this transparently.
- The model weights remain in unified memory through sleep on M-series (memory is preserved, not powered off). After wake, the first request after sleep may incur 1–3 second "warm-up" before decode speed normalises.
- With `caffeinate -s`, the machine never sleeps and this is a non-issue.

### Dedicated Server vs. Laptop

For NutriMe's always-on family server:
- **Mac Mini M4 Pro 64 GB** (~$2,200): best price/performance for 32B-class models, 4 sessions. Silent, low power, compact. No GPU throttling under sustained load. Strongly preferred.
- **Mac Studio M3 Ultra 192 GB**: overkill for family-of-4 but the right choice if the project scales or 70B models are required at quality.
- **Laptop (MacBook Pro)**: viable for development and demos; not recommended for always-on headless server production use due to thermal constraints and lid-close complications.

---

## 6. Analysis E — Recommended Stack for NutriMe

### Context

Family-of-4 scope, low QPS (mostly idle, 1–4 simultaneous conversational sessions at peak), local-first, privacy-preserving. MVP is a home server running an open-weight model. Commercial graduation is a potential future state.

### MVP — Get Running in a Day

**Hardware:** Whatever M-series Mac is already available, ≥32 GB.

**Stack:** Ollama 0.19+ (MLX backend enabled on Apple Silicon) + Open WebUI for family UI.

**Model:** Llama-3.1-8B-Instruct Q4_K_M or Qwen2.5-14B-Instruct Q4_K_M depending on RAM. Both are well-served by Ollama's model library.

**Rationale:** Ollama is the lowest-friction path from zero to running. The March 2026 MLX switch delivers 2× decode speed on Apple Silicon with no configuration. Open WebUI adds multi-user session management, conversation history, and a family-friendly interface. `OLLAMA_KEEP_ALIVE=-1` keeps the model warm. `caffeinate -s` in a launchd plist keeps the machine awake.

**Limitations to document:** Ollama does not expose paged attention; KV cache is allocated per-session, not globally optimal. At MVP this is fine.

### V1 — Tuned for Quality and Reliability

**Hardware:** Mac Mini M4 Pro 64 GB or Mac Studio M3/M4 Max 128 GB.

**Stack:** vllm-mlx or Ollama 0.19+ with MLX backend + Open WebUI + launchd service.

**Model:** Qwen2.5-32B-Instruct or Llama-3.3-70B-Instruct.
- 32 GB machine: Qwen2.5-32B Q4_K_M (20 GB weights, 4 sessions at 8K each).
- 64 GB machine: same, with more KV headroom.
- 128 GB machine: Llama-3.3-70B Q4_K_M (40 GB weights, 4 sessions comfortable).

**Why vllm-mlx over plain Ollama at V1:** vllm-mlx's paged KV cache and prefix caching reduce tail latency under concurrent load. Shared system prompts (NutriMe's nutritional context, user dietary profiles) get cached after the first session and are not recomputed for subsequent sessions. This is material for a shared-prefix nutrition assistant.

**Concurrent handling:** `--max-concurrent-requests 4` in vllm-mlx, or `OLLAMA_NUM_PARALLEL=4` in Ollama. Monitor KV cache utilisation; cap context per session to 8K to stay in budget.

**Observability:** Wrap with a reverse proxy (Caddy or nginx) for request logging. Pipe vllm-mlx metrics to a local Prometheus + Grafana instance if desired.

**Reliability:** launchd plist with `KeepAlive = true`. `caffeinate -s` embedded in launchd or managed via IOKit power assertion from the server process. Wake-on-LAN via Ethernet (Mac Mini) for remote management.

### Production Graduation

If NutriMe moves to a commercial multi-tenant product:

**Platform shift:** Move from Apple Silicon to Linux + NVIDIA H100/L40S for the inference tier, with upstream vLLM (full production paged attention, tensor parallelism, disaggregated prefill). Apple Silicon remains viable for development, evaluation, and cost-sensitive hobby deployment, but is not competitive with CUDA for throughput at scale.

**Apple Silicon niche at production scale:** Apple Silicon Mac Studio / Mac Pro retain value for: privacy-critical deployments where data must stay on-premises, edge inference for individual practices, and cost-sensitive non-profit deployments. The Mac Studio M3 Ultra at $7,999 and 192 GB can run a 70B model at 25–30 tok/s continuously — comparable to a single A100 80 GB at a fraction of the cost and power.

**API surface:** Keep OpenAI-compatible REST throughout all tiers so the iPhone clients never change their transport layer. This is the key graduation invariant.

---

## 7. Key Gaps and Honest Caveats

**Concurrent multi-tenant on Apple Silicon is genuinely a weak spot.** No Apple Silicon runtime as of June 2026 has a paged-attention Metal implementation that is production-proven at scale. llama.cpp's paged scheduler (discussion #21961) is in prototype; vllm-mlx is research-grade (EuroMLSys '26 is a peer-reviewed venue but the codebase is months old). For NutriMe's family-of-4 scale this is not a blocking problem — the concurrency demand is too low to stress-test these limits. But for >10 concurrent users, Apple Silicon + any current runtime will hit KV fragmentation and bandwidth saturation.

**Ollama MLX backend is in preview.** "Preview" means not all model architectures are supported on the MLX path; unsupported models fall back to llama.cpp Metal automatically. Before committing to an MLX-format model at V1, verify it is in Ollama's supported MLX model list.

**Benchmark numbers in this report.** Most throughput figures above are from community benchmarks and first-party blog posts, not independent peer-reviewed replication. The vllm-mlx figures (arXiv 2601.19139) are the most citable. All other numbers should be treated as directionally correct, not precisely reproducible.

**vLLM upstream.** The official vLLM project does not support Apple Silicon. Both Metal plugins are community-maintained. This is a risk factor for long-term support — though Docker's official vllm-metal integration reduces that risk materially.

---

## 8. Primary Sources

- arXiv 2601.19139 — [Native LLM and MLLM Inference at Scale on Apple Silicon](https://arxiv.org/abs/2601.19139) (vllm-mlx paper, EuroMLSys '26)
- Apple Machine Learning Research — [Exploring LLMs with MLX and the Neural Accelerators in the M5 GPU](https://machinelearning.apple.com/research/exploring-llms-mlx-m5)
- Ollama Blog — [Ollama is now powered by MLX on Apple Silicon in preview](https://ollama.com/blog/mlx) (March 2026)
- Ollama Blog — [Ollama's highest performance on Apple Silicon yet with MLX](https://ollama.com/blog/mlx-performance)
- llama.cpp Discussion #21961 — [Paged KV cache and scheduler: Phase 1](https://github.com/ggml-org/llama.cpp/discussions/21961)
- llama.cpp Discussion #20572 — [Tutorial: Persistent KV cache per session with llama-server hooks](https://github.com/ggml-org/llama.cpp/discussions/20572)
- GitHub — [vllm-mlx (waybarrios)](https://github.com/waybarrios/vllm-mlx)
- GitHub — [vllm-metal (vllm-project)](https://github.com/vllm-project/vllm-metal)
- GitHub — [omlx (jundot)](https://github.com/jundot/omlx)
- Docker Blog — [Docker Model Runner Adds vLLM Support on macOS](https://www.docker.com/blog/docker-model-runner-vllm-metal-macos/)
- Hugging Face Blog — [MetalRT: The Fastest AI Inference Engine for Apple Silicon](https://huggingface.co/blog/runanywhere/metalrt-fastest-inference-apple-silicon)
- yage.ai — [MLX vs llama.cpp on Apple Silicon: Benchmarks, M5 Neural Accelerators, and Why Ollama Switched](https://yage.ai/share/mlx-apple-silicon-en-20260331.html)
- kaitchup.substack.com — [Choosing a GGUF Model: K-Quants, I-Quants, and Legacy Formats](https://kaitchup.substack.com/p/choosing-a-gguf-model-k-quants-i)
- MACGPU Blog — [2026 Apple Silicon Mac Local LLM Concurrency & Queuing](https://macgpu.com/en/blog/2026-0414-mac-local-llm-concurrency-queue-ollama-lmstudio-tail-latency-remote.html)
- codersera.com — [Your Mac as a Local-LLM Server: What You Can Actually Run in 2026](https://codersera.com/blog/mac-as-a-local-llm-server-2026/)
- medium.com/@michael.hannecke — [Sharing Ollama Across Your LAN with Auto-Wake: One Mac Studio, Whole Team](https://medium.com/@michael.hannecke/sharing-ollama-across-your-lan-with-auto-wake-one-mac-studio-whole-team-cbf09eab8f48)
- Apple Support — [Mac Studio power consumption and thermal output](https://support.apple.com/en-us/102027)
- arXiv 2511.05502 — [Production-Grade Local LLM Inference on Apple Silicon: A Comparative Study of MLX, MLC-LLM, Ollama, llama.cpp, and PyTorch MPS](https://arxiv.org/abs/2511.05502)
- Red Hat Developer — [llama.cpp vs. vLLM: Choosing the right local LLM inference engine](https://developers.redhat.com/articles/2026/06/15/llamacpp-vs-vllm-choosing-right-local-llm-inference-engine)
- GitHub — [mlc-ai/mlc-llm](https://github.com/mlc-ai/mlc-llm)
- GitHub — [janhq/jan](https://github.com/janhq/jan)
- LM Studio — [lmstudio.ai](https://lmstudio.ai/)
- markaicode.com — [llama.cpp Inference Architecture — Production System Design](https://markaicode.com/architecture/llamacpp-inference-architecture/)

---

*Researched: 2026-06-29. Framework versions, benchmark numbers, and plugin maturity should be re-verified before a V1 build decision.*
