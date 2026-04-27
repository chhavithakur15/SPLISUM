import argparse
import pandas as pd
import matplotlib.pyplot as plt


def compare_fdr(
    estimated_file,
    actual_file,
    output_table,
    output_plot=None,
    threshold_col="Threshold",
    estimated_col="Estimated FDR",
    actual_col="Actual FDR",
):
    # Read estimated FDR
    if estimated_file.endswith(".xlsx"):
        estimated_df = pd.read_excel(estimated_file)
    else:
        estimated_df = pd.read_csv(estimated_file)

    # Read actual FDR
    if actual_file.endswith(".xlsx"):
        actual_df = pd.read_excel(actual_file)
    else:
        actual_df = pd.read_csv(actual_file)

    estimated_df.columns = estimated_df.columns.str.strip()
    actual_df.columns = actual_df.columns.str.strip()

    required_estimated = [threshold_col, estimated_col]
    required_actual = [threshold_col, actual_col]

    for col in required_estimated:
        if col not in estimated_df.columns:
            raise ValueError(f"Missing column in estimated FDR file: {col}")

    for col in required_actual:
        if col not in actual_df.columns:
            raise ValueError(f"Missing column in actual FDR file: {col}")

    estimated_df = estimated_df[[threshold_col, estimated_col]]
    actual_df = actual_df[[threshold_col, actual_col]]

    comparison_df = estimated_df.merge(
        actual_df,
        on=threshold_col,
        how="inner"
    )

    comparison_df = comparison_df.sort_values(by=threshold_col)

    if output_table.endswith(".xlsx"):
        comparison_df.to_excel(output_table, index=False)
    else:
        comparison_df.to_csv(output_table, index=False)

    print(f"Combined FDR comparison table saved to: {output_table}")

    if output_plot:
        plt.figure(figsize=(7, 5))
        plt.plot(
            comparison_df[threshold_col],
            comparison_df[estimated_col],
            marker="o",
            label="Estimated FDR",
        )
        plt.plot(
            comparison_df[threshold_col],
            comparison_df[actual_col],
            marker="o",
            label="Actual FDR",
        )

        plt.xlabel("Cosine Similarity Threshold")
        plt.ylabel("FDR")
        plt.title("Estimated vs Actual FDR")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_plot, dpi=300)
        print(f"FDR comparison plot saved to: {output_plot}")

    return comparison_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare estimated and actual FDR tables."
    )

    parser.add_argument("--estimated", required=True)
    parser.add_argument("--actual", required=True)
    parser.add_argument("--output_table", required=True)
    parser.add_argument("--output_plot", default=None)

    parser.add_argument("--threshold_col", default="Threshold")
    parser.add_argument("--estimated_col", default="Estimated FDR")
    parser.add_argument("--actual_col", default="Actual FDR")

    args = parser.parse_args()

    compare_fdr(
        estimated_file=args.estimated,
        actual_file=args.actual,
        output_table=args.output_table,
        output_plot=args.output_plot,
        threshold_col=args.threshold_col,
        estimated_col=args.estimated_col,
        actual_col=args.actual_col,
    )