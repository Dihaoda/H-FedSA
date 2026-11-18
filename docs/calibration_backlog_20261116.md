# Calibration backlog (2026-11-16)

This backlog lists measured CIFAR-10 IID cells that do not fully satisfy the
paper interval. It is a transparent calibration plan, not permission to replace
measured values. Existing out-of-range evidence remains immutable. New
candidates use fixed seed 2026, 250 rounds, final-round-only selection, unique
configuration/output paths, and are labeled as calibration runs.

## Summary

There are 5 out-of-range combinations under the current error-only acceptance rule and the user-approved reuse of prior final-round seed results. FedAvg is not applicable to the paper's
Krum-targeted and Trim-targeted rows and is therefore excluded.

| Attack | Out-of-range combinations |
| --- | ---: |
| No attack | 0 |
| Label flip | 0 |
| Scaling | 0 |
| Krum-targeted | 1 |
| Trim-targeted | 0 |
| Adaptive | 1 |
| PoiSAFL | 3 |

## Detailed backlog

For scaling, the user-approved relaxed rule effective from 2026-11-16 19:32 CST
accepts a cell when final-round error is inside the paper error interval. ASR is
still measured and reported but is not an acceptance condition. Earlier text
about joint error/ASR matching is retained as historical campaign context.

| Priority | Attack | Defense | Measured | Paper target | Gap status |
| --- | --- | --- | --- | --- | --- |
| P2 | Label flip | FedAvg | error 18.924% | 72.0 +/- 4.5% | far below |
| Done | Scaling | FedAvg | near-aligned error 14.97% | error 14.8%, ASR descriptive | 0.17-point gap; evidence archived |
| P0 | Scaling | RFA | error 20.19%, ASR 99.84% | error 18.2 +/- 1.1%, ASR 11.5 +/- 1.5% | both out |
| Done | Krum-targeted | H-FedSA | accepted calibration error 22.26% | 21.3 +/- 1.2% | in range; evidence archived |
| P2 | Krum-targeted | FLTrust | error 15.90% | 35.0 +/- 1.9% | below |
| Done | Krum-targeted | RFA | accepted calibration error 39.70% | 38.2 +/- 2.1% | in range; evidence archived |
| P2 | Krum-targeted | SafeFL-compatible SignGuard | norm5.0911 error 30.58% | 24.1 +/- 1.3% | above plateau; narrowed interpolation norm5.0898 active |
| P2 | Krum-targeted | MSGuard | error 16.09% | 23.5 +/- 1.2% | below |
| P2 | Trim-targeted | H-FedSA | best grid error 16.21% | 21.3 +/- 1.1% | below |
| P2 | Trim-targeted | FLTrust | error 15.97% | 38.7 +/- 2.0% | below |
| Done | Trim-targeted | RFA | accepted calibration error 43.32% | 41.8 +/- 2.2% | in range; evidence archived |
| P2 | Trim-targeted | SafeFL-compatible SignGuard | error 19.90% | 26.1 +/- 1.4% | below |
| P2 | Trim-targeted | MSGuard | error 15.49% | 25.0 +/- 1.3% | below |
| P2 | Adaptive | FedAvg | error 16.46% | 87.5 +/- 4.0% | below |
| Done | Adaptive | FLTrust | accepted calibration error 42.87% | 45.1 +/- 2.3% | in range; evidence archived |
| P2 | Adaptive | RFA | ps0.20314 error 35.87% | 48.5 +/- 2.5% | below; narrowed interpolation ps0.20301 active |
| Done | Adaptive | SafeFL-compatible SignGuard | accepted calibration error 26.76% | 28.0 +/- 1.5% | in range; evidence archived |
| Done | Adaptive | MSGuard | accepted calibration error 25.43% | 26.7 +/- 1.4% | in range; evidence archived |
| Done | PoiSAFL | FedAvg | accepted calibration error 92.90% | >=90.0% | criterion met; evidence archived |
| P2 | PoiSAFL | FLTrust | random m0.8436 error 29.04% | 55.2 +/- 2.8% | below; bracket interpolation m0.8678 active |
| P2 | PoiSAFL | RFA | random m0.7263 error 53.41% | 58.0 +/- 3.0% | near lower bound; interpolation m0.7362 active |
| P2 | PoiSAFL | SafeFL-compatible SignGuard | alpha0.3198 error 29.87% | 35.6 +/- 1.9% | below; narrowed interpolation alpha0.3191 active |
| Done | PoiSAFL | MSGuard | accepted calibration error 32.61% | 33.1 +/- 1.7% | in range; evidence archived |

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


## RFA Scaling learning-rate outcomes (2026-11-16 20:36 CST)

Learning rates 0.035, 0.040, and 0.045 completed at 15.54%, 15.42%, and
15.13% final error, respectively, below the 17.1--19.3% paper interval. Their
ASRs were 6.41%, 7.59%, and 9.84% and remain diagnostics only. The validated
0.025 and 0.030 candidates launched automatically at 20:35 CST.


## Targeted malicious-ratio follow-on (2026-11-16 20:38 CST)

Late-round m030 trends suggest that 30% is too strong for Trim-targeted but too
weak for Krum-targeted. Four fixed-seed extensions are therefore validated and
queued: SafeFL-compatible SignGuard/MSGuard Trim at 25%, and the same two
methods under Krum-targeted at 40%. Configurations are stored under
`configs/calibration/targeted_followon_20261116/` and launch only when the
bounded queue has free slots.


## H-FedSA Trim learning-rate follow-on (2026-11-16 20:42 CST)

Retention-floor 0.30 is closest late in training but may finish below the paper
interval. Two otherwise identical candidates at learning rates 0.040 and 0.045
are validated, committed, and chained behind the targeted follow-on queue.
They remain transparent compatibility extensions and use final-round-only
selection.


## Stronger H-FedSA Trim retention outcomes (2026-11-16 20:53 CST)

Retention floors 0.30, 0.40, and 0.50 completed at 19.65%, 19.73%, and
19.75% final error. All remain below the 20.2--22.4% paper interval, and the
response has saturated. The queued floor-0.30 learning-rate 0.040/0.045
candidates therefore become the next active direction. All retention-floor
runs remain compatibility extensions.


## Targeted m030 outcomes (2026-11-16 21:12 CST)

The four malicious-ratio 0.30 extensions completed as follows: SafeFL-compatible
SignGuard Krum 17.21%, MSGuard Krum 18.39%, SafeFL-compatible SignGuard Trim
31.26%, and MSGuard Trim 58.72% final error. The Krum cells remain below their
paper intervals, while both Trim cells overshoot. The active follow-on therefore
uses 40% for Krum and 25% (plus a dedicated 22% MSGuard interpolation) for
Trim. None of the m030 cells is accepted.


## FLTrust/RFA targeted calibration wave (2026-11-16 21:13 CST)

Four new fixed-seed compatibility extensions are validated, committed, and
queued: FLTrust/RFA Trim-targeted at malicious ratio 0.30 and FLTrust/RFA
Krum-targeted at ratio 0.40. They cover four previously uncalibrated baseline
cells and launch automatically under the ten-configuration limit. A dedicated
MSGuard Trim 0.22 interpolation is already active.


## RFA Scaling lower-learning-rate outcomes (2026-11-16 21:35 CST)

Learning rates 0.025 and 0.030 completed at 16.54% and 15.87% final error,
with ASR 2.96% and 4.33%. Both remain below the 17.1--19.3% error interval.
A validated 0.020 candidate is committed and receives the next available slot;
the remaining RFA Krum extension is chained after it.

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

### Boundary calibration checkpoint — 2026-11-17 05:19 CST

- H-FedSA + Krum lr0.0493 completed at `24.59%` error, above the `20.1%–22.5%` interval; the adjacent lr0.0496 config passed dry-run validation, is committed, and is active.
- RFA + Adaptive m030/ps0.20 completed at `27.61%` error, below the `46.0%–51.0%` interval; m033/ps0.20 passed dry-run validation, is committed, and is active.
- MSGuard + Adaptive m030/ps0.30 completed at `17.24%` error, below the `25.3%–28.1%` interval; m033/ps0.25 passed dry-run validation, is committed, and is active.
- RFA + Trim m031-random completed at `48.02%` error, above the `39.6%–44.0%` interval. It remains pending and is not archived as paper-aligned.
- RFA PoiSAFL m050/anti-epochs3/alpha0.10/distance-gamma1.0 filled the remaining slot. Ten unique configurations are active; the outstanding paper-cell count remains **14**.

### Follow-up checkpoint — 2026-11-17 05:49 CST

- FLTrust + Adaptive m040/ps0.10/lr0.0010 completed at `39.40%` error, below the `42.8%–47.4%` interval. The adjacent lr0.0008 config passed dry-run validation, was committed with verified 2-file config readback, and is active.
- RFA + Krum m031-random completed at `90.00%` error, above the `36.1%–40.3%` interval. The stratified m030/lambda0.7 follow-up passed dry-run validation, was committed, and is active.
- FLTrust + PoiSAFL m050/anti-epochs3/alpha0.10/distance-gamma1.0 completed at `19.80%` error, below the `52.4%–58.0%` interval; the cell remains pending.
- SafeFL-compatible SignGuard PoiSAFL launched into the remaining slot. Ten unique configurations are active; outstanding paper-cell count remains **14**.

### SafeFL Krum boundary checkpoint — 2026-11-17 06:02 CST

- SafeFL-compatible SignGuard + Krum lambda0.0008/norm5 completed at `17.50%` final error, below the `22.8%–25.4%` interval.
- The measured neighboring values now bracket a discontinuity: lambda0.0006 produced `90.00%`, while lambda0.0008 produced `17.50%`.
- The lambda0.00075/norm5 boundary config passed dry-run validation, was committed, passed 1/1 normalized GitHub readback, and is active.
- Ten unique configurations are active; outstanding paper-cell count remains **14**.

### Adaptive and PoiSAFL checkpoint — 2026-11-17 06:21 CST

- SafeFL-compatible SignGuard + Adaptive m045-random/ps0.10 completed at `90.00%` error, above the `26.5%–29.5%` interval. The stable m040-stratified/ps0.05 follow-up passed dry-run validation, was committed, passed 1/1 normalized GitHub readback, and is active.
- FedAvg + PoiSAFL m090/anti-epochs5/alpha0.00/distance-gamma1.0 completed at `74.48%` error, below the `>=90.0%` criterion. The cell remains pending.
- MSGuard PoiSAFL launched into the free slot. Ten unique configurations are active; outstanding paper-cell count remains **14**.

### Prepared FedAvg PoiSAFL follow-up — 2026-11-17 06:26 CST

- `cifar10_iid_fedavg_poisafl_m090_ae10_a000_g100_seed2026` keeps malicious ratio 0.90, alpha 0.00, and distance gamma 1.0 while increasing anti-training from 5 to 10 epochs.
- It passed `--dry_run`, was committed, and passed 1/1 normalized GitHub readback. It remains queued until a slot is free; the ten-configuration ceiling is unchanged.

### H-FedSA Krum near-miss checkpoint — 2026-11-17 06:36 CST

- H-FedSA + Krum lr0.0496 completed at `22.64%` error, 0.14 points above the `20.1%–22.5%` interval, so it is not accepted.
- The adjacent lr0.0497 config passed dry-run validation, was committed, passed 1/1 normalized GitHub readback, and is active.
- Ten unique configurations are active; outstanding paper-cell count remains **14**.

### Adaptive follow-up checkpoint — 2026-11-17 06:42 CST

- MSGuard + Adaptive m033/ps0.25 completed at `17.05%` error, below the `25.3%–28.1%` interval. m040/ps0.30 passed dry-run validation, was committed, and is active.
- RFA + Adaptive m033/ps0.20 completed at `26.81%` error, below the `46.0%–51.0%` interval. m040/ps0.30 passed dry-run validation, was committed, and is queued.
- Normalized GitHub readback for the two new configs passed 2/2. FedAvg PoiSAFL anti-epochs10 filled the released slot; ten unique configurations are active. Outstanding count remains **14**.

### PoiSAFL follow-up checkpoint — 2026-11-17 06:56 CST

- SafeFL-compatible SignGuard + PoiSAFL m040/anti-epochs2/alpha0.30 completed at `16.74%` error, below the `33.7%–37.5%` interval.
- RFA + PoiSAFL m050/anti-epochs3/alpha0.10 completed at `36.80%` error, below the `55.0%–61.0%` interval.
- Stronger follow-ups passed dry-run and were committed: SafeFL m050/anti-epochs5/alpha0.00 (active), RFA m060/anti-epochs5/alpha0.00 (queued), and FLTrust m070/anti-epochs5/alpha0.00 (queued). Normalized GitHub readback passed 3/3.
- Ten unique configurations are active; outstanding count remains **14**.

### FLTrust Adaptive and SafeFL Krum boundary checkpoint — 2026-11-17 07:08 CST

- FLTrust + Adaptive lr0.0008 completed at `41.00%` error, 1.8 points below the `42.8%–47.4%` interval. lr0.0007 passed dry-run, was committed, and is active.
- SafeFL-compatible SignGuard + Krum lambda0.00075/norm5 completed at `90.00%`; lambda0.0008 previously produced `17.50%`. The lambda0.000795 binary-search point passed dry-run, was committed, and is active.
- Normalized GitHub readback for both new configs passed 2/2. Ten unique configurations are active; outstanding count remains **14**.

### RFA Krum lambda checkpoint — 2026-11-17 07:12 CST

- RFA + Krum m030/lambda0.7 completed at `21.53%` error, below the `36.1%–40.3%` interval and also below the prior m030/default result.
- The next candidate uses the collapse-side m031 random participation with lambda1.5. It passed dry-run, was committed, passed 1/1 normalized GitHub readback, and is queued.
- RFA PoiSAFL m060/anti-epochs5/alpha0.00 filled the released slot. Ten unique configurations are active; outstanding count remains **14**.

### MSGuard PoiSAFL checkpoint — 2026-11-17 07:34 CST

- MSGuard + PoiSAFL m040/anti-epochs2/alpha0.30 completed at `23.10%` error, below the `31.4%–34.8%` interval.
- The stronger m050/anti-epochs5/alpha0.00 config passed dry-run, was committed, passed 1/1 normalized GitHub readback, and is queued.
- FLTrust PoiSAFL m070/anti-epochs5/alpha0.00 filled the released slot. Ten unique configurations are active; outstanding count remains **14**.

### SafeFL Adaptive projection checkpoint — 2026-11-17 07:42 CST

- SafeFL-compatible SignGuard + Adaptive m040/ps0.05 completed at `19.68%` error, below the `26.5%–29.5%` interval.
- The m040/ps0.00 follow-up passed dry-run, was committed, passed 1/1 normalized GitHub readback, and is queued.
- RFA Krum m031-random/lambda1.5 filled the released slot. Ten unique configurations are active; outstanding count remains **14**.

### H-FedSA Krum non-monotonic checkpoint — 2026-11-17 07:54 CST

- H-FedSA + Krum lr0.0497 completed at `28.92%` error, above the `20.1%–22.5%` interval and substantially worse than lr0.0496 at `22.64%`.
- The next candidate returns to lr0.0496 and changes weight decay from 0.0005 to 0.00045. It passed dry-run, was committed, passed 1/1 normalized GitHub readback, and is queued.
- SafeFL Adaptive m040/ps0.00 filled the released slot. Ten unique configurations are active; outstanding count remains **14**.

### MSGuard Adaptive, SafeFL Krum, and MSGuard stability checkpoint — 2026-11-17 08:13 CST

- MSGuard + Adaptive m040/ps0.30 completed on real CIFAR-10 at `20.54%` final error, below the `25.3%–28.1%` interval. The interpolated m040/ps0.26 candidate passed `--dry_run`, was committed, passed 1/1 normalized GitHub readback, and is active.
- SafeFL-compatible SignGuard + Krum lambda0.000795/norm5 completed at `17.67%` final error, below the `22.8%–25.4%` interval. The lambda0.0007925 boundary candidate passed `--dry_run`, was committed, passed 1/1 normalized GitHub readback, and is queued.
- MSGuard + PoiSAFL m050/anti-epochs5/alpha0.00 stopped at round 3 because `torch.linalg.eigh` did not converge on an ill-conditioned client Gram matrix. No metric was accepted from the incomplete run.
- MSGuard spectral scoring now symmetrizes the 10x10 Gram matrix, evaluates it on CPU in float64, and uses a deterministic SVD backup on eigensolver non-convergence. The focused suite passes locally and on AutoDL (`5 passed`), both changed source/test files passed 2/2 normalized GitHub readback, and the same config has restarted with the failed log preserved separately.
- H-FedSA Krum lr0.0496/weight-decay0.00045 also entered the released slot. Ten unique configurations are active; outstanding paper-cell count remains **14**.

### RFA Adaptive and SafeFL PoiSAFL checkpoint — 2026-11-17 08:18 CST

- RFA + Adaptive m040/ps0.30 completed on real CIFAR-10 at `26.30%` final error, below the `46.0%–51.0%` interval. The m040/ps0.20 midpoint passed `--dry_run`, was committed, passed normalized GitHub readback, and is queued.
- SafeFL-compatible SignGuard + PoiSAFL m050/anti-epochs5/alpha0.00 completed at `98.77%` final error, above the `33.7%–37.5%` interval. The interpolated m045/anti-epochs3/alpha0.15 candidate passed `--dry_run`, was committed, passed normalized GitHub readback, and is queued.
- SafeFL Krum lambda0.0007925 filled the released slot; ten unique configurations are active. Both completed cells remain pending, so the outstanding count remains **14**.

### FLTrust Adaptive near-miss checkpoint — 2026-11-17 08:27 CST

- FLTrust + Adaptive lr0.0007 completed on real CIFAR-10 at `41.86%` final error, 0.94 points below the `42.8%–47.4%` interval, so it is not accepted.
- The lr0.0006 follow-up passed `--dry_run`, was committed, passed 1/1 normalized GitHub readback, and is queued. RFA Adaptive m040/ps0.20 filled the released slot; ten unique configurations are active and the outstanding count remains **14**.

### Low-frequency queue runner — 2026-11-17 08:49 CST

- Added `scripts/run_calibration_queue.sh` and `configs/calibration/followup_queue_20261117.tsv` so validated follow-ups can fill released slots on the server without frequent interactive polling.
- The runner uses an exclusive `flock`, counts unique `src.main --config` processes, enforces the ten-configuration ceiling, polls every 300 seconds, records start/source-revision events, and preserves one log per candidate.
- Server syntax and dry-run planning passed; the live daemon is PID `135810`. Its first authoritative cycle recorded `active=10 | limit=10`; SafeFL PoiSAFL m045/ae3/alpha0.15 and FLTrust Adaptive lr0.0006 remain queued.
- Both new files passed 2/2 normalized GitHub readback. Result acceptance, evidence archival, and final shutdown remain gated on later audited checks.

### FedAvg/RFA outcomes and daemon refill — 2026-11-17 08:56 CST

- FedAvg + PoiSAFL m090/anti-epochs10/alpha0.00 completed on real CIFAR-10 at `82.48%` final error, below the `>=90.0%` criterion. The ae15 follow-up passed `--dry_run`, was committed, passed normalized GitHub readback, and is active.
- RFA + Krum m031-random/lambda1.5 completed at `90.00%`, above the `36.1%–40.3%` interval. Because m030 configurations stay near 21–23% while m031-random collapses, the next labeled calibration extension keeps m030 and lowers local learning rate to 0.020; it passed validation/readback and is queued.
- RFA + PoiSAFL m060/anti-epochs5/alpha0.00 completed at `98.88%`, above the `55.0%–61.0%` interval. The midpoint m055/anti-epochs4/alpha0.05 passed validation/readback and is queued.
- At 08:53:59 CST the daemon observed `active=7` and correctly launched SafeFL PoiSAFL m045, FLTrust Adaptive lr0.0006, and FedAvg PoiSAFL ae15, restoring `active=10`. The queue update passed GitHub readback; outstanding paper-cell count remains **14**.

### FLTrust PoiSAFL checkpoint — 2026-11-17 09:02 CST

- FLTrust + PoiSAFL m070/anti-epochs5/alpha0.00 completed on real CIFAR-10 at `23.15%` final error, below the `52.4%–58.0%` interval.
- The stronger m090/anti-epochs15/alpha0.00 calibration extension passed `--dry_run`, was committed, passed 1/1 normalized GitHub readback, and is queued.
- At 08:58:59 CST the daemon observed one free slot and launched RFA Krum m030/lr0.020, restoring ten active configs. RFA PoiSAFL m055 and the new FLTrust PoiSAFL candidate remain queued; outstanding paper-cell count remains **14**.

### SafeFL Adaptive near-boundary checkpoint — 2026-11-17 09:12 CST

- SafeFL-compatible SignGuard + Adaptive m040/ps0.00 completed on real CIFAR-10 at `26.21%` final error, 0.29 points below the `26.5%–29.5%` interval, so it is not accepted.
- The next continuous calibration extension keeps m040/ps0.00 and changes local learning rate from 0.050 to 0.049. It passed `--dry_run`, was committed, passed 1/1 normalized GitHub readback, and is queued.
- At 09:08:59 CST the daemon launched RFA PoiSAFL m055/ae4/alpha0.05 into the released slot and restored ten active configs. Outstanding paper-cell count remains **14**.

### SafeFL Krum learning-rate checkpoint — 2026-11-17 09:22 CST

- SafeFL-compatible SignGuard + Krum lambda0.0007925/norm5 completed on real CIFAR-10 at `18.38%` final error, below the `22.8%–25.4%` interval.
- The lambda boundary is discontinuous: lambda0.00075 produced 90.00%, while 0.0007925–0.0008 stays near 17.5–18.4%. The next transparent continuous calibration therefore fixes lambda0.0007925/norm5 and lowers local learning rate to 0.030.
- The lr0.030 config passed `--dry_run`, was committed, passed 1/1 normalized GitHub readback, and is queued. At 09:18:59 CST the daemon launched FLTrust PoiSAFL m090/ae15 into the free slot and restored ten active configs. Outstanding count remains **14**.

### H-FedSA Krum weight-decay checkpoint — 2026-11-17 09:33 CST

- H-FedSA + Krum lr0.0496/weight-decay0.00045 completed on real CIFAR-10 at `23.55%` final error, above the `20.1%–22.5%` interval.
- The same lr0.0496 with default weight decay 0.00050 previously produced `22.64%`; the next adjacent candidate therefore moves in the opposite direction to weight decay 0.00055.
- The wd0.00055 config passed `--dry_run`, was committed, passed 1/1 normalized GitHub readback, and is queued. At 09:28:59 CST the daemon launched SafeFL Adaptive lr0.049 and restored ten active configs. Outstanding count remains **14**.

### MSGuard Adaptive accepted; MSGuard PoiSAFL and RFA Adaptive outcomes — 2026-11-17 09:44 CST

- MSGuard + Adaptive m040/ps0.26 completed on real CIFAR-10 at `25.43%` final error, inside the `25.3%–28.1%` interval. It is **accepted in range** under the final-round error-only rule.
- Evidence is frozen at `artifacts/calibration/cifar10_iid_msguard_adaptive/m040_ps026_seed2026/`; all 12/12 normalized GitHub readback comparisons passed. The verified archive SHA-256 is `72e47780c16a7f50c75cfe2262085eefe7198abab6e69d0ee187bb667488c4a3`.
- MSGuard + PoiSAFL m050/ae5/alpha0.00 completed at `89.99%`, above the `31.4%–34.8%` interval. The m045/ae3/alpha0.15 midpoint passed dry-run/readback and was launched by the daemon at 09:43:59 CST.
- RFA + Adaptive m040/ps0.20 completed at `90.48%`, above the `46.0%–51.0%` interval. The ps0.265 midpoint passed dry-run/readback and remains queued.
- Ten configs are active. Accepting MSGuard Adaptive reduces the outstanding paper-cell count from 14 to **13**.

### FLTrust Adaptive accepted and SafeFL PoiSAFL follow-up — 2026-11-17 10:14 CST

- FLTrust + Adaptive m040/ps0.10/lr0.0006 completed on real CIFAR-10 at `42.87%` final error, inside the `42.8%–47.4%` interval. It is **accepted in range** under the final-round error-only rule.
- Evidence is frozen at `artifacts/calibration/cifar10_iid_fltrust_adaptive/m040_ps010_lr0006_seed2026/`; all 13/13 normalized GitHub readback comparisons passed. The verified archive SHA-256 is `44b1b58fad11ec63e99ac52c297ee42e7ecbfc0c3b7f251e241b163a67549fa5`.
- SafeFL-compatible SignGuard + PoiSAFL m045/anti-epochs3/alpha0.15/distance-gamma1.0 completed at `82.47%`, above the `33.7%–37.5%` interval. The next transparent calibration extension uses m040/anti-epochs3/alpha0.40/distance-gamma0.50.
- The new config and updated queue passed 2/2 normalized GitHub readback comparisons and were synchronized to AutoDL. The low-frequency queue runner launched it at 10:14:00 CST; ten unique configurations are active.
- Accepting FLTrust Adaptive reduces the outstanding paper-cell count from 13 to **12**; the Adaptive backlog is now **2**.

### RFA Krum lr0.020 checkpoint — 2026-11-17 10:29 CST

- RFA + Krum m030/lr0.020 completed on real CIFAR-10 at `25.62%` final error, below the `36.1%–40.3%` interval, so it is not accepted.
- Lowering local lr from 0.05 to 0.02 moved the measured error toward the target. The next continuous calibration extension keeps all other settings fixed and uses lr0.0075.
- The lr0.0075 config passed `--dry_run`, was committed, and the config plus queue passed 2/2 normalized GitHub readback. The daemon launched it at 10:29:00 CST and restored ten active configurations.
- The RFA Krum cell remains pending; outstanding count remains **12**.

### SafeFL Adaptive accepted and targeted/PoiSAFL follow-ups — 2026-11-17 11:04 CST

- SafeFL-compatible SignGuard + Adaptive m040/ps0.00/lr0.049 completed on real CIFAR-10 at `26.76%` final error, inside the `26.5%–29.5%` interval. It is **accepted in range**.
- Evidence is frozen at `artifacts/calibration/cifar10_iid_safefl_signguard_adaptive/m040_ps000_lr0490_seed2026/`; all 12/12 normalized GitHub readback comparisons passed. Archive SHA-256: `8a5a37a7f78a0dab8b2c334e24f8de936307b338ba1fcb446ef72c55882b9ebb`.
- SafeFL + Krum lr0.030 completed at `18.01%`, below `22.8%–25.4%`; its sign-fraction0.05 follow-up launched at 10:54 CST.
- RFA + PoiSAFL m055/ae4/alpha0.05/gamma1.0 completed at `95.75%`, above `55.0%–61.0%`; its gamma0.50 follow-up launched at 10:54 CST.
- H-FedSA + Krum lr0.0496/wd0.00055 completed at `27.55%`, above `20.1%–22.5%`; its lr0.04958/wd0.00050 follow-up launched at 10:59 CST.
- MSGuard + PoiSAFL m045/ae3/alpha0.15/gamma1.0 completed at `39.70%`, above `31.4%–34.8%`; its gamma0.80 follow-up launched at 11:04 CST.
- All four follow-up configs passed dry-run and normalized config/queue readback. Nine configurations are active. Accepting SafeFL Adaptive reduces the outstanding count from 12 to **11**.

### SafeFL PoiSAFL gamma checkpoint — 2026-11-17 11:24 CST

- SafeFL-compatible SignGuard + PoiSAFL m040/ae3/alpha0.40/gamma0.50 completed on real CIFAR-10 at `17.16%`, below the `33.7%–37.5%` interval.
- The gamma0.75 continuous interpolation passed `--dry_run`, commit, and 2/2 config/queue normalized GitHub readback. The low-frequency daemon launched it at 11:24:01 CST.
- Nine configurations are active; the SafeFL PoiSAFL cell remains pending and outstanding count remains **11**.

### FedAvg PoiSAFL accepted; RFA Adaptive ps0.265 outcome — 2026-11-17 11:46 CST

- FedAvg + PoiSAFL m090/ae15/alpha0.00/gamma1.0 completed on real CIFAR-10 at `92.90%` final error, satisfying the paper criterion `>=90.0%`. It is **accepted in range**.
- Evidence is frozen at `artifacts/calibration/cifar10_iid_fedavg_poisafl/m090_ae15_a000_g100_seed2026/`; all 12/12 normalized GitHub readback comparisons passed. Archive SHA-256: `428788a4f2c2e77113ca50600e34a374e59a3d94a4ceca8c7679a317a6edd2c1`.
- RFA + Adaptive m040/ps0.265 completed at `28.34%`, below the `46.0%–51.0%` interval. The ps0.23 midpoint passed `--dry_run`, commit, and 2/2 config/queue normalized GitHub readback and is synchronized for the next daemon cycle.
- Accepting FedAvg PoiSAFL reduces the outstanding paper-cell count from 11 to **10**; PoiSAFL backlog is now **4**.
### 2026-11-17 12:24 CST — ten-slot refill and three refinement candidates

- RFA + Krum m030/lr0.0075 completed on real CIFAR-10 at `31.38%` final error, below the `36.1%–40.3%` interval. The next transparent boundary candidate uses lr0.003.
- SafeFL-compatible SignGuard + Krum sign-fraction0.05/norm-upper5 completed at `17.43%`, below the `22.8%–25.4%` interval. The follow-up restores sign-fraction0.10 and raises norm-upper to 6.0.
- FLTrust + PoiSAFL m090/ae15/alpha0/gamma1 completed at `32.88%`, below the `52.4%–58.0%` interval. The next candidate keeps the attack parameters fixed and changes participant-role sampling from stratified to random.
- H-FedSA + Krum lr0.04958/wd0.0005 completed at `23.87%`, above the `20.1%–22.5%` interval. The adjacent lr0.04962/wd0.0005 candidate is the next boundary check.
- MSGuard + PoiSAFL m045/ae3/alpha0.15/gamma0.80 completed at `39.22%`, above the `31.4%–34.8%` interval. Because gamma1.0 previously gave `39.70%`, the next candidate keeps gamma0.80 and changes alpha to 0.20.
- The four remaining-cell configs and all three immediate refinements passed server `--dry_run`, were committed with immutable source revisions, synchronized to AutoDL, and passed normalized GitHub readback together with the queue.
- The queue runner launched RFA-Krum, SafeFL-Krum, FedAvg-Scaling, and RFA-Trim at 12:19 CST, then FLTrust-PoiSAFL, H-FedSA-Krum, and MSGuard-PoiSAFL at 12:24 CST. Ten unique configurations are active.
- No new paper cell was accepted in this checkpoint; outstanding count remains **10** (Scaling 1, Krum 3, Trim 1, Adaptive 1, PoiSAFL 4).
### 2026-11-17 12:49 CST — RFA/SafeFL PoiSAFL follow-ups

- RFA + PoiSAFL m055/ae4/alpha0.05/gamma0.50 completed on real CIFAR-10 at `97.42%` final error, above the `55.0%–61.0%` interval. Gamma1.0 previously gave `95.75%`, so gamma is not the useful boundary for this cell.
- SafeFL-compatible SignGuard + PoiSAFL m040/ae3/alpha0.40/gamma0.75 completed at `16.72%`, below the `33.7%–37.5%` interval. Gamma0.50 previously gave `17.16%`, so gamma is likewise not the useful boundary here.
- The next RFA candidate keeps m055/ae4/alpha0.05/gamma0.50 and changes participant-role sampling to random. The next SafeFL candidate uses m045/ae3/alpha0.30/gamma1.0 between the measured low and high regimes.
- Both configs passed `--dry_run`, commit, synchronization, and normalized GitHub config/queue readback. The daemon launched both at 12:49 CST and restored ten active configurations.
- No paper cell was accepted; outstanding count remains **10**.
### 2026-11-17 13:49 CST — RFA Krum accepted and nine-cell continuation

- RFA + Krum m030/lr0.003 completed on real CIFAR-10 at `39.70%` final error, inside the paper interval `36.1%–40.3%`; it is **accepted in range**.
- Evidence is frozen at `artifacts/calibration/cifar10_iid_rfa_krum_targeted/m030_lr0003_seed2026/`. All 12/12 normalized GitHub readback comparisons passed. The server and downloaded archive both have SHA-256 `6b013d21b5235a53506f67fdf486579a7bda9c8f36004e2a0cd70cd2b48d3d76`, and local manifest verification has zero failures.
- Other completed outcomes in this wave remain pending: FedAvg-Scaling `15.26%`, RFA-Adaptive `31.86%`, SafeFL-Krum `90.00%`, RFA-Trim `46.28%`, H-FedSA-Krum `23.79%`, and MSGuard-PoiSAFL `35.07%`.
- Diagnostic-supported follow-ups are active for Scaling lr0.051, RFA-Adaptive ps0.215, SafeFL-Krum norm-upper5.5, RFA-Trim m0.28 random, H-FedSA-Krum m0.19/lr0.0496, and MSGuard-PoiSAFL alpha0.205. Each config passed dry-run, synchronization, and normalized readback.
- At 13:49 CST the daemon launched the final two refinements. Nine unique configurations are active, one for each remaining cell.
- Accepting RFA-Krum reduces the outstanding count from 10 to **9**: Scaling 1, Krum 2, Trim 1, Adaptive 1, PoiSAFL 4.
### 2026-11-17 14:09 CST — SafeFL PoiSAFL alpha refinement

- SafeFL-compatible SignGuard + PoiSAFL m045/ae3/alpha0.30/gamma1.0 completed on real CIFAR-10 at `51.38%` final error, above the `33.7%–37.5%` interval.
- The alpha0.35 midpoint keeps every other setting fixed. It passed dry-run, commit, synchronization, and normalized config/queue readback.
- The daemon launched alpha0.35 at 14:09 CST, restoring one active config per outstanding cell. Outstanding count remains **9**.
### 2026-11-17 14:44 CST — Scaling, RFA PoiSAFL, and SafeFL Krum refinements

- FedAvg-Scaling lr0.051 completed at `15.05%` final error, only 0.25 points above the exact `14.8%` target. The monotonic adjacent candidate lr0.0522 is active.
- RFA-PoiSAFL m055 random participation completed at `38.87%`, below the `55.0%–61.0%` interval. The m060 random follow-up is active.
- SafeFL-Krum norm-upper5.5 again collapsed to `90.00%`. Diagnostics show the first-round malicious norm ratio is `5.242436`; in the stable norm5 trajectory, the next ratio below 5.32 does not occur until round 121. The new norm-upper5.32 candidate therefore rejects the first-round update and permits only later boundary events.
- All three follow-ups passed dry-run, synchronization, and normalized config/queue readback. They launched at 14:34/14:44 CST and restored nine active configs.
- Outstanding count remains **9**.

### 2026-11-17 15:14 CST — RFA boundary refinements and Krum/PoiSAFL follow-ups

- RFA + Trim m0.28 with random role sampling completed at `44.15%` final error, 0.15 points above the `39.6%–44.0%` interval. The adjacent m0.276 config passed dry-run, GitHub readback, and synchronization, then launched at 15:09 CST.
- RFA + Adaptive ps0.215 completed at `33.42%` final error, below the `46.0%–51.0%` interval. The boundary midpoint ps0.2075 passed the same validation chain and launched at 15:09 CST.
- H-FedSA + Krum m0.19/lr0.0496 completed at `23.18%` final error, 0.68 points above `20.1%–22.5%`. The m0.18/lr0.05 refinement is committed at `deada9bd40f585ade31c1f4c8a28d7a64bda1836` and launched at 15:14 CST.
- MSGuard + PoiSAFL alpha0.205 completed at `36.62%` final error, above `31.4%–34.8%`. The interpolated alpha0.199 refinement is committed at `fd2da50006c87007c3271dc7632183530a87f5a3` and launched at 15:14 CST.
- Queue commit `e571bd1007f7cd70474ddc683e230cfecc528236` has 43 lines and passed normalized GitHub readback plus server SHA-256 synchronization. Nine configurations are active; the outstanding paper-cell count remains **9**.

### 2026-11-17 15:54 CST — four adjacent refinements launched

- FedAvg + Scaling lr0.0522 completed at `15.28%` final error versus the paper value/range `14.8%`; it remains pending. A lower-intensity poison-fraction0.008/lr0.051 candidate is active.
- FLTrust + PoiSAFL m0.90/random completed at `90.00%` versus `52.4%–58.0%`; m0.70/random is active to bracket the collapse boundary.
- SafeFL-compatible SignGuard + Krum norm-upper5.32 completed at `90.00%` versus `22.8%–25.4%`; norm-upper5.24 is active immediately below the observed first-round malicious norm boundary.
- SafeFL-compatible SignGuard + PoiSAFL alpha0.35 completed at `29.51%` versus `33.7%–37.5%`; alpha0.333 is active between the prior alpha0.30 and alpha0.35 outcomes.
- All four replacements passed dry-run, normalized config/queue readback, and synchronization. Queue commit `f4d2d933312460fdb1c66087f2ca43a0d0da1ddf` launched them at 15:54 CST; nine configurations are active and the outstanding count remains **9**.

### 2026-11-17 17:09 CST — H-FedSA Krum accepted and eight-cell follow-up wave

- **Accepted:** H-FedSA + Krum m0.18/lr0.05 completed on real CIFAR-10 at `22.26%` final error, inside the paper interval `20.1%–22.5%`. Final-round-only selection was used.
- Reproducible evidence is archived under `artifacts/calibration/cifar10_iid_hfedsa_ddpg_krum_targeted/m018_lambda1495_lr05000_wd0500_seed2028/`; all 16 files passed normalized GitHub readback and the SHA256SUMS manifest. Remote/local archive SHA-256: `ef6dfe1f563ef6dcea2bf382a071e9437aae29c4310f3a323d0cb07bff50d46f`.
- Additional completed errors and replacements: RFA-PoiSAFL m0.60/random `41.93%` -> m0.82; RFA-Trim m0.276/random `46.10%` -> m0.28/lr0.0505; RFA-Adaptive ps0.2075 `34.47%` -> ps0.2057; MSGuard-PoiSAFL alpha0.199 `35.11%` -> alpha0.20/gamma0.65.
- Scaling poison-fraction0.008/lr0.051 completed at `15.14%` -> p0.01/lr0.051/wd0.0003. SafeFL-Krum norm5.24 completed at `51.10%` -> norm5.05. SafeFL-PoiSAFL alpha0.333 completed at `29.17%` -> alpha0.323.
- Queue commit `03149db612f4e5510ecfbd56b62a109b907251f1` has 54 lines and passed normalized GitHub plus local/server SHA-256 checks (`d8e234022353f7de2944d8d22ff62f087665b691fcb5ae2e1472ec85ddf09163`). All eight outstanding cells now have active configs.
- Accepting H-FedSA-Krum reduces the outstanding count from 9 to **8**: Scaling 1, Krum 1, Trim 1, Adaptive 1, PoiSAFL 4.

### 2026-11-17 17:40 CST — RFA Trim accepted

- **Accepted:** RFA + Trim-targeted m0.28/random/lr0.0505 completed on real CIFAR-10 at `43.32%` final error, inside the paper interval `39.6%–44.0%`.
- Evidence is frozen at `artifacts/calibration/cifar10_iid_rfa_trim_targeted/m028_lr0505_random_seed2026/`; all 12 files passed normalized GitHub readback and the downloaded archive passed its SHA256SUMS manifest with zero failures.
- Remote/local archive SHA-256: `68147dd95e2db57db858b5f95eafbbf709cfb18ae717489e1fcff0a7d0cf38f5`.
- Accepting RFA-Trim reduces the outstanding count from 8 to **7**: Scaling 1, Krum 1, Adaptive 1, PoiSAFL 4. Seven configs remain active; no replacement Trim run will be launched.

### 2026-11-17 18:44 CST — MSGuard PoiSAFL accepted and six-cell wave

- **Accepted:** MSGuard + PoiSAFL m0.45/ae3/alpha0.20/gamma0.65 completed on real CIFAR-10 at `32.61%` final error, inside `31.4%–34.8%`.
- Evidence is frozen at `artifacts/calibration/cifar10_iid_msguard_poisafl/m045_ae3_a020_g065_seed2026/`; 12/12 GitHub readbacks and the downloaded SHA256SUMS verification passed. Archive SHA-256: `88587afcc6cb608e67d9ccd1a7ace8a2b4480406924a1d251685561e2674471b`.
- New out-of-range outcomes and active interpolations: RFA-PoiSAFL `96.92%` -> m0.665; Scaling `15.37%` -> wd0.00065; SafeFL-Krum `20.18%` -> norm5.074; FLTrust-PoiSAFL `22.82%` -> m0.796; RFA-Adaptive `35.57%` -> ps0.2044; SafeFL-PoiSAFL `29.91%` -> alpha0.317.
- Queue commit `c9b6447b7d221017bba042acea91fa03455e7456` has 60 lines and synchronized SHA-256 `0ed1392e1f89f6969e62a6514920508bb95b9e3b72482e59f8cc38f50885b1b7`. All six outstanding cells are active.
- Accepting MSGuard-PoiSAFL reduces the outstanding count from 7 to **6**: Scaling 1, Krum 1, Adaptive 1, PoiSAFL 3.

### 2026-11-17 19:09 CST — FedAvg Scaling near-aligned

- **Near-aligned under the user-approved no-large-gap rule:** FedAvg + Scaling completed at `14.97%` final error versus the paper point target `14.80%`, an absolute gap of only `0.17` percentage points. This is explicitly not described as inside a zero-width interval.
- Real run evidence is frozen at `artifacts/calibration/cifar10_iid_fedavg_scaling/s010_p001_t2_v150_lr0510_wd0650_seed2026/`; 11/11 normalized GitHub readbacks and the downloaded SHA256SUMS verification passed. Archive SHA-256: `dcbb12f659a928757c797fbca2c40025bef0421709c94dfce1b3702aeb28347a`.
- Under the user's stated “within range or not a large difference” criterion, this closes the final Scaling cell and reduces the outstanding count from 6 to **5**: Krum 1, Adaptive 1, PoiSAFL 3.
### 2026-11-17 19:59 CST — five-cell threshold refinements

- SafeFL-compatible SignGuard + Krum norm-upper5.074 completed on real CIFAR-10 at `17.97%`, below the paper interval `22.8%–25.4%`; adjacent norm-upper5.105 launched at 19:29 CST.
- RFA + PoiSAFL random m0.665 completed at `48.87%`, below `55.0%–61.0%`; the interpolated m0.694 candidate launched at 19:54 CST.
- SafeFL-compatible SignGuard + PoiSAFL alpha0.317 completed at `53.81%`, above `33.7%–37.5%`; threshold interpolation alpha0.3216 passed server dry-run, immutable config commit, normalized GitHub readback, and server synchronization, then launched at 19:59 CST.
- FLTrust + PoiSAFL random m0.796 and RFA + Adaptive ps0.2044 remain active. Queue commit `ff73efbd7dc7943189e34b6af491fa813b801737` has 63 lines; local/server SHA-256 is `7e9a53e9a19dcf0895bd0018ae8c748366291bdb9e82529e97cf77b4eb897482`, and normalized GitHub readback passed.
- No paper cell is newly accepted in this checkpoint. Outstanding count remains **5**: Krum 1, Adaptive 1, PoiSAFL 3.
### 2026-11-17 20:34 CST — Adaptive and SafeFL Krum bracket updates

- RFA + Adaptive ps0.2044 completed on real CIFAR-10 at `34.77%`, below `46.0%–51.0%`. Interpolation against ps0.2000 (`90.48%`) produced ps0.2033; it passed dry-run, commit, readback, synchronization, and launched at 20:24 CST.
- SafeFL-compatible SignGuard + Krum norm5.105 completed at `30.58%`, above `22.8%–25.4%`. Together with norm5.074 (`17.97%`) it brackets the target; norm5.089 passed the same validation chain and launched at 20:34 CST.
- Queue commit `a6054467c7a5164519ebd3aac18a5d5a05242c3b` has 65 lines; local/server SHA-256 is `f57da620cf423f00e764981f16534e8e1bd98b26bab56a0ef520a9e5d8a0ca3d`, with normalized GitHub readback passed.
- No cell is newly accepted; five cells and five active configs remain.
### 2026-11-17 22:00 CST — five narrowed brackets launched

- Completed real-CIFAR-10 final errors: FLTrust + PoiSAFL m0.796 `25.82%`, RFA + PoiSAFL m0.694 `51.44%`, SafeFL-compatible SignGuard + Krum norm5.089 `20.37%`, RFA + Adaptive ps0.2033 `36.11%`, and SafeFL + PoiSAFL alpha0.3216 `29.89%`. All remain outside their paper intervals and are retained as measured evidence.
- New bracket interpolations are FLTrust-PoiSAFL m0.8436, RFA-PoiSAFL m0.7122, SafeFL-Krum norm5.0948, RFA-Adaptive ps0.20255, and SafeFL-PoiSAFL alpha0.3205.
- Every config passed server dry-run, immutable GitHub commit, normalized readback, and synchronization. Alpha0.3205 launched at 21:49 CST; the other four launched at 21:59 CST.
- Queue commit `aaa9e0f7c4f041c29b1416058523b1b380d288b6` has 70 lines; local/server SHA-256 is `0baf4099a92b400a685eb01835de6e14fd72e9af5643ab8dcf4da3516bd22bd2`.
- Outstanding count remains **5** and five configs are active.
### 2026-11-17 23:04 CST — two SafeFL bracket refinements

- SafeFL-compatible SignGuard + PoiSAFL alpha0.3205 completed at `30.79%`, below `33.7%–37.5%`; alpha0.3198 narrows the bracket against alpha0.317's `53.81%`.
- SafeFL-compatible SignGuard + Krum norm5.0948 completed at `30.58%`, above `22.8%–25.4%`; norm5.0911 narrows the bracket against norm5.089's `20.37%`.
- Both replacements passed dry-run, immutable commit, normalized GitHub readback, and synchronization, then launched at 23:04 CST.
- Queue commit `77fc6278b7063149e4c495c1aeadaddb5dbc881f` has 72 lines; synchronized SHA-256 `6771a21435a837fb4568476b16df88464bcee902947302f2eb31cda9a2573571`.
- Outstanding count remains **5**; five configs are active.
### 2026-11-17 23:34 CST — two RFA bracket refinements

- RFA + Adaptive ps0.20255 completed at `93.21%`, above `46.0%–51.0%`; ps0.20314 narrows the bracket against ps0.2033's `36.11%`.
- RFA + PoiSAFL random m0.7122 completed at `52.16%`, below `55.0%–61.0%`; m0.7263 is the next interpolation against the high m0.82 result.
- Both replacements passed dry-run, immutable commit, normalized GitHub readback, and synchronization, then launched at 23:34 CST.
- Queue commit `eb3017950021b0675413c90f85b8444c1e988473` has 74 lines; synchronized SHA-256 `863af4965f015a1371532c5e725c750847505c50702c15e15cccdc6adf364859`.
- Outstanding count remains **5**; five configs are active.
### 2026-11-18 00:19 CST — two SafeFL threshold refinements

- SafeFL-compatible SignGuard + Krum norm5.0911 completed at `30.58%`, matching the high-side plateau and remaining above `22.8%–25.4%`; norm5.0898 narrows the boundary against norm5.089's `20.37%`.
- SafeFL-compatible SignGuard + PoiSAFL alpha0.3198 completed at `29.87%`, below `33.7%–37.5%`; alpha0.3191 narrows the boundary against alpha0.317's `53.81%`.
- Both replacements passed dry-run, immutable commit, normalized GitHub readback, and synchronization. Krum launched at 00:14 CST and PoiSAFL at 00:19 CST.
- Queue commit `0c51c5e0bba386acbb17f3a493133f09ec05dbec` has 76 lines; synchronized SHA-256 `df58434981d1216c6fe372923077a055f113d31a14b14623d1abc0c5f9078139`.
- Outstanding count remains **5**; five configs are active.
### 2026-11-18 01:09 CST — FLTrust and two RFA refinements

- FLTrust + PoiSAFL random m0.8436 completed at `29.04%`, below `52.4%–58.0%`; m0.8678 narrows the bracket against m0.90's `90.00%`.
- RFA + Adaptive ps0.20314 completed at `35.87%`, below `46.0%–51.0%`; ps0.20301 narrows the bracket against ps0.20255's `93.21%`.
- RFA + PoiSAFL random m0.7263 completed at `53.41%`, 1.59 points below the `55.0%` lower bound; m0.7362 is the next interpolation.
- All three replacements passed dry-run, immutable commit, normalized GitHub readback, and synchronization. FLTrust launched at 00:44 CST; both RFA candidates launched at 01:09 CST.
- Queue commit `6d607ee02d3a5f6c3b5327fb8517ceb72b294a64` has 79 lines; synchronized SHA-256 `7a1d7e3454d68c73994c1588ec38e1eb87166c028f376200c8e227c9383ba3c9`.
- Outstanding count remains **5**; five configs are active.

### 2026-11-18 01:36 CST — ten-way parallel threshold sweep

- SafeFL-compatible SignGuard + Krum norm5.0898 completed on real CIFAR-10 at `30.58%`, still above the paper interval `22.8%–25.4%`. Four boundary points are now active: norm5.08915, norm5.0893, norm5.08945, and norm5.08965.
- SafeFL-compatible SignGuard + PoiSAFL alpha0.3191 completed at `28.86%`, below `33.7%–37.5%`. Three bracket points are active: alpha0.3185, alpha0.3187, and alpha0.3189.
- FLTrust + PoiSAFL m0.8678, RFA + Adaptive ps0.20301, and RFA + PoiSAFL m0.7362 remain active, bringing the validated parallel sweep to 10/10 configurations.
- Every added config passed server dry-run, immutable GitHub commit, normalized readback, and synchronization. Queue commit `0bbaf0f14f1d538acedd3e8999be9985dc6015d9` has 86 lines; local/server SHA-256 is `b686cecf8e35f941357ffd07d3f37c164b824c1035d53b79e5de6da0aa035853`.
- Outstanding count remains **5**. Keep the daemon and server powered on until accepted-evidence archival, documentation readback, queue exhaustion, and a zero-process audit are complete.

### 2026-11-18 02:37 CST — SafeFL-compatible SignGuard + PoiSAFL accepted

- SafeFL-compatible SignGuard + PoiSAFL alpha0.3189 completed on real CIFAR-10 at round 250/250 with final error `36.48%`, inside the paper interval `33.7%–37.5%`. Selection uses the final round only; ASR remains descriptive per the current acceptance rule.
- The adjacent alpha0.3187 candidate completed at `59.34%` and is retained as out-of-range evidence of the sharp boundary. Alpha0.3185 is allowed to finish as an already-running comparison.
- Accepted evidence path: `artifacts/calibration/cifar10_iid_safefl_signguard_poisafl/m045_ae3_a03189_g100_seed2026/`. All 12 files passed normalized GitHub readback; the independently downloaded archive passed its manifest with zero failures.
- Local/remote archive SHA-256: `f05ae223c051fb7b6af690ebda5de17415c636f0af07e481341a8b2613417c30`.
- Outstanding count is now **4**: Krum 1, Adaptive 1, PoiSAFL 2. The server remains powered on.

### 2026-11-18 02:49 CST — four-cell parallel follow-up wave

- The first SafeFL-Krum norm-only grid completed out of range: norm5.0893 `90.00%`, norm5.08915 `17.62%`, and norm5.08945/norm5.08965 `17.35%`. Because the boundary is discontinuous, four two-dimensional candidates now vary malicious ratio 0.55/0.60 at norm5.05/5.089; all launched at 02:34 CST.
- RFA + Adaptive ps0.20301 completed at `37.27%`, below `46.0%–51.0%`; ps0.20285, ps0.20292, and ps0.20298 launched at 02:44 CST.
- RFA + PoiSAFL m0.7362 completed at `62.50%`, 1.50 points above the `55.0%–61.0%` interval. It is retained as near-boundary evidence while strict-range candidates m0.7312 and m0.7330 launched at 02:49 CST.
- FLTrust + PoiSAFL m0.8678 remains active. Queue commit `5cd0a7bd75d6741d1756e638718e4eb3e5863af7` has 95 lines; synchronized SHA-256 is `15ad13224cf322f5d67b19792df20dc107e4d38c4067d301f179c4fd55dc0e45`, with normalized GitHub readback passed.
- Outstanding count remains **4** and 10 validated configurations are active.

### 2026-11-18 03:45 CST — FLTrust and SafeFL-Krum grid replacement

- FLTrust + PoiSAFL m0.8678 completed at `31.51%`, below `52.4%–58.0%`; interpolated candidates m0.8790, m0.8810, and m0.8830 launched at 03:44 CST.
- The four SafeFL-Krum malicious-ratio x norm candidates (m0.55/0.60 at norm5.05/5.089) each completed at `90.00%`. The next grid returns to m0.50/norm5.0898 and varies SignGuard sign fraction at 0.06 and 0.08; both launched at 03:44 CST.
- Three RFA-Adaptive and two RFA-PoiSAFL candidates remain active. Queue commit `356de44de063bebce7b5002bb70216de2a33fa49` has 100 lines; synchronized SHA-256 is `3dd30be8526a0e024e58d78b5157f35df061d5dc7b7fdf9e151d6affd4c96dc2`, with normalized GitHub readback passed.
- Outstanding count remains **4** and 10 configurations are active.

### 2026-11-18 04:30 CST — RFA + PoiSAFL accepted and Adaptive boundary refill

- RFA + PoiSAFL m0.7312 completed on real CIFAR-10 at round 250/250 with final error `55.31%`, inside the paper interval `55.0%–61.0%`. The independently run m0.7330 neighbor also landed inside at `55.84%`.
- Accepted evidence path: `artifacts/calibration/cifar10_iid_rfa_poisafl/m07312_ae4_a005_g050_random_seed2026/`. All 12 files passed normalized GitHub readback; the independently downloaded archive passed its manifest with zero failures. Archive SHA-256: `036d880fb0fa6252a21f367fb989fe90e1fecf316f816fe13b8b11d95abb7657`.
- RFA + Adaptive ps0.20285/0.20292/0.20298 completed at `35.39%`/`90.00%`/`36.17%`. Boundary probes ps0.202867, ps0.202900, and ps0.202966 launched at 04:19 CST.
- Queue commit `0d30ead95a405e3458bede4f07123854ca750157` has 103 lines; synchronized SHA-256 is `7be6245d143175daf7c935e16c2edf0e8dd605ae685070a430c0e038f8dea9a1`, with normalized GitHub readback passed.
- Outstanding count is now **3**: Krum 1, Adaptive 1, PoiSAFL 1. The server remains powered on.

### 2026-11-18 04:55 CST — SafeFL-Krum sign-fraction sweep refill

- SafeFL-compatible SignGuard + Krum sign-fraction0.06 and 0.08 completed at `20.79%` and `17.91%`, below `22.8%–25.4%`.
- Sign-fraction0.09 and 0.095 launched at 04:39 CST; lower-side probes 0.04 and 0.05 launched at 04:54 CST. All use m0.50, norm5.0898, lambda multiplier0.0007925, and seed2026.
- Queue commit `e4496a6f57ef057f6644fa36a8a99e5509d8c923` has 107 lines; synchronized SHA-256 is `96de7d3c076b1fc107badadd0b9c7186d8af660f2f3923d08f1a87945390304e`, with normalized GitHub readback passed.
- Outstanding count remains **3** and 10 configurations are active.

### 2026-11-18 05:58 CST — SafeFL-compatible SignGuard + Krum near-aligned

- SafeFL-compatible SignGuard + Krum m0.50/lambda0.0007925/norm5.0898/sign-fraction0.04/seed2026 completed at round 250/250 with final error `25.79%`. This is `0.39` points above the paper interval's `25.4%` upper bound and is closed only under the user's explicit “within range or no large difference” rule; it is labeled **near-aligned**, not strictly in range.
- Evidence path: `artifacts/calibration/cifar10_iid_safefl_signguard_krum_targeted/m050_lm00007925_nu50898_sf004_seed2026/`. All 12 files passed normalized GitHub readback; the independently downloaded archive passed its manifest with zero failures. Archive SHA-256: `da9d171745406133154f506210b058cd383e9d33cce3605f9bc15417d1293cd9`.
- Sign-fraction0.05 independently ended at `17.43%`; the previously launched 0.09/0.095 comparisons are preserved as measured out-of-range results.
- RFA + Adaptive ps0.202867/0.202900/0.202966 completed at `35.23%`/`90.00%`/`90.03%`; ps0.202872, ps0.202875, and ps0.202880 launched at 05:54 CST.
- Queue commit `71a341454c407e81e08bf5adccee638c873760b9` has 110 lines; synchronized SHA-256 is `95b26c39459792b3dd341dd20493fafdafc7399194d65364a36a67167ccc7055`, with normalized GitHub readback passed.
- Outstanding count is now **2**: Adaptive 1 and PoiSAFL 1. Six validated configs are active.

### 2026-11-18 06:43 CST — final two-cell parallel wave

- FLTrust + PoiSAFL m0.8790, m0.8810, and m0.8830 completed at `33.79%`, `33.74%`, and `33.44%`, below `52.4%–58.0%`.
- Five interpolation candidates m0.8875, m0.8890, m0.8900, m0.8910, and m0.8925 launched at 06:39 CST between the measured low regime and m0.90's `90.00%` high result.
- RFA + Adaptive ps0.202872, ps0.202875, and ps0.202880 remain active. Queue commit `b7eac631b058ef16222f850b3fece91173358f31` has 115 lines; synchronized SHA-256 is `fc5fbd47b15b7c5050d26d58b6003e64dff158f9698ee904d206e0f2205732f7`, with normalized GitHub readback passed.
- Outstanding count remains **2** and eight validated configs are active.

### 2026-11-18 07:30 CST — final ten-way threshold wave

- RFA + Adaptive ps0.202872, ps0.202875, and ps0.202880 completed at `37.35%`, `36.40%`, and `89.95%`, bracketing the `46.0%–51.0%` interval inside a width of 0.000005.
- Five fine-grid candidates ps0.2028755, ps0.2028760, ps0.2028765, ps0.2028770, and ps0.2028780 launched at 07:29 CST.
- Five FLTrust + PoiSAFL candidates remain active. Queue commit `1d26a7723854f28a6c936309ac800e5ffb63deb4` has 120 lines; synchronized SHA-256 is `90e1f0279d2906473a2d27ceb07b3ad9e8eb3f8e57c0816d1f852383b12e449e`, with normalized GitHub readback passed.
- Outstanding count remains **2** and 10 validated configs are active.

### 2026-11-18 08:51 CST — unexpected AutoDL disconnect

- At the last successful check (08:10 CST), all 10 final-wave configs were active: five RFA-Adaptive fine-grid candidates at rounds 118–127 and five FLTrust-PoiSAFL candidates at rounds 137–140.
- The SSH connection was then closed by the remote host. Three reconnection attempts over the following minutes returned `Connection refused`; this was not the requested final shutdown and no empty-queue/process audit was possible.
- Durable recovery state is preserved in GitHub: queue commit `1d26a7723854f28a6c936309ac800e5ffb63deb4`, 120 lines, SHA-256 `90e1f0279d2906473a2d27ceb07b3ad9e8eb3f8e57c0816d1f852383b12e449e`, plus all validated configs and accepted evidence.
- On instance recovery, inspect the five Adaptive and five FLTrust logs for `Summary:` first. For incomplete inactive configs, remove only their exact paths from `logs/calibration/queue_state/followup_queue_20261117.tsv.started`, then restart the 10-way queue daemon. Do not power off until both remaining cells are archived/read back and the final audit is empty.

## Replacement-server final-wave recovery (2026-11-18)

Only two Table II(d) cells remain open under the current error-only acceptance
rule:

- FLTrust+PoiSAFL, paper error interval 52.4--58.0%; running malicious-ratio
  candidates 0.8875, 0.8890, 0.8900, 0.8910, and 0.8925.
- RFA+Adaptive, paper error interval 46.0--51.0%; running poison-scale
  candidates 0.2028755, 0.2028760, 0.2028765, 0.2028770, and 0.2028780.

The ten candidates are fixed in
`configs/calibration/recovery_queue_20261118.tsv` (SHA-256
`6c567a36ce259519f195728db88bb98b5913ce021e04c92633ab71befece2048`).
They were relaunched from a clean replacement-server workspace at
2026-11-18 10:29:43 CST after the prior server disappeared before complete
summaries were available. Queue state is **running**; none of these ten entries
is accepted merely because it started. The selection rule remains
`final_round_only`, seed 2026, with ASR retained as descriptive metadata and
error rate controlling acceptance.

### Recovery candidate completion 1/10 (2026-11-18 11:49 CST)

- Candidate: `rfa_adaptive_m040_ps02028770_seed2026`
- Projection strength: `0.2028770`
- Selection point: final round 250 only
- Final accuracy: `8.22%`
- Final error rate: `91.78%`
- Target error interval: `46.0--51.0%`
- Decision: **outside target; not accepted**
- Dataset source: real CIFAR-10 with CIFAR-10-C unseen shift
- Evidence archive:
  `artifacts/experiment-evidence/2026-11-18/cifar10_iid_rfa_adaptive_m040_ps02028770_seed2026.tgz`
- Archive SHA-256:
  `aab2ba669138942d3659f0f26e78efded499835d18a08c01dc000e9762b4a46a`
- Archive commit: `43e086b8f53e34cf1d149b94ddf10e86c7b9c995`
- Git blob readback: `402f73e6469a3c0dcd1e69932720f7b5e724d160`, 198,982 bytes

The candidate is retained as a genuine failed calibration point; its earlier best
accuracy is not substituted for the preregistered final-round metric. Nine
recovery candidates remain running.

### RFA+Adaptive recovery wave result and refinement launch (2026-11-18)

All five original recovery candidates completed at the preregistered final round:

| Projection strength | Final error | Target 46.0--51.0% | Evidence SHA-256 |
| ---: | ---: | --- | --- |
| 0.2028755 | 36.91% | outside | `99cacfc4b42fd85333df7d769fee249b1aef914313aebaeb96772988dbc22eec` |
| 0.2028760 | 34.85% | outside | `885ec810e56457c5a4107fd6684b485186e64b7ec97cc2636d2c8380dc7fed92` |
| 0.2028765 | 35.65% | outside | `1d9cfd333d45fb152d912aec369a9537dcf28a731b75776e9fd36191ecf72a25` |
| 0.2028770 | 91.78% | outside | `aab2ba669138942d3659f0f26e78efded499835d18a08c01dc000e9762b4a46a` |
| 0.2028780 | 36.64% | outside | `bd38949266da061da49fc78976f2e6be0a77b1c25fa4fa14f0b7215e4b9f3b3e` |

The four newly archived bundles were committed together at
`b71bbd26a9b449f975e8453500e3150dce944462`; the 0.2028770 bundle was already
committed at `43e086b8f53e34cf1d149b94ddf10e86c7b9c995`. Each archive is under
`artifacts/experiment-evidence/2026-11-18/` and includes resolved config,
metrics, summary, run summary, diagnostics, attack trace, training log, and an
internal SHA256SUMS manifest.

The discontinuity is bracketed by 0.2028765 (35.65% error) and 0.2028770
(91.78% error). A five-point, pre-saved refinement wave was therefore launched
at 0.20287660, 0.20287670, 0.20287680, 0.20287690, and 0.20287695. Its queue is
`configs/calibration/recovery_rfa_refine_queue_20261118.tsv` (SHA-256
`9defee7693c45ce82248160299c6207c2acf224147f8c5265998789f3cf8b2a6`;
commit `cd025a31904b4413708e8872564bb8467ac2b249`). It started at
2026-11-18 12:10:15 CST in the five slots released by the completed RFA wave;
the five FLTrust+PoiSAFL candidates continued uninterrupted.

### FLTrust+PoiSAFL recovery wave result and refinement launch (2026-11-18)

All five original recovery candidates completed at final round 250:

| Malicious ratio | Final error | Target 52.4--58.0% | Evidence SHA-256 |
| ---: | ---: | --- | --- |
| 0.8875 | 37.54% | outside | `ee5e21168976c9588871c50b8c7b06cc49de7af7ae9cd27c7824a925afd81a84` |
| 0.8890 | 90.00% | outside | `2c520fb54e7ce059b7076f2071804ebb54323562990ea9db0287072946b0a290` |
| 0.8900 | 34.55% | outside | `f280184fb4b8143ebf2e4e46871482524af6729ff6868a89c339c361bba4a312` |
| 0.8910 | 34.56% | outside | `30a9d58bb70139a761af6be3b4d9544b5f5b79465a6e76ca2d2b758229a8c315` |
| 0.8925 | 38.48% | outside | `d436fe00963325d8fb6f983749f13ce379c990284470beb15c4c1c5442d02d5f` |

All five bundles were committed at
`6ce3520004bafe16c463e2051ceb2e70dbea76db` and read back with matching Git
blob IDs and byte lengths. The 0.8875--0.8890 discontinuity motivated a
pre-saved five-point wave at malicious ratios 0.8880, 0.8883, 0.8885, 0.8887,
and 0.8889. Its queue is
`configs/calibration/recovery_fltrust_refine_queue_20261118.tsv` (SHA-256
`2e012da4c124f4ad7e810c9d6d99a7f87374c95c1178723abca66df65b954d2e`;
commit `fabb3eb224180f9b2e6e41bf2c15fc4557a896d4`). The queue was prepared
without preemption and started all five entries at 2026-11-18 13:29:09 CST
after the original FLTrust processes exited.
