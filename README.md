# Consistent Explanations — NLP with Deep Learning Project

## Overview

This project investigates whether LLMs are self-consistent in their explanations. When a model answers a question and explains its reasoning, the explanation makes **commitments** — claims about facts, rules, or reasoning principles. We measure whether the model still agrees with those commitments when probed out of context.

## Pipeline

```
Question → LLM Answer + Explanation
              ↓
    Commitment Extraction
    (explicit / implicit / logical_principle)
              ↓
    Out-of-context Probing (yes/no)
              ↓
    Consistency Score
```

## Files

| File | Description |
|------|-------------|
| `Pipeline.py` | Full pipeline: answer generation + extraction + probing |
| `Multi_model_pipeline.py` | Compare consistency across multiple models |
| `Pilot_set_generator.py` | Generate pilot set from TriviaQA |
| `Benchmark.py` | Run benchmark on pilot set, per-category analysis |
| `Commitment_extractor.py` | Extract commitments from explanations |
| `Probing.py` | Probe commitments with yes/no |
| `pilot_set.json` | 19-example manually curated pilot set |
| `annotation_guidelines.md` | Guidelines for human annotation |

## Results

### Benchmark (Llama 3.3 70B, 19 examples)

| Category | Consistency |
|----------|-------------|
| Explicit | 91.67% |
| Implicit | 90.20% |
| Logical Principle | 97.37% |
| **Overall** | **92.43%** |

### Multi-model Comparison

| Model | Consistency |
|-------|-------------|
| Llama 3.3 70B | ~92% |
| Llama 3.1 8B | ~83% |
| Qwen3 32B | ~60% |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install groq python-dotenv datasets requests
```

Create a `.env` file:
```
GROQ_API_KEY=your_key_here
```

## Usage

```bash
# Run full pipeline on TriviaQA questions
python3 -u Pipeline.py

# Compare multiple models
python3 -u Multi_model_pipeline.py

# Generate pilot set
python3 -u Pilot_set_generator.py

# Run benchmark on pilot set
python3 -u Benchmark.py
```

## Dataset

Questions from [TriviaQA](https://huggingface.co/datasets/trivia_qa) (unfiltered.nocontext, validation split).

## Related Papers

1. Parcalabescu & Frank (ACL 2024) — [On Measuring Faithfulness or Self-Consistency of Natural Language Explanations](https://aclanthology.org/2024.acl-long.329/)
2. Admoni et al. (ACL Findings 2026) — [Aligning What LLMs Do and Say](https://arxiv.org/abs/2506.07523v3)
3. Turpin et al. (2023) — [Language Models Don't Always Say What They Think](https://arxiv.org/abs/2305.04388)