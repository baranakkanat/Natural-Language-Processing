import os
import csv
import time
from openai import OpenAI
from dotenv import load_dotenv
from datasets import load_dataset

# ------------------------------------------------------------
# Settings CHANGE ONLY HERE
# ------------------------------------------------------------
OUTPUT_FILE = "big_annotation_results_with_options.csv"
# output path → outputs/explanations/llm_answer.csv


START = 0 # Question index to start from (0-based)
N_QUESTIONS = 600 # Number of questions to process

# ─────────────────────────────────────────────────────────────
# Load environment variables
# ─────────────────────────────────────────────────────────────

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY not found. Put your OpenRouter token in a .env file."
    )

# Initialize the OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# ─────────────────────────────────────────────────────────────
# Models required by the assignment
# (Using OpenRouter's free tier endpoints)
# ─────────────────────────────────────────────────────────────

MODELS = {
    "llama": "meta-llama/llama-3.1-8b-instruct",
    "qwen": "qwen/qwen-2.5-7b-instruct",
}

# ─────────────────────────────────────────────────────────────
# Load ARC-Challenge dataset
# ─────────────────────────────────────────────────────────────

print("Loading ARC-Challenge dataset...")

arc = load_dataset(
    "allenai/ai2_arc",
    "ARC-Challenge",
    split="train"
)

# ─────────────────────────────────────────────────────────────
# Select 20 examples
# ─────────────────────────────────────────────────────────────

QUESTIONS = []

for item in arc.select(range(START, START + N_QUESTIONS)):
    choices = dict(
        zip(item["choices"]["label"], item["choices"]["text"])
    )

    QUESTIONS.append(
        (
            item["question"],
            choices,
            item["answerKey"]
        )
    )

# ─────────────────────────────────────────────────────────────
# Preview questions
# ─────────────────────────────────────────────────────────────

print("\nLoaded Questions:\n")

for i, (q, choices, answer) in enumerate(QUESTIONS):
    print(f"\n── Q{i+1} (correct: {answer}) ──")
    print(q)

    for k, v in choices.items():
        print(f"  {k}) {v}")

# ─────────────────────────────────────────────────────────────
# Prompt formatting
# ─────────────────────────────────────────────────────────────


def format_question(question, choices):
    choices_text = "\n".join(
        f"{k}) {v}" for k, v in choices.items()
    )

    return f"{question}\n\n{choices_text}"

# ─────────────────────────────────────────────────────────────
# Query OpenRouter
# ─────────────────────────────────────────────────────────────


def query_openrouter(model_id, prompt, max_new_tokens=100):
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_new_tokens,
            temperature=0,
            # OpenRouter recommends these headers for logging
            extra_headers={
                "HTTP-Referer": "https://github.com/annotation-project",
                "X-Title": "ARC Annotation Script",
            }
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"OpenRouter API Error: {str(e)}")

# ─────────────────────────────────────────────────────────────
# Ask model: Answer only, then explain briefly
# ─────────────────────────────────────────────────────────────


def ask_model(model_id, question, choices):

    formatted_question = format_question(question, choices)

    # Step 1: answer only
    step1_prompt = (
        "Answer the following multiple choice question.\n"
        "Reply with ONLY the letter of the correct answer "
        "(A, B, C, or D).\n\n"
        f"{formatted_question}"
    )

    raw_answer = query_openrouter(
        model_id,
        step1_prompt,
        max_new_tokens=5
    )

    raw_answer = raw_answer.strip().upper()

    valid_labels = set(choices.keys())

    answer = next(
        (c for c in raw_answer if c in valid_labels),
        "?"
    )

    # Step 2: explanation
    step2_prompt = (
        step1_prompt
        + f"\n\nAnswer: {answer}\n\n"
        + "Explain your reasoning in clear sentences. Do not repeat the answer letter, but justify your choice."
    )

    explanation = query_openrouter(
        model_id,
        step2_prompt,
        max_new_tokens=120
    )

    return answer, explanation

# ─────────────────────────────────────────────────────────────
# Main annotation loop
# ─────────────────────────────────────────────────────────────


def run_annotation():

    results = []

    for i, (question, choices, correct) in enumerate(QUESTIONS):

        print(
            f"\n── Question {i+1}/{len(QUESTIONS)} "
            "──────────────────────"
        )

        print(question[:100] + "...")

        row = {
            "question_id": i + 1,
            "question": question,
            "correct_answer": correct,
        }
        row["options"] = "\n".join(f"{k}. {v}" for k, v in choices.items())

        for model_name, model_id in MODELS.items():

            print(f"  Querying {model_name}...")

            try:

                answer, explanation = ask_model(
                    model_id,
                    question,
                    choices
                )

                row[f"{model_name}_answer"] = answer
                row[f"{model_name}_explanation"] = explanation

                row[f"{model_name}_correct"] = (
                    "YES" if answer == correct else "NO"
                )

                print(
                    f"  {model_name}: {answer} "
                    f"({'✓' if answer == correct else '✗'})"
                )

            except Exception as e:

                print(f"  ERROR with {model_name}: {e}")

                row[f"{model_name}_answer"] = "ERROR"
                row[f"{model_name}_explanation"] = str(e)
                row[f"{model_name}_correct"] = "ERROR"

            # OpenRouter free tier has rate limits, keep a small pause
            time.sleep(3)

        # Manual annotation notes
        row["notes"] = ""

        results.append(row)

    # ─────────────────────────────────────────────────────────
    # Save results
    # ─────────────────────────────────────────────────────────

    output_file = "outputs/explenations/" + OUTPUT_FILE

    fieldnames = [
        "question_id",
        "question",
        "options",
        "correct_answer",

        "llama_answer",
        "llama_explanation",
        "llama_correct",

        "qwen_answer",
        "qwen_explanation",
        "qwen_correct",

        "notes"
    ]

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    # ─────────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────────

    llama_correct = sum(
        1 for r in results
        if r["llama_correct"] == "YES"
    )

    qwen_correct = sum(
        1 for r in results
        if r["qwen_correct"] == "YES"
    )

    print("\n✓ Done!")
    print(f"Results saved to: {output_file}")

    print(
        f"\nLlama accuracy: "
        f"{llama_correct}/{len(results)}"
    )

    print(
        f"Qwen accuracy: "
        f"{qwen_correct}/{len(results)}"
    )

# ─────────────────────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────────────────────


if __name__ == "__main__":
    run_annotation()
