import argparse
import subprocess


def run_msslash(
    msslash_path,
    library,
    query,
    decoy,
    output,
    threads=8,
    iterations=100,
    similarity=0.0,
    tolerance=1000,
    precision=1.0,
    min_mz=0,
):
    cmd = [
        msslash_path,
        "-n", str(threads),
        "-i", str(iterations),
        "-s", str(similarity),
        "-t", "1",
        "-l", library,
        "-e", query,
        "-d", decoy,
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
    parser = argparse.ArgumentParser(description="Run msSLASH search.")

    parser.add_argument("--msslash_path", required=True)
    parser.add_argument("--library", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--decoy", required=True)
    parser.add_argument("--output", required=True)

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
        decoy=args.decoy,
        output=args.output,
        threads=args.threads,
        iterations=args.iterations,
        similarity=args.similarity,
        tolerance=args.tolerance,
        precision=args.precision,
        min_mz=args.min_mz,
    )