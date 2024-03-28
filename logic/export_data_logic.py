"""Parses data from models into easy-to-use format for Pandas."""

import yaml

from logic.builder_logic import Builder
from models.network import Network
from models.network_group import NetworkGroup
from models.network_object import NetworkObject
from models.port import Port
from models.port_group import PortGroup
from models.port_object import PortObject


class Data:
    def __init__(self, builder: Builder, config) -> None:  # noqa:D107
        self.builder = builder
        with open(config, encoding='utf-8') as cfg:
            self.config = yaml.safe_load(cfg)
        self.ports_data = self.get_ports_data()
        self.networks_data = self.get_networks_data()
        self.access_rules_data = self.get_access_rules_data()
        self.access_policies_data = self.get_access_policy_data()

    def get_access_policy_data(self) -> list:
        """Create the access policy data for export.

        Returns:
        -------
            list[str]: The list of access policy data.

        """
        return [(
            policy.name,
            policy.enabled_rules_count(),
            policy.allowed_rules_count(),
            policy.enabled_rules_ratio(),
            policy.allowed_rules_ratio(),
            policy.calculate_avg_src_network_size_of_acp(),
            policy.calculate_avg_dst_network_size_of_acp(),
            policy.calculate_avg_dst_port_size_of_acp()) for policy in self.builder.policies]

    def get_access_rules_data(self) -> dict[str, list]:
        """Create the access rules data for export.

        Returns:
        -------
            dict[str, list]: The dictionary of access rules data by access policy names.

        """
        access_rule_data = {}
        for policy in self.builder.policies:
            avg_src_ip_num = policy.calculate_avg_src_network_size_of_acp()
            avg_dst_ip_num = policy.calculate_avg_dst_network_size_of_acp()
            avg_port_number = policy.calculate_avg_dst_port_size_of_acp()
            access_rule_data[policy.name] = [(
                rule.name,
                rule.action,
                rule.enabled,
                self.get_zones_data_by_rule(rule.source_zones),
                self._get_networks_data_by_rule(rule.source_networks),
                self._get_ports_data_by_rule(rule.source_ports),
                self.get_zones_data_by_rule(rule.destination_zones),
                self._get_networks_data_by_rule(rule.destination_networks),
                self._get_ports_data_by_rule(rule.destination_ports),
                rule.get_source_networks_size() if rule.get_source_networks_size() > 0 else 4294967296,
                rule.get_destination_network_size() if rule.get_destination_network_size() > 0 else 4294967296,
                rule.get_destination_port_size() if rule.get_destination_network_size() > 0 else 65535,
                rule.risk_category_by_src_network_static(self.config['SOURCE_NETWORK_CATEGORIES']),
                rule.risk_category_by_source_network_dynamic(avg_src_ip_num, self.config['RELATIVE_SOURCE_NETWORK_CATEGORIES']),
                rule.risk_category_by_dst_network_static(self.config['DESTINATION_NETWORK_CATEGORIES']),
                rule.risk_category_by_dst_network_dynamic(avg_dst_ip_num, self.config['RELATIVE_DESTINATION_NETWORK_CATEGORIES']),
                rule.risk_category_by_dst_port_static(self.config['DESTINATION_PORT_CATEGORIES']),
                rule.risk_category_by_destination_port_dynamic(avg_port_number, self.config['RELATIVE_DESTINATION_PORT_CATEGORIES']))
            for rule in policy.rules]
        return access_rule_data

    def get_zones_data_by_rule(self, zones: list[str]) -> str:
        if len(zones) > 0:
            return ', '.join(zones)
        else:
            return 'Any'

    def _get_ports_data_by_rule(self, ports: list[PortObject]) -> str:
        if len(ports) > 0:
            return ', '.join(port.name if port.name != '' else port.port for port in ports)
        else:
            return 'Any'

    def _get_networks_data_by_rule(self, networks: list[NetworkObject]) -> str:
        if len(networks) > 0:
            return ', '.join(network.name if network.name != '' else str(network.value) for network in networks)
        else:
            return 'Any'

    def get_ports_data(self) -> list:
        """Create the ports data for export.

        Returns:
        -------
            list: The list of ports data.

        """
        ports_data = []
        ports_count = self.get_port_object(self.builder.port_objs)
        for port in self.builder.port_objs.values():
            if isinstance(port, Port):
                ports_data.append((None, port.name, port.protocol, port.port, port.size, port._is_risky_port(self.config['HIGH_RISK_PROTOCOLS']), self.get_equal_ports_data(port.equal_with), ports_count[port.id]))
            elif isinstance(port, PortGroup):
                for p in port.ports:
                    ports_data.append((port.name, p.name, p.protocol, p.port, p.size, p._is_risky_port(self.config['HIGH_RISK_PROTOCOLS']), self.get_equal_ports_data(port.equal_with), ports_count[port.id]))
        return ports_data

    def get_equal_ports_data(self, ports: list[PortObject]) -> str:
        return ', '.join(port.name for port in ports)

    def get_port_object(self, ports_dict: dict[str, PortObject]) -> dict:
        ports = {}
        for port in ports_dict.values():
            ports[port.id] = 0
        self.port_object_count(ports)
        return ports

    def port_object_count(self, ports: dict[str, int]) -> None:
        for policy in self.builder.policies:
            for rule in policy.rules:
                for key in ports:
                    if rule.port_used_in_rule(key):
                            ports[key] += 1
                            port = self.builder.port_objs.get(key, None)
                            if isinstance(port, PortGroup):
                                for flat in port.flat_port_object_grp():
                                    if flat.id != '':
                                        ports[flat.id] += 1

    def get_networks_data(self) -> list:
        """Create the networks data for export.

        Returns:
        -------
            list: The list of networks data.

        """
        networks_data = []
        networks_count = self.get_network_object(self.builder.network_objs)
        for network in self.builder.network_objs.values():
            if isinstance(network, NetworkGroup):
                nets = network.flat_network_object_grp()
                networks_data.extend([(network.name, network.depth, net.name, net.value, net.size, self.get_equal_networks_data(network.equal_with), networks_count[network.id]) for net in nets])
            elif isinstance(network, Network):
                networks_data.append((None, None, network.name, network.value, network.size, self.get_equal_networks_data(network.equal_with), networks_count[network.id]))
        return networks_data

    def get_equal_networks_data(self, networks: list[NetworkObject]) -> str:
        return ', '.join(network.name for network in networks)

    def get_network_object(self, networks_dict: dict[str, NetworkObject]) -> dict:
        networks = {}
        for network in networks_dict.values():
            networks[network.id] = 0
        self.network_object_count(networks)
        return networks

    def network_object_count(self, networks: dict[str, int]) -> None:
        for policy in self.builder.policies:
            for rule in policy.rules:
                for key in networks:
                    if rule.network_used_in_rule(key):
                            networks[key] += 1
                            network = self.builder.network_objs.get(key, None)
                            if isinstance(network, NetworkGroup):
                                for flat in network.flat_network_object_grp():
                                    if flat.id != '':
                                        networks[flat.id] += 1