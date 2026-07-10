from pathlib import Path
import pandas as pd

JUDGMENT_FOLDER = Path("outputs/judgments")
OUTPUT_FOLDER = Path("outputs/stats")
OUTPUT_FOLDER.mkdir(exist_ok=True)

TRUTH_COL = "statement_true_in_isolation"

EXCLUDED_QUESTIONS = [149, 156, 159, 163, 175, 183, 206] # the other two questions (255,225) were left empty so they do not need have any commitments anyway so it doesn't need to be explicitly excluded


def clean_truth(x):
    if pd.isna(x):
        return None

    x = str(x).strip().upper()

    if x.startswith("TRUE"):
        return "TRUE"

    if x.startswith("FALSE"):
        return "FALSE"

    return None


def clean_correct(x):
    if pd.isna(x):
        return None

    x = str(x).strip().upper()

    if x in ["YES", "TRUE", "1"]:
        return "YES"

    if x in ["NO", "FALSE", "0"]:
        return "NO"

    return None


def rate_table(df, group_cols, name):
    out = (
        df.groupby(group_cols, dropna=False)
        .agg(
            n_statements=("statement", "count"),
            n_true=("truth_binary", "sum"),
            truth_rate=("truth_binary", "mean"),
            n_questions=("question_id", "nunique"),
        )
        .reset_index()
    )

    out["truth_rate_percent"] = out["truth_rate"] * 100

    out.to_csv(
        OUTPUT_FOLDER / f"{name}.csv",
        index=False,
    )

    return out


def main():
    files = sorted(JUDGMENT_FOLDER.glob("*.csv"))

    if not files:
        raise FileNotFoundError(
            f"No CSV files found in {JUDGMENT_FOLDER}"
        )

    dfs = []

    for file in files:
        df = pd.read_csv(file)
        df["source_file"] = file.name
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    # Ensure question_id is numeric
    df["question_id"] = pd.to_numeric(
        df["question_id"],
        errors="coerce",
    )

    # Clean truth judgments
    df[TRUTH_COL] = df[TRUTH_COL].apply(clean_truth)

    df["truth_binary"] = df[TRUTH_COL].map(
        {
            "TRUE": 1,
            "FALSE": 0,
        }
    )

    # Infer the original answer correctness column
    def get_llm_correct(row):
        llm = str(row["llm"]).strip().lower()
        col = f"{llm}_correct"

        if col in row.index:
            return clean_correct(row[col])

        return None

    if "llm_correct" in df.columns:
        df["answer_correct"] = df["llm_correct"].apply(clean_correct)
    else:
        df["answer_correct"] = df.apply(
            get_llm_correct,
            axis=1,
        )

    # Remove invalid or unparsed judgments
    valid_before_exclusion = df.dropna(
        subset=["truth_binary", "question_id"]
    ).copy()

    n_invalid = len(df) - len(valid_before_exclusion)

    # Remove excluded questions
    valid = valid_before_exclusion[
        ~valid_before_exclusion["question_id"].isin(EXCLUDED_QUESTIONS)
    ].copy()

    # 1. Overall truth rate by LLM
    by_llm = rate_table(
        valid,
        ["llm"],
        "truth_rate_by_llm",
    )

    # 2. Truth rate by LLM and answer correctness
    by_llm_correctness = rate_table(
        valid,
        ["llm", "answer_correct"],
        "truth_rate_by_llm_and_answer_correctness",
    )

    # 3. Truth rate per question and LLM
    rate_table(
        valid,
        [
            "question_id",
            "question",
            "llm",
            "answer_correct",
        ],
        "truth_rate_by_question_and_llm",
    )

    # 4. Number of false statements per question
    false_counts = (
        valid.assign(
            false_binary=1 - valid["truth_binary"]
        )
        .groupby(
            [
                "question_id",
                "question",
                "llm",
                "answer_correct",
            ],
            dropna=False,
        )
        .agg(
            n_statements=("statement", "count"),
            n_false=("false_binary", "sum"),
            false_rate=("false_binary", "mean"),
        )
        .reset_index()
    )

    false_counts["false_rate_percent"] = (
        false_counts["false_rate"] * 100
    )

    false_counts.to_csv(
        OUTPUT_FOLDER / "false_statement_counts_by_question.csv",
        index=False,
    )

    # 5. Truth rate per source file and LLM
    rate_table(
        valid,
        ["source_file", "llm"],
        "truth_rate_by_file_and_llm",
    )

    # 6. Save combined cleaned data
    valid.to_csv(
        OUTPUT_FOLDER / "combined_cleaned_judgments.csv",
        index=False,
    )

    print("Total files:", len(files))
    print("Total statements:", len(df))
    print("Valid judgments:", len(valid))
    print("Invalid judgments:", n_invalid)

    print("\nTruth rate by LLM:")
    print(by_llm)

    print("\nTruth rate by LLM and answer correctness:")
    print(by_llm_correctness)

    print(f"\nSaved summaries to: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()