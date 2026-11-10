#!/usr/bin/env bash
set -euo pipefail

python_bin="${PYTHON_BIN:-.venv/bin/python}"

"${python_bin}" -m src.main \
  --config configs/paper/cifar10_iid_hfedsa_ddpg_scaling.yaml \
  --num_clients 20 \
  --clients_per_round 5 \
  --rounds 1 \
  --local_epochs 1 \
  --output_dir results/smoke/cifar10_c_real

