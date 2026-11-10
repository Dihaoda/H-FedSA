from __future__ import annotations

import torch
from torch import nn


def _norm_layer(channels: int, batchnorm: bool) -> nn.Module:
    return nn.BatchNorm2d(channels) if batchnorm else nn.Identity()


class GTSRBBasicBlock(nn.Module):
    expansion = 1

    def __init__(self, in_planes: int, planes: int, stride: int = 1, batchnorm: bool = True) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(in_planes, planes, kernel_size=3, stride=stride, padding=1, bias=not batchnorm)
        self.bn1 = _norm_layer(planes, batchnorm)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=not batchnorm)
        self.bn2 = _norm_layer(planes, batchnorm)
        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != planes:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_planes, planes, kernel_size=1, stride=stride, bias=not batchnorm),
                _norm_layer(planes, batchnorm),
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out = out + self.shortcut(x)
        return self.relu(out)


class ResNet18GTSRB(nn.Module):
    """CIFAR/GTSRB-sized ResNet-18 with optional BatchNorm for FL calibration."""

    def __init__(self, num_classes: int = 43, batchnorm: bool = True, width: int = 64) -> None:
        super().__init__()
        self.batchnorm = bool(batchnorm)
        self.in_planes = int(width)
        self.conv1 = nn.Conv2d(3, int(width), kernel_size=3, stride=1, padding=1, bias=not self.batchnorm)
        self.bn1 = _norm_layer(int(width), self.batchnorm)
        self.relu = nn.ReLU(inplace=True)
        self.layer1 = self._make_layer(int(width), 2, stride=1)
        self.layer2 = self._make_layer(int(width) * 2, 2, stride=2)
        self.layer3 = self._make_layer(int(width) * 4, 2, stride=2)
        self.layer4 = self._make_layer(int(width) * 8, 2, stride=2)
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(int(width) * 8, num_classes)
        self._init_weights()

    def _make_layer(self, planes: int, blocks: int, stride: int) -> nn.Sequential:
        strides = [stride] + [1] * (blocks - 1)
        layers = []
        for current_stride in strides:
            layers.append(GTSRBBasicBlock(self.in_planes, planes, current_stride, self.batchnorm))
            self.in_planes = planes
        return nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = self.pool(out)
        return self.fc(torch.flatten(out, 1))

    def _init_weights(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.BatchNorm2d):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)


class GTSRBCNN(nn.Module):
    """Compact CNN sanity model for GTSRB data/label pipeline checks."""

    def __init__(self, num_classes: int = 43, channels: tuple[int, int, int] = (32, 64, 128), dropout: float = 0.2) -> None:
        super().__init__()
        c1, c2, c3 = (int(channels[0]), int(channels[1]), int(channels[2]))
        self.features = nn.Sequential(
            nn.Conv2d(3, c1, kernel_size=3, padding=1),
            nn.BatchNorm2d(c1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(c1, c2, kernel_size=3, padding=1),
            nn.BatchNorm2d(c2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(c2, c3, kernel_size=3, padding=1),
            nn.BatchNorm2d(c3),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(float(dropout)),
            nn.Linear(c3, num_classes),
        )
        self._init_weights()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))

    def _init_weights(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.BatchNorm2d):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)


def build_pretrained_resnet18_gtsrb(num_classes: int = 43, weights_name: str = "DEFAULT") -> nn.Module:
    from torchvision import models

    weights = None
    if str(weights_name).lower() not in {"none", "false", "off", "null"}:
        weights = models.ResNet18_Weights.DEFAULT
    model = models.resnet18(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    nn.init.xavier_uniform_(model.fc.weight)
    nn.init.zeros_(model.fc.bias)
    return model
