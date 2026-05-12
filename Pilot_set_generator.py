import os
import json
import random
from groq import Groq
from dotenv import load_dotenv
from datasets import load_dataset

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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


def fetch_triviaqa(n: int = 20) -> list:
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


if __name__ == "__main__":
    questions = fetch_triviaqa(n=20)
    pilot_set = []

    for i, item in enumerate(questions):
        q = item["question"]
        print(f"\n[{i+1}/20] {q}")

        try:
            answer, explanation = generate_answer_and_explanation(q)
            if not explanation:
                print("  Skipping — no explanation generated")
                continue

            commitments = extract_commitments(q, answer, explanation)
            total = sum(len(v) for v in commitments.values())

            if total == 0:
                print("  Skipping — no commitments extracted")
                continue

            print(f"  Answer: {answer}")
            print(f"  Commitments: {total} total")

            pilot_set.append({
                "id": len(pilot_set) + 1,
                "question": q,
                "correct_answer": item["correct_answer"],
                "model_answer": answer,
                "explanation": explanation,
                "commitments": commitments,
                "human_verified": False,
                "notes": ""
            })

        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    print(f"\n✓ Pilot set: {len(pilot_set)} examples")

    with open("pilot_set.json", "w") as f:
        json.dump(pilot_set, f, indent=2)

    print("Saved to pilot_set.json")