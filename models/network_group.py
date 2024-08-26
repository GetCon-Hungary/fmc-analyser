"""Represents the network group model."""

from netaddr import IPSet

from models.fqdn_object import FQDNObject
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

            self_ip_set = IPSet([network.value for network in self_flatten_networks if not isinstance(network, FQDNObject)])
            __value_ip_set = IPSet([__value.value for __value in __value_flatten_networks if not isinstance(__value, FQDNObject)])

            self_fqdn = [network.value for network in self_flatten_networks if isinstance(network, FQDNObject)]
            __value_fqdn = [__value.value for __value in __value_flatten_networks if isinstance(__value, FQDNObject)]

            return self_ip_set == __value_ip_set and self_fqdn == __value_fqdn
        
        return False

    def flat_network_object_grp(self) -> list[NetworkObject]:
        final = []
        for network_obj in self.networks:
            if isinstance(network_obj, NetworkGroup):
                final.extend(network_obj.flat_network_object_grp())
            else:
                final.append(network_obj)
            
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
    