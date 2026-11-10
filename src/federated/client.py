from __future__ import annotations

from collections import OrderedDict

import torch
from torch import nn
from torch.utils.data import DataLoader

from src.attacks.backdoor_scaling import poison_backdoor_batch
from src.attacks.poison import poison_labels, poison_update
from src.federated.tensor_ops import StateDict, state_dict_delta


class Client:
    def __init__(
        self,
        client_id: int | str,
        dataloader: DataLoader,
        model_factory,
        device: torch.device,
        num_classes: int,
        role: str = "benign",
    ) -> None:
        self.client_id = client_id
        self.dataloader = dataloader
        self.model_factory = model_factory
        self.device = device
        self.num_classes = num_classes
        self.role = role

    def train(
        self,
        global_state: StateDict,
        local_epochs: int,
        learning_rate: float,
        optimizer_name: str = "sgd",
        momentum: float = 0.9,
        weight_decay: float = 0.0,
        aggregate_bn_buffers: bool = True,
        attack_type: str = "none",
        scale_factor: float = 1.0,
        attack_cfg: dict | None = None,
        mixed_precision: bool = False,
    ) -> OrderedDict[str, torch.Tensor]:
        model = self.model_factory().to(self.device)
        model.load_state_dict(global_state)
        model.train()
        optimizer_name = optimizer_name.lower()
        if optimizer_name == "adam":
            optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        elif optimizer_name == "adamw":
            optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        else:
            optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum, weight_decay=weight_decay)
        criterion = nn.CrossEntropyLoss()
        use_amp = bool(mixed_precision and self.device.type == "cuda")
        scaler = torch.amp.GradScaler("cuda") if use_amp else None

        for _ in range(local_epochs):
            for features, labels in self.dataloader:
                features = features.to(self.device, non_blocking=True)
                labels = labels.to(self.device, non_blocking=True)
                if self.role == "malicious":
                    if attack_type == "backdoor_scaling":
                        features, labels = poison_backdoor_batch(features, labels, self.num_classes, attack_cfg)
                    else:
                        labels = poison_labels(labels, self.num_classes, attack_type)
                optimizer.zero_grad(set_to_none=True)
                if use_amp:
                    with torch.amp.autocast("cuda"):
                        loss = criterion(model(features), labels)
                    assert scaler is not None
                    scaler.scale(loss).backward()
                    scaler.step(optimizer)
                    scaler.update()
                    continue
                else:
                    loss = criterion(model(features), labels)
                loss.backward()
                optimizer.step()

        local_state = OrderedDict((name, tensor.detach().cpu()) for name, tensor in model.state_dict().items())
        cpu_global_state = OrderedDict((name, tensor.detach().cpu()) for name, tensor in global_state.items())
        update = state_dict_delta(local_state, cpu_global_state)
        if not aggregate_bn_buffers:
            update = _zero_batchnorm_buffer_updates(update)
        if self.role == "malicious":
            update = poison_update(update, attack_type, scale_factor)
        return update


def _zero_batchnorm_buffer_updates(update: OrderedDict[str, torch.Tensor]) -> OrderedDict[str, torch.Tensor]:
    return OrderedDict(
        (
            name,
            torch.zeros_like(tensor)
            if name.endswith(("running_mean", "running_var", "num_batches_tracked"))
            else tensor,
        )
        for name, tensor in update.items()
    )
