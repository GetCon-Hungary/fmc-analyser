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

def fmc_init():
    with fmcapi.FMC(
        host='192.168.33.193',
        username='admin',#input('Enter the username: '),
        password='GetCon135!!',#input('Enter the password: '),
        autodeploy=False,
    ) as fmc:
        #obj = get_network_object(fmc)
        #print(obj)
        
        
        acp = fmcapi.AccessPolicies(fmc).get()
        policies = get_access_policies(fmc, acp)
        access_rule_header = ['Access Rule', 'Action', 'Enabled', 'Source Networks', 'Source Zones', 'Source Ports', 'Destination Networks', 'Destination Zones', 'Destination Ports']
        for policy in policies:
                access_rule_data = [(rule.name, rule.action, rule.enabled, get_networks_data_by_rule(rule.source_networks), rule.source_zones, get_ports_data_by_rule(rule.source_ports) , get_networks_data_by_rule(rule.destination_networks), rule.destination_zones, get_ports_data_by_rule(rule.destination_ports)) for rule in policy.rules]
                export_to_excel(access_rule_data, access_rule_header, 'access_rules_of_{}'.format(policy.name))
        
        """
        ports_header = ['Group Name', 'Name', 'Protocol', 'Port', 'Size', 'Risky', 'Equal with']
        ports = []
        protocol_port_objs = fmcapi.ProtocolPortObjects(fmc).get()
        port_obj_groups = fmcapi.PortObjectGroups(fmc).get()
        ports.extend(get_ports(fmc, protocol_port_objs['items']))
        ports.extend(get_ports(fmc, port_obj_groups['items']))
        equal_port_object_finder(ports)
        ports_data = get_ports_data(ports)
        export_to_excel(ports_data, ports_header, 'ports')
        

        network_header = ['Group Name', 'Name', 'Value', 'Mask', 'Size', 'Equal with']
        network_objs = []
        hosts = fmcapi.Hosts(fmc).get()
        networks = fmcapi.Networks(fmc).get()
        ranges = fmcapi.Ranges(fmc).get()
        network_groups = fmcapi.NetworkGroups(fmc).get()
        network_objs.extend(get_networks(fmc, hosts['items']))
        network_objs.extend(get_networks(fmc, networks['items']))
        network_objs.extend(get_networks(fmc, ranges['items']))
        network_objs.extend(get_networks(fmc, network_groups['items']))
        equal_network_object_finder(network_objs)
        network_data = get_networks_data(network_objs)
        export_to_excel(network_data, network_header, 'networks')
        """
        print('Done')

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

def get_networks_data_by_rule(networks):
        value = ""
        value_2 = ""
        for network in networks:
                if isinstance(network, NetworkObject):
                        nets = flat_network_object_grp(network)
                        for net in nets:
                                value_2 += "{} : {}, ".format(net.name, net.value)
                        value += "{}: ({}), ".format(network.name, value_2)
                else:
                        value += "{} : {}, ".format(network.name, network.value)

        return value


def get_network_object(fmc):
        netObj = fmcapi.Networks(fmc).get()
        groupObj = fmcapi.NetworkGroups(fmc).get()
        hostObj = fmcapi.Hosts(fmc).get()
        rangeObj = fmcapi.Ranges(fmc).get()
        obj = {}
        for x in netObj['items']:
                obj[x['name']] = 0
        for x in groupObj['items']:
                obj[x['name']] = 0
        for x in hostObj['items']:
                obj[x['name']] = 0
        for x in rangeObj['items']:
                obj[x['name']] = 0
        
        return obj

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
        return True

def equal_port_object_finder(ports):
        for i in range(len(ports) - 1):
                for j in range(i + 1, len(ports)):
                        if isinstance(ports[i], Port) and isinstance(ports[j], Port):
                                if ports[i].__eq__(ports[j]):
                                        ports[i].equal_with += "{}, ".format(ports[j].name)
                                        ports[j].equal_with += "{}, ".format(ports[i].name)  
                        elif isinstance(ports[i], PortObject) and isinstance(ports[j], PortObject):
                                if ports[i].__eq__(ports[j]):
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

def get_networks_by_rule(fmc, rule):
        s_networks = rule.get('sourceNetworks', None)
        d_networks = rule.get('destinationNetworks', None)
        s_networks_list = []
        d_networks_list = []
        if s_networks is not None:
                for s_network in s_networks['objects']:
                        source_collector = get_networks(fmc, [s_network])
                        s_networks_list.extend(source_collector)
        if d_networks is not None:
                for d_network in d_networks['objects']:
                        dest_collector = get_networks(fmc, [d_network])
                        d_networks_list.extend(dest_collector)
        
        return s_networks_list, d_networks_list

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
                        network_group = NetworkObject(network_id, group_name, [], 1)

                        if networks_grp.get('objects', None) is not None:
                                for network_obj in networks_grp['objects']:
                                        group_result = get_networks(fmc, [network_obj])
                                        network_group.networks.extend(group_result)
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
                network_value, available_clients, network_mask = calculate_range_size(network_obj)
        else:
                network_value, available_clients, network_mask = calculate_network_size(network_obj)
        return Network(network_id, network_type, network_name, network_value, available_clients, network_mask)

def _get_networks_info(network_obj):
        network_id = network_obj.get('id', None)
        network_type = network_obj.get('type', None)
        network_name = network_obj.get('name', None)
        return network_id, network_type, network_name

def calculate_network_size(network_obj):
        try:
                network = network_obj['value'].split('/')[0]
                mask = int(network_obj['value'].split('/')[1])
                if '::' not in network_obj['value']:
                        available_clients = int(math.pow(2, 32 - mask) - 2)
                else:
                        available_clients = 'NaN'
        except:
                network = network_obj['value']
                mask = "32"
                available_clients = 1
        
        return network, available_clients, "/{}".format(mask)

def calculate_range_size(network_obj):
        network = network_obj['value']
        network_from = network.split('-')[0]
        network_to = network.split('-')[1]
        try:
                network_from_mask = network_from.split('/')[1]
                network_to_mask = network_to.split('/')[1]
                available_clients = int(math.pow(2, 32 - network_from_mask) - 2) + int(math.pow(2, 32 - network_to_mask) - 2)
        except:
                network_from_mask = '32'
                network_to_mask = '32'
                available_clients = int(network_to.split('.')[-1]) - int(network_from.split('.')[-1])
                
        return network, available_clients, "/{} /{}".format(network_from_mask, network_to_mask)

def equal_network_object_finder(objs):
        for i in range(len(objs) - 1):
                for j in range(i + 1, len(objs)):
                        if isinstance(objs[i], Network) and isinstance(objs[j], Network):
                                if objs[i].__eq__(objs[j]):
                                        objs[i].equal_with += "{}, ".format(objs[j].name)
                                        objs[j].equal_with += "{}, ".format(objs[i].name)
                        elif isinstance(objs[i], NetworkObject) and isinstance(objs[j], NetworkObject):
                                obj_i = flat_network_object_grp(objs[i])
                                obj_j = flat_network_object_grp(objs[j])
                                if obj_i.__eq__(obj_j):
                                        objs[i].equal_with += "{}, ".format(objs[j].name)
                                        objs[j].equal_with += "{}, ".format(objs[i].name)

def flat_network_object_grp(network_obj_group):
        final = []
        for network_obj in network_obj_group.networks:
                if isinstance(network_obj, Network):
                        final.append(network_obj)
                elif isinstance(network_obj, NetworkObject):
                        final = flat_network_object_grp(network_obj)
        return final

def get_networks_data(networks):
        networks_data = []
        for network in networks:
                if isinstance(network, NetworkObject):
                        nets = flat_network_object_grp(network)
                        networks_data.extend([(network.name, net.name, net.value, net.mask, net.size, network.equal_with) for net in nets])
                else:
                        networks_data.append((None, network.name, network.value, network.mask, network.size, network.equal_with))

        return networks_data

def export_to_excel(data, header, sheet_name):
        df = pd.DataFrame(data, columns=header)
        export_dir = os.getcwd() + '/Exports/final.xlsx'
        with pd.ExcelWriter(path=export_dir, mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(excel_writer=writer, sheet_name=sheet_name)

fmc_init()