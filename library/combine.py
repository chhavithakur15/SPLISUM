import os
import argparse


def add_label_to_title(line, label):
    title = line.strip().split("=", 1)[1]

    if title.startswith(label):
        return line

    return f"TITLE={label}{title}\n"


def merge_mgf_folder(input_folder, output_file, title_label=None):
    mgf_files = sorted(
        [f for f in os.listdir(input_folder) if f.endswith((".mgf", ".txt"))]
    )

    with open(output_file, "w") as out:
        for file_name in mgf_files:
            path = os.path.join(input_folder, file_name)

            with open(path, "r") as f:
                for line in f:
                    if title_label and line.startswith("TITLE="):
                        out.write(add_label_to_title(line, title_label))
                    else:
                        out.write(line)

                out.write("\n")

    print(f"Merged MGF written to: {output_file}")


def combine_target_decoy(target_folder, decoy_folder, output_file):
    with open(output_file, "w") as out:
        for folder, label in [
            (target_folder, "Original_"),
            (decoy_folder, "Decoy_"),
        ]:
            mgf_files = sorted(
                [f for f in os.listdir(folder) if f.endswith((".mgf", ".txt"))]
            )

            for file_name in mgf_files:
                path = os.path.join(folder, file_name)

                with open(path, "r") as f:
                    for line in f:
                        if line.startswith("TITLE="):
                            out.write(add_label_to_title(line, label))
                        else:
                            out.write(line)

                    out.write("\n")

    print(f"Combined target-decoy MGF written to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge or combine MGF files.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    merge_parser = subparsers.add_parser("merge-folder")
    merge_parser.add_argument("--input_folder", required=True)
    merge_parser.add_argument("--output", required=True)
    merge_parser.add_argument("--title_label", default=None)

    combine_parser = subparsers.add_parser("combine-target-decoy")
    combine_parser.add_argument("--target_folder", required=True)
    combine_parser.add_argument("--decoy_folder", required=True)
    combine_parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.command == "merge-folder":
        merge_mgf_folder(
            input_folder=args.input_folder,
            output_file=args.output,
            title_label=args.title_label,
        )

    elif args.command == "combine-target-decoy":
        combine_target_decoy(
            target_folder=args.target_folder,
            decoy_folder=args.decoy_folder,
            output_file=args.output,
        )