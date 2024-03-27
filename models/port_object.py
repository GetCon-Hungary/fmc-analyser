"""Represents the port object class."""
import abc

class PortObject():
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name
        self.equal_with = []
    
    @abc.abstractmethod
    def get_size(self) -> int:
        pass