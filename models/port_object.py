"""Represents the port object model."""
import abc


class PortObject():
    def __init__(self, id: str, name: str) -> None:  # noqa: D107
        self.id = id
        self.name = name
        self.equal_with = []

    @abc.abstractmethod
    def get_size(self) -> int:  # noqa: D102
        pass
