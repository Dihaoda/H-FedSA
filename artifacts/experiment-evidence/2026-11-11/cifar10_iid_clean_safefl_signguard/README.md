# CIFAR-10 IID clean SafeFL-compatible SignGuard formal evidence

This directory preserves the resolved configuration and generated run summary
for each preregistered seed (`2026`--`2030`). The shared manifest is
`configs/paper/cifar10_iid_clean_safefl_signguard.yaml`; all runs declared
source revision `8ce8962d2139392121a3f7b2b99654d8329a4c2e`, used real
CIFAR-10/CIFAR-10-C data, and completed 250 communication rounds.

The final seed errors were `15.51%`, `15.72%`, `15.44%`, `15.23%`, and
`15.25%`. Their mean and sample standard deviation are
`15.430 +/- 0.202%`, compared with the H-FedSA paper's SafeFL target
`15.3 +/- 0.3%` (mean gap `+0.130` percentage points). The published
machine-readable aggregate is
`results/published/cifar10_iid_clean_safefl_signguard_5seeds.json`.

The configuration explicitly uses the public SafeFL-compatible SignGuard
profile. The H-FedSA paper does not identify which SafeFL rule generated its
table column, so this evidence must retain the compatibility qualifier.

