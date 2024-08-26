"""Represents the port model."""
from models.port_object import PortObject


class ICMPObject(PortObject):
    def __init__(self, id: str, name: str, icmp_type: str) -> None:
        super().__init__(id, name)
        self.icmp_type = icmp_type
        self.is_risky = False

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, ICMPObject):
            return self.icmp_type == __value.icmp_type
        else:
            return False

    def is_risky_port(self, risky_ports: dict) -> bool:
        return True

    def get_size(self) -> int:  # noqa: D102
        return 1