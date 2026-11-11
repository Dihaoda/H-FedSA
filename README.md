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

- FedAvg, FLTrust, RFA, H-FedSA, SafeFL-compatible SignGuard, and MSGuard aggregation;
- the paper's direction, intensity, and normalized-sparsity client features;
- three-component full-covariance GMM client profiling;
- paper-form probabilistic aggregation weights;
- DDPG exploration control using GMM statistics and server-root validation signals;
- deterministic partial unseen-data shifts via `unseen_data_fraction`;
- a memory-mapped CIFAR-10-C adapter for Gaussian-noise and shot-noise unseen data;
- stratified round sampling that preserves malicious and unseen-client ratios;
- label-flipping, scaling, backdoor-scaling, Krum-targeted, Trim-targeted,
  adaptive feature-matched, and synchronous PoiSAFL attack utilities.
- a capability-registry test that instantiates every public defense and
  validates every public attack name, plus GitHub Actions unit tests.

The remaining work is focused on real-data validation of the non-CIFAR shifted
adapters, the remaining paper experiment manifests, and multi-seed result
generation. See
[`docs/baselines_and_attacks.md`](docs/baselines_and_attacks.md) for the exact
semantics and limitations of comparison methods whose original artifacts are
ambiguous or unavailable.

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

The completed five-seed CIFAR-10 IID results currently include clean FedAvg
(`15.088 +/- 0.360%` error), clean FLTrust (`15.614 +/- 0.595%` error), clean
RFA (`15.144 +/- 0.209%` error), SafeFL-compatible SignGuard
(`15.430 +/- 0.202%` error), MSGuard published-component implementation
(`15.504 +/- 0.227%` error), clean H-FedSA-DDPG with the preregistered
no-attack presence gate (`15.094 +/- 0.264%` error), and H-FedSA-DDPG under backdoor scaling
(`15.770 +/- 0.317%` error, `1.476 +/- 0.172%` ASR). The RFA, FLTrust,
SafeFL-compatible, and MSGuard means differ from their paper targets by
`-0.056`, `+0.214`, `+0.130`, and `+0.304` percentage points respectively.
The MSGuard mean is `0.004` points above the paper's one-standard-deviation
upper bound; the other three clean-defense means are inside their reported
ranges. For H-FedSA scaling, ASR is inside the reported range while error
remains `+0.570` points above the paper mean.
The clean H-FedSA result is `-0.606` points below the paper mean; it is retained
as measured rather than being degraded or post-hoc tuned to the target.

## Documentation

- [`configs/paper/README.md`](configs/paper/README.md): paper-protocol manifests and data layout
- [`docs/autodl.md`](docs/autodl.md): AutoDL data-disk setup and real-data smoke command
- [`docs/calibration_protocol.md`](docs/calibration_protocol.md): measured calibration and fixed-seed reporting rules
- [`docs/baselines_and_attacks.md`](docs/baselines_and_attacks.md): runnable baseline/attack semantics and limitations
- [`docs/dataset_adapters.md`](docs/dataset_adapters.md): external shifted-data layouts and label mapping
- [`docs/reproduction_status.md`](docs/reproduction_status.md): implemented, tested, and pending work
- [`results/README.md`](results/README.md): measured-result publication policy

