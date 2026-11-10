# Reproduction status

This document separates implemented software paths from completed measured
experiments. A checked implementation item does not imply that a paper table
has been reproduced.

| Area | Status | Notes |
| --- | --- | --- |
| Core federated trainer | Implemented and smoke-tested | Real CIFAR-10 run verified on an NVIDIA A100 |
| Paper H-FedSA features and weight formula | Implemented and unit-tested | Direction, intensity, normalized sparsity, and probabilistic weight |
| Three-component GMM | Implemented and unit-tested | Full covariance is the paper-manifest default |
| DDPG exploration control | Implemented and smoke-tested | 39-dimensional state; server-root validation feedback only |
| Client-role sampling | Implemented and unit-tested | Preserves malicious/unseen ratios in small rounds |
| CIFAR-10-C unseen data | Implemented and real-data smoke-tested | Gaussian noise and shot noise; exact 40% replacement |
| FEMNIST + Chars74K | Pending | Real shifted-data adapter not yet implemented |
| GTSRB + CTSDB/GTSDB | Pending | Dataset naming/source must be reconciled with the paper |
| Stanford Cars + CompCars | Pending | Real shifted-data adapter not yet implemented |
| FedAvg, FLTrust, RFA | Implemented | Formal comparison manifests and multi-seed runs pending |
| SafeFL, MSGuard | Pending | Current factory raises an explicit not-implemented path |
| Label flip, scaling, backdoor scaling | Implemented | Protocol-level validation still required per paper table |
| Krum-targeted, Trim-targeted, PoiSAFL | Pending | Not yet implemented |
| Full paper tables | Pending | No smoke or synthetic output is accepted as a measured paper result |

The CIFAR-10 Table II(d) values and five fixed reporting seeds are recorded in
`configs/paper/targets/table_ii_cifar10_iid.yaml`. This target manifest is used
to calculate measured gaps; it is never copied into run-generated metrics.

Curated measured summaries may be added under `results/published/` only with
the resolved configuration, seed list, raw run locations, and aggregation
method. Generated run directories remain ignored by Git.

