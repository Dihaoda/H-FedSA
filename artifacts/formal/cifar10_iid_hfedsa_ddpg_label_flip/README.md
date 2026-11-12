# H-FedSA label-flipping formal campaign

The candidate and seed list are frozen in
`configs/paper/cifar10_iid_hfedsa_ddpg_label_flip.yaml`. All reported values
use the final round only, and completed seeds are never rerun or selected by
outcome.

## Completed

- Seed `2026`: accuracy `82.75%`, error `17.25%`, malicious TPR
  `97.4%`, non-malicious FPR `0.75%`.
- Seed `2027`: accuracy `84.10%`, error `15.90%`, malicious TPR
  `98.0%`, non-malicious FPR `0.80%`.
- Seed `2028`: accuracy `84.87%`, error `15.13%`, malicious TPR
  `96.8%`, non-malicious FPR `2.00%`.
- Every run completed 250/250 rounds on real CIFAR-10/CIFAR-10-C. No completed
  run had a GMM fallback, non-finite diagnostic, or weight-collapse alert.
- The provisional three-seed error is `16.093 +/- 1.073%` (sample standard
  deviation). It is not the final paper comparison.

## Remaining

Run seeds `2029` and `2030` unchanged:

```bash
HFEDSA_SOURCE_REVISION=75705eac0a3586aca246e75ba46729a2dfebf1f0 \
  PYTHONPATH=. .venv/bin/python -m src.main \
  --config configs/paper/cifar10_iid_hfedsa_ddpg_label_flip.yaml \
  --seed 2029
```

After each seed, archive `config_resolved.yaml`, `run_summary.json`,
`summary.json`, `metrics.csv`, H-FedSA round/diagnostic summaries, and the
maximum-share client-detail round before moving to the next seed.
