from __future__ import annotations

import math

import numpy as np
import torch

from src.federated.tensor_ops import StateDict, flatten_update, unflatten_update


TARGETED_MODEL_ATTACKS = {"krum_targeted", "trim_targeted", "poisafl"}


def apply_targeted_model_attack(
    updates: list[tuple[int, StateDict]],
    malicious_clients: set[int],
    attack_type: str,
    attack_cfg: dict,
    seed: int,
    round_number: int,
) -> tuple[list[tuple[int, StateDict]], list[dict]]:
    """Apply a round-level model poisoning attack after local training.

    Krum- and Trim-targeted attacks follow the attacks distributed by the
    SafeFL authors (which in turn cite Fang et al.). PoiSAFL applies the
    distance-aware scaling stage after its local anti-training/distillation
    stages have produced malicious updates.
    """

    key = str(attack_type).lower()
    if key not in TARGETED_MODEL_ATTACKS:
        return updates, []
    malicious_indices = [index for index, (client_id, _) in enumerate(updates) if client_id in malicious_clients]
    if not malicious_indices:
        return updates, []
    flats = torch.stack([flatten_update(update) for _, update in updates]).float()
    if key == "trim_targeted":
        attacked, metadata = _trim_targeted(flats, malicious_indices, seed + 7919 * round_number)
    elif key == "krum_targeted":
        attacked, metadata = _krum_targeted(flats, malicious_indices, attack_cfg.get("krum_targeted", {}))
    else:
        attacked, metadata = _poisafl_distance_scale(flats, malicious_indices, attack_cfg.get("poisafl", {}))

    result: list[tuple[int, StateDict]] = []
    traces: list[dict] = []
    malicious_index_set = set(malicious_indices)
    for index, (client_id, reference) in enumerate(updates):
        result.append((client_id, unflatten_update(attacked[index], reference)))
        if index in malicious_index_set:
            traces.append(
                {
                    "round": int(round_number),
                    "client_id": int(client_id),
                    "attack_type": key,
                    "original_norm": float(torch.linalg.norm(flats[index]).item()),
                    "attacked_norm": float(torch.linalg.norm(attacked[index]).item()),
                    **metadata,
                }
            )
    return result, traces


def _trim_targeted(
    flats: torch.Tensor,
    malicious_indices: list[int],
    seed: int,
) -> tuple[torch.Tensor, dict]:
    attacked = flats.clone()
    coordinate_max = torch.max(flats, dim=0).values
    coordinate_min = torch.min(flats, dim=0).values
    direction = torch.sign(torch.sum(flats, dim=0))
    directed = torch.where(direction > 0, coordinate_min, coordinate_max)
    directed = torch.where(direction == 0, -torch.mean(flats, dim=0), directed)
    generator = torch.Generator(device="cpu")
    generator.manual_seed(int(seed))
    for index in malicious_indices:
        random_factor = 1.0 + torch.rand(directed.shape, generator=generator)
        same_sign = direction * directed > 0
        candidate = torch.where(same_sign, directed / random_factor, directed * random_factor)
        attacked[index] = candidate
    return attacked, {"target_rule": "coordinate_trimmed_mean"}


def _krum_scores(flats: torch.Tensor, byzantine_count: int) -> torch.Tensor:
    count = int(flats.shape[0])
    neighbor_count = max(1, count - int(byzantine_count) - 2)
    distances = torch.cdist(flats, flats, p=2).square()
    distances.fill_diagonal_(float("inf"))
    nearest = torch.topk(distances, k=min(neighbor_count, count - 1), largest=False, dim=1).values
    return nearest.sum(dim=1)


def _krum_targeted(
    flats: torch.Tensor,
    malicious_indices: list[int],
    config: dict,
) -> tuple[torch.Tensor, dict]:
    attacked = flats.clone()
    count, dimension = int(flats.shape[0]), int(flats.shape[1])
    malicious_set = set(malicious_indices)
    benign_indices = [index for index in range(count) if index not in malicious_set]
    if not benign_indices:
        return -attacked, {"target_rule": "krum", "lambda": 1.0, "krum_selected_malicious": True}

    benign = flats[benign_indices]
    reference = benign.mean(dim=0)
    reference_scores = _krum_scores(flats, len(malicious_indices))
    update_before = flats[int(torch.argmin(reference_scores).item())]
    sign_direction = torch.sign(update_before)
    sign_direction[sign_direction == 0] = torch.sign(reference[sign_direction == 0])
    sign_direction[sign_direction == 0] = 1.0

    benign_distances = torch.cdist(benign, benign, p=2)
    neighbor_count = max(1, count - len(malicious_indices) - 2)
    if len(benign_indices) > 1:
        benign_distances.fill_diagonal_(float("inf"))
        nearest = torch.topk(
            benign_distances,
            k=min(neighbor_count, len(benign_indices) - 1),
            largest=False,
            dim=1,
        ).values
        minimum_benign_score = float(nearest.sum(dim=1).min().item())
    else:
        minimum_benign_score = float(torch.linalg.norm(reference).item())
    denominator = max((count - 2 * len(malicious_indices) - 1) * math.sqrt(max(dimension, 1)), 1.0)
    high = minimum_benign_score / denominator + float(torch.linalg.norm(benign, dim=1).max().item()) / math.sqrt(
        max(dimension, 1)
    )
    high *= float(config.get("lambda_multiplier", 1.0))
    high = max(high, float(config.get("minimum_lambda", 1e-5)))
    threshold = float(config.get("search_threshold", 1e-5))
    maximum_steps = int(config.get("max_search_steps", 32))

    selected_malicious = False
    actual_lambda = high
    candidate = -actual_lambda * sign_direction
    for _ in range(maximum_steps):
        candidate = -actual_lambda * sign_direction
        trial = flats.clone()
        for index in malicious_indices:
            trial[index] = candidate
        selected = int(torch.argmin(_krum_scores(trial, len(malicious_indices))).item())
        if selected in malicious_set:
            selected_malicious = True
            attacked = trial
            break
        actual_lambda *= 0.5
        if actual_lambda <= threshold:
            break
    if not selected_malicious:
        for index in malicious_indices:
            attacked[index] = candidate
    return attacked, {
        "target_rule": "krum",
        "lambda": float(actual_lambda),
        "krum_selected_malicious": bool(selected_malicious),
    }


def _poisafl_distance_scale(
    flats: torch.Tensor,
    malicious_indices: list[int],
    config: dict,
) -> tuple[torch.Tensor, dict]:
    attacked = flats.clone()
    malicious_set = set(malicious_indices)
    benign_indices = [index for index in range(len(flats)) if index not in malicious_set]
    if benign_indices:
        benign_norms = torch.linalg.norm(flats[benign_indices], dim=1)
        reference_distance = float(torch.median(benign_norms).item())
    else:
        reference_distance = float(torch.median(torch.linalg.norm(flats, dim=1)).item())
    gamma = float(np.clip(float(config.get("distance_gamma", 0.8)), 1e-6, 1.0))
    distance_limit = max(gamma * reference_distance, 1e-12)
    minimum_scale = float(np.clip(float(config.get("minimum_scale", 0.05)), 0.0, 1.0))
    scales = []
    for index in malicious_indices:
        norm = float(torch.linalg.norm(attacked[index]).item())
        scale = min(1.0, distance_limit / max(norm, 1e-12))
        scale = max(scale, minimum_scale)
        attacked[index] *= scale
        scales.append(scale)
    return attacked, {
        "target_rule": "distance_aware_scaling",
        "distance_reference": float(reference_distance),
        "distance_limit": float(distance_limit),
        "applied_scale": float(np.mean(scales)) if scales else 1.0,
    }

