# AutoDL experiment evidence (2026-11-10)

This directory preserves the portable evidence needed to audit or resume the
2026-11-10 CIFAR-10 experiments after the original AutoDL instance is released.
The bundle contains 245 files from:

- `results/formal/`;
- `results/calibration/`;
- the AutoDL training-log directory, normalized to `logs/` in the archive.

Included files are run configurations, resolved configurations, data and
partition diagnostics, complete or partial metric CSVs, run summaries, and
training logs. Model checkpoints (`*.pt`), datasets, caches, aggregation-debug
tables, client-label tables, and per-client diagnostic tables are intentionally
excluded. These large files are not required to reconstruct the environment or
verify the reported final metrics.

The gzip archive is stored as ordered base64 text parts so it can be committed
through the GitHub API without Git LFS. Reconstruct it on Linux from this
directory with:

```bash
cat hfedsa-experiment-evidence-2026-11-10.tar.gz.b64.part-* \
  | base64 -d > hfedsa-experiment-evidence-2026-11-10.tar.gz
sha256sum -c SHA256SUMS
tar -xzf hfedsa-experiment-evidence-2026-11-10.tar.gz -C /path/to/H-FedSA
```

Expected archive SHA-256:

```text
e63fe46f771a2b7b421f3acc37df6a8e71d9620bf282df974c4e5e9f97aa1a88
```

The archive itself is 691,809 bytes. The published five-seed summary JSON files
remain under `results/published/` and are the canonical reported results.

