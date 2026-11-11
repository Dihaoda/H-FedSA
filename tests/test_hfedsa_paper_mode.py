from collections import OrderedDict

import numpy as np
import pytest
import torch

from src.defenses.ddpg_beta_agent import DDPGBetaAgent, DDPGBetaConfig
from src.defenses.hfedsa import HFedSAConfig, HFedSAStatic


def _update(values: list[float]):
    return OrderedDict(weight=torch.tensor(values, dtype=torch.float32))


def test_paper_features_match_equations() -> None:
    defense = HFedSAStatic(HFedSAConfig(feature_mode="paper"))
    root = torch.tensor([1.0, 0.0])
    updates = [(0, _update([1.0, 0.0])), (1, _update([0.0, 2.0])), (2, _update([-3.0, 0.0]))]

    features, cosines, norms, _, _ = defense._extract_features(updates, root, 1.0)

    np.testing.assert_allclose(features[:, 0], [1.0, 0.0, -1.0], atol=1e-6)
    np.testing.assert_allclose(features[:, 1], [1.0, 2.0, 3.0], atol=1e-6)
    np.testing.assert_allclose(features[:, 2], [1 / np.sqrt(2)] * 3, atol=1e-6)
    np.testing.assert_allclose(cosines, features[:, 0], atol=1e-6)
    np.testing.assert_allclose(norms, features[:, 1], atol=1e-6)


def test_full_gmm_returns_soft_posteriors_and_covariances() -> None:
    rng = np.random.default_rng(3)
    features = np.vstack(
        [
            rng.normal([0.9, 1.0, 0.8], 0.03, size=(12, 3)),
            rng.normal([0.2, 0.2, 0.7], 0.03, size=(12, 3)),
            rng.normal([-0.3, 3.0, 0.2], 0.03, size=(12, 3)),
        ]
    )
    defense = HFedSAStatic(
        HFedSAConfig(gmm_covariance_type="full", cluster_role_strategy="intensity_order")
    )

    posteriors, roles = defense._fit_gmm(features)

    assert posteriors.shape == (36, 3)
    np.testing.assert_allclose(posteriors.sum(axis=1), 1.0, atol=1e-6)
    assert defense.last_gmm_covariances.shape == (3, 3, 3)
    assert set(roles) == {"benign", "unseen", "malicious"}


def test_paper_cluster_roles_follow_intensity_order() -> None:
    centers = np.asarray([[0.8, 0.0, 0.7], [0.4, -2.0, 0.8], [-0.2, 3.0, 0.2]])
    defense = HFedSAStatic(HFedSAConfig(cluster_role_strategy="intensity_order"))

    benign, malicious = defense._assign_cluster_roles(centers)

    assert benign == 0
    assert malicious == 2


def test_role_confidence_softens_only_weak_intensity_separation() -> None:
    defense = HFedSAStatic(
        HFedSAConfig(role_confidence_mode="intensity_separation")
    )
    posteriors = np.eye(3, dtype=float)
    raw_posteriors = np.eye(3, dtype=float)
    features = np.asarray(
        [
            [0.8, 1.0, 0.8],
            [0.2, 0.5, 0.7],
            [-0.2, 1.1, 0.2],
        ]
    )

    adjusted = defense._apply_role_confidence(
        posteriors,
        features,
        raw_posteriors,
        benign_cluster=0,
        malicious_cluster=2,
    )

    assert defense.last_malicious_role_confidence == pytest.approx(1.0 / 11.0)
    assert adjusted[2, 0] == pytest.approx(10.0 / 11.0)
    assert adjusted[2, 2] == pytest.approx(1.0 / 11.0)
    np.testing.assert_allclose(adjusted.sum(axis=1), 1.0)


def test_hard_role_confidence_preserves_paper_posteriors() -> None:
    defense = HFedSAStatic(HFedSAConfig(role_confidence_mode="hard"))
    posteriors = np.eye(3, dtype=float)

    adjusted = defense._apply_role_confidence(
        posteriors,
        np.asarray([[0.8, 1.0, 0.8], [0.2, 0.5, 0.7], [-0.2, 1.1, 0.2]]),
        np.eye(3, dtype=float),
        benign_cluster=0,
        malicious_cluster=2,
    )

    np.testing.assert_array_equal(adjusted, posteriors)
    assert defense.last_malicious_role_confidence == 1.0


def test_attack_presence_gate_separates_weak_and_strong_intensity_gaps() -> None:
    defense = HFedSAStatic(
        HFedSAConfig(
            attack_presence_gate_enabled=True,
            attack_presence_intensity_ratio_threshold=3.0,
        )
    )
    responsibilities = np.eye(3, dtype=float)

    defense._update_attack_presence(
        np.asarray([[0.8, 1.0, 0.8], [0.2, 0.5, 0.7], [-0.2, 1.2, 0.2]]),
        responsibilities,
        benign_cluster=0,
        malicious_cluster=2,
    )
    assert defense.last_attack_presence_intensity_ratio == pytest.approx(1.2)
    assert not defense.last_attack_present
    assert defense.last_attack_presence_gate_triggered

    defense._update_attack_presence(
        np.asarray([[0.8, 1.0, 0.8], [0.2, 0.5, 0.7], [-0.2, 12.0, 0.2]]),
        responsibilities,
        benign_cluster=0,
        malicious_cluster=2,
    )
    assert defense.last_attack_presence_intensity_ratio == pytest.approx(12.0)
    assert defense.last_attack_present
    assert not defense.last_attack_presence_gate_triggered


def test_attack_absent_uniform_raw_bypasses_paper_weighting_and_root_normalization() -> None:
    defense = HFedSAStatic(
        HFedSAConfig(
            attack_presence_gate_enabled=True,
            attack_absent_aggregation="uniform_raw",
            normalize_update_to_root=True,
        )
    )
    posteriors = np.asarray(
        [
            [0.9, 0.05, 0.05],
            [0.05, 0.9, 0.05],
            [0.05, 0.05, 0.9],
        ],
        dtype=float,
    )

    def attack_absent_gmm(_features):
        defense.last_attack_presence_intensity_ratio = 1.2
        defense.last_attack_present = False
        defense.last_attack_presence_gate_triggered = True
        return posteriors, {"benign": 0, "unseen": 1, "malicious": 2}

    defense._fit_gmm = attack_absent_gmm
    updates = [
        (0, _update([1.0, 0.0])),
        (1, _update([3.0, 0.0])),
        (2, _update([5.0, 0.0])),
    ]

    aggregated, diagnostics = defense.aggregate(updates, root_update=_update([0.1, 0.0]))

    torch.testing.assert_close(aggregated["weight"], torch.tensor([3.0, 0.0]))
    assert [item["weight"] for item in diagnostics] == pytest.approx([1.0 / 3.0] * 3)
    assert all(item["p_malicious"] == 0.0 for item in diagnostics)
    assert diagnostics[2]["gmm_p_malicious"] == pytest.approx(0.9)
    assert all(item["attack_absent_passthrough"] for item in diagnostics)
    assert all(item["update_scale"] == 1.0 for item in diagnostics)


def test_paper_ddpg_state_has_expected_statistics() -> None:
    defense = HFedSAStatic(HFedSAConfig(beta_mode="ddpg"))
    defense.last_gmm_means = np.arange(9, dtype=float).reshape(3, 3)
    defense.last_gmm_covariances = np.arange(27, dtype=float).reshape(3, 3, 3)
    defense._previous_validation_loss = 0.75
    defense._last_validation_delta = 0.1
    defense.last_beta_trace = {"beta_explore": 0.2}

    state = defense._ddpg_state_vector()

    assert state.shape == (39,)
    np.testing.assert_allclose(state[-3:], [0.75, 0.1, 0.2])


def test_ddpg_rejects_silent_state_truncation() -> None:
    agent = DDPGBetaAgent(DDPGBetaConfig(state_dim=39), seed=0)

    with pytest.raises(ValueError, match="state_dim=39"):
        agent.select_beta(np.zeros(24, dtype=float), train=False)


class _RecordingAgent:
    def __init__(self) -> None:
        self.rewards: list[float] = []

    def observe(self, reward: float, next_state: np.ndarray) -> dict:
        assert next_state.shape == (39,)
        self.rewards.append(float(reward))
        return {"replay_size": len(self.rewards)}


def test_ddpg_reward_uses_only_root_validation_and_aggregation_diagnostics() -> None:
    agent = _RecordingAgent()
    defense = HFedSAStatic(
        HFedSAConfig(
            beta_mode="ddpg",
            ddpg_security_penalty=1.0,
            ddpg_residual_penalty=0.0,
            ddpg_smoothness_penalty=0.0,
        ),
        beta_agent=agent,
    )
    defense.last_beta_trace = {"beta_explore": 0.2, "previous_beta": 0.2}
    diagnostics = [
        {"weight": 0.4, "p_malicious": 0.75, "predicted_malicious": True},
        {"weight": 0.6, "p_malicious": 0.0, "predicted_malicious": False},
    ]

    defense.observe_round(validation_loss=1.0, validation_accuracy=0.0, diagnostics=diagnostics)
    trace = defense.observe_round(validation_loss=1.0, validation_accuracy=10.0, diagnostics=diagnostics)

    assert agent.rewards == pytest.approx([0.0, -0.2])
    assert trace["security_signal"] == pytest.approx(0.3)
    assert trace["security_signal_source"] == "aggregation_diagnostics"
    assert trace["predicted_malicious_mean_weight"] == pytest.approx(0.4)


def test_ddpg_empty_predicted_malicious_set_is_finite() -> None:
    agent = _RecordingAgent()
    defense = HFedSAStatic(
        HFedSAConfig(beta_mode="ddpg", ddpg_smoothness_penalty=0.0),
        beta_agent=agent,
    )
    defense.last_beta_trace = {"beta_explore": 0.2, "previous_beta": 0.2}
    diagnostics = [{"weight": 1.0, "p_malicious": 0.0, "predicted_malicious": False}]

    defense.observe_round(validation_loss=1.0, validation_accuracy=0.0, diagnostics=diagnostics)
    trace = defense.observe_round(validation_loss=1.0, validation_accuracy=0.0, diagnostics=diagnostics)

    assert trace["predicted_malicious_mean_weight"] == 0.0
    assert np.isfinite(trace["reward"])


def test_small_round_fallback_reports_normalized_weights() -> None:
    defense = HFedSAStatic(HFedSAConfig())
    updates = [(7, _update([1.0, 2.0])), (9, _update([3.0, 4.0]))]

    aggregated, diagnostics = defense.aggregate(updates, root_update=_update([1.0, 0.0]))

    torch.testing.assert_close(aggregated["weight"], torch.tensor([2.0, 3.0]))
    assert len(diagnostics) == 2
    assert sum(float(item["weight"]) for item in diagnostics) == pytest.approx(1.0)
    assert all(item["gmm_fallback_reason"] == "fewer_than_three_updates" for item in diagnostics)

