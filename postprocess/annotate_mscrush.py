import argparse
import pandas as pd


def read_table_smart(file_path, sheet_name="Sheet1"):
    """
    Read CSV or Excel safely.
    If Excel sheet_name is not found, use the first sheet.
    """
    if file_path.endswith(".xlsx"):
        xls = pd.ExcelFile(file_path)

        if sheet_name in xls.sheet_names:
            return pd.read_excel(file_path, sheet_name=sheet_name)

        print(
            f"Warning: Sheet '{sheet_name}' not found in {file_path}. "
            f"Using first sheet: '{xls.sheet_names[0]}'"
        )
        return pd.read_excel(file_path, sheet_name=0)

    return pd.read_csv(file_path)


def annotate_with_mscrush_clusters(
    results_file,
    cluster_stats_file,
    output_file,
    results_sheet="Sheet1",
    cluster_sheet="Sheet1",
    result_title_col="TARGET TITLE",
    cluster_title_col="TITLE",
    cluster_id_col="Cluster ID",
    cluster_compounds_col="Full_Cluster_Compounds",
):
    # Load main SPLISUM result table
    results_df = read_table_smart(results_file, results_sheet)

    # Load msCRUSH statistics table
    cluster_df = read_table_smart(cluster_stats_file, cluster_sheet)

    # Clean column names
    results_df.columns = results_df.columns.astype(str).str.strip()
    cluster_df.columns = cluster_df.columns.astype(str).str.strip()

    # Check required columns
    if result_title_col not in results_df.columns:
        raise ValueError(f"Missing column in results file: {result_title_col}")

    required_cluster_cols = [
        cluster_title_col,
        cluster_id_col,
        cluster_compounds_col,
    ]

    for col in required_cluster_cols:
        if col not in cluster_df.columns:
            raise ValueError(f"Missing column in msCRUSH statistics file: {col}")

    # Keep only useful columns from msCRUSH table
    cluster_lookup = cluster_df[
        [cluster_title_col, cluster_id_col, cluster_compounds_col]
    ].drop_duplicates(subset=[cluster_title_col])

    # Merge using TARGET TITLE from results and TITLE from msCRUSH table
    annotated_df = results_df.merge(
        cluster_lookup,
        left_on=result_title_col,
        right_on=cluster_title_col,
        how="left",
    )

    # Remove duplicate TITLE column from msCRUSH if different from TARGET TITLE
    if cluster_title_col in annotated_df.columns and cluster_title_col != result_title_col:
        annotated_df = annotated_df.drop(columns=[cluster_title_col])

    # Calculate cluster count
    annotated_df["Cluster_Count"] = annotated_df[cluster_compounds_col].apply(
        lambda x: len(str(x).split("|")) if pd.notna(x) and str(x).strip() else 0
    )

    # Save output
    if output_file.endswith(".xlsx"):
        annotated_df.to_excel(output_file, index=False)
    else:
        annotated_df.to_csv(output_file, index=False)

    print(f"Annotated msCRUSH table saved to: {output_file}")
    print(f"Total rows: {len(annotated_df)}")
    print(f"Rows with cluster annotation: {annotated_df[cluster_id_col].notna().sum()}")

    return annotated_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Annotate SPLISUM result table with msCRUSH cluster information."
    )

    parser.add_argument("--results", required=True)
    parser.add_argument("--cluster_stats", required=True)
    parser.add_argument("--output", required=True)

    parser.add_argument("--results_sheet", default="Sheet1")
    parser.add_argument("--cluster_sheet", default="Sheet1")

    parser.add_argument("--result_title_col", default="TARGET TITLE")
    parser.add_argument("--cluster_title_col", default="TITLE")
    parser.add_argument("--cluster_id_col", default="Cluster ID")
    parser.add_argument("--cluster_compounds_col", default="Full_Cluster_Compounds")

    args = parser.parse_args()

    annotate_with_mscrush_clusters(
        results_file=args.results,
        cluster_stats_file=args.cluster_stats,
        output_file=args.output,
        results_sheet=args.results_sheet,
        cluster_sheet=args.cluster_sheet,
        result_title_col=args.result_title_col,
        cluster_title_col=args.cluster_title_col,
        cluster_id_col=args.cluster_id_col,
        cluster_compounds_col=args.cluster_compounds_col,
    )