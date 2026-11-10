from src.federated.trainer import FederatedExperiment


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

