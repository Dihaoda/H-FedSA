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

## Completed formal FedAvg anchor

After the shared protocol was frozen, every preregistered seed (`2026` through
`2030`) was run without per-seed parameter changes. The measured final error was
`15.088 +/- 0.360%` (sample standard deviation), a mean gap of `+0.088`
percentage points from Table II(d). The portable summary and per-run provenance
are published at
`results/published/cifar10_iid_clean_fedavg_5seeds.json`.

## Completed formal FLTrust anchor

The same frozen clean protocol was run with FLTrust's documented default
`min_trust_score=0.0` for every preregistered seed. The measured final error was
`15.614 +/- 0.595%`, a mean gap of `+0.214` percentage points from Table II(d)'s
`15.4 +/- 0.4%`. No per-seed parameters or checkpoints were selected. The
dedicated manifest and portable result are
`configs/paper/cifar10_iid_clean_fltrust.yaml` and
`results/published/cifar10_iid_clean_fltrust_5seeds.json`.

## Completed formal RFA anchor

RFA was run under the same frozen clean protocol with a geometric-median
solver capped at 20 iterations (`tol=1e-5`, `eps=1e-8`). Across the five
preregistered seeds, the measured final error was `15.144 +/- 0.209%`, a mean
gap of `-0.056` percentage points from Table II(d)'s `15.2 +/- 0.3%`. Every
run completed all 250 rounds on real data; final-round metrics, rather than
best checkpoints, were aggregated. The dedicated manifest and portable result
are `configs/paper/cifar10_iid_clean_rfa.yaml` and
`results/published/cifar10_iid_clean_rfa_5seeds.json`.

## Completed formal SafeFL-compatible SignGuard anchor

The public SafeFL SignGuard profile was run under the same frozen clean
protocol with a 10% deterministic sign-coordinate sample and median-norm
bounds `[0.1, 3.0]`. Across the five preregistered seeds, the measured final
error was `15.430 +/- 0.202%`, a mean gap of `+0.130` percentage points from
the H-FedSA paper's SafeFL target `15.3 +/- 0.3%`. All runs completed 250
rounds on real data with final-round aggregation. Because the paper does not
name its selected SafeFL rule, the result remains labeled SafeFL-compatible
SignGuard. The manifest and result are
`configs/paper/cifar10_iid_clean_safefl_signguard.yaml` and
`results/published/cifar10_iid_clean_safefl_signguard_5seeds.json`.

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

The error is close to target, but the ASR remains too high. An attack-only
candidate therefore changed only `poison_fraction` from `1.0` to `0.5`; target
label, update scale, seed, model, defense, and training protocol remained
frozen. It finished at `84.30%` accuracy / `15.70%` error and `4.76%` ASR. The
weaker poisoning was rejected because it made the malicious update more similar
to an ordinary client update and increased, rather than decreased, measured
ASR. Full-batch poisoning remains the selected target-2 candidate.

Because the paper does not specify a target class, one final independent-seed
candidate changed only the target from class 2 to class 0. It finished at
`84.51%` accuracy / `15.49%` error and `1.78%` ASR. The gaps to Table II(d)
were `+0.29` error and `+0.58` ASR. Target 0 was selected before formal seeds:
it brought error inside the paper's reported error standard deviation and
reduced ASR by `0.69` points relative to target 2. No further target classes
will be searched.

## Completed formal H-FedSA scaling result

The frozen target-0 protocol was then run for every preregistered seed (`2026`
through `2030`) without per-seed parameter changes. The measured final error was
`15.770 +/- 0.317%`, a mean gap of `+0.570` percentage points from the Table
II(d) H-FedSA target. The measured ASR was `1.476 +/- 0.172%`, a mean gap of
`+0.276` points and therefore within the paper's reported `1.2 +/- 0.3%` ASR
range. All values are final-round measurements; no best checkpoint or favorable
seed was selected. The portable summary and per-run provenance are published at
`results/published/cifar10_iid_hfedsa_ddpg_scaling_5seeds.json`.

## H-FedSA clean-anchor diagnostics

The strict direct-FedAvg candidate exposed a no-attack edge case: a fixed
three-component GMM must label one component as malicious even when every
participant is benign. In the measured clean run, the highest-to-middle
intensity ratio had median `1.04` and maximum `1.63`; in the scaling-attack run,
the corresponding minimum was `15.16` and the median was `22.42`.

A label-free continuous role-confidence extension was implemented as an
opt-in candidate, but its `server_lr=1.0` run was stopped at round 48 after
underperforming both the strict interpretation and FedAvg at matched rounds.
Reducing `server_lr` to `0.7` worsened the matched curve and was stopped at
round 29. Interpreting the paper's undefined `NormalizeUpdate` operation as no
root-norm scaling was also rejected after round 60 (`70.29%` accuracy versus
`73.53%` for the strict interpretation). All partial metrics remain in the
calibration tree and are excluded from formal summaries.

The repository's pre-existing FedAvgM server optimizer was also checked with
otherwise unchanged H-FedSA settings. It reached only `68.06%` at round 60,
versus `73.53%` for the strict direct-update interpretation, and was stopped.
Increasing local epochs from 5 to 8 caused large aggregation norms and was
stopped at round 80. The intermediate 6-epoch candidate reached `74.09%` at
round 100, below the strict candidate's `76.71%`, and was also stopped.

The strict 5-epoch clean H-FedSA candidate itself reached `81.53%` at round 192
before calibration was stopped. No clean H-FedSA candidate has therefore been
promoted to formal results. This unresolved gap is retained explicitly rather
than substituting a target value or selecting a favorable partial checkpoint.

## Remaining reproduction gap

- investigate the clean H-FedSA gap only if an additional implementation detail
  or author-provided hyperparameter becomes available.

