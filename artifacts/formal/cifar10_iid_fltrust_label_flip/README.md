# FLTrust label-flipping formal campaign

The manifest `configs/paper/cifar10_iid_fltrust_label_flip.yaml` freezes the
same real CIFAR-10/CIFAR-10-C data path, client-role sampling, optimization
budget, deterministic `y -> 9 - y` attack, and final-round-only reporting rule
used by the completed H-FedSA and FedAvg label-flipping campaigns. The defense
is FLTrust with `min_trust_score: 0.0`.

## Completed

- Seed `2026`: final accuracy `82.91%`, final error `17.09%`, best
  accuracy `83.12%`, runtime `3053.382` seconds.
- Seed `2027`: final accuracy `83.49%`, final error `16.51%`, best
  accuracy `83.59%`, runtime `3065.679` seconds.
- Seed `2028`: final accuracy `82.90%`, final error `17.10%`, best
  accuracy `82.94%`, runtime `3151.687` seconds.

The paper target is `17.3 +/- 1.0%` error. All three completed seeds are
inside that interval. Their non-final checkpoint statistic is
`16.900 +/- 0.338%` error and `83.100 +/- 0.338%` accuracy (sample standard
deviation). This is not the publishable campaign aggregate: preregistered
seeds `2029` and `2030` must still be included.

## Paused

The campaign was paused at the user's request after seed `2028`. Resume with
seed `2029`, then `2030`, using the unchanged manifest, declared source
revision `75705eac0a3586aca246e75ba46729a2dfebf1f0`, and final-round-only
selection rule. Do not rerun or replace seeds `2026`-`2028`.

Seed `2028` had an earlier foreground attempt interrupted at round 28 when
the AutoDL SSH connection was closed by the remote host. That partial attempt
is excluded. The complete 250-round background rerun is the only formal seed
2028 result; details are in `seed2028/restart_note.json`.

Each completed seed directory archives the resolved configuration, final-round
metrics, aggregation diagnostics, FLTrust scaling diagnostics, data and
partition diagnostics, run summary, and compact summary. Large model
checkpoints remain on the execution server and are not required to verify the
reported scalar result.
