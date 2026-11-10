from __future__ import annotations

import argparse
import copy
from pathlib import Path
from typing import Any

import yaml

DATASETS = {"cifar10", "femnist", "gtsrb", "stanford_cars", "stanfordcars", "synthetic"}
DEFENSES = {
    "fedavg",
    "fltrust",
    "rfa",
    "hfedsa",
    "hfedsa_static",
    "hfedsa_base",
    "hfedsa_ema",
    "hfedsa_ema_normroot",
    "hfedsa_ddpg",
    "hfedsa_ddpg_normroot",
    "hfedsa_ddpg_normroot_retention",
    "safefl",
    "msguard",
}
ATTACKS = {
    "none",
    "no_attack",
    "label_flip",
    "label_flipping",
    "scaling",
    "backdoor_scaling",
    "adaptive_feature_matched",
    "krum_targeted",
    "trim_targeted",
    "poisafl",
}
MODELS = {
    "small_cnn",
    "paper_cnn",
    "resnet18_cifar",
    "resnet18_gtsrb",
    "gtsrb_resnet18",
    "resnet18_stanford_cars",
    "stanford_cars_resnet18",
    "resnet18_imagenet",
    "gtsrb_cnn",
    "simple_gtsrb_cnn",
    "femnist_cnn",
    "femnist_lightweight_cnn",
}
SERVER_OPTIMIZERS = {"fedavg", "fedavgm", "fedadam"}
LOCAL_OPTIMIZERS = {"sgd", "adam", "adamw"}
UNSEEN_SHIFT_TYPES = {
    "none",
    "off",
    "gaussian_noise",
    "brightness",
    "gaussian_noise_brightness",
    "cifar10_c",
    "cifar10c",
    "chars74k",
    "ctsdb",
    "gtsdb",
    "compcars",
    "imagefolder",
    "mapped_imagefolder",
}
EXTERNAL_SHIFT_TYPES = {
    "cifar10_c",
    "cifar10c",
    "chars74k",
    "ctsdb",
    "gtsdb",
    "compcars",
    "imagefolder",
    "mapped_imagefolder",
}


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    if not isinstance(config, dict):
        raise ValueError(f"Config must be a mapping: {config_path}")
    config["_config_path"] = str(config_path)
    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run H-FedSA federated experiments with YAML config plus optional CLI overrides."
    )
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config.")
    parser.add_argument("--dry_run", action="store_true", help="Load config, apply CLI overrides, validate, and exit without training.")

    parser.add_argument("--dataset", type=str, help="Dataset name, e.g. cifar10/femnist/gtsrb/stanford_cars.")
    parser.add_argument("--data_root", type=str, help="Dataset root/cache path. Overrides dataset.data_root.")
    parser.add_argument("--output_dir", type=str, help="Directory where run outputs are saved.")
    parser.add_argument(
        "--run_class",
        type=str,
        help="Reporting classification, e.g. calibration/formal_measured/smoke.",
    )
    parser.add_argument("--seed", type=int, help="Random seed.")
    parser.add_argument("--num_clients", type=int, help="Total number of federated clients.")
    parser.add_argument("--clients_per_round", type=int, help="Number of selected clients per communication round.")
    parser.add_argument("--rounds", type=int, help="Federated communication rounds.")
    parser.add_argument("--local_epochs", type=int, help="Local training epochs per selected client.")
    parser.add_argument("--batch_size", type=int, help="Client batch size.")
    parser.add_argument("--learning_rate", type=float, help="Local optimizer learning rate.")
    parser.add_argument("--local_optimizer", type=str, help="Local optimizer, e.g. sgd/adam/adamw.")
    parser.add_argument("--server_optimizer", type=str, help="Server optimizer, e.g. fedavg/fedavgm/fedadam.")
    parser.add_argument("--defense", type=str, help="Defense method or comma-separated methods, e.g. fedavg,hfedsa_ddpg_normroot.")
    parser.add_argument(
        "--attack_type",
        type=str,
        help=(
            "Attack type: no_attack/label_flipping/scaling/backdoor_scaling/"
            "krum_targeted/trim_targeted/adaptive_feature_matched/poisafl."
        ),
    )
    parser.add_argument("--malicious_ratio", type=float, help="Fraction of malicious clients.")
    parser.add_argument("--scaling_factor", type=float, help="Scaling factor for scaling/backdoor_scaling attacks.")
    parser.add_argument(
        "--ddpg_min_beta",
        type=float,
        help="Lower bound for the DDPG exploration action beta.",
    )
    parser.add_argument(
        "--ddpg_max_beta",
        type=float,
        help="Upper bound for the DDPG exploration action beta.",
    )
    parser.add_argument("--model", type=str, help="Model name, e.g. paper_cnn/resnet18_gtsrb/femnist_cnn.")
    parser.add_argument("--iid", nargs="?", const="true", type=parse_bool, help="Set federated.iid true/false. If value is omitted, true is used.")
    parser.add_argument("--non_iid", action="store_true", default=None, help="Shortcut for --iid false.")
    parser.add_argument("--alpha", type=float, help="Dirichlet non-IID alpha. Overrides federated.non_iid_alpha.")
    parser.add_argument("--quick_dev", type=parse_bool, help="Enable/disable dataset quick_dev mode.")
    parser.add_argument("--eval_every", type=int, help="Evaluate every N rounds.")
    parser.add_argument("--diagnostics_every", type=int, help="Write detailed client diagnostics every N rounds.")
    parser.add_argument("--device", type=str, help="Device string: auto/cpu/cuda/cuda:0.")
    parser.add_argument("--mixed_precision", type=parse_bool, help="Enable/disable CUDA automatic mixed precision.")
    return parser.parse_args()


def apply_cli_overrides(config: dict[str, Any], args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return a config copy with explicit command-line overrides applied."""
    updated = copy.deepcopy(config)
    overrides: list[dict[str, Any]] = []

    mapping: list[tuple[str, tuple[str, ...]]] = [
        ("dataset", ("dataset", "name")),
        ("data_root", ("dataset", "data_root")),
        ("output_dir", ("output_dir",)),
        ("run_class", ("reporting", "run_class")),
        ("seed", ("seed",)),
        ("num_clients", ("federated", "num_clients")),
        ("clients_per_round", ("federated", "clients_per_round")),
        ("rounds", ("federated", "rounds")),
        ("local_epochs", ("federated", "local_epochs")),
        ("batch_size", ("federated", "batch_size")),
        ("learning_rate", ("federated", "learning_rate")),
        ("local_optimizer", ("federated", "optimizer")),
        ("server_optimizer", ("federated", "server_optimizer")),
        ("attack_type", ("attack", "type")),
        ("malicious_ratio", ("federated", "malicious_ratio")),
        ("scaling_factor", ("attack", "scale_factor")),
        ("ddpg_min_beta", ("ddpg", "min_beta")),
        ("ddpg_max_beta", ("ddpg", "max_beta")),
        ("model", ("model", "name")),
        ("alpha", ("federated", "non_iid_alpha")),
        ("quick_dev", ("dataset", "quick_dev")),
        ("eval_every", ("federated", "eval_every")),
        ("diagnostics_every", ("diagnostics", "client_detail_every")),
        ("device", ("device",)),
        ("mixed_precision", ("performance", "mixed_precision")),
    ]
    for cli_name, path in mapping:
        value = getattr(args, cli_name, None)
        if value is not None:
            _set_path(updated, path, value, cli_name, overrides)

    if getattr(args, "iid", None) is not None and getattr(args, "non_iid", None):
        raise ValueError("Use either --iid or --non_iid, not both.")
    if getattr(args, "iid", None) is not None:
        _set_path(updated, ("federated", "iid"), bool(args.iid), "iid", overrides)
    if getattr(args, "non_iid", None):
        _set_path(updated, ("federated", "iid"), False, "non_iid", overrides)

    defense_value = getattr(args, "defense", None)
    if defense_value is not None:
        defenses = [item.strip() for item in str(defense_value).split(",") if item.strip()]
        if not defenses:
            raise ValueError("--defense cannot be empty.")
        _set_path(updated, ("defense",), defenses[0], "defense", overrides)
        _set_path(updated, ("defenses",), defenses, "defense", overrides)

    updated["_cli_overrides"] = overrides
    return updated, overrides


def validate_config(config: dict[str, Any]) -> list[str]:
    """Return warnings for recognized-but-suspicious settings; raise for unsupported key choices."""
    errors = []
    warnings = []
    dataset = str(config.get("dataset", {}).get("name", "")).lower()
    if dataset and dataset not in DATASETS:
        errors.append(f"Unsupported dataset '{dataset}'. Known: {sorted(DATASETS)}")
    configured_defenses = config.get("defenses")
    if isinstance(configured_defenses, str):
        defenses = [configured_defenses]
    elif configured_defenses:
        defenses = list(configured_defenses)
    else:
        defenses = [config.get("defense", "fedavg")]
    defense_keys = {str(defense).lower() for defense in defenses}
    for defense in defenses:
        key = str(defense).lower()
        if key not in DEFENSES:
            errors.append(f"Unsupported defense '{key}'. Known: {sorted(DEFENSES)}")
    attack = str(config.get("attack", {}).get("type", "none")).lower()
    if attack not in ATTACKS:
        errors.append(f"Unsupported attack_type '{attack}'. Known: {sorted(ATTACKS)}")
    model = str(config.get("model", {}).get("name", "small_cnn")).lower()
    if model not in MODELS:
        errors.append(f"Unsupported model '{model}'. Known: {sorted(MODELS)}")
    local_optimizer = str(config.get("federated", {}).get("optimizer", "sgd")).lower()
    if local_optimizer not in LOCAL_OPTIMIZERS:
        errors.append(f"Unsupported local_optimizer '{local_optimizer}'. Known: {sorted(LOCAL_OPTIMIZERS)}")
    server_optimizer = str(config.get("federated", {}).get("server_optimizer", "fedavg")).lower()
    if server_optimizer not in SERVER_OPTIMIZERS:
        errors.append(f"Unsupported server_optimizer '{server_optimizer}'. Known: {sorted(SERVER_OPTIMIZERS)}")
    if int(config.get("federated", {}).get("clients_per_round", 1)) > int(config.get("federated", {}).get("num_clients", 1)):
        errors.append("federated.clients_per_round cannot exceed federated.num_clients.")
    fed_cfg = config.get("federated", {})
    positive_integer_fields = ("num_clients", "clients_per_round", "rounds", "local_epochs", "batch_size")
    for field in positive_integer_fields:
        if int(fed_cfg.get(field, 1)) <= 0:
            errors.append(f"federated.{field} must be positive.")
    if int(fed_cfg.get("root_size", 0)) < 0:
        errors.append("federated.root_size cannot be negative.")
    root_dependent_defense = any(
        key == "fltrust" or key.startswith("hfedsa") for key in defense_keys
    )
    if root_dependent_defense and int(fed_cfg.get("root_size", 0)) <= 0:
        errors.append(
            "federated.root_size must be positive for FLTrust and H-FedSA defenses."
        )
    hfedsa_enabled = any(key.startswith("hfedsa") for key in defense_keys)
    if hfedsa_enabled and int(fed_cfg.get("clients_per_round", 1)) < 3:
        warnings.append(
            "H-FedSA needs at least three participating clients to fit its three-component GMM; "
            "smaller rounds use the documented uniform fallback."
        )
    hfedsa_cfg = config.get("hfedsa", {})
    ddpg_enabled = any(key.startswith("hfedsa_ddpg") for key in defense_keys) or (
        hfedsa_enabled and str(hfedsa_cfg.get("beta_mode", "static")).lower() == "ddpg"
    )
    if ddpg_enabled and int(config.get("ddpg", {}).get("state_dim", 39)) != 39:
        errors.append(
            "ddpg.state_dim must equal 39 for the paper-aligned H-FedSA state "
            "(9 GMM means, 27 covariance values, and 3 validation/action values)."
        )
    ddpg_cfg = config.get("ddpg", {})
    ddpg_min_beta = float(ddpg_cfg.get("min_beta", 0.0))
    ddpg_max_beta = float(ddpg_cfg.get("max_beta", 1.0))
    if not 0.0 <= ddpg_min_beta <= 1.0:
        errors.append("ddpg.min_beta must be in [0, 1].")
    if not 0.0 <= ddpg_max_beta <= 1.0:
        errors.append("ddpg.max_beta must be in [0, 1].")
    if ddpg_min_beta > ddpg_max_beta:
        errors.append("ddpg.min_beta cannot exceed ddpg.max_beta.")
    malicious_ratio = float(fed_cfg.get("malicious_ratio", 0.0))
    unseen_ratio = float(fed_cfg.get("unseen_ratio", 0.0))
    if not 0.0 <= malicious_ratio <= 1.0:
        errors.append("federated.malicious_ratio must be in [0, 1].")
    if not 0.0 <= unseen_ratio <= 1.0:
        errors.append("federated.unseen_ratio must be in [0, 1].")
    if malicious_ratio + unseen_ratio > 1.0 + 1e-12:
        errors.append("federated.malicious_ratio + federated.unseen_ratio cannot exceed 1.")
    unseen_fraction = float(fed_cfg.get("unseen_data_fraction", fed_cfg.get("unseen_shift", {}).get("fraction", 1.0)))
    if not 0.0 <= unseen_fraction <= 1.0:
        errors.append("federated.unseen_data_fraction must be in [0, 1].")
    shift_cfg = fed_cfg.get("unseen_shift", {})
    if bool(shift_cfg.get("enabled", False)):
        shift_type = str(shift_cfg.get("type", "gaussian_noise")).lower()
        if shift_type not in UNSEEN_SHIFT_TYPES:
            errors.append(f"Unsupported unseen_shift.type '{shift_type}'. Known: {sorted(UNSEEN_SHIFT_TYPES)}")
        if shift_type in EXTERNAL_SHIFT_TYPES and not (
            shift_cfg.get("data_root") or shift_cfg.get("root") or config.get("dataset", {}).get("cifar10_c_root")
        ):
            errors.append(f"federated.unseen_shift.data_root is required for external shift '{shift_type}'.")
    if attack not in {"none", "no_attack"} and malicious_ratio <= 0.0:
        warnings.append(f"attack.type='{attack}' is enabled but federated.malicious_ratio is zero.")
    output_parts = {part.lower() for part in Path(str(config.get("output_dir", ""))).parts}
    run_class = str(config.get("reporting", {}).get("run_class", "unspecified")).lower()
    if "calibration" in output_parts and run_class == "formal_measured":
        warnings.append(
            "output_dir is under calibration but reporting.run_class is formal_measured; "
            "use --run_class calibration so this run cannot enter a formal summary."
        )
    performance_cfg = config.get("performance", {})
    client_workers = int(performance_cfg.get("client_num_workers", performance_cfg.get("num_workers", 0)))
    if len(defenses) > 1 and client_workers > 0 and bool(performance_cfg.get("persistent_workers", False)):
        warnings.append(
            "Multiple defenses with persistent client DataLoader workers can break paired augmentation randomness; "
            "set performance.client_num_workers=0 for formal comparisons."
        )
    if errors:
        raise ValueError("\n".join(errors))
    if bool(config.get("performance", {}).get("mixed_precision", False)):
        warnings.append("mixed_precision is enabled; it is used only when the resolved device is CUDA.")
    return warnings


def config_to_yaml(config: dict[str, Any]) -> str:
    return yaml.safe_dump(config, sort_keys=False, allow_unicode=True)


def parse_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Expected boolean value, got '{value}'.")


def _set_path(config: dict[str, Any], path: tuple[str, ...], value: Any, cli_name: str, overrides: list[dict[str, Any]]) -> None:
    cursor: dict[str, Any] = config
    for key in path[:-1]:
        child = cursor.get(key)
        if not isinstance(child, dict):
            child = {}
            cursor[key] = child
        cursor = child
    leaf = path[-1]
    old_value = copy.deepcopy(cursor.get(leaf, None))
    cursor[leaf] = value
    overrides.append(
        {
            "arg": f"--{cli_name}",
            "path": ".".join(path),
            "old": old_value,
            "new": copy.deepcopy(value),
        }
    )

