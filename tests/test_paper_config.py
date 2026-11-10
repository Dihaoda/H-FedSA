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
    assert config["hfedsa"]["normalization_mode"] == "root_norm"
    assert config["hfedsa"]["normalize_update_to_root"] is True
    assert config["hfedsa"]["gmm_covariance_type"] == "full"
    assert config["model"]["batchnorm"] is False
    assert config["ddpg"]["state_dim"] == 39
    assert config["attack"]["type"] == "backdoor_scaling"
    assert config["reporting"]["paper_attack_key"] == "scaling"
    assert config["performance"]["client_num_workers"] == 0
    assert config["performance"]["eval_num_workers"] == 2


def test_cifar10_clean_manifest_is_fixed_before_multiseed_runs() -> None:
    config = load_config(Path("configs/paper/cifar10_iid_clean.yaml"))

    validate_config(config)
    assert config["federated"]["num_clients"] == 100
    assert config["federated"]["clients_per_round"] == 10
    assert config["federated"]["rounds"] == 250
    assert config["federated"]["local_epochs"] == 5
    assert config["federated"]["server_optimizer"] == "fedavg"
    assert config["federated"]["malicious_ratio"] == 0.0
    assert config["federated"]["unseen_ratio"] == 0.1
    assert config["federated"]["unseen_data_fraction"] == 0.4
    assert config["federated"]["eval_every"] == 10
    assert config["federated"]["unseen_shift"]["type"] == "cifar10_c"
    assert config["attack"]["type"] == "no_attack"
    assert config["reporting"]["preregistered_seeds"] == [2026, 2027, 2028, 2029, 2030]
    assert config["performance"]["client_num_workers"] == 0
    assert config["performance"]["eval_num_workers"] == 2


def test_attack_calibration_is_independent_and_not_formal() -> None:
    config = load_config(
        Path("configs/calibration/cifar10_iid_hfedsa_ddpg_backdoor_seed31415.yaml")
    )

    validate_config(config)
    assert config["seed"] == 31415
    assert config["federated"]["unseen_ratio"] == 0.1
    assert config["federated"]["unseen_data_fraction"] == 0.4
    assert config["attack"]["type"] == "backdoor_scaling"
    assert config["attack"]["target_label"] == 2
    assert config["attack"]["scale_factor"] == 8.0
    assert config["attack"]["poison_fraction"] == 1.0
    assert config["reporting"]["run_class"] == "calibration"
    assert config["reporting"]["excluded_from_formal_summary"] is True


def test_strict_attack_calibration_uses_direct_server_update() -> None:
    config = load_config(
        Path(
            "configs/calibration/"
            "cifar10_iid_hfedsa_ddpg_backdoor_strict_seed31415.yaml"
        )
    )

    validate_config(config)
    assert config["seed"] == 31415
    assert config["federated"]["server_optimizer"] == "fedavg"
    assert config["federated"]["unseen_ratio"] == 0.1
    assert config["attack"]["target_label"] == 2
    assert config["attack"]["scale_factor"] == 8.0
    assert config["reporting"]["run_class"] == "calibration"
    assert config["reporting"]["excluded_from_formal_summary"] is True

