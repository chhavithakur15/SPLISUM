from splisum.io.mgf import read_mgf, write_mgf

def detect_mode(spec):
    params = spec["params"]

    if "PRECURSOR_TYPE" in params:
        adduct = params["PRECURSOR_TYPE"]
        if adduct.endswith("+"):
            return "positive"
        elif adduct.endswith("-"):
            return "negative"

    if "CHARGE" in params:
        charge = params["CHARGE"]
        if charge.endswith("+"):
            return "positive"
        elif charge.endswith("-"):
            return "negative"

    return None


def get_collision_energy(spec):
    params = spec["params"]
    if "COLLISION_ENERGY" not in params:
        return None

    val = params["COLLISION_ENERGY"]
    val = val.replace("eV", "").replace("=", "").strip()

    try:
        return float(val)
    except:
        return None


def filter_library(input_mgf, output_mgf, mode=None, energy=20, tolerance=0.5):
    spectra = read_mgf(input_mgf)

    filtered = []

    for spec in spectra:
        keep = True

        # Filter mode
        if mode:
            m = detect_mode(spec)
            if m != mode:
                keep = False

        # Filter energy
        ce = get_collision_energy(spec)
        if ce is not None:
            if abs(ce - energy) > tolerance:
                keep = False

        if keep:
            filtered.append(spec)

    write_mgf(filtered, output_mgf)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", choices=["positive", "negative"], default=None)
    parser.add_argument("--energy", type=float, default=20)
    parser.add_argument("--tolerance", type=float, default=0.5)

    args = parser.parse_args()

    filter_library(
        args.input,
        args.output,
        mode=args.mode,
        energy=args.energy,
        tolerance=args.tolerance
    )