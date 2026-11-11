# Reproduction status

This document separates implemented software paths from completed measured
experiments. A checked implementation item does not imply that a paper table
has been reproduced.

| Area | Status | Notes |
| --- | --- | --- |
| Core federated trainer | Implemented and smoke-tested | Real CIFAR-10 run verified on an NVIDIA A100 |
| Paper H-FedSA features and weight formula | Implemented and unit-tested | Direction, intensity, normalized sparsity, and probabilistic weight |
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
| SafeFL-compatible SignGuard, MSGuard | Implemented and smoke-tested | SafeFL rule ambiguity and MSGuard artifact limitations are documented |
| Label flip, scaling, backdoor scaling | Implemented; CIFAR-10 IID H-FedSA scaling formally measured | Five fixed-seed result: `15.770 +/- 0.317%` error and `1.476 +/- 0.172%` ASR |
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

