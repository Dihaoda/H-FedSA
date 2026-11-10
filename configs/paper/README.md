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

The paper specifies a lightweight two-convolution/two-fully-connected network
but does not report BatchNorm or all optimizer hyperparameters. This manifest
therefore disables BatchNorm (so running-statistic buffers cannot dominate the
paper's update features) and records the remaining reconstruction defaults
explicitly in YAML. These defaults are parameters to validate empirically, not
claims copied from the paper.

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
local epochs and FedAvgM, and compares FedAvg with H-FedSA from the same initial
model. The 250-round budget was selected during seed-2026 calibration before
the five formal seeds were run; it must not be changed per seed or per method.

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

