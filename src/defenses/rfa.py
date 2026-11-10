from __future__ import annotations

import torch

from src.federated.tensor_ops import StateDict, average_updates, flatten_update, unflatten_update


class RFA:
    name = "rfa"

    def __init__(self, max_iter: int = 20, tol: float = 1e-5, eps: float = 1e-8) -> None:
        self.max_iter = max_iter
        self.tol = tol
        self.eps = eps

    def aggregate(
        self,
        updates: list[tuple[int, StateDict]],
        root_update: StateDict | None = None,
        sample_counts: dict[int, int] | None = None,
        **_: object,
    ) -> tuple[StateDict, list[dict]]:
        if not updates:
            raise ValueError("RFA cannot aggregate an empty update list.")
        if len(updates) == 1:
            return updates[0][1], [{"client_id": updates[0][0], "weight": 1.0}]

        flats = torch.stack([flatten_update(update) for _, update in updates])
        median = flats.mean(dim=0)
        weights = torch.full((len(updates),), 1.0 / len(updates))

        for _ in range(self.max_iter):
            distances = torch.linalg.norm(flats - median, dim=1).clamp_min(self.eps)
            weights = 1.0 / distances
            weights = weights / weights.sum()
            next_median = torch.sum(flats * weights[:, None], dim=0)
            shift = torch.linalg.norm(next_median - median).item()
            median = next_median
            if shift < self.tol:
                break

        diagnostics = [
            {"client_id": client_id, "weight": float(weights[idx].item())}
            for idx, (client_id, _) in enumerate(updates)
        ]
        return unflatten_update(median, updates[0][1]), diagnostics
