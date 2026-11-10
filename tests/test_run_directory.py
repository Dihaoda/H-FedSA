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

