"""Represents the network group model."""

from netaddr import IPSet
import math

from models.network import Network
from models.network_object import NetworkObject


class NetworkGroup(NetworkObject):
    def __init__(self, id: str, name: str) -> None:
        super().__init__(id, name)
        self.networks: list[NetworkObject] = []
        self.depth = 0

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, NetworkGroup):
            self_flatten_networks = self.flat_network_object_grp()
            __value_flatten_networks = __value.flat_network_object_grp()
            self_ip_set = IPSet([(network.value) for network in self_flatten_networks])
            __value_ip_set = IPSet([(__value.value) for __value in __value_flatten_networks])
            return self_ip_set == __value_ip_set
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
    
    def _calculate_subnet_mask(self, ip_number: int) -> int:
        # Initialize a mask
        mask = 0x80000000  # 0b10000000000000000000000000000000

        # Find the leftmost set bit
        position = 32
        while position >= 0:
            if ip_number - mask > 0:
                half_mask = mask >> 1
                if ip_number - mask - half_mask >= 0:
                    return 32 - position
                else:
                    return 32 - (position - 1)
            mask >>= 1
            position -= 1
        
        return 0
