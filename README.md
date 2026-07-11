# README

## Overview

This repository evaluates the **commitment consistency** of two large language models on the **ARC-Challenge** dataset.

The workflow consists of four main steps:

1. Generate answers and explanations from the LLMs.
2. Manually annotate the explicit commitments contained in each explanation.
3. Ask each model whether it agrees with the commitments extracted from **its own** explanations.
4. Aggregate the results and compute commitment consistency statistics.

Each commitment is judged by the **same model that originally produced the explanation**, allowing us to measure the model's internal consistency.

---

# Models

* Llama 3.1 8B Instruct (`meta-llama/llama-3.1-8b-instruct`)
* Qwen 2.5 7B Instruct (`qwen/qwen-2.5-7b-instruct`)

# Dataset

* ARC-Challenge (`allenai/ai2_arc`)

---

# Installation

Install the project dependencies.

```bash
uv sync
```

Create a `.env` file in the project root containing your OpenRouter API key:

```text
OPENROUTER_API_KEY=your_api_key_here
```

---

# Repository structure

```
annotations/
    Human commitment annotations

outputs/explanations/
    Generated model answers and explanations

outputs/judgments/
    Commitment consistency judgments

outputs/stats/
    Computed statistics results

scripts/
    Scripts for generation, judging, and analysis
```

---

# Annotation Guidelines

Follow the annotation guidelines provided here:

https://docs.google.com/document/d/1BzEw2V8cb-p7db6rx9n2tyMyRkpaBVOcmUA23N688jE/edit?usp=sharing

---

# Prompting Strategy

## Answer Extraction

Models are first prompted to return only the answer label.

```text
Answer the following multiple choice question.
Reply with ONLY the letter of the correct answer (A, B, C, or D).
```

## Explanation Generation

After selecting an answer, the model is prompted to justify its choice.

```text
Explain your reasoning in clear sentences.
Do not repeat the answer letter, but justify your choice.
```

## Commitment Consistency Judgment

For each annotated commitment, the corresponding model is prompted to judge whether the statement is true or false in isolation using the following prompt:

```text
Decide whether the following statement is factually TRUE or FALSE.

Judge the statement in isolation.
Do not judge spelling or grammar.

Statement:
{statement}

Reply with ONLY one word:
TRUE or FALSE
```

---

# Generation Parameters

| Parameter                | Value |
| ------------------------ | ----: |
| Temperature              | 0.001 |
| Max tokens (answer)      |     5 |
| Max tokens (explanation) |   120 |

---

# Step 1 – Generate Explanations

Run

```bash
python scripts/answer_gen.py
```

This script:

* downloads the selected ARC-Challenge questions,
* queries each model,
* stores the answers and explanations.

### Configuration

To change the output filename:

```python
OUTPUT_FILE = "llm_answer.csv"
```

To select which questions are processed:

```python
START = 0          # Starting question index (0-based)
N_QUESTIONS = 600  # Number of questions to process
```

The generated explanations are saved to

```
outputs/explanations/
```

---

# Step 2 – Annotate Commitments

Open the generated CSV file and annotate the explicit commitments made in each explanation.

Each annotation cell should contain **all explicit commitments for one question**.

Each commitment should be written as a separate sentence and separated by a period (`.`).

Example:

```
Copper is a good conductor of electricity.
Copper has free electrons that can move freely within its structure.
Wood is an insulator.
```

After annotation, place the completed CSV file inside

```
annotations/
```

---

# Step 3 – Run Commitment Consistency Judgments

Open `scripts/judging_commitments.py` and set

```python
INPUT_FILE = "your_annotations_file.csv"
```

If your annotation column names differ from the defaults

```python
ANNOTATION_COLUMNS = {
    "llama": "llama_annotations",
    "qwen": "qwen_annotations",
}
```

update them accordingly.

Run

```bash
python scripts/judging_commitments.py
```

The script splits each annotated explanation into individual commitments and prompts the same model that originally generated the explanation to judge each commitment independently using the prompt above. The resulting judgments are saved to

```
outputs/judgments/
```

---

# Step 4 – Compute Statistics

Run

```bash
python scripts/analyze.py
```

This script automatically processes **all judgment CSV files** found in

```
outputs/stats/
```

and computes

* truth rate for each LLM,
* truth rate conditioned on answer correctness,
* per-question statistics,
* counts and rates of false statements,
* per-file statistics that combine results from multiple annotators.

The resulting statistics are summarized in `Our_Analysis.md`.
