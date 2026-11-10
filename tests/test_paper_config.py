from pathlib import Path

from src.utils.config import load_config, validate_config


def test_cifar10_paper_config_matches_protocol() -> None:
    config_path = Path("configs/paper/cifar10_iid_hfedsa_ddpg_scaling.yaml")
    config = load_config(config_path)

    assert validate_config(config) == [
        "mixed_precision is enabled; it is used only when the resolved device is CUDA."
    ]
    assert config["federated"]["num_clients"] == 100
    assert config["federated"]["clients_per_round"] == 10
    assert config["federated"]["malicious_ratio"] == 0.2
    assert config["federated"]["unseen_ratio"] == 0.1
    assert config["federated"]["unseen_data_fraction"] == 0.4
    assert config["federated"]["unseen_shift"]["corruptions"] == [
        "gaussian_noise",
        "shot_noise",
    ]
    assert config["hfedsa"]["feature_mode"] == "paper"
    assert config["hfedsa"]["formula_mode"] == "paper"
    assert config["hfedsa"]["gmm_covariance_type"] == "full"
    assert config["ddpg"]["state_dim"] == 39

