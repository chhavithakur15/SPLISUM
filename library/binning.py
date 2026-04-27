import os


def get_pepmass(block):
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


def is_within_ppm(m1, m2, ppm):
    return abs(m1 - m2) <= (ppm * m1 / 1_000_000)


def bin_mgf_complete_linkage(input_file, output_folder, ppm_tolerance=50):
    os.makedirs(output_folder, exist_ok=True)

    spectra = []

    with open(input_file, "r") as f:
        block = []
        for line in f:
            block.append(line)
            if line.strip() == "END IONS":
                pepmass = get_pepmass(block)
                if pepmass is not None:
                    spectra.append((pepmass, block))
                block = []

    bins = []

    for pepmass, block in spectra:
        assigned = False

        for pepmass_list, block_list in bins:
            if all(is_within_ppm(pepmass, pm, ppm_tolerance) for pm in pepmass_list):
                pepmass_list.append(pepmass)
                block_list.append(block)
                assigned = True
                break

        if not assigned:
            bins.append(([pepmass], [block]))

    for i, (pepmasses, blocks) in enumerate(bins):
        filename = f"bin_{i+1}_center_{pepmasses[0]:.4f}_ppm{ppm_tolerance}_complete.mgf"
        path = os.path.join(output_folder, filename)

        with open(path, "w") as f:
            for block in blocks:
                f.writelines(block)

    print(f"Created {len(bins)} bins in: {output_folder}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output_folder", required=True)
    parser.add_argument("--ppm", type=float, default=50)

    args = parser.parse_args()

    bin_mgf_complete_linkage(
        input_file=args.input,
        output_folder=args.output_folder,
        ppm_tolerance=args.ppm
    )