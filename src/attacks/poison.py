from __future__ import annotations

from collections import OrderedDict

import torch


def poison_labels(labels: torch.Tensor, num_classes: int, attack_type: str) -> torch.Tensor:
    attack_type = str(attack_type).lower()
    if attack_type not in {"label_flip", "label_flipping", "scaling"}:
        return labels
    return (num_classes - 1) - labels


def poison_update(update: OrderedDict[str, torch.Tensor], attack_type: str, scale_factor: float) -> OrderedDict[str, torch.Tensor]:
    attack_type = str(attack_type).lower()
    if attack_type not in {"scaling", "backdoor_scaling"}:
        return update
    return OrderedDict((name, tensor * scale_factor) for name, tensor in update.items())

