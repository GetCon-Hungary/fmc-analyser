"""Represents the access rule model."""

from models.network_object import NetworkObject
from models.port_group import PortGroup
from models.port_object import PortObject
from models.risk_enum import Risk


class AccessRule:
    """Represents a single access rule in an access control policy."""

    def __init__(self, id: str, name: str, action: str, enabled: str, source_networks: list[NetworkObject], source_zones: list[str], source_ports: list[PortObject], destination_networks: list[NetworkObject], destination_zones: list[str], destination_ports: list[PortObject]) -> None:  # noqa: D107
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
        self.equal_with = []
        self.rev_eq = []
        self.merge_can = []
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value, AccessRule):
            return self.action == value.action and self.source_zones == value.source_zones and self.source_networks == value.source_networks and self.source_ports == value.source_ports and self.destination_zones == value.destination_zones and self.destination_networks == value.destination_networks and self.destination_ports == value.destination_ports
        else:
            return False
    
    def reverse_eq(self, value: object) -> bool:
        if isinstance(value, AccessRule):
            return self.action == value.action and self.source_zones == value.destination_zones and self.source_networks == value.destination_networks and self.source_ports == value.destination_ports and self.destination_zones == value.source_zones and self.destination_networks == value.source_networks and self.destination_ports == value.source_ports
        else:
            return False
    
    def merge_candidates(self, value: object) -> bool:
        if isinstance(value, AccessRule):
            return self.action == value.action and self.source_zones == value.source_zones and self.source_networks == value.source_networks and self.destination_zones == value.destination_zones and self.destination_networks == value.destination_networks
        else:
            return False

    def port_used(self, xport: str, ports: list[PortObject]) -> bool:  # noqa: D102
        return any(xport == port.id for port in ports)

    def port_used_in_rule(self, port: str) -> bool:  # noqa: D102
        return self.port_used(port, self.source_ports) or self.port_used(port, self.destination_ports)

    def network_used(self, xnetwork: str, networks: list[NetworkObject]) -> bool:  # noqa: D102
        return any(xnetwork == network.id for network in networks)

    def network_used_in_rule(self, network: str) -> bool:  # noqa: D102
        return self.network_used(network, self.source_networks) or self.network_used(network, self.destination_networks)

    def get_source_networks_size(self) -> int:  # noqa: D102
        return sum(network.get_size() for network in self.source_networks)

    def get_destination_network_size(self) -> int:  # noqa: D102
        return sum(network.get_size() for network in self.destination_networks)

    def get_source_port_size(self) -> int:
        return sum(port.get_size() for port in self.source_ports)

    def get_destination_port_size(self) -> int:
        return sum(port.get_size() for port in self.destination_ports)

    def risk_category_by_destination_port_dynamic(self, avg_port_number: float, relative_destination_port: dict[str, int]) -> str:
        if self.action.lower() == 'allow':
            if len(self.destination_ports) > 0:
                dst_port_size = self.get_destination_port_size()
                if dst_port_size >= relative_destination_port['HIGH'] * avg_port_number:
                    return Risk.HIGH.name
                elif dst_port_size >= relative_destination_port['MEDIUM'] * avg_port_number:
                    return Risk.MEDIUM.name
                elif dst_port_size >= relative_destination_port['LOW'] * avg_port_number:
                    return Risk.LOW.name
                else:
                    return Risk.NONE.name
            return Risk.HIGH.name
        else:
            return Risk.NONE.name

    def risk_category_by_source_network_dynamic(self, avg_ip_number: float, relative_source_network: dict[str, int]) -> str:
        if self.action.lower() == 'allow':
            if len(self.source_networks) > 0:
                src_network_size = self.get_source_networks_size()
                if src_network_size >= relative_source_network['HIGH'] * avg_ip_number:
                    return Risk.HIGH.name
                elif src_network_size >= relative_source_network['MEDIUM'] * avg_ip_number:
                    return Risk.MEDIUM.name
                elif src_network_size >= relative_source_network['LOW'] * avg_ip_number:
                    return Risk.LOW.name
                else:
                    return Risk.NONE.name
            return Risk.HIGH.name
        else:
            return Risk.NONE.name

    def risk_category_by_dst_network_dynamic(self, avg_ip_number: float, relative_destination_network: dict[str, int]) -> str:  # noqa: D102
        if self.action.lower() == 'allow':
            if len(self.destination_networks) > 0:
                dst_network_size = self.get_destination_network_size()
                if dst_network_size >= relative_destination_network['HIGH'] * avg_ip_number:
                    return Risk.HIGH.name
                elif dst_network_size >= relative_destination_network['MEDIUM'] * avg_ip_number:
                    return Risk.MEDIUM.name
                elif dst_network_size >= relative_destination_network['LOW'] * avg_ip_number:
                    return Risk.LOW.name
                else:
                    return Risk.NONE.name
            return Risk.HIGH.name
        return Risk.NONE.name

    def risk_category_by_dst_port_static(self, port_number: dict[str, int]) -> str:  # noqa: D102
        if self.action.lower() == 'allow':
            if len(self.destination_ports) > 0:
                if len(self.destination_ports) == 1 and isinstance(self.destination_ports[0], PortGroup):
                    flattened_ports = self.destination_ports[0].flat_port_object_grp()
                    return self._return_risk(flattened_ports, port_number)
                return self._return_risk(self.destination_ports, port_number)
            return Risk.HIGH.name
        else:
            return Risk.NONE.name

    def _return_risk(self, ports: list[PortObject], port_number: dict[str, int]) -> str:
        if len(ports) >= port_number['HIGH']:
            return Risk.HIGH.name
        elif len(ports) >= port_number['MEDIUM']:
            return Risk.MEDIUM.name
        elif len(ports) >= port_number['LOW']:
            return Risk.LOW.name
        else:
            return Risk.NONE.name

    def risk_category_by_src_network_static(self, risky_source_network_mask: dict[str, str]) -> str:  # noqa: D102
        if self.action.lower() == 'allow':
            ip_number = self.get_source_networks_size()
            if ip_number > 0:
                mask = self._calculate_subnet_mask(ip_number)
                if mask <= int(risky_source_network_mask['HIGH'].split('/')[1]):
                    return Risk.HIGH.name
                elif mask <= int(risky_source_network_mask['MEDIUM'].split('/')[1]):
                    return Risk.MEDIUM.name
                elif mask <= int(risky_source_network_mask['LOW'].split('/')[1]):
                    return Risk.LOW.name
                else:
                    return Risk.NONE.name
            return Risk.HIGH.name
        else:
            return Risk.NONE.name

    def risk_category_by_dst_network_static(self, risky_destination_network_mask: dict[str, str]) -> str:  # noqa: D102
        if self.action.lower() == 'allow':
            ip_number = self.get_destination_network_size()
            if ip_number > 0:
                mask = self._calculate_subnet_mask(ip_number)
                if mask <= int(risky_destination_network_mask['HIGH'].split('/')[1]):
                    return Risk.HIGH.name
                elif mask <= int(risky_destination_network_mask['MEDIUM'].split('/')[1]):
                    return Risk.MEDIUM.name
                elif mask <= int(risky_destination_network_mask['LOW'].split('/')[1]):
                    return Risk.LOW.name
                else:
                    return Risk.NONE.name
            return Risk.HIGH.name
        else:
            return Risk.NONE.name
    
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