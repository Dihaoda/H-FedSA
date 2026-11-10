import numpy as np
import torch
from torch.utils.data import TensorDataset

from src.data.datasets import (
    CIFAR10CorruptionDataset,
    ExternalShiftedSubset,
    MappedImageFolderDataset,
    _build_external_shift_dataset,
)


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


def test_external_shift_aligns_labels_when_pool_contains_them() -> None:
    base = TensorDataset(
        torch.arange(6, dtype=torch.float32)[:, None],
        torch.tensor([0, 1, 0, 1, 0, 1]),
    )
    shifted = TensorDataset(
        torch.ones(8, 1),
        torch.tensor([1, 1, 0, 0, 1, 0, 1, 0]),
    )
    mixed = ExternalShiftedSubset(base, list(range(6)), shifted, fraction=1.0, seed=9)

    assert [int(mixed[index][1]) for index in range(len(mixed))] == [0, 1, 0, 1, 0, 1]
    assert mixed.label_fallback_count == 0


def test_mapped_imagefolder_supports_explicit_cross_dataset_labels(tmp_path) -> None:
    from PIL import Image

    for class_name, value in (("speed_limit", 32), ("stop", 224)):
        class_dir = tmp_path / class_name
        class_dir.mkdir()
        Image.fromarray(np.full((8, 8, 3), value, dtype=np.uint8)).save(class_dir / "sample.png")
    config = {
        "enabled": True,
        "type": "imagefolder",
        "data_root": str(tmp_path),
        "label_map": {"speed_limit": 3, "stop": 14},
    }
    dataset = _build_external_shift_dataset(
        config,
        {"name": "gtsrb", "num_classes": 43, "image_size": 16},
    )

    assert isinstance(dataset, MappedImageFolderDataset)
    assert sorted(dataset.targets.tolist()) == [3, 14]
    image, label = dataset[0]
    assert tuple(image.shape) == (3, 16, 16)
    assert label in {3, 14}

