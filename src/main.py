from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.data.datasets import build_federated_data
from src.federated.trainer import FederatedExperiment
from src.utils.config import apply_cli_overrides, config_to_yaml, load_config, parse_args, validate_config
from src.utils.logging import setup_logger
from src.utils.seed import set_seed


def _log_file_path(config: dict, now: datetime | None = None) -> Path:
    timestamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S_%f")
    experiment_name = config.get("experiment_name", "experiment")
    seed = int(config.get("seed", 0))
    return Path(config.get("log_dir", "logs")) / (
        f"{experiment_name}_seed{seed}_{timestamp}.log"
    )


def main() -> None:
    args = parse_args()
    config, overrides = apply_cli_overrides(load_config(args.config), args)
    warnings = validate_config(config)
    if args.dry_run:
        print("Dry run: final resolved config follows.\n")
        print(config_to_yaml(config))
        if overrides:
            print("CLI overrides:")
            for item in overrides:
                print(f"- {item['arg']} -> {item['path']}: {item['old']} -> {item['new']}")
        else:
            print("CLI overrides: none")
        for warning in warnings:
            print(f"Warning: {warning}")
        return

    set_seed(int(config["seed"]))

    log_file = _log_file_path(config)
    log_dir = log_file.parent
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = setup_logger(log_file)
    logger.info("Loaded config: %s", args.config)
    if overrides:
        for item in overrides:
            logger.info("CLI override %s -> %s: %r -> %r", item["arg"], item["path"], item["old"], item["new"])
    else:
        logger.info("CLI overrides: none")
    for warning in warnings:
        logger.warning(warning)

    fed_data = build_federated_data(config)
    experiment = FederatedExperiment(config, fed_data, logger)
    result = experiment.run()
    logger.info("Run complete: %s", result["run_dir"])
    logger.info("Summary: %s", result["summaries"])


if __name__ == "__main__":
    main()

