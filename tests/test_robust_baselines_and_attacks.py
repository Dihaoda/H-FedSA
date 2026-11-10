from collections import OrderedDict

import torch

from src.attacks.targeted_model_poisoning import apply_targeted_model_attack
from src.defenses.factory import build_defense
from src.federated.tensor_ops import flatten_update


def _update(values: list[float]):
    return OrderedDict(weight=torch.tensor(values, dtype=torch.float32))


def test_safefl_and_msguard_are_runnable_and_normalize_weights() -> None:
    updates = [
        (0, _update([1.0, 1.1, 0.9, 1.0])),
        (1, _update([0.9, 1.0, 1.1, 1.0])),
        (2, _update([1.1, 0.9, 1.0, 1.0])),
        (3, _update([-30.0, 30.0, -30.0, 30.0])),
    ]
    config = {
        "seed": 7,
        "safefl": {"rule": "signguard", "sign_fraction": 1.0},
        "msguard": {"min_retained_fraction": 0.5},
    }
    for name in ("safefl", "msguard"):
        defense = build_defense(name, config)
        aggregate, diagnostics = defense.aggregate(updates)
        assert torch.isfinite(flatten_update(aggregate)).all()
        assert len(diagnostics) == len(updates)
        assert abs(sum(float(item["weight"]) for item in diagnostics) - 1.0) < 1e-6
        assert all("predicted_malicious" in item for item in diagnostics)


def test_trim_targeted_is_deterministic_and_changes_only_malicious_updates() -> None:
    updates = [
        (0, _update([1.0, 2.0, 3.0])),
        (1, _update([1.1, 1.9, 3.1])),
        (2, _update([0.9, 2.1, 2.9])),
        (3, _update([1.2, 2.2, 3.2])),
    ]
    first, trace = apply_targeted_model_attack(updates, {0}, "trim_targeted", {}, 13, 2)
    second, _ = apply_targeted_model_attack(updates, {0}, "trim_targeted", {}, 13, 2)
    assert not torch.equal(flatten_update(first[0][1]), flatten_update(updates[0][1]))
    assert torch.equal(flatten_update(first[1][1]), flatten_update(updates[1][1]))
    assert torch.equal(flatten_update(first[0][1]), flatten_update(second[0][1]))
    assert trace[0]["target_rule"] == "coordinate_trimmed_mean"


def test_krum_targeted_returns_finite_attack_and_trace() -> None:
    updates = [
        (0, _update([1.0, 1.0, 1.0, 1.0])),
        (1, _update([1.1, 0.9, 1.0, 1.0])),
        (2, _update([0.9, 1.1, 1.0, 1.0])),
        (3, _update([1.0, 1.0, 0.9, 1.1])),
        (4, _update([1.0, 1.0, 1.1, 0.9])),
    ]
    attacked, trace = apply_targeted_model_attack(updates, {0}, "krum_targeted", {}, 3, 1)
    assert torch.isfinite(flatten_update(attacked[0][1])).all()
    assert torch.equal(flatten_update(attacked[1][1]), flatten_update(updates[1][1]))
    assert trace[0]["target_rule"] == "krum"
    assert float(trace[0]["lambda"]) > 0


def test_poisafl_distance_stage_caps_malicious_update_norm() -> None:
    updates = [
        (0, _update([100.0, 0.0])),
        (1, _update([1.0, 0.0])),
        (2, _update([0.0, 1.0])),
    ]
    attacked, trace = apply_targeted_model_attack(
        updates,
        {0},
        "poisafl",
        {"poisafl": {"distance_gamma": 0.8, "minimum_scale": 0.0}},
        5,
        1,
    )
    assert torch.linalg.norm(flatten_update(attacked[0][1])).item() <= 0.800001
    assert trace[0]["target_rule"] == "distance_aware_scaling"

