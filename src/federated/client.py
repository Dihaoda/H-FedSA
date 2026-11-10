from __future__ import annotations

from collections import OrderedDict

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
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
        optimizer = _build_optimizer(model, optimizer_name, learning_rate, momentum, weight_decay)
        criterion = nn.CrossEntropyLoss()
        use_amp = bool(mixed_precision and self.device.type == "cuda")
        scaler = torch.amp.GradScaler("cuda") if use_amp else None

        if self.role == "malicious" and attack_type == "poisafl":
            _train_poisafl_student(
                student=model,
                model_factory=self.model_factory,
                global_state=global_state,
                dataloader=self.dataloader,
                device=self.device,
                local_epochs=local_epochs,
                learning_rate=learning_rate,
                optimizer_name=optimizer_name,
                momentum=momentum,
                weight_decay=weight_decay,
                attack_cfg=attack_cfg or {},
            )
        else:
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


def _build_optimizer(
    model: nn.Module,
    optimizer_name: str,
    learning_rate: float,
    momentum: float,
    weight_decay: float,
):
    if optimizer_name == "adam":
        return torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    if optimizer_name == "adamw":
        return torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    return torch.optim.SGD(
        model.parameters(),
        lr=learning_rate,
        momentum=momentum,
        weight_decay=weight_decay,
    )


def _train_poisafl_student(
    student: nn.Module,
    model_factory,
    global_state: StateDict,
    dataloader: DataLoader,
    device: torch.device,
    local_epochs: int,
    learning_rate: float,
    optimizer_name: str,
    momentum: float,
    weight_decay: float,
    attack_cfg: dict,
) -> None:
    """Synchronous PoiSAFL adaptation: anti-train a teacher, then distill.

    PoiSAFL was proposed for semi-asynchronous FL. This local stage preserves
    its anti-training and loss-aware distillation objectives; the trainer adds
    the distance-aware scaling stage after collecting the round's updates.
    """

    poisafl_cfg = attack_cfg.get("poisafl", {})
    teacher = model_factory().to(device)
    teacher.load_state_dict(global_state)
    teacher.train()
    anti_optimizer = _build_optimizer(
        teacher,
        optimizer_name,
        float(poisafl_cfg.get("anti_learning_rate", learning_rate)),
        momentum,
        weight_decay,
    )
    anti_epochs = max(1, int(poisafl_cfg.get("anti_epochs", 1)))
    epsilon = float(poisafl_cfg.get("probability_epsilon", 1e-6))
    for _ in range(anti_epochs):
        for features, labels in dataloader:
            features = features.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            anti_optimizer.zero_grad(set_to_none=True)
            probabilities = torch.softmax(teacher(features), dim=1)
            correct_probability = probabilities.gather(1, labels[:, None]).squeeze(1)
            anti_loss = -torch.log((1.0 - correct_probability).clamp_min(epsilon)).mean()
            anti_loss.backward()
            anti_optimizer.step()

    teacher.eval()
    for parameter in teacher.parameters():
        parameter.requires_grad_(False)
    student.train()
    student_optimizer = _build_optimizer(student, optimizer_name, learning_rate, momentum, weight_decay)
    alpha = float(np.clip(float(poisafl_cfg.get("alpha", 0.7)), 0.0, 1.0))
    temperature = max(float(poisafl_cfg.get("temperature", 2.0)), 1e-6)
    criterion = nn.CrossEntropyLoss()
    for _ in range(local_epochs):
        for features, labels in dataloader:
            features = features.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            student_optimizer.zero_grad(set_to_none=True)
            with torch.no_grad():
                teacher_logits = teacher(features)
            student_logits = student(features)
            supervised_loss = criterion(student_logits, labels)
            distillation_loss = F.kl_div(
                F.log_softmax(student_logits / temperature, dim=1),
                F.softmax(teacher_logits / temperature, dim=1),
                reduction="batchmean",
            ) * (temperature**2)
            loss = alpha * supervised_loss + (1.0 - alpha) * distillation_loss
            loss.backward()
            student_optimizer.step()

