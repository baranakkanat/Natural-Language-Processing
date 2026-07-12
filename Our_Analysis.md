# Results and Analysis

#### Group 14: Katarzyna Kapuscinska (s4723708) and Mekhola Doha (s4790650)

#### Date: 10/07/2026

This analysis is based on 2,347 commitments extracted from the explanations for answers given by the Llama and Qwen models to questions 121–270 of the ARC-Challenge dataset.  Nine questions (IDs: 149, 156, 159, 163, 175, 183, 206, 225 and 255) were excluded based on the annotators' judgment of relevance. To assess the consistency of each model, we asked the respective model whether it agreed with the commitments extracted from its own explanations.

The following tables present the percentage of extracted commitments that the coresponding model judged to be true.

## Truth Rate by LLM

| LLM   | Questions | Statements | True Statements | Truth Rate |
| ----- | --------: | ---------: | --------------: | ---------: |
| Llama |       141 |      1,219 |           1,088 | **89.25%** |
| Qwen  |       141 |      1,128 |             937 | **83.07%** |

## Truth Rate by LLM and Answer Correctness

| LLM   | Answer Correct | Questions | Statements | True Statements | Truth Rate |
| ----- | -------------- | --------: | ---------: | --------------: | ---------: |
| Llama | Yes            |       117 |      1,015 |             921 | **90.74%** |
| Llama | No             |        24 |        204 |             167 | **81.86%** |
| Qwen  | Yes            |       124 |      1,003 |             837 | **83.45%** |
| Qwen  | No             |        17 |        125 |             100 | **80.00%** |

We observed a moderately high consistency rate for both models. Llama achieved a slightly higher truth rate of 89.25% than Qwen, which had a truth rate of 83.07%. For both models, the truth rate was higher when the original answer was correct than when it was incorrect. This difference was more pronounced for Llama (90.74% vs. 81.86%) than for Qwen (83.45% vs. 80.00%). Therefore, in these experiments, when a model's original answer was correct, it was more likely to agree with the commitments extracted from its explanation.

---

#### Baran Akkanat (s6388434)

#### Date: 12/07/2026

This analysis is based on 649 commitments extracted from the explanations for answers given by the Llama and Qwen models to questions 421–470 of the ARC-Challenge dataset. No questions were excluded. To assess the consistency of each model, we asked the respective model whether it agreed with the commitments extracted from its own explanations.

The following tables present the percentage of extracted commitments that the corresponding model judged to be true.

## Truth Rate by LLM

| LLM   | Questions | Statements | True Statements | Truth Rate |
| ----- | --------: | ---------: | --------------: | ---------: |
| Llama |        50 |        333 |             292 | **87.69%** |
| Qwen  |        50 |        316 |             255 | **80.70%** |

## Truth Rate by LLM and Answer Correctness

| LLM   | Answer Correct | Questions | Statements | True Statements | Truth Rate |
| ----- | -------------- | --------: | ---------: | --------------: | ---------: |
| Llama | Yes            |        37 |        255 |             232 | **90.98%** |
| Llama | No             |        13 |         78 |              60 | **76.92%** |
| Qwen  | Yes            |        41 |        251 |             206 | **82.07%** |
| Qwen  | No             |         9 |         65 |              49 | **75.38%** |

Consistent with the results reported for questions 121–270, both models showed a moderately high consistency rate. Llama achieved a higher truth rate of 87.69% than Qwen at 80.70%. For both models, the truth rate was higher when the original answer was correct than when it was incorrect. This difference was more pronounced for Llama (90.98% vs. 76.92%) than for Qwen (82.07% vs. 75.38%). Therefore, as in the earlier range, when a model's original answer was correct it was more likely to agree with the commitments extracted from its own explanation.