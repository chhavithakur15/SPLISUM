# SPLISUM

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-Academic%20Use-informational)

**SPLISUM** (Spectral Prediction and Library Searching for Untargeted Metabolomics) is a Python package for metabolite identification using predicted spectral libraries, target–decoy-based false discovery rate (FDR) estimation, structural validation, and cluster-aware analysis.

---

## Overview

SPLISUM provides an end-to-end workflow:

- MGF preprocessing and standardization  
- Ion-mode and collision-energy filtering  
- 50 ppm complete-linkage precursor-mass binning  
- msCRUSH-based clustering and library organization  
- Decoy generation via local precursor-mass reshuffling  
- Spectral search using **msSLASH**  
- Estimated FDR calculation (target–decoy)  
- Structural validation using **MCES (edit similarity)**  
- Comparison of estimated vs actual FDR  

---

## External Dependencies

SPLISUM requires:

- **msSLASH** (spectral search)  
- **msCRUSH** (clustering)

Provide paths when running:

    --msslash_path /path/to/bruteforce
    --mscrush_path /path/to/mscrush

---

## Getting Started

### Run the full pipeline

    python -m splisum.workflow.run_pipeline \
      --input_library input_library.mgf \
      --query_mgf query.mgf \
      --target_library_excel target_library.xlsx \
      --msslash_path /path/to/bruteforce \
      --mscrush_path /path/to/mscrush \
      --outdir results

---

## Detailed Pipeline

### Step 1: Standardizing MGF Files

Standardizes metadata fields such as `PEPMASS`, `PRECURSOR_MZ`, and `CHARGE`.

Why: Ensures compatibility with downstream tools like msSLASH.

    python -m splisum.io.mgf \
      --input input_library.mgf \
      --output standardized_library.mgf

---

### Step 2: Filtering by Ion Mode and Collision Energy

Filters spectra to retain only:

- Positive mode: `[M+H]+`  
- Negative mode: `[M-H]-`  
- Collision energy: **20 eV**

Why: Fragmentation patterns depend on acquisition conditions; mixing them reduces match quality.

    python -m splisum.library.filter \
      --input standardized_library.mgf \
      --output positive_20ev.mgf \
      --mode positive \
      --energy 20

---

### Step 3: 50 ppm Complete-Linkage Binning

Groups spectra into precursor-mass bins using a 50 ppm constraint.

Why: Prevents loose grouping and preserves realistic mass structure.

    python -m splisum.library.binning \
      --input positive_20ev.mgf \
      --output_folder binned_spectra \
      --ppm 50

---

### Step 4: msCRUSH Clustering

Clusters spectra to generate representative spectra and reduce redundancy.

Why: Improves library organization and stabilizes downstream decoy generation.

    python -m splisum.clustering.mscrush \
      --mscrush_path /path/to/mscrush \
      --input positive_20ev.mgf \
      --output_prefix clusters/clusters

    python -m splisum.clustering.parse \
      --input clusters \
      --output mscrush_cluster_statistics.xlsx

---

### Step 5: Decoy Generation

Generates decoy spectra by reassigning precursor masses across nearby bins while keeping fragment peaks unchanged.

Why: Produces realistic incorrect matches required for FDR estimation.

    python -m splisum.decoy.generate \
      --input_folder binned_spectra \
      --output_folder decoy_spectra \
      --seed 42

---

### Step 6: Merge Decoy Library

Combines all decoy spectra into a single file.

    python -m splisum.library.combine \
      merge-folder \
      --input_folder decoy_spectra \
      --output decoy_library.mgf

---

### Step 7: Spectral Search (msSLASH)

Matches query spectra against both target and decoy libraries.

Why: Core identification step.

    python -m splisum.search.msslash \
      --msslash_path /path/to/bruteforce \
      --library positive_20ev.mgf \
      --query query.mgf \
      --decoy decoy_library.mgf \
      --output msslash_output.txt

---

### Step 8: Estimated FDR

Estimated FDR is computed as:

    Estimated FDR = (# Decoy Hits) / (# Target Hits)

Why: Provides a fast statistical estimate of false positives.

    python -m splisum.fdr.estimated \
      --input msslash_output.txt \
      --output estimated_fdr.xlsx

---

### Step 9: Prepare Input for Actual FDR

Maps query and target compounds and computes edit similarity (MCES).

Why: Enables structure-based validation of matches.

    python -m splisum.fdr.prepare_actual_fdr_input \
      --msslash_txt msslash_output.txt \
      --target_mgf positive_20ev.mgf \
      --query_mgf query.mgf \
      --target_library_excel target_library.xlsx \
      --output actual_fdr_input.xlsx

---

### Step 10: Actual FDR Calculation

Classifies matches into:

- Exact Match  
- Stereoisomer  
- Highly Similar (≥ 0.9)  
- Not Identical (< 0.9)

Actual FDR is computed as:

    Actual FDR = Not Identical / Total

Why: Measures true correctness using structural similarity.

    python -m splisum.fdr.actual_fdr \
      --input actual_fdr_input.xlsx \
      --output actual_fdr.xlsx

---

### Step 11: Compare Estimated vs Actual FDR

Generates comparison table and visualization.

Why: Highlights the gap between statistical and structural validation.

    python -m splisum.postprocess.compare_fdr \
      --estimated estimated_fdr.xlsx \
      --actual actual_fdr.xlsx \
      --output_table fdr_comparison.xlsx \
      --output_plot fdr_comparison.png

---

## Key Insight

Estimated FDR < Actual FDR

Estimated FDR is based on decoy matches, whereas actual FDR reflects structural correctness.

---

## Pipeline

    Input MGF
       ↓
    Standardization
       ↓
    Filtering (mode + energy)
       ↓
    50 ppm Binning
       ↓
    msCRUSH Clustering
       ↓
    Decoy Generation
       ↓
    Target + Decoy Libraries
       ↓
    msSLASH Search
       ↓
    Estimated FDR
       ↓
    MCES (Edit Similarity)
       ↓
    Actual FDR
       ↓
    FDR Comparison