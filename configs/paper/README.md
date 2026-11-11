# Paper-protocol configurations

These configurations are intended for measured reproductions, not synthetic or
paper-targeted result generation. Output metrics are written by the training
code and are not stored as pre-filled measurements.

## CIFAR-10 with CIFAR-10-C

`cifar10_iid_hfedsa_ddpg_scaling.yaml` uses the paper protocol:

- 100 total clients and 10 selected clients per round;
- 20% malicious clients;
- 10% unseen clients, with exactly 40% shifted samples per unseen client;
- CIFAR-10-C Gaussian noise and shot noise at severity 3;
- the paper's pre-aggregation client-update normalization to the trusted root
  update norm;
- the paper's three security features and a three-component full-covariance GMM;
- the 39-dimensional DDPG state (GMM means, full covariances, validation loss,
  validation-loss change, and previous beta).

The paper's Scaling row reports both model error and backdoor ASR. The manifest
therefore uses the `backdoor_scaling` implementation (trigger poisoning plus
model-update scaling) and maps it to the paper target key `scaling`. The plain
`scaling` implementation is a label-flip/update-scaling stress test and is not
used for this Table II row.

The paper does not specify the target class, trigger-poisoning fraction, update
scale, DDPG action floor, or server momentum. Independent-seed calibration
selected target class 0, full-batch trigger poisoning, update scale 8, a DDPG
minimum beta of 0.1, and a direct FedAvg server update. Seed 31415 measured
`15.49%` final error and `1.78%` ASR; these parameters were then frozen before
the preregistered reporting seeds were launched.

The paper specifies a lightweight two-convolution/two-fully-connected network
but does not report BatchNorm or all optimizer hyperparameters. This manifest
therefore disables BatchNorm (so running-statistic buffers cannot dominate the
paper's update features) and records the remaining reconstruction defaults
explicitly in YAML. These defaults are parameters to validate empirically, not
claims copied from the paper.

`cifar10_iid_hfedsa_ddpg_label_flip.yaml` freezes the measured label-flipping
candidate for seeds `2026` through `2030`. It uses the deterministic
`y -> 9 - y` transform and an explicitly labeled compatibility extension: a
raw-weight floor of `0.05` applies only when the GMM assigns
`p_malicious < 0.3`. The independent confirmation seed `27182` measured
`15.68%` final error, `97.2%` malicious TPR, `0.8%` non-malicious FPR, and no
weight-collapse alerts. Because the floor is not specified by Algorithm 1,
formal results from this manifest must retain the compatibility qualifier.

Expected data layout:

```text
data/
  cifar10/
  cifar10-c-download/
    CIFAR-10-C/
      gaussian_noise.npy
      shot_noise.npy
      labels.npy
```

The CIFAR-10-C archive is available from the official Zenodo record
<https://zenodo.org/records/2535967>. Its archive MD5 is
`56bf5dcef84df0e2308c6dcbcbbd8499`.

## CIFAR-10 clean anchor

`cifar10_iid_clean.yaml` is the frozen clean calibration/formal manifest for
Table II(d). It disables malicious clients but retains the paper-default 10%
unseen clients with 40% shifted local samples. It uses 250 rounds with five
local epochs and a direct FedAvg server update, and compares FedAvg with
H-FedSA from the same initial model. The shared budget and learning rate were
selected with the independent calibration seed `31415` before the five formal
seeds were run; they must not be changed per seed or per method. The selected
FedAvg anchor measured `15.60%` error versus the paper's `15.0%` target. See
[`../../docs/calibration_report_cifar10.md`](../../docs/calibration_report_cifar10.md)
for the accepted and rejected candidates.

`cifar10_iid_clean_fltrust.yaml` reuses this frozen protocol and changes only
the defense to FLTrust with the explicit default `min_trust_score=0.0`. Its five
fixed-seed formal result is `15.614 +/- 0.595%` error versus the paper's
`15.4 +/- 0.4%`.

`cifar10_iid_clean_rfa.yaml` reuses the same protocol and changes only the
defense to RFA, with the geometric-median solver fixed at `max_iter=20`,
`tol=1e-5`, and `eps=1e-8`. Its five fixed-seed formal result is
`15.144 +/- 0.209%` error versus the paper's `15.2 +/- 0.3%`; the resolved
configuration and run summary for every seed are archived under
`artifacts/experiment-evidence/2026-11-11/cifar10_iid_clean_rfa/`.

`cifar10_iid_clean_safefl_signguard.yaml` reuses the same protocol and fixes
the public SafeFL-compatible SignGuard profile to a 10% deterministic
sign-coordinate sample and median-norm bounds `[0.1, 3.0]`. Its five-seed
formal result is `15.430 +/- 0.202%` error versus the paper's SafeFL column
`15.3 +/- 0.3%`. The compatibility qualifier is required because the H-FedSA
paper does not identify which SafeFL rule generated its column. Per-seed
resolved configurations and summaries are archived under
`artifacts/experiment-evidence/2026-11-11/cifar10_iid_clean_safefl_signguard/`.

`cifar10_iid_clean_msguard.yaml` reuses the shared protocol and fixes the
MSGuard published-component implementation to automatic Mean Shift bandwidth,
`quantile=0.3`, and `min_retained_fraction=0.5`. Its five-seed result is
`15.504 +/- 0.227%` error versus the paper's `15.2 +/- 0.3%`; the unrounded
mean is `0.004` points above the paper's one-standard-deviation upper bound.
Per-seed resolved configurations and summaries are archived under
`artifacts/experiment-evidence/2026-11-11/cifar10_iid_clean_msguard/`.

Validate the configuration without starting training:

```bash
python -m src.main \
  --config configs/paper/cifar10_iid_hfedsa_ddpg_scaling.yaml \
  --dry_run
```

For an infrastructure smoke test, keep the real datasets but shorten the run:

```bash
python -m src.main \
  --config configs/paper/cifar10_iid_hfedsa_ddpg_scaling.yaml \
  --num_clients 20 --clients_per_round 5 --rounds 1 --local_epochs 1 \
  --output_dir results/smoke/cifar10_c
```

## Independent attack calibration

`../calibration/cifar10_iid_hfedsa_ddpg_backdoor_seed31415.yaml` evaluates the
historical target-label-2/scale-8 backdoor candidate with the current 39-state,
paper-formula implementation. It uses the independent calibration seed `31415`
and retains the paper-default unseen-client shift. Its results are explicitly
excluded from formal summaries; after this one calibration run, the selected
attack parameters are frozen before seeds `2026` through `2030` are launched.

That historical candidate retains FedAvgM so it can be compared with the
prototype's earlier calibration. The paper-strict companion manifest,
`../calibration/cifar10_iid_hfedsa_ddpg_backdoor_strict_seed31415.yaml`, uses a
standard direct FedAvg server update. Algorithm 1 returns the normalized
aggregate directly, and the paper does not describe a server-momentum term;
the strict manifest therefore takes precedence when freezing the formal
protocol.
