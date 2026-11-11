# CIFAR-10 IID clean H-FedSA formal evidence

This directory preserves the resolved configuration and generated run summary
for every preregistered seed (`2026`--`2030`). All five runs used real
CIFAR-10/CIFAR-10-C data, completed 250 communication rounds, and declared
source revision `fd738bc6fb835a28a8fd698aa8f11dce55d895b7`.

The final seed errors were `15.02%`, `15.24%`, `14.94%`, `15.47%`, and
`14.80%`. Their mean and sample standard deviation are
`15.094 +/- 0.264%`, compared with the paper target `15.7 +/- 0.2%` (mean
gap `-0.606` percentage points). No best checkpoint or seed was selected.

The registered attack-presence gate triggered in all 1,250 attack-free rounds.
The largest observed high-to-middle GMM intensity ratio was `1.2587`, below the
frozen threshold of `3.0`. There were no GMM fallbacks, non-finite feature
rounds, or weight-collapse rounds. The aggregate and gate audit are under
`results/published/`.

