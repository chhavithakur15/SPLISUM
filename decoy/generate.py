import os
import random
import re


def extract_bin_center(filename):
    match = re.search(r"center_([0-9.]+)", filename)
    if match:
        return float(match.group(1))

    nums = re.findall(r"[0-9.]+", filename)
    if nums:
        return float(nums[0])

    return float("inf")


def read_mgf_blocks(file_path):
    blocks = []
    block = []

    with open(file_path, "r") as f:
        for line in f:
            block.append(line)
            if line.strip() == "END IONS":
                blocks.append(block)
                block = []

    return blocks


def get_precursor_mass(block):
    for line in block:
        if line.startswith("PEPMASS="):
            try:
                return float(line.strip().split("=")[1].split()[0])
            except Exception:
                return None

        if line.startswith("PRECURSOR_MASS="):
            try:
                return float(line.strip().split("=")[1].split()[0])
            except Exception:
                return None

    return None


def replace_precursor_mass(block, new_mass):
    updated = []

    has_pepmass = any(line.startswith("PEPMASS=") for line in block)
    has_precursor_mz = any(line.startswith("PRECURSOR_MZ=") for line in block)

    for line in block:
        if line.startswith("PEPMASS="):
            updated.append(f"PEPMASS={new_mass:.6f}\n")

        elif line.startswith("PRECURSOR_MASS="):
            updated.append(f"PRECURSOR_MASS={new_mass:.6f}\n")

        elif line.startswith("PRECURSOR_MZ="):
            updated.append(f"PRECURSOR_MZ={new_mass:.6f}\n")

        elif line.startswith("TITLE="):
            title = line.strip().split("=", 1)[1]
            if title.startswith("DECOY_"):
                updated.append(line)
            else:
                updated.append(f"TITLE=DECOY_{title}\n")

        else:
            updated.append(line)

    if not has_pepmass:
        insert_idx = 1
        updated.insert(insert_idx, f"PEPMASS={new_mass:.6f}\n")

    if not has_precursor_mz:
        insert_idx = 2
        updated.insert(insert_idx, f"PRECURSOR_MZ={new_mass:.6f}\n")

    return updated


def load_bins(input_folder):
    bin_files = sorted(
        [f for f in os.listdir(input_folder) if f.endswith((".mgf", ".txt"))],
        key=extract_bin_center
    )

    bins = []

    for file_name in bin_files:
        file_path = os.path.join(input_folder, file_name)
        blocks = read_mgf_blocks(file_path)

        spectra = []
        for block in blocks:
            mass = get_precursor_mass(block)
            if mass is not None:
                spectra.append({"mass": mass, "block": block})

        if spectra:
            bins.append({
                "file": file_name,
                "spectra": spectra
            })

    return bins


def generate_decoys_from_neighbor_bins(input_folder, output_folder, seed=42):
    random.seed(seed)
    os.makedirs(output_folder, exist_ok=True)

    bins = load_bins(input_folder)

    if len(bins) < 2:
        raise ValueError("Need at least two bin files for neighboring-bin reshuffling.")

    for i in range(len(bins)):
        current_bin = bins[i]

        if i < len(bins) - 1:
            neighbor_bin = bins[i + 1]
        else:
            neighbor_bin = bins[i - 1]

        current_spectra = current_bin["spectra"]
        neighbor_spectra = neighbor_bin["spectra"]

        candidate_masses = [s["mass"] for s in current_spectra + neighbor_spectra]
        random.shuffle(candidate_masses)

        output_file = os.path.join(output_folder, f"decoy_{current_bin['file']}")

        with open(output_file, "w") as out:
            for spectrum, new_mass in zip(current_spectra, candidate_masses):
                decoy_block = replace_precursor_mass(spectrum["block"], new_mass)
                out.writelines(decoy_block)
                out.write("\n")

    print(f"Decoy MGF files created in: {output_folder}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_folder", required=True)
    parser.add_argument("--output_folder", required=True)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    generate_decoys_from_neighbor_bins(
        input_folder=args.input_folder,
        output_folder=args.output_folder,
        seed=args.seed
    )