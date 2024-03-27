"""Represents the access rule model."""
import math
from typing import Union

from models.network import Network
from models.network_group import NetworkGroup
from models.port import Port
from models.port_group import PortGroup
from models.risk_enum import Risk


class AccessRule:
    """Represents a single access rule in an access control policy."""
    def __init__(self, id: str, name: str, action: str, enabled: str, source_networks: list[Union[Network, NetworkGroup]], source_zones: list[str], source_ports: list[Union[Port, PortGroup]], destination_networks: list[Union[Network, NetworkGroup]], destination_zones: list[str], destination_ports: list[Union[Port, PortGroup]]) -> None:
        self.id = id
        self.name = name
        self.action = action
        self.enabled = enabled
        self.source_networks = source_networks
        self.source_zones = source_zones
        self.source_ports = source_ports
        self.destination_networks = destination_networks
        self.destination_zones = destination_zones
        self.destination_ports = destination_ports

    def port_used(self, xport, ports: list[Union[Port, PortGroup]]) -> bool:  # noqa: D102
        return any(xport == port.name for port in ports)

    def port_used_in_rule(self, port) -> bool:  # noqa: D102
        return self.port_used(port, self.source_ports) or self.port_used(port, self.destination_ports)

    def network_used(self, xnetwork, networks: list[Union[Network, NetworkGroup]]) -> bool:  # noqa: D102
        return any(xnetwork == network.name for network in networks)

    def network_used_in_rule(self, network) -> bool:  # noqa: D102
        return self.network_used(network, self.source_networks) or self.network_used(network, self.destination_networks)

    def get_source_networks_size(self) -> int:  # noqa: D102
        sum = 0
        for network in self.source_networks:
            sum += network.get_size()
        return sum

    def get_destination_network_size(self) -> int:  # noqa: D102
        return sum(network.get_size() for network in self.destination_networks)

    def get_source_port_size(self) -> int:
        sum = 0
        for port in self.source_ports:
            sum += port.get_size()
        return sum

    def get_destination_port_size(self) -> int:
        sum = 0
        for port in self.destination_ports:
            sum += port.get_size()
        return sum

    def risk_category_by_destination_port_dynamic(self, avg_port_number: float, relative_destination_port: dict[str, int]) -> str:
        if len(self.destination_ports) > 0:
            if self.get_destination_port_size() >= relative_destination_port['HIGH'] * avg_port_number:
                return Risk.HIGH.name
            if self.get_destination_port_size() >= relative_destination_port['MEDIUM'] * avg_port_number:
                return Risk.MEDIUM.name
            return Risk.LOW.name
        return Risk.HIGH.name

    def risk_category_by_source_network_dynamic(self, avg_ip_number: float, relative_source_network: dict[str, int]) -> str:
        if len(self.source_networks) > 0:
            if self.get_source_networks_size() >= relative_source_network['HIGH'] * avg_ip_number:
                return Risk.HIGH.name
            if self.get_source_networks_size() >= relative_source_network['MEDIUM'] * avg_ip_number:
                return Risk.MEDIUM.name
            return Risk.LOW.name
        return Risk.HIGH.name

    def risk_category_by_dst_network_dynamic(self, avg_ip_number: float, relative_destination_network: dict[str, int]) -> str:  # noqa: D102
        if len(self.destination_networks) > 0:
            if self.get_destination_network_size() >= relative_destination_network['HIGH'] * avg_ip_number:
                return Risk.HIGH.name
            if self.get_destination_network_size() >= relative_destination_network['MEDIUM'] * avg_ip_number:
                return Risk.MEDIUM.name
            return Risk.LOW.name
        return Risk.HIGH.name

    def risk_category_by_dst_port_static(self, port_number: dict[str, int]) -> str:  # noqa: D102
        if len(self.destination_ports) > 0:
            if len(self.destination_ports) == 1 and isinstance(self.destination_ports[0], PortGroup):
                flattened_ports = self.destination_ports[0].flat_port_object_grp()
                return self._return_risk(flattened_ports, port_number)
            return self._return_risk(self.destination_ports, port_number)
        return Risk.HIGH.name

    def _return_risk(self, ports: list[Union[Port, PortGroup]], port_number: dict[str, int]) -> str:
        if len(ports) >= port_number['HIGH']:
            return Risk.HIGH.name
        if len(ports) >= port_number['MEDIUM']:
            return Risk.MEDIUM.name
        return Risk.LOW.name

    def risk_category_by_src_network_static(self, risky_source_network_mask: dict[str, str]) -> str:  # noqa: D102
        ip_number = self.get_source_networks_size()
        if ip_number > 0:
            mask = self._calculate_subnet_mask(ip_number)
            if mask <= int(risky_source_network_mask['HIGH'].split('/')[1]):
                return Risk.HIGH.name
            if mask <= int(risky_source_network_mask['MEDIUM'].split('/')[1]):
                return Risk.MEDIUM.name
            return Risk.LOW.name
        return Risk.HIGH.name

    def risk_category_by_dst_network_static(self, risky_destination_network_mask: dict[str, str]) -> str:  # noqa: D102
        ip_number = self.get_destination_network_size()
        if ip_number > 0:
            mask = self._calculate_subnet_mask(ip_number)
            if mask <= int(risky_destination_network_mask['HIGH'].split('/')[1]):
                return Risk.HIGH.name
            if mask <= int(risky_destination_network_mask['MEDIUM'].split('/')[1]):
                return Risk.MEDIUM.name
            return Risk.LOW.name
        return Risk.HIGH.name

    def _calculate_subnet_mask(self, ip_number: int) -> float:
        mask = 32 - math.ceil(math.log2(ip_number))
        if mask > 0:
            return mask
        return 0