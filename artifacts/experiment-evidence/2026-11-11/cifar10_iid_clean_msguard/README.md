# CIFAR-10 IID clean MSGuard formal evidence

This directory preserves the resolved configuration and generated run summary
for each preregistered seed (`2026`--`2030`). The shared manifest is
`configs/paper/cifar10_iid_clean_msguard.yaml`; all runs declared source
revision `484c0b22ab195aaa551469213ebc4f3c84cae468`, used real
CIFAR-10/CIFAR-10-C data, and completed 250 communication rounds.

The final seed errors were `15.69%`, `15.52%`, `15.75%`, `15.21%`, and
`15.35%`. Their mean and sample standard deviation are
`15.504 +/- 0.227%`, compared with the paper target `15.2 +/- 0.3%` (mean
gap `+0.304` percentage points). The unrounded mean is `0.004` points above
the paper's one-standard-deviation upper bound. The machine-readable aggregate
is `results/published/cifar10_iid_clean_msguard_5seeds.json`.

The configuration implements the four published MSGuard components with Mean
Shift clustering. No public author artifact is available, so the evidence must
retain the published-component implementation qualifier.

