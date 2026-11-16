# Calibration backlog (2026-11-16)

This backlog lists measured CIFAR-10 IID cells that do not fully satisfy the
paper interval. It is a transparent calibration plan, not permission to replace
measured values. Existing out-of-range evidence remains immutable. New
candidates use fixed seed 2026, 250 rounds, final-round-only selection, unique
configuration/output paths, and are labeled as calibration runs.

## Summary

There are 23 out-of-range combinations under the current error-only acceptance rule and the user-approved reuse of prior final-round seed results. FedAvg is not applicable to the paper's
Krum-targeted and Trim-targeted rows and is therefore excluded.

| Attack | Out-of-range combinations |
| --- | ---: |
| No attack | 0 |
| Label flip | 1 |
| Scaling | 2 |
| Krum-targeted | 5 |
| Trim-targeted | 5 |
| Adaptive | 5 |
| PoiSAFL | 5 |

## Detailed backlog

For scaling, the user-approved relaxed rule effective from 2026-11-16 19:32 CST
accepts a cell when final-round error is inside the paper error interval. ASR is
still measured and reported but is not an acceptance condition. Earlier text
about joint error/ASR matching is retained as historical campaign context.

| Priority | Attack | Defense | Measured | Paper target | Gap status |
| --- | --- | --- | --- | --- | --- |
| P2 | Label flip | FedAvg | error 18.924% | 72.0 +/- 4.5% | far below |
| P1 | Scaling | FedAvg | error 91.36%, ASR 45.76% | error 14.8%, ASR 100.0% | both out |
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


## Calibration outcome update (2026-11-16 18:11 CST)

FLTrust/RFA trigger values 1.25--1.75 and H-FedSA Trim malicious penalties
0.0--0.6 all completed outside their paper intervals. Lower FLTrust/RFA trigger
values 0.50 and 0.75 are running. H-FedSA Trim retention-floor probes, if run,
will be labeled compatibility extensions because the floor is not part of the
paper-mode default.


## Completed H-FedSA clean cell

H-FedSA clean dropout 0.10 completed at 15.81% final error, inside the
15.5--15.9% paper interval. Complete evidence is stored under
`artifacts/calibration/cifar10_iid_clean_hfedsa_ddpg/d010_seed2026/`.
This reduces the active backlog from 27 to 26 cells. The existing five-seed
formal clean summary is unchanged.


## Low-value Scaling update (2026-11-16 19:10 CST)

FLTrust and RFA values 0.50/0.75 completed outside the joint error/ASR
criteria. RFA value 0.75 reached 10.68% ASR but only 15.27% error. A six-run
joint learning-rate wave is active/queued with FLTrust value 0.65 and RFA
value 0.75.


## H-FedSA Scaling low-dropout follow-on (2026-11-16 19:17 CST)

Because the higher-dropout boundary wave did not lower final error enough,
three seed-2026 candidates with dropout 0.00, 0.05, and 0.10 are validated and
queued. They retain the same attack, defense, optimizer, 250-round budget, and
final-round-only evaluation policy; only model dropout changes.


## H-FedSA Trim stronger-retention follow-on (2026-11-16 19:21 CST)

The current 0.02--0.20 compatibility-extension wave shows the expected
mid-run monotonic direction, so retention floors 0.30, 0.40, and 0.50 are
validated and queued. Selection remains based only on the final round; these
runs are explicitly not unmodified paper-mode H-FedSA.


## Error-only acceptance update (2026-11-16 19:32 CST)

The acceptance rule was relaxed prospectively and then applied to existing
immutable final-round measurements: error inside the paper interval is now
sufficient, while ASR remains a reported diagnostic. FLTrust Scaling trigger
value 1.50 completed at 15.72% error and 39.22% ASR. Its error is inside the
15.6--17.4% paper interval, so the cell is removed from the active backlog;
its ASR is explicitly not claimed to match. Complete verified evidence is in
`artifacts/calibration/cifar10_iid_fltrust_scaling/scale010_p001_t2_v150_seed2026/`.
This reduces the active backlog from 26 to 25 cells. Two redundant unfinished
FLTrust learning-rate probes were stopped and the queue was consolidated around
RFA Scaling and the remaining H-FedSA candidates.


## H-FedSA Trim retention outcomes (2026-11-16 19:45 CST)

The transparent compatibility-extension candidates with retention floors 0.02,
0.05, 0.10, and 0.20 completed at 16.68%, 17.73%, 18.40%, and 19.07% final
error, respectively, versus the 20.2--22.4% paper interval. None is accepted,
but the monotonic direction supports continuing the preregistered 0.30, 0.40,
and 0.50 candidates. These results are not unmodified paper-mode H-FedSA.


## Reused prior formal seed outcomes (2026-11-16 19:50 CST)

At the user's direction, existing real final-round seed outcomes are reused
before launching new work. The formal MSGuard clean campaign contains seed 2029
at 15.21% error and seed 2030 at 15.35%, both inside the 14.9--15.5% interval.
The formal H-FedSA Scaling five-seed summary records a minimum final error of
15.46%, inside the 14.9--15.5% interval; ASR is not an acceptance gate under
the relaxed rule. These two cells are removed from the backlog, reducing it
from 25 to 23. Four unfinished MSGuard clean probes and three newly started
H-FedSA Scaling probes were stopped as redundant; their partial logs remain on
the server. The formal summaries remain unchanged and are the cited evidence.


## Targeted-attack malicious-ratio extension wave (2026-11-16 19:57 CST)

Four fixed-seed candidates are active for SafeFL-compatible SignGuard and
MSGuard under Krum-targeted and Trim-targeted attacks. Relative to the existing
pilots, only `malicious_ratio` changes from 0.20 to 0.30. The configs are under
`configs/calibration/targeted_m030_20261116/` and are explicitly labeled
calibration extensions, because the paper target uses the original scenario.
They fill four slots released by prior-result reuse; the server remains at ten
active configurations.


## RFA Scaling lower-learning-rate follow-on (2026-11-16 20:25 CST)

The active learning-rate 0.035--0.045 candidates remain below the paper error
interval late in training. Two otherwise identical fixed-seed candidates at
0.025 and 0.030 passed dry-run validation, are committed in the existing
Scaling grid, and wait for automatic slot refill. Acceptance uses final-round
error only.
