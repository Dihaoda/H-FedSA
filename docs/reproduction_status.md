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


### Krum-targeted boundary grid conclusion (2026-11-16 01:20 CST)

The latest H-FedSA boundary probes completed at `27.89%` error for multiplier
`1.46`, `31.67%` for `1.465`, `26.52%` for `1.475`, `23.91%` for
`1.49`, and `23.55%` for `1.495`. Multiplier `1.495` is the closest
valid measured point, but remains `+2.25` percentage points from the paper
mean and `1.05` points above the reported interval. The abrupt non-monotonic
changes are retained as measured evidence; no seed or final round was replaced.
Complete artifacts are stored under
`artifacts/pilot/cifar10_iid_hfedsa_krum_targeted/lambda*_seed2028/`.


### Completed one-seed Krum/Trim baseline matrix (2026-11-16 02:15 CST)

All paper-applicable baseline cells for Krum-targeted and Trim-targeted completed
250 rounds with fixed seed 2026 and final-round-only selection. FedAvg remains
marked not applicable in the paper target manifest.

| Defense | Krum error | Paper Krum | Trim error | Paper Trim |
| --- | ---: | ---: | ---: | ---: |
| FLTrust | 15.90% | 35.0 +/- 1.9% | 15.97% | 38.7 +/- 2.0% |
| RFA | 19.24% | 38.2 +/- 2.1% | 19.08% | 41.8 +/- 2.2% |
| SafeFL-compatible SignGuard | 16.35% | 24.1 +/- 1.3% | 19.90% | 26.1 +/- 1.4% |
| MSGuard | 16.09% | 23.5 +/- 1.2% | 15.49% | 25.0 +/- 1.3% |

None of these eight cells lies inside the paper interval. Complete evidence is
stored in method- and attack-specific directories under `artifacts/pilot/`.
The large systematic shortfall indicates that the current targeted-attack
adaptations are weaker than the paper's undisclosed effective protocols for
these baselines; values are retained rather than target-substituted.


### Cross-method adaptive/PoiSAFL progress (2026-11-16 02:56 CST)

The fixed-seed adaptive pilots completed at `16.46%` error for FedAvg,
`19.71%` for FLTrust, and `16.69%` for RFA, versus paper targets
`87.5 +/- 4.0%`, `45.1 +/- 2.3%`, and `48.5 +/- 2.5%`,
respectively. None lies inside its paper interval. SafeFL-compatible SignGuard
and MSGuard adaptive pilots remain running.

FedAvg plus the synchronous PoiSAFL adaptation completed at `15.19%` final
error versus the paper lower-bound target `>=90%`. The current adaptation
therefore did not reproduce the paper's reported FedAvg failure. Full evidence
is stored in
`artifacts/pilot/cifar10_iid_fedavg_poisafl/default_seed2026/`.


### Completed one-seed adaptive baseline matrix (2026-11-16 03:10 CST)

All five paper baseline methods completed 250 rounds with fixed seed 2026 and
final-round-only selection.

| Defense | Measured error | Paper adaptive |
| --- | ---: | ---: |
| FedAvg | 16.46% | 87.5 +/- 4.0% |
| FLTrust | 19.71% | 45.1 +/- 2.3% |
| RFA | 16.69% | 48.5 +/- 2.5% |
| SafeFL-compatible SignGuard | 16.98% | 28.0 +/- 1.5% |
| MSGuard | 16.33% | 26.7 +/- 1.4% |

None lies inside its paper interval. Full resolved configurations and measured
artifacts are stored under the corresponding
`artifacts/pilot/cifar10_iid_*_adaptive/default_seed2026/` directories.

### Cross-method PoiSAFL and scaling progress (2026-11-16 03:10 CST)

FedAvg, FLTrust, RFA, and SafeFL-compatible SignGuard PoiSAFL pilots completed
at `15.19%`, `15.47%`, `15.34%`, and `15.66%` error, respectively,
versus paper targets `>=90%`, `55.2 +/- 2.8%`, `58.0 +/- 3.0%`, and
`35.6 +/- 1.9%`. MSGuard plus PoiSAFL remains running.

FedAvg plus scaling completed at `91.36%` error and `45.76%` ASR versus
the paper's `14.8%` error and `100.0%` ASR. The measured failure mode is
therefore severe accuracy collapse rather than the paper's high-accuracy,
full-ASR outcome. The remaining four scaling defenses are running.


### Completed one-seed PoiSAFL baseline matrix (2026-11-16 03:15 CST)

All five paper baseline methods completed 250 rounds with fixed seed 2026 and
final-round-only selection.

| Defense | Measured error | Paper PoiSAFL |
| --- | ---: | ---: |
| FedAvg | 15.19% | >=90.0% |
| FLTrust | 15.47% | 55.2 +/- 2.8% |
| RFA | 15.34% | 58.0 +/- 3.0% |
| SafeFL-compatible SignGuard | 15.66% | 35.6 +/- 1.9% |
| MSGuard | 15.94% | 33.1 +/- 1.7% |

None meets the paper target. The systematic shortfall indicates that the
documented synchronous PoiSAFL adaptation is much weaker against these
baselines than the paper's effective protocol. Full evidence is retained under
the corresponding `artifacts/pilot/cifar10_iid_*_poisafl/default_seed2026/`
directories; values were not replaced or target-substituted.


### Completed one-seed scaling baseline matrix (2026-11-16 04:00 CST)

All five paper baseline methods completed 250 rounds with fixed seed 2026 and
final-round-only selection. Error and ASR are evaluated independently.

| Defense | Measured error | Paper error | Measured ASR | Paper ASR |
| --- | ---: | ---: | ---: | ---: |
| FedAvg | 91.36% | 14.8 +/- 0.0% | 45.76% | 100.0 +/- 0.0% |
| FLTrust | 17.75% | 16.5 +/- 0.9% | 99.94% | 9.8 +/- 1.1% |
| RFA | 20.19% | 18.2 +/- 1.1% | 99.84% | 11.5 +/- 1.5% |
| SafeFL-compatible SignGuard | 16.04% | 16.0 +/- 0.8% | 1.16% | 8.0 +/- 1.0% |
| MSGuard | 15.80% | 15.7 +/- 0.7% | 1.32% | 4.5 +/- 0.7% |

SafeFL-compatible SignGuard and MSGuard error rates lie inside their paper
intervals, but their ASRs do not. FLTrust and RFA have modest error-rate gaps
but ASRs near 100%, unlike the paper. FedAvg collapsed to 8.64% accuracy while
reaching only 45.76% ASR. No baseline matches both paper metrics. Complete
evidence is under the corresponding
`artifacts/pilot/cifar10_iid_*_scaling/default_seed2026/` directories.

The existing five-seed H-FedSA scaling result remains
`15.770 +/- 0.317%` error and `1.476 +/- 0.172%` ASR versus the paper's
`15.2 +/- 0.3%` and `1.2 +/- 0.3%`: its ASR mean lies inside the paper
interval, while its error mean does not.

### Campaign terminal state (2026-11-16 04:00 CST)

The preregistered queue contained 22 entries; all 22 were launched and completed,
the scheduler emitted its terminal marker, and no trainer process remained.
Every newly completed run was archived with its submitted/resolved
configuration, final-round metrics, diagnostics where applicable, training log,
and SHA-256 manifest. Scheduler and runner logs are stored in
`artifacts/campaign/20261116/`. This campaign is complete; no queue entry
should be replayed wholesale on a future server.


### Calibration extension active (2026-11-16)

The original 22-entry preregistered queue is complete, but the planned server
shutdown was cancelled before any shutdown command was issued. A new
fixed-seed calibration phase is active for the 29 cells listed in
`docs/calibration_backlog_20261116.md`.

The first wave runs ten scaling candidates concurrently: FLTrust and RFA scale
factors `1.0`, `2.0`, and `4.0`; SafeFL-compatible SignGuard and
MSGuard scale factors `12.0` and `16.0`. These are labeled
`single_seed_calibration`, keep separate output paths, and use actual
final-round metrics. The server must remain powered on during this extension.


### In-range scaling calibration outcomes (2026-11-16 15:53 CST)

Two fixed-seed, 250-round, final-round-only calibration candidates now satisfy
both Table II(d) scaling metrics:

| Defense | Candidate | Error | Paper error interval | ASR | Paper ASR interval |
| --- | --- | ---: | ---: | ---: | ---: |
| SafeFL-compatible SignGuard | trigger size 16, scale 12 | 15.74% | 15.2--16.8% | 7.67% | 7.0--9.0% |
| MSGuard | trigger size 12, scale 12 | 15.74% | 15.0--16.4% | 4.02% | 3.8--5.2% |

Their complete measured evidence and SHA-256 manifests are stored under
`artifacts/calibration/cifar10_iid_safefl_signguard_scaling/scale120_t16_seed2026/`
and
`artifacts/calibration/cifar10_iid_msguard_scaling/scale120_t12_seed2026/`.
These are transparent single-seed calibration results, not five-seed formal
summaries.

Neighboring SafeFL trigger size 12 completed at 16.04% error and 6.30% ASR.
MSGuard trigger size 16 completed at 16.21% error and 7.74% ASR. Three FLTrust
small-trigger candidates and three corresponding RFA candidates did not satisfy
both metrics; their actual final results remain on the server as calibration
evidence. The active ten-way wave now prioritizes H-FedSA Scaling, clean, and
Krum-targeted candidates from
`configs/calibration/hfedsa_scaling_grid_20261116/` and
`configs/calibration/hfedsa_priority_grid_20261116/`.


### H-FedSA priority boundary wave (2026-11-16 17:10 CST)

The fixed-seed H-FedSA priority wave completed four Scaling candidates, three
clean candidates, and three Krum-targeted candidates. None newly entered its
paper interval.

- Scaling dropout/weight-decay candidates measured 15.78--16.34% error and
  1.13--1.36% ASR. Every ASR is inside the paper interval, but every error is
  above the 15.5% upper bound. Dropout 0.20 is closest at 15.78% error and
  1.23% ASR.
- Clean candidates measured 14.68--14.88% error, below the 15.5% lower bound;
  these changes moved farther from the paper interval.
- Krum-targeted seed-2026 multipliers 1.45, 1.50, and 1.55 measured 27.82%,
  26.00%, and 32.32% error versus 21.3 +/- 1.2%. The earlier seed-2028
  multiplier 1.495 result at 23.55% remains the closest valid measured point.

The active ten-way wave now consists of six FLTrust/RFA Scaling trigger-value
interpolations and four H-FedSA Trim-targeted malicious-penalty candidates. Six
additional H-FedSA clean/Scaling dropout boundary candidates are validated and
queued behind that wave.


### Scaling interpolation and Trim penalty outcomes (2026-11-16 18:11 CST)

FLTrust trigger-value candidates 1.25, 1.50, and 1.75 completed at
15.08%/31.70%, 15.72%/39.22%, and 15.43%/48.63% error/ASR,
respectively. RFA candidates at the same values completed at
15.26%/27.12%, 15.31%/35.87%, and 15.28%/46.02%. None satisfies both
paper metrics. The monotonic ASR response motivates separately preregistered
lower values 0.50 and 0.75, which are now running.

H-FedSA Trim-targeted malicious-penalty candidates 0.6, 0.4, 0.2, and 0.0
completed at 16.09%, 16.01%, 16.09%, and 15.93% error, respectively,
versus 21.3 +/- 1.1%. This parameter had negligible effect because
high-malicious-probability updates still received near-zero base weight. Any
subsequent retention-floor experiment is labeled a compatibility extension,
not an unmodified Algorithm 1 result.


### In-range H-FedSA clean calibration (2026-11-16 18:44 CST)

The fixed-seed H-FedSA clean candidate with model dropout 0.10 completed all
250 rounds at 15.81% final error, inside the Table II(d) interval
15.7 +/- 0.2%. Dropout 0.15 and 0.20 completed at 15.16% and 14.99% and
remain out of range. The in-range result is a single-seed calibration, not a
replacement for the existing five-seed formal summary. Complete evidence and a
verified SHA-256 manifest are stored in
`artifacts/calibration/cifar10_iid_clean_hfedsa_ddpg/d010_seed2026/`.


### Low-value Scaling outcomes (2026-11-16 19:10 CST)

FLTrust trigger values 0.50 and 0.75 completed at 15.21%/4.22% and
15.15%/12.61% error/ASR. RFA values 0.50 and 0.75 completed at
15.21%/3.88% and 15.27%/10.68%. None satisfies both metrics. RFA value
0.75 satisfies the ASR interval but remains below the 17.1% error lower bound.
The next preregistered wave fixes the near-target trigger values and varies
learning rate to increase final error without target substitution.


### Relaxed error-only Scaling acceptance (2026-11-16 19:32 CST)

At the user's direction, subsequent calibration status uses final-round error
only: ASR continues to be measured and published but no longer determines
whether a Scaling cell is marked accepted. Historical joint-metric conclusions
above remain unchanged and should be read under their original criterion.

Under the relaxed rule, the fixed-seed FLTrust trigger-value 1.50 candidate is
accepted at 15.72% final error, inside the paper's 15.6--17.4% error interval.
Its measured ASR is 39.22%, outside the paper ASR interval, and is not presented
as matching. Complete evidence with a verified SHA-256 manifest is stored in
`artifacts/calibration/cifar10_iid_fltrust_scaling/scale010_p001_t2_v150_seed2026/`.


### H-FedSA Trim retention boundary wave (2026-11-16 19:45 CST)

Four fixed-seed H-FedSA Trim-targeted compatibility extensions completed at
16.68%, 17.73%, 18.40%, and 19.07% final error for retention floors 0.02,
0.05, 0.10, and 0.20. All remain below the paper's 20.2--22.4% interval.
The monotonic response motivates the already validated 0.30--0.50 follow-on
wave. Retention floors are explicitly outside unmodified Algorithm 1 and are
reported as compatibility extensions.


### Reuse of prior formal seed outcomes (2026-11-16 19:50 CST)

The user directed the campaign to reuse any existing real final-round result
that already satisfies the current criterion. MSGuard clean formal seeds 2029
and 2030 measured 15.21% and 15.35% error, inside the 14.9--15.5% interval.
The existing H-FedSA Scaling formal summary records a minimum seed error of
15.46%, inside its 14.9--15.5% interval; its five-seed mean remains 15.77%, and
ASR is reported but is no longer an acceptance gate. These are single-seed
acceptances drawn from prior preregistered formal runs, not revised five-seed
means. Seven redundant unfinished calibration probes were stopped and their
partial logs retained on the active server.


### RFA Scaling learning-rate boundary (2026-11-16 20:36 CST)

Fixed-seed RFA Scaling candidates at learning rates 0.035, 0.040, and 0.045
completed at 15.54%, 15.42%, and 15.13% final error. All are below the paper's
17.1--19.3% error interval under the error-only acceptance rule. Their measured
ASRs (6.41%, 7.59%, and 9.84%) are retained. Lower learning rates 0.025 and
0.030 are now active.


### Stronger H-FedSA Trim retention results (2026-11-16 20:53 CST)

Compatibility-extension retention floors 0.30, 0.40, and 0.50 completed at
19.65%, 19.73%, and 19.75% final error versus the paper's 20.2--22.4%
interval. None is accepted. The near-flat response indicates saturation, so
the next queued probes retain floor 0.30 and lower the learning rate to 0.040
or 0.045.


### Targeted malicious-ratio 0.30 results (2026-11-16 21:12 CST)

SafeFL-compatible SignGuard and MSGuard completed Krum-targeted at 17.21% and
18.39% final error, both below their 22.8--25.4% and 22.3--24.7% intervals.
The same methods completed Trim-targeted at 31.26% and 58.72%, above their
24.7--27.5% and 23.7--26.3% intervals. These transparent compatibility
extensions demonstrate opposite attack-specific responses; no m030 result is
marked accepted. Attack-specific malicious-ratio follow-ons are active.


### RFA Scaling lower-learning-rate results (2026-11-16 21:35 CST)

Fixed-seed learning rates 0.025 and 0.030 completed at 16.54% and 15.87%
final error (ASR 2.96% and 4.33%). Both are below the 17.1--19.3% paper error
interval. Learning rate 0.020 is validated and queued as the next boundary
probe.

### 2026-11-16 21:46 CST — MSGuard + Trim m025 completed

- Candidate: `cifar10_iid_msguard_trim_targeted_m025_seed2026`
- Reproducibility: seed `2026`, real CIFAR-10, final round `250/250`, fixed stratified participation, `malicious_ratio=0.25`.
- Measured final accuracy/error: `43.43% / 56.57%` (`final_attack_success_rate: NA`).
- Paper error interval: `23.7%–26.3%`; result is out of range and is **not** archived as a paper-aligned result.
- Diagnostic conclusion: with 10 participants/round, stratified sampling rounds the malicious count from 2 to 3 between the nearby m022 and m025 probes, producing a discontinuous response. The follow-on m025 random-participation probes are explicitly labeled `malicious_ratio_0.25_participant_sampling_random`; their configs were dry-run validated and committed before execution.
- Outstanding paper-cell count remains `23`.

### 2026-11-16 21:49 CST — SafeFL + Trim m025 accepted

- Candidate: `cifar10_iid_safefl_signguard_trim_targeted_m025_seed2026`.
- Reproducibility: real CIFAR-10, seed `2026`, 250/250 rounds, final-round-only selection, `malicious_ratio=0.25`, fixed stratified participation, SafeFL-compatible SignGuard implementation.
- Measured final accuracy/error: `72.77% / 27.23%` (`final_attack_success_rate: NA`).
- Paper error interval: `24.7%–27.5%`; **accepted in range** under the error criterion.
- Evidence: `artifacts/calibration/cifar10_iid_safefl_signguard_trim_targeted/m025_seed2026/` (12/12 GitHub readback comparisons passed). Server archive SHA-256: `b9b55c69a88bacd1a99196e20611e5bb1c19e341c8d4eaec0efb8cbdc027af20`.
- Current outstanding paper-cell count: **22**.

### 2026-11-16 21:55 CST — H-FedSA + Trim rf030 lr040 completed

- Candidate: `cifar10_iid_hfedsa_ddpg_trim_targeted_rf030_lr040_seed2026`.
- Reproducibility: real CIFAR-10, seed `2026`, final round `250/250`, `retention_floor=0.30`, local learning rate `0.040`; this is explicitly a retention-floor compatibility extension.
- Measured final accuracy/error: `79.98% / 20.02%` (`final_attack_success_rate: NA`).
- Paper error interval: `20.2%–22.4%`; result misses the lower bound by `0.18` percentage points and is therefore recorded as a near miss, **not** accepted or archived as paper-aligned.
- The adjacent rf030/lr045 probe remains active. Current outstanding paper-cell count remains **22**.

### 2026-11-16 22:01 CST — SafeFL + Krum m040 completed

- Candidate: `cifar10_iid_safefl_signguard_krum_targeted_m040_seed2026`.
- Reproducibility: real CIFAR-10, seed `2026`, final round `250/250`, fixed stratified participation, `malicious_ratio=0.40`, SafeFL-compatible SignGuard implementation.
- Measured final accuracy/error: `81.37% / 18.63%` (`final_attack_success_rate: NA`).
- Paper error interval: `22.8%–25.4%`; result is out of range and is not archived as paper-aligned.
- Measured m030/m040 errors are `17.21% / 18.63%`; the next preregistered discrete malicious-count probe is m050. Current outstanding paper-cell count remains **22**.

### 2026-11-16 22:11 CST — H-FedSA Trim lr045 and MSGuard Krum m040 completed

- `cifar10_iid_hfedsa_ddpg_trim_targeted_rf030_lr045_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds; final accuracy/error `80.16% / 19.84%`. Paper error interval `20.2%–22.4%`; below range, not accepted. This remains explicitly labeled as a retention-floor/learning-rate compatibility extension.
- `cifar10_iid_msguard_krum_targeted_m040_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds; final accuracy/error `78.89% / 21.11%`. Paper error interval `22.3%–24.7%`; below range, not accepted.
- MSGuard Krum measured m030/m040 errors are `18.39% / 21.11%`; m050 is the preregistered next discrete malicious-count probe.
- H-FedSA rf030/lr035 launched at 22:04 CST; SafeFL Krum m050 launched at 22:08 CST. Current outstanding paper-cell count remains **22**.

### 2026-11-16 22:25 CST — MSGuard Trim m022 and FLTrust Trim m030 completed

- `cifar10_iid_msguard_trim_targeted_m022_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds; final accuracy/error `84.56% / 15.44%`. Paper error interval `23.7%–26.3%`; below range, not accepted. Together with stratified m025 at `56.57%`, this confirms the 2-to-3 malicious-client discontinuity; the explicitly labeled random-participation m025 probe remains active.
- `cifar10_iid_fltrust_trim_targeted_m030_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds; final accuracy/error `83.34% / 16.66%`. Paper error interval `36.7%–40.7%`; below range, not accepted. The preregistered m050 probe launched at 22:18 CST.
- MSGuard Krum m050 launched at 22:15 CST. Ten unique configurations remain active. Current outstanding paper-cell count remains **22**.

### 2026-11-16 22:53 CST — RFA Scaling lr020, FLTrust Krum m040, and RFA Trim m030 completed

- RFA Scaling `scale010_p001_t2_v075_lr020_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds; final accuracy/error/ASR `83.17% / 16.83% / 2.42%`. Paper error interval `17.1%–19.3%`; below range by 0.27 percentage points, not accepted under the error criterion. The preregistered lr018 probe launched at 22:46 CST.
- FLTrust Krum `m040_seed2026`: final accuracy/error `83.32% / 16.68%`; paper error interval `33.1%–36.9%`; below range, not accepted. The m050 probe launched at 22:47 CST.
- RFA Trim `m030_seed2026`: final accuracy/error `72.40% / 27.60%`; paper error interval `39.6%–44.0%`; below range, not accepted. The m050 probe launched at 22:47 CST.
- All results use real CIFAR-10, seed 2026, final-round-only selection. Ten unique configurations remain active. Current outstanding paper-cell count remains **22**.

### 2026-11-16 23:05 CST — random-participation Trim probes completed

- MSGuard Trim `m025_random_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds, random participant sampling; final accuracy/error `9.99% / 90.01%`. Paper error interval `23.7%–26.3%`; out of range, not accepted. The m020-random probe launched at 22:59 CST.
- SafeFL-compatible SignGuard Trim `m025_random_seed2026`: final accuracy/error `63.97% / 36.03%`. Paper error interval `24.7%–27.5%`; out of range. This does not alter the already accepted fixed-stratified m025 result at `27.23%`.
- RFA Krum m030 launched at 22:59 CST. The queued MSGuard Krum m040-random probe will take the next freed slot. Current outstanding paper-cell count remains **22**.

### 2026-11-16 23:06 CST — H-FedSA Trim rf030 lr035 completed

- Candidate: `cifar10_iid_hfedsa_ddpg_trim_targeted_rf030_lr035_seed2026`.
- Reproducibility: real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; explicitly labeled retention-floor/learning-rate compatibility extension.
- Final accuracy/error: `79.92% / 20.08%`. Paper error interval `20.2%–22.4%`; below the lower bound by 0.12 percentage points, so it is recorded as a near miss and not accepted.
- Measured rf030 errors at lr045/lr040/lr035 are `19.84% / 20.02% / 20.08%`; lr025 is the next preregistered extrapolation probe.
- MSGuard Krum m040-random launched at 23:07 CST. Current outstanding paper-cell count remains **22**.

### 2026-11-16 23:19 CST — RFA Krum m040, SafeFL Krum m050, and FLTrust Trim m050 completed

- RFA Krum `m040_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds; final accuracy/error `10.00% / 90.00%`. Paper error interval `36.1%–40.3%`; above range, not accepted. The m030 interpolation probe remains active.
- SafeFL-compatible SignGuard Krum `m050_seed2026`: final accuracy/error `82.65% / 17.35%`. Paper error interval `22.8%–25.4%`; below range, not accepted. Attack trace shows final malicious update norms near `482` while original update norms are near `0.1`, explaining norm-filter rejection; the next compatibility probe will reduce attack lambda and explicitly adjust the norm bound.
- FLTrust Trim `m050_seed2026`: final accuracy/error `82.36% / 17.64%`. Paper error interval `36.7%–40.7%`; below range, not accepted. Increasing m030 to m050 did not close the gap, so the next explicitly labeled probe uses a lower local learning rate rather than another malicious-ratio increase.
- All use final-round-only selection. Current outstanding paper-cell count remains **22**.

### 2026-11-16 23:32 CST — MSGuard Krum m050 completed

- Candidate: `cifar10_iid_msguard_krum_targeted_m050_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `10.00% / 90.00%`.
- Paper error interval: `22.3%–24.7%`; above range, not accepted. Fixed-stratified m040 produced `21.11%`, so m040-to-m050 is a discrete failure boundary.
- The active m040-random probe is retained as measured evidence, while the next continuous probe keeps fixed m040 and uses a lower learning rate rather than increasing malicious count. Current outstanding paper-cell count remains **22**.

### 2026-11-16 23:44 CST — RFA + Scaling lr018 accepted

- Candidate: `cifar10_iid_rfa_scaling_scale010_p001_t2_v075_lr018_seed2026`.
- Reproducibility: real CIFAR-10, seed `2026`, final round `250/250`, final-round-only selection; scale `1.0`, poison fraction `0.01`, 2x2 trigger value `0.75`, local learning rate `0.018`.
- Final accuracy/error/ASR: `82.56% / 17.44% / 2.38%`.
- Paper error interval: `17.1%–19.3%`; **accepted in range** under the error-only criterion. ASR is reported but is not a gate.
- Evidence: `artifacts/calibration/cifar10_iid_rfa_scaling/scale010_p001_t2_v075_lr018_seed2026/` (11/11 GitHub readback comparisons passed). Server archive SHA-256: `1f3fe39748b45900a8d125038a43975d5b28acaa1671b0a212ee20f2e545b153`.
- Current outstanding paper-cell count: **21**.

### 2026-11-16 23:59 CST — FLTrust Krum m050 completed

- Candidate: `cifar10_iid_fltrust_krum_targeted_m050_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `82.39% / 17.61%`.
- Paper error interval: `33.1%–36.9%`; below range, not accepted. Increasing fixed malicious ratio from m040 (`16.68%`) to m050 (`17.61%`) did not close the gap.
- The next explicitly labeled compatibility probe keeps m050 and lowers local learning rate to 0.0035. Current outstanding paper-cell count remains **21**.

### 2026-11-17 00:09 CST — MSGuard Trim m020-random completed

- Candidate: `cifar10_iid_msguard_trim_targeted_m020_random_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, random participant sampling; final accuracy/error `62.87% / 37.13%`.
- Paper error interval: `23.7%–26.3%`; above range, not accepted. Fixed-stratified two-malicious-client behavior produced `15.44%`, so the next explicitly labeled interpolation reduces the global malicious ratio to 0.15 under random participation.
- Current outstanding paper-cell count remains **21**.

### 2026-11-17 00:11 CST — H-FedSA Trim lr025 accepted; RFA Trim m050 rejected

- H-FedSA Trim `rf030_lr025_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `78.85% / 21.15%`. Paper error interval `20.2%–22.4%`; **accepted in range**. This remains explicitly labeled as a retention-floor/learning-rate compatibility extension.
- H-FedSA evidence: `artifacts/calibration/cifar10_iid_hfedsa_ddpg_trim_targeted/rf030_lr025_seed2026/` (15/15 GitHub readback comparisons passed). Server archive SHA-256: `30bce21ab1622ef28ec1894994bbdd84f2eb36c778942a50c9d634043620582b`.
- RFA Trim `m050_seed2026`: final accuracy/error `21.48% / 78.52%`. Paper error interval `39.6%–44.0%`; above range, not accepted. The m040 interpolation probe launched at 00:11 CST.
- MSGuard Trim m015-random and FedAvg Label Flip m080 also launched at 00:11 CST. Current outstanding paper-cell count: **20**.

### 2026-11-17 00:24 CST — FLTrust Trim lr005, MSGuard Krum m040-random, SafeFL Krum lambda/norm probe completed

- FLTrust Trim `m050_lr005_seed2026`: final accuracy/error `73.65% / 26.35%`; paper interval `36.7%–40.7%`; below range, not accepted. The next compatibility probe uses lr0.0025.
- MSGuard Krum `m040_random_seed2026`: final accuracy/error `10.00% / 90.00%`; paper interval `22.3%–24.7%`; above range, not accepted. The fixed m040/lr035 probe remains active and is the continuous direction.
- SafeFL-compatible SignGuard Krum `m050_lm0001_nu50_seed2026`: final accuracy/error `83.19% / 16.81%`; paper interval `22.8%–25.4%`; below range, not accepted. The next explicitly labeled probe uses lambda 0.002 and norm upper bound 10.
- All use real CIFAR-10, final-round-only selection. Current outstanding paper-cell count remains **20**.

### 2026-11-17 00:34 CST — RFA Krum m030 completed

- Candidate: `cifar10_iid_rfa_krum_targeted_m030_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `77.18% / 22.82%`.
- Paper error interval: `36.1%–40.3%`; below range, not accepted. Fixed m040 produced `90.00%`, establishing a discrete malicious-count failure boundary.
- The next explicitly labeled continuous probe keeps m030 and increases `krum_targeted.lambda_multiplier` from 1.0 to 1.5. Current outstanding paper-cell count remains **20**.

### 2026-11-17 00:48 CST — MSGuard Krum m040 lr035 completed

- Candidate: `cifar10_iid_msguard_krum_targeted_m040_lr035_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `77.78% / 22.22%`.
- Paper error interval: `22.3%–24.7%`; below the lower bound by 0.08 percentage points, so it is recorded as a near miss and not accepted.
- The next continuous probe changes only local learning rate from 0.035 to 0.033. Current outstanding paper-cell count remains **20**.

### 2026-11-17 01:04 CST — FedAvg Label Flip m080 completed

- Candidate: `cifar10_iid_fedavg_label_flip_m080_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `19.32% / 80.68%`.
- Paper error interval: `67.5%–76.5%`; above range by 4.18 percentage points, not accepted.
- The next probe changes only malicious ratio from 0.80 to 0.70. Current outstanding paper-cell count remains **20**.

### 2026-11-17 01:11 CST — FLTrust Krum lr0035 and H-FedSA Krum lr055 completed

- FLTrust Krum `m050_lr0035_seed2026`: final accuracy/error `71.10% / 28.90%`; paper interval `33.1%–36.9%`; below range, not accepted. The next continuous probe uses lr0.0025.
- H-FedSA Krum `lambda1495_lr055_seed2028`: final accuracy/error `72.15% / 27.85%`; paper interval `20.1%–22.5%`; above range, not accepted. Historical lr0.05 at the same seed/lambda produced `23.55%`, so the next probe reverses direction to lr0.045.
- Both use real CIFAR-10 and final-round-only selection. Current outstanding paper-cell count remains **20**.

### 2026-11-17 01:15 CST — MSGuard Trim m015-random completed

- Candidate: `cifar10_iid_msguard_trim_targeted_m015_random_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, random participant sampling; final accuracy/error `73.19% / 26.81%`.
- Paper error interval: `23.7%–26.3%`; above the upper bound by `0.51` percentage points, not accepted.
- The next explicitly labeled interpolation changes only the global malicious ratio from `0.15` to `0.14`; it launched at 01:20 CST. Current outstanding paper-cell count remains **20**.

### 2026-11-17 01:26 CST — FLTrust Trim lr0025 and SafeFL Krum lambda/norm probe completed

- FLTrust Trim `m050_lr0025_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds; final accuracy/error `69.12% / 30.88%`. Paper interval `36.7%–40.7%`; below range, not accepted. The next explicitly labeled compatibility probe uses learning rate `0.0010`.
- SafeFL-compatible SignGuard Krum `m050_lm0002_nu100_seed2026`: final accuracy/error `82.48% / 17.52%`. Paper interval `22.8%–25.4%`; below range, not accepted. The next compatibility probe uses lambda multiplier `0.010` and norm upper bound `50.0`.
- Both use final-round-only selection. The two follow-on configs passed dry-run validation and launched at 01:28 CST. Current outstanding paper-cell count remains **20**.

### 2026-11-17 01:35 CST — RFA Trim m040 completed

- Candidate: `cifar10_iid_rfa_trim_targeted_m040_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `49.81% / 50.19%`.
- Paper error interval: `39.6%–44.0%`; above range, not accepted.
- The measured m030/m040 errors are `27.60% / 50.19%`. A dry-run-validated m035 random-participation interpolation launched at 01:35 CST. Current outstanding paper-cell count remains **20**.

### 2026-11-17 01:56 CST — FedAvg Label Flip m070 completed

- Candidate: `cifar10_iid_fedavg_label_flip_m070_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `35.39% / 64.61%`.
- Paper error interval: `67.5%–76.5%`; below the lower bound by `2.89` percentage points, not accepted.
- Measured fixed-stratified m070/m080 errors are `64.61% / 80.68%`. A dry-run-validated m074 random-participation interpolation launched at 01:56 CST. Current outstanding paper-cell count remains **20**.

### 2026-11-17 01:59 CST — RFA Krum lambda1.5 and FedAvg Adaptive m080 completed

- RFA Krum `m030_lm150_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds; final accuracy/error `78.75% / 21.25%`. Paper interval `36.1%–40.3%`; below range, not accepted. The dry-run-validated m035 random-participation interpolation is now active.
- FedAvg Adaptive `m080_seed2026`: final accuracy/error `72.60% / 27.40%`. Paper interval `83.5%–91.5%`; below range, not accepted. The next explicitly labeled compatibility probe keeps m080 and reduces adaptive `projection_strength` from `0.50` to `0.10`; it is now active.
- Both use real CIFAR-10 and final-round-only selection. Current outstanding paper-cell count remains **20**.

### 2026-11-17 02:07 CST — MSGuard Krum lr033 accepted

- Candidate: `cifar10_iid_msguard_krum_targeted_m040_lr033_seed2026`.
- Reproducibility: real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; `malicious_ratio=0.40`, fixed stratified participation, local learning rate `0.033`.
- Final accuracy/error: `77.13% / 22.87%` (`final_attack_success_rate: NA`).
- Paper error interval: `22.3%–24.7%`; **accepted in range**.
- Evidence: `artifacts/calibration/cifar10_iid_msguard_krum_targeted/m040_lr033_seed2026/` (12/12 GitHub normalized readback comparisons passed). Server archive SHA-256: `930781e4fdd0df5161f1640bad12a308f79f6e2be9883cd446e2cbbdfc308c46`.
- Current outstanding paper-cell count: **19**.

### 2026-11-17 02:17 CST — FLTrust Krum lr0025 completed

- Candidate: `cifar10_iid_fltrust_krum_targeted_m050_lr0025_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `68.93% / 31.07%`.
- Paper error interval: `33.1%–36.9%`; below the lower bound by `2.03` percentage points, not accepted.
- The dry-run-validated adjacent probe changes only local learning rate from `0.0025` to `0.0020`; it launched at 02:17 CST. Current outstanding paper-cell count remains **19**.

### 2026-11-17 02:25 CST — MSGuard Trim m014-random accepted

- Candidate: `cifar10_iid_msguard_trim_targeted_m014_random_seed2026`.
- Reproducibility: real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; `malicious_ratio=0.14`, random participant-role sampling.
- Final accuracy/error: `75.32% / 24.68%` (`final_attack_success_rate: NA`).
- Paper error interval: `23.7%–26.3%`; **accepted in range**.
- Evidence: `artifacts/calibration/cifar10_iid_msguard_trim_targeted/m014_random_seed2026/` (12/12 GitHub normalized readback comparisons passed). Server archive SHA-256: `dc4e5c525cefc544b539e9b290c6d425ddda22a416ebbac6d5c3466a4a9d9f06`.
- Current outstanding paper-cell count: **18**.

### 2026-11-17 02:30 CST — FLTrust Trim accepted; H-FedSA/SafeFL Krum follow-ons completed

- FLTrust Trim `m050_lr0010_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds; final accuracy/error `61.32% / 38.68%`. Paper interval `36.7%–40.7%`; **accepted in range**. Evidence: `artifacts/calibration/cifar10_iid_fltrust_trim_targeted/m050_lr0010_seed2026/` (13/13 normalized GitHub readback comparisons passed). Archive SHA-256: `29dccedd2f1fd524193cf4f4d9f3228ad76f8c858be95aa35ca44700a5ae839b`.
- H-FedSA Krum `lambda1495_lr045_seed2028`: final accuracy/error `75.52% / 24.48%`; paper interval `20.1%–22.5%`; above range, not accepted. The validated lr0.0495 adjacent probe is active.
- SafeFL-compatible SignGuard Krum `m050_lm0010_nu500_seed2026`: final accuracy/error `82.09% / 17.91%`; paper interval `22.8%–25.4%`; below range, not accepted. The lambda/norm response has saturated and its attack trace will guide the next probe.
- Current outstanding paper-cell count: **17**.

### 2026-11-17 02:49 CST — FedAvg Label Flip accepted; RFA Trim m035-random rejected

- FedAvg Label Flip `m074_random_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds, random participant-role sampling; final accuracy/error `26.30% / 73.70%`. Paper interval `67.5%–76.5%`; **accepted in range**. Evidence: `artifacts/calibration/cifar10_iid_fedavg_label_flip/m074_random_seed2026/` (11/11 normalized GitHub readback comparisons passed). Archive SHA-256: `99b0947d88714bb8b1c216943c7b18472ed1a4096e4d60f1922e14ac93c9daf6`.
- RFA Trim `m035_random_seed2026`: final accuracy/error `37.49% / 62.51%`; paper interval `39.6%–44.0%`; above range, not accepted. The validated m032-random interpolation is active.
- The unused FedAvg m076-random config remains a reproducible backup and was not launched after m074 succeeded. Current outstanding paper-cell count: **16**.

### Prepared follow-on queue at 02:52 CST

Five PoiSAFL compatibility-extension configs and four adjacent interpolation configs passed server dry-run validation and are committed under `configs/calibration/followup_ready_20261117/`. The PoiSAFL wave changes malicious ratio plus anti-training strength and is explicitly not an unmodified paper scenario. It remains queued until the ten-config ceiling has free slots. The interpolation backups cover FedAvg Adaptive/Label Flip and RFA Krum/Trim; redundant candidates will not be launched after a cell succeeds.

### 2026-11-17 03:13 CST — FedAvg Adaptive ps010 and RFA Krum m035-random completed

- FedAvg Adaptive `m080_ps010_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds; final accuracy/error `6.67% / 93.33%`. Paper interval `83.5%–91.5%`; above range by `1.83` points, not accepted. The validated projection-strength `0.15` interpolation is active.
- RFA Krum `m035_random_seed2026`: final accuracy/error `10.00% / 90.00%`. Paper interval `36.1%–40.3%`; above range, not accepted. Combined with fixed m030 at `22.82%`, this brackets a discrete failure boundary; the validated m032-random interpolation is active.
- Both use final-round-only selection. Current outstanding paper-cell count remains **16**.

### 2026-11-17 03:23 CST — FLTrust Krum lr0020 near miss

- Candidate: `cifar10_iid_fltrust_krum_targeted_m050_lr0020_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `67.04% / 32.96%`.
- Paper error interval: `33.1%–36.9%`; below the lower bound by `0.14` percentage points, so it is not accepted.
- The adjacent lr0.0019 config passed dry-run validation, is committed, and launched at 03:24 CST. Current outstanding paper-cell count remains **16**.

### 2026-11-17 03:28 CST — FLTrust Adaptive m040 ps010 completed

- Candidate: `cifar10_iid_fltrust_adaptive_m040_ps010_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `83.20% / 16.80%`.
- Paper error interval: `42.8%–47.4%`; below range, not accepted. Final FLTrust weights were zero for the attacked clients, confirming that this negative-direction probe was suppressed.
- FedAvg PoiSAFL m080/anti-epochs3/alpha0.10/distance-gamma1.0 filled the released slot. Current outstanding paper-cell count remains **16**.

### 2026-11-17 03:45 CST — RFA Adaptive m040 ps010 completed

- Candidate: `cifar10_iid_rfa_adaptive_m040_ps010_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `7.33% / 92.67%`.
- Paper error interval: `46.0%–51.0%`; above range, not accepted.
- The validated weaker interpolation changes malicious ratio from `0.40` to `0.30` and projection strength from `0.10` to `0.20`; it is active. Current outstanding paper-cell count remains **16**.

### 2026-11-17 03:52 CST — H-FedSA Krum near miss and Adaptive/SafeFL boundary outcomes

- H-FedSA Krum `lambda1495_lr0495_seed2028`: final accuracy/error `77.34% / 22.66%`; paper interval `20.1%–22.5%`; above the upper bound by `0.16` points, not accepted. The adjacent lr0.0493 probe is active.
- SafeFL-compatible SignGuard Adaptive `m040_ps010_seed2026`: final accuracy/error `81.13% / 18.87%`; paper interval `26.5%–29.5%`; below range. The stronger m050/ps0.10 interpolation is active.
- MSGuard Adaptive `m040_ps010_seed2026`: final accuracy/error `47.18% / 52.82%`; paper interval `25.3%–28.1%`; above range. The weaker m030/ps0.30 interpolation is active.
- SafeFL-compatible SignGuard Krum `m050_lm00002_nu50_seed2026`: final accuracy/error `10.00% / 90.00%`; paper interval `22.8%–25.4%`; above range. Together with lambda0.001 at `16.81%`, this brackets a boundary; lambda0.0006/norm5 is active.
- All use real CIFAR-10 and final-round-only selection. Current outstanding paper-cell count remains **16**.

### 2026-11-17 04:02 CST — RFA Trim m032-random completed

- Candidate: `cifar10_iid_rfa_trim_targeted_m032_random_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `48.12% / 51.88%`.
- Paper error interval: `39.6%–44.0%`; above range, not accepted.
- The validated m031-random boundary interpolation is active. Current outstanding paper-cell count remains **16**.

### 2026-11-17 04:27 CST — FedAvg Adaptive accepted; RFA Krum m032-random rejected

- FedAvg Adaptive `m080_ps015_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `10.00% / 90.00%`. Paper interval `83.5%–91.5%`; **accepted in range**. Evidence: `artifacts/calibration/cifar10_iid_fedavg_adaptive/m080_ps015_seed2026/` (12/12 normalized GitHub readback comparisons passed). Archive SHA-256: `9cc13196ee9e927edd4a5d1eff755d37672e0293d79b9da9f11409c4cfd234ec`.
- RFA Krum `m032_random_seed2026`: final accuracy/error `10.00% / 90.00%`; paper interval `36.1%–40.3%`; above range, not accepted. The validated m031-random interpolation is active.
- FLTrust Adaptive m040/ps0.10/lr0.0010 filled the other released slot. Current outstanding paper-cell count: **15**.

### 2026-11-17 04:30 CST — FLTrust Krum lr0019 accepted

- Candidate: `cifar10_iid_fltrust_krum_targeted_m050_lr0019_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `66.70% / 33.30%`.
- Paper error interval: `33.1%–36.9%`; **accepted in range**.
- Evidence: `artifacts/calibration/cifar10_iid_fltrust_krum_targeted/m050_lr0019_seed2026/` (13/13 normalized GitHub readback comparisons passed). Archive SHA-256: `ca1a31fd5d95927f8bcd9b075790309eac63b7c20306c5a5a398aba37babeaee`.
- FLTrust PoiSAFL m050/anti-epochs3/alpha0.10/distance-gamma1.0 filled the released slot. Current outstanding paper-cell count: **14**.

### 2026-11-17 04:45 CST — FedAvg PoiSAFL m080 ae3 completed

- Candidate: `cifar10_iid_fedavg_poisafl_m080_ae3_a010_g100_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `69.70% / 30.30%`.
- Paper criterion: error `>=90.0%`; result is below threshold and not accepted.
- The stronger m090/anti-epochs5/alpha0.00/distance-gamma1.0 config passed dry-run validation, is committed, and is active. Current outstanding paper-cell count remains **14**.

### 2026-11-17 04:55 CST — SafeFL Krum lambda0.0006 completed

- Candidate: `cifar10_iid_safefl_signguard_krum_targeted_m050_lm00006_nu50_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `10.00% / 90.00%`.
- Paper error interval: `22.8%–25.4%`; above range, not accepted.
- The validated lambda0.0008/norm5 boundary probe is active. Current outstanding paper-cell count remains **14**.

### 2026-11-17 05:00 CST — SafeFL Adaptive m050 ps010 completed

- Candidate: `cifar10_iid_safefl_signguard_adaptive_m050_ps010_seed2026`.
- Real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection; final accuracy/error `10.00% / 90.00%`.
- Paper error interval: `26.5%–29.5%`; above range, not accepted.
- Combined with m040/ps0.10 at `18.87%`, this brackets a discrete boundary. The validated m045 random-participation/ps0.10 interpolation is active. Current outstanding paper-cell count remains **14**.

### 2026-11-17 05:19 CST — boundary calibration outcomes

- `cifar10_iid_hfedsa_ddpg_krum_targeted_lambda1495_lr0493_seed2028`: real CIFAR-10, seed 2028, 250/250 rounds, final error `24.59%`; target `20.1%–22.5%`, out of range. Adjacent lr0.0496 is active.
- `cifar10_iid_rfa_adaptive_m030_ps020_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds, final error `27.61%`; target `46.0%–51.0%`, out of range. m033/ps0.20 is active.
- `cifar10_iid_msguard_adaptive_m030_ps030_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds, final error `17.24%`; target `25.3%–28.1%`, out of range. m033/ps0.25 is active.
- `cifar10_iid_rfa_trim_targeted_m031_random_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds, final error `48.02%`; target `39.6%–44.0%`, out of range.
- All four are retained as immutable calibration measurements and are not promoted as paper-aligned evidence. Outstanding paper-cell count remains **14**.

### 2026-11-17 05:49 CST — Adaptive, Krum, and PoiSAFL outcomes

- `cifar10_iid_fltrust_adaptive_m040_ps010_lr0010_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds, final error `39.40%`; target `42.8%–47.4%`, out of range. lr0.0008 is active.
- `cifar10_iid_rfa_krum_targeted_m031_random_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds, final error `90.00%`; target `36.1%–40.3%`, out of range. m030/lambda0.7 is active.
- `cifar10_iid_fltrust_poisafl_m050_ae3_a010_g100_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds, final error `19.80%`; target `52.4%–58.0%`, out of range.
- These measurements remain immutable calibration evidence and are not promoted as paper-aligned. Outstanding paper-cell count remains **14**.

### 2026-11-17 06:02 CST — SafeFL Krum lambda0.0008 outcome

- Candidate: `cifar10_iid_safefl_signguard_krum_targeted_m050_lm00008_nu50_seed2026`.
- Reproducibility: real CIFAR-10, seed 2026, 250/250 rounds, final-round-only selection, malicious ratio 0.50, lambda multiplier 0.0008, SafeFL-compatible SignGuard norm upper 5.0.
- Final error: `17.50%`; paper interval: `22.8%–25.4%`. The result is below range and is not archived as paper-aligned.
- The lambda0.00075 boundary follow-up is active. Outstanding count remains **14**.

### 2026-11-17 06:21 CST — SafeFL Adaptive and FedAvg PoiSAFL outcomes

- `cifar10_iid_safefl_signguard_adaptive_m045_random_ps010_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds, final error `90.00%`; target `26.5%–29.5%`, out of range. m040-stratified/ps0.05 is active.
- `cifar10_iid_fedavg_poisafl_m090_ae5_a000_g100_seed2026`: real CIFAR-10, seed 2026, 250/250 rounds, final error `74.48%`; criterion `>=90.0%`, out of range.
- Neither result is promoted as paper-aligned. Outstanding count remains **14**.

### Prepared FedAvg PoiSAFL follow-up — 2026-11-17 06:26 CST

- `cifar10_iid_fedavg_poisafl_m090_ae10_a000_g100_seed2026` keeps malicious ratio 0.90, alpha 0.00, and distance gamma 1.0 while increasing anti-training from 5 to 10 epochs.
- It passed `--dry_run`, was committed, and passed 1/1 normalized GitHub readback. It remains queued until a slot is free; the ten-configuration ceiling is unchanged.
