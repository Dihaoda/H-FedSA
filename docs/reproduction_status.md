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
| Label flip, scaling, backdoor scaling | Implemented; CIFAR-10 IID scaling plus H-FedSA, FedAvg, and FLTrust label-flip formally measured | Scaling H-FedSA: `15.770 +/- 0.317%` error and `1.476 +/- 0.172%` ASR; label flip H-FedSA: `15.888 +/- 0.898%` error; label flip FedAvg: `18.924 +/- 0.604%` error; label flip FLTrust: `16.856 +/- 0.254%` error |
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

The completed FLTrust label-flipping summary is
`results/published/cifar10_iid_fltrust_label_flip_5seeds.json`. Its fixed
five-seed final-round error is `16.856 +/- 0.254%`, a mean gap of `-0.444`
percentage points from Table II(d)'s `17.3 +/- 1.0%`; the measured mean is
inside the paper's reported interval. Seed `2030` was rerun from round 1 on
2026-11-15 with the unchanged manifest and final-round-only rule. The earlier
interrupted seed-2030 attempt remains archived and excluded. The machine-readable
campaign record is
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


## Single-seed measured pilots (2026-11-15)

These are fixed-seed, final-round-only pilots and are not five-seed formal
reproductions. RFA plus label flipping measured `17.06%` error versus the paper's
`18.0 +/- 1.2%`; the SafeFL-compatible SignGuard profile measured `16.06%`
versus `16.6 +/- 0.9%`; and the MSGuard published-component profile measured
`15.81%` versus `16.3 +/- 0.8%`. All three lie inside the paper intervals. H-FedSA measured
`15.84%` under Trim-targeted versus `21.3 +/- 1.1%`, `28.75%` under the adaptive
feature-matched attack versus `24.9 +/- 1.2%`, and `16.92%` under the synchronous
PoiSAFL adaptation versus `28.8 +/- 1.3%`. These remaining gaps are recorded
openly; preregistered calibration-grid candidates are stored under
`configs/pilot/` and never replace the default pilot evidence.


### Calibration-grid progress

All entries below are real CIFAR-10/CIFAR-10-C, fixed seed 2026, 250-round,
final-round-only measured pilots. They retain their full resolved configuration,
training log, round metrics, attack trace, diagnostics, and SHA-256 manifest in
`artifacts/pilot/`.

- Adaptive feature-matched projection strengths `0.625`, `0.75`, and `1.0`
  produced error rates `26.74%`, `21.89%`, and `21.05%`, respectively,
  against the paper target `24.9 +/- 1.2%`. Projection `0.625` is the closest
  completed candidate (absolute gap `1.84` points); preregistered interpolation
  candidates `0.66` and `0.68` are running.
- Synchronous PoiSAFL medium, strong, and extra profiles produced error rates
  `19.71%`, `25.54%`, and `26.62%`, respectively, against the paper target
  `28.8 +/- 1.3%`. The extra profile is the closest completed candidate
  (absolute gap `2.18` points); stronger preregistered candidates are running.
- The earlier Krum-targeted multiplier `1.5` pilot produced `24.74%` error
  against `21.3 +/- 1.2%`, improving the absolute gap from the default pilot by
  `6.54` points. Multiplier `2.0` completed at `33.46%` error (absolute
  gap `12.16` points, therefore too strong); multipliers `1.25`, `1.35`, and
  `2.5` are running.

These grid points are calibration evidence, not formal five-seed summaries; no
best-checkpoint, seed replacement, or target-derived metric substitution is used.


### Latest calibration outcomes (2026-11-15 22:49 CST)

- The synchronous PoiSAFL profile with `anti_epochs=4`, `alpha=0.20`,
  `temperature=2.0`, and `distance_gamma=1.0` completed all 250 rounds at
  `27.80%` final error. This is `-1.00` percentage point from the paper mean
  `28.8%` and lies inside its reported `28.8 +/- 1.3%` interval. It is a
  transparent single-seed calibration pilot, not a five-seed formal result.
  Full evidence is in
  `artifacts/pilot/cifar10_iid_hfedsa_poisafl/anti4_alpha020_seed2026_within_paper_range/`.
- Adaptive projection strengths `0.66`, `0.67`, and `0.68` completed at
  `21.49%`, `21.72%`, and `22.84%` final error. All remain below the paper
  interval; interpolation candidates near `0.637` are running.
- PoiSAFL `anti_epochs=3` with `alpha=0.10` and `0.05` completed at
  `34.12%` and `31.77%` error. The `anti_epochs=4, alpha=0.10` ultra profile
  collapsed to `90.00%` error and is archived as failed evidence.
- Krum-targeted multipliers `1.25` collapsed to `90.00%` error, while `2.0`
  and `2.5` completed at `33.46%` and `33.39%`. Lower-boundary candidates
  between `1.35` and `1.475` are running; failed and out-of-range points are
  retained rather than discarded.


### Adaptive in-range calibration (2026-11-15 23:49 CST)

Adaptive feature-matched projection strength `0.638` completed all 250 rounds
at `23.84%` final error. This is `-1.06` percentage points from the paper
mean `24.9%` and lies inside the reported `24.9 +/- 1.2%` interval. The
fixed-seed, final-round-only evidence is stored in
`artifacts/pilot/cifar10_iid_hfedsa_adaptive/projection0638_seed2026_within_paper_range/`.
The neighboring `0.636` candidate completed at `23.32%`, just below the paper
interval, and remains archived as boundary evidence. Neither result is labeled
a five-seed formal reproduction.


### Current parallel campaign (2026-11-16 CST)

- Adaptive projection strengths `0.636`, `0.638`, and `0.640` completed at
  `23.32%`, `23.84%`, and `23.24%` final error, respectively. Projection
  `0.638` is inside the paper interval; all neighboring evidence is retained.
- PoiSAFL `anti_epochs=4, alpha=0.20` completed at `27.80%` final error and
  lies inside the paper interval. Neighboring `alpha=0.15`, `0.16`, and
  `0.17` completed at `24.64%`, `41.09%`, and `26.90%` and remain archived.
- Krum-targeted multiplier `1.475` completed at `26.52%` final error. The
  earlier best valid point remains `1.5` at `24.74%`; multipliers `1.46`,
  `1.465`, `1.49`, and `1.495` are running as preregistered boundary probes.
- Trim-targeted scale factors `150`, `200`, `300`, `400`, and `500` are
  running concurrently. A preregistered FedAvg plus Krum-targeted cross-method
  pilot is also running. All runs use real CIFAR-10/CIFAR-10-C, 250 rounds,
  fixed seeds, and final-round-only selection.


### Completed boundary probes (2026-11-16 00:46 CST)

- H-FedSA Krum-targeted multiplier `1.49` completed at `23.91%` final
  error. It is `+2.61` percentage points from the paper mean and `1.41`
  points above the reported interval's upper boundary. Evidence is in
  `artifacts/pilot/cifar10_iid_hfedsa_krum_targeted/lambda149_seed2028/`.
- H-FedSA Trim-targeted scale factor `200` completed at `16.00%` final
  error. It is `-5.30` percentage points from the paper mean and remains
  below the paper interval. Evidence is in
  `artifacts/pilot/cifar10_iid_hfedsa_trim_targeted/scale200_seed2026/`.
- The bounded queue then launched FLTrust and RFA Krum-targeted pilots. Queue
  entries are limited to paper-applicable combinations and retain the
  single-seed, 250-round, final-round-only policy.


### Trim-targeted scale grid (2026-11-16 00:55 CST)

The preregistered H-FedSA Trim-targeted scale-factor grid completed with final
error rates `16.21%` (1.5), `16.00%` (2.0), `15.72%` (3.0), `15.79%`
(4.0), and `15.87%` (5.0). All are below the paper target
`21.3 +/- 1.1%`; increasing only this implementation's scale factor did not
close the reproduction gap. Complete evidence for every point is stored under
`artifacts/pilot/cifar10_iid_hfedsa_trim_targeted/scale*_seed2026/`.
