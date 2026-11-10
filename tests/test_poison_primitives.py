from collections import OrderedDict

import torch

from src.attacks.poison import poison_labels, poison_update


def test_label_flip_aliases_have_identical_effect() -> None:
    labels = torch.tensor([0, 2, 4])
    expected = torch.tensor([4, 2, 0])

    assert torch.equal(poison_labels(labels, 5, "label_flip"), expected)
    assert torch.equal(poison_labels(labels, 5, "LABEL_FLIPPING"), expected)


def test_scaling_preserves_non_floating_buffer_dtype() -> None:
    update = OrderedDict(
        weight=torch.tensor([1.0, -2.0]),
        num_batches_tracked=torch.tensor(0, dtype=torch.long),
    )

    poisoned = poison_update(update, "backdoor_scaling", 10.0)

    torch.testing.assert_close(poisoned["weight"], torch.tensor([10.0, -20.0]))
    assert poisoned["num_batches_tracked"].dtype == torch.long
    assert poisoned["num_batches_tracked"].item() == 0

