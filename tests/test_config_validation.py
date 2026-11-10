import argparse
from copy import deepcopy

import pytest

from src.utils.config import apply_cli_overrides, validate_config


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


def test_cli_can_classify_an_overridden_output_as_calibration() -> None:
    config = deepcopy(BASE_CONFIG)
    config["output_dir"] = "results/paper/candidate"
    config["reporting"] = {"run_class": "formal_measured"}
    args = argparse.Namespace(
        output_dir="results/calibration/candidate",
        run_class="calibration",
    )

    updated, overrides = apply_cli_overrides(config, args)

    assert updated["output_dir"] == "results/calibration/candidate"
    assert updated["reporting"]["run_class"] == "calibration"
    assert [item["path"] for item in overrides] == [
        "output_dir",
        "reporting.run_class",
    ]
    assert validate_config(updated) == []


def test_calibration_output_warns_if_mislabeled_formal() -> None:
    config = deepcopy(BASE_CONFIG)
    config["output_dir"] = "results/calibration/candidate"
    config["reporting"] = {"run_class": "formal_measured"}

    assert validate_config(config) == [
        "output_dir is under calibration but reporting.run_class is formal_measured; "
        "use --run_class calibration so this run cannot enter a formal summary."
    ]


def test_cli_can_set_ddpg_beta_bounds_for_calibration() -> None:
    config = deepcopy(BASE_CONFIG)
    config["defense"] = "hfedsa_ddpg"
    config["ddpg"] = {"state_dim": 39, "min_beta": 0.0, "max_beta": 1.0}
    args = argparse.Namespace(ddpg_min_beta=0.1, ddpg_max_beta=0.8)

    updated, overrides = apply_cli_overrides(config, args)

    assert updated["ddpg"]["min_beta"] == 0.1
    assert updated["ddpg"]["max_beta"] == 0.8
    assert [item["path"] for item in overrides] == [
        "ddpg.min_beta",
        "ddpg.max_beta",
    ]
    assert validate_config(updated) == []


def test_cli_can_set_hfedsa_role_confidence_for_calibration() -> None:
    config = deepcopy(BASE_CONFIG)
    config["defense"] = "hfedsa_ddpg"
    args = argparse.Namespace(
        role_confidence_mode="intensity_separation",
        role_confidence_power=1.5,
    )

    updated, overrides = apply_cli_overrides(config, args)

    assert updated["hfedsa"]["role_confidence_mode"] == "intensity_separation"
    assert updated["hfedsa"]["role_confidence_power"] == 1.5
    assert [item["path"] for item in overrides] == [
        "hfedsa.role_confidence_mode",
        "hfedsa.role_confidence_power",
    ]
    assert validate_config(updated) == []


def test_cli_can_set_server_learning_rate() -> None:
    config = deepcopy(BASE_CONFIG)
    args = argparse.Namespace(server_lr=0.7)

    updated, overrides = apply_cli_overrides(config, args)

    assert updated["federated"]["server_lr"] == 0.7
    assert [item["path"] for item in overrides] == ["federated.server_lr"]
    assert validate_config(updated) == []


@pytest.mark.parametrize(
    ("minimum", "maximum", "message"),
    [
        (-0.1, 1.0, "min_beta must be in"),
        (0.0, 1.1, "max_beta must be in"),
        (0.8, 0.2, "min_beta cannot exceed"),
    ],
)
def test_invalid_ddpg_beta_bounds_are_rejected(
    minimum: float,
    maximum: float,
    message: str,
) -> None:
    config = deepcopy(BASE_CONFIG)
    config["ddpg"] = {
        "state_dim": 39,
        "min_beta": minimum,
        "max_beta": maximum,
    }

    with pytest.raises(ValueError, match=message):
        validate_config(config)


def test_cli_can_set_backdoor_poison_fraction() -> None:
    config = deepcopy(BASE_CONFIG)
    config["attack"] = {
        "type": "backdoor_scaling",
        "poison_fraction": 1.0,
    }
    args = argparse.Namespace(poison_fraction=0.5)

    updated, overrides = apply_cli_overrides(config, args)

    assert updated["attack"]["poison_fraction"] == 0.5
    assert [item["path"] for item in overrides] == ["attack.poison_fraction"]
    assert validate_config(updated) == []


@pytest.mark.parametrize("poison_fraction", [-0.1, 1.1])
def test_invalid_backdoor_poison_fraction_is_rejected(poison_fraction: float) -> None:
    config = deepcopy(BASE_CONFIG)
    config["attack"] = {
        "type": "backdoor_scaling",
        "poison_fraction": poison_fraction,
    }

    with pytest.raises(ValueError, match="poison_fraction must be in"):
        validate_config(config)

