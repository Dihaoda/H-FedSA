# H-FedSA label-flipping formal campaign

The candidate and seed list are frozen in
`configs/paper/cifar10_iid_hfedsa_ddpg_label_flip.yaml`. The campaign was
paused at the user's request after seed `2026`; no later seed was started.

## Completed

- Seed `2026`: 250/250 rounds, real CIFAR-10/CIFAR-10-C, final accuracy
  `82.75%`, final error `17.25%`, malicious TPR `97.4%`, non-malicious FPR
  `0.75%`, no GMM fallback, non-finite diagnostic, or weight-collapse alert.
- The result is outside the paper's `15.7 +/- 0.4%` error interval and must
  remain in the eventual five-seed aggregate.

## Remaining

Run seeds `2027`, `2028`, `2029`, and `2030` unchanged. On a replacement
server, restore the repository and datasets, then use:

```bash
HFEDSA_SOURCE_REVISION=<current-github-commit> PYTHONPATH=. .venv/bin/python \
  -m src.main \
  --config configs/paper/cifar10_iid_hfedsa_ddpg_label_flip.yaml \
  --seed 2027
```

After each seed, archive `config_resolved.yaml`, `run_summary.json`,
`summary.json`, `metrics.csv`, H-FedSA round/diagnostic summaries, and the
maximum-share client-detail round before moving to the next seed.
