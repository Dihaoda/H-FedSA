# Calibration backlog (2026-11-16)

This backlog lists measured CIFAR-10 IID cells that do not fully satisfy the
paper interval. It is a transparent calibration plan, not permission to replace
measured values. Existing out-of-range evidence remains immutable. New
candidates use fixed seed 2026, 250 rounds, final-round-only selection, unique
configuration/output paths, and are labeled as calibration runs.

## Summary

There are 19 out-of-range combinations under the current error-only acceptance rule and the user-approved reuse of prior final-round seed results. FedAvg is not applicable to the paper's
Krum-targeted and Trim-targeted rows and is therefore excluded.

| Attack | Out-of-range combinations |
| --- | ---: |
| No attack | 0 |
| Label flip | 1 |
| Scaling | 1 |
| Krum-targeted | 4 |
| Trim-targeted | 3 |
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
