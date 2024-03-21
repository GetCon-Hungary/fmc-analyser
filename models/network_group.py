"""Represents the network group class."""
from typing import Union

from models.network import Network


class NetworkGroup:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name
        self.networks: list[Union[Network, NetworkGroup]] = []
        self.depth = 0
        self.equal_with = ''

    def __eq__(self, __value: 'NetworkGroup') -> bool:
        counter = 0
        if len(self.networks) == len(__value.networks):
            for i in range(len(self.networks)):
                for j in range(len(__value.networks)):
                    if self.networks[i].__eq__(__value.networks[j]):
                        counter += 1
                        if counter == len(self.networks):
                            return True
            return False
        return False

    def flat_network_object_grp(self) -> list:
        final = []
        for network_obj in self.networks:
            if isinstance(network_obj, Network):
                final.append(network_obj)
            elif isinstance(network_obj, NetworkGroup):
                final.extend(network_obj.flat_network_object_grp())
        return final

    def get_network_depth(self) -> int:
        depth = 0
        for network_obj in self.networks:
            if isinstance(network_obj, NetworkGroup):
                depth += network_obj.get_network_depth()
                depth += 1
        return depth

    def get_size(self) -> int:
        summ = 0
        for network in self.networks:
            summ += network.get_size()
        return summ
