# FLTrust label-flipping formal campaign

The manifest `configs/paper/cifar10_iid_fltrust_label_flip.yaml` freezes the
same real CIFAR-10/CIFAR-10-C data path, client-role sampling, optimization
budget, deterministic `y -> 9 - y` attack, and final-round-only reporting rule
used by the completed H-FedSA and FedAvg label-flipping campaigns. The defense
is FLTrust with `min_trust_score: 0.0`.

## Completed

- Seed `2026`: final accuracy `82.91%`, final error `17.09%`, best
  accuracy `83.12%`, runtime `3053.382` seconds.

The paper target is `17.3 +/- 1.0%` error. Seed 2026 is inside that interval,
but no campaign-level comparison is claimed until all five preregistered seeds
(`2026`-`2030`) finish.

## In progress

- Seed `2027` is running.
- Seeds `2028`, `2029`, and `2030` remain preregistered.

Each completed seed directory archives the resolved configuration, final-round
metrics, aggregation diagnostics, FLTrust scaling diagnostics, data and
partition diagnostics, run summary, and compact summary. Large model
checkpoints remain on the execution server and are not required to verify the
reported scalar result.
