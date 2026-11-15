#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 6 ]; then
  echo "usage: $0 RESULT_DIR TRAINING_LOG ARTIFACT_DIR VARIANT ATTACK_TRACE ARCHIVE_TGZ" >&2
  exit 2
fi

result_dir="$1"
training_log="$2"
artifact_dir="$3"
variant="$4"
attack_trace="$5"
archive_tgz="$6"

if [ ! -d "$result_dir" ]; then
  echo "missing result directory: $result_dir" >&2
  exit 1
fi
if [ ! -f "$training_log" ]; then
  echo "missing training log: $training_log" >&2
  exit 1
fi

mkdir -p "$artifact_dir"
for name in \
  "aggregation_debug_${variant}.csv" \
  client_label_distribution.csv \
  config.yaml \
  config_resolved.yaml \
  data_diagnostics.json \
  "hfedsa_beta_trace_${variant}.csv" \
  hfedsa_diagnostic_summary.csv \
  "hfedsa_round_diagnostics_${variant}.csv" \
  metrics.csv \
  partition_summary.json \
  run_summary.json \
  summary.json \
  "$attack_trace"
do
  if [ -f "$result_dir/$name" ]; then
    cp "$result_dir/$name" "$artifact_dir/"
  fi
done
cp "$training_log" "$artifact_dir/training.log"

(
  cd "$artifact_dir"
  sha256sum -- * > SHA256SUMS
)
tar -czf "$archive_tgz" -C "$(dirname "$artifact_dir")" "$(basename "$artifact_dir")"
echo "$archive_tgz"

