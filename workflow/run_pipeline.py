import argparse
import os
import subprocess


def run_command(cmd):
    print("\nRunning:")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Run the minimal SPLISUM target-decoy FDR workflow."
    )

    parser.add_argument("--input_library", required=True)
    parser.add_argument("--query_mgf", required=True)
    parser.add_argument("--target_library_excel", required=True)
    parser.add_argument("--msslash_path", required=True)
    parser.add_argument("--outdir", default="splisum_results")

    args = parser.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    binned_dir = f"{args.outdir}/binned_spectra"
    decoy_dir = f"{args.outdir}/decoy_spectra"
    decoy_library = f"{args.outdir}/decoy_library.mgf"
    msslash_output = f"{args.outdir}/msslash_output.txt"

    estimated_fdr = f"{args.outdir}/estimated_fdr.xlsx"
    actual_input = f"{args.outdir}/actual_fdr_input.xlsx"
    actual_fdr = f"{args.outdir}/actual_fdr.xlsx"
    comparison_table = f"{args.outdir}/fdr_comparison.xlsx"
    comparison_plot = f"{args.outdir}/fdr_comparison.png"

    # 1. 50 ppm complete-linkage binning
    run_command([
        "python", "-m", "splisum.library.binning",
        "--input", args.input_library,
        "--output_folder", binned_dir,
        "--ppm", "50",
    ])

    # 2. Generate decoy spectra from neighboring bins
    run_command([
        "python", "-m", "splisum.decoy.generate",
        "--input_folder", binned_dir,
        "--output_folder", decoy_dir,
        "--seed", "42",
    ])

    # 3. Merge decoy folder into one decoy MGF file
    run_command([
        "python", "-m", "splisum.library.combine",
        "merge-folder",
        "--input_folder", decoy_dir,
        "--output", decoy_library,
    ])

    # 4. Run msSLASH using target library and decoy library separately
    run_command([
        "python", "-m", "splisum.search.msslash",
        "--msslash_path", args.msslash_path,
        "--library", args.input_library,
        "--query", args.query_mgf,
        "--decoy", decoy_library,
        "--output", msslash_output,
    ])

    # 5. Estimated FDR
    run_command([
        "python", "-m", "splisum.fdr.estimated",
        "--input", msslash_output,
        "--output", estimated_fdr,
    ])

    # 6. Prepare actual FDR input
    run_command([
        "python", "-m", "splisum.fdr.prepare_actual_fdr_input",
        "--msslash_txt", msslash_output,
        "--target_mgf", args.input_library,
        "--query_mgf", args.query_mgf,
        "--target_library_excel", args.target_library_excel,
        "--output", actual_input,
    ])

    # 7. Actual FDR
    run_command([
        "python", "-m", "splisum.fdr.actual_fdr",
        "--input", actual_input,
        "--output", actual_fdr,
    ])

    # 8. Compare estimated and actual FDR
    run_command([
        "python", "-m", "splisum.postprocess.compare_fdr",
        "--estimated", estimated_fdr,
        "--actual", actual_fdr,
        "--output_table", comparison_table,
        "--output_plot", comparison_plot,
    ])

    print("\nSPLISUM workflow completed.")
    print(f"Results saved in: {args.outdir}")


if __name__ == "__main__":
    main()