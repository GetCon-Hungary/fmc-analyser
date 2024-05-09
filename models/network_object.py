"""Represents the network object model."""
import abc


class NetworkObject():
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name
        self.equal_with = []

    @abc.abstractmethod
    def get_size(self) -> int:
        pass
    
    @abc.abstractmethod
    def __eq__(self, value: object) -> bool:
        pass
