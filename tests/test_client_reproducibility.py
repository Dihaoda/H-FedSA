from collections import OrderedDict

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from src.federated.client import Client


def _model_factory():
    return nn.Sequential(
        nn.Flatten(),
        nn.Linear(4, 8),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(8, 2),
    )


def test_local_training_seed_pairs_shuffle_and_dropout_across_runs() -> None:
    torch.manual_seed(5)
    initial_model = _model_factory()
    global_state = OrderedDict(
        (name, tensor.detach().cpu().clone()) for name, tensor in initial_model.state_dict().items()
    )
    dataset = TensorDataset(
        torch.arange(48, dtype=torch.float32).reshape(12, 1, 2, 2) / 48.0,
        torch.tensor([0, 1] * 6),
    )
    client = Client(
        client_id=3,
        dataloader=DataLoader(dataset, batch_size=3, shuffle=True),
        model_factory=_model_factory,
        device=torch.device("cpu"),
        num_classes=2,
    )

    first = client.train(global_state, 2, 0.05, training_seed=12345)
    second = client.train(global_state, 2, 0.05, training_seed=12345)

    assert all(torch.equal(first[name], second[name]) for name in first)

