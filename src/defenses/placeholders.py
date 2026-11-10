from __future__ import annotations


class NotImplementedDefense:
    def __init__(self, name: str) -> None:
        self.name = name

    def aggregate(self, *args, **kwargs):
        raise NotImplementedError(
            f"{self.name} is reserved as an interface only. It is not implemented in the quick_dev baseline."
        )
