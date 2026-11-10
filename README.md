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
- stratified round sampling that preserves malicious and unseen-client ratios;
- label-flipping, scaling, backdoor-scaling, and adaptive feature-matched attack utilities.

The remaining work is focused on real shifted-dataset adapters, missing comparison baselines and attacks, full paper experiment manifests, and multi-seed result generation.

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

