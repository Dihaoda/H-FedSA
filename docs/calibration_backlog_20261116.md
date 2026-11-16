# Calibration backlog (2026-11-16)

This backlog lists measured CIFAR-10 IID cells that do not fully satisfy the
paper interval. It is a transparent calibration plan, not permission to replace
measured values. Existing out-of-range evidence remains immutable. New
candidates use fixed seed 2026, 250 rounds, final-round-only selection, unique
configuration/output paths, and are labeled as calibration runs.

## Summary

There are 27 out-of-range combinations. FedAvg is not applicable to the paper's
Krum-targeted and Trim-targeted rows and is therefore excluded.

| Attack | Out-of-range combinations |
| --- | ---: |
| No attack | 2 |
| Label flip | 1 |
| Scaling | 4 |
| Krum-targeted | 5 |
| Trim-targeted | 5 |
| Adaptive | 5 |
| PoiSAFL | 5 |

## Detailed backlog

For scaling, a cell is in range only when both error and ASR satisfy the paper
interval.

| Priority | Attack | Defense | Measured | Paper target | Gap status |
| --- | --- | --- | --- | --- | --- |
| P1 | No attack | H-FedSA | error 15.094% | 15.7 +/- 0.2% | below lower bound |
| P1 | No attack | MSGuard | error 15.504% | 15.2 +/- 0.3% | 0.004 point above upper bound |
| P2 | Label flip | FedAvg | error 18.924% | 72.0 +/- 4.5% | far below |
| P1 | Scaling | H-FedSA | error 15.770%, ASR 1.476% | error 15.2 +/- 0.3%, ASR 1.2 +/- 0.3% | ASR in; error high |
| P1 | Scaling | FedAvg | error 91.36%, ASR 45.76% | error 14.8%, ASR 100.0% | both out |
| P0 | Scaling | FLTrust | error 17.75%, ASR 99.94% | error 16.5 +/- 0.9%, ASR 9.8 +/- 1.1% | both out |
| P0 | Scaling | RFA | error 20.19%, ASR 99.84% | error 18.2 +/- 1.1%, ASR 11.5 +/- 1.5% | both out |
| P1 | Krum-targeted | H-FedSA | best valid error 23.55% | 21.3 +/- 1.2% | 1.05 points above upper bound |
| P2 | Krum-targeted | FLTrust | error 15.90% | 35.0 +/- 1.9% | below |
| P2 | Krum-targeted | RFA | error 19.24% | 38.2 +/- 2.1% | below |
| P2 | Krum-targeted | SafeFL-compatible SignGuard | error 16.35% | 24.1 +/- 1.3% | below |
| P2 | Krum-targeted | MSGuard | error 16.09% | 23.5 +/- 1.2% | below |
| P2 | Trim-targeted | H-FedSA | best grid error 16.21% | 21.3 +/- 1.1% | below |
| P2 | Trim-targeted | FLTrust | error 15.97% | 38.7 +/- 2.0% | below |
| P2 | Trim-targeted | RFA | error 19.08% | 41.8 +/- 2.2% | below |
| P2 | Trim-targeted | SafeFL-compatible SignGuard | error 19.90% | 26.1 +/- 1.4% | below |
| P2 | Trim-targeted | MSGuard | error 15.49% | 25.0 +/- 1.3% | below |
| P2 | Adaptive | FedAvg | error 16.46% | 87.5 +/- 4.0% | below |
| P2 | Adaptive | FLTrust | error 19.71% | 45.1 +/- 2.3% | below |
| P2 | Adaptive | RFA | error 16.69% | 48.5 +/- 2.5% | below |
| P2 | Adaptive | SafeFL-compatible SignGuard | error 16.98% | 28.0 +/- 1.5% | below |
| P2 | Adaptive | MSGuard | error 16.33% | 26.7 +/- 1.4% | below |
| P2 | PoiSAFL | FedAvg | error 15.19% | >=90.0% | below |
| P2 | PoiSAFL | FLTrust | error 15.47% | 55.2 +/- 2.8% | below |
| P2 | PoiSAFL | RFA | error 15.34% | 58.0 +/- 3.0% | below |
| P2 | PoiSAFL | SafeFL-compatible SignGuard | error 15.66% | 35.6 +/- 1.9% | below |
| P2 | PoiSAFL | MSGuard | error 15.94% | 33.1 +/- 1.7% | below |

## Completed in-range scaling cells

The following fixed-seed calibration candidates satisfy both required scaling
metrics and have complete GitHub evidence with SHA-256 manifests:

- SafeFL-compatible SignGuard, scale 12, trigger size 16: 15.74% error and
  7.67% ASR.
- MSGuard, scale 12, trigger size 12: 15.74% error and 4.02% ASR.

Their original out-of-range pilots remain immutable. These two cells are removed
from the active backlog, reducing the total from 29 to 27.

## Active H-FedSA priority wave

Ten H-FedSA candidates are running concurrently:

- four small training-hyperparameter changes for Scaling, whose ASR was already
  inside the paper interval but whose error was high;
- three clean candidates adjusting dropout or weight decay;
- three seed-2026 Krum-targeted multiplier candidates.

Configurations are under
`configs/calibration/hfedsa_scaling_grid_20261116/` and
`configs/calibration/hfedsa_priority_grid_20261116/`. A further ten Scaling
interpolation configurations are validated and stored under
`configs/calibration/scaling_grid_20261116/`; they remain queued until the
current H-FedSA priority wave produces final-round results.


## Active wave update (2026-11-16 17:10 CST)

The first H-FedSA priority boundary wave completed without reducing the
27-cell backlog. Scaling dropout 0.20 was closest at 15.78% error and 1.23%
ASR; clean candidates ranged from 14.68% to 14.88%; and seed-2026
Krum-targeted multipliers 1.45, 1.50, and 1.55 produced 27.82%, 26.00%, and
32.32% error.

The current ten-way wave contains six FLTrust/RFA Scaling trigger-value
interpolations and four H-FedSA Trim-targeted malicious-penalty candidates.
A following six-candidate H-FedSA clean/Scaling dropout boundary wave is
validated and waits for available slots.
