# H-FedSA label-flipping formal campaign

The candidate and seed list are frozen in
`configs/paper/cifar10_iid_hfedsa_ddpg_label_flip.yaml`. All reported values
use the final round only, and completed seeds were never rerun or selected by
outcome.

## Completed results

- Seed `2026`: accuracy `82.75%`, error `17.25%`, mean malicious TPR
  `97.4%`, mean non-malicious FPR `0.75%`.
- Seed `2027`: accuracy `84.10%`, error `15.90%`, mean malicious TPR
  `98.0%`, mean non-malicious FPR `0.80%`.
- Seed `2028`: accuracy `84.87%`, error `15.13%`, mean malicious TPR
  `96.8%`, mean non-malicious FPR `2.00%`.
- Seed `2029`: accuracy `84.97%`, error `15.03%`, mean malicious TPR
  `97.4%`, mean non-malicious FPR `2.00%`.
- Seed `2030`: accuracy `83.87%`, error `16.13%`, mean malicious TPR
  `98.0%`, mean non-malicious FPR `0.40%`.

Every run completed 250/250 rounds on real CIFAR-10/CIFAR-10-C. No run had a
GMM fallback, non-finite diagnostic, or weight-collapse alert.

The fixed five-seed final-round result is `15.888 +/- 0.898%` error and
`84.112 +/- 0.898%` accuracy (sample standard deviation). The measured error
mean is `+0.188` percentage points from the paper's `15.7 +/- 0.4%` and is
inside that reported interval; the measured between-seed standard deviation is
larger.

The machine-readable aggregate is
`results/published/cifar10_iid_hfedsa_ddpg_label_flip_5seeds.json`. Each seed
directory contains its resolved configuration, metrics, diagnostics, run
summary, and compact summary.
