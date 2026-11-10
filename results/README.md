# Results policy

`results/` is the local destination for generated experiments. Run directories,
checkpoints, raw metrics, and smoke outputs are ignored by Git.

Only reviewed, measured summaries belong in `results/published/`. Each published
summary must identify the exact configuration, commit, seeds, dataset source,
and whether the numbers are measured, synthetic, or illustrative. Smoke output
must never be promoted as a paper result.

