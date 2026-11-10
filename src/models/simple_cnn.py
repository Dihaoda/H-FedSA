from __future__ import annotations

from torch import nn

from src.models.paper_cnn import PaperCNN, ResNet18CIFAR
from src.models.resnet_gtsrb import GTSRBCNN, ResNet18GTSRB, build_pretrained_resnet18_gtsrb


class FEMNISTCNN(nn.Module):
    """Two-conv/two-FC grayscale CNN for 62-class writer-partitioned FEMNIST."""

    def __init__(self, num_classes: int = 62, conv_channels: tuple[int, int] = (32, 64), hidden_dim: int = 256, dropout: float = 0.2) -> None:
        super().__init__()
        c1, c2 = (int(conv_channels[0]), int(conv_channels[1]))
        self.features = nn.Sequential(
            nn.Conv2d(1, c1, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(c1, c2, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )
        classifier: list[nn.Module] = [
            nn.Flatten(),
            nn.Linear(c2 * 7 * 7, hidden_dim),
            nn.ReLU(inplace=True),
        ]
        if dropout > 0:
            classifier.append(nn.Dropout(dropout))
        classifier.append(nn.Linear(hidden_dim, num_classes))
        self.classifier = nn.Sequential(*classifier)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))


class SmallCNN(nn.Module):
    def __init__(self, num_classes: int = 10) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32 * 8 * 8, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))


def build_model(num_classes: int, model_cfg: dict | None = None) -> nn.Module:
    model_cfg = model_cfg or {}
    name = str(model_cfg.get("name", "small_cnn")).lower()
    if name == "paper_cnn":
        batchnorm = model_cfg.get("batchnorm", model_cfg.get("paper_cnn_bn_enabled", True))
        return PaperCNN(
            num_classes=num_classes,
            conv_channels=tuple(model_cfg.get("conv_channels", [64, 128])),
            hidden_dim=int(model_cfg.get("hidden_dim", 512)),
            batchnorm=bool(batchnorm),
            dropout=float(model_cfg.get("dropout", 0.25)),
        )
    if name == "resnet18_cifar":
        return ResNet18CIFAR(num_classes=num_classes)
    if name in {"resnet18_gtsrb", "gtsrb_resnet18", "resnet18_stanford_cars", "stanford_cars_resnet18", "resnet18_imagenet"}:
        if bool(model_cfg.get("pretrained", False)):
            model = build_pretrained_resnet18_gtsrb(
                num_classes=num_classes,
                weights_name=str(model_cfg.get("weights", "DEFAULT")),
            )
            if bool(model_cfg.get("freeze_backbone", False)):
                for param in model.parameters():
                    param.requires_grad = False
                for param in model.fc.parameters():
                    param.requires_grad = True
            return model
        return ResNet18GTSRB(
            num_classes=num_classes,
            batchnorm=bool(model_cfg.get("batchnorm", True)),
            width=int(model_cfg.get("width", 64)),
        )
    if name in {"gtsrb_cnn", "simple_gtsrb_cnn"}:
        return GTSRBCNN(
            num_classes=num_classes,
            channels=tuple(model_cfg.get("channels", [32, 64, 128])),
            dropout=float(model_cfg.get("dropout", 0.2)),
        )
    if name in {"femnist_cnn", "femnist_lightweight_cnn"}:
        return FEMNISTCNN(
            num_classes=num_classes,
            conv_channels=tuple(model_cfg.get("conv_channels", [32, 64])),
            hidden_dim=int(model_cfg.get("hidden_dim", 256)),
            dropout=float(model_cfg.get("dropout", 0.2)),
        )
    return SmallCNN(num_classes=num_classes)
