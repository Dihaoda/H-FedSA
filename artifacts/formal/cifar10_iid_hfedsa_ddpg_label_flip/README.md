# H-FedSA label-flipping formal campaign

The candidate and seed list are frozen in
`configs/paper/cifar10_iid_hfedsa_ddpg_label_flip.yaml`. All reported values
use the final round only, and completed seeds are never rerun or selected by
outcome.

## Completed

- Seed `2026`: 250/250 rounds, final accuracy `82.75%`, final error
  `17.25%`, malicious TPR `97.4%`, non-malicious FPR `0.75%`.
- Seed `2027`: 250/250 rounds, final accuracy `84.10%`, final error
  `15.90%`, malicious TPR `98.0%`, non-malicious FPR `0.80%`.
- Both runs used real CIFAR-10/CIFAR-10-C data. Neither run had a GMM
  fallback, non-finite diagnostic, or weight-collapse alert.
- The provisional two-seed error is `16.575 +/- 0.955%` (sample standard
  deviation). It is not the final paper comparison.

## Remaining

Run seeds `2028`, `2029`, and `2030` unchanged:

```bash
HFEDSA_SOURCE_REVISION=75705eac0a3586aca246e75ba46729a2dfebf1f0 \
  PYTHONPATH=. .venv/bin/python -m src.main \
  --config configs/paper/cifar10_iid_hfedsa_ddpg_label_flip.yaml \
  --seed 2028
```

After each seed, archive `config_resolved.yaml`, `run_summary.json`,
`summary.json`, `metrics.csv`, H-FedSA round/diagnostic summaries, and the
maximum-share client-detail round before moving to the next seed.
