# Reproduction status

This document separates implemented software paths from completed measured
experiments. A checked implementation item does not imply that a paper table
has been reproduced.

| Area | Status | Notes |
| --- | --- | --- |
| Core federated trainer | Implemented and smoke-tested | Real CIFAR-10 run verified on an NVIDIA A100 |
| Paper H-FedSA features and weight formula | Implemented, unit-tested, and clean-formally measured | Direction, intensity, normalized sparsity, probabilistic weight, and opt-in no-attack presence gate |
| Three-component GMM | Implemented and unit-tested | Full covariance is the paper-manifest default |
| DDPG exploration control | Implemented and smoke-tested | 39-dimensional state; reward uses trusted-root validation and aggregation-internal security signals, never test accuracy or ASR |
| Client-role sampling | Implemented and unit-tested | Preserves malicious/unseen ratios in small rounds |
| Paired local randomness | Implemented and unit-tested | Seeded by experiment, round, and client across defense comparisons |
| Detection metrics | Implemented and unit-tested | TPR on malicious clients; paper FPR on unseen clients; overall benign FPR also recorded |
| CIFAR-10-C unseen data | Implemented and real-data smoke-tested | Gaussian noise and shot noise; exact 40% replacement |
| FEMNIST + Chars74K | Implemented and unit-tested | Sample001--Sample062 label mapping; real-data smoke pending |
| GTSRB + CTSDB/GTSDB | Implemented and unit-tested | Requires an explicit semantic label map; real-data smoke pending |
| Stanford Cars + CompCars | Implemented and unit-tested | Requires a curated make/model label map; real-data smoke pending |
| FedAvg, FLTrust, RFA | Implemented and formally measured | Clean CIFAR-10 IID five-seed results completed for all three methods |
| SafeFL-compatible SignGuard, MSGuard | Implemented and formally measured | Clean CIFAR-10 IID five-seed results completed; SafeFL rule ambiguity and MSGuard artifact limitations remain documented |
| Label flip, scaling, backdoor scaling | Implemented; CIFAR-10 IID scaling, H-FedSA label flip, and FedAvg label-flip formally measured; FLTrust label flip paused after 4/5 seeds | Scaling H-FedSA: `15.770 +/- 0.317%` error and `1.476 +/- 0.172%` ASR; label flip H-FedSA: `15.888 +/- 0.898%` error; label flip FedAvg: `18.924 +/- 0.604%` error; non-final FLTrust checkpoint: `16.850 +/- 0.293%` error |
| Krum-targeted, Trim-targeted, PoiSAFL | Implemented and smoke-tested | PoiSAFL is an explicitly documented synchronous adaptation |
| Full paper tables | Pending | No smoke or synthetic output is accepted as a measured paper result |

The runtime enforces the main prerequisites before training: root-dependent
defenses require a non-empty trusted root set, the paper-aligned DDPG state is
fixed at 39 values, and an H-FedSA round with fewer than three clients emits a
warning and uses a recorded uniform fallback instead of pretending a
three-component GMM was fitted.

The CIFAR-10 Table II(d) values and five fixed reporting seeds are recorded in
`configs/paper/targets/table_ii_cifar10_iid.yaml`. This target manifest is used
to calculate measured gaps; it is never copied into run-generated metrics.

Curated measured summaries may be added under `results/published/` only with
the resolved configuration, seed list, raw run locations, and aggregation
method. Generated run directories remain ignored by Git.

The completed H-FedSA-DDPG scaling summary is
`results/published/cifar10_iid_hfedsa_ddpg_scaling_5seeds.json`. Its ASR mean
differs from Table II(d) by `+0.276` percentage points, inside the paper's
reported ASR standard deviation; its error mean differs by `+0.570` points and
is therefore recorded as a remaining reproduction gap.

The completed H-FedSA-DDPG label-flipping summary is
`results/published/cifar10_iid_hfedsa_ddpg_label_flip_5seeds.json`. Its fixed
five-seed final-round error is `15.888 +/- 0.898%`, a mean gap of `+0.188`
percentage points from Table II(d)'s `15.7 +/- 0.4%`. The measured mean is
inside the paper's reported interval, while the measured sample standard
deviation is larger. All 1,250 rounds used real CIFAR-10/CIFAR-10-C, and no run
had a GMM fallback, non-finite diagnostic, or weight-collapse alert. The
low-risk raw-weight floor remains explicitly labeled as a compatibility
extension because it is not specified by Algorithm 1.

The completed FedAvg label-flipping baseline is
`results/published/cifar10_iid_fedavg_label_flip_5seeds.json`. Its fixed
five-seed final-round error is `18.924 +/- 0.604%`, a mean gap of
`-53.076` percentage points from Table II(d)'s `72.0 +/- 4.5%`. All five
runs used the same deterministic `y -> 9 - y` attack, 20% malicious-client
ratio, real CIFAR-10/CIFAR-10-C data, and optimization budget as the H-FedSA
label-flipping campaign. The large gap indicates that the paper's FedAvg
label-flipping result depends on attack details not reproduced by the current
deterministic protocol; it is recorded openly rather than changed post hoc.

The FLTrust label-flipping campaign is paused after fixed seeds `2026`,
`2027`, `2028`, and `2029`, whose final-round errors are `17.09%`, `16.51%`,
`17.10%`, and `16.70%`. The non-final four-seed checkpoint is
`16.850 +/- 0.293%` error, inside Table II(d)'s `17.3 +/- 1.0%` interval.
A seed `2030` attempt stopped after round 73/250 at the user's request is
explicitly excluded. Seed `2030` remains preregistered and must be rerun from
round 1 before creating a published five-seed summary. The machine-readable
resume state is
`results/published/cifar10_iid_fltrust_label_flip_formal_progress.json`.

The completed clean H-FedSA-DDPG summary is
`results/published/cifar10_iid_clean_hfedsa_ddpg_5seeds.json`. Its five-seed
error is `15.094 +/- 0.264%`, a mean gap of `-0.606` percentage points from
Table II(d)'s `15.7 +/- 0.2%`. The independently calibrated no-attack gate used
the frozen intensity-ratio threshold `3.0`; it triggered in all 1,250 formal
rounds, whose largest observed ratio was `1.2587`. The result is better than the
paper mean but outside its one-standard-deviation interval, so the numerical gap
is reported rather than hidden by post-hoc degradation.

The completed clean FLTrust summary is
`results/published/cifar10_iid_clean_fltrust_5seeds.json`. Its five-seed error
is `15.614 +/- 0.595%`, a mean gap of `+0.214` percentage points from Table
II(d)'s `15.4 +/- 0.4%`; the measured mean is inside the paper's reported
range. The dedicated preregistered manifest is
`configs/paper/cifar10_iid_clean_fltrust.yaml`.

The completed clean RFA summary is
`results/published/cifar10_iid_clean_rfa_5seeds.json`. Its five-seed error is
`15.144 +/- 0.209%`, a mean gap of `-0.056` percentage points from Table
II(d)'s `15.2 +/- 0.3%`. All five runs used the same preregistered RFA settings
(`max_iter=20`, `tol=1e-5`, `eps=1e-8`) in
`configs/paper/cifar10_iid_clean_rfa.yaml`; no best-checkpoint or per-seed
selection was used.

The completed clean SafeFL-compatible SignGuard summary is
`results/published/cifar10_iid_clean_safefl_signguard_5seeds.json`. Its
five-seed error is `15.430 +/- 0.202%`, a mean gap of `+0.130` percentage
points from the H-FedSA paper's SafeFL column (`15.3 +/- 0.3%`). The manifest
fixes the public SignGuard profile at a 10% sign-coordinate sample and norm
bounds `[0.1, 3.0]`. Because the H-FedSA paper does not identify which SafeFL
rule produced its column, this result is explicitly reported as compatible,
not as bit-for-bit reproduction of an unspecified rule.

The completed clean MSGuard summary is
`results/published/cifar10_iid_clean_msguard_5seeds.json`. Its five-seed error
is `15.504 +/- 0.227%`, a mean gap of `+0.304` percentage points from Table
II(d)'s `15.2 +/- 0.3%`. The unrounded mean is `0.004` points above the
paper's one-standard-deviation upper bound. The manifest fixes Mean Shift to
automatic bandwidth estimation with `quantile=0.3` and a 50% minimum-retention
floor. Because no public author artifact is available, this remains labeled a
published-component implementation rather than source-identical reproduction.
