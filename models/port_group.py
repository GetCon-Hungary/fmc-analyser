"""Represents the network group model."""
from models.port import Port
from models.port_object import PortObject


class PortGroup(PortObject):
    def __init__(self, id: str, name: str) -> None:
        super().__init__(id, name)
        self.ports: list[Port] = []

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, PortGroup):
            if len(self.ports) == len(__value.ports):
                self.ports.sort(key=lambda x: x.name)
                __value.ports.sort(key=lambda x: x.name)
                if self.ports == __value.ports:
                    return True
                return False
        return False

    def flat_port_object_grp(self) -> list[Port]:
        return self.ports

    def get_size(self) -> int:
        return sum(port.get_size() for port in self.ports)
