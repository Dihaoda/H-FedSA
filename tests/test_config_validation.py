from copy import deepcopy

import pytest

from src.utils.config import validate_config


BASE_CONFIG = {
    "dataset": {"name": "synthetic"},
    "model": {"name": "small_cnn"},
    "federated": {
        "num_clients": 10,
        "clients_per_round": 5,
        "rounds": 1,
        "local_epochs": 1,
        "batch_size": 4,
        "optimizer": "sgd",
        "server_optimizer": "fedavg",
        "malicious_ratio": 0.2,
        "unseen_ratio": 0.1,
        "root_size": 4,
    },
    "attack": {"type": "none"},
    "defense": "fedavg",
}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("num_clients", 0),
        ("clients_per_round", 0),
        ("rounds", 0),
        ("local_epochs", 0),
        ("batch_size", 0),
    ],
)
def test_non_positive_training_dimensions_are_rejected(field: str, value: int) -> None:
    config = deepcopy(BASE_CONFIG)
    config["federated"][field] = value
    with pytest.raises(ValueError, match=field):
        validate_config(config)


def test_disjoint_role_ratios_cannot_exceed_population() -> None:
    config = deepcopy(BASE_CONFIG)
    config["federated"]["malicious_ratio"] = 0.7
    config["federated"]["unseen_ratio"] = 0.4
    with pytest.raises(ValueError, match="cannot exceed 1"):
        validate_config(config)


def test_external_shift_requires_a_root_in_dry_run_validation() -> None:
    config = deepcopy(BASE_CONFIG)
    config["federated"]["unseen_shift"] = {"enabled": True, "type": "chars74k"}
    with pytest.raises(ValueError, match="data_root is required"):
        validate_config(config)


def test_attack_without_malicious_clients_emits_warning() -> None:
    config = deepcopy(BASE_CONFIG)
    config["attack"]["type"] = "trim_targeted"
    config["federated"]["malicious_ratio"] = 0.0
    assert validate_config(config) == [
        "attack.type='trim_targeted' is enabled but federated.malicious_ratio is zero."
    ]


@pytest.mark.parametrize("defense", ["fltrust", "hfedsa_static", "hfedsa_ddpg"])
def test_root_dependent_defenses_require_root_data(defense: str) -> None:
    config = deepcopy(BASE_CONFIG)
    config["defense"] = defense
    config["federated"]["root_size"] = 0

    with pytest.raises(ValueError, match="root_size must be positive"):
        validate_config(config)


def test_hfedsa_ddpg_rejects_non_paper_state_dimension() -> None:
    config = deepcopy(BASE_CONFIG)
    config["defense"] = "hfedsa_ddpg"
    config["ddpg"] = {"state_dim": 24}

    with pytest.raises(ValueError, match="state_dim must equal 39"):
        validate_config(config)


def test_hfedsa_small_round_warns_about_uniform_fallback() -> None:
    config = deepcopy(BASE_CONFIG)
    config["defenses"] = "hfedsa_static"
    config["federated"]["clients_per_round"] = 2

    assert validate_config(config) == [
        "H-FedSA needs at least three participating clients to fit its three-component GMM; "
        "smaller rounds use the documented uniform fallback."
    ]

