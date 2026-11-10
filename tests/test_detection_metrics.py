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


def test_detection_rates_are_blank_when_round_has_no_relevant_class() -> None:
    experiment = FederatedExperiment.__new__(FederatedExperiment)
    experiment.fed_data = SimpleNamespace(malicious_clients={2}, unseen_clients={0})

    metrics = experiment._detection_metrics(
        [{"client_id": 4, "predicted_malicious": False}]
    )

    assert metrics["detection_tpr"] == ""
    assert metrics["detection_fpr"] == ""
    assert metrics["detection_overall_fpr"] == 0.0


def test_overall_fpr_is_blank_when_only_malicious_clients_participate() -> None:
    experiment = FederatedExperiment.__new__(FederatedExperiment)
    experiment.fed_data = SimpleNamespace(malicious_clients={2}, unseen_clients=set())

    metrics = experiment._detection_metrics(
        [{"client_id": 2, "predicted_malicious": True}]
    )

    assert metrics["detection_tpr"] == 1.0
    assert metrics["detection_fpr"] == ""
    assert metrics["detection_overall_fpr"] == ""

