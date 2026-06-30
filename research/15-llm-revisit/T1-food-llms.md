# Food / Nutrition / Flavor LLM Landscape — Research Report
**Task:** T1 — Food-LLM Ecosystem Survey  
**Date:** 2026-06-29  
**Scope:** Verification of six named projects + adjacent OSS landscape discovery

---

## Section 1 — Verification of Named Projects

### 1.1 FoodSky

**Status: CONFIRMED**

- **Primary sources:** arXiv [2406.10261](https://arxiv.org/abs/2406.10261) (preprint June 2024); peer-reviewed publication in *Cell Patterns* (April 2025, DOI via ScienceDirect [S2666-3899(25)00082-0](https://www.sciencedirect.com/science/article/pii/S2666389925000820)); GitHub [LanceZPF/FoodSky](https://github.com/LanceZPF/FoodSky); dataset on Zenodo [10.5281/zenodo.13836709](https://zenodo.org/records/13836709).
- **What it is:** The first Chinese-language food-domain LLM. Trained on the FoodEarth corpus and fine-tuned for cooking and dietetic reasoning.
- **Base models:** Two backbone variants — Chinese LLaMA-2 (CLLaMA2-7B and CLLaMA2-13B) and Qwen2.5. Fine-tuning used LoRA throughout. Named variants are FoodSky-CL (7B and 13B) and FoodSky-Qw.
- **Key capabilities:**
  - Passes Chinese National Chef Examination (83.3% accuracy) and Chinese Dietetic Examination (91.2% accuracy)
  - Recipe generation, dietary recommendation, diet-disease correlation reasoning
  - Incorporates Topic-Based Selective State Space Model (TS3M) and Hierarchical Topic Retrieval-Enhanced Generation (HTRAG) for food-specific context handling
- **License:** CC BY-NC-ND (non-commercial, no derivatives) — confirmed via GitHub and journal publication notice.
- **Currency:** Journal paper April 2025; GitHub repository has 27 stars, limited recent commit activity. An online demo existed at `http://222.92.101.211:8200` (availability not verified).
- **Limitations:** Chinese-language corpus and exams only; English-language performance is untested by the authors; full FoodEarth corpus is encrypted due to commercial conflicts (only the 20K-instance mini is public).
- **Fit for NutriMe:** Low for English-first use. The architecture choices (TS3M, HTRAG) and LoRA fine-tuning approach are instructive as a template, but the model itself is not directly usable for an English-language personal nutrition app.

---

### 1.2 FoodyLLM

**Status: CONFIRMED**

- **Primary sources:** ScienceDirect / *npj Digital Medicine* (received Nov 2025, accepted Feb 2026, published Feb 16 2026): [S2665927126000511](https://www.sciencedirect.com/science/article/pii/S2665927126000511); PMC [PMC12927182](https://pmc.ncbi.nlm.nih.gov/articles/PMC12927182/); PubMed [41737890](https://pubmed.ncbi.nlm.nih.gov/41737890/); HuggingFace [Matej/FoodyLLM](https://huggingface.co/Matej/FoodyLLM); GitHub [matejMartinc/FoodyLLM](https://github.com/matejMartinc/FoodyLLM).
- **What it is:** A domain-specialized LLM fine-tuned for structured food-science tasks supporting FAIR data principles.
- **Base model:** Meta-Llama-3-8B-Instruct (8B parameters), fine-tuned via LoRA adapters.
- **Training data:** 225,000 task-aligned QA pairs covering three tasks: recipe nutrient estimation, traffic-light food labeling (UK/EU scheme), and ontology-based food entity linking.
- **Key capabilities and results:**
  - Nutrient estimation accuracy: 0.91–0.97 (vs. 0.43 for zero-shot GPT baseline)
  - Traffic-light macro F1: 0.86–0.97 (vs. 0.46 baseline)
  - Ontology entity linking (FoodOn/SNOMED): 0.67–0.84 on real corpora
- **License:** MIT — confirmed via GitHub.
- **Currency:** Published February 2026; model on HuggingFace as of publication date; active GitHub repository.
- **Limitations:** Fine-tuned for structured prediction tasks (classification, estimation), not open-ended dialogue or recipe generation. English-language only. Ontology linking requires specific ontology targets (FoodOn, SNOMED-CT, Hansard).
- **Fit for NutriMe:** High relevance for the nutrient-estimation and condition-gating modules. The LoRA adapter approach on Llama-3-8B-Instruct means the training recipe is fully reproducible on consumer hardware. MIT license is clean for personal use.

---

### 1.3 FoodPuzzle

**Status: CONFIRMED**

- **Primary sources:** arXiv [2409.12832](https://arxiv.org/abs/2409.12832) (September 2024); published in *Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining*, KDD '25, pages 5493–5504 ([ACM DL](https://dl.acm.org/doi/10.1145/3711896.3737384)); GitHub [tenghaohuang/FoodPuzzle](https://github.com/tenghaohuang/FoodPuzzle).
- **What it is:** A benchmark and scientific-agent framework treating LLMs as autonomous "flavor scientists" for flavor profile sourcing and ingredient pairing hypothesis generation.
- **Architecture:** Not a fine-tuned model — a pipeline combining in-context learning, RAG from FlavorDB, scholarly articles, and food blogs, and structured hypothesis generation. Uses general-purpose LLMs (GPT-4 class) as the reasoning backbone.
- **Dataset:** FoodPuzzle benchmark — 978 food items, 1,766 flavor molecule profiles, derived from FlavorDB. Includes Molecule Prediction Challenge (MPC) tasks.
- **License:** CC BY-NC-ND 4.0 (paper); GitHub repository LICENSE file present (specific type requires direct inspection).
- **Currency:** Preprint September 2024; ACM KDD 2025 proceedings (published 2025).
- **Limitations:** Not a standalone model — requires a capable general-purpose LLM as backend. Research artifact; no production deployment. The benchmark is narrow (flavor molecule prediction), not broad culinary or nutrition reasoning.
- **Fit for NutriMe:** Moderate. The RAG-over-FlavorDB approach is directly applicable to a flavor-pairing module. The benchmark could serve as an evaluation harness. The "agent as flavor scientist" framing is a useful mental model for the recipe-generation layer.

---

### 1.4 FlavorDB / FlavorDB2

**Status: CONFIRMED — FlavorDB2 exists and is the current version**

- **Primary sources:** FlavorDB2 journal paper, *Journal of Food Science* 2024, vol. 89, pp. 7076–7082 ([Wiley](https://ift.onlinelibrary.wiley.com/doi/10.1111/1750-3841.17298)); arXiv [2205.05451](https://arxiv.org/abs/2205.05451) (preprint May 2022); hosted at IIIT-Delhi CosyLab: [cosylab.iiitd.edu.in/flavordb2](https://cosylab.iiitd.edu.in/flavordb2/how_to_use).
- **Correction to user-provided info:** The institution is IIIT-Delhi (Indraprastha Institute of Information Technology Delhi) / CosyLab, not IISER Pune. IISER Pune is associated with a different flavoromics line of work.
- **What it is:** A relational database of flavor molecules and their association with natural food ingredients.
- **Scale:** 25,595 flavor molecules total; 2,254 molecules associated with 936 natural ingredients across 34 categories. Each molecule entry includes: flavor profile, chemical properties, regulatory status, consumption statistics, taste/aroma thresholds, reported food-category uses, synthesis information.
- **License:** Freely accessible for non-commercial use; no registration required.
- **Currency:** Published in Journal of Food Science 2024; web interface actively maintained at IIIT-Delhi.
- **Fit for NutriMe:** High value as a reference dataset for a flavor-pairing module. Non-commercial license is acceptable for personal use. Can be queried or scraped for building a local flavor-pairing index; the FoodPuzzle project demonstrates exactly this pattern.

---

### 1.5 Epicure

**Status: CONFIRMED — exists, but narrower in scope than the user description implies**

- **Primary sources:** arXiv [2604.22776](https://arxiv.org/abs/2604.22776) (April 2026, "Multidimensional Flavor Structure in Food Ingredient Embeddings"); follow-on paper arXiv [2605.22391](https://arxiv.org/abs/2605.22391) (May 2026, "Navigating the Emergent Geometry of Food Ingredient Embeddings"); HuggingFace models [Kaikaku/epicure-cooc](https://huggingface.co/Kaikaku/epicure-cooc), [Kaikaku/epicure-core](https://huggingface.co/Kaikaku/epicure-core), dataset [Kaikaku/epicure-corpus-resources](https://huggingface.co/datasets/Kaikaku/epicure-corpus-resources).
- **Clarification:** Epicure is not a fine-tuned LLM or a multi-dimensional "tacit culinary knowledge" dataset in the sense of a QA corpus. It is a 300-dimensional skip-gram ingredient embedding trained on recipe co-occurrence from 4.14M recipes across 7 languages and 1,790 canonical ingredients. An LLM (Gemini 2.5 Flash) was used in the curation pipeline to normalize ingredient strings, but the output artifact is an embedding model, not a language model.
- **Key finding:** The embeddings encode at least 15 independently classifiable dimensions including taste (spiciness, bitterness), texture, geographic origin, processing state, and cultural association — dimensions that emerge from recipe co-occurrence alone without explicit chemistry signals.
- **License:** CC BY 4.0 (models and derived statistics on HuggingFace). The 4.14M source recipes cannot be redistributed (heterogeneous third-party licenses); only derived embeddings and aggregated statistics are released.
- **Currency:** April–May 2026, very recent; active development by authors Radzikowski and Chen.
- **Fit for NutriMe:** High value for an ingredient-pairing or flavor-recommendation module. The CC BY 4.0 license is fully permissive. At 2MB for 1,790 ingredients in 300 dimensions, it could be bundled directly into a local-first app. This is the most immediately practical flavor-embedding resource in this survey.

---

### 1.6 FoodEarth

**Status: CONFIRMED — mini version publicly available; full version encrypted**

- **Primary sources:** Zenodo [10.5281/zenodo.13836709](https://zenodo.org/records/13836709); described in detail in the FoodSky paper (arXiv 2406.10261 / Cell Patterns 2025).
- **What it is:** A Chinese-language food instruction dataset compiled from authoritative sources including e-books, websites, recipe corpora, and dietetic references. Used as the pre-training and fine-tuning corpus for FoodSky.
- **Scale:** Full corpus: 811,491 instruction entries across food-related topics. Public release: 20,000-instance mini version on Zenodo.
- **License:** The mini dataset on Zenodo is publicly downloadable; the full corpus is encrypted due to commercial conflicts with source publishers.
- **Currency:** Released alongside FoodSky in 2024.
- **Fit for NutriMe:** Limited for English-language use. Chinese-language corpus only. The mini version (20K) is too small for pre-training; could be used for a very narrow Chinese food QA fine-tune. The construction methodology (scraping authoritative e-books + multi-stage filtering) is worth replicating in English.

---

## Section 2 — Adjacent OSS Landscape

### 2.1 Recipe Generation Models and Datasets

**RecipeNLG**
- 2.23 million semi-structured recipes for recipe text generation, constructed by cleaning and augmenting Recipe1M+ web scrapes. Published INLG 2020. GitHub: [Glorf/recipenlg](https://github.com/Glorf/recipenlg); HuggingFace: [mbien/recipe_nlg](https://huggingface.co/datasets/mbien/recipe_nlg); also on Kaggle. License: not explicitly stated in retrieved results — check repo directly before commercial use.
- Practical status: Foundational dataset. Still the largest English-language recipe text corpus. Used as fine-tuning data in virtually every subsequent recipe-generation paper.

**Recipe1M+**
- 1M+ recipes with 800K food images; extended to 13M+ food images in Recipe1M+. Foundational academic dataset from MIT. Data access requires registration at the project website. Not a free/open license — check terms before use.

**LLaVA-Chef (arXiv 2408.16889)**
- Multi-modal recipe generation model extending LLaVA (Vicuna LLM + CLIP vision encoder). Multi-stage training on a curated diverse recipe prompt dataset. Outperforms GPT-4 on ingredient F1 (0.531 vs. 0.481 for GPT-4). Published August 2024. HuggingFace paper page: [2408.16889](https://huggingface.co/papers/2408.16889). Paper licensed CC BY 4.0. Model/code license requires direct repository inspection.

**FoodMLLM-JP (arXiv 2409.18459)**
- Fine-tunes LLaVA-1.5 and Phi-3 Vision on a Japanese recipe dataset. Demonstrates that domain fine-tuning of open MLLMs surpasses GPT-4o on ingredient generation for a non-English cuisine. Published via MultiMedia Modeling 2025 proceedings. September 2024 preprint. Relevant as a proof-of-concept for non-Western food domain fine-tuning.

**FoodLMM (arXiv 2312.14991)**
- Versatile food assistant based on large multi-modal model architecture (built on LISA). Handles food recognition, ingredient detection, segmentation, recipe generation, and nutritional estimation in a unified model with task-specific tokens and heads. Two-stage training on multiple public food benchmarks. GitHub: [YuehaoYin/FoodLMM](https://github.com/YuehaoYin/FoodLMM). IEEE published version available 2024. License requires direct inspection.

**KERL (arXiv 2505.14629, ACL 2025)**
- Knowledge-Enhanced Personalized Recipe Recommendation system combining food knowledge graphs with LLMs. Three-module pipeline: recommendation (KERL-Recom), recipe generation (KERL-Recipe), nutrition generation (KERL-Nutri). Uses LoRA fine-tuning. Given a natural language query, extracts entities, constructs SPARQL queries against a food KG, retrieves subgraphs, and feeds them to the LLM. GitHub: [mohbattharani/KERL](https://github.com/mohbattharani/KERL); datasets and benchmarks publicly available. Accepted ACL 2025. This is directly relevant to the "intake conversation + personalized recommendation" use case.

---

### 2.2 Food Knowledge Graphs and Ontologies

**FoodOn**
- Open-source ontology for food entities (ingredients, processing methods, animal/plant parts, derived products). Reuses AGRO, RO, and other OBO Foundry ontologies. Used as a linking target by FoodyLLM, FoodSEM, and others. Available at [foodon.org](https://foodon.org). OBO license (CC0 / open).

**FoodKG**
- Semantics-driven knowledge graph for food recommendation integrating FoodOn, Recipe1M+, and USDA nutrient records. WhatToMake ontology inside. Research artifact from RPI; not actively maintained as a service. Useful as an architecture reference.

**FoodSEM (arXiv 2509.22125)**
- Fine-tuned open-source LLM for food Named-Entity Linking (NEL) to FoodOn, SNOMED-CT, and Hansard taxonomy. Achieves F1 up to 98% on some ontologies. Resources (annotated corpora, model) publicly available per paper. September 2025. Published via Springer/LREC proceedings. Directly useful for the condition-gating layer (linking user-mentioned foods to controlled ontology terms).

**FoodOntoRAG (arXiv 2603.09758)**
- RAG-based approach for robust food entity linking under ontology drift. Complements FoodSEM. March 2026. Demonstrates that RAG can substitute for fine-tuning in entity linking when ontologies evolve.

**CookingSense (arXiv 2405.00523, LREC-COLING 2024)**
- Culinary knowledgebase built from web data, scientific papers, and recipes, filtered using dictionary + LM-based semantic filtering. Also introduces FoodBench, an evaluation benchmark for culinary decision support. Improves RAG-augmented LM performance on culinary queries. GitHub: [dmis-lab/cookingsense](https://github.com/dmis-lab/cookingsense). Published by Sony AI / DMIS Lab.

**AGROVOC**
- FAO multilingual agricultural thesaurus including extensive food vocabulary. Used as a linking vocabulary in FAIR food data projects. Freely available from FAO; SKOS format.

**USDA FoodData Central (FDC)**
- Not an LLM, but the canonical nutrient reference database for US foods. Public domain (CC0). REST API available at no cost ([fdc.nal.usda.gov](https://fdc.nal.usda.gov)). Recent development: an MCP server wrapping the FDC API (TypeScript, 2025) allows LLM agents to query FDC directly. An open-source Go implementation of the FDC API also exists ([littlebunch/fdc-api](https://github.com/littlebunch/fdc-api)).

---

### 2.3 Flavor Science Datasets

**FlavorDB2**
- See Section 1.4. Primary chemical flavor compound reference. 25,595 molecules, 936 ingredients. Non-commercial free access.

**FlavorNet**
- Cornell catalog of 783 aroma compounds with GC-olfactometry potency data and ASTM odor descriptors. Last updated 2004. Static academic resource at [acree.foodscience.cornell.edu/flavornet.html](http://acree.foodscience.cornell.edu/flavornet.html). Narrow (aroma only, no broader chemical or regulatory data). Partially mirrored in an informal GitHub repo [levi006/FlavorNet](https://github.com/levi006/FlavorNet).

**FlavorGraph**
- Large-scale food-chemical graph combining 1M+ recipe co-occurrence data with 1,500+ flavor molecule chemical data. Used to generate ingredient embeddings and recommend food pairings via link prediction (GNN). Academic artifact; no active production deployment. The Epicure project (Section 1.5) uses FlavorGraph embeddings as input.

**Leffingwell Flavor-Base (10th edition)**
- Commercial reference database of flavor and regulatory data for industry. Not open-source. Mentioned here as the source for several curated scientific datasets.

**Open Food Facts**
- Crowdsourced database of 3M+ food products with nutrition labels, ingredients, and product images. Open Database License (ODbL v1.0). HuggingFace organization: [openfoodfacts](https://huggingface.co/openfoodfacts) with datasets including product-database, nutrition-table-detection, and nutrient-detection-layout. Actively maintained. Excellent for training product-label parsing and nutrient extraction models.

---

### 2.4 Nutrition Q&A and Clinical Nutrition LLMs

**ChatDiet (arXiv 2403.00781, Smart Health 2024)**
- LLM-augmented framework for personalized nutrition-oriented food recommendation chatbots. Integrates personal model (individual user history) and population model (epidemiological evidence) via an orchestrator feeding context to an LLM. Achieves 92% food recommendation effectiveness rate. Published March 2024. Code release status unclear — check authors' repositories.

**GLEN-Bench (arXiv 2601.18106, January 2026)**
- First comprehensive graph-language benchmark for nutritional health. Combines NHANES health records, FNDDS food composition data, and USDA food-access metrics into a knowledge graph. Three linked tasks: population risk detection, personalized food recommendation (with socioeconomic constraints), and graph-grounded QA explanation. Addresses clinically realistic constraints (comorbidities, food access, poverty). High relevance for condition-aware nutrition reasoning.

**FAM-Bench (arXiv 2605.31410, May 2026)**
- Multimodal benchmark for condition-aware Food-as-Medicine reasoning. 2,500 nutrition-expert-verified instances across 13 diet-related health conditions. Two tasks: dish-level suitability assessment (given image + ingredient list, judge suitability for a condition) and comparative dish ranking. This is the most directly relevant benchmark for NutriMe's condition-gating use case.

**FoodGuardBench / FoodGuard-4B (arXiv 2604.01444, April 2026)**
- FoodGuardBench: first comprehensive food-safety LLM benchmark. 3,339 queries grounded in FDA guidelines. Reveals that current LLMs have sparse food-safety alignment and are vulnerable to jailbreak attacks. FoodGuard-4B: specialized guardrail model fine-tuned to detect unsafe food-related LLM outputs. Relevant for any production food advisory system.

**NGQA (arXiv 2412.15547)**
- Nutritional Graph Question Answering benchmark for personalized health-aware nutritional reasoning. Combines graph-structured nutrition data with natural language questions.

---

### 2.5 Additional Notable Work

**FooDB / ChemSpider Food Entries**
- FooDB (University of Alberta, part of the HMDB project) is the most comprehensive food constituent database: 70,926 compounds across 1,021 foods, with links to flavor, nutrition, and health data. Freely accessible at [foodb.ca](http://foodb.ca). Not LLM-specific but a foundational reference dataset for any food-chemistry reasoning layer.

**Epicure (extended, arXiv 2605.22391)**
- The May 2026 follow-on paper "Navigating the Emergent Geometry" extends the April paper's analysis into the geometry of the full 300-dimensional embedding space. Still CC BY 4.0. Represents the current frontier in compact, deployable flavor-chemistry embeddings.

---

## Section 3 — Synthesis

### What shape does this ecosystem actually have?

**The field is large, fragmented, and Chinese-first at the model level, but English-first at the data level.**

FoodSky is the most complete food-domain LLM with a published peer-reviewed evaluation (chef and dietetic exams), but its Chinese-language focus and CC BY-NC-ND license make it a reference architecture, not a deployable artifact for an English-language personal app. No equivalent English-language food-specialist LLM with peer-reviewed domain benchmarks currently exists as an OSS artifact.

FoodyLLM is the exception: it is English, MIT-licensed, based on Llama-3-8B-Instruct, and addresses structured nutrition tasks with dramatic accuracy gains. It is the closest thing to a "ready to use" food-domain LLM, though its task scope is narrow (classification and estimation, not dialogue or recipe generation).

**The emerging dominant pattern is RAG + KG + LoRA, not monolithic pre-training.**

Virtually every 2024–2026 paper — KERL, FoodyLLM, FoodSEM, ChatDiet, FoodOntoRAG — converges on the same architecture: take a general-purpose 7–13B base model (Llama-3 or Qwen2.5), add LoRA fine-tuning on a domain QA dataset of 50K–225K pairs, and augment at inference time with retrieval from a structured food knowledge source (FoodOn, FDC, FlavorDB2, recipe KG). Full food-domain pre-training (as in FoodSky's FoodEarth corpus) shows diminishing returns versus this lighter approach, and none of the full-pretraining efforts have released usable English artifacts.

**Flavor science is well-resourced at the data layer but thin at the model layer.**

FlavorDB2 (25K molecules, 936 ingredients), FlavorNet (783 aroma compounds), FlavorGraph (molecule + recipe co-occurrence), and the Epicure embeddings together constitute a rich flavor-chemistry information layer. FoodPuzzle demonstrates that a RAG pipeline over FlavorDB2 can replicate significant flavor-scientist reasoning. But there is no fine-tuned open model specifically for flavor reasoning — this remains a RAG problem, not a fine-tuning problem.

**Condition-aware nutrition reasoning is the fastest-moving frontier.**

FAM-Bench (May 2026), GLEN-Bench (January 2026), FoodGuardBench (April 2026), and NGQA (December 2025) all appeared within the last six months and collectively constitute the first rigorous evaluation infrastructure for health-condition-aware dietary AI. These benchmarks are important for NutriMe because they define what "good" looks like for the condition-gating module. No open model has yet been benchmarked against all of these simultaneously.

### Mature vs. emerging

**Mature (use now):**
- RecipeNLG / Recipe1M+ as training data
- USDA FDC as nutrient ground truth (CC0, REST API, MCP wrapper available)
- FlavorDB2 as flavor-molecule reference (non-commercial, web accessible)
- Open Food Facts as product-label training data (ODbL)
- FoodOn + FoodKG as ontology layer for entity linking
- FoodyLLM (MIT, Llama-3-8B) as the nutrient-estimation fine-tune reference

**Emerging (watch / evaluate):**
- Epicure embeddings — very new (April–May 2026) but immediately practical for flavor pairing; CC BY 4.0
- KERL — recipe recommendation + KG integration; ACL 2025, code public
- FoodSEM — food entity linking to FoodOn; September 2025
- FAM-Bench — condition-aware reasoning benchmark; May 2026
- FoodGuard-4B — food-safety guardrail; April 2026
- FoodOntoRAG — RAG-based entity linking under ontology drift; March 2026

**Hype / not confirmed:**
- The user's description of Epicure as a "multi-dimensional LLM-augmented dataset for tacit culinary knowledge" somewhat overstates it; it is a specialized ingredient embedding model, not a knowledge dataset or LLM.
- The claim that FoodSky base model is IISER Pune is incorrect; FoodSky is from the Chinese Academy of Sciences group. The IISER Pune confusion likely arises from a different flavoromics research group.
- There is no confirmed open-source English-language model equivalent to FoodSky's exam-passing performance. Claims about general-purpose LLMs "knowing nutrition" are largely unvalidated; the FoodyLLM paper's zero-shot baselines show Llama-3 and Gemini at 43–63% accuracy on nutrient estimation tasks.

### Practical recommendations for NutriMe

| Module | Best current OSS option | License | Gap |
|---|---|---|---|
| Nutrient estimation | FoodyLLM (Llama-3-8B-Instruct + LoRA) | MIT | English only; inference-time, not dialogue |
| Condition gating | Fine-tune Llama-3 on FAM-Bench / GLEN-Bench data | Benchmark: research license | No off-the-shelf model yet; benchmarks just published |
| Flavor pairing | Epicure embeddings + FlavorDB2 RAG | CC BY 4.0 / non-commercial | No dialogue wrapper yet |
| Recipe generation | LLaVA-Chef or FoodLMM as starting points | Check repos | Multi-modal adds complexity; text-only recipe gen is simpler |
| Intake conversation | General Llama-3/Qwen2.5 + KERL-style KG augmentation | Llama/Apache | No food-specific conversational model exists in OSS |
| Food entity linking | FoodSEM (fine-tuned for FoodOn/SNOMED) | Check repo | Very recent; production-readiness unknown |
| Safety guardrail | FoodGuard-4B | Check repo | April 2026; very new |

The most defensible short-term architecture for NutriMe is: Llama-3-8B-Instruct or Qwen2.5-7B as base, LoRA fine-tuned on a curated mix of FoodyLLM-style QA + KERL-style recipe-nutrition pairs + FAM-Bench condition-aware examples, with FlavorDB2 and USDA FDC as RAG sources at inference time. This avoids the need for expensive full pre-training (as in FoodSky), does not require proprietary data, and stays within the MIT / Apache / CC0 license stack.

---

## Section 4 — Sources

### Part 1 — Named Projects

- [FoodSky arXiv 2406.10261](https://arxiv.org/abs/2406.10261)
- [FoodSky — Cell Patterns 2025 (peer review)](https://www.sciencedirect.com/science/article/pii/S2666389925000820)
- [FoodSky — GitHub LanceZPF/FoodSky](https://github.com/LanceZPF/FoodSky)
- [FoodEarth + FoodSky — Zenodo 13836709](https://zenodo.org/records/13836709)
- [FoodyLLM — ScienceDirect 2026](https://www.sciencedirect.com/science/article/pii/S2665927126000511)
- [FoodyLLM — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12927182/)
- [FoodyLLM — PubMed](https://pubmed.ncbi.nlm.nih.gov/41737890/)
- [FoodyLLM — HuggingFace Matej/FoodyLLM](https://huggingface.co/Matej/FoodyLLM)
- [FoodyLLM — GitHub matejMartinc/FoodyLLM](https://github.com/matejMartinc/FoodyLLM)
- [FoodPuzzle arXiv 2409.12832](https://arxiv.org/abs/2409.12832)
- [FoodPuzzle — ACM KDD 2025](https://dl.acm.org/doi/10.1145/3711896.3737384)
- [FoodPuzzle — GitHub tenghaohuang/FoodPuzzle](https://github.com/tenghaohuang/FoodPuzzle)
- [FlavorDB2 — Journal of Food Science 2024 (Wiley)](https://ift.onlinelibrary.wiley.com/doi/10.1111/1750-3841.17298)
- [FlavorDB2 — arXiv 2205.05451](https://arxiv.org/abs/2205.05451)
- [FlavorDB2 — IIIT-Delhi CosyLab](https://cosylab.iiitd.edu.in/flavordb2/how_to_use)
- [Epicure arXiv 2604.22776](https://arxiv.org/abs/2604.22776)
- [Epicure follow-on arXiv 2605.22391](https://arxiv.org/abs/2605.22391)
- [Epicure — HuggingFace epicure-cooc](https://huggingface.co/Kaikaku/epicure-cooc)
- [Epicure — HuggingFace epicure-core](https://huggingface.co/Kaikaku/epicure-core)
- [Epicure — HuggingFace corpus resources dataset](https://huggingface.co/datasets/Kaikaku/epicure-corpus-resources)

### Part 2 — Adjacent OSS Landscape

- [RecipeNLG — ACL Anthology INLG 2020](https://aclanthology.org/2020.inlg-1.4/)
- [RecipeNLG — GitHub Glorf/recipenlg](https://github.com/Glorf/recipenlg)
- [RecipeNLG — HuggingFace mbien/recipe_nlg](https://huggingface.co/datasets/mbien/recipe_nlg)
- [LLaVA-Chef arXiv 2408.16889](https://arxiv.org/abs/2408.16889)
- [LLaVA-Chef — HuggingFace paper page](https://huggingface.co/papers/2408.16889)
- [FoodMLLM-JP arXiv 2409.18459](https://arxiv.org/abs/2409.18459)
- [FoodLMM arXiv 2312.14991](https://arxiv.org/abs/2312.14991)
- [FoodLMM — GitHub YuehaoYin/FoodLMM](https://github.com/YuehaoYin/FoodLMM)
- [KERL arXiv 2505.14629](https://arxiv.org/abs/2505.14629)
- [KERL — GitHub mohbattharani/KERL](https://github.com/mohbattharani/KERL)
- [FoodOn — foodon.org](https://foodon.org)
- [FoodSEM arXiv 2509.22125](https://arxiv.org/abs/2509.22125)
- [FoodOntoRAG arXiv 2603.09758](https://arxiv.org/html/2603.09758)
- [CookingSense arXiv 2405.00523](https://arxiv.org/abs/2405.00523)
- [CookingSense — GitHub dmis-lab/cookingsense](https://github.com/dmis-lab/cookingsense)
- [USDA FoodData Central API](https://fdc.nal.usda.gov/)
- [FDC open-source REST API — GitHub littlebunch/fdc-api](https://github.com/littlebunch/fdc-api)
- [ChatDiet arXiv 2403.00781](https://arxiv.org/abs/2403.00781)
- [GLEN-Bench arXiv 2601.18106](https://arxiv.org/abs/2601.18106)
- [FAM-Bench arXiv 2605.31410](https://arxiv.org/abs/2605.31410)
- [Cooking Up Risks / FoodGuardBench arXiv 2604.01444](https://arxiv.org/abs/2604.01444)
- [NGQA arXiv 2412.15547](https://arxiv.org/pdf/2412.15547)
- [Open Food Facts — HuggingFace openfoodfacts/product-database](https://huggingface.co/datasets/openfoodfacts/product-database)
- [Open Food Facts — data portal](https://world.openfoodfacts.org/data)
- [FlavorNet — Cornell](http://acree.foodscience.cornell.edu/flavornet.html)
- [FlavorNet — GitHub levi006/FlavorNet](https://github.com/levi006/FlavorNet)
- [Food Data Semantic Web review arXiv 2509.00986](https://arxiv.org/html/2509.00986v1)
