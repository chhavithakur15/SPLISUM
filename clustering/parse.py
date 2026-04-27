import argparse
import os
import pandas as pd


def parse_mscrush_cluster_file(cluster_file, mode=None):
    rows = []

    with open(cluster_file, "r") as f:
        header = f.readline().strip().split("\t")

        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split("\t")

            if len(parts) < 2:
                continue

            cluster_id = parts[0]
            titles_text = parts[1]

            titles = [t.strip() for t in titles_text.split("|") if t.strip()]
            cluster_count = len(titles)

            for title in titles:
                rows.append({
                    "Cluster ID": cluster_id,
                    "TITLE": title,
                    "Full_Cluster_Compounds": titles_text,
                    "Cluster_Count": cluster_count,
                    "Mode": mode
                })

    return pd.DataFrame(rows)


def parse_mscrush_clusters(input_path, output_file, mode=None):
    all_tables = []

    if os.path.isdir(input_path):
        cluster_files = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.endswith(".txt")
        ]
    else:
        cluster_files = [input_path]

    cluster_files = sorted(cluster_files)

    for cluster_file in cluster_files:
        df = parse_mscrush_cluster_file(cluster_file, mode=mode)
        df["Source_File"] = os.path.basename(cluster_file)
        all_tables.append(df)

    if not all_tables:
        raise ValueError("No msCRUSH cluster files found.")

    final_df = pd.concat(all_tables, ignore_index=True)

    if output_file.endswith(".xlsx"):
        final_df.to_excel(output_file, index=False)
    else:
        final_df.to_csv(output_file, index=False)

    print(f"msCRUSH cluster table saved to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse msCRUSH cluster output into a statistics table."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="msCRUSH cluster txt file or folder containing cluster txt files"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output .xlsx or .csv file"
    )

    parser.add_argument(
        "--mode",
        default=None,
        choices=["positive", "negative"],
        help="Ion mode label to add to the table"
    )

    args = parser.parse_args()

    parse_mscrush_clusters(
        input_path=args.input,
        output_file=args.output,
        mode=args.mode
    )