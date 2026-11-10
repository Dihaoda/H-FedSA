# AutoDL setup

Keep source code on the system disk and datasets/results on the data disk. The
commands below assume the repository is at `/root/H-FedSA` and the persistent
data disk is `/root/autodl-tmp`.

```bash
cd /root/H-FedSA
python -m venv --system-site-packages .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt

mkdir -p /root/autodl-tmp/datasets
ln -s /root/autodl-tmp/datasets /root/H-FedSA/data

bash scripts/download_cifar10_c.sh data/cifar10-c-download
.venv/bin/python -m pytest -q
bash scripts/smoke_cifar10_c.sh
```

If `data` already exists, inspect it before creating the symlink. Never put SSH
credentials, tokens, `.env` files, downloaded datasets, or run checkpoints in
the repository.

The smoke command uses real CIFAR-10/CIFAR-10-C data but deliberately reduces
the client and round counts. Its output validates infrastructure only and must
not be reported as a paper result. Formal runs use the YAML values without
these CLI overrides and should be repeated across documented seeds.

