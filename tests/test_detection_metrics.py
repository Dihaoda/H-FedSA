from types import SimpleNamespace

from src.federated.trainer import FederatedExperiment


def test_paper_fpr_is_computed_on_unseen_clients_only() -> None:
    experiment = FederatedExperiment.__new__(FederatedExperiment)
    experiment.fed_data = SimpleNamespace(malicious_clients={2, 3}, unseen_clients={0, 1})
    diagnostics = [
        {"client_id": 0, "predicted_malicious": True},
        {"client_id": 1, "predicted_malicious": False},
        {"client_id": 2, "predicted_malicious": True},
        {"client_id": 3, "predicted_malicious": False},
        {"client_id": 4, "predicted_malicious": True},
        {"client_id": 5, "predicted_malicious": False},
    ]

    metrics = experiment._detection_metrics(diagnostics)

    assert metrics["detection_tpr"] == 0.5
    assert metrics["detection_fpr"] == 0.5
    assert metrics["detection_overall_fpr"] == 0.5


def test_detection_metrics_are_blank_for_non_detector() -> None:
    experiment = FederatedExperiment.__new__(FederatedExperiment)
    experiment.fed_data = SimpleNamespace(malicious_clients=set(), unseen_clients=set())

    assert experiment._detection_metrics([]) == {
        "detection_tpr": "",
        "detection_fpr": "",
        "detection_overall_fpr": "",
    }

