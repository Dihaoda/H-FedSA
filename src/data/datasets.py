from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from collections import Counter
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset, Subset, TensorDataset


@dataclass
class FederatedData:
    client_loaders: list[DataLoader]
    root_loader: DataLoader
    train_eval_loader: DataLoader
    test_loader: DataLoader
    client_roles: dict[int, str]
    malicious_clients: set[int]
    unseen_clients: set[int]
    num_classes: int
    input_shape: tuple[int, int, int]
    dataset_source: str
    metadata: dict


class ShiftedSubset(Dataset):
    """Subset wrapper for deterministic unseen-client perturbations."""

    def __init__(self, dataset: Dataset, indices: list[int], shift_cfg: dict, seed: int) -> None:
        self.dataset = dataset
        self.indices = list(indices)
        self.shift_type = str(shift_cfg.get("type", "gaussian_noise"))
        self.noise_std = float(shift_cfg.get("noise_std", 0.15))
        self.brightness_delta = float(shift_cfg.get("brightness_delta", 0.10))
        self.seed = int(seed)

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, item: int):
        source_index = int(self.indices[item])
        image, label = self.dataset[source_index]
        if self.shift_type in {"none", "off"}:
            return image, label
        if self.shift_type == "gaussian_noise":
            generator = torch.Generator()
            generator.manual_seed(self.seed + source_index)
            noise = torch.randn(image.shape, generator=generator, dtype=image.dtype) * self.noise_std
            return image + noise, label
        if self.shift_type == "brightness":
            return image + self.brightness_delta, label
        if self.shift_type == "gaussian_noise_brightness":
            generator = torch.Generator()
            generator.manual_seed(self.seed + source_index)
            noise = torch.randn(image.shape, generator=generator, dtype=image.dtype) * self.noise_std
            return image + noise + self.brightness_delta, label
        return image, label


class CachedTensorDataset(Dataset):
    """Materialized tensor view for repeated FL passes over image datasets."""

    def __init__(self, dataset: Dataset, num_classes: int | None = None) -> None:
        images = []
        labels = []
        for index in range(len(dataset)):
            image, label = dataset[index]
            images.append(image.detach().clone() if torch.is_tensor(image) else torch.as_tensor(image))
            labels.append(int(label))
        self.tensors = torch.stack(images)
        self.targets = torch.tensor(labels, dtype=torch.long)
        self.dataset_variant = f"{getattr(dataset, 'dataset_variant', dataset.__class__.__name__)}_cached_tensors"
        self.source_repository = getattr(dataset, "source_repository", "unknown")
        self.transform_description = f"Cached tensors from: {getattr(dataset, 'transform_description', 'unknown transform')}"
        self.num_classes = int(num_classes) if num_classes is not None else len(set(labels))

    def __len__(self) -> int:
        return int(self.targets.numel())

    def __getitem__(self, item: int):
        return self.tensors[int(item)], int(self.targets[int(item)])


class FEMNISTHFDataset(Dataset):
    """PyTorch view over writer-partitioned LEAF FEMNIST from Hugging Face."""

    def __init__(self, dataset, indices: list[int], transform, writer_ids: list[str], targets: list[int], split_name: str) -> None:
        self.dataset = dataset
        self.indices = [int(index) for index in indices]
        self.transform = transform
        self.writer_ids = [str(writer_ids[index]) for index in self.indices]
        self.targets = np.asarray([int(targets[index]) for index in self.indices], dtype=np.int64)
        self.writer_to_indices: dict[str, list[int]] = {}
        for local_index, writer_id in enumerate(self.writer_ids):
            self.writer_to_indices.setdefault(writer_id, []).append(local_index)
        self.dataset_variant = "leaf_femnist_huggingface"
        self.split_name = split_name
        self.transform_description = "ToTensor + Normalize(mean=(0.5,), std=(0.5,))"

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, item: int):
        row = self.dataset[self.indices[int(item)]]
        image = row["image"].convert("L")
        return self.transform(image), int(row["character"])


class HFImageClassificationDataset(Dataset):
    """PyTorch view over Hugging Face image-classification datasets."""

    def __init__(self, dataset, transform, label_column: str = "label", variant: str = "huggingface_image_dataset") -> None:
        self.dataset = dataset
        self.transform = transform
        self.label_column = str(label_column)
        self.targets = np.asarray([int(value) for value in dataset[self.label_column]], dtype=np.int64)
        self.dataset_variant = variant
        self.source_repository = "huggingface"
        self.transform_description = "PIL RGB + configured torchvision transforms"

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, item: int):
        row = self.dataset[int(item)]
        image = row["image"].convert("RGB")
        return self.transform(image), int(row[self.label_column])


def build_federated_data(config: dict) -> FederatedData:
    dataset_cfg = config["dataset"]
    fed_cfg = config["federated"]
    seed = int(config["seed"])
    rng = np.random.default_rng(seed)

    train_dataset, test_dataset, num_classes, source = _load_dataset(dataset_cfg, fed_cfg, rng, seed)
    iid = bool(fed_cfg.get("iid", False))
    partition_method = str(fed_cfg.get("partition_method", "")).lower()
    if partition_method in {"writer", "natural_writer"} and hasattr(train_dataset, "writer_to_indices"):
        client_indices, root_indices = _partition_clients_by_writer(
            train_dataset=train_dataset,
            num_clients=int(fed_cfg["num_clients"]),
            root_size=int(fed_cfg["root_size"]),
            seed=seed,
        )
        iid = False
    else:
        client_indices, root_indices = _partition_clients(
            train_dataset=train_dataset,
            num_clients=int(fed_cfg["num_clients"]),
            root_size=int(fed_cfg["root_size"]),
            seed=seed,
            iid=iid,
            num_classes=num_classes,
            alpha=fed_cfg.get("non_iid_alpha", "NA"),
            min_client_samples=int(fed_cfg.get("min_client_samples", 1)),
        )

    unseen_count = int(round(int(fed_cfg["num_clients"]) * float(fed_cfg["unseen_ratio"])))
    malicious_count = int(round(int(fed_cfg["num_clients"]) * float(fed_cfg["malicious_ratio"])))
    unseen_clients = set(range(unseen_count))
    malicious_clients = set(range(unseen_count, unseen_count + malicious_count))

    client_roles = {}
    for client_id in range(len(client_indices)):
        if client_id in malicious_clients:
            client_roles[client_id] = "malicious"
        elif client_id in unseen_clients:
            client_roles[client_id] = "unseen"
        else:
            client_roles[client_id] = "benign"

    batch_size = int(fed_cfg["batch_size"])
    unseen_shift_cfg = fed_cfg.get("unseen_shift", {})
    if bool(unseen_shift_cfg.get("enabled", False)):
        unseen_shift_type = str(unseen_shift_cfg.get("type", "gaussian_noise"))
    else:
        unseen_shift_type = "none"
    client_datasets = []
    for client_id, indices in enumerate(client_indices):
        if client_id in unseen_clients and unseen_shift_type != "none":
            client_datasets.append(ShiftedSubset(train_dataset, indices, unseen_shift_cfg, seed + 1000 * (client_id + 1)))
        else:
            client_datasets.append(Subset(train_dataset, indices))
    client_loader_kwargs = _loader_kwargs(fed_cfg, prefix="client")
    eval_loader_kwargs = _loader_kwargs(fed_cfg, prefix="eval")
    client_loaders = [
        DataLoader(dataset, batch_size=batch_size, shuffle=True, **client_loader_kwargs)
        for dataset in client_datasets
    ]
    root_loader = DataLoader(Subset(train_dataset, root_indices), batch_size=batch_size, shuffle=bool(root_indices), **client_loader_kwargs)
    train_eval_size = int(dataset_cfg.get("train_eval_subset", min(len(train_dataset), 2000)))
    train_eval_indices = list(range(min(train_eval_size, len(train_dataset))))
    train_eval_loader = DataLoader(Subset(train_dataset, train_eval_indices), batch_size=batch_size * 2, shuffle=False, **eval_loader_kwargs)
    test_loader = DataLoader(test_dataset, batch_size=batch_size * 2, shuffle=False, **eval_loader_kwargs)
    metadata = _build_metadata(
        train_dataset=train_dataset,
        test_dataset=test_dataset,
        client_indices=client_indices,
        root_indices=root_indices,
        train_eval_indices=train_eval_indices,
        num_classes=num_classes,
        dataset_cfg=dataset_cfg,
        fed_cfg=fed_cfg,
        source=source,
        iid=iid,
        client_roles=client_roles,
        malicious_clients=malicious_clients,
        unseen_clients=unseen_clients,
        unseen_shift_type=unseen_shift_type,
    )

    first_image, _ = train_dataset[0]
    return FederatedData(
        client_loaders=client_loaders,
        root_loader=root_loader,
        train_eval_loader=train_eval_loader,
        test_loader=test_loader,
        client_roles=client_roles,
        malicious_clients=malicious_clients,
        unseen_clients=unseen_clients,
        num_classes=num_classes,
        input_shape=tuple(int(value) for value in first_image.shape),
        dataset_source=source,
        metadata=metadata,
    )


def _load_dataset(dataset_cfg: dict, fed_cfg: dict, rng: np.random.Generator, seed: int) -> tuple[Dataset, Dataset, int, str]:
    name = str(dataset_cfg.get("name", "cifar10")).lower()
    num_classes = int(dataset_cfg.get("num_classes", 10))
    if name == "cifar10":
        try:
            return _load_cifar10(dataset_cfg, num_classes)
        except Exception as exc:
            if not bool(dataset_cfg.get("use_synthetic_fallback", True)):
                raise
            print(f"CIFAR-10 loading failed, using synthetic fallback. Reason: {exc}")
    if name == "femnist":
        try:
            return _load_femnist(dataset_cfg, fed_cfg, seed)
        except Exception as exc:
            if not bool(dataset_cfg.get("use_synthetic_fallback", False)):
                raise RuntimeError(
                    "Real FEMNIST loading failed. Configure dataset.data_root/local_path or enable download; "
                    "synthetic fallback is disabled for FEMNIST."
                ) from exc
            print(f"FEMNIST loading failed, using explicitly enabled synthetic fallback. Reason: {exc}")
    if name == "gtsrb":
        try:
            return _load_gtsrb(dataset_cfg, num_classes)
        except Exception as exc:
            if not bool(dataset_cfg.get("use_synthetic_fallback", False)):
                raise RuntimeError(
                    "Real GTSRB loading failed. Configure dataset.data_root/local_path or enable download; "
                    "synthetic fallback is disabled for GTSRB."
                ) from exc
            print(f"GTSRB loading failed, using explicitly enabled synthetic fallback. Reason: {exc}")
    if name in {"stanford_cars", "stanfordcars", "cars"}:
        try:
            return _load_stanford_cars(dataset_cfg, num_classes)
        except Exception as exc:
            if not bool(dataset_cfg.get("use_synthetic_fallback", False)):
                raise RuntimeError(
                    "Real Stanford Cars loading failed. Configure dataset.data_root/local_path or enable download; "
                    "synthetic fallback is disabled for Stanford Cars."
                ) from exc
            print(f"Stanford Cars loading failed, using explicitly enabled synthetic fallback. Reason: {exc}")
    return _make_synthetic_images(dataset_cfg, num_classes, rng)


def _loader_kwargs(fed_cfg: dict, prefix: str) -> dict:
    perf_cfg = fed_cfg.get("dataloader", {})
    num_workers = int(
        perf_cfg.get(
            f"{prefix}_num_workers",
            fed_cfg.get(f"{prefix}_num_workers", fed_cfg.get("num_workers", 0)),
        )
    )
    pin_memory = bool(perf_cfg.get("pin_memory", fed_cfg.get("pin_memory", torch.cuda.is_available())))
    kwargs = {"num_workers": max(0, num_workers), "pin_memory": pin_memory}
    if num_workers > 0:
        kwargs["persistent_workers"] = bool(
            perf_cfg.get("persistent_workers", fed_cfg.get("persistent_workers", False))
        )
        prefetch_factor = int(perf_cfg.get("prefetch_factor", fed_cfg.get("prefetch_factor", 2)))
        if prefetch_factor > 0:
            kwargs["prefetch_factor"] = prefetch_factor
    return kwargs


def _load_cifar10(dataset_cfg: dict, num_classes: int) -> tuple[Dataset, Dataset, int, str]:
    from torchvision import datasets, transforms

    normalize = transforms.Normalize(mean=(0.4914, 0.4822, 0.4465), std=(0.247, 0.243, 0.261))
    train_steps = []
    if bool(dataset_cfg.get("augment_train", False)):
        train_steps.extend(
            [
                transforms.RandomCrop(32, padding=int(dataset_cfg.get("random_crop_padding", 4))),
                transforms.RandomHorizontalFlip(),
            ]
        )
    train_steps.extend([transforms.ToTensor(), normalize])
    train_transform = transforms.Compose(train_steps)
    test_transform = transforms.Compose([transforms.ToTensor(), normalize])
    data_dir = Path(dataset_cfg.get("data_root") or dataset_cfg.get("data_dir", "data"))
    train = datasets.CIFAR10(root=data_dir, train=True, transform=train_transform, download=bool(dataset_cfg.get("download", False)))
    test = datasets.CIFAR10(root=data_dir, train=False, transform=test_transform, download=bool(dataset_cfg.get("download", False)))

    if bool(dataset_cfg.get("quick_dev", True)):
        train_subset = int(dataset_cfg.get("train_subset_size", dataset_cfg.get("train_subset", 900)))
        test_subset = int(dataset_cfg.get("test_subset_size", dataset_cfg.get("test_subset", 300)))
        train = _balanced_subset(train, train_subset, num_classes, seed=7)
        test = _balanced_subset(test, test_subset, num_classes, seed=11)
    return train, test, num_classes, "real"


def _load_femnist(dataset_cfg: dict, fed_cfg: dict, seed: int) -> tuple[Dataset, Dataset, int, str]:
    from datasets import load_dataset, load_from_disk
    from torchvision import transforms

    data_root = Path(dataset_cfg.get("data_root", "data/femnist_hf"))
    local_path = dataset_cfg.get("local_path")
    if local_path:
        source_path = Path(local_path)
        if source_path.is_dir():
            raw = load_from_disk(str(source_path))
            raw = raw["train"] if hasattr(raw, "keys") and "train" in raw else raw
        else:
            raw = load_dataset("parquet", data_files=str(source_path), split="train", cache_dir=str(data_root))
    else:
        repository = str(dataset_cfg.get("repository", "flwrlabs/femnist"))
        if not bool(dataset_cfg.get("download", True)) and not data_root.exists():
            raise FileNotFoundError(f"FEMNIST cache not found and download=false: {data_root}")
        raw = load_dataset(repository, split="train", cache_dir=str(data_root))

    required = {"image", "writer_id", "character"}
    if not required.issubset(set(raw.column_names)):
        raise ValueError(f"FEMNIST source must contain {sorted(required)}; got {raw.column_names}")
    writer_ids = [str(value) for value in raw["writer_id"]]
    targets = [int(value) for value in raw["character"]]
    counts = Counter(writer_ids)
    min_writer_samples = int(dataset_cfg.get("min_writer_samples", 100))
    eligible = sorted(writer_id for writer_id, count in counts.items() if count >= min_writer_samples)
    required_writers = int(fed_cfg["num_clients"])
    if len(eligible) < required_writers:
        raise ValueError(f"Only {len(eligible)} FEMNIST writers have >= {min_writer_samples} samples; need {required_writers}")
    writer_rng = np.random.default_rng(seed)
    writer_rng.shuffle(eligible)
    selected_writers = eligible[:required_writers]
    selected_set = set(selected_writers)
    writer_global_indices: dict[str, list[int]] = {writer_id: [] for writer_id in selected_writers}
    for index, writer_id in enumerate(writer_ids):
        if writer_id in selected_set:
            writer_global_indices[writer_id].append(index)

    test_fraction = float(dataset_cfg.get("test_fraction", 0.2))
    train_indices: list[int] = []
    test_indices: list[int] = []
    for offset, writer_id in enumerate(selected_writers):
        indices = np.asarray(writer_global_indices[writer_id], dtype=int)
        split_rng = np.random.default_rng(seed + 1009 * (offset + 1))
        split_rng.shuffle(indices)
        test_count = max(1, min(len(indices) - 1, int(round(len(indices) * test_fraction))))
        test_indices.extend(indices[:test_count].tolist())
        train_indices.extend(indices[test_count:].tolist())

    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(mean=(0.5,), std=(0.5,)),
        ]
    )
    train = FEMNISTHFDataset(raw, train_indices, transform, writer_ids, targets, "train")
    test = FEMNISTHFDataset(raw, test_indices, transform, writer_ids, targets, "test")
    train.selected_writer_ids = list(selected_writers)
    test.selected_writer_ids = list(selected_writers)
    train.source_repository = str(dataset_cfg.get("repository", "flwrlabs/femnist"))
    test.source_repository = train.source_repository
    return train, test, 62, "real"


def _load_gtsrb(dataset_cfg: dict, num_classes: int) -> tuple[Dataset, Dataset, int, str]:
    from torchvision import datasets, transforms

    image_size = int(dataset_cfg.get("image_size", 32))
    normalize = transforms.Normalize(
        mean=tuple(dataset_cfg.get("normalize_mean", [0.3403, 0.3121, 0.3214])),
        std=tuple(dataset_cfg.get("normalize_std", [0.2724, 0.2608, 0.2669])),
    )
    train_steps = [transforms.Resize((image_size, image_size))]
    if bool(dataset_cfg.get("augment_train", False)):
        train_steps.extend(
            [
                transforms.RandomRotation(float(dataset_cfg.get("random_rotation", 10.0))),
                transforms.RandomAffine(
                    degrees=0,
                    translate=tuple(dataset_cfg.get("random_translate", [0.05, 0.05])),
                    scale=tuple(dataset_cfg.get("random_scale", [0.95, 1.05])),
                ),
            ]
        )
    train_steps.extend([transforms.ToTensor(), normalize])
    train_transform = transforms.Compose(train_steps)
    test_transform = transforms.Compose([transforms.Resize((image_size, image_size)), transforms.ToTensor(), normalize])
    data_dir = Path(dataset_cfg.get("data_root") or dataset_cfg.get("data_dir", "data/gtsrb"))
    train = datasets.GTSRB(root=data_dir, split="train", transform=train_transform, download=bool(dataset_cfg.get("download", False)))
    test = datasets.GTSRB(root=data_dir, split="test", transform=test_transform, download=bool(dataset_cfg.get("download", False)))
    train.dataset_variant = "torchvision_gtsrb"
    test.dataset_variant = "torchvision_gtsrb"
    train.source_repository = "torchvision.datasets.GTSRB"
    test.source_repository = train.source_repository
    train.transform_description = (
        f"Resize({image_size}) + optional rotation/affine augmentation + ToTensor + Normalize(GTSRB)"
    )
    test.transform_description = f"Resize({image_size}) + ToTensor + Normalize(GTSRB)"
    if bool(dataset_cfg.get("quick_dev", False)):
        train_subset = int(dataset_cfg.get("train_subset_size", dataset_cfg.get("train_subset", 10000)))
        test_subset = int(dataset_cfg.get("test_subset_size", dataset_cfg.get("test_subset", 3000)))
        train = _balanced_subset(train, train_subset, num_classes, seed=17)
        test = _balanced_subset(test, test_subset, num_classes, seed=19)
        train.dataset_variant = "torchvision_gtsrb_balanced_subset"
        test.dataset_variant = "torchvision_gtsrb_balanced_subset"
    if bool(dataset_cfg.get("cache_tensors", False)):
        train = CachedTensorDataset(train, num_classes)
        test = CachedTensorDataset(test, num_classes)
    return train, test, num_classes, "real"


def _load_stanford_cars(dataset_cfg: dict, num_classes: int) -> tuple[Dataset, Dataset, int, str]:
    from torchvision import datasets, transforms

    image_size = int(dataset_cfg.get("image_size", 224))
    resize_size = int(dataset_cfg.get("resize_size", max(256, image_size)))
    normalize = transforms.Normalize(
        mean=tuple(dataset_cfg.get("normalize_mean", [0.485, 0.456, 0.406])),
        std=tuple(dataset_cfg.get("normalize_std", [0.229, 0.224, 0.225])),
    )
    train_steps = [transforms.Resize((resize_size, resize_size))]
    if bool(dataset_cfg.get("augment_train", True)):
        train_steps.extend(
            [
                transforms.RandomResizedCrop(image_size, scale=tuple(dataset_cfg.get("random_resized_crop_scale", [0.75, 1.0]))),
                transforms.RandomHorizontalFlip(),
            ]
        )
    else:
        train_steps.append(transforms.CenterCrop(image_size))
    train_steps.extend([transforms.ToTensor(), normalize])
    train_transform = transforms.Compose(train_steps)
    test_transform = transforms.Compose(
        [
            transforms.Resize((resize_size, resize_size)),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            normalize,
        ]
    )
    data_dir = Path(dataset_cfg.get("data_root") or dataset_cfg.get("data_dir", "data/stanford_cars"))
    source = str(dataset_cfg.get("source", "torchvision")).lower()
    if source in {"huggingface", "hf"}:
        train, test = _load_stanford_cars_hf(dataset_cfg, train_transform, test_transform, data_dir)
    else:
        try:
            train = datasets.StanfordCars(root=data_dir, split="train", transform=train_transform, download=bool(dataset_cfg.get("download", False)))
            test = datasets.StanfordCars(root=data_dir, split="test", transform=test_transform, download=bool(dataset_cfg.get("download", False)))
            train.dataset_variant = "torchvision_stanford_cars"
            test.dataset_variant = "torchvision_stanford_cars"
            train.source_repository = "torchvision.datasets.StanfordCars"
            test.source_repository = train.source_repository
            train.transform_description = (
                f"Resize({resize_size}) + RandomResizedCrop({image_size})/CenterCrop + optional horizontal flip + ToTensor + Normalize(ImageNet)"
            )
            test.transform_description = f"Resize({resize_size}) + CenterCrop({image_size}) + ToTensor + Normalize(ImageNet)"
        except Exception:
            if not bool(dataset_cfg.get("hf_fallback", False)):
                raise
            train, test = _load_stanford_cars_hf(dataset_cfg, train_transform, test_transform, data_dir)
    if bool(dataset_cfg.get("quick_dev", False)):
        train_subset = int(dataset_cfg.get("train_subset_size", dataset_cfg.get("train_subset", 2000)))
        test_subset = int(dataset_cfg.get("test_subset_size", dataset_cfg.get("test_subset", 1000)))
        source_repository = getattr(train, "source_repository", "torchvision.datasets.StanfordCars")
        train_transform_description = getattr(train, "transform_description", "Stanford Cars train transforms")
        test_transform_description = getattr(test, "transform_description", "Stanford Cars test transforms")
        train = _balanced_subset(train, train_subset, num_classes, seed=23)
        test = _balanced_subset(test, test_subset, num_classes, seed=29)
        base_variant = "hf_stanford_cars" if "huggingface" in source_repository.lower() or "StanfordCars" in source_repository else "torchvision_stanford_cars"
        train.dataset_variant = f"{base_variant}_balanced_subset"
        test.dataset_variant = f"{base_variant}_balanced_subset"
        train.source_repository = source_repository
        test.source_repository = source_repository
        train.transform_description = train_transform_description
        test.transform_description = test_transform_description
    if bool(dataset_cfg.get("cache_tensors", False)):
        train = CachedTensorDataset(train, num_classes)
        test = CachedTensorDataset(test, num_classes)
    return train, test, num_classes, "real"


def _load_stanford_cars_hf(dataset_cfg: dict, train_transform, test_transform, data_dir: Path) -> tuple[Dataset, Dataset]:
    from datasets import load_dataset

    repository = str(dataset_cfg.get("repository", "mteb/StanfordCars"))
    train_split = str(dataset_cfg.get("train_split", "train"))
    test_split = str(dataset_cfg.get("test_split", "test"))
    label_column = str(dataset_cfg.get("label_column", "label"))
    cache_dir = str(data_dir / "hf_cache")
    train_raw = load_dataset(repository, split=train_split, cache_dir=cache_dir)
    test_raw = load_dataset(repository, split=test_split, cache_dir=cache_dir)
    train = HFImageClassificationDataset(train_raw, train_transform, label_column=label_column, variant="hf_stanford_cars")
    test = HFImageClassificationDataset(test_raw, test_transform, label_column=label_column, variant="hf_stanford_cars")
    train.source_repository = repository
    test.source_repository = repository
    train.transform_description = "HF Stanford Cars + train transforms + ImageNet normalization"
    test.transform_description = "HF Stanford Cars + test transforms + ImageNet normalization"
    return train, test


def _make_synthetic_images(dataset_cfg: dict, num_classes: int, rng: np.random.Generator) -> tuple[Dataset, Dataset, int, str]:
    total = int(dataset_cfg.get("synthetic_samples", 1200))
    test_total = max(int(total * 0.25), int(dataset_cfg.get("test_subset_size", dataset_cfg.get("test_subset", 300))))
    train_total = max(total, int(dataset_cfg.get("train_subset_size", dataset_cfg.get("train_subset", 900))))
    prototypes = rng.normal(0.0, 1.0, size=(num_classes, 3, 32, 32)).astype("float32")

    def sample(count: int) -> TensorDataset:
        labels = np.arange(count) % num_classes
        rng.shuffle(labels)
        images = prototypes[labels] + rng.normal(0.0, 0.45, size=(count, 3, 32, 32)).astype("float32")
        images = (images - images.mean(axis=(1, 2, 3), keepdims=True)) / (images.std(axis=(1, 2, 3), keepdims=True) + 1e-6)
        return TensorDataset(torch.tensor(images, dtype=torch.float32), torch.tensor(labels, dtype=torch.long))

    return sample(train_total), sample(test_total), num_classes, "synthetic"


def _balanced_subset(dataset: Dataset, subset_size: int, num_classes: int, seed: int) -> Subset:
    rng = np.random.default_rng(seed)
    targets = _extract_targets(dataset)
    selected: list[int] = []
    per_class = max(1, subset_size // num_classes)
    for class_id in range(num_classes):
        class_indices = np.where(targets == class_id)[0]
        if len(class_indices) == 0:
            continue
        take = min(per_class, len(class_indices))
        selected.extend(rng.choice(class_indices, size=take, replace=False).tolist())
    rng.shuffle(selected)
    return Subset(dataset, selected[:subset_size])


def _partition_clients(
    train_dataset: Dataset,
    num_clients: int,
    root_size: int,
    seed: int,
    iid: bool,
    num_classes: int,
    alpha,
    min_client_samples: int,
) -> tuple[list[list[int]], list[int]]:
    rng = np.random.default_rng(seed)
    total_indices = np.arange(len(train_dataset))
    rng.shuffle(total_indices)
    root_indices = total_indices[:root_size].tolist()
    client_pool = total_indices[root_size:]
    if iid:
        return _partition_clients_iid(train_dataset, client_pool, num_clients, num_classes, rng), root_indices
    parsed_alpha = _parse_float(alpha)
    if parsed_alpha is not None and parsed_alpha > 0:
        return (
            _partition_clients_dirichlet(
                train_dataset=train_dataset,
                client_pool=client_pool,
                num_clients=num_clients,
                num_classes=num_classes,
                alpha=parsed_alpha,
                min_client_samples=max(1, int(min_client_samples)),
                rng=rng,
            ),
            root_indices,
        )
    splits = np.array_split(client_pool, num_clients)
    return [split.tolist() for split in splits], root_indices


def _partition_clients_by_writer(
    train_dataset: Dataset,
    num_clients: int,
    root_size: int,
    seed: int,
) -> tuple[list[list[int]], list[int]]:
    writer_to_indices = getattr(train_dataset, "writer_to_indices", {})
    writer_ids = list(getattr(train_dataset, "selected_writer_ids", writer_to_indices.keys()))
    if len(writer_ids) < num_clients:
        raise ValueError(f"Writer partition has {len(writer_ids)} writers but num_clients={num_clients}")
    client_indices = [list(writer_to_indices[writer_id]) for writer_id in writer_ids[:num_clients]]
    root_indices: list[int] = []
    if root_size > 0:
        rng = np.random.default_rng(seed + 4242)
        candidates = [(client_id, index) for client_id, indices in enumerate(client_indices) for index in indices]
        rng.shuffle(candidates)
        for client_id, index in candidates[: min(root_size, len(candidates))]:
            if len(client_indices[client_id]) > 1:
                client_indices[client_id].remove(index)
                root_indices.append(index)
    return client_indices, root_indices


def _partition_clients_iid(
    train_dataset: Dataset,
    client_pool: np.ndarray,
    num_clients: int,
    num_classes: int,
    rng: np.random.Generator,
) -> list[list[int]]:
    targets = _extract_targets(train_dataset)
    client_indices: list[list[int]] = [[] for _ in range(num_clients)]
    for class_id in range(num_classes):
        class_indices = client_pool[targets[client_pool] == class_id]
        rng.shuffle(class_indices)
        splits = np.array_split(class_indices, num_clients)
        for client_id, split in enumerate(splits):
            client_indices[client_id].extend(split.tolist())
    for indices in client_indices:
        rng.shuffle(indices)
    return client_indices


def _partition_clients_dirichlet(
    train_dataset: Dataset,
    client_pool: np.ndarray,
    num_clients: int,
    num_classes: int,
    alpha: float,
    min_client_samples: int,
    rng: np.random.Generator,
    max_attempts: int = 100,
) -> list[list[int]]:
    targets = _extract_targets(train_dataset)
    min_client_samples = min(min_client_samples, max(1, len(client_pool) // max(num_clients, 1)))
    best_split: list[list[int]] | None = None
    best_min_count = -1
    for _ in range(max_attempts):
        client_indices: list[list[int]] = [[] for _ in range(num_clients)]
        for class_id in range(num_classes):
            class_indices = client_pool[targets[client_pool] == class_id]
            rng.shuffle(class_indices)
            if len(class_indices) == 0:
                continue
            proportions = rng.dirichlet(np.full(num_clients, alpha, dtype=float))
            split_points = (np.cumsum(proportions) * len(class_indices)).astype(int)[:-1]
            splits = np.split(class_indices, split_points)
            for client_id, split in enumerate(splits):
                client_indices[client_id].extend(split.tolist())
        counts = [len(indices) for indices in client_indices]
        current_min = min(counts) if counts else 0
        if current_min > best_min_count:
            best_split = [list(indices) for indices in client_indices]
            best_min_count = current_min
        if current_min >= min_client_samples:
            for indices in client_indices:
                rng.shuffle(indices)
            return client_indices

    client_indices = best_split or [[] for _ in range(num_clients)]
    _repair_min_client_samples(client_indices, min_client_samples, rng)
    for indices in client_indices:
        rng.shuffle(indices)
    return client_indices


def _repair_min_client_samples(client_indices: list[list[int]], min_client_samples: int, rng: np.random.Generator) -> None:
    for client_id in range(len(client_indices)):
        while len(client_indices[client_id]) < min_client_samples:
            donor_id = int(np.argmax([len(indices) for indices in client_indices]))
            if donor_id == client_id or len(client_indices[donor_id]) <= min_client_samples:
                return
            moved_index = client_indices[donor_id].pop(int(rng.integers(len(client_indices[donor_id]))))
            client_indices[client_id].append(moved_index)


def _build_metadata(
    train_dataset: Dataset,
    test_dataset: Dataset,
    client_indices: list[list[int]],
    root_indices: list[int],
    train_eval_indices: list[int],
    num_classes: int,
    dataset_cfg: dict,
    fed_cfg: dict,
    source: str,
    iid: bool,
    client_roles: dict[int, str],
    malicious_clients: set[int],
    unseen_clients: set[int],
    unseen_shift_type: str,
) -> dict:
    train_targets = _extract_targets(train_dataset)
    test_targets = _extract_targets(test_dataset)
    client_class_counts = []
    client_label_distribution = []
    for client_id, indices in enumerate(client_indices):
        labels = train_targets[np.asarray(indices, dtype=int)] if indices else np.asarray([], dtype=int)
        counts = np.bincount(labels, minlength=num_classes).astype(int).tolist()
        client_class_counts.append(counts)
        row = {
            "client_id": client_id,
            "true_type": client_roles.get(client_id, "benign"),
            "is_malicious": client_id in malicious_clients,
            "is_unseen": client_id in unseen_clients,
            "num_samples": len(indices),
        }
        for class_id, count in enumerate(counts):
            row[f"class_{class_id}"] = count
        client_label_distribution.append(row)
    first_loader = DataLoader(Subset(train_dataset, list(range(min(1, len(train_dataset))))), batch_size=1)
    first_batch = next(iter(first_loader))
    return {
        "dataset_name": dataset_cfg.get("name", "unknown"),
        "dataset_source": source,
        "synthetic": source == "synthetic",
        "train_size": len(train_dataset),
        "test_size": len(test_dataset),
        "uses_subset": bool(dataset_cfg.get("quick_dev", False)),
        "train_subset_size": int(dataset_cfg.get("train_subset_size", dataset_cfg.get("train_subset", len(train_dataset)))),
        "test_subset_size": int(dataset_cfg.get("test_subset_size", dataset_cfg.get("test_subset", len(test_dataset)))),
        "train_eval_size": len(train_eval_indices),
        "dataset_variant": getattr(train_dataset, "dataset_variant", dataset_cfg.get("name", "unknown")),
        "source_repository": getattr(train_dataset, "source_repository", "NA"),
        "selected_writer_ids": getattr(train_dataset, "selected_writer_ids", []),
        "transform": getattr(
            train_dataset,
            "transform_description",
            "train: optional RandomCrop/RandomHorizontalFlip + ToTensor + Normalize; "
            "test: ToTensor + Normalize(mean=(0.4914,0.4822,0.4465), std=(0.247,0.243,0.261))",
        ),
        "label_min": int(min(train_targets.min(), test_targets.min())),
        "label_max": int(max(train_targets.max(), test_targets.max())),
        "batch_shape": list(first_batch[0].shape),
        "num_clients": int(fed_cfg["num_clients"]),
        "clients_per_round": int(fed_cfg["clients_per_round"]),
        "iid": iid,
        "non_iid_alpha": fed_cfg.get("non_iid_alpha", "NA"),
        "min_client_samples": int(fed_cfg.get("min_client_samples", 1)),
        "partition_method": _partition_method_name(fed_cfg, iid, train_dataset),
        "root_size": len(root_indices),
        "client_sample_counts": [len(indices) for indices in client_indices],
        "client_class_counts": client_class_counts,
        "client_label_distribution": client_label_distribution,
        "client_roles": {str(key): value for key, value in client_roles.items()},
        "malicious_client_ids": sorted(int(idx) for idx in malicious_clients),
        "unseen_client_ids": sorted(int(idx) for idx in unseen_clients),
        "unseen_shift_type": unseen_shift_type,
        "partition_summary": {
            "partition_method": _partition_method_name(fed_cfg, iid, train_dataset),
            "iid": iid,
            "non_iid_alpha": fed_cfg.get("non_iid_alpha", "NA"),
            "min_client_samples": int(fed_cfg.get("min_client_samples", 1)),
            "empty_clients": [idx for idx, indices in enumerate(client_indices) if not indices],
            "min_client_samples_observed": min((len(indices) for indices in client_indices), default=0),
            "max_client_samples_observed": max((len(indices) for indices in client_indices), default=0),
        },
    }


def _partition_method_name(fed_cfg: dict, iid: bool, train_dataset: Dataset) -> str:
    requested = str(fed_cfg.get("partition_method", "")).lower()
    if requested in {"writer", "natural_writer"} and hasattr(train_dataset, "writer_to_indices"):
        return "natural_writer"
    return "iid_balanced" if iid else ("dirichlet" if _parse_float(fed_cfg.get("non_iid_alpha", "NA")) else "random_split")


def _parse_float(value) -> float | None:
    try:
        if value in {None, "", "NA", "na", "null"}:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_targets(dataset: Dataset) -> np.ndarray:
    if isinstance(dataset, Subset):
        parent_targets = _extract_targets(dataset.dataset)
        return parent_targets[np.array(dataset.indices)]
    if hasattr(dataset, "targets"):
        return np.asarray(dataset.targets)
    if hasattr(dataset, "_samples"):
        return np.asarray([int(sample[1]) for sample in dataset._samples])
    if hasattr(dataset, "_labels"):
        return np.asarray([int(label) for label in dataset._labels])
    if hasattr(dataset, "tensors"):
        return dataset.tensors[1].numpy()
    labels = [int(dataset[i][1]) for i in range(len(dataset))]
    return np.asarray(labels)
