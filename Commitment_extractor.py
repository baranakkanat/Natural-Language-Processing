import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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
        commitments = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        commitments = json.loads(raw[start:end])

    return commitments


if __name__ == "__main__":
    question = "What is the best venue for my NLP paper? (A) ACL (B) CVPR"
    answer = "A"
    explanation = "I chose ACL because ACL focuses on NLP, and NLP-focused venues are the best fit for NLP papers."

    print("Input:")
    print(f"  Q: {question}")
    print(f"  A: {answer}")
    print(f"  Explanation: {explanation}")
    print()

    commitments = extract_commitments(question, answer, explanation)

    print("Extracted Commitments:")
    print(json.dumps(commitments, indent=2))