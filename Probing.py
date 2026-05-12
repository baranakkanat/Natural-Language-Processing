import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

PROBING_PROMPT = """Answer with only 'yes' or 'no'. Do not think or explain. Just answer yes or no.

Statement: {commitment}

Answer (yes or no):"""


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

    return {
        "commitment": commitment,
        "answer": result,
        "raw": answer
    }


def probe_all(commitments: dict) -> dict:
    results = {}

    for category, commitment_list in commitments.items():
        results[category] = []
        for commitment in commitment_list:
            probe_result = probe_commitment(commitment)
            results[category].append(probe_result)
            print(f"  [{category}] '{commitment[:60]}...' → {probe_result['answer']}")

    return results


def consistency_score(probe_results: dict) -> float:
    total = 0
    consistent = 0

    for category, results in probe_results.items():
        for r in results:
            total += 1
            if r["answer"] == "yes":
                consistent += 1

    if total == 0:
        return 0.0

    return consistent / total


if __name__ == "__main__":
    # Example commitments from commitment_extractor.py output
    commitments = {
        "explicit": [
            "ACL focuses on NLP",
            "NLP-focused venues are the best fit for NLP papers"
        ],
        "implicit": [
            "ACL is a better fit for NLP papers than CVPR",
            "The best venue for an NLP paper is one that focuses on NLP"
        ],
        "logical_principle": [
            "the principle of matching the topic of a paper to the focus of a venue"
        ]
    }

    print("Probing commitments...\n")
    probe_results = probe_all(commitments)

    score = consistency_score(probe_results)

    print(f"\nConsistency Score: {score:.2%}")
    print("\nFull Results:")
    print(json.dumps(probe_results, indent=2))