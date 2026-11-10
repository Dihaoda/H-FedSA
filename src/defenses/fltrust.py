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
        if not updates:
            raise ValueError("FLTrust cannot aggregate an empty update list.")
        root_flat = flatten_update(root_update)
        root_norm = torch.linalg.norm(root_flat).item()
        if root_norm <= 1e-12:
            uniform = 1.0 / len(updates)
            diagnostics = [
                {
                    "client_id": client_id,
                    "trust_score": 0.0,
                    "cosine_similarity": 0.0,
                    "client_update_norm": float(torch.linalg.norm(flatten_update(update)).item()),
                    "root_update_norm": root_norm,
                    "update_scale": 1.0,
                    "scaled_update_norm": float(torch.linalg.norm(flatten_update(update)).item()),
                    "weight": uniform,
                    "predicted_malicious": False,
                    "fallback_reason": "zero_root_update",
                }
                for client_id, update in updates
            ]
            return average_updates([update for _, update in updates]), diagnostics

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
                    "weight": 0.0,
                    "predicted_malicious": cos <= 0.0,
                    "fallback_reason": "",
                }
            )
            if trust > 0.0:
                scaled_update = {name: tensor * scale for name, tensor in update.items()}
                weighted_updates.append(scaled_update)
                weights.append(trust)

        if not weighted_updates or sum(weights) <= 0:
            uniform = 1.0 / len(updates)
            for item in diagnostics:
                item["weight"] = uniform
                item["fallback_reason"] = "no_positive_trust_scores"
            return average_updates([update for _, update in updates]), diagnostics
        normalizer = sum(weights)
        for item in diagnostics:
            item["weight"] = float(item["trust_score"]) / normalizer
        return average_updates(weighted_updates, [w / normalizer for w in weights]), diagnostics

