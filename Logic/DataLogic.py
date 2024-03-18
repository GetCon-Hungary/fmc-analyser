from Logic.BuilderLogic import Builder
from Models.Port import Port
from Models.PortGroup import PortGroup
from Models.Network import Network
from Models.NetworkGroup import NetworkGroup

class Data():
    def __init__(self, builder: Builder):
        self.builder = builder
        self.ports_data = self.get_ports_data(self.builder.port_objs)
        self.networks_data = self.get_networks_data(self.builder.network_objs)
        self.access_rules_data = self.get_access_rules_data(self.builder.policies)
           
    def get_access_rules_data(self, policies):
        access_rule_data = {}
        for policy in policies:
                access_rule_data[policy.name] = [(rule.name, rule.action, rule.enabled, self._get_networks_data_by_rule(rule.source_networks), rule.source_zones, self._get_ports_data_by_rule(rule.source_ports), self._get_networks_data_by_rule(rule.destination_networks), rule.destination_zones, self._get_ports_data_by_rule(rule.destination_ports)) for rule in policy.rules]
        return access_rule_data
    
    def get_ports_data(self, ports):
        ports_data = []
        for port in ports.values():
                if isinstance(port, Port):
                        ports_data.append((None, port.name, port.protocol, port.port, port.size, port.is_risky, port.equal_with))
                elif isinstance(port, PortGroup):
                        for p in port.ports:
                                ports_data.append((port.name, p.name, p.protocol, p.port, p.size, p.is_risky, port.equal_with))
        return ports_data

    def get_networks_data(self, networks):
        networks_data = []
        for network in networks.values():
                if isinstance(network, NetworkGroup):
                        nets = network.flat_network_object_grp()
                        networks_data.extend([(network.name, network.depth, net.name, net.value, net.size, network.equal_with) for net in nets])
                else:
                        networks_data.append((None, None, network.name, network.value, network.size, network.equal_with))
        return networks_data

    def _get_ports_data_by_rule(self, ports):
        value = ""
        value_2 = ""
        for port in ports:
                if isinstance(port, Port):
                        value += "{} - {} {}, ".format(port.name, port.protocol, port.port)
                elif isinstance(port, PortGroup):
                        for p in port.ports:
                                value_2 += "{} - {} {}, ".format(p.name, p.protocol, p.port)
                        value += "{}: ({}), ".format(port.name, value_2)
        return value

    def _get_networks_data_by_rule(self, networks):
        value = ""
        value_2 = ""
        for network in networks:
                if isinstance(network, NetworkGroup):
                        nets = network.flat_network_object_grp()
                        for net in nets:
                                value_2 += "{} : {}, ".format(net.name, net.value)
                        value += "{}: ({}), ".format(network.name, value_2)
                else:
                        value += "{} : {}, ".format(network.name, network.value)

        return value