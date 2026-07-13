# Annotation Guidelines

This document describes the guidelines used for annotating commitments in model-generated explanations. The goal of annotation is to extract the individual factual commitments made by the model in its explanation.

## What is a Commitment?

Commitments are statements expressed in the model's explanation, either directly or through a close paraphrase. When a commitment contains multiple facts, it should be decomposed into standalone atomic commitments whenever possible.

---

## General Annotation Guidelines

### 1. Keep commitments atomic

Long reasoning chains should be split into individual atomic commitments.

However, avoid **over-splitting**, as this may remove important context.

**Example**

Instead of extracting:

> ACL is a venue.

retain enough context for the statement to be meaningfully evaluated.

---

### 2. Preserve the original order

Commitments should be extracted in the same order that they appear in the explanation.

This helps reduce missed statements and makes annotation more consistent.

---

### 3. Minimize conjunctions

Whenever possible, avoid conjunctions such as:

- and
- which
- but

Instead, split compound statements into separate commitments.

---

### 4. Reuse defined terms

If a commitment introduces a definition, subsequent commitments should refer to the defined term rather than using pronouns or determiners.

---

### 5. Annotate with full context

Annotators should always have access to:

- the original question, and
- all answer options.

Without this information, certain commitments cannot be recovered.

For example:

> "CVPR does not focus on NLP."

may only be inferable after considering the alternative answer choices.

---

### 6. Multiple-choice questions
For questions in which evaluating the incorrect answer options is necessary to justify the correct answer (e.g., *"Which is the best..."*), commitments about the eliminated alternatives should also be annotated when they are expressed or required by the explanation.