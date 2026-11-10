from collections import OrderedDict

import pytest
import torch

from src.defenses.fltrust import FLTrust
from src.federated.tensor_ops import flatten_update


def _update(values: list[float]):
    return OrderedDict(weight=torch.tensor(values, dtype=torch.float32))


def test_fltrust_diagnostics_report_effective_normalized_weights() -> None:
    defense = FLTrust()
    updates = [
        (0, _update([1.0, 0.0])),
        (1, _update([0.5, 0.5])),
        (2, _update([-1.0, 0.0])),
    ]
    aggregate, diagnostics = defense.aggregate(updates, _update([1.0, 0.0]))

    assert torch.isfinite(flatten_update(aggregate)).all()
    assert sum(float(item["weight"]) for item in diagnostics) == pytest.approx(1.0)
    assert diagnostics[2]["weight"] == 0.0
    assert diagnostics[2]["predicted_malicious"] is True


def test_fltrust_zero_root_fallback_matches_uniform_aggregation() -> None:
    updates = [(0, _update([1.0, 0.0])), (1, _update([0.0, 1.0]))]
    aggregate, diagnostics = FLTrust().aggregate(updates, _update([0.0, 0.0]))

    torch.testing.assert_close(flatten_update(aggregate), torch.tensor([0.5, 0.5]))
    assert [item["weight"] for item in diagnostics] == [0.5, 0.5]
    assert all(item["fallback_reason"] == "zero_root_update" for item in diagnostics)

