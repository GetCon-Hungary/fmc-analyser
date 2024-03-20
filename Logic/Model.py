from Logic.BuilderLogic import Builder
from typing import Union
from Models.Port import Port
from Models.PortGroup import PortGroup
from Models.Network import Network
from Models.NetworkGroup import NetworkGroup

class Model():
        def __init__(self, builder: Builder, config: dict):
                self.builder = builder
                self.config = config

        def set_port_risk(self):
                for port in self.builder.port_objs.values():
                        port.is_risky = port._is_risky_port(self.config['HIGH_RISK_PROTOCOLS'])

        def test(self):
                for policy in self.builder.policies:
                        avg_src_ip_num = policy.calculate_avg_source_network_size_of_acp()
                        avg_dst_ip_num = policy.calculate_avg_destination_network_size_of_acp()
                        avg_port_number = policy.calculate_avg_destination_port_size_of_acp()
                        for rule in policy.rules:
                                rule.risk_category_by_source_network_static(self.config['SOURCE_NETWORK_CATEGORIES'])
                                rule.risk_category_by_destination_network_static(self.config['DESTINATION_NETWORK_CATEGORIES'])
                                rule.risk_category_by_destination_port_static(self.config['DESTINATION_PORT_CATEGORIES'])
                                rule.risk_category_by_source_network_dynamic(avg_src_ip_num, self.config['RELATIVE_SOURCE_NETWORK_CATEGORIES'])
                                rule.risk_category_by_destination_network_dynamic(avg_dst_ip_num, self.config['RELATIVE_DESTINATION_NETWORK_CATEGORIES'])
                                rule.risk_category_by_destination_port_dynamic(avg_port_number, self.config['RELATIVE_DESTINATION_PORT_CATEGORIES'])


        def port_object_count(self, ports: dict):
                for policy in self.builder.policies:
                        for rule in policy.rules:
                                for key in ports.keys():
                                        if rule.port_used_in_rule(key):
                                                ports[key] += 1

        def get_port_object(self, ports_dict: dict[str, Union[Port, PortGroup]]):
                ports = {}
                for port in ports_dict.values():
                        ports[port.name] = 0

                return ports

        def network_object_count(self, networks: dict):
                for policy in self.builder.policies:
                        for rule in policy.rules:
                                for key in networks.keys():
                                        if rule.network_used_in_rule(key):
                                                networks[key] += 1

        def get_network_object(self, networks_dict: dict[str, Union[Network, NetworkGroup]]):
                networks = {}
                for network in networks_dict.values():
                        networks[network.name] = 0
                
                return networks

        def test(self):
                for policy in self.builder.policies:    
                        enabled_count = policy.enabled_rules_count()
                        allowed_count = policy.allowed_rules_count()
                        allowed_ratio = policy.allowed_rules_ratio()
                        enabled_ratio = policy.enabled_rules_ratio()
                        print(str(enabled_ratio) + " " + str(len(policy.rules)) + " " + str(enabled_count) + " " + str(allowed_ratio) + " " + str(len(policy.rules)) + " " + str(allowed_count))
                                
                        print(policy.name)
                        for x in policy.rules:
                                print("halo")
                                print(str(x.get_source_networks_size()) + " " + str(x.get_destination_network_size()))
                                print("portok")
                                print(str(x.get_source_port_size()) + " " + str(x.get_destination_port_size()))