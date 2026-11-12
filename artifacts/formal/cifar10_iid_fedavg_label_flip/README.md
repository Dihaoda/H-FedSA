# FedAvg label-flipping formal campaign

The manifest `configs/paper/cifar10_iid_fedavg_label_flip.yaml` freezes the
same real CIFAR-10/CIFAR-10-C data path, client-role sampling, optimization
budget, deterministic `y -> 9 - y` attack, and final-round-only reporting rule
used for the completed H-FedSA label-flipping campaign. Only the defense changes
to standard FedAvg; no H-FedSA or DDPG parameters are active.

## Completed

- Seed `2026`: final accuracy `80.64%`, final error `19.36%`, best
  accuracy `81.07%`, runtime `2869.969` seconds.
- Seed `2027`: final accuracy `80.38%`, final error `19.62%`, best
  accuracy `80.66%`, runtime `2803.725` seconds.
- Seed `2028`: final accuracy `81.52%`, final error `18.48%`, best
  accuracy `81.52%`, runtime `2855.513` seconds.
- Seed `2029`: final accuracy `81.00%`, final error `19.00%`, best
  accuracy `81.17%`, runtime `2834.908` seconds.

The paper target is `72.0 +/- 4.5%` error. The provisional four-seed result is
`19.115 +/- 0.494%` error (sample standard deviation), a mean gap of
`-52.885` percentage points. This is an explicit reproduction gap, not a
matched result. The final preregistered seed is `2030`; no final aggregate is
reported until all five finish.

Each seed directory archives the resolved configuration, final-round metrics,
aggregation diagnostics, data and partition diagnostics, run summary, and
compact summary. Large model checkpoints remain on the execution server and
are not required to verify the reported scalar result.
