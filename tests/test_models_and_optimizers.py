from collections import OrderedDict

import pytest
import torch

from src.federated.server_optimizers import build_server_optimizer
from src.models.paper_cnn import PaperCNN, ResNet18CIFAR
from src.models.resnet_gtsrb import GTSRBCNN, ResNet18GTSRB
from src.models.simple_cnn import FEMNISTCNN, SmallCNN, build_model
from src.utils.config import MODELS


EXPECTED_MODEL_TYPES = {
    "small_cnn": SmallCNN,
    "paper_cnn": PaperCNN,
    "resnet18_cifar": ResNet18CIFAR,
    "resnet18_gtsrb": ResNet18GTSRB,
    "gtsrb_resnet18": ResNet18GTSRB,
    "resnet18_stanford_cars": ResNet18GTSRB,
    "stanford_cars_resnet18": ResNet18GTSRB,
    "resnet18_imagenet": ResNet18GTSRB,
    "gtsrb_cnn": GTSRBCNN,
    "simple_gtsrb_cnn": GTSRBCNN,
    "femnist_cnn": FEMNISTCNN,
    "femnist_lightweight_cnn": FEMNISTCNN,
}


@pytest.mark.parametrize("name", sorted(MODELS))
def test_every_model_alias_builds_the_intended_architecture(name: str) -> None:
    model = build_model(7, {"name": name, "pretrained": False, "width": 8})
    assert isinstance(model, EXPECTED_MODEL_TYPES[name])


@pytest.mark.parametrize(
    ("name", "shape"),
    [
        ("small_cnn", (2, 3, 32, 32)),
        ("paper_cnn", (2, 3, 32, 32)),
        ("resnet18_cifar", (2, 3, 32, 32)),
        ("gtsrb_cnn", (2, 3, 32, 32)),
        ("femnist_cnn", (2, 1, 28, 28)),
    ],
)
def test_unique_model_families_produce_class_logits(name: str, shape: tuple[int, ...]) -> None:
    model = build_model(7, {"name": name, "width": 8})
    model.eval()
    with torch.no_grad():
        output = model(torch.randn(shape))
    assert tuple(output.shape) == (2, 7)
    assert torch.isfinite(output).all()


def _state(value: float):
    return OrderedDict(weight=torch.tensor([value, -value]), counter=torch.tensor(0, dtype=torch.long))


@pytest.mark.parametrize("name", ["fedavg", "fedavgm", "fedadam"])
def test_server_optimizers_return_finite_updates_and_diagnostics(name: str) -> None:
    config = {
        "federated": {
            "server_optimizer": name,
            "server_lr": 0.5,
            "server_momentum": 0.9,
            "server_beta1": 0.9,
            "server_beta2": 0.99,
            "server_eps": 1e-8,
        }
    }
    optimizer = build_server_optimizer(config, _state(0.0))
    update, diagnostics = optimizer.step(_state(2.0))

    assert torch.isfinite(update["weight"]).all()
    assert update["counter"].item() == 0
    assert diagnostics["server_optimizer"] == name
    assert diagnostics["server_update_norm"] > 0


def test_server_optimizer_sanitizes_non_finite_values() -> None:
    optimizer = build_server_optimizer(
        {"federated": {"server_optimizer": "fedavg", "server_lr": 1.0}},
        _state(0.0),
    )
    poisoned = OrderedDict(
        weight=torch.tensor([float("nan"), float("inf")]),
        counter=torch.tensor(0, dtype=torch.long),
    )
    update, diagnostics = optimizer.step(poisoned)

    assert torch.equal(update["weight"], torch.zeros(2))
    assert diagnostics["server_nan_flag"] is True
    assert diagnostics["server_inf_flag"] is True

