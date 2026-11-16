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
