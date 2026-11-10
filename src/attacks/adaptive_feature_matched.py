from __future__ import annotations

from collections import OrderedDict

import numpy as np
import torch

from src.federated.tensor_ops import StateDict, flatten_update, unflatten_update


def apply_adaptive_feature_matched_attack(
    updates: list[tuple[int, StateDict]],
    root_update: StateDict,
    malicious_clients: set[int],
    client_roles: dict[int, str],
    config: dict,
    round_number: int,
) -> tuple[list[tuple[int, StateDict]], list[dict]]:
    """Approximate Algorithm-3 style feature-matched adaptive attack.

    The attack optimizes malicious update vectors so that their H-FedSA feature
    triplet moves toward the current unseen-cluster feature mean while starting
    from the negative root/server direction.
    """

    attack_cfg = config.get("attack", {}).get("adaptive", {})
    iterations = int(attack_cfg.get("iterations", 5))
    step_size = float(attack_cfg.get("step_size", 0.05))
    projection_strength = float(attack_cfg.get("projection_strength", 0.5))
    zeroth_order_sigma = float(attack_cfg.get("zeroth_order_sigma", 1e-3))
    seed = int(config.get("seed", 0)) + 7919 * int(round_number)
    generator = torch.Generator()
    generator.manual_seed(seed)
    root_flat = flatten_update(root_update)
    root_norm = torch.linalg.norm(root_flat).item()
    feature_by_client = {client_id: _features(flatten_update(update), root_flat, root_norm) for client_id, update in updates}
    unseen_features = [feature for client_id, feature in feature_by_client.items() if client_roles.get(client_id) == "unseen"]
    benign_features = [feature for client_id, feature in feature_by_client.items() if client_roles.get(client_id) == "benign"]
    if unseen_features:
        target_feature = np.mean(np.asarray(unseen_features, dtype=float), axis=0)
    elif benign_features:
        target_feature = np.mean(np.asarray(benign_features, dtype=float), axis=0)
    else:
        target_feature = np.zeros(3, dtype=float)

    attacked: list[tuple[int, StateDict]] = []
    traces: list[dict] = []
    for client_id, update in updates:
        if client_id not in malicious_clients:
            attacked.append((client_id, update))
            continue
        original_flat = flatten_update(update)
        start_flat = -root_flat.clone()
        if torch.linalg.norm(start_flat).item() <= 1e-12:
            start_flat = -original_flat.clone()
        optimized_flat, client_trace = _optimize_flat_update(
            start_flat=start_flat,
            reference_update=update,
            root_flat=root_flat,
            root_norm=root_norm,
            target_feature=target_feature,
            iterations=iterations,
            step_size=step_size,
            projection_strength=projection_strength,
            zeroth_order_sigma=zeroth_order_sigma,
            generator=generator,
            client_id=client_id,
            round_number=round_number,
        )
        attacked.append((client_id, unflatten_update(optimized_flat, update)))
        traces.extend(client_trace)
    return attacked, traces


def _optimize_flat_update(
    start_flat: torch.Tensor,
    reference_update: StateDict,
    root_flat: torch.Tensor,
    root_norm: float,
    target_feature: np.ndarray,
    iterations: int,
    step_size: float,
    projection_strength: float,
    zeroth_order_sigma: float,
    generator: torch.Generator,
    client_id: int,
    round_number: int,
) -> tuple[torch.Tensor, list[dict]]:
    current = start_flat.detach().float().cpu().clone()
    reference_norm = max(torch.linalg.norm(flatten_update(reference_update)).item(), 1e-8)
    traces = []
    for iteration in range(iterations + 1):
        before_feature = _features(current, root_flat, root_norm)
        objective = _objective(before_feature, target_feature)
        traces.append(
            {
                "round": round_number,
                "client_id": client_id,
                "iteration": iteration,
                "objective": objective,
                "f_dir": before_feature[0],
                "f_int": before_feature[1],
                "f_spa": before_feature[2],
                "target_f_dir": target_feature[0],
                "target_f_int": target_feature[1],
                "target_f_spa": target_feature[2],
            }
        )
        if iteration == iterations:
            break
        direction = torch.randn(current.shape, generator=generator, dtype=current.dtype)
        direction = direction / (torch.linalg.norm(direction) + 1e-12)
        plus = current + zeroth_order_sigma * direction
        minus = current - zeroth_order_sigma * direction
        grad_estimate = (
            _objective(_features(plus, root_flat, root_norm), target_feature)
            - _objective(_features(minus, root_flat, root_norm), target_feature)
        ) / max(2.0 * zeroth_order_sigma, 1e-12)
        current = current - step_size * float(grad_estimate) * direction
        current = _project_to_features(current, root_flat, root_norm, target_feature, reference_norm, projection_strength)
    return current, traces


def _project_to_features(
    flat: torch.Tensor,
    root_flat: torch.Tensor,
    root_norm: float,
    target_feature: np.ndarray,
    reference_norm: float,
    projection_strength: float,
) -> torch.Tensor:
    current = flat.detach().float().cpu().clone()
    target_intensity = float(target_feature[1])
    target_norm = max(root_norm * float(np.exp(target_intensity)), 1e-8)
    current_norm = torch.linalg.norm(current).item()
    if current_norm > 1e-12:
        current = current * ((1.0 - projection_strength) + projection_strength * target_norm / current_norm)

    if root_norm > 1e-12 and torch.linalg.norm(current).item() > 1e-12:
        target_cosine = float(np.clip(1.0 - target_feature[0], -0.99, 0.99))
        root_unit = root_flat / (torch.linalg.norm(root_flat) + 1e-12)
        orthogonal = current - torch.dot(current, root_unit) * root_unit
        orthogonal_norm = torch.linalg.norm(orthogonal)
        if orthogonal_norm <= 1e-12:
            orthogonal = torch.randn(current.shape, dtype=current.dtype)
            orthogonal = orthogonal - torch.dot(orthogonal, root_unit) * root_unit
            orthogonal_norm = torch.linalg.norm(orthogonal)
        orthogonal_unit = orthogonal / (orthogonal_norm + 1e-12)
        norm = torch.linalg.norm(current).item()
        projected = norm * (target_cosine * root_unit + float(np.sqrt(max(0.0, 1.0 - target_cosine**2))) * orthogonal_unit)
        current = (1.0 - projection_strength) * current + projection_strength * projected

    current_norm = torch.linalg.norm(current).item()
    if current_norm > 10.0 * reference_norm:
        current = current * (10.0 * reference_norm / current_norm)
    return current


def _features(flat: torch.Tensor, root_flat: torch.Tensor, root_norm: float) -> np.ndarray:
    flat = flat.detach().float().cpu()
    client_norm = torch.linalg.norm(flat).item()
    if client_norm <= 1e-12 or root_norm <= 1e-12:
        cosine = 0.0
    else:
        cosine = torch.nn.functional.cosine_similarity(root_flat, flat, dim=0).item()
    l1_norm = torch.linalg.norm(flat, ord=1).item()
    sparsity = l1_norm / (np.sqrt(float(flat.numel())) * client_norm + 1e-12)
    intensity = np.log((client_norm + 1e-12) / (root_norm + 1e-12))
    return np.nan_to_num(np.asarray([1.0 - cosine, intensity, sparsity], dtype=float), nan=0.0, posinf=0.0, neginf=0.0)


def _objective(feature: np.ndarray, target_feature: np.ndarray) -> float:
    diff = np.asarray(feature, dtype=float) - np.asarray(target_feature, dtype=float)
    return float(np.dot(diff, diff))
