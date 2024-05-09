"""Represents the port model."""
from models.port_object import PortObject


class Port(PortObject):
    def __init__(self, id: str, name: str, protocol: str, port: str) -> None:
        super().__init__(id, name)
        self.protocol = protocol
        self.port = port
        self.is_risky = False

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Port):
            return self.protocol == __value.protocol and self.port == __value.port
        else:
            return False

    def is_risky_port(self, risky_ports: dict) -> bool:
        for protocol, ports in risky_ports.items():
            if ports is not None:
                for port in ports:
                    if self.protocol == protocol and self.port == str(port):
                        return True
        return False

    def get_size(self) -> int:  # noqa: D102
        size = 1
        if self.port == '':
            size = 65535
            self.port = 'Any'
        elif '-' in self.port:
            size = int(self.port.split('-')[1]) - (int(self.port.split('-')[0]) - 1)
        return size