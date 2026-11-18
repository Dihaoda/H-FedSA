# H-FedSA

Implementation of **H-FedSA: A Self-Adaptive Federated Learning Framework with Dynamic Probabilistic Client Security Analysis**.

Paper-aligned CIFAR-10 reproduction configurations are provided in [`configs/reproduction/`](configs/reproduction/).

```bash
pip install -r requirements.txt
python -m src.main --config configs/reproduction/cifar10_iid/hfedsa_ddpg/no_attack.yaml
```
