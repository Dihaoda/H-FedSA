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

