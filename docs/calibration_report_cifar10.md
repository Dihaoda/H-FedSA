# CIFAR-10 Table II(d) calibration report

This report records measured calibration decisions. Calibration used the
independent seed `31415`; the formal seeds remain fixed at `2026` through
`2030`. Values below came from real CIFAR-10/CIFAR-10-C runs with synthetic
fallback disabled. Calibration outputs are excluded from formal summaries.

## Frozen shared clean-training protocol

- 100 total clients; 10 sampled per round;
- IID base partition, 10% unseen clients, and 40% shifted data per unseen
  client;
- two-convolution/two-fully-connected paper CNN without BatchNorm;
- 250 communication rounds, 5 local epochs, SGD learning rate `0.050` with
  cosine decay, and direct FedAvg server updates;
- sample-count aggregation, 500 trusted-root samples, and evaluation every 10
  rounds plus the final five rounds.

The selected strict FedAvg anchor finished at `84.40%` accuracy / `15.60%`
error. The Table II(d) target is `15.0 +/- 0.3%` error, so the independent-seed
gap is `+0.60` percentage points. Direct FedAvg was preferred over the closer
FedAvgM candidates because the paper presents FedAvg as its non-defensive
baseline and its H-FedSA algorithms do not specify a server-momentum term.

## Completed clean candidates

| Candidate | Final accuracy | Final error | Gap to 15.0 | Decision |
|---|---:|---:|---:|---|
| FedAvg, 250 rounds, 5 local epochs, lr 0.050 | 84.40 | 15.60 | +0.60 | Selected shared protocol |
| FedAvgM, 170 rounds, 5 local epochs | 85.83 | 14.17 | -0.83 | Rejected: server-momentum deviation and too strong |
| FedAvgM, 200 rounds, 4 local epochs | 86.92 | 13.08 | -1.92 | Rejected: server-momentum deviation and too strong |

The FedAvgM 250-round candidate was stopped after round 38 because the
170-round candidate had already overshot the target and historical 250-round
evidence was stronger still. The direct-FedAvg `lr=0.055` candidate was stopped
after round 202: at round 200 it measured `83.84%`, below the selected
`lr=0.050` curve's `84.24%` at the same checkpoint.

## Completed historical attack comparison

The historical-match attack candidate used H-FedSA-DDPG with FedAvgM, 300
rounds, target label 2, full-batch trigger poisoning, and update scale 8. It
finished at `84.77%` accuracy / `15.23%` error and `2.72%` ASR. The paper
targets are `15.2 +/- 0.3%` error and `1.2 +/- 0.3%` ASR. The error gap was only
`+0.03`, but the ASR gap was `+1.52`; moreover, FedAvgM is not the paper-strict
server update. This run is retained only as a measured historical comparison.

## Completed paper-strict attack candidate

With the frozen direct-FedAvg training protocol, target label 2, full-batch
trigger poisoning, update scale 8, and a DDPG exploration floor of `0.1`, the
paper-strict candidate finished at `84.38%` accuracy / `15.62%` error and
`2.47%` ASR. The gaps to the Table II(d) H-FedSA targets were `+0.42` error and
`+1.27` ASR. The exploration floor was retained because it improved accuracy
and ASR at matched rounds 60, 80, and 100 by preventing the DDPG policy from
zeroing the contribution of the entire GMM unseen-data component.

The error is close to target, but the ASR remains too high. A final attack-only
candidate therefore changes only `poison_fraction` from `1.0` to `0.5`; target
label, update scale, seed, model, defense, and training protocol remain frozen.

## Pending before formal launch

- finish the half-batch-poisoning attack candidate;
- finish the no-attack H-FedSA clean anchor under the frozen shared protocol;
- freeze the defense/attack-only parameters, then launch every preregistered
  seed without per-seed changes.

