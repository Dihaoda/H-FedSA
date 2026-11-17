#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 QUEUE_FILE" >&2
  exit 2
fi

queue_file=$1
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

max_parallel=${HFEDSA_QUEUE_MAX_PARALLEL:-10}
poll_seconds=${HFEDSA_QUEUE_POLL_SECONDS:-300}
run_once=${HFEDSA_QUEUE_ONCE:-0}
dry_run=${HFEDSA_QUEUE_DRY_RUN:-0}
default_revision=${HFEDSA_SOURCE_REVISION:-unknown}

if [[ ! -f "$queue_file" ]]; then
  echo "queue file not found: $queue_file" >&2
  exit 2
fi
if ! [[ "$max_parallel" =~ ^[1-9][0-9]*$ ]]; then
  echo "HFEDSA_QUEUE_MAX_PARALLEL must be a positive integer" >&2
  exit 2
fi
if ! [[ "$poll_seconds" =~ ^[1-9][0-9]*$ ]]; then
  echo "HFEDSA_QUEUE_POLL_SECONDS must be a positive integer" >&2
  exit 2
fi

state_dir=${HFEDSA_QUEUE_STATE_DIR:-logs/calibration/queue_state}
mkdir -p "$state_dir"
queue_name=$(basename "$queue_file")
started_file="$state_dir/${queue_name}.started"
event_log="$state_dir/${queue_name}.events.log"
touch "$started_file" "$event_log"

lock_file="$state_dir/${queue_name}.lock"
exec 9>"$lock_file"
if ! flock -n 9; then
  echo "another queue runner already holds $lock_file" >&2
  exit 3
fi

timestamp() {
  date '+%Y-%m-%d %H:%M:%S %Z'
}

active_configs() {
  ps -eo args \
    | sed -n '/[.]venv\/bin\/python -m src.main --config/ s/.*--config \([^ ]*\).*/\1/p' \
    | sort -u
}

active_count() {
  active_configs | awk 'END { print NR + 0 }'
}

is_started() {
  local config_path=$1
  grep -Fqx -- "$config_path" "$started_file"
}

mark_started() {
  local config_path=$1
  if ! is_started "$config_path"; then
    printf '%s\n' "$config_path" >> "$started_file"
  fi
}

is_active() {
  local config_path=$1
  active_configs | grep -Fqx -- "$config_path"
}

start_entry() {
  local config_path=$1
  local log_path=$2
  local revision=$3

  if [[ ! -f "$config_path" ]]; then
    printf '%s | MISSING_CONFIG | %s\n' "$(timestamp)" "$config_path" | tee -a "$event_log" >&2
    mark_started "$config_path"
    return
  fi

  if is_active "$config_path"; then
    printf '%s | ALREADY_ACTIVE | %s\n' "$(timestamp)" "$config_path" | tee -a "$event_log"
    mark_started "$config_path"
    return
  fi

  if [[ -f "$log_path" ]] && grep -q 'Summary:' "$log_path"; then
    printf '%s | ALREADY_COMPLETE | %s | %s\n' "$(timestamp)" "$config_path" "$log_path" | tee -a "$event_log"
    mark_started "$config_path"
    return
  fi

  if [[ "$dry_run" == 1 ]]; then
    printf '%s | WOULD_START | %s | %s | revision=%s\n' "$(timestamp)" "$config_path" "$log_path" "$revision"
    return
  fi

  mkdir -p "$(dirname "$log_path")"
  mark_started "$config_path"
  HFEDSA_SOURCE_REVISION="$revision" \
  PYTHONUNBUFFERED=1 \
  PYTHONPATH=. \
  OMP_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 \
  OPENBLAS_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 \
    nohup .venv/bin/python -m src.main --config "$config_path" > "$log_path" 2>&1 &
  local pid=$!
  printf '%s | STARTED | pid=%s | %s | %s | revision=%s\n' \
    "$(timestamp)" "$pid" "$config_path" "$log_path" "$revision" | tee -a "$event_log"
}

run_cycle() {
  local active
  active=$(active_count)
  printf '%s | CYCLE | active=%s | limit=%s\n' "$(timestamp)" "$active" "$max_parallel" >> "$event_log"

  while IFS=$'\t' read -r config_path log_path revision extra; do
    [[ -z "${config_path:-}" || "$config_path" == \#* ]] && continue
    if [[ -n "${extra:-}" ]]; then
      printf '%s | INVALID_ENTRY | %s\n' "$(timestamp)" "$config_path" | tee -a "$event_log" >&2
      continue
    fi
    [[ -n "${log_path:-}" ]] || log_path="logs/calibration/$(basename "$config_path" .yaml)_queue.log"
    [[ -n "${revision:-}" ]] || revision=$default_revision
    is_started "$config_path" && continue

    active=$(active_count)
    if (( active >= max_parallel )); then
      break
    fi
    start_entry "$config_path" "$log_path" "$revision"
  done < "$queue_file"
}

while :; do
  run_cycle
  [[ "$run_once" == 1 ]] && break
  sleep "$poll_seconds"
done

