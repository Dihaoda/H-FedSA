import csv

import pytest

from src.utils.results import attach_paper_target, read_final_rows, summarize_final_rows


FIELDS = [
    "round",
    "method",
    "dataset",
    "attack_type",
    "seed",
    "accuracy",
    "error_rate",
    "attack_success_rate",
    "detection_tpr",
    "detection_fpr",
    "detection_overall_fpr",
]


def _write_metrics(path, seed: int, final_error: float) -> None:
    path.parent.mkdir(parents=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "round": 1,
                "method": "fedavg",
                "dataset": "cifar10",
                "attack_type": "no_attack",
                "seed": seed,
                "accuracy": 50.0,
                "error_rate": 50.0,
                "attack_success_rate": "NA",
                "detection_tpr": 0.5,
                "detection_fpr": 0.25,
                "detection_overall_fpr": 0.1,
            }
        )
        writer.writerow(
            {
                "round": 250,
                "method": "fedavg",
                "dataset": "cifar10",
                "attack_type": "no_attack",
                "seed": seed,
                "accuracy": 100.0 - final_error,
                "error_rate": final_error,
                "attack_success_rate": "NA",
                "detection_tpr": 0.8,
                "detection_fpr": 0.2,
                "detection_overall_fpr": 0.05,
            }
        )


def test_summary_uses_every_seed_and_only_final_round(tmp_path) -> None:
    _write_metrics(tmp_path / "seed_a" / "metrics.csv", 2026, 14.8)
    _write_metrics(tmp_path / "seed_b" / "metrics.csv", 2027, 15.2)

    summary = summarize_final_rows(read_final_rows([tmp_path]))[0]
    compared = attach_paper_target(summary, {"error_mean": 15.0, "error_std": 0.3}, 5)

    assert summary["seeds"] == [2026, 2027]
    assert summary["rounds"] == [250, 250]
    assert summary["error_rate"]["mean"] == pytest.approx(15.0)
    assert summary["error_rate"]["sample_std"] == pytest.approx(0.2828427)
    assert summary["detection_tpr"]["mean"] == pytest.approx(0.8)
    assert summary["detection_fpr"]["mean"] == pytest.approx(0.2)
    assert summary["detection_overall_fpr"]["mean"] == pytest.approx(0.05)
    assert compared["error_mean_gap"] == pytest.approx(0.0)
    assert compared["complete"] is False


def test_summary_rejects_duplicate_seed_selection(tmp_path) -> None:
    _write_metrics(tmp_path / "run_a" / "metrics.csv", 2026, 14.8)
    _write_metrics(tmp_path / "run_b" / "metrics.csv", 2026, 14.9)

    with pytest.raises(ValueError, match="Duplicate seeds"):
        summarize_final_rows(read_final_rows([tmp_path]))

