import argparse
import os
import subprocess


def create_dummy_decoy(dummy_decoy_path):
    """
    Create a minimal dummy decoy MGF file required by msSLASH.

    In SPLISUM, target and decoy spectra are already combined in the main
    searchable library passed with -l. The -d file is only a required
    msSLASH argument.
    """
    with open(dummy_decoy_path, "w") as f:
        f.write("BEGIN IONS\n")
        f.write("PEPMASS=0\n")
        f.write("CHARGE=1+\n")
        f.write("END IONS\n")


def run_msslash(
    msslash_path,
    library,
    query,
    output,
    dummy_decoy=None,
    threads=8,
    iterations=100,
    similarity=0.0,
    tolerance=1000,
    precision=1.0,
    min_mz=0,
):
    if dummy_decoy is None:
        output_dir = os.path.dirname(os.path.abspath(output))
        dummy_decoy = os.path.join(output_dir, "dummy_decoy.mgf")

    if not os.path.exists(dummy_decoy):
        create_dummy_decoy(dummy_decoy)

    cmd = [
        msslash_path,
        "-n", str(threads),
        "-i", str(iterations),
        "-s", str(similarity),
        "-t", "1",
        "-l", library,          # combined target-decoy library
        "-e", query,            # query spectra
        "-d", dummy_decoy,      # dummy file required by msSLASH
        "-o", output,
        "-r", "1",
        "-m", str(tolerance),
        "--precision", str(precision),
        "--min_mz", str(min_mz),
    ]

    print("Running msSLASH:")
    print(" ".join(cmd))

    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Run msSLASH search. In SPLISUM, --library should be the combined "
            "target-decoy MGF file. A dummy decoy MGF is created automatically "
            "because msSLASH requires the -d argument."
        )
    )

    parser.add_argument("--msslash_path", required=True)
    parser.add_argument("--library", required=True, help="Combined target-decoy MGF library.")
    parser.add_argument("--query", required=True, help="Query MGF file.")
    parser.add_argument("--output", required=True, help="msSLASH output file.")
    parser.add_argument(
        "--dummy_decoy",
        default=None,
        help="Optional dummy decoy MGF path. If not provided, it is created automatically.",
    )

    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--similarity", type=float, default=0.0)
    parser.add_argument("--tolerance", type=float, default=1000)
    parser.add_argument("--precision", type=float, default=1.0)
    parser.add_argument("--min_mz", type=float, default=0)

    args = parser.parse_args()

    run_msslash(
        msslash_path=args.msslash_path,
        library=args.library,
        query=args.query,
        output=args.output,
        dummy_decoy=args.dummy_decoy,
        threads=args.threads,
        iterations=args.iterations,
        similarity=args.similarity,
        tolerance=args.tolerance,
        precision=args.precision,
        min_mz=args.min_mz,
    )
