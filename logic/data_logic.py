"""Parses data from models into easy-to-use format for Pandas."""
from typing import Union

import yaml

from logic.builder_logic import Builder
from models.access_policy import AccessPolicy
from models.network import Network
from models.network_group import NetworkGroup
from models.port import Port
from models.port_group import PortGroup


class Data:
    def __init__(self, builder: Builder, config: dict) -> None:
        self.builder = builder
        with open(config, encoding='utf-8') as cfg:
            self.config = yaml.safe_load(cfg)
        self.ports_data = self.get_ports_data(self.builder.port_objs)
        self.networks_data = self.get_networks_data(self.builder.network_objs)
        self.access_rules_data = self.get_access_rules_data(self.builder.policies)
        self.access_policies_data = self.get_access_policy_data(self.builder.policies)

    def get_access_policy_data(self, policies: list[AccessPolicy]) -> list:
        return [(
            policy.name,
            policy.enabled_rules_count(),
            policy.allowed_rules_count(),
            policy.enabled_rules_ratio(),
            policy.allowed_rules_ratio()) for policy in policies]

    def get_access_rules_data(self, policies: list[AccessPolicy]) -> dict:
        access_rule_data = {}
        for policy in policies:
            avg_src_ip_num = policy.calculate_avg_src_network_size_of_acp()
            avg_dst_ip_num = policy.calculate_avg_dst_network_size_of_acp()
            avg_port_number = policy.calculate_avg_destination_port_size_of_acp()
            access_rule_data[policy.name] = [(
            rule.name,
            rule.action,
            rule.enabled,
            self._get_networks_data_by_rule(rule.source_networks),
            self.get_zones_data_by_rule(rule.source_zones),
            self._get_ports_data_by_rule(rule.source_ports),
            self._get_networks_data_by_rule(rule.destination_networks),
            self.get_zones_data_by_rule(rule.destination_zones),
            self._get_ports_data_by_rule(rule.destination_ports),
            rule.risk_category_by_dst_port_static(self.config['DESTINATION_PORT_CATEGORIES']),
            rule.risk_category_by_destination_port_dynamic(avg_port_number, self.config['RELATIVE_DESTINATION_PORT_CATEGORIES']),
            rule.risk_category_by_src_network_static(self.config['SOURCE_NETWORK_CATEGORIES']),
            rule.risk_category_by_dst_network_static(self.config['DESTINATION_NETWORK_CATEGORIES']),
            rule.risk_category_by_source_network_dynamic(avg_src_ip_num, self.config['RELATIVE_SOURCE_NETWORK_CATEGORIES']),
            rule.risk_category_by_dst_network_dynamic(avg_dst_ip_num, self.config['RELATIVE_DESTINATION_NETWORK_CATEGORIES']))
            for rule in policy.rules]
        return access_rule_data

    def get_zones_data_by_rule(self, zones: list[str]) -> str:
        value = ''
        for zone in zones:
            value += '{}, '.format(zone)
        return value

    def _get_ports_data_by_rule(self, ports: list[Union[Port, PortGroup]]) -> str:
        value = ''
        value_2 = ''
        for port in ports:
            if isinstance(port, Port):
                value += '{} - {} {}, '.format(port.name, port.protocol, port.port)
            elif isinstance(port, PortGroup):
                for p in port.ports:
                    value_2 += '{} - {} {}, '.format(p.name, p.protocol, p.port)
                value += '{}: ({}), '.format(port.name, value_2)
        return value

    def _get_networks_data_by_rule(self, networks: list[Union[Network, NetworkGroup]]) -> str:
        value = ''
        value_2 = ''
        for network in networks:
            if isinstance(network, NetworkGroup):
                nets = network.flat_network_object_grp()
                for net in nets:
                    value_2 += '{} : {}, '.format(net.name, net.value)
                value += '{}: ({}), '.format(network.name, value_2)
            else:
                value += '{} : {}, '.format(network.name, network.value)
        return value

    def get_ports_data(self, ports: dict[str, Union[Port, PortGroup]]) -> list:
        ports_data = []
        ports_count = self.get_port_object(ports)
        for port in ports.values():
            if isinstance(port, Port):
                ports_data.append((None, port.name, port.protocol, port.port, port.size, port._is_risky_port(self.config['HIGH_RISK_PROTOCOLS']), port.equal_with, ports_count[port.name]))
            elif isinstance(port, PortGroup):
                for p in port.ports:
                    ports_data.append((port.name, p.name, p.protocol, p.port, p.size, p._is_risky_port(self.config['HIGH_RISK_PROTOCOLS']), port.equal_with, ports_count[port.name]))
        return ports_data
    def get_port_object(self, ports_dict: dict[str, Union[Port, PortGroup]]) -> dict:
        ports = {}
        for port in ports_dict.values():
            ports[port.name] = 0
        self.port_object_count(ports)
        return ports

    def port_object_count(self, ports: dict) -> None:
        for policy in self.builder.policies:
            for rule in policy.rules:
                for key in ports:
                    if rule.port_used_in_rule(key):
                        ports[key] += 1

    def get_networks_data(self, networks: dict[str, Union[Network, NetworkGroup]]) -> list:
        networks_data = []
        networks_count = self.get_network_object(networks)
        for network in networks.values():
            if isinstance(network, NetworkGroup):
                nets = network.flat_network_object_grp()
                networks_data.extend([(network.name, network.depth, net.name, net.value, net.size, network.equal_with, networks_count[network.name]) for net in nets])
            else:
                networks_data.append((None, None, network.name, network.value, network.size, network.equal_with, networks_count[network.name]))
        return networks_data

    def get_network_object(self, networks_dict: dict[str, Union[Network, NetworkGroup]]) -> dict:
        networks = {}
        for network in networks_dict.values():
            networks[network.name] = 0
        self.network_object_count(networks)
        return networks

    def network_object_count(self, networks: dict) -> None:
        for policy in self.builder.policies:
            for rule in policy.rules:
                for key in networks:
                    if rule.network_used_in_rule(key):
                        networks[key] += 1
