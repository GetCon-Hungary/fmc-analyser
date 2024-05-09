"""Represents the host model."""

from netaddr import IPNetwork

from models.network_object import NetworkObject


class Host(NetworkObject):
    def __init__(self, id: str, name: str, value: str) -> None:
        super().__init__(id, name)
        self.value = IPNetwork(value)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Host):
            return self.value == __value.value
        return False

    def get_size(self) -> int:
        return self.value.size
