"""Represents the network group class."""
from models.port_object import PortObject
from models.port import Port


class PortGroup(PortObject):
    def __init__(self, id: str, name: str) -> None:
        super().__init__(id, name)
        self.ports: list[Port] = []
        
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, PortGroup):
            counter = 0
            if len(self.ports) == len(__value.ports):
                for i in range(len(self.ports)):
                    for j in range(len(__value.ports)):
                        if self.ports[i].__eq__(__value.ports[j]):
                            counter += 1
                            if counter == len(self.ports):
                                return True
                return False
        return False

    def flat_port_object_grp(self) -> list[Port]:
        return self.ports

    def get_size(self) -> int:
        return sum(port.get_size() for port in self.ports)
