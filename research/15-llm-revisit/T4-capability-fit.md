# T4: LLM Capability Fit for NutriMe — OSS vs. Cloud, Mid-2026

**Research date:** 2026-06-29  
**Scope:** Seven capability dimensions comparing leading closed-cloud models against OSS models at 70B, 30B, and 7B parameter classes. NutriMe-specific gap assessment in final section.

**Current frontier closed models (as of June 2026):**
- **Claude Opus 4.6 / Sonnet 4.x** (Anthropic)
- **GPT-5 / GPT-5.4 / GPT-5.5** (OpenAI)
- **Gemini 3.1 Pro / Gemini 2.5 Pro** (Google DeepMind)
- **Grok 4** (xAI)

**Current leading OSS models referenced:**
- 70B+ class: Llama 4 Maverick (400B MoE, 17B active), Qwen3-72B, DeepSeek V3.2, GLM-5.2 / GLM-4.5
- 30B class: Qwen3-32B, Qwen3.5-27B, DeepSeek V3.1
- 7B–14B class: Llama 3.3 8B, Qwen3-7B / 8B, Phi-4 (~14B), Gemma 3-9B/27B

---

## Dimension 1 — Tool Use / Function Calling

**Why it matters for NutriMe:** The Stage 3 C1 orchestration layer depends on agents reliably calling food composition APIs, epistemic trail queries, meal-plan mutation tools, and condition-gating checks — often in multi-step chains across a single planning session.

### Benchmarks

**BFCL v4 (Berkeley Function Calling Leaderboard, June 2026)**  
The current authoritative structured function-call benchmark. v4 is the latest iteration, adding holistic agentic evaluation on top of v3's multi-turn interactions. As of June 2026, 9 models had been evaluated on BFCL v4.

| Model | BFCL v4 Score | Notes |
|---|---|---|
| Qwen3.7 Max (OSS, frontier MoE) | 75.0% | Top of v4 leaderboard |
| Qwen3.5-397B-A17B (OSS MoE) | 72.9% | |
| Qwen3.5-122B-A10B (OSS MoE) | 72.2% | |
| Qwen3.5-27B (OSS 27B dense) | 68.5% | Cheapest within 10% of leader |
| GLM-4.5 / GLM-5 (OSS) | ~70–76.7% on BFCL v3 | GLM-4.5 led BFCL v3 at 76.7% in June 2026 |

Note: As of June 2026, BFCL v4 had been published for only approximately 6 weeks and closed-cloud model scores (GPT-5, Claude Opus 4.x, Gemini 3.1) were not yet fully enumerated in the public leaderboard. On prior BFCL v3, top closed models scored in the 75–85% range (Claude 3.5/3.7 Sonnet and GPT-4o typically leading). The v4 gap between leading OSS and closed models appears to be narrowing.

**tau-bench (Sierra, multi-turn tool use in real-world scenarios)**  
Tests multi-step agentic tool calling across realistic retail and airline customer-service simulations. This is more demanding than BFCL because it measures task-level completion rather than per-call accuracy. GPT-5 and Claude Opus 4.x lead on tau-bench and WebArena; this is described as the area where "open-weights models have not yet closed" the gap as of mid-2026.

**Production failure-rate data (2026 practitioner benchmarks)**  
Observed well-formed tool invocation rates from local testing across 13 LLMs:
- Llama 3.3 70B: ~97% well-formed call rate (best OSS)
- Qwen3 32B+ families: competitive, ~90%+ well-formed in structured benchmarks
- Sub-7B models (Llama 3B, most generic 7B models): "low or zero tool invocation rates, confabulated responses in place of tool use, catastrophic failure on multi-step tool chains"
- 7B fine-tuned specialists (ToolACE-8B): reliable tool calling achievable, but requires explicit tool-call fine-tuning

**MCP-Atlas (June 2026, Model Context Protocol tool use, 500 tasks):**  
- GLM-5: 71.8%  
- Claude Opus 4.6: 69.2%  
- GPT-5.4: 67.2%

### Gap assessment — Dimension 1

**State of gap: Closing at 70B+, stable gap remains at 30B, significant gap below 7B.**

For NutriMe's multi-turn agent orchestration specifically: the 70B OSS tier (Qwen3 72B, DeepSeek V3.2, GLM-4.5/5, Llama 4 Maverick) is approaching parity with cloud models on single-call and short multi-step tool use. The **long-horizon, policy-constrained multi-turn** tier (tau-bench style) still favors GPT-5 and Claude Opus 4.x by a meaningful but not insurmountable margin.

Below 30B, the risk of malformed tool calls in complex multi-tool pipelines is high enough that production use requires either (a) specialist fine-tuning, (b) grammar-constrained decoding, or (c) routing through a larger model for tool dispatch. A 7B model should not be the sole tool-calling agent in NutriMe's orchestration layer.

---

## Dimension 2 — RAG / Grounding

**Why it matters for NutriMe:** The epistemic trail (Stage 3 B2) requires models to cite sources accurately and refuse to generate unsupported nutritional claims. Evidence-grounded recommendations depend on faithful retrieval and resistance to confabulation.

### Benchmarks

**FACTS Grounding (Google DeepMind)**  
Tests whether model outputs are fully supported by provided context. Critically distinguishes "hallucinating new facts" from "correctly saying 'I don't know.'"

**GaRAGe (Amazon Science, June 2026)**  
Large-scale RAG benchmark with human-curated long-form answers and grounding-passage annotations. 2,366 questions, 35K+ annotated passages from both private documents and the web.

**RAGBench / ARES**  
General-purpose retrieval-and-generation benchmarks covering faithfulness, answer relevance, and context relevance.

**URAG (2026) — Uncertainty Quantification in RAG**  
Specific focus on whether models correctly express uncertainty when retrieved context does not support a claim — directly relevant to NutriMe's "refuse when unsupported" requirement.

**Current state of RAG grounding by model tier:**

Closed models (GPT-5, Gemini 3.1 Pro, Claude Opus 4.x) consistently achieve higher faithfulness scores and lower hallucination rates in RAG contexts, partly because their RLHF/Constitutional AI training explicitly rewards citation accuracy and refusal on unsupported claims. Specific numeric comparisons on GaRAGe and URAG are not yet widely published as of June 2026 (these benchmarks are relatively new), so exact scores are not available.

For the Qwen3 family, the 72B model shows strong RAG faithfulness when context is well-structured but degrades on adversarial or noisy retrieval contexts. DeepSeek V3.2 shows a weaker instruction-following profile (DeepSeek V3.1 ranked 95/104 on instruction-following leaderboards), which predicts weaker grounding discipline. GLM-4.5 performs well on SimpleQA (factual accuracy with cited sources) despite being a smaller model (355B total parameters) performing comparably to DeepSeek V3/R1 (671B).

**Nutrition-domain grounding specifically:** FoodBench-QA 2026 found that domain-specialized models (FoodyLLM) significantly outperform general-purpose LLMs on grounded food-and-nutrition QA. Few-shot use of Gemini 2.5 Flash was the strongest general-purpose approach. OSS models at 7B-8B without food-domain fine-tuning showed meaningful gaps on grounded nutritional entity linking.

### Gap assessment — Dimension 2

**State of gap: Stable, modest gap favoring closed models, especially on uncertainty and refusal behavior.**

For NutriMe's epistemic trail specifically: RAG retrieval quality itself is now roughly equivalent across model tiers (the retrieval pipeline matters more than the model). The gap lives in **faithful citation and principled refusal** — "I cannot support this claim from retrieved context." Closed models are more reliably trained for that behavior. OSS 70B models can match this with explicit system prompting, but the behavior is more brittle under adversarial prompting or noisy retrieval. Below 30B, grounding discipline degrades noticeably. The FoodBench-QA finding about domain-specialized models is the most actionable for NutriMe: a fine-tuned OSS model may outperform a general-purpose cloud model on nutrition grounding.

---

## Dimension 3 — Long Context

**Why it matters for NutriMe:** Loading the user's epistemic trail (potentially spanning months of dietary history), multi-document recipe corpora, and dietary constraint history requires reliable usability across 32K–128K context windows.

### Benchmarks

**RULER (NVIDIA, configurable-length NIAH variants)**  
13 tasks across retrieval, multi-hop tracing, aggregation, and QA. Reveals that claimed context lengths are often much larger than usable context lengths — RULER found that only half of 17 tested models maintained satisfactory performance at 32K when they claimed to support it.

**LongBench v2 / LongBench Pro (2026 bilingual)**  
LongBench Pro evaluated 46 long-context LLMs and found that "long-context optimization contributes more than parameter scaling to comprehension quality."

**NIAH (Needle-in-a-Haystack)**  
The foundational retrieval benchmark at varying context depths.

**Current findings by model tier:**

**Claimed vs. usable context — the central finding:**  
Most 2026 models claiming 128K context show 15–30% accuracy degradation between 4K and 128K on RULER. This is not unique to OSS models — it affects all tiers, but the degradation is generally steeper for smaller models and models without explicit long-context training.

**Model-specific notes:**
- **Qwen3 family (all dense models):** Native 32K context, extended to 128K with YaRN. The 7B–32B range shows improving performance with scale; marginal gains decrease above 32B. The Qwen family has invested explicitly in long-context training.
- **Llama 4 Scout/Maverick:** Claimed 10M token context (Scout) and very long windows (Maverick) are marketing claims; usable context for complex reasoning tasks is substantially shorter. Maverick's active-parameter MoE architecture helps with throughput but context degradation on multi-hop reasoning remains at frontier-model levels.
- **DeepSeek V3.2:** 128K window; strong at moderate lengths (up to 64K), degrades on complex multi-hop reasoning above 64K.
- **GLM-4.5 / GLM-5:** Supports 128K; performs well on long-document summarization tasks.
- **Closed models:** Gemini 3.1 Pro leads on long-context tasks with its 2M token window; usable accuracy across the full window is not perfectly maintained but degrades less than most OSS models. Claude Opus 4.x performs well up to 200K; GPT-5 degrades at very long contexts.

**Quantization note (2026 paper):** A May 2026 paper found that 4-bit quantization degrades long-context retrieval accuracy by 5–12%, with degradation increasing at higher compression. This matters for OSS deployment where quantization enables running 70B models on consumer hardware.

### Gap assessment — Dimension 3

**State of gap: Widening at extreme lengths (>128K), roughly stable at 32K–64K between closed and 70B OSS.**

For NutriMe's specific use: an epistemic trail of months of history is unlikely to exceed 64K tokens as a practical matter. At 32K–64K, Qwen3-32B and Qwen3-72B perform adequately. The breakpoint is 128K+ — at that range, Gemini 3.1 Pro maintains reliability while most OSS models degrade. The practical recommendation is to design the epistemic trail context window to stay under 64K, which makes the OSS tier viable. If quantization is used (4-bit for 70B deployment), budget for 5–12% additional degradation on retrieval tasks.

---

## Dimension 4 — Instruction Following / Constitutional Behavior

**Why it matters for NutriMe:** NutriMe has 10 non-negotiable constitutional rules (e.g., condition-gating requirements, epistemic transparency). These must be reliably applied across all agent turns and cannot be overridden by adversarial user prompting.

### Benchmarks

**IFEval (Google, instruction-following evaluation)**  
Structured benchmark testing compliance with explicit format and constraint instructions. The June 2026 IFEval leaderboard has 65 evaluated models.

**FollowBench / MT-Bench**  
Multi-constraint and multi-turn instruction following.

**IFEval scores by model (June 2026):**

| Model | IFEval Score | Notes |
|---|---|---|
| Qwen3.5-27B (OSS) | 95.0% | Leaderboard leader |
| Qwen3.6 Plus (OSS) | 94.3% | |
| Llama 3.3 8B (OSS) | 92.1% | Strongest small model |
| Qwen3.5-9B (OSS) | 91.5% | |
| DeepSeek R1 (OSS) | 87.8% | |
| Nemotron Ultra 253B (OSS) | 89.5% | |
| Claude Opus 4.x (closed) | Not separately listed in results found; historically competitive with top OSS on IFEval |
| GPT-5 family (closed) | Not separately listed; historically ≥90% on structured instruction following |

The striking finding is that Qwen3.5-27B leads the IFEval leaderboard at 95%, surpassing comparable closed models on this specific benchmark. Llama 3.3 8B at 92.1% is the best small-model result found.

**Constitutional / adversarial behavior:**  
This is where the gap is most consequential and least quantified. Constitutional AI (Anthropic's approach) and OpenAI's deliberative alignment are explicitly trained for principled rule-following under adversarial pressure. 2026 jailbreak research finds:
- Success rates of 65–99% against frontier models under sophisticated automated attacks (this affects all models, not OSS-only)
- "Competing content fragments" in long contexts can degrade safety enforcement by up to 21.2% even on instruction-following-tuned models
- OSS models without explicit adversarial RLHF training are more vulnerable; this is a known limitation of the Llama, Qwen, and DeepSeek families relative to Anthropic/OpenAI models with explicit adversarial training

DeepSeek V3.1's instruction following rank of 95/104 on one comprehensive leaderboard is a meaningful warning — it suggests inconsistent compliance even without adversarial pressure.

### Gap assessment — Dimension 4

**State of gap: IFEval gap is closed at 27B+; constitutional / adversarial robustness gap remains real at all OSS scales.**

For NutriMe's constitutional rules specifically: structured instruction following (IFEval-style format compliance) is fine at 27B+ OSS. The gap is in **adversarial rule-following** — whether constitutional rules hold when users probe them. Closed models with explicit Constitutional AI or deliberative alignment training are meaningfully more robust. This gap does not close with parameter count alone; it requires explicit adversarial fine-tuning. The 7B class is adequate for structured instruction following under normal conditions but is a higher risk under adversarial prompting.

---

## Dimension 5 — Multilingual

**Why it matters for NutriMe:** Recipes and cuisines span globally. Ingredient names, technique descriptions, and nutrition education content exist in multiple languages. Chinese-language cuisine and food ontologies are particularly relevant.

### Benchmarks

**MGSM (Multilingual Grade School Math)**  
250 problems translated into 10 languages spanning high-resource (Chinese, German), medium-resource (Thai, Japanese), and low-resource groups. Tests mathematical reasoning across languages.

**FLORES-101 / FLORES-200**  
Translation benchmarks; 5-shot evaluation. Tests language transfer quality.

**C-Eval / CMMLU (Chinese-specific)**  
High-quality Chinese academic and professional knowledge benchmarks.

**Current findings:**

**Qwen3 family is the strongest OSS multilingual performer:**
- Trained on 36 trillion tokens across 119 languages and dialects (up from 29 in Qwen 2.5)
- Qwen2.5-72B achieves MGSM results comparable to Llama 3-405B while using one-fifth of the parameters
- "Qwen series models are the best" on MGSM among recent open models per the Llama 3 technical report
- Native Chinese training corpus gives it a structural advantage over Western-centric models on C-Eval and CMMLU

**Llama 4 family:**  
Maverick and Scout are natively multimodal with multilingual text capabilities. Maverick scores 85.5% on MMLU (which has multilingual variants) but its multilingual depth outside English is not as strong as Qwen's due to training corpus composition.

**Closed models:**  
Gemini 3.1 Pro leads on multilingual tasks because of Google Translate-quality training data. GPT-5.x is strong across high-resource languages. Claude Opus 4.x is strong in English and European languages but Qwen3 consistently outperforms it on Chinese-specific benchmarks.

**GLM-5 / GLM-4.5:**  
Developed by Tsinghua/Zhipu AI, these models are purpose-built for Chinese-English bilingual tasks. GLM-5 specifically excels on Chinese long-document and code tasks.

**For low-resource languages:**  
The gap between closed models and OSS remains meaningful below the top-6 language groups. For NutriMe's cuisine scope (covering Southeast Asian, South Asian, Mediterranean, East Asian cuisines), Qwen3 at 32B+ handles the relevant language surface area well.

### Gap assessment — Dimension 5

**State of gap: Closed or reversed for Chinese; narrowing for top-10 languages; real gap persists for low-resource.**

For NutriMe's specific use: Chinese recipe and food-concept handling is actually better in Qwen3 (any size ≥32B) than in Claude or GPT-5 for many Chinese-specific tasks. Japanese, Korean, Spanish, French, Italian, Thai are well-served by 72B+ OSS models. Low-resource language cuisines (many African, Central Asian dishes) may need fallback to cloud Gemini. This dimension is one of the strongest arguments for OSS (specifically Qwen3) in NutriMe's architecture.

---

## Dimension 6 — Reasoning + Math

**Why it matters for NutriMe:** Nutrient correctness requires accurate arithmetic across multi-ingredient recipes. Dietary constraint satisfaction (condition-gating) involves multi-step logical reasoning over health conditions. Personalization calculations require correct numeric reasoning.

### Benchmarks

**GPQA Diamond (graduate-level science reasoning)**  
Canonical benchmark for hard reasoning requiring multi-step scientific judgment.

**AIME 2024/2025 (AMC/AIME math competition)**  
Hard mathematical reasoning requiring multi-step proof and calculation.

**MATH-500 / MMLU-Pro**  
MMLU-Pro adds chain-of-thought and harder reasoning; MATH-500 tests competition math.

**ARC-AGI v2**  
Abstract reasoning benchmark. Still substantially unsolved.

**Scores (mid-2026):**

**GPQA Diamond:**

| Model | Score | Notes |
|---|---|---|
| Gemini 3.1 Pro (closed) | 94.1% | Current leaderboard leader as of June 2026 |
| GPT-5.5 (closed) | 94.0% | |
| Claude Opus 4.8 (closed) | 93.6% | |
| Qwen3-235B-A22B thinking (OSS MoE) | 88.4% | Strongest OSS; beats every closed model except top frontier |
| DeepSeek R1 (OSS) | ~85% range (mid-2025 data) | |
| Qwen3-32B (thinking mode) | Competitive in 78–82% range based on Qwen3 technical report |
| Qwen3-7B (thinking mode) | ~70% range estimate |

Note: GPQA is approaching saturation at the top frontier; MMLU is already saturated (88–94% for all top models, "no longer differentiates frontier models").

**AIME 2025:**

Top closed models (GPT-5, Grok 4, Gemini 2.5 Pro/3.1, DeepSeek R1): 88–95% band  
Qwen3-235B-A22B (thinking): leads OSS open-weight models; outperforms DeepSeek-R1 on 17/23 benchmarks  
Qwen3-30B on AIME 2025: 70–90% depending on sampling; outperforms Claude 3.7 Sonnet (55%) but trails o3 (86%)  
Klear-Reasoner 8B (fine-tuned): 83.2% — demonstrates that fine-tuned 8B models can reach competitive math performance  
DeepSeek R1: 74.0% vs GPT-5's 94.6%

**MATH-500:**  
DeepSeek R1: 97.3% (near-perfect on MATH-500)  
MATH-500 is effectively saturated for top-tier models.

**DeepSeek V4 (latest, released early 2026):**  
92.8% MMLU-Pro, 99.4% AIME 2026 — the strongest single OSS model on reasoning benchmarks as of mid-2026.

### Gap assessment — Dimension 6

**State of gap: Largely closed for math at top OSS tier (70B+ with thinking); modest gap remains on multi-step scientific reasoning.**

For NutriMe's specific use: nutrient arithmetic and recipe scaling are straightforward math — all models at 7B+ handle this reliably. Dietary constraint satisfaction (multi-step logical reasoning over health conditions) is where reasoning depth matters. At 70B+ with thinking mode (Qwen3, DeepSeek V4, GLM-5), OSS models are competitive with closed models. At 7B, reasoning chains on complex multi-constraint problems fail at a meaningful rate. The 32B range is the practical sweet spot for reliable multi-step dietary reasoning.

---

## Dimension 7 — Medical / Nutrition Domain Knowledge

**Why it matters for NutriMe:** Dietary recommendations intersect clinical medicine — especially condition-gating for diabetes, CVD, renal disease, pregnancy. Nutrient correctness and safety-relevant dietary advice requires accurate domain knowledge.

### Benchmarks

**HealthBench (OpenAI, 2025)**  
Realistic clinical queries designed by clinicians. Tests both factual accuracy and clinically appropriate uncertainty expression. More demanding than MCQ benchmarks.

**MedQA / USMLE-style**  
Multiple-choice medical knowledge benchmark. Well-established but increasingly saturated.

**PubMedQA**  
Scientific literature question answering.

**NutriBench (ICLR 2025)**  
First dedicated nutrition-estimation benchmark. 11,857 meal descriptions annotated with macro-nutrient labels. Evaluated 12 LLMs including Llama 3.1 variants (8B, 70B, 405B), Gemma 2 (9B, 27B), Qwen 2 (7B, 70B), GPT-4o, OpenBioLLM-70B. Best performance: 66.82% accuracy with Chain-of-Thought prompting.

**FoodBench-QA 2026 (LREC 2026)**  
Nutrient estimation, FSA traffic-light prediction, and food entity recognition/linking across food semantic models. Found that domain-specialized FoodyLLM "significantly outperforms general-purpose LLMs across all tasks." Gemini 2.5 Flash was the best general-purpose approach.

**HealthBench scores:**

| Model | HealthBench Score | Notes |
|---|---|---|
| GPT-5 (thinking) (closed) | ~0.73 (73% on scale) | ~1.6% error on hard cases |
| o3 (closed) | 0.60 | Led original HealthBench release |
| GPT-4.1 (closed) | Better than GPT-4o; worse than o3 | |
| Claude 3.7 Sonnet (closed) | Below o3 on HealthBench original | |
| GPT-4o (closed) | 15.8% error rate on hard cases | |
| Llama 4 Maverick (OSS) | Listed as evaluated; score not pinpointed in sources |
| OSS 70B general (Llama 3.1 70B) | Not separately scored; inferred below closed frontier on HealthBench |

**MedQA / USMLE notes:**  
GPT-5 reaches ~93% on USMLE-style MedQA; OSS 70B models (Llama 3.1 70B, OpenBioLLM-70B) reach the 70–80% range. The gap between 93% GPT-5 and 75% OSS 70B represents real clinical knowledge differences, but NutriMe's use case is dietary advice, not clinical diagnosis.

**Critical NutriQA finding:**  
No dedicated NutriQA benchmark was found; the benchmark does not appear to be widely established in literature. NutriBench is the closest active nutrition-specific benchmark. FoodBench-QA 2026 is the most current.

**Domain specialization beats parameter count:**  
FoodBench-QA's finding that FoodyLLM (fine-tuned) outperforms all general-purpose LLMs including cloud models is important for NutriMe. A fine-tuned 7B OSS model on nutrition data may outperform GPT-5 on food entity linking and nutrient estimation. This is a strategic option for NutriMe's food composition lookup path.

### Gap assessment — Dimension 7

**State of gap: Real but shrinking for clinical MCQ; most significant on realistic clinical judgment (HealthBench); potentially reversible through domain fine-tuning.**

For NutriMe's specific use: food composition lookups (calories, macros, micros per ingredient) are well within the capability of all 30B+ OSS models with or without fine-tuning. The gap appears when the system must exercise clinical judgment — e.g., flagging drug-nutrient interactions, reasoning about kidney-disease dietary restrictions in complex cases. For condition-gating specifically, a 70B OSS model with carefully designed system prompts covering the conditions is likely adequate for the NutriMe use case (not clinical diagnosis, but personalized dietary guidance). Domain fine-tuning is the highest-leverage lever for nutrition-specific accuracy.

---

## NutriMe-Relevant Capability Gap Assessment

### Summary matrix

| Dimension | 7B OSS | 30B OSS | 70B OSS | Cloud Closed | Notes |
|---|---|---|---|---|---|
| Tool use / function calling | High risk | Moderate risk | Near-parity | Best | Multi-turn chains critical for Stage 3 C1 |
| RAG grounding / refusal | Moderate risk | Moderate risk | Moderate gap | Best | Adversarial grounding discipline still favors closed |
| Long context (32K–64K) | Degrades | Adequate | Adequate | Best | Critical: stay under 64K epistemic trail |
| Instruction following (structured) | Fine | Fine | Fine | Fine | IFEval gap is closed at 27B+ |
| Constitutional / adversarial rules | High risk | Moderate risk | Moderate gap | Best | Adversarial robustness not equal |
| Multilingual (top 10 languages) | Adequate | Good | Near-parity | Best | Qwen3 leads OSS, rivals cloud on Chinese |
| Reasoning + math | Adequate for simple | Adequate | Near-parity | Best | 32B+ reliable for complex constraint reasoning |
| Medical / nutrition domain | High risk | Moderate | Adequate | Best | Fine-tuning reverses gap |

### Specific breakpoints by parameter class

**7B class (Llama 3.3 8B, Qwen3-7B/8B, Phi-4 14B, Gemma 3-9B):**
- IFEval structured instruction following: adequate (Llama 3.3 8B reaches 92.1%)
- Multi-step tool calling: high failure rate without specialist fine-tuning; not production-safe for NutriMe's multi-tool orchestration layer
- Long context: degrades measurably above 32K; Qwen3 8B with YaRN can reach 128K claimed but usable length is much shorter
- Constitutional robustness: adequate under normal prompting; meaningful risk under adversarial pressure
- Multilingual: Qwen3-7B handles top-6 languages reasonably; edge cases in non-English cuisine terminology will fail
- Nutrition domain: unreliable for complex nutrient reasoning without fine-tuning; NutriBench 2024 showed 70B models substantially outperform 7B on carbohydrate estimation
- **Verdict for NutriMe:** 7B models are suitable only for isolated, low-stakes leaf tasks (e.g., ingredient name normalization, simple format conversion). Not suitable as primary orchestrator or tool-calling agent.

**30B class (Qwen3-32B, Qwen3.5-27B, DeepSeek V3.1):**
- IFEval: excellent — Qwen3.5-27B leads at 95.0%
- Tool use: adequate for single-turn and short multi-turn; fragility appears on 5+ step chains
- Long context: 64K usable reliably; 128K with degradation
- Constitutional: structured rules hold reliably; adversarial robustness moderate
- Reasoning: 32B is the practical sweet spot for reliable multi-step dietary constraint reasoning
- Multilingual: Qwen3-32B is among the best OSS options for Chinese-language food content
- **Verdict for NutriMe:** 30B is the minimum viable tier for the reasoning core. Qwen3-32B is the strongest single choice in this tier.

**70B+ class (Qwen3-72B, Llama 4 Maverick, DeepSeek V3.2, GLM-4.5/5):**
- Tool calling: near-parity with closed models for structured function calling; some gap remains in long-horizon multi-agent policy compliance
- RAG grounding: adequate with explicit system prompts; adversarial faithfulness slightly below closed models
- Long context: 64K reliable; 128K usable with planned degradation budget
- Constitutional: best-available OSS option; still below Anthropic Constitutional AI and OpenAI deliberative alignment on adversarial tests
- Reasoning: competitive with o3 / Claude Sonnet on most NutriMe-class tasks
- Nutrition domain: adequate for condition-gating with well-designed prompts; domain fine-tuning would close the remaining gap
- **Verdict for NutriMe:** 70B+ is the tier at which OSS becomes genuinely viable for the full NutriMe stack. Qwen3-72B or GLM-5 are the recommended primary options.

### Named capability gaps that matter for NutriMe

**Gap 1 — Multi-turn tool use below 30B:**  
The tau-bench class of multi-turn, policy-constrained tool use remains the sharpest gap between OSS and closed models. This matters because NutriMe's meal-planning agent makes 4–8 sequential tool calls (food lookup, constraint check, epistemic trail update, condition gate, recipe mutation, macro recalculation). Below 30B, failure rates on this chain are non-trivial. At 70B+, OSS narrows the gap substantially but does not fully close it.

**Gap 2 — Adversarial constitutional robustness at all OSS scales:**  
If a user systematically probes NutriMe's constitutional rules (e.g., attempting to bypass condition-gating for a clinically restricted ingredient), OSS models at all scales are more susceptible than Claude Opus 4.x with Constitutional AI. This gap does not correlate cleanly with parameter count — it requires explicit adversarial training. The practical mitigation is a hardcoded rule layer outside the LLM for the most critical gates.

**Gap 3 — Long context above 64K:**  
For an epistemic trail that grows over months, context length management is important. The OSS-viable window is 32K–64K. Above 64K, accuracy degrades enough to recommend Gemini 3.1 Pro (2M window with best long-context accuracy) for trail-loading tasks. Practical design recommendation: chunk and summarize epistemic trail rather than loading raw history above 64K.

**Gap 4 — Nutrition-specific domain knowledge at 7B:**  
NutriBench results show that carbohydrate estimation accuracy at 7B OSS is materially worse than at 70B or GPT-4o. For nutrition computation tasks (macro tracking, meal scoring against dietary targets), the 7B tier needs either (a) specialist fine-tuning or (b) RAG against a structured food composition database (USDA FoodData Central, etc.) rather than relying on parametric knowledge.

**Gap 5 — DeepSeek V3.x instruction following reliability:**  
DeepSeek V3.1's ranking of 95/104 on instruction-following benchmarks in one comprehensive leaderboard is a specific warning flag. For NutriMe's constitutional rules, a model that is not reliably instruction-following is a structural risk. DeepSeek's reasoning variants (R1) are strong at mathematical tasks but should not be the primary instruction-following agent. Qwen3 and GLM families are preferable for instruction-discipline tasks.

### Strategic recommendation for NutriMe's LLM architecture

Based on the mid-2026 benchmark landscape:

1. **Primary orchestrator and tool-calling agent:** Qwen3-72B (OSS) or cloud Claude Sonnet 4.x depending on privacy/cost tradeoffs. Qwen3-72B is the strongest all-rounder OSS choice; the gap to Claude Sonnet 4.x is small enough to be worth the tradeoff for local-first deployment.

2. **Constitutional rules enforcement:** Do not rely solely on LLM instruction following for the hardest non-negotiable rules (condition-gating for clinical constraints). Layer a deterministic rule-check outside the model.

3. **Nutrition domain lookups:** RAG against USDA FoodData Central or similar structured source is more reliable than parametric knowledge at any model tier, but especially below 70B.

4. **Chinese and East Asian recipe content:** Qwen3 (32B+) is preferred over Claude/GPT for Chinese-language cuisine handling — the gap reverses in OSS's favor.

5. **Epistemic trail context:** Design to stay under 64K tokens. Summarize rather than concatenate for longer trails. This keeps the OSS 70B tier viable and avoids forced cloud dependence.

6. **7B deployment (on-device or low-cost):** Viable only for narrow, low-stakes leaf tasks. Not viable as primary agent. If on-device capability is a future goal, plan for specialist fine-tuning of a 7B model for the specific NutriMe tool-call and instruction-following surface.

---

## Source Freshness Flags

- BFCL v4 data: June 2026 (fresh), but only 9 models evaluated — coverage incomplete
- tau-bench gap description: based on general 2026 industry reporting, not a June 2026 primary paper
- HealthBench: original paper May 2025 (arxiv:2505.08775); updated with GPT-5 data through early 2026
- NutriBench: ICLR 2025 (model scores reflect pre-Qwen3 / pre-Llama4 era — roughly 12 months stale for OSS model comparisons)
- FoodBench-QA: LREC 2026 (fresh)
- IFEval leaderboard: June 2026 (fresh)
- GPQA/AIME scores: mid-2025 for some OSS models; frontier closed model scores through June 2026
- DeepSeek V4 benchmark data: early 2026 release data
- GLM-4.5 technical report: arxiv:2508.06471 — note this timestamp is August 2025, which is within the assistant's knowledge cutoff but reflects pre-release data from the GLM team

---

## Primary Sources

- [BFCL v4 Leaderboard — Berkeley Gorilla](https://gorilla.cs.berkeley.edu/leaderboard.html)
- [BFCL-V4 Leaderboard scores — llm-stats.com](https://llm-stats.com/benchmarks/bfcl-v4)
- [Function Calling Benchmarks Leaderboard 2026 — Awesome Agents](https://awesomeagents.ai/leaderboards/function-calling-benchmarks-leaderboard/)
- [AI Agent Tool Calling Benchmarks — Spheron Blog](https://www.spheron.network/blog/tool-calling-benchmarks-bfcl-tau-bench-latency-optimization/)
- [Best Local Models for Tool Calling in 2026 — PromptQuorum](https://www.promptquorum.com/power-local-llm/best-local-models-tool-calling-2026)
- [Why Small LLMs Fail at Tool Calling — DEV Community](https://dev.to/anak_wannaphaschaiyong_11/why-small-llms-fail-at-tool-calling-the-shocking-discovery-from-our-llama-3b-benchmark-5lg)
- [I Tested 13 Local LLMs on Tool Calling — jdhodges.com](https://www.jdhodges.com/blog/local-llms-on-tool-calling-2026-pt1-local-lm/)
- [GaRAGe Benchmark (Amazon Science, June 2026)](https://arxiv.org/abs/2506.07671)
- [RAG Evaluation 2026 — Label Your Data](https://labelyourdata.com/articles/llm-fine-tuning/rag-evaluation)
- [RULER Leaderboard — llm-stats.com](https://llm-stats.com/benchmarks/ruler)
- [Long-Context Benchmarks Leaderboard — Awesome Agents](https://awesomeagents.ai/leaderboards/long-context-benchmarks-leaderboard/)
- [LongBench Pro (arxiv:2601.02872)](https://arxiv.org/html/2601.02872v1)
- [Does Quantization Affect Long-Context Performance? (arxiv:2505.20276)](https://arxiv.org/pdf/2505.20276)
- [IFEval Leaderboard 2026 — BenchLM.ai](https://benchlm.ai/instruction-following)
- [IFEval Rankings 2026 — Awesome Agents](https://awesomeagents.ai/leaderboards/instruction-following-leaderboard/)
- [LLM Jailbreaks 2026 — redteams.ai](https://redteams.ai/blog/llm-jailbreaking-2026)
- [LLM Jailbreaks — RingSafe](https://ringsafe.in/llm-jailbreaks-2026-universal-suffixes-many-shot-crescendo-and-what-constitutional-ai-actually-stops/)
- [Qwen3 Technical Report (arxiv:2505.09388)](https://arxiv.org/html/2505.09388v1)
- [Qwen2.5-LLM Blog — Qwen](https://qwenlm.github.io/blog/qwen2.5-llm/)
- [Medical LLM Leaderboard 2026 — Awesome Agents](https://awesomeagents.ai/leaderboards/medical-llm-leaderboard/)
- [HealthBench Paper (arxiv:2505.08775)](https://arxiv.org/html/2505.08775v1)
- [OpenAI HealthBench in Action (arxiv:2509.02594v2)](https://arxiv.org/html/2509.02594v2)
- [NutriBench (arxiv:2407.12843)](https://arxiv.org/abs/2407.12843)
- [FoodBench-QA 2026 (arxiv:2604.25774)](https://arxiv.org/html/2604.25774)
- [Large LLMs in Food and Nutrition Science — ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2665927126000511)
- [GLM-5 Benchmark Scores — BenchLM.ai](https://benchlm.ai/models/glm-5)
- [GLM-4.5 Technical Report (arxiv:2508.06471)](https://arxiv.org/pdf/2508.06471)
- [Llama 4 Maverick Benchmarks — BenchLM.ai](https://benchlm.ai/models/llama-4-maverick)
- [DeepSeek V3.2 Technical Report (arxiv:2512.02556)](https://arxiv.org/pdf/2512.02556)
- [AIME 2025 Benchmark Analysis — IntuitionLabs](https://intuitionlabs.ai/articles/aime-2025-ai-benchmark-explained)
- [2025 LLM Review — Atoms.dev](https://atoms.dev/blog/2025-llm-review-gpt-5-2-gemini-3-pro-claude-4-5)
- [GPQA Leaderboard 2026 — pricepertoken.com](https://pricepertoken.com/leaderboards/benchmark/gpqa)
- [Open Source LLM Leaderboard — BenchLM.ai](https://benchlm.ai/best/open-source)
- [Open Source vs Closed LLMs: The 2026 Decision Framework — Let's Data Science](https://letsdatascience.com/blog/open-source-vs-closed-llms-choosing-the-right-model-in-2026)
