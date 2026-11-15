#!/usr/bin/env bash
set -u

repo_root="${1:-.}"
queue_file="${2:-configs/pilot/queue_20261116.txt}"
max_parallel="${MAX_PARALLEL:-10}"
poll_seconds="${POLL_SECONDS:-30}"

cd "$repo_root" || exit 1
source_revision="$(git rev-parse HEAD)"
scheduler_log="logs/pilot/queue_20261116_scheduler.log"
mkdir -p logs/pilot

active_count() {
  pgrep -af '^.venv/bin/python -m src.main --config ' \
    | sed -E 's/^[0-9]+ //' \
    | sort -u \
    | wc -l
}

log_event() {
  printf '%s | %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" | tee -a "$scheduler_log"
}

while IFS= read -r config_path; do
  case "$config_path" in
    ""|\#*) continue ;;
  esac

  while [ "$(active_count)" -ge "$max_parallel" ]; do
    sleep "$poll_seconds"
  done

  config_base="$(basename "$config_path" .yaml)"
  run_log="logs/pilot/${config_base}_20261116.log"
  log_event "launching ${config_path} -> ${run_log}"
  nohup env \
    HFEDSA_SOURCE_REVISION="$source_revision" \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=. \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    .venv/bin/python -m src.main --config "$config_path" \
    > "$run_log" 2>&1 < /dev/null &
  sleep 2
done < "$queue_file"

log_event "all preregistered queue entries launched"

