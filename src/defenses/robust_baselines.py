from __future__ import annotations

import math

import numpy as np
import torch
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.cluster import KMeans

from src.federated.tensor_ops import StateDict, average_updates, flatten_update, unflatten_update


def _safe_standardize(features: np.ndarray) -> np.ndarray:
    features = np.nan_to_num(np.asarray(features, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    scale = features.std(axis=0)
    scale[scale < 1e-12] = 1.0
    return (features - features.mean(axis=0)) / scale


def _uniform_aggregate(
    updates: list[tuple[int, StateDict]], retained: list[int]
) -> tuple[StateDict, list[dict]]:
    if not retained:
        retained = list(range(len(updates)))
    weight = 1.0 / len(retained)
    retained_set = set(retained)
    aggregate = average_updates([updates[index][1] for index in retained], [weight] * len(retained))
    diagnostics = [
        {
            "client_id": client_id,
            "weight": weight if index in retained_set else 0.0,
            "retained": index in retained_set,
            "predicted_malicious": index not in retained_set,
        }
        for index, (client_id, _) in enumerate(updates)
    ]
    return aggregate, diagnostics


class SafeFLCompatible:
    """Runnable SafeFL-compatible baseline using its published SignGuard rule.

    SafeFL is an MPC evaluation framework rather than one uniquely defined
    aggregator.  The H-FedSA paper does not name which SafeFL rule produced its
    table entries, so this adapter makes the choice explicit and reproducible.
    The default reproduces the SignGuard path shipped by the SafeFL authors:
    median-norm filtering intersected with two-cluster sign statistics.
    """

    name = "safefl"

    def __init__(
        self,
        rule: str = "signguard",
        seed: int = 0,
        sign_fraction: float = 0.1,
        norm_lower: float = 0.1,
        norm_upper: float = 3.0,
    ) -> None:
        if str(rule).lower() != "signguard":
            raise ValueError("SafeFLCompatible currently supports rule='signguard' only.")
        self.rule = "signguard"
        self.seed = int(seed)
        self.sign_fraction = float(np.clip(sign_fraction, 0.0, 1.0))
        self.norm_lower = float(norm_lower)
        self.norm_upper = float(norm_upper)
        self.round_index = 0
        self.last_fallback_reason = ""

    def aggregate(
        self,
        updates: list[tuple[int, StateDict]],
        root_update: StateDict | None = None,
        sample_counts: dict[int, int] | None = None,
        **_: object,
    ) -> tuple[StateDict, list[dict]]:
        if not updates:
            raise ValueError("SafeFL cannot aggregate an empty update list.")
        if len(updates) == 1:
            aggregate, diagnostics = _uniform_aggregate(updates, [0])
            diagnostics[0]["safe_rule"] = self.rule
            return aggregate, diagnostics

        flats = torch.stack([flatten_update(update) for _, update in updates]).float()
        norms = torch.linalg.norm(flats, dim=1)
        median_norm = float(torch.median(norms).item())
        ratios = norms / max(median_norm, 1e-12)
        norm_kept = {
            index
            for index, ratio in enumerate(ratios.tolist())
            if self.norm_lower <= float(ratio) <= self.norm_upper
        }

        dimension = int(flats.shape[1])
        sample_size = max(1, min(dimension, int(round(dimension * self.sign_fraction))))
        generator = torch.Generator(device="cpu")
        generator.manual_seed(self.seed + self.round_index)
        coordinates = torch.randperm(dimension, generator=generator)[:sample_size]
        selected_signs = torch.sign(flats[:, coordinates])
        sign_features = torch.stack(
            [
                (selected_signs > 0).float().mean(dim=1),
                (selected_signs == 0).float().mean(dim=1),
                (selected_signs < 0).float().mean(dim=1),
            ],
            dim=1,
        ).numpy()
        labels = KMeans(n_clusters=2, max_iter=20, n_init=10, random_state=self.seed + self.round_index).fit_predict(
            sign_features
        )
        cluster_counts = np.bincount(labels, minlength=2)
        largest_cluster = int(np.argmax(cluster_counts))
        sign_kept = {index for index, label in enumerate(labels.tolist()) if label == largest_cluster}
        retained = sorted(norm_kept & sign_kept)
        self.last_fallback_reason = ""
        if not retained:
            retained = sorted(norm_kept or sign_kept or set(range(len(updates))))
            self.last_fallback_reason = "empty_norm_sign_intersection"

        aggregate, diagnostics = _uniform_aggregate(updates, retained)
        retained_set = set(retained)
        for index, item in enumerate(diagnostics):
            item.update(
                {
                    "safe_rule": self.rule,
                    "norm_ratio": float(ratios[index].item()),
                    "norm_filter_pass": index in norm_kept,
                    "sign_cluster": int(labels[index]),
                    "sign_cluster_pass": index in sign_kept,
                    "sign_positive_fraction": float(sign_features[index, 0]),
                    "sign_zero_fraction": float(sign_features[index, 1]),
                    "sign_negative_fraction": float(sign_features[index, 2]),
                    "predicted_malicious": index not in retained_set,
                    "fallback_reason": self.last_fallback_reason,
                }
            )
        self.round_index += 1
        return aggregate, diagnostics


class MSGuard:
    """Multi-strategy robust aggregation with Mean-Shift client clustering.

    The implementation follows the public algorithm description: it combines
    cosine similarity, sign statistics, spectral anomaly scores, and gradient
    magnitude before Mean-Shift clustering.  It does not require the number of
    Byzantine clients.
    """

    name = "msguard"

    def __init__(
        self,
        quantile: float = 0.3,
        bandwidth: float | None = None,
        min_retained_fraction: float = 0.5,
    ) -> None:
        self.quantile = float(np.clip(quantile, 0.05, 1.0))
        self.bandwidth = None if bandwidth is None else float(bandwidth)
        self.min_retained_fraction = float(np.clip(min_retained_fraction, 0.1, 1.0))
        self.last_fallback_reason = ""

    def aggregate(
        self,
        updates: list[tuple[int, StateDict]],
        root_update: StateDict | None = None,
        sample_counts: dict[int, int] | None = None,
        **_: object,
    ) -> tuple[StateDict, list[dict]]:
        if not updates:
            raise ValueError("MSGuard cannot aggregate an empty update list.")
        if len(updates) <= 2:
            aggregate, diagnostics = _uniform_aggregate(updates, list(range(len(updates))))
            for item in diagnostics:
                item["fallback_reason"] = "too_few_clients_for_clustering"
            self.last_fallback_reason = "too_few_clients_for_clustering"
            return aggregate, diagnostics

        flats = torch.stack([flatten_update(update) for _, update in updates]).float()
        norms = torch.linalg.norm(flats, dim=1).clamp_min(1e-12)
        normalized = flats / norms[:, None]
        reference = torch.median(flats, dim=0).values
        reference_norm = torch.linalg.norm(reference).clamp_min(1e-12)
        cosine = torch.mv(normalized, reference / reference_norm)

        sign_values = torch.sign(flats)
        sign_positive = (sign_values > 0).float().mean(dim=1)
        sign_zero = (sign_values == 0).float().mean(dim=1)
        sign_negative = (sign_values < 0).float().mean(dim=1)

        centered = normalized - normalized.mean(dim=0, keepdim=True)
        if torch.linalg.norm(centered).item() <= 1e-12:
            spectral = torch.zeros(len(updates), dtype=torch.float32)
        else:
            # Only the small client-by-client Gram matrix is decomposed, so the
            # cost stays linear in the model dimension for a fixed client count.
            gram = centered @ centered.T
            eigenvalues, eigenvectors = torch.linalg.eigh(gram)
            top_left = eigenvectors[:, int(torch.argmax(eigenvalues).item())]
            spectral = top_left.square()

        median_norm = torch.median(norms).clamp_min(1e-12)
        norm_ratio = norms / median_norm
        raw_features = torch.stack(
            [cosine, sign_positive, sign_zero, sign_negative, spectral, torch.log(norm_ratio)], dim=1
        ).numpy()
        features = _safe_standardize(raw_features)
        bandwidth = self.bandwidth
        if bandwidth is None:
            bandwidth = float(estimate_bandwidth(features, quantile=self.quantile, n_samples=len(updates)))
        if not np.isfinite(bandwidth) or bandwidth <= 1e-8:
            bandwidth = None
        labels = MeanShift(bandwidth=bandwidth, bin_seeding=False, cluster_all=True).fit_predict(features)

        unique_labels = sorted(set(int(label) for label in labels.tolist()))
        cluster_scores: dict[int, tuple[float, float, int]] = {}
        for label in unique_labels:
            indices = np.where(labels == label)[0]
            cluster_scores[label] = (
                float(np.mean(raw_features[indices, 0]) - np.mean(raw_features[indices, 4]) - 0.1 * np.mean(np.abs(raw_features[indices, 5]))),
                float(np.mean(raw_features[indices, 0])),
                int(len(indices)),
            )
        largest_size = max(score[2] for score in cluster_scores.values())
        eligible = [label for label, score in cluster_scores.items() if score[2] == largest_size]
        benign_label = max(eligible, key=lambda label: cluster_scores[label][:2])
        retained = np.where(labels == benign_label)[0].tolist()

        minimum = max(1, int(math.ceil(len(updates) * self.min_retained_fraction)))
        self.last_fallback_reason = ""
        if len(retained) < minimum:
            # Keep the most benign feature scores rather than silently failing
            # when Mean-Shift creates many tiny clusters on highly non-IID data.
            ranking_score = raw_features[:, 0] - raw_features[:, 4] - 0.1 * np.abs(raw_features[:, 5])
            retained = np.argsort(-ranking_score)[:minimum].tolist()
            self.last_fallback_reason = "minimum_retention_floor"

        aggregate, diagnostics = _uniform_aggregate(updates, retained)
        retained_set = set(retained)
        for index, item in enumerate(diagnostics):
            item.update(
                {
                    "cosine_similarity": float(cosine[index].item()),
                    "sign_positive_fraction": float(sign_positive[index].item()),
                    "sign_zero_fraction": float(sign_zero[index].item()),
                    "sign_negative_fraction": float(sign_negative[index].item()),
                    "spectral_score": float(spectral[index].item()),
                    "norm_ratio": float(norm_ratio[index].item()),
                    "mean_shift_cluster": int(labels[index]),
                    "predicted_malicious": index not in retained_set,
                    "fallback_reason": self.last_fallback_reason,
                }
            )
        return aggregate, diagnostics

