import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

PROBING_PROMPT = """Answer with only 'yes' or 'no'. Do not think or explain. Just answer yes or no.

Statement: {commitment}

Answer (yes or no):"""


def probe_commitment(commitment: str, model: str) -> str:
    prompt = PROBING_PROMPT.format(commitment=commitment)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=5
    )
    answer = response.choices[0].message.content.strip().lower()
    if "yes" in answer:
        return "yes"
    elif "no" in answer:
        return "no"
    return "unclear"


def benchmark_pilot_set(pilot_set_path: str, model: str = "llama-3.3-70b-versatile"):
    with open(pilot_set_path) as f:
        pilot_set = json.load(f)

    print(f"Benchmarking {len(pilot_set)} examples with {model}\n")

    category_stats = {
        "explicit": {"yes": 0, "no": 0, "unclear": 0},
        "implicit": {"yes": 0, "no": 0, "unclear": 0},
        "logical_principle": {"yes": 0, "no": 0, "unclear": 0}
    }

    results = []

    for item in pilot_set:
        q = item["question"]
        commitments = item["commitments"]
        print(f"Q: {q[:70]}")

        item_results = {"id": item["id"], "question": q, "probe_results": {}}

        for category, commitment_list in commitments.items():
            item_results["probe_results"][category] = []
            for commitment in commitment_list:
                answer = probe_commitment(commitment, model)
                category_stats[category][answer] += 1
                item_results["probe_results"][category].append({
                    "commitment": commitment,
                    "answer": answer
                })
                print(f"  [{category}] {commitment[:50]} → {answer}")

        results.append(item_results)
        print()

    # Per-category consistency scores
    print("=" * 60)
    print("RESULTS PER CATEGORY")
    print("=" * 60)
    for category, stats in category_stats.items():
        total = stats["yes"] + stats["no"] + stats["unclear"]
        if total > 0:
            score = stats["yes"] / total
            print(f"  {category:20s}: {score:.2%} consistent ({stats['yes']}/{total})")

    # Overall
    total_yes = sum(s["yes"] for s in category_stats.values())
    total_all = sum(s["yes"] + s["no"] + s["unclear"] for s in category_stats.values())
    print(f"\n  {'OVERALL':20s}: {total_yes/total_all:.2%} consistent ({total_yes}/{total_all})")

    # Save
    output = {
        "model": model,
        "n_examples": len(pilot_set),
        "category_stats": category_stats,
        "results": results
    }
    with open("benchmark_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nSaved to benchmark_results.json")


if __name__ == "__main__":
    benchmark_pilot_set("pilot_set.json")