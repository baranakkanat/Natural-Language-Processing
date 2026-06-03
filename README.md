# README

## Models

* Llama 3.1 8B Instruct (`meta-llama/llama-3.1-8b-instruct`)
* Qwen 2.5 7B Instruct (`qwen/qwen-2.5-7b-instruct`)

## Dataset

* ARC-Challenge (`allenai/ai2_arc`)
* First 20 examples from the training split were used.

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
