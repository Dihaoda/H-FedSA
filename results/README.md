# Results policy

`results/` is the local destination for generated experiments. Run directories,
checkpoints, raw metrics, and smoke outputs are ignored by Git.

Only reviewed, measured summaries belong in `results/published/`. Each published
summary must identify the exact configuration, commit, seeds, dataset source,
and whether the numbers are measured, synthetic, or illustrative. Smoke output
must never be promoted as a paper result.

Published measured summaries:

- `published/cifar10_iid_clean_fedavg_5seeds.json`: CIFAR-10 IID, no attack,
  FedAvg, seeds 2026--2030; final error `15.088 +/- 0.360%`.
- `published/cifar10_iid_hfedsa_ddpg_scaling_5seeds.json`: CIFAR-10 IID,
  H-FedSA-DDPG under backdoor scaling, seeds 2026--2030; final error
  `15.770 +/- 0.317%` and ASR `1.476 +/- 0.172%`.
