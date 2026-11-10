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
- the paper's three security features and a three-component full-covariance GMM;
- the 39-dimensional DDPG state (GMM means, full covariances, validation loss,
  validation-loss change, and previous beta).

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

