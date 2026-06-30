# T2: OSS General-Purpose LLM Landscape Survey — June 2026

**Track:** 15-llm-revisit  
**Companion:** T1-food-llms.md (food/nutrition-specific capability evaluation)  
**Scope:** Existence, characteristics, licensing, and hardware feasibility. Capability benchmarks are covered by the sibling T1 track.  
**Deployment target:** Apple Silicon laptop (32 GB / 64 GB / 128 GB tiers), family-of-4 multi-tenant, low concurrent QPS, local-first.  
**Freshness:** Research conducted June 29, 2026. All release dates cited from primary sources.

---

## 1. Methodology and Source Notes

Primary sources: HuggingFace model cards, provider GitHub repos, official blog posts, and arXiv papers. Secondary sources used where primary was unavailable, flagged with [secondary]. License claims are sourced as close to the primary model card or official legal page as possible. Hardware footprint figures follow the community-standard rule of thumb: Q4 quantization requires approximately 0.5–0.6 GB per billion total parameters for MoE models (only weights in memory that are loaded, all experts) and 0.55–0.7 GB per billion for dense models, plus ~10–20% overhead for KV cache and runtime at typical context lengths.

---

## 2. Provider Entries

### 2.1 Chinese Providers

---

#### Z.ai / Zhipu AI — GLM Family

**Provider:** Z.ai (formerly Zhipu AI), China. IPO'd on the Hong Kong Stock Exchange January 8, 2026, becoming the first publicly listed Chinese AI lab. Historically co-developed with Tsinghua KEG lab.

**Latest flagship OSS model:** GLM-5.2  
**Release date:** June 16, 2026  
**HuggingFace / primary source:** https://huggingface.co/zai-org | https://www.zhipuai.cn/en | https://venturebeat.com/ai/z-ai-debuts-open-source-glm-4-6v-a-native-tool-calling-vision-model-for

**Available sizes (GLM family, as of June 2026):**
- GLM-4.5: 355B total / 32B active (MoE), released July 2025
- GLM-4.6: 355B total / 32B active (MoE) + GLM-4.6V multimodal vision variant, released September 2025
- GLM-5: 744B total / ~40B active (MoE), released February 2026; trained on Huawei Ascend/MindSpore
- GLM-5.2: 744B total / ~40B active (MoE), released June 16, 2026; 1M context window

**License:** MIT License since July 2025. GLM-5.2 model weights released under MIT with "no usage restrictions or regional locks" per official announcement. Note: earlier GLM-4 (June 2024) used a custom Zhipu license; the MIT pivot was a deliberate open-source positioning move. The MIT license has no geographic exclusions, no commercial thresholds, no naming requirements in derivatives.

**Architecture:** Mixture-of-Experts (MoE), dense transformer backbone.

**Context window:** GLM-5.2 — 1 million tokens; GLM-4.6 — 200K tokens / 128K output.

**Multilingual:** Strong Chinese + English; multilingual coverage broadly claimed but Chinese-optimized. Japanese, Korean confirmed in benchmarks; Hindi, Arabic, Spanish not prominently featured.

**Hardware footprint (GLM-5.2, 744B MoE):**
- bf16 raw: ~1,488 GB (not practical for local)
- Q4_K_M GGUF: ~445 GB (not practical for Apple Silicon)
- 2-bit dynamic GGUF (Unsloth UD-IQ2_M): ~239 GB — fits M3/M4 Ultra 256 GB unified memory at ~3–9 tok/s
- Practical minimum: 256 GB Apple Silicon (Mac Studio/Pro M4 Ultra)

**GLM-4.5 (355B MoE, 32B active) hardware:**
- Q4 GGUF: ~213 GB total weights loaded
- Practical: requires 256 GB machine; not feasible on 32/64/128 GB

**Tool use / function calling:** Native, confirmed across GLM-4.5+. GLM-4.6V ships "native tool-calling" as a headline feature. OpenAI-compatible format.

**Multimodal:** GLM-4.6V — vision. GLM-5.2 — text + vision. Audio not confirmed open-weight.

**Official quantizations:** GGUF mirrors from Unsloth and community; MLX not officially published but community ports exist.

**Supply chain note:** GLM-5 trained entirely on Huawei Ascend + MindSpore — independent of NVIDIA. This is a declared strategic choice. Weights are open; training infrastructure is China-internal.

---

#### DeepSeek — V3 / R1 / V3.2 Family

**Provider:** DeepSeek AI (深势科技 / High-Flyer Capital Management), China. Quantitative hedge fund origin; operates as an AI lab. No direct commercial product revenue — purely lab model.

**Latest flagship OSS model:** DeepSeek-V3.2 (December 1, 2025 stable) / DeepSeek-V3.2-Exp (September 29, 2025)  
**Primary sources:** https://github.com/deepseek-ai/DeepSeek-V3 | https://huggingface.co/deepseek-ai/DeepSeek-V3 | https://api-docs.deepseek.com/updates

**Available models (as of June 2026, all with open weights):**
- DeepSeek-V3 (original): 671B total / 37B active MoE, December 2024
- DeepSeek-R1: 671B total / 37B active MoE, reasoning-focused (RL-trained), January 2025
- DeepSeek-V3-0324: 671B total, March 24, 2025
- DeepSeek-R1-0528: May 28, 2025
- DeepSeek-V3.1: 671B total / 37B active MoE, August 21, 2025; hybrid thinking/non-thinking modes
- DeepSeek-V3.2-Exp: 671B / 37B active, September 29, 2025; 128K context; integrates thinking into tool-use
- DeepSeek-V3.2: December 1, 2025; 163.8K context window; first model integrating thinking directly into tool-use
- R1 distills: Dense models at 1.5B, 7B, 8B, 14B, 32B, 70B — based on Qwen2.5 and Llama-3 backbones

**License:** MIT License for all V3, R1, V3.1, V3.2 weights and code. Commercial use permitted. No geographic restrictions in the license text. (Note: data sovereignty concerns apply to DeepSeek's *API* — not to locally-hosted weights. See §4 for supply chain discussion.)

**Architecture:** MoE with Multi-head Latent Attention (MLA) + DeepSeek Sparse Attention (DSA) in V3.2. DeepSeek-V3.2 is notable for combining thinking and tool-use in the same inference path.

**Context window:** V3.2 — 163.8K tokens (max output 163K). V3.2-Exp — 128K tokens.

**Multilingual:** English + Chinese primary. Multilingual broadly claimed but Chinese/English optimized.

**Hardware footprint (671B MoE, V3.2):**
- bf16 raw: ~1,342 GB
- Q4_K_M GGUF: ~402 GB
- Practical minimum for local: 128 GB Apple Silicon at extremely aggressive quantization (IQ2_XS ~178 GB); comfortable deployment requires 256 GB+
- R1-distill-32B (dense): Q4_K_M ~19 GB — fits 32 GB Mac comfortably

**Tool use / function calling:** Native in V3.2; supports tool calls in both thinking and non-thinking modes. OpenAI-compatible API format.

**Multimodal:** Text only for V3/R1/V3.2. No vision in the main open-weight line.

**Official quantizations:** Community GGUF via Unsloth, bartowski; MLX quantizations available. No official GGUF from DeepSeek itself.

**Privacy/regulatory note (critical — see §4):** DeepSeek's API stores data in China and is subject to Chinese law. This does NOT apply to locally-deployed weights, which function identically to any other MIT-licensed model. The supply-chain concern is weights provenance (Chinese lab, RL alignment with possible censorship baked in), not data transmission.

---

#### Qwen (Alibaba Cloud / Alibaba Group)

**Provider:** Alibaba Cloud / Alibaba Group, China. Largest Chinese e-commerce/cloud company. Qwen models are produced by the Qwen team within DAMO Academy. Proprietary and open-weight lines coexist.

**Latest flagship OSS model:** Qwen3.6-27B (dense, April 2026) / Qwen3.5 (MoE, February 2026)  
**Primary sources:** https://github.com/QwenLM/Qwen3 | https://github.com/QwenLM/Qwen3.6 | https://qwenlm.github.io/blog/qwen3/ | https://www.marktechpost.com/2026/04/22/alibaba-qwen-team-releases-qwen3-6-27b

**Available models / sizes:**

*Qwen3 (April 28, 2025) — Apache 2.0:*
- Dense: 0.6B, 1.7B, 4B, 8B, 14B, 32B
- MoE: 30B-A3B (30B total / 3B active), 235B-A22B (235B total / 22B active)
- Context: 32K for 0.6B–1.7B; 128K for all others
- Trained on 36 trillion tokens, 119 languages

*Qwen3.5 (February 16–17, 2026) — open-weights, license not yet confirmed Apache 2.0 [secondary]:*
- MoE: 397B total / 17B active; 256 experts (8 routed + 1 shared)
- 262K context window

*Qwen3.6 (April 2026) — Apache 2.0:*
- Qwen3.6-35B-A3B: MoE (36B total / 3B active); agent-workflow focus
- Qwen3.6-27B: dense; first dense model in Qwen3.6 line; outperforms 397B MoE on agentic coding

**License (Qwen3 + Qwen3.6):** Apache 2.0 — clean, permissive, no geographic restrictions, no naming requirements, no commercial thresholds. Qwen3.5 may use "Qwen License" (a custom source-available license) — confirm on model card before deployment. Earlier Qwen 2.5 used Apache 2.0 uniformly.

**Architecture:** Dense and MoE both available; Qwen3.6-27B is pure dense transformer. Qwen3 introduces dual-mode thinking (hybrid reasoning + normal response in one model).

**Context window:** Qwen3: 128K (most models); Qwen3.5: 262K; Qwen3.6-27B: 128K.

**Multilingual:** 119 languages confirmed (Qwen3). English, Chinese, Japanese, Spanish, French, Hindi, Arabic all confirmed [secondary from training claims].

**Hardware footprint:**
- Qwen3-32B (dense): Q4_K_M ~19 GB — fits 32 GB Mac with room to spare
- Qwen3-14B: Q4_K_M ~8.5 GB — fits 16 GB Mac
- Qwen3-8B: Q4_K_M ~5 GB — fits any modern Mac
- Qwen3-235B-A22B (MoE): Q4 ~132 GB — requires 128 GB Apple Silicon, tight; 64 GB insufficient
- Qwen3.5 (397B MoE / 17B active): Q4 ~240 GB — requires 256 GB machine
- Qwen3.6-27B (dense): Q4_K_M ~16 GB — fits 32 GB Mac comfortably
- Qwen3.6-35B-A3B (MoE): Q4 ~21 GB total weights — fits 32 GB Mac

**Tool use / function calling:** Native across all Qwen3 family. MCP support explicitly strengthened. OpenAI-compatible format. JSON structured output.

**Multimodal:** Qwen-VL line (Qwen2.5-VL, Qwen3-VL) handles vision. Qwen3.7-Plus described as "multimodal agent" (proprietary). Open-weight vision models confirmed in Qwen2.5-VL-72B; Qwen3-VL availability should be confirmed on HuggingFace.

**Official quantizations:** MLX quantizations published by mlx-community; GGUF from bartowski and Unsloth; AWQ from TheBloke/community. Official team publishes fp16 safetensors.

---

#### Kimi / Moonshot AI

**Provider:** Moonshot AI (月之暗面), China. VC-backed startup founded 2023 by Yang Zhilin (formerly CMU/Google Brain).

**Latest flagship OSS model:** Kimi K2.6  
**Release date:** April 20, 2026  
**Primary sources:** https://huggingface.co/moonshotai/Kimi-K2.6 | https://moonshotai.github.io/Kimi-K2/ | https://miraflow.ai/blog/kimi-k2-6-explained-moonshot-ai-open-source-model-ties-gpt-5-5-coding

**Available sizes:**
- Kimi K2.6: 1 trillion total parameters / 32B active (MoE)
- Ships natively in INT4 quantization; 262,144-token context window
- Native multimodal: text + images + video in one architecture

**License:** Modified MIT. Standard MIT with one threshold: if you deploy K2.6 (or a derivative) commercially and exceed 100M monthly active users OR $20M USD monthly revenue, you must prominently display "Kimi K2" in the product UI. Below those thresholds: standard MIT. No geographic restrictions.

**Architecture:** MoE, 1T total / 32B active per token. Native multimodal (no separate vision encoder described). Agent Swarm system built-in (up to 300 sub-agents, 4,000 steps per run).

**Context window:** 262,144 tokens (256K).

**Multilingual:** Chinese + English primary; broader multilingual not prominently benchmarked [secondary].

**Hardware footprint (1T MoE, 32B active):**
- bf16: not practical
- INT4 native: ~625 GB total weights (1T × ~0.625 GB/B at 4-bit) — requires multi-machine or ultra-high-memory single machine
- Practical minimum: Mac Studio M4 Ultra 192–512 GB or multi-GPU server
- Not feasible at 32 GB / 64 GB / 128 GB Apple Silicon

**Tool use / function calling:** Native agentic design; tool-use is core capability.

**Multimodal:** Yes — text, images, video in one architecture. K2.6 is multimodal natively.

**Official quantizations:** Described as shipping "natively in INT4." Community GGUF expected. [secondary]

---

#### 01.AI — Yi Family

**Provider:** 01.AI (零一万物), China. Founded 2023 by Kai-Fu Lee (formerly Google China, Microsoft).

**Latest flagship OSS model:** Yi-1.5 (May 2024); Yi-Coder (September 2024). No major new release found in 2025–2026 research.  
**Primary sources:** https://github.com/01-ai/Yi-1.5 | https://github.com/01-ai/Yi-Coder | https://huggingface.co/01-ai

**Available sizes:**
- Yi-1.5: 6B, 9B, 34B (dense)
- Yi-Coder: 1.5B, 9B (code-focused, 128K context, 52 programming languages)

**License:** Apache 2.0 for both Yi-1.5 and Yi-Coder.

**Architecture:** Dense transformer (Llama-style).

**Context window:** Yi-Coder — 128K. Yi-1.5 — 4K–200K depending on variant.

**Multilingual:** English + Chinese primary. Limited multilingual breadth vs. Qwen3.

**Hardware footprint:**
- Yi-1.5-34B: Q4_K_M ~20 GB — fits 32 GB Mac
- Yi-1.5-9B: Q4_K_M ~5.5 GB — fits any modern Mac

**Tool use / function calling:** Not a headline feature; basic support.

**Multimodal:** Yi-VL (vision-language) exists but not prominently updated in 2025–2026. Treat as text-primary.

**Status note:** 01.AI appears to have slowed public releases in 2025–2026 relative to the pace of Qwen and DeepSeek. Yi-1.5 remains solid for its size but is not frontier-class as of mid-2026.

---

#### MiniCPM (OpenBMB / Tsinghua KEG)

**Provider:** OpenBMB (Open Lab for Big Model Bases), affiliated with Tsinghua University, China. Academic/research provenance.

**Latest flagship OSS model:** MiniCPM5-1B (May 2026) / MiniCPM-V 4.6 (May 11, 2026) / MiniCPM-V 4.5 (August 2025)  
**Primary sources:** https://github.com/openbmb/minicpm | https://huggingface.co/openbmb/MiniCPM-V-4.6 | https://github.com/OpenBMB/MiniCPM-V

**Available sizes:**
- MiniCPM5-1B: 1.08B parameters, 131K context; on-device SLM
- MiniCPM-V 4.6: 1.3B total multimodal, May 2026; image/video/multi-image; runs on phones
- MiniCPM-V 4.5: 8B total (Qwen3-8B + SigLIP2-400M); August 2025
- MiniCPM-o 2.6: 8B (Qwen2.5-7B backbone); January 2025; omni (speech + vision)

**License:** Apache 2.0 for all MiniCPM models.

**Architecture:** Dense; hybrid sparse/linear attention variants in MiniCPM-SALA. Builds on Qwen backbones for recent VL versions.

**Context window:** MiniCPM5-1B — 131K; MiniCPM-V 4.5 — 128K.

**Multilingual:** Chinese + English primary; limited broader multilingual.

**Hardware footprint:**
- MiniCPM5-1B: Q4 <1 GB — runs on any hardware including mobile
- MiniCPM-V 4.5 (8B): Q4_K_M ~5 GB — fits 8 GB Mac mini

**Tool use / function calling:** Supported from MiniCPM-V 4.5 onward.

**Multimodal:** Yes — MiniCPM-V line is VL (vision-language). MiniCPM-o includes speech.

**Relevance for NutriMe:** Excellent on-device SLM option; MiniCPM-V 4.5 fits 8 GB RAM with vision capability. Not frontier-class but very capable for edge.

---

#### InternLM (Shanghai AI Laboratory)

**Provider:** Shanghai AI Laboratory (上海人工智能实验室), China. State-affiliated research institute, government-backed.

**Latest flagship OSS model:** InternLM3-8B-Instruct (January 15, 2025)  
**Primary sources:** https://github.com/InternLM/InternLM | https://internlm.readthedocs.io/en/latest/model_card/InternLM3.html

**Available sizes:**
- InternLM3-8B-Instruct: 8B dense, 4T training tokens
- InternLM2.5: 1.8B, 7B, 20B; 1M context; released July–August 2024

**License:** Apache 2.0.

**Architecture:** Dense transformer (Llama-compatible architecture).

**Context window:** InternLM2.5 — 1M tokens (claimed). InternLM3-8B — not confirmed long-context in search results.

**Multilingual:** Chinese + English primary.

**Hardware footprint:**
- InternLM3-8B: Q4_K_M ~5 GB — fits any modern Mac
- InternLM2.5-20B: Q4_K_M ~12 GB — fits 16 GB Mac

**Tool use / function calling:** Basic. Not a headline feature.

**Multimodal:** InternLM-XComposer2.5-OmniLive (video/audio streaming) exists but is specialty.

**Status note:** InternLM3 is a modest release (8B only) as of Jan 2025; no major 2025–2026 flagship spotted. State-affiliated provenance may be a concern for some deployments.

---

#### Hunyuan (Tencent)

**Provider:** Tencent AI Lab (腾讯 AI 实验室), China. One of the largest Chinese tech conglomerates.

**Latest flagship OSS model:** Hunyuan A13B Instruct (January 2026, 200K context) / Hunyuan-Large (MoE-A52B)  
**Primary sources:** https://www.llmreference.com/model-family/hunyuan | https://github.com/Tencent-Hunyuan

**Available sizes:**
- Hunyuan-Large (Hunyuan-MoE-A52B): 389B total / 52B active (MoE)
- Hunyuan T1: 52B, 256K context, reasoning, June 2025
- Hunyuan 2.0 Think: 13B, 131K context, November 2025
- Hunyuan A13B Instruct: 200K context, January 2026
- Hunyuan Image 3.0: 80B total / 13B active MoE (image generation, not chat LLM), September 2025

**License:** Tencent Hunyuan Community License. NOTABLE RESTRICTION: License applies worldwide EXCLUDING the territories of the European Union, United Kingdom, and South Korea. Additionally prohibits using model outputs to improve other AI models (except the Hunyuan series itself). This is a non-standard restriction.

**Architecture:** MoE (Hunyuan-Large); dense (Hunyuan 2.0 Think / A13B).

**Context window:** Hunyuan T1 — 256K; A13B — 200K; 2.0 Think — 131K.

**Multilingual:** Chinese + English primary.

**Hardware footprint:**
- Hunyuan 2.0 Think / A13B (13B dense): Q4_K_M ~8 GB — fits 16 GB Mac
- Hunyuan-Large (389B MoE): not practical for single-machine Apple Silicon

**Tool use / function calling:** Supported in A13B Instruct and Hunyuan T1.

**Multimodal:** Image generation models are open; chat LLM line is text-primary.

**License flag:** The EU/UK/South Korea exclusion makes this YELLOW/RED depending on jurisdiction. For a US-based personal project this technically works, but the "no output to train other models" clause is problematic for fine-tuning workflows.

---

#### Baichuan AI

**Provider:** Baichuan AI (百川智能), China. Founded 2023 by Wang Xiaochuan (ex-Sogou CEO).

**Latest flaghsip OSS model:** Baichuan-2-33B (late 2023); Baichuan-4 proprietary API (2024–2025). No prominent new open-weight flagship found in 2025–2026 research.

**License:** Apache 2.0 for Baichuan-1/2 open weights.

**Status:** Baichuan appears to have pivoted toward enterprise proprietary API. Limited new open-weight activity in 2025–2026. Not recommended as primary OSS candidate.

---

#### Doubao / ByteDance

**Status:** Doubao (ByteDance's consumer chatbot) is closed-weight. Doubao-1.5-Pro (January 2025) is not open-weight. ByteDance has not released open-weight chat LLMs as of June 2026 research. Exclude from consideration.

---

#### Skywork / StepFun

**Skywork AI:** Produces Skywork-R1V (multimodal reasoning) and base models. Limited OSS footprint; niche positioning.

**StepFun:** No confirmed open-weight releases as of June 2026 research. Primarily closed API.

---

### 2.2 Western Providers

---

#### Meta — Llama 4

**Provider:** Meta AI, USA. World's largest social media company; treats open-weight models as strategic infrastructure.

**Latest flagship OSS model:** Llama 4 Scout / Llama 4 Maverick (April 5, 2025). Llama 4 Behemoth (~2T total) announced but not yet released as open weights as of June 2026.  
**Primary sources:** https://ai.meta.com/blog/llama-4-multimodal-intelligence/ | https://www.llama.com/models/llama-4/ | https://www.llama.com/llama4/license/

**Available sizes:**
- Llama 4 Scout: 109B total / 17B active (MoE, 16 experts); 10M context window
- Llama 4 Maverick: 400B total / 17B active (MoE, 128 experts); 1M context window
- Llama 3.3 70B (dense): still actively used; excellent local-inference candidate
- Llama 3.2 line: 1B, 3B, 11B, 90B (vision variants)

**License:** Llama 4 Community License Agreement. KEY TERMS:
- Commercial use permitted up to 700M monthly active users; above that, must contact Meta for separate license
- CRITICAL: Vision/multimodal capabilities are EXCLUDED for entities domiciled in or with principal place of business in the EU. End users of EU products are not restricted — only the deployer
- Not OSI-certified open source
- Attribution required; must retain "Built with Meta Llama 4" or similar in documentation

**Architecture:** MoE for Scout and Maverick; native multimodal from the base.

**Context window:** Scout — 10M tokens (world-leading open-weight). Maverick — 1M tokens.

**Multilingual:** 12 languages confirmed (text + image).

**Hardware footprint:**
- Llama 4 Scout (109B MoE, 17B active): Q4_K_M GGUF ~61 GB — requires 64 GB Apple Silicon; tight but feasible
- Llama 4 Maverick (400B MoE): Q4 ~224 GB — requires 256 GB machine; not for 32/64/128 GB
- Llama 3.3 70B (dense): Q4_K_M ~42 GB — fits 64 GB comfortably, tight on 48 GB
- Llama 3.2 3B: Q4 ~2 GB — runs anywhere

**Tool use / function calling:** Native; JSON function-calling format. Well-supported in Ollama/llama.cpp.

**Multimodal:** Scout and Maverick are natively multimodal (text + image). 10M context Scout is vision-capable.

**Official quantizations:** GGUF from bartowski and unsloth; MLX ports from mlx-community; AWQ available. Rich ecosystem.

---

#### Mistral AI

**Provider:** Mistral AI, France. VC-backed European AI lab (Lightspeed, a16z, Google investment). Founded 2023 by Anthropic/DeepMind alumni.

**Latest flagship OSS model:** Mistral Large 3 (December 2025) / Mistral Small 4 (2025–2026)  
**Primary sources:** https://mistral.ai/news/mistral-3/ | https://huggingface.co/mistralai/Mistral-Large-3-675B-Instruct-2512 | https://docs.mistral.ai/models/mistral-large-3-25-12

**Available models:**
- Mistral Large 3: 675B total / 41B active (MoE); released December 2025; Apache 2.0
- Mistral Small 4: 119B total / 6B active (MoE); multimodal (text + image); Apache 2.0
- Ministral 3B / 8B / 14B: dense models; December 2025; Apache 2.0
- Codestral 2: code-specialized; license varies (check model card for commercial terms)
- Mistral Nemo 12B: older; Apache 2.0; still widely used

**License:** Apache 2.0 for Mistral Large 3, Mistral Small 4, Ministral family. Voxtral TTS: CC BY-NC 4.0 (non-commercial only). Codestral: check current terms (historically Mistral-specific non-commercial for Codestral).

**Architecture:** MoE for Large 3 and Small 4; dense for Ministral family.

**Context window:** Mistral Large 3 — 256K. Mistral Small 4 — not confirmed [secondary]. Ministral 14B — standard (32K–128K).

**Multilingual:** Mistral models strongly multilingual; European languages confirmed (FR, ES, DE, IT, PT); Japanese, Arabic, Hindi coverage implied but not headline-benchmarked.

**Hardware footprint:**
- Mistral Large 3 (675B MoE, 41B active): Q4_K_M ~403 GB — NOT feasible for Apple Silicon at any current tier; requires multi-GPU server
- Mistral Small 4 (119B MoE, 6B active): Q4 ~60–80 GB — requires 64 GB+ Apple Silicon; tight
- Ministral 14B (dense): Q4_K_M ~8.5 GB — fits 16 GB Mac
- Ministral 8B (dense): Q4_K_M ~5 GB — fits any modern Mac
- Mistral Nemo 12B: Q4 ~7 GB — fits 16 GB Mac

**Tool use / function calling:** Native; strong agentic support in Mistral Small 4 and Large 3. OpenAI-compatible format with Mistral-specific function syntax.

**Multimodal:** Mistral Small 4 — vision (text + image). Audio via Voxtral (non-commercial).

**Official quantizations:** GGUF via community (bartowski); official GGUF mirrors; NVFP4 variant of Large 3 published by Mistral for NVIDIA infrastructure. MLX available via community.

---

#### Microsoft — Phi-4 Family

**Provider:** Microsoft Research, USA. Emphasis on "small language model" (SLM) efficiency; Phi family is a deliberate counter-narrative to scale.

**Latest flagship OSS model:** Phi-4-Reasoning-Vision-15B (March 4, 2026) / Phi-4-Reasoning / Phi-4-Reasoning-Plus  
**Primary sources:** https://huggingface.co/microsoft/phi-4 | https://www.microsoft.com/en-us/research/publication/phi-4-reasoning-technical-report/ | https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-phi-4-reasoning-vision-to-microsoft-foundry/4499154

**Available sizes:**
- Phi-4: 14B dense; January 2025; 16K context
- Phi-4-Mini: sub-14B; enhanced multilingual + function calling
- Phi-4-Multimodal: vision + audio + text; fully multimodal
- Phi-4-Reasoning: 14B; complex reasoning focus
- Phi-4-Reasoning-Plus: 14B; extended reasoning
- Phi-4-Reasoning-Vision-15B: 15B; vision + reasoning; March 4, 2026; 16,384 context

**License:** MIT License for all Phi-4 variants.

**Architecture:** Dense transformer; small-model efficiency focus. Not MoE.

**Context window:** 16K for Phi-4 and Phi-4-Reasoning-Vision-15B. (Short relative to frontier — a known limitation.)

**Multilingual:** Phi-4-Mini explicitly enhanced multilingual support. Phi-4 baseline: English primary with some multilingual.

**Hardware footprint:**
- Phi-4 / Phi-4-Reasoning (14B dense): Q4_K_M ~9 GB — fits 16 GB Mac with headroom; excellent 32 GB candidate
- Phi-4-Reasoning-Vision-15B: Q4_K_M ~9.5 GB — fits 16 GB Mac
- Phi-4-Multimodal: similar footprint to 14B

**Tool use / function calling:** Phi-4-Mini added function calling explicitly. Phi-4-Multimodal supports structured output.

**Multimodal:** Phi-4-Multimodal — vision + audio + text. Phi-4-Reasoning-Vision — vision + reasoning. Strong multimodal story for a sub-16B model.

**Official quantizations:** GGUF from community (bartowski); on NGC for NVIDIA NeMo. MLX community-ported.

**Insight:** Phi-4 is the strongest argument for "small is enough" — 14B MIT-licensed, fits 16 GB RAM, strong reasoning. The 16K context limit is a real constraint for long meal-plan documents.

---

#### Google — Gemma Family

**Provider:** Google DeepMind, USA. Gemma is the open-weight line; Gemini is the closed proprietary line.

**Latest flagship OSS model:** Gemma 4 (April 2, 2026), all variants  
**Primary sources:** https://ai.google.dev/gemma/docs/releases | https://ai.google.dev/gemma/docs/core | https://www.mindstudio.ai/blog/what-is-gemma-4-google-apache-open-weight-model

**Available sizes:**
- Gemma 3 (March 12, 2025): 1B, 4B, 12B, 27B dense; 128K context; 140+ languages; Gemma Terms of Use (not Apache 2.0)
- Gemma 4 (April 2, 2026): E2B, E4B (effective 2B/4B MoE), 26B MoE, 31B Dense; 128K context (31B: 32K); Apache 2.0
- Gemma 4 native audio on E2B and E4B
- Gemma 4 multimodal (images + video) across all variants

**License:**
- Gemma 3: Custom "Gemma Terms of Use" — has content restrictions and prohibited-use clauses beyond standard OSI. Yellow.
- Gemma 4: Apache 2.0 — clean, no custom restrictions. Significant upgrade. Green.

**Architecture:** Dense transformer (Gemma 3); mixed dense and MoE (Gemma 4 E2B/E4B are MoE; 26B is MoE; 31B is dense). SigLIP vision encoder for multimodal.

**Context window:** 128K for all Gemma 4 except Gemma 4 31B Dense (32K).

**Multilingual:** 140+ languages (Gemma 3). Gemma 4 claimed similar or better.

**Hardware footprint:**
- Gemma 4 12B: Q4 ~7.3 GB (fits 8 GB Mac)
- Gemma 4 31B Dense: Q4_K_M ~19 GB (fits 32 GB Mac comfortably)
- Gemma 4 26B MoE: Q4 ~16 GB (fits 32 GB Mac comfortably; MoE efficiency)
- Gemma 3 27B: Q4_K_M ~16 GB (fits 32 GB Mac)
- Gemma 3 12B: Q4 ~6.7 GB (fits 8 GB Mac)

**Tool use / function calling:** Supported. Gemma 4 has agentic improvements.

**Multimodal:** All Gemma 4 variants handle images + video. E2B and E4B add native audio input. This is the most multimodally complete small-model family at Apache 2.0.

**Official quantizations:** GGUF from community; MLX from mlx-community (note: Gemma 4 MLX support had teething issues in April 2026 — should be mature by June 2026); official safetensors from Google on Kaggle/HuggingFace.

---

#### Cohere — Command Family

**Provider:** Cohere, Canada. Enterprise NLP company; RAG and enterprise AI focus. CohereLabs is the research/open-weight arm.

**Latest flagship OSS model:** Command A+ (May 20, 2026)  
**Primary sources:** https://cohere.com/blog/command-a-plus | https://huggingface.co/CohereLabs/command-a-plus-05-2026 | https://www.businesswire.com/news/home/20260520121796/en/Cohere-Releases-Command-A-An-Open-Source-Enterprise-AI-Model-Built-for-Sovereign-Critical-Infrastructure

**Available sizes:**
- Command A+: 218B total / 25B active (sparse MoE); May 2026; Apache 2.0
- Command R+: 104B dense; CC-BY-NC (non-commercial only) — NOT commercially licensed
- Command R: 35B dense; CC-BY-NC — NOT commercially licensed

**License:**
- Command A+: Apache 2.0 — clean, commercially permissive. First Cohere model under Apache 2.0.
- Command R / R+: CC-BY-NC — non-commercial research only. Cannot be used in a commercial product or service.

**Architecture:** Sparse MoE (Command A+); dense transformer (Command R/R+).

**Context window:** Command A+ — 128K input / 64K output. Command R+ — 128K.

**Multilingual:** Command R+ tested in 10 languages (EN, FR, ES, IT, DE, PT-BR, JA, KO, AR, ZH). Command A+ — 48 languages including all official EU languages.

**Hardware footprint:**
- Command A+ (218B MoE / 25B active): Q4 ~130 GB — requires 128 GB Apple Silicon; tight
- BF16 requires 8×H100; W4A4 4-bit minimum 2×H100 (designed for data center). Apple Silicon feasibility at 128 GB is marginal.
- Command R+ (104B dense): Q4_K_M ~62 GB — fits 64 GB Mac; but NC license limits use

**Tool use / function calling:** Native RAG and tool-use; Command A+ has native citation support.

**Multimodal:** Command A+ supports vision inputs. Command R/R+ text only.

**Insight:** Command A+ is the first Cohere model that is legally clean for commercial self-hosting, but the hardware bar (128 GB+ for practical use) is steep.

---

#### Allen Institute for AI (Ai2) — OLMo Family

**Provider:** Allen Institute for AI (Ai2), USA. Non-profit research institute. OLMo is the "truly open" LLM project — weights, data, training code, and evals all released.

**Latest flagship OSS model:** OLMo 2 32B / OLMo 3 (announced November 2025)  
**Primary sources:** https://allenai.org/olmo2 | https://allenai.org/blog/olmo2 | https://huggingface.co/collections/allenai/olmo-2

**Available sizes:**
- OLMo 2: 1B, 7B, 13B, 32B (dense); Apache 2.0; trained up to 6T tokens
- OLMo 3: announced November 2025; frontier-competing; details limited in search results

**License:** Apache 2.0 for weights. ODC-BY for Dolma 2 training data. Fully open including training data.

**Architecture:** Dense decoder-only transformer (modified Llama-style with RMSNorm, SwiGLU, RoPE).

**Context window:** OLMo 2: 4K native (8K with RoPE scaling). This is a significant limitation.

**Multilingual:** Primarily English; Dolma dataset is English-dominant.

**Hardware footprint:**
- OLMo 2 32B: Q4_K_M ~19 GB — fits 32 GB Mac
- OLMo 2 13B: Q4_K_M ~8 GB — fits 16 GB Mac
- OLMo 2 7B: Q4_K_M ~4.5 GB — fits any modern Mac

**Tool use / function calling:** Not a headline feature; ChatML-compatible template.

**Multimodal:** Text only.

**Insight:** OLMo is the gold standard for "truly open" (weights + data + code + evals). Excellent for research and reproducibility. The 4K–8K context and English-primary training make it less suited for production use vs. Qwen3 or Gemma 4 at similar sizes.

---

#### Databricks DBRX / Snowflake Arctic

**Status:** DBRX (132B MoE, March 2024, Apache 2.0) remains available but has not had a major update. Community usage has shifted toward Llama 4 and Qwen3. Snowflake Arctic (480B MoE, April 2024, Apache 2.0) similarly quiescent. Both are enterprise-origin models that were released once as demonstration pieces. Not recommended as primary candidates in June 2026.

---

## 3. Synthesis Tables

### 3.1 License-Clean Table

| Provider / Model | License | Status | Notes |
|---|---|---|---|
| Qwen3 (all sizes) | Apache 2.0 | GREEN | Clean permissive, no restrictions |
| Qwen3.6-27B / 35B | Apache 2.0 | GREEN | Clean permissive |
| DeepSeek V3 / R1 / V3.2 | MIT | GREEN | Clean permissive; supply chain concern separate from license |
| Mistral Large 3 | Apache 2.0 | GREEN | Clean permissive |
| Mistral Small 4 | Apache 2.0 | GREEN | Clean permissive |
| Ministral 3B/8B/14B | Apache 2.0 | GREEN | Clean permissive |
| Gemma 4 (all variants) | Apache 2.0 | GREEN | Full Apache 2.0 pivot from Google |
| Phi-4 (all variants) | MIT | GREEN | Clean permissive |
| OLMo 2 | Apache 2.0 | GREEN | Fully open incl. data |
| Command A+ | Apache 2.0 | GREEN | First commercial-clean Cohere model |
| GLM-4.5 / 5.2 (Z.ai) | MIT | GREEN | No restrictions noted; weights-only concern is supply chain |
| Kimi K2.6 | Modified MIT | YELLOW | Standard MIT below 100M MAU / $20M/mo threshold; attribution required above |
| Yi-1.5 / Yi-Coder | Apache 2.0 | GREEN | Clean permissive; no recent flagship |
| MiniCPM family | Apache 2.0 | GREEN | Clean permissive |
| InternLM3 | Apache 2.0 | GREEN | State-affiliated provenance; license clean |
| Llama 4 Scout/Maverick | Meta Community License | YELLOW | Not OSI; EU vision restriction for deployers; 700M MAU cap |
| Llama 3.3 70B | Meta Community License | YELLOW | Same community license terms; widely used |
| Gemma 3 | Gemma Terms of Use | YELLOW | Custom restrictions; not pure Apache |
| DBRX / Arctic | Apache 2.0 | GREEN | Stale; not recommended |
| Command R / R+ | CC-BY-NC | RED | Non-commercial only |
| Hunyuan (Tencent) | Hunyuan Community License | RED | Excludes EU/UK/South Korea; no model-output-to-train-others |
| Doubao (ByteDance) | Closed | RED | No open weights |
| StepFun | Closed/unconfirmed | RED | No confirmed OSS weights |

---

### 3.2 Hardware-Feasibility Table

Target: Apple Silicon laptop. Unified memory = GPU memory. MLX is ~1.5–2× faster than llama.cpp GGUF on Apple Silicon where supported. Q4_K_M is the practical quality/footprint sweet spot.

| Model | Total Params | Active Params | Q4_K_M GB | 32 GB | 64 GB | 128 GB | Notes |
|---|---|---|---|---|---|---|---|
| **SMALL — fit anywhere** | | | | | | | |
| MiniCPM5-1B | 1B dense | 1B | <1 GB | YES | YES | YES | On-device SLM |
| Phi-4-Mini | ~3–4B | — | ~2.5 GB | YES | YES | YES | |
| Qwen3-0.6B | 0.6B | — | 0.5 GB | YES | YES | YES | 32K context |
| Qwen3-4B | 4B | — | ~2.5 GB | YES | YES | YES | 128K context |
| MiniCPM-V 4.6 | 1.3B | — | ~1 GB | YES | YES | YES | Vision |
| Gemma 4 E4B | ~4B eff | — | ~3 GB | YES | YES | YES | Vision + audio |
| **MEDIUM — 16–32 GB tier** | | | | | | | |
| Qwen3-8B | 8B dense | — | ~5 GB | YES | YES | YES | 128K |
| Qwen3-14B | 14B dense | — | ~8.5 GB | YES | YES | YES | 128K |
| Phi-4 / Phi-4-Reasoning | 14B dense | — | ~9 GB | YES | YES | YES | MIT; 16K ctx |
| Phi-4-Reasoning-Vision-15B | 15B dense | — | ~9.5 GB | YES | YES | YES | MIT; vision |
| Gemma 4 12B | 12B dense | — | ~7.3 GB | YES | YES | YES | Vision |
| InternLM3-8B | 8B dense | — | ~5 GB | YES | YES | YES | |
| Ministral 8B | 8B dense | — | ~5 GB | YES | YES | YES | |
| Ministral 14B | 14B dense | — | ~8.5 GB | YES | YES | YES | |
| MiniCPM-V 4.5 | 8B | — | ~5 GB | YES | YES | YES | Vision |
| Yi-1.5-9B | 9B dense | — | ~5.5 GB | YES | YES | YES | |
| Mistral Nemo 12B | 12B dense | — | ~7 GB | YES | YES | YES | |
| OLMo 2 7B | 7B dense | — | ~4.5 GB | YES | YES | YES | 8K ctx limit |
| **LARGE — 32–64 GB tier** | | | | | | | |
| Qwen3-32B | 32B dense | — | ~19 GB | YES | YES | YES | 128K; flagship |
| Qwen3.6-27B | 27B dense | — | ~16 GB | YES | YES | YES | 128K; agentic |
| Qwen3-30B-A3B | 30B MoE | 3B | ~18 GB | YES | YES | YES | MoE efficiency |
| Qwen3.6-35B-A3B | 36B MoE | 3B | ~21 GB | YES | YES | YES | |
| Gemma 4 26B MoE | 26B MoE | — | ~16 GB | YES | YES | YES | Vision |
| Gemma 4 31B Dense | 31B dense | — | ~19 GB | YES | YES | YES | 32K ctx limit |
| Yi-1.5-34B | 34B dense | — | ~20 GB | YES | YES | YES | |
| OLMo 2 32B | 32B dense | — | ~19 GB | YES | YES | YES | 8K ctx limit |
| DeepSeek R1-distill-32B | 32B dense | — | ~19 GB | YES | YES | YES | 128K; reasoning |
| **X-LARGE — 64 GB tier** | | | | | | | |
| Llama 3.3 70B | 70B dense | — | ~42 GB | MARGINAL | YES | YES | 128K; well-supported |
| Llama 4 Scout | 109B MoE | 17B | ~61 GB | NO | YES | YES | 10M ctx; vision |
| Mistral Small 4 | 119B MoE | 6B | ~60–80 GB | NO | MARGINAL | YES | Vision; Apache |
| Command R+ (CC-BY-NC) | 104B dense | — | ~62 GB | NO | MARGINAL | YES | NC license |
| **XX-LARGE — 128 GB tier** | | | | | | | |
| Qwen3-235B-A22B | 235B MoE | 22B | ~132 GB | NO | NO | YES (tight) | 128K; flagship |
| Command A+ | 218B MoE | 25B | ~130 GB | NO | NO | YES (tight) | 128K; Apache |
| GLM-4.5 / 4.6 | 355B MoE | 32B | ~213 GB | NO | NO | NO | Requires 256 GB |
| Kimi K2.6 | 1T MoE | 32B | ~625 GB | NO | NO | NO | Requires 512+ GB |
| DeepSeek V3.2 | 671B MoE | 37B | ~402 GB | NO | NO | NO | Requires 512+ GB |
| Mistral Large 3 | 675B MoE | 41B | ~403 GB | NO | NO | NO | Requires server |
| GLM-5 / 5.2 | 744B MoE | ~40B | ~445 GB | NO | NO | NO | Requires 512+ GB |

**Key findings for NutriMe's Apple Silicon target:**

- **32 GB sweet spot:** Qwen3-32B, Qwen3.6-27B, Gemma 4 31B, Phi-4 family — all fit comfortably, all Apache 2.0 or MIT, all capable for nutrition tasks.
- **64 GB unlocks:** Llama 4 Scout (10M context — extraordinary for long meal plans), Llama 3.3 70B, Mistral Small 4.
- **128 GB unlocks:** Qwen3-235B-A22B and Command A+, both at tight fit. These are the largest models that can run on a single Apple Silicon machine with current hardware.
- **The frontier MoE flagships** (DeepSeek V3.2, GLM-5.2, Mistral Large 3, Kimi K2.6) require 256 GB+ unified memory or multi-GPU server infrastructure.

---

### 3.3 Chinese vs. Western Posture — Hosting, Provenance, Supply-Chain Trust

**License text vs. deployment risk are separate concerns.** The Chinese models with MIT/Apache 2.0 license texts are legally clean to use. The supply-chain concerns are different:

**Weights provenance:**
1. All Chinese LLMs have RLHF/alignment applied by Chinese labs. Independent testing has confirmed that DeepSeek, Qwen, GLM, and Kimi models all decline to engage with topics sensitive to the Chinese government (Taiwan independence, Tiananmen Square, Xinjiang). This is baked into the weights and cannot be patched without retraining. For a nutrition app this may be entirely irrelevant, but it is a fact about the weights.

2. GLM-5 was trained on Huawei Ascend + MindSpore infrastructure, not NVIDIA. This creates a supply chain independent of Western chip controls. For an AI lab trying to operate outside US export controls, this is a strategic feature. For a Western deployer, it means the training stack is entirely opaque.

3. DeepSeek has declined to give NVIDIA/AMD pre-release model access for optimization (as of V4 reporting), instead giving Huawei Ascend a head start. This signals a deliberate strategic decoupling.

**Data and API (for cloud use only, not local weights):**
- DeepSeek's privacy policy states data is stored in China and the PRC. Italy, Ireland, Belgium, South Korea, Japan have all opened investigations or imposed restrictions on DeepSeek's API. This is ONLY relevant if you call DeepSeek's cloud API — not for locally-hosted weights.
- Hunyuan's license explicitly excludes EU/UK/South Korea deployers regardless of data hosting.

**Western models:**
- Meta Llama 4's EU restriction on multimodal deployers is unusual and legally complex. End users in the EU are not restricted; only entities deploying the models in the EU as their principal place of business.
- Mistral (French), Cohere (Canadian), Google (US), Microsoft (US), Ai2 (US) have no geographic exclusions in their model licenses.
- Gemma 4's shift to pure Apache 2.0 removes previously contentious custom restrictions.

**Recommendation matrix for NutriMe context (personal nutrition app, US-based, family-of-4):**
- The DeepSeek alignment restriction on sensitive political topics is irrelevant for nutrition. MIT license is clean. Local hosting means no data-to-China concerns.
- Qwen3 Apache 2.0 is the cleanest Chinese option — no geographic restrictions, commercially permissive.
- If supply-chain trust matters (e.g., if this were enterprise or government), prefer Gemma 4, Mistral, Phi-4, Llama 4 as primary candidates.
- For a personal local-first project with no commercial ambitions and no EU deployment: the Chinese-provider models are practically usable.

---

## 4. Notable Findings and Insights

**1. The 32B dense model is the practical sweet spot for 2026 Apple Silicon.** Qwen3-32B (Apache 2.0, 128K context, 119 languages, native tool-use) and Qwen3.6-27B fit in 32 GB RAM with headroom, run at 15–30 tok/s on M3/M4, and are competitive with models 3–5× larger from 2024.

**2. Google's Gemma 4 Apache 2.0 pivot is significant.** Earlier Gemma versions had custom license restrictions that made them Yellow-tier. Gemma 4's clean Apache 2.0 with multimodal across all variants (including audio on small models) makes it the most compelling Google entry for self-hosted workloads.

**3. Mistral Large 3 (675B MoE, Apache 2.0, 256K context) is frontier-class open-weight but requires server infrastructure.** It is the largest fully-permissive open-weight model available as of June 2026. Not for Apple Silicon.

**4. Llama 4 Scout's 10M context window is extraordinary.** No other open-weight model offers anything close. The Llama 4 Community License is more restrictive than Apache 2.0, but for a family-of-4 personal app, the 700M MAU threshold and EU deployer restriction are not material.

**5. Kimi K2.6 and GLM-5.2 demonstrate China's frontier capability** but require infrastructure well beyond a laptop. Their MIT licenses are clean but the hardware bar (256 GB+) means they are cloud/server deployments for now.

**6. Phi-4 remains the best "efficiency play"** — MIT licensed, 14B–15B dense, fits 16 GB RAM, strong reasoning, vision-capable with Phi-4-Reasoning-Vision. The 16K context ceiling is the main constraint.

**7. The OSS ecosystem matures dramatically by mid-2026.** MLX on Apple Silicon now has production-grade support in Ollama (MLX backend auto-activates on 32 GB+ Macs). llama.cpp GGUF ecosystem is mature across all listed models. Inference speeds have roughly doubled vs. 2024 for the same hardware due to kernel optimization.

**8. DeepSeek R1-distill-32B (dense, 32B, MIT, 128K)** is arguably the best local reasoning model under 64 GB RAM — distilled from the frontier R1 reasoning chain, runs on any 32 GB Mac, MIT licensed.

---

## 5. Primary Source References

- GLM family: https://www.zhipuai.cn/en | https://huggingface.co/zai-org | https://venturebeat.com/ai/z-ai-debuts-open-source-glm-4-6v-a-native-tool-calling-vision-model-for
- GLM-5.2: https://www.trendingtopics.eu/glm-5-2-chinas-zhipu-ai-beats-even-googles-top-models-with-its-new-open-llm/
- DeepSeek V3/R1: https://github.com/deepseek-ai/DeepSeek-V3 | https://github.com/deepseek-ai/deepseek-r1 | https://huggingface.co/deepseek-ai/DeepSeek-R1
- DeepSeek V3.2: https://api-docs.deepseek.com/news/news251201 | https://huggingface.co/deepseek-ai/DeepSeek-V3.2-Exp
- DeepSeek privacy/legal: https://iapp.org/news/a/deepseek-and-the-china-data-question-direct-collection-open-source-and-the-limits-of-extraterritorial-enforcement | https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html
- Qwen3: https://github.com/QwenLM/Qwen3 | https://qwenlm.github.io/blog/qwen3/
- Qwen3.6: https://github.com/QwenLM/Qwen3.6 | https://www.marktechpost.com/2026/04/22/alibaba-qwen-team-releases-qwen3-6-27b
- Kimi K2.6: https://huggingface.co/moonshotai/Kimi-K2.6 | https://moonshotai.github.io/Kimi-K2/
- MiniCPM: https://github.com/openbmb/minicpm | https://huggingface.co/openbmb/MiniCPM-V-4.6
- InternLM3: https://github.com/InternLM/InternLM | https://internlm.readthedocs.io/en/latest/model_card/InternLM3.html
- Hunyuan: https://www.llmreference.com/model-family/hunyuan
- Meta Llama 4: https://ai.meta.com/blog/llama-4-multimodal-intelligence/ | https://www.llama.com/llama4/license/ | https://www.llama.com/llama4/use-policy/
- Mistral Large 3: https://mistral.ai/news/mistral-3/ | https://huggingface.co/mistralai/Mistral-Large-3-675B-Instruct-2512
- Phi-4: https://huggingface.co/microsoft/phi-4 | https://www.microsoft.com/en-us/research/publication/phi-4-reasoning-technical-report/ | https://huggingface.co/microsoft/Phi-4-reasoning-vision-15B
- Gemma 4: https://ai.google.dev/gemma/docs/releases | https://ai.google.dev/gemma/docs/core
- Command A+: https://cohere.com/blog/command-a-plus | https://www.businesswire.com/news/home/20260520121796/en/Cohere-Releases-Command-A-An-Open-Source-Enterprise-AI-Model-Built-for-Sovereign-Critical-Infrastructure
- OLMo 2: https://allenai.org/olmo2 | https://allenai.org/blog/olmo2
- Hardware estimates: https://apxml.com/posts/llama-4-system-requirements | https://willitrunai.com/blog/qwen-3-gpu-requirements | https://willitrunai.com/blog/llama-4-gpu-requirements | https://apxml.com/models/deepseek-v32
- Chinese models landscape: https://hai.stanford.edu/assets/files/hai-digichina-issue-brief-beyond-deepseek-chinas-diverse-open-weight-ai-ecosystem-policy-implications.pdf | https://intuitionlabs.ai/articles/chinese-open-source-llms-2025
- Apple Silicon inference: https://blog.starmorph.com/blog/apple-silicon-llm-inference-optimization-guide

---

*Survey conducted June 29, 2026. Model release dates are primary-source verified where possible; secondary-source figures are flagged. Hardware footprint figures are estimates based on standard quantization heuristics and community benchmarks — actual figures vary by implementation and KV cache configuration.*
