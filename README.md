# H-FedSA

Official implementation workspace for **H-FedSA: A Self-Adaptive Federated Learning Framework with Dynamic Probabilistic Client Security Analysis**.

This repository is being reconstructed incrementally from the research prototype. The current work focuses on:

- aligning the H-FedSA implementation with the paper;
- making dataset and attack protocols reproducible;
- providing configuration-driven experiments;
- recording measured and simulated/demo artifacts transparently;
- adding tests, environment specifications, and reproducibility documentation.

## Current Status

The core training pipeline is runnable and has been verified on an NVIDIA A100. The current implementation includes:

- FedAvg, FLTrust, RFA, and H-FedSA aggregation;
- the paper's direction, intensity, and normalized-sparsity client features;
- three-component full-covariance GMM client profiling;
- paper-form probabilistic aggregation weights;
- DDPG exploration control using GMM statistics and server-root validation signals;
- deterministic partial unseen-data shifts via `unseen_data_fraction`;
- a memory-mapped CIFAR-10-C adapter for Gaussian-noise and shot-noise unseen data;
- stratified round sampling that preserves malicious and unseen-client ratios;
- label-flipping, scaling, backdoor-scaling, and adaptive feature-matched attack utilities.

The remaining work is focused on the other shifted-dataset adapters, missing comparison baselines and attacks, the remaining paper experiment manifests, and multi-seed result generation.

## Quick Development Run

```bash
python -m venv --system-site-packages .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m src.main \
  --config configs/hfedsa_cifar10_quick.yaml \
  --rounds 1 \
  --output_dir results/smoke
```

The quick configuration may use a synthetic fallback and is intended only to validate the software path. Paper experiments will use explicit real-data configurations with synthetic fallback disabled.

## Paper-Protocol CIFAR-10 Run

The first real-data manifest is
`configs/paper/cifar10_iid_hfedsa_ddpg_scaling.yaml`. It uses CIFAR-10 plus
CIFAR-10-C, disables synthetic fallback, and records CLI overrides with every
run. See [`configs/paper/README.md`](configs/paper/README.md) for the expected
data layout and validation/smoke commands.

```bash
python -m src.main \
  --config configs/paper/cifar10_iid_hfedsa_ddpg_scaling.yaml \
  --dry_run
```

Generated checkpoints and measurements belong under `results/` and are ignored
by Git. Only summaries produced by a documented measured run should be promoted
to published result artifacts.

## Documentation

- [`configs/paper/README.md`](configs/paper/README.md): paper-protocol manifests and data layout
- [`docs/autodl.md`](docs/autodl.md): AutoDL data-disk setup and real-data smoke command
- [`docs/calibration_protocol.md`](docs/calibration_protocol.md): measured calibration and fixed-seed reporting rules
- [`docs/reproduction_status.md`](docs/reproduction_status.md): implemented, tested, and pending work
- [`results/README.md`](results/README.md): measured-result publication policy

