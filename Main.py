import fmcapi
from Models.AccessPolicy import AccessPolicy
from Models.AccessRule import AccessRule
from Models.PortObject import PortObject
from Models.Port import Port
from Models.NetworkObject import NetworkObject
from Models.Network import Network
import pandas as pd
import os
import math
import argparse


def fmc_init(ip, user, passw, query, deploy):
    with fmcapi.FMC(
        host=ip,
        username=user,
        password=passw,
        autodeploy=deploy,
    ) as fmc:
        if query == 'acp' or query == 'all':
                acp = fmcapi.AccessPolicies(fmc).get()
                policies = get_access_policies(fmc, acp)
                access_rule_header = ['Access Rule', 'Action', 'Enabled', 'Source Networks', 'Source Zones', 'Source Ports', 'Destination Networks', 'Destination Zones', 'Destination Ports']
                for policy in policies:
                        access_rule_data = [(rule.name, rule.action, rule.enabled, get_networks_data_by_rule(rule.source_networks), rule.source_zones, get_ports_data_by_rule(rule.source_ports) , get_networks_data_by_rule(rule.destination_networks), rule.destination_zones, get_ports_data_by_rule(rule.destination_ports)) for rule in policy.rules]
                        export_to_excel(access_rule_data, access_rule_header, 'access_rules_of_{}'.format(policy.name))

                for policy in policies:    
                        enabled_count = policy.enabled_rules_count()
                        allowed_count = policy.allowed_rules_count()
                        allowed_ratio = policy.allowed_rules_ratio()
                        enabled_ratio = policy.enabled_rules_ratio()
                        print(str(enabled_ratio) + " " + str(len(policy.rules)) + " " + str(enabled_count) + " " + str(allowed_ratio) + " " + str(len(policy.rules)) + " " + str(allowed_count))
                        
                        print(policy.name)
                        for x in policy.rules:
                                print("halo")
                                print(str(x.get_source_size()) + " " + str(x.get_destination_size()))
                                print("portok")
                                print(str(x.get_source_port_size()) + " " + str(x.get_destination_port_size()))

        if query == 'ports' or query == 'all':
                ports_header = ['Group Name', 'Name', 'Protocol', 'Port', 'Size', 'Risky', 'Equal with']
                port_objs = []
                protocol_port_objs = fmcapi.ProtocolPortObjects(fmc).get()
                port_obj_groups = fmcapi.PortObjectGroups(fmc).get()

                port_objs.extend(get_ports(fmc, protocol_port_objs['items']))
                port_objs.extend(get_ports(fmc, port_obj_groups['items']))
                equal_port_object_finder(port_objs)
                ports_data = get_ports_data(port_objs)
                export_to_excel(ports_data, ports_header, 'ports')
        
        if query == 'networks' or query == 'all':
                network_header = ['Group Name', 'Group depth', 'Name', 'Value', 'Size', 'Equal with']
                network_objs = []
                network_groups = fmcapi.NetworkGroups(fmc).get()
                hosts = fmcapi.Hosts(fmc).get()
                networks = fmcapi.Networks(fmc).get()
                ranges = fmcapi.Ranges(fmc).get()
                
                network_objs.extend(get_networks(fmc, hosts['items']))
                network_objs.extend(get_networks(fmc, networks['items']))
                network_objs.extend(get_networks(fmc, ranges['items']))
                network_objs.extend(get_networks(fmc, network_groups['items']))
                equal_network_object_finder(network_objs)
                network_data = get_networks_data(network_objs)
                export_to_excel(network_data, network_header, 'networks')

        print('Done')

def get_access_policies(fmc, acp):
        policies = []
        for acp in acp['items']:
            id = acp.get('id', None)
            name = acp.get('name', None)
            accessrules = fmcapi.AccessRules(fmc, acp_id=id).get()
            rules = get_access_rules(fmc, accessrules['items'], name)
            policies.append(AccessPolicy(id, name, rules))
        
        return policies

def get_access_rules(fmc, accessrules, acp_name):
        rules = []
        for rule in accessrules:
                access_policy = acp_name
                id = rule.get('id', None)
                name = rule.get('name', None)
                action = rule.get('action', None)
                enabled = rule.get('enabled', None)
                source_network, destination_networks = get_networks_by_rule(fmc, rule)
                source_zones, destination_zones = get_zones_by_rule(rule)
                source_ports, destination_ports = get_ports_by_rule(fmc, rule)
                rules.append(AccessRule(access_policy, id, name, action, enabled, source_network, source_zones, source_ports, destination_networks, destination_zones, destination_ports))
        
        return rules

def get_zones_by_rule(rule):
        s_zones = rule.get('sourceZones', None)
        d_zones = rule.get('destinationZones', None)
        if s_zones is not None:
                s_zones =  s_zones['objects'][0]['name']
        if d_zones is not None:
                d_zones =  d_zones['objects'][0]['name']
        return s_zones, d_zones

def get_ports_by_rule(fmc, rule):
        s_ports = rule.get('sourcePorts', None)
        d_ports = rule.get('destinationPorts', None)
        s_ports_list = []
        d_ports_list = []
        if s_ports is not None:
                s_objects = s_ports.get('objects', None)
                s_literals = s_ports.get('literals', None)
                if s_objects is not None:
                        s_ports_list.extend(get_ports(fmc, s_objects))
                elif s_literals is not None:
                        s_ports_list.extend(get_ports(fmc, s_literals))
        if d_ports is not None:
                d_objects = d_ports.get('objects', None)
                d_literals = d_ports.get('literals', None)
                if d_objects is not None:
                        d_ports_list.extend(get_ports(fmc, d_objects))
                elif d_literals is not None:
                        d_ports_list.extend(get_ports(fmc, d_literals))
                        
        return s_ports_list, d_ports_list

def port_object_count(obj, accessPolicy):
        for policy in accessPolicy:
                for rule in policy.rules:
                        for key in obj.keys():
                                if rule.PortUsedInRule(key):
                                        obj[key] += 1

def get_port_object(objs):
        obj = {}
        
        for x in objs:
                obj[x.name] = 0

        return obj

def get_ports(fmc, ports):
        port_objs = []
        for port in ports:
                port_id = port.get('id', None)
                port_type = port.get('type', None)
                if port_type == 'ProtocolPortObject':
                        protocol_port_obj = fmcapi.ProtocolPortObjects(fmc, id=port_id).get()
                        port_objs.append(_create_port(protocol_port_obj))
                elif port_type == 'PortObjectGroup':
                        port_grp = []
                        port_obj_grp = fmcapi.PortObjectGroups(fmc, id=port_id).get()
                        group_name = port_obj_grp['name']
                        flattened_port_obj_grp = flat_port_object_grp(fmc, port_obj_grp)
                        for protocol_port_obj in flattened_port_obj_grp:
                                port_grp.append(_create_port(protocol_port_obj))
                        port_objs.append(PortObject(port_id, group_name, port_grp))
                elif port_type == 'ICMPv4PortLiteral':
                        port_objs.append(Port(port_id, port_type, port.get('protocol', None), port.get('icmpType', None), '1', True))
        return port_objs

def flat_port_object_grp(fmc, port_obj_group):
        port_obj = []
        for port in port_obj_group['objects']:
                port_id = port['id']
                port_obj.append(fmcapi.ProtocolPortObjects(fmc, id=port_id).get())
        return port_obj

def _create_port(port_obj):
        port_id, port_name, port_port, port_protocol = _get_ports_info(port_obj)
        port_size = calculate_protocol_port_object_size(port_port)
        is_risky = _is_risky_port([], port_port)
        return Port(port_id, port_name, port_protocol, port_port, port_size, is_risky)

def _get_ports_info(protocol_port_obj):
        port_id = protocol_port_obj.get('id', None)
        port_name = protocol_port_obj.get('name', None)
        port_port = protocol_port_obj.get('port', None)
        port_protocol = protocol_port_obj.get('protocol', None)
        return port_id, port_name, port_port, port_protocol

def calculate_protocol_port_object_size(port_port):
        port_size = 1
        if "-" in port_port:
                port_size = int(port_port.split("-")[1]) - int(port_port.split("-")[0])
        return port_size

def _is_risky_port(risky_ports, current_port):
        return False

def equal_port_object_finder(ports):
        for i in range(len(ports) - 1):
                for j in range(i + 1, len(ports)):
                        if isinstance(ports[i], Port) and isinstance(ports[j], Port) and ports[i].__eq__(ports[j]):
                                ports[i].equal_with += "{}, ".format(ports[j].name)
                                ports[j].equal_with += "{}, ".format(ports[i].name)  
                        elif isinstance(ports[i], PortObject) and isinstance(ports[j], PortObject) and ports[i].__eq__(ports[j]):
                                ports[i].equal_with += "{}, ".format(ports[j].name)
                                ports[j].equal_with += "{}, ".format(ports[i].name)

def get_ports_data(ports):
        ports_data = []
        for port in ports:
                if isinstance(port, Port):
                        ports_data.append((None, port.name, port.protocol, port.port, port.size, port.is_risky, port.equal_with))
                elif isinstance(port, PortObject):
                        for p in port.ports:
                                ports_data.append((port.name, p.name, p.protocol, p.port, p.size, p.is_risky, port.equal_with))
        return ports_data

def get_ports_data_by_rule(ports):
        value = ""
        value_2 = ""
        for port in ports:
                if isinstance(port, Port):
                        value += "{} - {} {}, ".format(port.name, port.protocol, port.port)
                elif isinstance(port, PortObject):
                        for p in port.ports:
                                value_2 += "{} - {} {}, ".format(p.name, p.protocol, p.port)
                        value += "{}: ({}), ".format(port.name, value_2)
        return value

def get_networks_by_rule(fmc, rule):
        s_networks = rule.get('sourceNetworks', None)
        d_networks = rule.get('destinationNetworks', None)
        s_networks_list = []
        d_networks_list = []
        if s_networks is not None:
                for s_network in s_networks['objects']:
                        source_depth = 0
                        source_collector = get_networks(fmc, [s_network])
                        s_networks_list.extend(source_collector)
        if d_networks is not None:
                for d_network in d_networks['objects']:
                        dest_depth = 0
                        dest_collector = get_networks(fmc, [d_network])
                        d_networks_list.extend(dest_collector)
        
        return s_networks_list, d_networks_list

def network_object_count(obj, accessPolicy):
        for policy in accessPolicy:
                for rule in policy.rules:
                        for key in obj.keys():
                                if rule.NetworkUsedInRule(key):
                                        obj[key] += 1

def get_network_object(objs):
        obj = {}
        for x in objs:
                obj[x.name] = 0
        
        return obj

def get_networks(fmc, networks):
        recursive_collector = []
        result = None
        for network in networks:
                network_id = network.get('id', None)
                network_type = network.get('type', None)

                if network_type == 'Host':
                        host = fmcapi.Hosts(fmc, id=network_id).get()
                        result = _create_network(host)
                elif network_type == 'Network':
                        net = fmcapi.Networks(fmc, id=network_id).get()
                        result = _create_network(net)
                elif network_type == 'Range':
                        range = fmcapi.Ranges(fmc, id=network_id).get()
                        result = _create_network(range, True)
                elif network_type == 'NetworkGroup':
                        networks_grp = fmcapi.NetworkGroups(fmc, id=network_id).get()
                        group_name = networks_grp.get('name', None)
                        network_group = NetworkObject(network_id, group_name)
                        
                        if networks_grp.get('objects', None) is not None:
                                for network_obj in networks_grp['objects']:
                                        group_result = get_networks(fmc, [network_obj])
                                        network_group.networks.extend(group_result)
                                network_group.depth = network_group.set_network_depth()
                                recursive_collector.append(network_group)
                        
                        if networks_grp.get('literals', None) is not None:
                                network_literals = networks_grp['literals']
                                for network_literal in network_literals:
                                        network_group.networks.append(_create_network(network_literal))
                                recursive_collector.append(network_group)
                if result:
                        recursive_collector.append(result)
                
        return recursive_collector

def _create_network(network_obj, range = False):
        network_id, network_type, network_name = _get_networks_info(network_obj)
        if range:
                network_value, available_clients = calculate_range_size(network_obj)
        else:
                network_value, available_clients = calculate_network_size(network_obj)
        return Network(network_id, network_type, network_name, network_value, available_clients)

def _get_networks_info(network_obj):
        network_id = network_obj.get('id', None)
        network_type = network_obj.get('type', None)
        network_name = network_obj.get('name', None)
        return network_id, network_type, network_name

def calculate_network_size(network_obj):
        network = network_obj['value']
        try:
                mask = int(network_obj['value'].split('/')[1])
                if '::' not in network_obj['value']:
                        available_clients = int(math.pow(2, 32 - mask) - 2)
                else:
                        available_clients = 'NaN'
        except:
                network = network_obj['value'] + "/32"
                available_clients = 1
        
        return network, available_clients

def calculate_range_size(network_obj):
        network = network_obj['value']
        network_from = network.split('-')[0]
        network_to = network.split('-')[1]
        try:
                network_from_mask = network_from.split('/')[1]
                network_to_mask = network_to.split('/')[1]
                available_clients = int(math.pow(2, 32 - network_from_mask) - 2) + int(math.pow(2, 32 - network_to_mask) - 2)
        except:
                network_from_mask = '/32'
                network_to_mask = '/32'
                network = "{}{}-{}{}".format(network_from, network_from_mask, network_to, network_to_mask)
                available_clients = int(network_to.split('.')[-1]) - int(network_from.split('.')[-1])
                
        return network, available_clients

def equal_network_object_finder(objs):
        for i in range(len(objs) - 1):
                for j in range(i + 1, len(objs)):
                        if isinstance(objs[i], Network) and isinstance(objs[j], Network) and objs[i].__eq__(objs[j]):
                                objs[i].equal_with += "{}, ".format(objs[j].name)
                                objs[j].equal_with += "{}, ".format(objs[i].name)
                        elif isinstance(objs[i], NetworkObject) and isinstance(objs[j], NetworkObject):
                                obj_i = objs[i].flat_network_object_grp()
                                obj_j = objs[j].flat_network_object_grp()
                                if obj_i.__eq__(obj_j):
                                        objs[i].equal_with += "{}, ".format(objs[j].name)
                                        objs[j].equal_with += "{}, ".format(objs[i].name)

def get_networks_data(networks):
        networks_data = []
        for network in networks:
                if isinstance(network, NetworkObject):
                        nets = network.flat_network_object_grp()
                        networks_data.extend([(network.name, network.depth, net.name, net.value, net.size, network.equal_with) for net in nets])
                else:
                        networks_data.append((None, None, network.name, network.value, network.size, network.equal_with))

        return networks_data

def get_networks_data_by_rule(networks):
        value = ""
        value_2 = ""
        for network in networks:
                if isinstance(network, NetworkObject):
                        nets = network.flat_network_object_grp()
                        for net in nets:
                                value_2 += "{} : {}, ".format(net.name, net.value)
                        value += "{}: ({}), ".format(network.name, value_2)
                else:
                        value += "{} : {}, ".format(network.name, network.value)

        return value

def export_to_excel(data, header, sheet_name):
        df = pd.DataFrame(data, columns=header)
        df.index = range(1, len(df)+1)
        export_dir = os.getcwd() + '/Exports/final.xlsx'
        with pd.ExcelWriter(path=export_dir, mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(excel_writer=writer, sheet_name=sheet_name)

if __name__ == "__main__":

        parser = argparse.ArgumentParser(description='FMC Analyser')
        parser.add_argument('-i', '--ip', required=True, help='ip address of FMC')
        parser.add_argument('-u', '--username', required=True, help='enter username')
        parser.add_argument('-p', '--password', required=True, help='enter password')
        parser.add_argument('-q', '--query', required=False, choices=['acp', 'ports', 'networks'], default='all', help='chose from list or leave blank and run all by default')
        parser.add_argument('-d', '--deploy', required=False, default=False, help='enable auto deploy with True. By default it is False')
        ARGS = parser.parse_args()

        fmc_init(ARGS.ip, ARGS.username, ARGS.password, ARGS.query, ARGS.deploy)
