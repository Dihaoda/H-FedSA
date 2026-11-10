import numpy as np

from src.federated.trainer import sample_participating_clients


def test_paper_sampling_preserves_round_role_ratios() -> None:
    malicious = set(range(10, 30))
    unseen = set(range(10))
    selected = sample_participating_clients(
        rng=np.random.default_rng(42),
        num_clients=100,
        clients_per_round=10,
        malicious_clients=malicious,
        unseen_clients=unseen,
        mode="paper",
    )

    assert len(selected) == 10
    assert len(set(selected)) == 10
    assert sum(client in malicious for client in selected) == 2
    assert sum(client in unseen for client in selected) == 1


def test_random_sampling_remains_available() -> None:
    selected = sample_participating_clients(
        rng=np.random.default_rng(7),
        num_clients=20,
        clients_per_round=5,
        malicious_clients=set(range(4)),
        unseen_clients={4, 5},
        mode="random",
    )

    assert len(selected) == 5
    assert len(set(selected)) == 5

