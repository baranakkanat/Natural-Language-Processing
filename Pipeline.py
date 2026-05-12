import os
import json
import random
from groq import Groq
from dotenv import load_dotenv
from datasets import load_dataset

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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

PROBING_PROMPT = """Answer with only 'yes' or 'no'. Do you agree with the following statement?

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

# ── LLM Answer + Explanation ───────────────────────────────────────────────────

def generate_answer_and_explanation(question: str) -> tuple:
    prompt = ANSWER_PROMPT.format(question=question)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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

# ── Extraction ─────────────────────────────────────────────────────────────────

def extract_commitments(question: str, answer: str, explanation: str) -> dict:
    prompt = EXTRACTION_PROMPT.format(
        question=question,
        answer=answer,
        explanation=explanation
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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

# ── Probing ────────────────────────────────────────────────────────────────────

def probe_commitment(commitment: str) -> dict:
    prompt = PROBING_PROMPT.format(commitment=commitment)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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

    return {"commitment": commitment, "answer": result, "raw": answer}


def probe_all(commitments: dict) -> dict:
    results = {}
    for category, commitment_list in commitments.items():
        results[category] = []
        for commitment in commitment_list:
            r = probe_commitment(commitment)
            results[category].append(r)
            print(f"  [{category}] '{commitment[:60]}' → {r['answer']}")
    return results

# ── Scoring ────────────────────────────────────────────────────────────────────

def consistency_score(probe_results: dict) -> float:
    total, consistent = 0, 0
    for results in probe_results.values():
        for r in results:
            total += 1
            if r["answer"] == "yes":
                consistent += 1
    return consistent / total if total > 0 else 0.0

# ── Full Pipeline ──────────────────────────────────────────────────────────────

def run_pipeline(question: str) -> dict:
    print("=" * 60)
    print(f"Q: {question}")

    print("STEP 1: Generating answer and explanation...")
    answer, explanation = generate_answer_and_explanation(question)
    print(f"  Answer: {answer}")
    print(f"  Explanation: {explanation}")
    print()

    print("STEP 2: Extracting commitments...")
    commitments = extract_commitments(question, answer, explanation)
    print(json.dumps(commitments, indent=2))
    print()

    print("STEP 3: Probing commitments...")
    probe_results = probe_all(commitments)
    print()

    score = consistency_score(probe_results)
    print(f"CONSISTENCY SCORE: {score:.2%}")
    print("=" * 60)

    return {
        "question": question,
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
    for item in questions:
        result = run_pipeline(item["question"])
        result["correct_answer"] = item["correct_answer"]
        all_results.append(result)
        print()

    with open("results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    avg_score = sum(r["consistency_score"] for r in all_results) / len(all_results)
    print(f"\nAVERAGE CONSISTENCY SCORE: {avg_score:.2%}")
    print("Results saved to results.json")