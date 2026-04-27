import argparse
import os
import subprocess


def run_mscrush(
    mscrush_path,
    input_mgf,
    output_prefix,
    threads=40,
    hashes=15,
    iterations=100,
    similarity=0.56,
    min_mz=200,
    max_mz=2000,
):
    os.makedirs(os.path.dirname(output_prefix), exist_ok=True)

    cmd = [
        mscrush_path,
        "-f", input_mgf,
        "-t", str(threads),
        "-n", str(hashes),
        "-i", str(iterations),
        "-s", str(similarity),
        "-l", str(min_mz),
        "-r", str(max_mz),
        "-c", output_prefix,
    ]

    print("Running msCRUSH command:")
    print(" ".join(cmd))

    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run msCRUSH clustering for SPLISUM.")

    parser.add_argument("--mscrush_path", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output_prefix", required=True)

    parser.add_argument("--threads", type=int, default=40)
    parser.add_argument("--hashes", type=int, default=15)
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--similarity", type=float, default=0.56)
    parser.add_argument("--min_mz", type=int, default=200)
    parser.add_argument("--max_mz", type=int, default=2000)

    args = parser.parse_args()

    run_mscrush(
        mscrush_path=args.mscrush_path,
        input_mgf=args.input,
        output_prefix=args.output_prefix,
        threads=args.threads,
        hashes=args.hashes,
        iterations=args.iterations,
        similarity=args.similarity,
        min_mz=args.min_mz,
        max_mz=args.max_mz,
    )