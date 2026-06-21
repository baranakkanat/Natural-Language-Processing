# README


## Models

* Llama 3.1 8B Instruct (`meta-llama/llama-3.1-8b-instruct`)
* Qwen 2.5 7B Instruct (`qwen/qwen-2.5-7b-instruct`)

## Dataset

* ARC-Challenge (`allenai/ai2_arc`)

## Prompting Strategy

###  Answer Extraction

Models were prompted to return only the answer label using the prompt below: 

```
Answer the following multiple choice question.
Reply with ONLY the letter of the correct answer (A, B, C, or D).
```

###  Explanation Generation

After the models gave an answer they were prompted to justify their answer choice using the prompt below:

```
Explain your reasoning in clear sentences.
Do not repeat the answer letter, but justify your choice.
```

## Parameters that were used for the first set of annotations 

| Parameter                | Value |
| ------------------------ | ----- |
| Temperature              | 0.001 |
| Max tokens (answer)      | 5     |
| Max tokens (explanation) | 120   |




Results are saved to:

```
outputs/llm_answer.csv
```


# Instruction for annotaters - Running Commitment Consistency Judgments

## 1. Add your annotation file

After annotating explicit commitments, place your annotation CSV file in the `annotations/` folder.

## 2. Configure `judging_comitments.py`

Open `scripts/judging_comitments.py` and change:

```python
INPUT_FILE = "your_annotations_file.csv"
```

to the name of the file you just added to the `annotations/` folder.

If your annotation columns use different names than the defaults

```python
ANNOTATION_COLUMNS = {
    "llama": "llama_annotations",
    "qwen": "qwen_annotations",
}
```

update the dictionary accordingly.

## 3. Annotation format

The annotation columns should contain all explicit commitments for a question in a **single cell**. Each commitment must be written as a separate sentence and separated by a period (`.`).

Example:

```
Copper is a good conductor of electricity. Copper has free electrons that can move freely within its structure. Wood is an insulator.
```

## 4. Run the judgment script

Run:

```bash
python scripts/judging_comitments.py
```

The script will:

* Split each annotation cell into individual statements.
* Ask the corresponding model to judge each statement in isolation:
* Save the results to:

```
outputs/judgments/
```

## 5. Update statistics

After all desired judgment files have been generated, run:

```bash
python scripts/analyze_judgments.py
```

This script automatically processes **all judgment CSV files** in `outputs/judgments/` and updates the aggregate statistics, including:

* Truth rate for each LLM.
* Truth rate conditioned on whether the original answer was correct or incorrect.
* Per-question statistics.
* Counts and rates of false statements.
* Per-file statistics, allowing results from multiple annotators to be combined automatically.
