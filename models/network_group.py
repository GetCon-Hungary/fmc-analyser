"""Represents the network group class."""

from models.network_object import NetworkObject
from models.network import Network


class NetworkGroup(NetworkObject):
    def __init__(self, id: str, name: str) -> None:
        super().__init__(id, name)
        self.networks: list[NetworkObject] = []
        self.depth = 0
        
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, NetworkGroup):
            self_flatten_networks = self.flat_network_object_grp()
            __value_flatten_networks = __value.flat_network_object_grp()
            counter = 0
            if len(self_flatten_networks) == len(__value_flatten_networks):
                for i in range(len(self_flatten_networks)):
                    for j in range(len(__value_flatten_networks)):
                        if self_flatten_networks[i] == __value_flatten_networks[j]:
                            counter += 1
                            if counter == len(self_flatten_networks):
                                return True
                return False
        return False

    def flat_network_object_grp(self) -> list[Network]:
        final = []
        for network_obj in self.networks:
            if isinstance(network_obj, Network):
                final.append(network_obj)
            elif isinstance(network_obj, NetworkGroup):
                final.extend(network_obj.flat_network_object_grp())
        return final

    def get_network_depth(self) -> int:
        depth = 0
        max_depth = 1
        for network_obj in self.networks:
            if isinstance(network_obj, NetworkGroup):
                depth = network_obj.get_network_depth()
                depth += 1
                if max_depth < depth:
                    max_depth = depth
        return max_depth

    def get_size(self) -> int:
        return sum(network.get_size() for network in self.networks)