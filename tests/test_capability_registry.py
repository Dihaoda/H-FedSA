from copy import deepcopy

import pytest

from src.defenses.factory import build_defense
from src.utils.config import ATTACKS, DEFENSES, validate_config


BASE_CONFIG = {
    "seed": 11,
    "dataset": {"name": "synthetic", "num_classes": 3},
    "model": {"name": "small_cnn"},
    "federated": {
        "num_clients": 10,
        "clients_per_round": 5,
        "rounds": 1,
        "local_epochs": 1,
        "batch_size": 4,
        "learning_rate": 0.01,
        "optimizer": "sgd",
        "server_optimizer": "fedavg",
        "malicious_ratio": 0.2,
        "unseen_ratio": 0.1,
        "root_size": 4,
    },
    "attack": {"type": "none"},
    "defense": "fedavg",
    "ddpg": {"state_dim": 39, "hidden_dim": 8, "replay_capacity": 8, "batch_size": 2},
}


@pytest.mark.parametrize("attack", sorted(ATTACKS))
def test_every_registered_attack_passes_validation(attack: str) -> None:
    config = deepcopy(BASE_CONFIG)
    config["attack"]["type"] = attack
    assert validate_config(config) == []


@pytest.mark.parametrize("defense", sorted(DEFENSES))
def test_every_registered_defense_builds_a_runnable_aggregator(defense: str) -> None:
    config = deepcopy(BASE_CONFIG)
    config["defense"] = defense
    assert validate_config(config) == []
    aggregator = build_defense(defense, config)
    assert callable(aggregator.aggregate)

