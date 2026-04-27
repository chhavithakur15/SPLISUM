import argparse
from collections import defaultdict
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdRascalMCES
from concurrent.futures import ThreadPoolExecutor


def read_msslash_txt(input_txt):
    df = pd.read_csv(input_txt, sep="\t")
    df.columns = [str(c).strip() for c in df.columns]

    rename_map = {
        "Title": "QUERY TITLE",
        "TopPep": "TARGET PEPTIDE",
    }

    df = df.rename(columns=rename_map)

    if "TARGET TITLE" not in df.columns:
        df["TARGET TITLE"] = ""

    if "QUERY PEPTIDE" not in df.columns:
        df["QUERY PEPTIDE"] = ""

    return df


def parse_target_mgf_peptide_to_title(mgf_path):
    peptide_to_title = {}
    peptide_duplicates = defaultdict(list)

    current_title = None
    current_peptide = None
    inside_block = False

    with open(mgf_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()

            if line == "BEGIN IONS":
                inside_block = True
                current_title = None
                current_peptide = None
                continue

            if line == "END IONS":
                if current_peptide is not None and current_title is not None:
                    if current_peptide in peptide_to_title:
                        peptide_duplicates[current_peptide].append(current_title)
                    else:
                        peptide_to_title[current_peptide] = current_title

                inside_block = False
                continue

            if inside_block:
                if line.startswith("TITLE="):
                    current_title = line.split("=", 1)[1].strip()
                elif line.startswith("PEPTIDE="):
                    current_peptide = line.split("=", 1)[1].strip()

    return peptide_to_title, peptide_duplicates


def parse_query_mgf_title_to_smiles(mgf_path):
    title_to_smiles = {}
    title_duplicates = defaultdict(list)

    current_title = None
    current_smiles = None
    inside_block = False

    with open(mgf_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()

            if line == "BEGIN IONS":
                inside_block = True
                current_title = None
                current_smiles = None
                continue

            if line == "END IONS":
                if current_title is not None and current_smiles is not None:
                    if current_title in title_to_smiles:
                        title_duplicates[current_title].append(current_smiles)
                    else:
                        title_to_smiles[current_title] = current_smiles

                inside_block = False
                continue

            if inside_block:
                if line.startswith("TITLE="):
                    current_title = line.split("=", 1)[1].strip()
                elif line.startswith("PEPTIDE="):
                    current_smiles = line.split("=", 1)[1].strip()

    return title_to_smiles, title_duplicates


def clean_value(x):
    if pd.isna(x):
        return None
    x = str(x).strip()
    return x if x else None


def canonicalize_smiles(smiles):
    try:
        mol = Chem.MolFromSmiles(str(smiles))
        if mol:
            return Chem.MolToSmiles(mol, isomericSmiles=True)
    except Exception:
        return None
    return None


def calculate_edit_similarity(smiles1, smiles2):
    try:
        mol1 = Chem.MolFromSmiles(str(smiles1))
        mol2 = Chem.MolFromSmiles(str(smiles2))

        if not mol1 or not mol2:
            return None

        opts = rdRascalMCES.RascalOptions()
        opts.similarityThreshold = 0.7
        opts.returnEmptyMCES = True
        opts.ignoreAtomAromaticity = False
        opts.ignoreBondOrders = False
        opts.exactConnectionsMatch = True

        results = rdRascalMCES.FindMCES(mol1, mol2, opts)

        return results[0].tier1Sim if results else 0.0

    except Exception:
        return None


def prepare_actual_fdr_input(
    msslash_txt,
    target_mgf,
    query_mgf,
    output_file,
    target_library_excel=None,
    target_library_smiles_col="PEPTIDE",
):
    df = read_msslash_txt(msslash_txt)

    peptide_to_title, peptide_duplicates = parse_target_mgf_peptide_to_title(target_mgf)
    title_to_smiles, title_duplicates = parse_query_mgf_title_to_smiles(query_mgf)

    target_title_filled = 0
    query_peptide_filled = 0

    for idx in df.index:
        target_peptide = clean_value(df.at[idx, "TARGET PEPTIDE"])
        query_title = clean_value(df.at[idx, "QUERY TITLE"])

        if target_peptide:
            matched_title = peptide_to_title.get(target_peptide)
            if matched_title is not None:
                df.at[idx, "TARGET TITLE"] = matched_title
                target_title_filled += 1

        if query_title:
            matched_smiles = title_to_smiles.get(query_title)
            if matched_smiles is not None:
                df.at[idx, "QUERY PEPTIDE"] = matched_smiles
                query_peptide_filled += 1

    def process_row(row):
        target_smiles = row.get("TARGET PEPTIDE", None)
        query_smiles = row.get("QUERY PEPTIDE", None)

        if clean_value(target_smiles) and clean_value(query_smiles):
            return calculate_edit_similarity(target_smiles, query_smiles)

        return None

    with ThreadPoolExecutor() as executor:
        edit_scores = list(executor.map(process_row, df.to_dict("records")))

    df["Edit Similarity"] = edit_scores

    if target_library_excel:
        target_data = pd.read_excel(target_library_excel)
        target_data.columns = [str(c).strip() for c in target_data.columns]

        if target_library_smiles_col not in target_data.columns:
            raise ValueError(
                f"Column '{target_library_smiles_col}' not found in target library Excel."
            )

        target_data["Canonical_PEPTIDE"] = target_data[target_library_smiles_col].apply(
            canonicalize_smiles
        )

        target_smiles_set = set(target_data["Canonical_PEPTIDE"].dropna())

        def check_existence(smiles):
            canonical = canonicalize_smiles(smiles)
            if canonical:
                return "Yes" if canonical in target_smiles_set else "No"
            return "No"

        df["Exist in Target Library?"] = "NA"

        valid = df["TopMatch"] != -1
        df.loc[valid, "Exist in Target Library?"] = df.loc[valid, "QUERY PEPTIDE"].apply(
            check_existence
        )

    else:
        df["Exist in Target Library?"] = "NA"

    if output_file.endswith(".xlsx"):
        df.to_excel(output_file, index=False)
    else:
        df.to_csv(output_file, index=False)

    print(f"Prepared actual FDR input saved to: {output_file}")
    print(f"TARGET TITLE filled: {target_title_filled}")
    print(f"QUERY PEPTIDE filled: {query_peptide_filled}")

    if peptide_duplicates:
        print(f"Warning: {len(peptide_duplicates)} duplicate PEPTIDE entries in target MGF.")

    if title_duplicates:
        print(f"Warning: {len(title_duplicates)} duplicate TITLE entries in query MGF.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prepare annotated SPLISUM result table for actual FDR calculation."
    )

    parser.add_argument("--msslash_txt", required=True)
    parser.add_argument("--target_mgf", required=True)
    parser.add_argument("--query_mgf", required=True)
    parser.add_argument("--output", required=True)

    parser.add_argument(
        "--target_library_excel",
        default=None,
        help="Optional Excel file containing target library SMILES for existence checking."
    )

    parser.add_argument(
        "--target_library_smiles_col",
        default="PEPTIDE",
        help="SMILES column in target library Excel."
    )

    args = parser.parse_args()

    prepare_actual_fdr_input(
        msslash_txt=args.msslash_txt,
        target_mgf=args.target_mgf,
        query_mgf=args.query_mgf,
        output_file=args.output,
        target_library_excel=args.target_library_excel,
        target_library_smiles_col=args.target_library_smiles_col,
    )