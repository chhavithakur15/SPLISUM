#!/bin/bash
python -m splisum.workflow.run_pipeline \
  --input_library examples/data/sample_library_positive.mgf \
  --query_mgf examples/data/sample_query_positive.mgf \
  --target_library_excel examples/data/sample_target_metadata.csv \
  --msslash_path /path/to/bruteforce \
  --mscrush_path /path/to/mscrush \
  --outdir examples/results/positive
