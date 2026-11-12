# FedAvg label-flipping formal campaign

The manifest `configs/paper/cifar10_iid_fedavg_label_flip.yaml` freezes the
same real CIFAR-10/CIFAR-10-C data path, client-role sampling, optimization
budget, deterministic `y -> 9 - y` attack, and final-round-only reporting rule
used for the completed H-FedSA label-flipping campaign. Only the defense changes
to standard FedAvg; no H-FedSA or DDPG parameters are active.

## Completed

- Seed `2026`: final accuracy `80.64%`, final error `19.36%`, best
  accuracy `81.07%`, runtime `2869.969` seconds.

The paper target is `72.0 +/- 4.5%` error. This first measured seed is
`-52.64` percentage points from the paper mean and is therefore an explicit
reproduction gap, not a matched result. The remaining preregistered seeds are
`2027` through `2030`; no final aggregate is reported until all five finish.

Each seed directory archives the resolved configuration, final-round metrics,
aggregation diagnostics, data and partition diagnostics, run summary, and
compact summary. Large model checkpoints remain on the execution server and
are not required to verify the reported scalar result.
