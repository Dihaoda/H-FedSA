from __future__ import annotations

import torch
from torch import nn


class PaperCNN(nn.Module):
    """Two-conv/two-FC CIFAR-10 CNN used for paper-target calibration."""

    def __init__(
        self,
        num_classes: int = 10,
        conv_channels: tuple[int, int] = (64, 128),
        hidden_dim: int = 512,
        batchnorm: bool = True,
        dropout: float = 0.25,
    ) -> None:
        super().__init__()
        c1, c2 = int(conv_channels[0]), int(conv_channels[1])
        layers: list[nn.Module] = [nn.Conv2d(3, c1, kernel_size=5, padding=2)]
        if batchnorm:
            layers.append(nn.BatchNorm2d(c1))
        layers.extend([nn.ReLU(inplace=True), nn.MaxPool2d(2)])
        layers.append(nn.Conv2d(c1, c2, kernel_size=5, padding=2))
        if batchnorm:
            layers.append(nn.BatchNorm2d(c2))
        layers.extend([nn.ReLU(inplace=True), nn.MaxPool2d(2)])
        self.features = nn.Sequential(*layers)
        classifier: list[nn.Module] = [
            nn.Flatten(),
            nn.Linear(c2 * 8 * 8, hidden_dim),
            nn.ReLU(inplace=True),
        ]
        if dropout > 0.0:
            classifier.append(nn.Dropout(dropout))
        classifier.append(nn.Linear(hidden_dim, num_classes))
        self.classifier = nn.Sequential(*classifier)
        self._init_weights()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))

    def _init_weights(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, in_planes: int, planes: int, stride: int = 1) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(in_planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != planes:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_planes, planes, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes),
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out = out + self.shortcut(x)
        return self.relu(out)


class ResNet18CIFAR(nn.Module):
    """CIFAR-sized ResNet-18 fallback for capacity calibration."""

    def __init__(self, num_classes: int = 10) -> None:
        super().__init__()
        self.in_planes = 64
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.layer1 = self._make_layer(64, 2, stride=1)
        self.layer2 = self._make_layer(128, 2, stride=2)
        self.layer3 = self._make_layer(256, 2, stride=2)
        self.layer4 = self._make_layer(512, 2, stride=2)
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512, num_classes)
        self._init_weights()

    def _make_layer(self, planes: int, blocks: int, stride: int) -> nn.Sequential:
        strides = [stride] + [1] * (blocks - 1)
        layers = []
        for current_stride in strides:
            layers.append(BasicBlock(self.in_planes, planes, current_stride))
            self.in_planes = planes
        return nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = self.pool(out)
        out = torch.flatten(out, 1)
        return self.fc(out)

    def _init_weights(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
            elif isinstance(module, nn.BatchNorm2d):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)
