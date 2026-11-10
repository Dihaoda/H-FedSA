from __future__ import annotations


class ExplorationPolicy:
    """Interface for future adaptive beta_explore policies."""

    def select_beta(self, round_idx: int, state: dict | None = None) -> float:
        raise NotImplementedError

    def update(self, transition: dict) -> None:
        raise NotImplementedError


class StaticExplorationPolicy(ExplorationPolicy):
    def __init__(self, beta_explore: float) -> None:
        self.beta_explore = beta_explore

    def select_beta(self, round_idx: int, state: dict | None = None) -> float:
        return self.beta_explore

    def update(self, transition: dict) -> None:
        return None
