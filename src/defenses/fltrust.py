from __future__ import annotations

import torch

from src.federated.tensor_ops import StateDict, average_updates, flatten_update


class FLTrust:
    name = "fltrust"

    def __init__(self, min_trust_score: float = 0.0) -> None:
        self.min_trust_score = min_trust_score

    def aggregate(
        self,
        updates: list[tuple[int, StateDict]],
        root_update: StateDict | None = None,
        sample_counts: dict[int, int] | None = None,
        **_: object,
    ) -> tuple[StateDict, list[dict]]:
        if root_update is None:
            raise ValueError("FLTrust requires a trusted root update.")
        root_flat = flatten_update(root_update)
        root_norm = torch.linalg.norm(root_flat).item()
        if root_norm <= 1e-12:
            return average_updates([update for _, update in updates]), []

        weighted_updates = []
        weights = []
        diagnostics = []
        for client_id, update in updates:
            client_flat = flatten_update(update)
            client_norm = torch.linalg.norm(client_flat).item()
            cos = 0.0 if client_norm <= 1e-12 else torch.nn.functional.cosine_similarity(root_flat, client_flat, dim=0).item()
            trust = max(cos, self.min_trust_score, 0.0)
            scale = root_norm / (client_norm + 1e-12) if client_norm > 1e-12 else 1.0
            diagnostics.append(
                {
                    "client_id": client_id,
                    "trust_score": trust,
                    "cosine_similarity": cos,
                    "client_update_norm": client_norm,
                    "root_update_norm": root_norm,
                    "update_scale": scale,
                    "scaled_update_norm": client_norm * scale,
                    "weight": trust,
                }
            )
            if trust > 0.0:
                scaled_update = {name: tensor * scale for name, tensor in update.items()}
                weighted_updates.append(scaled_update)
                weights.append(trust)

        if not weighted_updates or sum(weights) <= 0:
            return average_updates([update for _, update in updates]), diagnostics
        normalizer = sum(weights)
        return average_updates(weighted_updates, [w / normalizer for w in weights]), diagnostics
