from pathlib import Path

def read_mgf(file_path):
    spectra = []
    current = None

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()

            if line == "BEGIN IONS":
                current = {"params": {}, "peaks": []}

            elif line == "END IONS":
                spectra.append(current)
                current = None

            elif current is not None:
                if "=" in line:
                    key, value = line.split("=", 1)
                    current["params"][key.strip()] = value.strip()
                else:
                    parts = line.split()
                    if len(parts) == 2:
                        try:
                            mz = float(parts[0])
                            intensity = float(parts[1])
                            current["peaks"].append((mz, intensity))
                        except:
                            pass

    return spectra


def write_mgf(spectra, file_path):
    with open(file_path, "w") as f:
        for spec in spectra:
            f.write("BEGIN IONS\n")

            for k, v in spec["params"].items():
                f.write(f"{k}={v}\n")

            for mz, intensity in spec["peaks"]:
                f.write(f"{mz} {intensity}\n")

            f.write("END IONS\n\n")


def add_missing_fields(spectra):
    for spec in spectra:
        params = spec["params"]

        # Add PRECURSOR_MZ
        if "PRECURSOR_MZ" not in params and "PEPMASS" in params:
            try:
                mz = float(params["PEPMASS"].split()[0])
                params["PRECURSOR_MZ"] = str(mz)
            except:
                pass

        # Add CHARGE from PRECURSOR_TYPE
        if "CHARGE" not in params and "PRECURSOR_TYPE" in params:
            adduct = params["PRECURSOR_TYPE"]
            if adduct.endswith("+"):
                params["CHARGE"] = "1+"
            elif adduct.endswith("-"):
                params["CHARGE"] = "1-"

    return spectra


def standardize_mgf(input_file, output_file):
    spectra = read_mgf(input_file)
    spectra = add_missing_fields(spectra)
    write_mgf(spectra, output_file)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    standardize_mgf(args.input, args.output)