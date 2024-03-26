"""Represents the network class."""
from typing import Union

from models.network_object import NetworkObject
from netaddr import IPNetwork, IPRange


class Network(NetworkObject):
    def __init__(self, id: str, type: str, name: str, value: str) -> None:
        super().__init__(id, name)
        self.type = type
        self.value = self.create_network_value(value)
        self.size = self.value.size

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Network):
            return self.type == __value.type and self.value == __value.value
        else:
            return False

    def create_network_value(self, network_value: str) -> Union[IPNetwork, IPRange]:
        value = None
        if '-' in network_value:
            value = IPRange(network_value.split('-')[0], network_value.split('-')[1])
        else:
            value = IPNetwork(network_value)
        return value

    def get_size(self) -> int:
        return self.size
