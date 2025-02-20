"""Represents the network model."""
from typing import Union

from netaddr import IPNetwork

from models.network_object import NetworkObject


class Network(NetworkObject):
    def __init__(self, id: str, name: str, value: str) -> None:
        super().__init__(id, name)
        self.value = IPNetwork(value)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Network):
            return self.value == __value.value
        return False

    def get_size(self) -> int:
        return self.value.size
