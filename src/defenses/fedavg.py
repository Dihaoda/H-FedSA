from __future__ import annotations

import torch

from src.federated.tensor_ops import StateDict, average_updates, flatten_update


class FedAvg:
    name = "fedavg"

    def __init__(self, aggregation_weighting: str = "uniform") -> None:
        weighting = str(aggregation_weighting).lower()
        if weighting not in {"uniform", "sample_count"}:
            raise ValueError(f"Unsupported FedAvg aggregation_weighting: {aggregation_weighting}")
        self.aggregation_weighting = weighting

    def aggregate(
        self,
        updates: list[tuple[int, StateDict]],
        root_update: StateDict | None = None,
        sample_counts: dict[int, int] | None = None,
        **_: object,
    ) -> tuple[StateDict, list[dict]]:
        if not updates:
            raise ValueError("FedAvg cannot aggregate an empty update list.")
        update_values = [update for _, update in updates]
        weights = self._weights(updates, sample_counts)
        diagnostics = [
            {
                "client_id": client_id,
                "weight": float(weights[idx]),
                "num_samples": int(sample_counts.get(client_id, 0)) if sample_counts else "NA",
                "update_norm": float(torch.linalg.norm(flatten_update(update)).item()),
                "aggregation_weighting": self.aggregation_weighting,
            }
            for idx, (client_id, update) in enumerate(updates)
        ]
        return average_updates(update_values, weights), diagnostics

    def _weights(self, updates: list[tuple[int, StateDict]], sample_counts: dict[int, int] | None) -> list[float]:
        if self.aggregation_weighting == "sample_count" and sample_counts:
            counts = [max(int(sample_counts.get(client_id, 0)), 0) for client_id, _ in updates]
            total = float(sum(counts))
            if total > 0:
                return [count / total for count in counts]
        return [1.0 / len(updates)] * len(updates)
