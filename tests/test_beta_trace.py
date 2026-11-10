import csv
from types import SimpleNamespace

from src.federated.trainer import FederatedExperiment


def test_beta_trace_preserves_reward_provenance(tmp_path) -> None:
    experiment = FederatedExperiment.__new__(FederatedExperiment)
    experiment.run_dir = tmp_path
    experiment.logger = SimpleNamespace(info=lambda *args, **kwargs: None)
    row = {
        "round": 2,
        "security_signal": 0.125,
        "security_signal_source": "aggregation_diagnostics",
        "validation_loss": 0.75,
        "validation_accuracy": 62.5,
        "validation_loss_improvement": 0.05,
    }

    experiment._write_beta_trace("hfedsa_ddpg", [row])

    with (tmp_path / "hfedsa_beta_trace_hfedsa_ddpg.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        saved = next(csv.DictReader(stream))
    assert saved["security_signal"] == "0.125"
    assert saved["security_signal_source"] == "aggregation_diagnostics"
    assert saved["validation_loss"] == "0.75"
    assert saved["validation_accuracy"] == "62.5"
    assert saved["validation_loss_improvement"] == "0.05"

