# CIFAR-10 IID clean FLTrust formal evidence

This directory preserves the exact resolved configurations and run summaries
for the five preregistered formal seeds `2026` through `2030`.

- Manifest: `configs/paper/cifar10_iid_clean_fltrust.yaml`
- Declared source revision: `bfc760750271d916446456d0dcf8e3158d0bc668`
- Dataset source: real CIFAR-10 and CIFAR-10-C
- Rounds: 250 per seed
- Final error: `15.614 +/- 0.595%` (sample standard deviation)
- Table II(d) target: `15.4 +/- 0.4%`
- Mean gap: `+0.214` percentage points

Each `seed*_config_resolved.yaml` is the configuration actually used after CLI
overrides. Each adjacent `seed*_run_summary.json` records the runtime, output
location, final metrics, environment provenance, overrides, and the same final
configuration in machine-readable form.

