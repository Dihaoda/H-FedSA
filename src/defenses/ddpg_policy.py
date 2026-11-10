from __future__ import annotations

from abc import ABC, abstractmethod


class ExplorationPolicy(ABC):
    """Interface for future adaptive beta_explore policies."""

    @abstractmethod
    def select_beta(self, round_idx: int, state: dict | None = None) -> float:
        """Return the exploration weight for the current round."""

    @abstractmethod
    def update(self, transition: dict) -> None:
        """Consume an optional policy transition."""


class StaticExplorationPolicy(ExplorationPolicy):
    def __init__(self, beta_explore: float) -> None:
        self.beta_explore = beta_explore

    def select_beta(self, round_idx: int, state: dict | None = None) -> float:
        return self.beta_explore

    def update(self, transition: dict) -> None:
        return None

