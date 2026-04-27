#!/bin/bash
python -m splisum.workflow.run_pipeline \
  --input_library examples/data/sample_library_negative.mgf \
  --query_mgf examples/data/sample_query_negative.mgf \
  --target_library_excel examples/data/sample_target_metadata.csv \
  --msslash_path /path/to/bruteforce \
  --mscrush_path /path/to/mscrush \
  --outdir examples/results/negative
