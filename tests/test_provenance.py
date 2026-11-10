import torch

from src.federated.trainer import FederatedExperiment


def test_runtime_provenance_records_environment_and_config_hash(monkeypatch) -> None:
    monkeypatch.setenv("HFEDSA_SOURCE_REVISION", "github-head-test")
    experiment = FederatedExperiment.__new__(FederatedExperiment)
    experiment.config = {"seed": 2026, "dataset": {"name": "synthetic"}}
    experiment.device = torch.device("cpu")

    provenance = experiment._runtime_provenance()

    assert len(provenance["config_sha256"]) == 64
    assert provenance["python"]
    assert provenance["torch"] == torch.__version__
    assert provenance["cuda_available"] == torch.cuda.is_available()
    assert provenance["gpu"] == "NA"
    assert provenance["declared_source_revision"] == "github-head-test"

