import os
import json
import random
from groq import Groq
from dotenv import load_dotenv
from datasets import load_dataset

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODELS = {
    "llama-3.3-70b": "llama-3.3-70b-versatile",
    "llama-3.1-8b": "llama-3.1-8b-instant",
    "qwen3-32b": "qwen/qwen3-32b",
}

# ── Prompts ────────────────────────────────────────────────────────────────────

ANSWER_PROMPT = """Answer the following question and explain your reasoning clearly.

Question: {question}

Respond in this exact format:
Answer: <your answer>
Explanation: <your explanation>"""

EXTRACTION_PROMPT = """You are an expert at analyzing explanations and extracting commitments.

Given a Question, Answer, and Explanation, extract all commitments the explanation makes.
Commitments fall into three categories:
- explicit: directly stated facts
- implicit: facts that are implied but not directly stated
- logical_principle: general rules or reasoning principles used

Return ONLY a JSON object in this exact format, no other text:
{{
  "explicit": ["commitment 1", "commitment 2"],
  "implicit": ["commitment 1", "commitment 2"],
  "logical_principle": ["principle 1", "principle 2"]
}}

Question: {question}
Answer: {answer}
Explanation: {explanation}"""

PROBING_PROMPT = """Answer with only 'yes' or 'no'. Do not think or explain. Just answer yes or no.


Statement: {commitment}

Answer:"""

# ── TriviaQA ───────────────────────────────────────────────────────────────────

def fetch_triviaqa(n: int = 5) -> list:
    print(f"Fetching {n} questions from TriviaQA...")
    dataset = load_dataset("trivia_qa", "unfiltered.nocontext", split="validation")
    indices = random.sample(range(len(dataset)), n)
    questions = []
    for i in indices:
        row = dataset[i]
        q = row["question"]
        correct = row["answer"]["aliases"][0] if row["answer"]["aliases"] else row["answer"]["value"]
        questions.append({"question": q, "correct_answer": correct})
    return questions

# ── Core Functions ─────────────────────────────────────────────────────────────

def generate_answer_and_explanation(question: str, model: str) -> tuple:
    prompt = ANSWER_PROMPT.format(question=question)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    raw = response.choices[0].message.content.strip()
    answer, explanation = "", ""
    for line in raw.split("\n"):
        if line.startswith("Answer:"):
            answer = line.replace("Answer:", "").strip()
        elif line.startswith("Explanation:"):
            explanation = line.replace("Explanation:", "").strip()
    return answer, explanation


def extract_commitments(question: str, answer: str, explanation: str, model: str) -> dict:
    prompt = EXTRACTION_PROMPT.format(question=question, answer=answer, explanation=explanation)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])


def probe_commitment(commitment: str, model: str) -> dict:
    prompt = PROBING_PROMPT.format(commitment=commitment)
    response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.0,
    max_tokens=5
    )
    answer = response.choices[0].message.content.strip().lower()
    if "yes" in answer:
        result = "yes"
    elif "no" in answer:
        result = "no"
    else:
        result = "unclear"
    return {"commitment": commitment, "answer": result}


def probe_all(commitments: dict, model: str) -> dict:
    results = {}
    for category, commitment_list in commitments.items():
        results[category] = []
        for commitment in commitment_list:
            r = probe_commitment(commitment, model)
            results[category].append(r)
            print(f"    [{category}] '{commitment[:50]}' → {r['answer']}")
    return results


def consistency_score(probe_results: dict) -> float:
    total, consistent = 0, 0
    for results in probe_results.values():
        for r in results:
            total += 1
            if r["answer"] == "yes":
                consistent += 1
    return consistent / total if total > 0 else 0.0

# ── Per-model Pipeline ─────────────────────────────────────────────────────────

def run_model(question: str, model_name: str, model_id: str) -> dict:
    print(f"\n  [{model_name}] Generating answer...")
    answer, explanation = generate_answer_and_explanation(question, model_id)
    print(f"  Answer: {answer}")

    print(f"  [{model_name}] Extracting commitments...")
    commitments = extract_commitments(question, answer, explanation, model_id)
    total_commitments = sum(len(v) for v in commitments.values())
    print(f"  Found {total_commitments} commitments")

    print(f"  [{model_name}] Probing...")
    probe_results = probe_all(commitments, model_id)

    score = consistency_score(probe_results)
    print(f"  [{model_name}] SCORE: {score:.2%}")

    return {
        "model": model_name,
        "answer": answer,
        "explanation": explanation,
        "commitments": commitments,
        "probe_results": probe_results,
        "consistency_score": score
    }

# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    questions = fetch_triviaqa(n=5)

    all_results = []
    model_scores = {name: [] for name in MODELS}

    for item in questions:
        q = item["question"]
        print("\n" + "=" * 60)
        print(f"Q: {q}")
        print(f"Correct answer: {item['correct_answer']}")

        question_result = {"question": q, "correct_answer": item["correct_answer"], "models": []}

        for model_name, model_id in MODELS.items():
            try:
                result = run_model(q, model_name, model_id)
                question_result["models"].append(result)
                model_scores[model_name].append(result["consistency_score"])
            except Exception as e:
                print(f"  [{model_name}] ERROR: {e}")

        all_results.append(question_result)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY — Average Consistency Score per Model")
    print("=" * 60)
    for model_name, scores in model_scores.items():
        if scores:
            avg = sum(scores) / len(scores)
            print(f"  {model_name:20s}: {avg:.2%}")

    with open("multi_model_results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print("\nResults saved to multi_model_results.json")