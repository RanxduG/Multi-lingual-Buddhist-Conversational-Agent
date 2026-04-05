# Multilingual Buddhist Conversational Agent

A domain-adapted conversational model for Sinhala Buddhist scripture, built on top of Llama-3.1-8B-Instruct with QLoRA fine-tuning and a RAG pipeline grounded in the Theravada Tripitaka.

Submitted as a final year project for BSc (Hons) Artificial Intelligence and Data Science at Robert Gordon University, Aberdeen, UK.

**Author:** Ranidu Hansaka Gurusinghe  
**Supervisor:** Nevidu Jayatilleke  
**Institution:** Informatics Institute of Technology, Sri Lanka  

---

## Overview

Sinhala is a Category 2 low-resource language spoken by approximately 17 million people. Classical Buddhist Sinhala is even harder, the Theravada Tripitaka is written in a code-mixed register of Sinhala prose and Pali verses, a domain that no existing language model has ever seen.

This project addresses that gap through three coordinated contributions:

1. **SiPaKosa Corpus** — The first large-scale Sinhala and Pali Buddhist corpus: 786,344 sentences and 9.25M tokens, sourced from the IFBC digital archive and the Sutta Piṭaka from tripitaka.online.
2. **Domain-Adapted LLM** — Llama-3.1-8B-Instruct fine-tuned with QLoRA on a bilingual Buddhist QA dataset generated and quality-controlled by a 5-node LangGraph agentic pipeline.
3. **Multi-Dimensional Evaluation Framework** — A four-metric framework (Token Recall, K-Precision, Language Consistency, BERTScore F1) designed specifically for religious-domain QA beyond standard lexical metrics.

The fine-tuned model achieves **79.0% Sinhala language consistency** (+64.4 percentage points over base), and outperforms the unmodified LLaMA-3.1-8B-Chat on the SinhalaMMLU Buddhism-only subset.

---

## Published Resources

The SiPaKosa corpus produced during this project is publicly available:

- **HuggingFace Dataset:** [RaniduG/SiPaKosa](https://huggingface.co/datasets/RaniduG/SiPaKosa)
- **Dataset Repository:** [github.com/RanxduG/SiPaKosa-Dataset](https://github.com/RanxduG/SiPaKosa-Dataset)
- **arXiv Preprint:** [arxiv.org/abs/2603.29221](https://arxiv.org/abs/2603.29221)

```bibtex
@misc{gurusinghe2026sipakosacomprehensivecorpuscanonical,
      title={SiPaKosa: A Comprehensive Corpus of Canonical and Classical Buddhist Texts in Sinhala and Pali},
      author={Ranidu Gurusinghe and Nevidu Jayatilleke},
      year={2026},
      eprint={2603.29221},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2603.29221},
}
```

---

## Key Results

| Metric | Base Model | Fine-Tuned (IFT) | IFT + RAG |
|---|---|---|---|
| Sinhala Language Consistency | 14.6% | 79.0% | 79.0% |
| Token Recall | — | — | — |
| BERTScore F1 | — | — | — |
| SinhalaMMLU Buddhism Accuracy | 25.76% | above baseline | — |

Fine-tuning and retrieval address **complementary failure modes**: fine-tuning provides the linguistic register; RAG prevents doctrinal hallucination.

---

## System Architecture

The full pipeline runs in four phases:

```
Raw Sources (IFBC PDFs + tripitaka.online)
        |
        v
Corpus Construction (OCR, cleaning, language classification)
        |
        v
QA Dataset Generation (Three-Pillar framework, LangGraph QA pipeline)
        |
        v
Instruction Fine-Tuning (Llama-3.1-8B-Instruct + QLoRA)
        |
        v
RAG Pipeline (FAISS vector index + fine-tuned generator)
        |
        v
Evaluation (Token Recall, K-Precision, Language Consistency, BERTScore)
```

**Data sources:**
- IFBC digital archive — 16 copyright-cleared Sinhala Buddhist books
- tripitaka.online — Full Sutta Pitaka (Sinhala rendering)

**QA Generation:**
- Three-Pillar automatic generation framework
- 14,494 raw bilingual QA pairs generated
- 4,874 approved after LangGraph agentic quality pipeline (doctrinal accuracy, source grounding, Sinhala naturalness)

**Fine-Tuning:**
- Base model: `meta-llama/Meta-Llama-3.1-8B-Instruct` (4-bit NF4 via QLoRA)
- Hardware: RTX 4090 (24 GB VRAM)
- LoRA applied to attention weight matrices

**Retrieval:**
- Dense Passage Retrieval (DPR) backbone
- FAISS vector index over the Sutta Pitaka corpus

---

## Tech Stack

| Component | Tool |
|---|---|
| Base LLM | Llama-3.1-8B-Instruct |
| Fine-Tuning | QLoRA (via PEFT + bitsandbytes) |
| Training Framework | HuggingFace Transformers, TRL |
| RAG / Retrieval | FAISS, LangChain |
| QA Pipeline | LangGraph |
| OCR | Google Document AI |
| Language | Python |

---

## Scope

This project covers:
- Theravada Buddhism only (not Mahayana or Vajrayana)
- Two canonical data sources: IFBC archive and tripitaka.online
- Sutta Pitaka only (Vinaya and Abhidhamma Pitakas are future work)
- Automatic evaluation only (no human annotators)

---

## Limitations and Future Work

- The QA dataset is limited to Pillar 1 (context-grounded pairs) for the full quality pipeline due to API cost constraints
- Continual pre-training caused catastrophic forgetting and was excluded from the final pipeline
- No human evaluation of doctrinal correctness was performed

Planned future directions:
- Scale and diversify the QA dataset across all three pillars
- Expert human evaluation by qualified Theravada practitioners
- Trained Sinhala-Pali language classifier
- Cross-lingual retrieval for mixed-script passages
- Extension to Vinaya and Abhidhamma Pitakas
- Adaptive-RAG and Tree-of-Question routing for multi-hop doctrinal queries
- Public deployment as a free accessible app

---

Thanks to IFBC and tripitaka.online for making digitised Buddhist texts publicly accessible.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

Corpus data (SiPaKosa) is released separately under its own license. See the [SiPaKosa Dataset Repository](https://github.com/RanxduG/SiPaKosa-Dataset) for details.