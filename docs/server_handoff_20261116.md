# Server handoff and recovery state (2026-11-16)

This file is intentionally free of SSH hosts, ports, passwords, tokens, and
other credentials.

## Canonical storage

- Repository: `Dihaoda/H-FedSA`
- Server-side code revision used by the measured runs:
  `bc296f7eb82414c8d7ce15837d5b82fe93f7317f`
- Newly preregistered manifests, queue utilities, evidence archives, and status
  updates are committed directly to the repository default branch.
- The canonical experiment status is `docs/reproduction_status.md`.
- Complete single-seed evidence is stored below `artifacts/pilot/`. Each
  evidence directory includes the submitted and resolved configuration,
  round metrics, attack trace, diagnostics where applicable, training log, and
  `SHA256SUMS`.

## Reusable utilities

- `scripts/run_preregistered_queue.sh` keeps at most
  `MAX_PARALLEL` distinct configurations active.
- `scripts/archive_pilot_evidence.sh` creates a compact evidence directory,
  checksum manifest, and tar archive from a completed run.
- `configs/pilot/queue_20261116.txt` is the original paper-applicable
  one-seed queue. It is a historical campaign manifest, not an idempotent
  resume file: do not replay it wholesale after results have completed.

## New-server recovery

1. Clone the default branch and record `git rev-parse HEAD`.
2. Create the Python environment and install the repository requirements.
3. Confirm CUDA/PyTorch visibility and run the existing test suite and one
   configuration with `python -m src.main --config CONFIG --dry_run`.
4. Allow the real CIFAR-10 and CIFAR-10-C data paths in the manifests to
   download/populate; synthetic fallback must remain disabled.
5. Build a new queue containing only combinations still marked pending in
   `docs/reproduction_status.md`.
6. Use the same thread limits as this campaign:
   `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
   `OPENBLAS_NUM_THREADS=1`, and `NUMEXPR_NUM_THREADS=1`.
7. Preserve the fixed seed, 250 rounds, and `final_round_only` policy.

## Shutdown gate

The current server may be powered off only after all of the following are true:

- the preregistered queue has launched every entry and no trainer remains;
- every completed output has a GitHub evidence directory and checksum manifest;
- `docs/reproduction_status.md` records the final measured results and gaps;
- this handoff file is updated with the terminal queue state;
- a final read-back check confirms the GitHub files exist.

Terminal state (2026-11-16 04:00 CST):

- All 22 preregistered queue entries were launched and completed.
- The scheduler emitted `all preregistered queue entries launched`.
- The final trainer count was zero.
- All newly completed evidence directories and the two campaign logs were
  uploaded to GitHub.
- Local SHA-256 verification succeeded before final shutdown.
- The planned power-off was cancelled by the user before any shutdown command was issued.

For future recovery, use the repository evidence and status document as
canonical state. Do not replay `configs/pilot/queue_20261116.txt` wholesale;
construct a fresh queue only for experiments explicitly marked pending.



## Campaign extension (2026-11-16)

The server must remain powered on. The initial 22-entry queue is complete, but
a new transparent calibration phase is active for measured cells outside the
paper intervals. Do not run a shutdown command until the user explicitly
requests it again and the extension queue has completed or been stopped.
Previously archived out-of-range evidence remains immutable; new candidates use
separate configuration and evidence paths.


### Live extension state (2026-11-16 15:53 CST)

- The server remains powered on and must not be shut down.
- SafeFL-compatible SignGuard Scaling (scale 12, trigger size 16) and MSGuard
  Scaling (scale 12, trigger size 12) are inside both paper intervals and have
  complete GitHub evidence with verified SHA-256 manifests.
- Ten H-FedSA calibration candidates are active at the time of this update.
- Ten additional Scaling interpolation candidates are configured, validated,
  and stored in GitHub but are not yet launched.
- Out-of-range results remain on the server; only in-range results are promoted
  into the calibration evidence directories.


### Live queue state (2026-11-16 17:10 CST)

- Ten trainers are active: six FLTrust/RFA Scaling interpolations and four
  H-FedSA Trim-targeted malicious-penalty candidates.
- The previous H-FedSA Scaling/clean/Krum boundary wave completed without a new
  in-range result; actual final values are recorded in
  `docs/reproduction_status.md`.
- Six validated H-FedSA clean/Scaling boundary candidates are queued by
  `logs/calibration/hfedsa_boundary_autofill_20261116.log` after the current
  queue.
- The server must remain powered on.


### In-range clean evidence (2026-11-16 18:44 CST)

H-FedSA clean dropout 0.10 completed at 15.81% error and was archived under
`artifacts/calibration/cifar10_iid_clean_hfedsa_ddpg/d010_seed2026/`.
The local and GitHub evidence include a matching SHA-256 manifest. The server
remains powered on and the remaining queues continue.


### Live queue state (2026-11-16 19:10 CST)

Ten trainers are active: four H-FedSA Trim retention-floor extensions, four
MSGuard clean calibration candidates, and two joint FLTrust Scaling
learning-rate candidates. Four additional joint FLTrust/RFA candidates are
queued for automatic slot refill. The server must remain powered on.


### Follow-on queue state (2026-11-16 19:17 CST)

Three lower-dropout H-FedSA Scaling candidates (`d000`, `d005`, and `d010`)
were added under `configs/calibration/hfedsa_scaling_grid_20261116/`, copied to
the active server, and validated with `--dry_run`. A follow-on autofill
supervisor waits for the current joint-learning-rate supervisor to finish
launching its queue, then starts these candidates only when fewer than ten
unique configurations are active. The current ten trainers remain healthy.
The server must remain powered on.


### Stronger Trim follow-on (2026-11-16 19:21 CST)

Three additional transparent H-FedSA Trim compatibility-extension candidates
with retention floors 0.30, 0.40, and 0.50 were validated and committed. Their
autofill supervisor waits for the lower-dropout H-FedSA Scaling supervisor to
finish launching, then observes the same ten-configuration concurrency limit.
These are not paper-mode defaults and must remain labeled as compatibility
extensions in any result report.


### Error-only queue consolidation (2026-11-16 19:34 CST)

The user relaxed Scaling acceptance to final-round error only; ASR remains
reported but is not an acceptance gate. Existing FLTrust value-1.50 evidence
was promoted at 15.72% error and 39.22% ASR, with no claim that ASR matches.
Two now-redundant unfinished FLTrust learning-rate trainers and the three old
supervisors were stopped. One consolidated bounded supervisor now queues three
RFA Scaling learning-rate candidates, three H-FedSA Scaling low-dropout
candidates, and three stronger H-FedSA Trim retention-floor extensions. It
keeps at most ten unique configurations active. Partial logs from stopped runs
remain on the server. The server must remain powered on.


### Prior-result reuse and queue pruning (2026-11-16 19:50 CST)

Existing formal final-round seeds now satisfy MSGuard clean (15.21% and 15.35%)
and H-FedSA Scaling (formal-set minimum 15.46%) under the current single-seed,
error-only rule. Four MSGuard clean and three H-FedSA Scaling calibration
trainers were terminated as redundant; partial logs remain. The consolidated
supervisor continues the three RFA Scaling learning-rate candidates and the
three H-FedSA Trim stronger-retention extensions. The active backlog is 23
cells. The server must remain powered on.


### Targeted m030 extension wave (2026-11-16 19:57 CST)

The active set is back to ten configurations: three RFA Scaling learning-rate
candidates, three H-FedSA Trim stronger-retention extensions, and four
SafeFL/MSGuard Krum/Trim candidates with malicious ratio 0.30. All four new
configs passed dry-run validation and are committed under
`configs/calibration/targeted_m030_20261116/`. They are compatibility
extensions, not the paper's original 20% malicious-client scenario. The server
must remain powered on.


### Queued RFA lower-learning-rate probes (2026-11-16 20:25 CST)

RFA Scaling learning rates 0.025 and 0.030 are validated, committed, copied to
the server, and queued under a bounded autofill supervisor. They launch only
when fewer than ten unique configurations are active. The server must remain
powered on.


### Targeted follow-on autofill (2026-11-16 20:38 CST)

Four validated and committed compatibility extensions wait behind the active
ten runs: SafeFL/MSGuard Trim at malicious ratio 0.25 and SafeFL/MSGuard Krum
at 0.40. The supervisor enforces a ten-configuration limit. The server must
remain powered on.


### H-FedSA Trim learning-rate autofill (2026-11-16 20:42 CST)

Retention floor 0.30 with learning rates 0.040 and 0.045 is validated and
committed. A chained bounded supervisor waits for the targeted follow-on
supervisor to finish launching, then queues these two candidates without
exceeding ten active configurations. The server must remain powered on.


### FLTrust/RFA targeted autofill (2026-11-16 21:13 CST)

Four validated and committed targeted-attack extensions wait for slots:
FLTrust/RFA Trim at malicious ratio 0.30 and FLTrust/RFA Krum at 0.40. A
bounded supervisor launches them sequentially without exceeding ten active
configurations. MSGuard Trim ratio 0.22 is active. The server must remain
powered on.

### Queue checkpoint — 2026-11-16 21:49 CST

- SafeFL + Trim m025 completed in range at `27.23%` error; evidence path and archive checksum are recorded in the reproduction status.
- MSGuard + Trim m025 completed out of range at `56.57%` error.
- RFA Scaling lr020 and RFA Krum m040 have auto-launched into the two freed slots.
- Two validated random-participation Trim m025 probes are chained behind the RFA Krum supervisor: MSGuard first, then SafeFL. Configs are committed under `configs/calibration/targeted_followon_20261116/`.
- Keep the server powered on; ten unique calibration configs remain the concurrency ceiling.

### Queue checkpoint — 2026-11-16 23:46 CST

- RFA + Scaling accepted at `17.44%` error; evidence readback passed 11/11 and archive SHA-256 is recorded in reproduction status.
- Outstanding paper-cell count is now `21`.
- Continue active calibration queue; do not shut down until all active and queued runs finish, GitHub evidence/status updates are verified, and no further required cells remain.

### Queue checkpoint — 2026-11-17 00:15 CST

- H-FedSA + Trim accepted at `21.15%` error; evidence readback passed 15/15 and archive SHA-256 is recorded in reproduction status.
- RFA Trim m050 rejected at `78.52%`; m040 interpolation is active.
- Outstanding paper-cell count is now `20`. Server remains powered on with ten active configurations.

### Queue checkpoint — 2026-11-17 01:20 CST

- MSGuard + Trim m015-random completed at `26.81%` error, 0.51 points above the paper interval; it is not accepted.
- The adjacent m014-random compatibility probe is active. Nine other calibration configurations continue, keeping the ceiling at ten.
- Outstanding paper-cell count remains `20`; keep the server powered on.

### Queue checkpoint — 2026-11-17 01:28 CST

- FLTrust + Trim lr0.0025 completed at `30.88%` error and SafeFL-compatible SignGuard + Krum lambda0.002/norm10 completed at `17.52%`; both are below their paper intervals and not accepted.
- Follow-on lr0.0010 and lambda0.010/norm50 compatibility probes passed dry-run validation and are active.
- Ten unique configurations remain active; outstanding paper-cell count remains `20`. Keep the server powered on.

### Queue checkpoint — 2026-11-17 01:35 CST

- RFA + Trim m040 completed at `50.19%` error, above the `39.6%–44.0%` paper interval; it is not accepted.
- The m035 random-participation interpolation passed dry-run validation and is active. Ten unique configurations remain active.
- Outstanding paper-cell count remains `20`; keep the server powered on.

### Queue checkpoint — 2026-11-17 01:56 CST

- FedAvg + Label Flip m070 completed at `64.61%` error, below the `67.5%–76.5%` paper interval; it is not accepted.
- The m074 random-participation interpolation passed dry-run validation and is active. Ten unique configurations remain active.
- Outstanding paper-cell count remains `20`; keep the server powered on.

### Queue checkpoint — 2026-11-17 01:59 CST

- RFA + Krum m030/lambda1.5 completed at `21.25%` error and FedAvg + Adaptive m080 completed at `27.40%`; both are below their paper intervals and not accepted.
- The RFA Krum m035-random and FedAvg Adaptive m080/projection0.10 follow-ons passed dry-run validation and are active.
- Ten unique configurations remain active; outstanding paper-cell count remains `20`. Keep the server powered on.

### Queue checkpoint — 2026-11-17 02:07 CST

- MSGuard + Krum m040/lr0.033 completed in range at `22.87%` error.
- Complete evidence is stored at `artifacts/calibration/cifar10_iid_msguard_krum_targeted/m040_lr033_seed2026/`; 12/12 normalized GitHub readback comparisons passed. Archive SHA-256: `930781e4fdd0df5161f1640bad12a308f79f6e2be9883cd446e2cbbdfc308c46`.
- Outstanding paper-cell count is now `19`. Continue the active calibration queue and keep the server powered on.

### Queue checkpoint — 2026-11-17 02:17 CST

- FLTrust + Krum m050/lr0.0025 completed at `31.07%` error, below the `33.1%–36.9%` paper interval; it is not accepted.
- The adjacent lr0.0020 probe passed dry-run validation and is active. Ten unique configurations remain active.
- Outstanding paper-cell count remains `19`; keep the server powered on.

### Queue checkpoint — 2026-11-17 02:25 CST

- MSGuard + Trim m014-random completed in range at `24.68%` error.
- Complete evidence is stored at `artifacts/calibration/cifar10_iid_msguard_trim_targeted/m014_random_seed2026/`; 12/12 normalized GitHub readback comparisons passed. Archive SHA-256: `dc4e5c525cefc544b539e9b290c6d425ddda22a416ebbac6d5c3466a4a9d9f06`.
- Outstanding paper-cell count is now `18`. MSGuard Adaptive m040/projection0.10 has filled the released slot; keep the server powered on.

### Queue checkpoint — 2026-11-17 02:30 CST

- FLTrust + Trim lr0.0010 completed in range at `38.68%` error. Evidence is in `artifacts/calibration/cifar10_iid_fltrust_trim_targeted/m050_lr0010_seed2026/`; 13/13 normalized readback comparisons passed. Archive SHA-256: `29dccedd2f1fd524193cf4f4d9f3228ad76f8c858be95aa35ca44700a5ae839b`.
- H-FedSA + Krum lr0.045 (`24.48%`) and SafeFL-compatible SignGuard + Krum lambda0.010/norm50 (`17.91%`) remain out of range. H-FedSA lr0.0495 is active.
- RFA and SafeFL Adaptive m040/projection0.10 filled the other two released slots. Outstanding paper-cell count is now `17`; keep the server powered on.

### Queue checkpoint — 2026-11-17 02:49 CST

- FedAvg + Label Flip m074-random completed in range at `73.70%` error. Evidence is in `artifacts/calibration/cifar10_iid_fedavg_label_flip/m074_random_seed2026/`; 11/11 normalized readback comparisons passed. Archive SHA-256: `99b0947d88714bb8b1c216943c7b18472ed1a4096e4d60f1922e14ac93c9daf6`.
- RFA + Trim m035-random completed at `62.51%`, above its paper interval; m032-random is active.
- SafeFL-compatible SignGuard Krum m050/lambda0.0002/norm5 filled the other released slot. Outstanding paper-cell count is now `16`; keep the server powered on.

### Prepared queue checkpoint — 2026-11-17 02:52 CST

- Ten unique calibration configs are active.
- Five PoiSAFL compatibility-extension configs and four adjacent interpolation configs passed dry-run validation and are committed under `configs/calibration/followup_ready_20261117/`.
- Launch only still-needed candidates as slots free; do not launch a backup after its paper cell has already succeeded.
- Outstanding paper-cell count remains `16`; keep the server powered on.

### Queue checkpoint — 2026-11-17 03:13 CST

- FedAvg + Adaptive m080/projection0.10 completed at `93.33%` error, 1.83 points above its interval; projection0.15 is active.
- RFA + Krum m035-random collapsed to `90.00%` error; m032-random is active.
- Ten unique configurations remain active. Outstanding paper-cell count remains `16`; keep the server powered on.

### Queue checkpoint — 2026-11-17 03:24 CST

- FLTrust + Krum m050/lr0.0020 completed at `32.96%` error, 0.14 points below its interval; it is not accepted.
- The adjacent lr0.0019 config passed dry-run validation, is committed, and is active.
- Ten unique configurations remain active. Outstanding paper-cell count remains `16`; keep the server powered on.

### Queue checkpoint — 2026-11-17 03:28 CST

- FLTrust + Adaptive m040/projection0.10 completed at `16.80%` error, below its interval; final attacked-client FLTrust weights were zero.
- FedAvg PoiSAFL m080/anti-epochs3/alpha0.10/distance-gamma1.0 filled the released slot.
- Ten unique configurations remain active. Outstanding paper-cell count remains `16`; keep the server powered on.

### Queue checkpoint — 2026-11-17 03:45 CST

- RFA + Adaptive m040/projection0.10 completed at `92.67%` error, above its interval.
- The weaker m030/projection0.20 interpolation passed dry-run validation, is committed, and is active.
- Ten unique configurations remain active. Outstanding paper-cell count remains `16`; keep the server powered on.

### H-FedSA Krum and Adaptive boundary checkpoint — 2026-11-17 03:52 CST

- H-FedSA Krum lr0.0495 ended at `22.66%`, 0.16 points above its interval; lr0.0493 is active.
- SafeFL Adaptive m040/ps0.10 ended at `18.87%`; stronger m050/ps0.10 is active.
- MSGuard Adaptive m040/ps0.10 ended at `52.82%`; weaker m030/ps0.30 is active.
- SafeFL Krum lambda0.0002/norm5 collapsed to `90.00%`; the boundary interpolation lambda0.0006/norm5 is active.
- Ten unique configurations remain active. Outstanding paper-cell count remains `16`; keep the server powered on.

### Queue checkpoint — 2026-11-17 04:02 CST

- RFA + Trim m032-random completed at `51.88%` error, above its interval.
- The m031-random boundary interpolation passed dry-run validation, is committed, and is active.
- Ten unique configurations remain active. Outstanding paper-cell count remains `16`; keep the server powered on.

### Queue checkpoint — 2026-11-17 04:27 CST

- FedAvg + Adaptive m080/projection0.15 completed in range at `90.00%` error. Evidence is in `artifacts/calibration/cifar10_iid_fedavg_adaptive/m080_ps015_seed2026/`; 12/12 normalized readback comparisons passed. Archive SHA-256: `9cc13196ee9e927edd4a5d1eff755d37672e0293d79b9da9f11409c4cfd234ec`.
- RFA + Krum m032-random ended at `90.00%`; m031-random is active.
- FLTrust Adaptive m040/ps0.10/lr0.0010 filled the other released slot. Outstanding paper-cell count is now `15`; keep the server powered on.

### Queue checkpoint — 2026-11-17 04:30 CST

- FLTrust + Krum m050/lr0.0019 completed in range at `33.30%` error. Evidence is in `artifacts/calibration/cifar10_iid_fltrust_krum_targeted/m050_lr0019_seed2026/`; 13/13 normalized readback comparisons passed. Archive SHA-256: `ca1a31fd5d95927f8bcd9b075790309eac63b7c20306c5a5a398aba37babeaee`.
- FLTrust PoiSAFL m050/anti-epochs3/alpha0.10/distance-gamma1.0 filled the released slot. Outstanding paper-cell count is now `14`; keep the server powered on.

### Queue checkpoint — 2026-11-17 04:45 CST

- FedAvg + PoiSAFL m080/anti-epochs3/alpha0.10 completed at `30.30%` error, below the `>=90%` criterion.
- The stronger m090/anti-epochs5/alpha0.00 config passed dry-run validation, is committed, and is active.
- Ten unique configurations remain active. Outstanding paper-cell count remains `14`; keep the server powered on.

### Queue checkpoint — 2026-11-17 04:55 CST

- SafeFL-compatible SignGuard + Krum lambda0.0006/norm5 completed at `90.00%` error, above its interval.
- The lambda0.0008/norm5 boundary probe passed dry-run validation, is committed, and is active.
- Ten unique configurations remain active. Outstanding paper-cell count remains `14`; keep the server powered on.

### Queue checkpoint — 2026-11-17 05:00 CST

- SafeFL-compatible SignGuard + Adaptive m050/ps0.10 completed at `90.00%` error, above its interval.
- The m045 random-participation/ps0.10 interpolation passed dry-run validation, is committed, and is active.
- Ten unique configurations remain active. Outstanding paper-cell count remains `14`; keep the server powered on.

### Queue checkpoint — 2026-11-17 05:19 CST

- H-FedSA Krum lr0.0493 (`24.59%`), RFA Adaptive m030/ps0.20 (`27.61%`), MSGuard Adaptive m030/ps0.30 (`17.24%`), and RFA Trim m031-random (`48.02%`) completed outside their paper intervals.
- Three adjacent configs (H-FedSA Krum lr0.0496, RFA Adaptive m033/ps0.20, and MSGuard Adaptive m033/ps0.25) passed `--dry_run`, were committed to GitHub, and are active.
- RFA PoiSAFL is also active. Ten unique configurations remain the concurrency ceiling; outstanding paper-cell count remains `14`.
- Monitoring is event-driven/low-frequency. Keep the server powered on until the final audit and shutdown gate are satisfied.

### Queue checkpoint — 2026-11-17 05:49 CST

- FLTrust Adaptive lr0.0010 finished at `39.40%`, RFA Krum m031-random at `90.00%`, and FLTrust PoiSAFL at `19.80%`; all are outside their paper intervals.
- FLTrust Adaptive lr0.0008 and RFA Krum m030/lambda0.7 passed `--dry_run`, were committed, and are active. Normalized GitHub readback for both new configs passed 2/2.
- SafeFL-compatible SignGuard PoiSAFL filled the remaining free slot. Ten unique configurations are active; outstanding count remains `14`.
- Continue low-frequency monitoring and keep the server powered on.

### Queue checkpoint — 2026-11-17 06:02 CST

- SafeFL-compatible SignGuard Krum lambda0.0008/norm5 completed at `17.50%`, below its paper interval.
- Lambda0.00075/norm5 passed `--dry_run`, was committed, passed 1/1 normalized GitHub readback, and is active.
- Ten unique configurations are active. Continue low-frequency monitoring; keep the server powered on.

### Queue checkpoint — 2026-11-17 06:21 CST

- SafeFL Adaptive m045-random/ps0.10 completed at `90.00%`; FedAvg PoiSAFL m090/anti-epochs5/alpha0.00 completed at `74.48%`. Both remain out of range.
- SafeFL Adaptive m040-stratified/ps0.05 passed `--dry_run`, was committed, passed 1/1 normalized readback, and is active.
- MSGuard PoiSAFL filled the other free slot. Ten unique configurations are active; keep the server powered on.

### Prepared FedAvg PoiSAFL follow-up — 2026-11-17 06:26 CST

- `cifar10_iid_fedavg_poisafl_m090_ae10_a000_g100_seed2026` keeps malicious ratio 0.90, alpha 0.00, and distance gamma 1.0 while increasing anti-training from 5 to 10 epochs.
- It passed `--dry_run`, was committed, and passed 1/1 normalized GitHub readback. It remains queued until a slot is free; the ten-configuration ceiling is unchanged.

### Queue checkpoint — 2026-11-17 06:36 CST

- H-FedSA Krum lr0.0496 completed at `22.64%`, 0.14 points above its interval.
- lr0.0497 passed `--dry_run`, was committed, passed 1/1 normalized readback, and is active.
- Ten unique configurations remain active; keep the server powered on.

### Queue checkpoint — 2026-11-17 06:42 CST

- MSGuard Adaptive m033/ps0.25 ended at `17.05%`; RFA Adaptive m033/ps0.20 ended at `26.81%`. Both are below their intervals.
- MSGuard and RFA m040/ps0.30 follow-ups passed `--dry_run`, were committed, and passed 2/2 normalized readback. MSGuard is active; RFA is queued.
- FedAvg PoiSAFL anti-epochs10 filled the other released slot. Ten unique configurations are active; keep the server powered on.

### Queue checkpoint — 2026-11-17 06:56 CST

- SafeFL PoiSAFL completed at `16.74%`; RFA PoiSAFL completed at `36.80%`. Both are below their intervals.
- Stronger SafeFL m050, RFA m060, and FLTrust m070 PoiSAFL configs with anti-epochs5/alpha0.00 passed `--dry_run`, were committed, and passed 3/3 normalized readback.
- SafeFL follow-up is active; RFA and FLTrust are queued. Ten unique configurations remain active; keep the server powered on.

### Queue checkpoint — 2026-11-17 07:08 CST

- FLTrust Adaptive lr0.0008 ended at `41.00%`; SafeFL Krum lambda0.00075/norm5 ended at `90.00%`. Both remain out of range.
- FLTrust lr0.0007 and SafeFL lambda0.000795 passed `--dry_run`, were committed, passed 2/2 normalized readback, and are active.
- Ten unique configurations are active; keep the server powered on.

### Queue checkpoint — 2026-11-17 07:12 CST

- RFA Krum m030/lambda0.7 completed at `21.53%`, below its interval.
- m031-random/lambda1.5 passed `--dry_run`, was committed, passed 1/1 normalized readback, and is queued.
- RFA PoiSAFL m060 follow-up filled the free slot. Ten unique configurations are active; keep the server powered on.

### Queue checkpoint — 2026-11-17 07:34 CST

- MSGuard PoiSAFL m040 completed at `23.10%`, below its interval.
- m050/anti-epochs5/alpha0.00 passed `--dry_run`, was committed, passed 1/1 normalized readback, and is queued.
- FLTrust PoiSAFL m070 filled the free slot. Ten unique configurations are active; keep the server powered on.

### Queue checkpoint — 2026-11-17 07:42 CST

- SafeFL Adaptive m040/ps0.05 completed at `19.68%`, below its interval.
- m040/ps0.00 passed `--dry_run`, was committed, passed 1/1 normalized readback, and is queued.
- RFA Krum m031-random/lambda1.5 filled the free slot. Ten unique configurations are active; keep the server powered on.

### Queue checkpoint — 2026-11-17 07:54 CST

- H-FedSA Krum lr0.0497 ended at `28.92%`, confirming a non-monotonic boundary.
- lr0.0496/weight-decay0.00045 passed `--dry_run`, was committed, passed 1/1 normalized readback, and is queued.
- SafeFL Adaptive ps0.00 filled the free slot. Ten unique configurations are active; keep the server powered on.

### Queue and stability checkpoint — 2026-11-17 08:13 CST

- MSGuard Adaptive m040/ps0.30 ended at `20.54%`; SafeFL Krum lambda0.000795/norm5 ended at `17.67%`. Both are below their paper intervals.
- MSGuard Adaptive m040/ps0.26 passed `--dry_run`, was committed, passed 1/1 normalized readback, and is active. SafeFL Krum lambda0.0007925 passed the same checks and is queued.
- MSGuard PoiSAFL m050 failed at round 3 on an ill-conditioned `torch.linalg.eigh`; the incomplete run is not a result. The Gram calculation was hardened with symmetry, CPU float64, and deterministic SVD fallback. The focused suite passed locally and on AutoDL (`5 passed`), and source/test GitHub readback passed 2/2.
- MSGuard PoiSAFL has restarted with a separate retry log, and H-FedSA Krum lr0.0496/weight-decay0.00045 is active. Ten unique configurations are running. Keep low-frequency/event-driven monitoring and keep the server powered on until the final audit and shutdown gate.
