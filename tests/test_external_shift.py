import numpy as np
import torch
from torch.utils.data import TensorDataset

from src.data.datasets import CIFAR10CorruptionDataset, ExternalShiftedSubset


def test_external_shift_replaces_exact_fraction() -> None:
    base = TensorDataset(torch.zeros(10, 1), torch.zeros(10, dtype=torch.long))
    shifted = TensorDataset(torch.ones(20, 1), torch.ones(20, dtype=torch.long))
    mixed = ExternalShiftedSubset(base, list(range(10)), shifted, fraction=0.4, seed=5)

    labels = [int(mixed[index][1]) for index in range(len(mixed))]

    assert sum(labels) == 4
    assert len(mixed.shifted_source_indices) == 4


def test_cifar10_c_selects_requested_severity_block(tmp_path) -> None:
    root = tmp_path / "CIFAR-10-C"
    root.mkdir()
    images = np.arange(10 * 2 * 2 * 3, dtype=np.uint8).reshape(10, 2, 2, 3)
    np.save(root / "gaussian_noise.npy", images)
    np.save(root / "labels.npy", np.asarray([4, 7], dtype=np.int64))
    dataset = CIFAR10CorruptionDataset(
        root=tmp_path,
        corruptions=["gaussian_noise"],
        severity=3,
        transform=lambda image: np.asarray(image).copy(),
    )

    first_image, first_label = dataset[0]

    assert len(dataset) == 2
    np.testing.assert_array_equal(first_image, images[4])
    assert first_label == 4

