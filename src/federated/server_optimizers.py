from __future__ import annotations

from collections import OrderedDict

import torch

from src.federated.tensor_ops import StateDict, flatten_update, zeros_like_update


class ServerOptimizer:
    name = "fedavg"

    def step(self, aggregated_delta: StateDict) -> tuple[StateDict, dict]:
        raise NotImplementedError


class FedAvgServerOptimizer(ServerOptimizer):
    name = "fedavg"

    def __init__(self, server_lr: float = 1.0) -> None:
        self.server_lr = float(server_lr)

    def step(self, aggregated_delta: StateDict) -> tuple[StateDict, dict]:
        update = _scale_update(aggregated_delta, self.server_lr)
        return _sanitize_update(update, self.name, self.server_lr)


class FedAvgMServerOptimizer(ServerOptimizer):
    name = "fedavgm"

    def __init__(self, reference: StateDict, server_lr: float = 1.0, momentum: float = 0.9) -> None:
        self.server_lr = float(server_lr)
        self.momentum = float(momentum)
        self.velocity = zeros_like_update(reference)

    def step(self, aggregated_delta: StateDict) -> tuple[StateDict, dict]:
        for name, tensor in aggregated_delta.items():
            if torch.is_floating_point(tensor):
                self.velocity[name] = self.momentum * self.velocity[name] + tensor
        update = _scale_update(self.velocity, self.server_lr)
        sanitized, summary = _sanitize_update(update, self.name, self.server_lr)
        summary["server_momentum"] = self.momentum
        summary["velocity_norm"] = _safe_norm(self.velocity)
        summary["momentum_buffer_norm"] = summary["velocity_norm"]
        return sanitized, summary


class FedAdamServerOptimizer(ServerOptimizer):
    name = "fedadam"

    def __init__(
        self,
        reference: StateDict,
        server_lr: float = 0.001,
        beta1: float = 0.9,
        beta2: float = 0.99,
        eps: float = 1e-8,
    ) -> None:
        self.server_lr = float(server_lr)
        self.beta1 = float(beta1)
        self.beta2 = float(beta2)
        self.eps = float(eps)
        self.t = 0
        self.m = zeros_like_update(reference)
        self.v = zeros_like_update(reference)

    def step(self, aggregated_delta: StateDict) -> tuple[StateDict, dict]:
        self.t += 1
        update = OrderedDict()
        for name, tensor in aggregated_delta.items():
            if not torch.is_floating_point(tensor):
                update[name] = torch.zeros_like(tensor)
                continue
            self.m[name] = self.beta1 * self.m[name] + (1.0 - self.beta1) * tensor
            self.v[name] = self.beta2 * self.v[name] + (1.0 - self.beta2) * tensor.pow(2)
            m_hat = self.m[name] / (1.0 - self.beta1**self.t)
            v_hat = self.v[name] / (1.0 - self.beta2**self.t)
            update[name] = self.server_lr * m_hat / (torch.sqrt(v_hat) + self.eps)
        sanitized, summary = _sanitize_update(update, self.name, self.server_lr)
        summary.update(
            {
                "server_beta1": self.beta1,
                "server_beta2": self.beta2,
                "server_eps": self.eps,
                "server_step": self.t,
                "first_moment_norm": _safe_norm(self.m),
                "second_moment_norm": _safe_norm(self.v),
            }
        )
        return sanitized, summary


def build_server_optimizer(config: dict, reference_state: StateDict) -> ServerOptimizer:
    fed_cfg = config.get("federated", {})
    name = str(fed_cfg.get("server_optimizer", "fedavg")).lower()
    legacy_lr = float(fed_cfg.get("server_learning_rate", 1.0))
    server_lr = float(fed_cfg.get("server_lr", legacy_lr))
    if name == "fedavg":
        return FedAvgServerOptimizer(server_lr=server_lr)
    if name == "fedavgm":
        return FedAvgMServerOptimizer(
            reference=reference_state,
            server_lr=server_lr,
            momentum=float(fed_cfg.get("server_momentum", 0.9)),
        )
    if name == "fedadam":
        return FedAdamServerOptimizer(
            reference=reference_state,
            server_lr=server_lr,
            beta1=float(fed_cfg.get("server_beta1", 0.9)),
            beta2=float(fed_cfg.get("server_beta2", 0.99)),
            eps=float(fed_cfg.get("server_eps", 1e-8)),
        )
    raise ValueError(f"Unsupported server_optimizer: {name}")


def _scale_update(update: StateDict, scale: float) -> StateDict:
    return OrderedDict(
        (
            name,
            tensor * float(scale) if torch.is_floating_point(tensor) else torch.zeros_like(tensor),
        )
        for name, tensor in update.items()
    )


def _sanitize_update(update: StateDict, optimizer_name: str, server_lr: float) -> tuple[StateDict, dict]:
    nan_flag = False
    inf_flag = False
    sanitized = OrderedDict()
    for name, tensor in update.items():
        if torch.is_floating_point(tensor):
            nan_flag = nan_flag or bool(torch.isnan(tensor).any().item())
            inf_flag = inf_flag or bool(torch.isinf(tensor).any().item())
            sanitized[name] = torch.nan_to_num(tensor, nan=0.0, posinf=0.0, neginf=0.0)
        else:
            sanitized[name] = torch.zeros_like(tensor)
    summary = {
        "server_optimizer": optimizer_name,
        "server_lr": float(server_lr),
        "server_update_norm": _safe_norm(sanitized),
        "server_nan_flag": nan_flag,
        "server_inf_flag": inf_flag,
    }
    return sanitized, summary


def _safe_norm(update: StateDict) -> float:
    return float(torch.linalg.norm(flatten_update(update)).item())
