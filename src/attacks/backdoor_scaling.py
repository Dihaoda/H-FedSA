from __future__ import annotations

import torch


def apply_trigger(features: torch.Tensor, trigger_cfg: dict | None = None) -> torch.Tensor:
    cfg = trigger_cfg or {}
    size = int(cfg.get("size", 4))
    value = float(cfg.get("value", 2.5))
    location = str(cfg.get("location", "bottom_right")).lower()
    poisoned = features.clone()
    _, _, height, width = poisoned.shape
    size = max(1, min(size, height, width))
    if location == "top_left":
        y0, x0 = 0, 0
    elif location == "top_right":
        y0, x0 = 0, width - size
    elif location == "bottom_left":
        y0, x0 = height - size, 0
    else:
        y0, x0 = height - size, width - size
    poisoned[:, :, y0 : y0 + size, x0 : x0 + size] = value
    return poisoned


def poison_backdoor_batch(
    features: torch.Tensor,
    labels: torch.Tensor,
    num_classes: int,
    attack_cfg: dict | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    cfg = attack_cfg or {}
    target_label = int(cfg.get("target_label", 0)) % int(num_classes)
    poison_fraction = float(cfg.get("poison_fraction", 1.0))
    poison_fraction = min(max(poison_fraction, 0.0), 1.0)
    if poison_fraction <= 0.0 or labels.numel() == 0:
        return features, labels
    count = max(1, int(round(labels.numel() * poison_fraction)))
    poisoned_features = features.clone()
    poisoned_labels = labels.clone()
    selected = torch.arange(labels.numel(), device=labels.device)[:count]
    poisoned_features[selected] = apply_trigger(poisoned_features[selected], cfg.get("trigger", {}))
    poisoned_labels[selected] = target_label
    return poisoned_features, poisoned_labels
