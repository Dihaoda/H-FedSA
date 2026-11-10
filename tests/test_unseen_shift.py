import torch
from torch.utils.data import TensorDataset

from src.data.datasets import ShiftedSubset


def _dataset(size: int = 10) -> TensorDataset:
    images = torch.zeros(size, 1, 2, 2)
    labels = torch.arange(size)
    return TensorDataset(images, labels)


def test_shift_fraction_changes_exact_deterministic_subset() -> None:
    config = {"type": "brightness", "brightness_delta": 1.0, "fraction": 0.4}
    first = ShiftedSubset(_dataset(), list(range(10)), config, seed=7)
    second = ShiftedSubset(_dataset(), list(range(10)), config, seed=7)

    assert first.shifted_source_indices == second.shifted_source_indices
    assert len(first.shifted_source_indices) == 4
    changed = [index for index in range(10) if torch.count_nonzero(first[index][0]).item() > 0]
    assert set(changed) == first.shifted_source_indices


def test_shift_fraction_is_clamped() -> None:
    none_shifted = ShiftedSubset(_dataset(), list(range(10)), {"type": "brightness", "fraction": -1}, seed=1)
    all_shifted = ShiftedSubset(_dataset(), list(range(10)), {"type": "brightness", "fraction": 2}, seed=1)

    assert not none_shifted.shifted_source_indices
    assert len(all_shifted.shifted_source_indices) == 10

