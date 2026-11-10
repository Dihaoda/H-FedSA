# Calibration and result-matching protocol

The paper values are targets for diagnosis, not values to write into generated
metrics. The machine-readable CIFAR-10 targets are stored in
`configs/paper/targets/table_ii_cifar10_iid.yaml`.

## Allowed calibration

- tune explicitly documented optimizer, schedule, model, and defense parameters;
- run short calibration jobs in `results/calibration/`;
- compare learning curves and measured gaps against the paper;
- fix the five reporting seeds before formal runs;
- report all five formal runs, including failures and outliers.

## Disallowed result substitution

- hard-coding the paper values into `metrics.csv` or `summary.json`;
- relabeling synthetic, smoke, or interpolated values as measured results;
- running many seeds and reporting only the most favorable five;
- silently changing the protocol for one method to improve its table entry.

## Current CIFAR-10 sequence

1. Fit the no-attack FedAvg learning curve to the paper's `15.0%` error anchor.
2. Freeze shared model/training parameters.
3. Validate H-FedSA clean cost against its `15.7%` error anchor.
4. Calibrate scaling/backdoor mechanics and ASR measurement without changing
   the frozen clean-training protocol.
5. Run seeds `2026` through `2030` and report mean plus sample standard deviation.

Calibration outputs are evidence for choosing a protocol. They are not entries
in the final reproduction table.

