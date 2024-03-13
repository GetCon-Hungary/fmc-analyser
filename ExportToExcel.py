import pandas as pd
import os
from Models.Port import Port
from Models.PortGroup import PortGroup
from Models.Network import Network
from Models.NetworkGroup import NetworkGroup

ACCESS_RULE_HEADER = ['Access Rule', 'Action', 'Enabled', 'Source Networks', 'Source Zones', 'Source Ports', 'Destination Networks', 'Destination Zones', 'Destination Ports']
PORTS_HEADER = ['Group Name', 'Name', 'Protocol', 'Port', 'Size', 'Risky', 'Equal with']
NETWORK_HEADER = ['Group Name', 'Group depth', 'Name', 'Value', 'Size', 'Equal with']

def export_access_rules(policies):
        for policy in policies:
                access_rule_data = [(rule.name, rule.action, rule.enabled, _get_networks_data_by_rule(rule.source_networks), rule.source_zones, _get_ports_data_by_rule(rule.source_ports) , _get_networks_data_by_rule(rule.destination_networks), rule.destination_zones, _get_ports_data_by_rule(rule.destination_ports)) for rule in policy.rules]
                _export_to_excel(access_rule_data, ACCESS_RULE_HEADER, 'access_rules_of_{}'.format(policy.name))

def export_ports(ports):
        ports_data = []
        for port in ports:
                if isinstance(port, Port):
                        ports_data.append((None, port.name, port.protocol, port.port, port.size, port.is_risky, port.equal_with))
                elif isinstance(port, PortGroup):
                        for p in port.ports:
                                ports_data.append((port.name, p.name, p.protocol, p.port, p.size, p.is_risky, port.equal_with))
        _export_to_excel(ports_data, PORTS_HEADER, 'ports')

def export_networks(networks):
        networks_data = []
        for network in networks:
                if isinstance(network, NetworkGroup):
                        nets = network.flat_network_object_grp()
                        networks_data.extend([(network.name, network.depth, net.name, net.value.ip, net.size, network.equal_with) for net in nets])
                else:
                        networks_data.append((None, None, network.name, network.value.ip, network.size, network.equal_with))

        _export_to_excel(networks_data, NETWORK_HEADER, 'networks')

def _get_ports_data_by_rule(ports):
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

def _get_networks_data_by_rule(networks):
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

def _export_to_excel(data, header, sheet_name):
        df = pd.DataFrame(data, columns=header)
        df.index = range(1, len(df)+1)
        export_dir = os.getcwd() + '/Exports/final.xlsx'
        with pd.ExcelWriter(path=export_dir, mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(excel_writer=writer, sheet_name=sheet_name)