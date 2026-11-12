# H-FedSA label-flipping formal campaign

The candidate and seed list are frozen in
`configs/paper/cifar10_iid_hfedsa_ddpg_label_flip.yaml`. All reported values
use the final round only, and completed seeds are never rerun or selected by
outcome.

## Completed

- Seed `2026`: accuracy `82.75%`, error `17.25%`, TPR `97.4%`, FPR
  `0.75%`.
- Seed `2027`: accuracy `84.10%`, error `15.90%`, TPR `98.0%`, FPR
  `0.80%`.
- Seed `2028`: accuracy `84.87%`, error `15.13%`, TPR `96.8%`, FPR
  `2.00%`.
- Seed `2029`: accuracy `84.97%`, error `15.03%`, TPR `97.4%`, FPR
  `2.00%`.
- Every run completed 250/250 rounds on real CIFAR-10/CIFAR-10-C. No completed
  run had a GMM fallback, non-finite diagnostic, or weight-collapse alert.
- The provisional four-seed error is `15.828 +/- 1.025%` (sample standard
  deviation). It is not the final paper comparison.

## Remaining

Run the final seed `2030` unchanged:

```bash
HFEDSA_SOURCE_REVISION=75705eac0a3586aca246e75ba46729a2dfebf1f0 \
  PYTHONPATH=. .venv/bin/python -m src.main \
  --config configs/paper/cifar10_iid_hfedsa_ddpg_label_flip.yaml \
  --seed 2030
```

After completion, archive the same evidence set and generate the fixed
five-seed final-round aggregate.
