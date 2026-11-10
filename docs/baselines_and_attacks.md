# Robust baselines and attack semantics

This repository distinguishes runnable implementations from claims of
bit-for-bit equivalence to an unavailable research artifact.

## SafeFL

SafeFL is an MPC-friendly **framework** that evaluates several aggregation
rules; its paper does not define one aggregator named `SafeFL`. The H-FedSA
paper reports a `SafeFL` column without identifying which rule in that
framework was selected. The `safefl` entry in this repository is therefore an
explicit compatibility profile:

- `safefl.rule: signguard` (the only currently supported choice);
- median-norm filtering with the SafeFL bounds `[0.1, 3.0]`;
- sign statistics on a deterministic 10% coordinate sample;
- two-cluster K-Means and intersection of the norm/sign filters.

The implementation follows the public SafeFL author repository. It is fully
runnable, but should be reported as `SafeFL-compatible (SignGuard profile)`
unless the missing rule selection for the H-FedSA table is recovered.

Primary sources:

- <https://encrypto.de/papers/GMSSWY23.pdf>
- <https://github.com/encryptogroup/SAFEFL>

## MSGuard

`msguard` combines the four public components described for MSGuard:

1. cosine similarity to a robust coordinate-wise center;
2. positive/zero/negative sign statistics;
3. a spectral anomaly score from the client Gram matrix;
4. update-magnitude deviation.

The standardized feature vectors are clustered with Mean Shift, without using
the configured malicious-client count. The largest cluster is selected; ties
prefer higher cosine similarity and lower spectral/magnitude anomaly. A
minimum-retention floor prevents an empty or tiny cluster from stopping a run
under strongly non-IID updates.

The 2025 TIFS article has no public author artifact linked from the paper or
publisher record. Consequently this is a transparent implementation of the
published component description, not a claim of source-identical reproduction.

Primary citation: <https://doi.org/10.1109/TIFS.2025.3555193>

## Krum-targeted and Trim-targeted attacks

`krum_targeted` and `trim_targeted` are round-level attacks applied after all
selected clients have completed local training. Only selected malicious-client
updates are replaced. The implementation follows the SafeFL authors' public
attack code, based on the local model-poisoning attacks of Fang et al. Each run
writes `targeted_attack_trace_<defense>.csv` with before/after norms and search
metadata.

Primary sources:

- <https://github.com/encryptogroup/SAFEFL/blob/main/attacks.py>
- <https://www.usenix.org/conference/usenixsecurity20/presentation/fang>

## PoiSAFL

PoiSAFL was proposed for semi-asynchronous FL, while the H-FedSA experiments
use synchronous round aggregation. The `poisafl` entry makes this adaptation
explicit and retains the three published mechanisms:

1. a malicious teacher is initialized by minimizing the inverted loss
   `-log(1 - p_y)`;
2. each malicious client trains a student with supervised loss plus
   temperature-scaled teacher distillation;
3. after the round is collected, malicious updates are scaled to a configurable
   fraction of the median benign update distance.

This is a synchronous adaptation. It does not reproduce PoiSAFL's buffering,
staleness, or fastest-client scheduling model and must not be described as an
exact semi-asynchronous reproduction.

Primary source: <https://www.usenix.org/conference/usenixsecurity25/presentation/pang-xiaoyi>

