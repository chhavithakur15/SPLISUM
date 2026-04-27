import argparse
import pandas as pd


DEFAULT_THRESHOLDS = [0.01, 0.45, 0.55, 0.60, 0.65, 0.70, 0.75]


def calculate_estimated_fdr(
    input_file,
    output_file=None,
    thresholds=None,
    score_col="TopScore",
    peptide_col="TopPep",
    decoy_pattern="DECOY",
):
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    df = pd.read_csv(input_file, sep="\t")

    if score_col not in df.columns:
        raise ValueError(f"Column '{score_col}' not found in input file.")

    if peptide_col not in df.columns:
        raise ValueError(f"Column '{peptide_col}' not found in input file.")

    df["IsDecoy"] = df[peptide_col].astype(str).str.contains(
        decoy_pattern,
        case=False,
        na=False,
    )

    results = []

    for threshold in thresholds:
        df_above = df[df[score_col] >= threshold]

        decoy_hits = int(df_above["IsDecoy"].sum())
        target_hits = int(len(df_above) - decoy_hits)
        total_hits = int(len(df_above))

        estimated_fdr = decoy_hits / target_hits if target_hits > 0 else None

        results.append({
            "Threshold": threshold,
            "Total Hits": total_hits,
            "Target Hits": target_hits,
            "Decoy Hits": decoy_hits,
            "Estimated FDR": estimated_fdr,
        })

    result_df = pd.DataFrame(results)

    if output_file:
        if output_file.endswith(".xlsx"):
            result_df.to_excel(output_file, index=False)
        else:
            result_df.to_csv(output_file, index=False)

        print(f"Estimated FDR table saved to: {output_file}")

    return result_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate estimated FDR from msSLASH output."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="msSLASH output .txt file"
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Output .csv or .xlsx file"
    )

    parser.add_argument(
        "--thresholds",
        nargs="+",
        type=float,
        default=DEFAULT_THRESHOLDS,
        help="Similarity thresholds"
    )

    parser.add_argument(
        "--score_col",
        default="TopScore",
        help="Column containing similarity score"
    )

    parser.add_argument(
        "--peptide_col",
        default="TopPep",
        help="Column containing target/decoy peptide or title"
    )

    parser.add_argument(
        "--decoy_pattern",
        default="DECOY",
        help="Pattern used to identify decoy hits"
    )

    args = parser.parse_args()

    result = calculate_estimated_fdr(
        input_file=args.input,
        output_file=args.output,
        thresholds=args.thresholds,
        score_col=args.score_col,
        peptide_col=args.peptide_col,
        decoy_pattern=args.decoy_pattern,
    )

    print(result)