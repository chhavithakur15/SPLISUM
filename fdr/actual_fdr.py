import argparse
import pandas as pd


DEFAULT_THRESHOLDS = [0.01, 0.45, 0.55, 0.60, 0.65, 0.70, 0.75]


def calculate_actual_fdr(
    input_file,
    output_file=None,
    thresholds=None,
    score_col="TopScore",
    edit_col="Edit Similarity",
    exist_col="Exist in Target Library?",
):
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    if input_file.endswith(".xlsx"):
        df = pd.read_excel(input_file)
    else:
        df = pd.read_csv(input_file)

    df.columns = df.columns.str.strip()

    for col in [score_col, edit_col, exist_col]:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df[score_col] = pd.to_numeric(df[score_col], errors="coerce")
    df[edit_col] = pd.to_numeric(df[edit_col], errors="coerce")
    df[exist_col] = df[exist_col].astype(str).str.strip()

    results = []

    for threshold in thresholds:
        df_t = df[
            (df[score_col] >= threshold)
            & (df[edit_col].notna())
            & (df[exist_col].isin(["Yes", "No"]))
        ]

        target = (df_t[exist_col] == "Yes").sum()

        stereoisomers = (
            (df_t[exist_col] == "No")
            & (df_t[edit_col] >= 0.9999)
        ).sum()

        highly_similar = (
            (df_t[exist_col] == "No")
            & (df_t[edit_col] >= 0.9)
            & (df_t[edit_col] < 0.9999)
        ).sum()

        not_identical = (
            (df_t[exist_col] == "No")
            & (df_t[edit_col] < 0.9)
        ).sum()

        total = int(target + stereoisomers + highly_similar + not_identical)
        actual_fdr = not_identical / total if total > 0 else None

        results.append({
            "Threshold": threshold,
            "Target": int(target),
            "Stereoisomers": int(stereoisomers),
            "Highly Similar": int(highly_similar),
            "Not Identical": int(not_identical),
            "Total": total,
            "Actual FDR": actual_fdr,
        })

    result_df = pd.DataFrame(results)

    if output_file:
        if output_file.endswith(".xlsx"):
            result_df.to_excel(output_file, index=False)
        else:
            result_df.to_csv(output_file, index=False)

        print(f"Actual FDR table saved to: {output_file}")

    return result_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate actual FDR from prepared SPLISUM result table."
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default=None)

    parser.add_argument(
        "--thresholds",
        nargs="+",
        type=float,
        default=DEFAULT_THRESHOLDS,
    )

    parser.add_argument("--score_col", default="TopScore")
    parser.add_argument("--edit_col", default="Edit Similarity")
    parser.add_argument("--exist_col", default="Exist in Target Library?")

    args = parser.parse_args()

    result = calculate_actual_fdr(
        input_file=args.input,
        output_file=args.output,
        thresholds=args.thresholds,
        score_col=args.score_col,
        edit_col=args.edit_col,
        exist_col=args.exist_col,
    )

    print(result)
    