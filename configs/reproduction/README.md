# Reproduction configurations

This directory contains one selected CIFAR-10 IID configuration for every applicable H-FedSA paper comparison cell whose measured final error met the repository acceptance criterion. FedAvg with Krum-targeted and Trim-targeted attacks is not applicable in the paper.

| Defense | No attack | Label flip | Scaling | Krum-targeted | Trim-targeted | Adaptive | PoiSAFL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FedAvg | ✓ | ✓ | ✓ | — | — | ✓ | ✓ |
| FLTrust | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| H-FedSA-DDPG | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| MSGuard | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| RFA | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| SafeFL-compatible SignGuard | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Run any configuration with:

```bash
python -m src.main --config configs/reproduction/cifar10_iid/<defense>/<scenario>.yaml
```

All selected configurations use real CIFAR-10 data, disable synthetic fallback, and report the final round. The FLTrust/PoiSAFL configuration is the explicitly identified 80-round accelerated protocol; it is not a 250-round paper-protocol claim.
