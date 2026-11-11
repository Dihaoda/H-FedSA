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

## Completed formal MSGuard anchor

The documented MSGuard component implementation was run under the same frozen
clean protocol with automatic Mean Shift bandwidth estimation,
`quantile=0.3`, and a 50% minimum-retention floor. The five preregistered seeds
measured `15.504 +/- 0.227%` final error, a mean gap of `+0.304` percentage
points from Table II(d)'s `15.2 +/- 0.3%`. The unrounded mean is `0.004`
points above the paper's one-standard-deviation upper bound. All runs completed
250 rounds on real data and used final-round metrics. In the absence of a
public author artifact, the result is labeled a published-component
implementation. The manifest and result are
`configs/paper/cifar10_iid_clean_msguard.yaml` and
`results/published/cifar10_iid_clean_msguard_5seeds.json`.

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

### Preregistered no-attack presence-gate candidate

The paper-aligned implementation review confirmed that Algorithm 1 always
labels the highest-intensity GMM component as malicious, but does not define a
special case for an attack-free round. A new compatibility gate is therefore
implemented as an opt-in extension; the default remains the paper algorithm.
The gate uses only the current round's unlabeled GMM responsibilities and raw
update intensities. If the high-to-middle component intensity ratio is below
`3.0`, malicious posterior mass is released to the benign role and aggregation
uses the uniform raw client-update mean for that round.

The threshold was frozen before the new run. Recomputing the signal over the
192-round seed-31415 strict clean diagnostic gave a range of `1.0005` to
`1.9166` (median `1.0408`). The already completed five-seed scaling diagnostics
gave a range of `16.9426` to `107.3388` (median `28.7068`). Thus `3.0` lies in a
wide observed separation interval and does not depend on formal clean seeds.
The complete pending configuration is
`configs/calibration/cifar10_iid_clean_hfedsa_attack_presence_seed31415.yaml`;
only final-round error is eligible for the calibration decision.

An initial 10-round instrumentation pre-run was stopped and excluded after the
CSV writer was found not to export the new gate fields. The scientific settings
were not changed. The restarted run uses the `_v2` output directory and records
the intensity ratio, gate decision, and passthrough count for every round.

The restarted seed-31415 run completed all 250 rounds with final accuracy
`84.37%`, or `15.63%` error. This is `-0.07` percentage points from the Table
II(d) H-FedSA clean target (`15.7 +/- 0.2%`) and satisfies the frozen promotion
rule. The gate triggered in all 250 attack-free rounds; the measured ratio range
was `1.0007` to `1.2389`, with no GMM fallback, non-finite feature, or weight
collapse. The compact measured evidence is published at
`results/published/cifar10_iid_clean_hfedsa_attack_presence_calibration_seed31415.json`.
The frozen five-seed manifest is `configs/paper/cifar10_iid_clean_hfedsa_ddpg.yaml`.

## Completed formal H-FedSA clean result

The frozen candidate was run on all preregistered seeds (`2026` through `2030`)
without per-seed changes. Final errors were `15.02%`, `15.24%`, `14.94%`,
`15.47%`, and `14.80%`, producing `15.094 +/- 0.264%`. The mean is `-0.606`
percentage points below the Table II(d) target. Although this is better clean
accuracy, it is not numerically inside the paper's `15.7 +/- 0.2%` interval;
the measured value is retained without post-hoc degradation. All 1,250 rounds
triggered the registered no-attack path, with a maximum observed ratio of
`1.2587` and no diagnostic alerts. The aggregate, gate audit, and per-seed
resolved configurations are published in the repository.

## Completed strict label-flipping calibration

The strict paper-path candidate used 20% malicious clients, deterministic
`y -> 9 - y` labels, the previously selected DDPG lower bound `0.1`, and no
clean-only attack-presence gate. On independent seed `31415`, it completed all
250 rounds at `84.05%` accuracy / `15.95%` error. The final error is `+0.25`
percentage points from Table II(d)'s `15.7 +/- 0.4%` and is numerically inside
that interval. Across 2,500 selected updates, the malicious TPR was `96.8%`
and the non-malicious FPR was `0.4%`; there were no GMM fallbacks or non-finite
diagnostics.

The candidate was not promoted because its preregistered rule also required no
weight-collapse alert. At round 167, one unseen client received `82.02%` of the
normalized aggregation weight, while seven clients remained effective. This
single event is retained rather than waived after seeing the otherwise passing
final error. Compact results and run evidence are published under
`results/published/cifar10_iid_hfedsa_ddpg_label_flip_strict_calibration_seed31415.json`
and `artifacts/calibration/cifar10_iid_hfedsa_ddpg_label_flip_strict_seed31415/`.

### Preregistered low-risk retention confirmation

The next candidate changes only one existing compatibility switch: clients with
`p_malicious < 0.3` receive the implementation's existing raw-weight floor of
`0.05`. EMA remains disabled, high-malicious-posterior weights are not floored,
and all paper training and attack parameters remain frozen. The rule is
label-free, so a truly malicious client misclassified as low risk can receive
the floor; the confirmation run measures that tradeoff explicitly. This
directly targets the single concentration event without changing the
label-flipping attack or GMM roles. Because the change was chosen after
inspecting seed `31415`, the
confirmation uses new independent calibration seed `27182`; formal seeds
`2026` through `2030` remain untouched. Only the final round is eligible for
promotion, and any GMM fallback, non-finite value, or weight-collapse alert
rejects the candidate.

The seed-27182 confirmation completed all 250 rounds at `84.32%` accuracy /
`15.68%` error, only `-0.02` percentage points from the paper mean. Its
malicious TPR was `97.2%` and non-malicious FPR was `0.8%`. The low-risk floor
was applied 959 times, including six truly malicious clients that the GMM had
assigned low malicious posterior; this observed tradeoff is reported rather
than hidden. There were no GMM fallbacks, non-finite diagnostics, or
weight-collapse alerts, and the largest normalized client contribution was
`58.47%`. The candidate therefore passed every preregistered condition and was
frozen for formal seeds `2026` through `2030`.

## Formal label-flipping progress

The first frozen formal seed, `2026`, completed all 250 rounds with final
accuracy `82.75%` / error `17.25%`. This is `+1.55` percentage points from the
paper mean and outside the reported interval. The run nevertheless had strong
detection (`97.4%` malicious TPR, `0.75%` non-malicious FPR) and no GMM
fallback, non-finite diagnostic, or weight-collapse alert. Its accuracy curve
showed large mid-run oscillations, and its DDPG beta averaged `0.894`, compared
with `0.175` in the passing seed-27182 calibration. This seed remains part of
the formal aggregate; it will not be replaced or rerun for a favorable value.
The campaign is paused after seed `2026` and resumes with `2027`.
