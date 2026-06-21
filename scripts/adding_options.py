# add_arc_choices.py
import pandas as pd
from datasets import load_dataset

INPUT_CSV = "outputs/big_annotation_results.csv"
OUTPUT_CSV = "outputs/big_annotation_results_with_options.csv"

df = pd.read_csv(INPUT_CSV)
arc = load_dataset("allenai/ai2_arc", "ARC-Challenge", split="train")

# Match ARC rows by exact question text
options_lookup = {}

for row in arc:
    question = row["question"].strip()
    labels = row["choices"]["label"]
    texts = row["choices"]["text"]

    options = "\n".join(
        f"{label}. {text}"
        for label, text in zip(labels, texts)
    )

    options_lookup[question] = options

# Add one options column
df["options"] = df["question"].str.strip().map(options_lookup)

# Move options column after question
cols = list(df.columns)
cols.remove("options")
question_index = cols.index("question")
cols.insert(question_index + 1, "options")
df = df[cols]

# Check if some questions did not match
print("Missing options:", df["options"].isna().sum())

df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved to {OUTPUT_CSV}")