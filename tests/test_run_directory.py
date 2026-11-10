import csv
from datetime import datetime

from src.federated.trainer import FederatedExperiment
from src.main import _log_file_path


def test_run_directories_are_seeded_and_collision_resistant(tmp_path) -> None:
    experiment = FederatedExperiment.__new__(FederatedExperiment)
    experiment.config = {
        "experiment_name": "collision_test",
        "seed": 2026,
        "output_dir": str(tmp_path),
    }

    first = experiment._prepare_run_dir()
    second = experiment._prepare_run_dir()

    assert first != second
    assert "seed2026" in first.name
    assert (first / "config_resolved.yaml").is_file()
    assert (second / "config_resolved.yaml").is_file()


def test_log_paths_include_seed_and_microseconds(tmp_path) -> None:
    config = {
        "experiment_name": "collision_test",
        "seed": 2026,
        "log_dir": str(tmp_path),
    }

    first = _log_file_path(config, datetime(2026, 11, 10, 1, 2, 3, 4))
    second = _log_file_path(config, datetime(2026, 11, 10, 1, 2, 3, 5))

    assert first != second
    assert first.name == "collision_test_seed2026_20261110_010203_000004.log"


def test_partial_metrics_checkpoint_is_atomic_and_method_scoped(tmp_path) -> None:
    experiment = FederatedExperiment.__new__(FederatedExperiment)
    experiment.run_dir = tmp_path
    rows = [
        {
            "round": 10,
            "method": "hfedsa_ddpg",
            "dataset": "cifar10",
            "attack_type": "backdoor_scaling",
            "seed": 31415,
            "accuracy": 50.0,
            "error_rate": 50.0,
            "attack_success_rate": 2.0,
        }
    ]

    experiment._write_metrics_checkpoint("hfedsa/ddpg", rows)

    checkpoint = tmp_path / "metrics_partial_hfedsa_ddpg.csv"
    assert checkpoint.is_file()
    assert not (tmp_path / "metrics_partial_hfedsa_ddpg.csv.tmp").exists()
    with checkpoint.open(encoding="utf-8", newline="") as stream:
        saved = list(csv.DictReader(stream))
    assert saved[0]["round"] == "10"
    assert saved[0]["attack_success_rate"] == "2.0"

