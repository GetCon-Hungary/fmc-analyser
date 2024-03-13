import fmcapi
from Models.AccessPolicy import AccessPolicy
from Models.AccessRule import AccessRule
from Models.PortGroup import PortGroup
from Models.Port import Port
from Models.NetworkGroup import NetworkGroup
from Models.Network import Network
import argparse
import ExportToExcel as exp
from FMCLoader import FMCLoader

def fmc_init(ip, user, passw, query):
    with fmcapi.FMC(host=ip, username=user, password=passw, autodeploy=False) as fmc:
        if query == 'acp' or query == 'all':
                acps = fmcapi.AccessPolicies(fmc).get()
                policies = get_access_policies(fmc, acps['items'])
                exp.export_access_rules(policies)

                for policy in policies:    
                        enabled_count = policy.enabled_rules_count()
                        allowed_count = policy.allowed_rules_count()
                        allowed_ratio = policy.allowed_rules_ratio()
                        enabled_ratio = policy.enabled_rules_ratio()
                        print(str(enabled_ratio) + " " + str(len(policy.rules)) + " " + str(enabled_count) + " " + str(allowed_ratio) + " " + str(len(policy.rules)) + " " + str(allowed_count))
                        
                        print(policy.name)
                        for x in policy.rules:
                                print("halo")
                                print(str(x.get_source_network_size()) + " " + str(x.get_destination_network_size()))
                                print("portok")
                                print(str(x.get_source_port_size()) + " " + str(x.get_destination_port_size()))

        if query == 'ports' or query == 'all':
                port_objs = []
                protocol_port_objs = fmcapi.ProtocolPortObjects(fmc).get()
                port_obj_groups = fmcapi.PortObjectGroups(fmc).get()

                port_objs.extend(get_ports(fmc, protocol_port_objs['items']))
                port_objs.extend(get_ports(fmc, port_obj_groups['items']))
                equal_port_object_finder(port_objs)
                exp.export_ports(port_objs)

        if query == 'networks' or query == 'all':
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
                exp.export_networks(network_objs)

        print('Done')

def get_access_policies(fmc, acps):
        policies = []
        for acp in acps:
            id = acp.get('id', None)
            name = acp.get('name', None)
            accessrules = fmcapi.AccessRules(fmc, acp_id=id).get()
            rules = get_access_rules(fmc, accessrules['items'])
            policies.append(AccessPolicy(id, name, rules))
        
        return policies

def get_access_rules(fmc, accessrules):
        rules = []
        for rule in accessrules:
                id = rule.get('id', None)
                name = rule.get('name', None)
                action = rule.get('action', None)
                enabled = rule.get('enabled', None)
                ac_rule = AccessRule(id, name, action, enabled)
                ac_rule.source_zones, ac_rule.destination_zones = ac_rule.get_zones_by_rule(rule)
                ac_rule.source_networks, ac_rule.destination_networks = get_networks_by_rule(fmc, rule)
                ac_rule.source_ports, ac_rule.destination_ports = get_ports_by_rule(fmc, rule)
                rules.append(ac_rule)
        
        return rules

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
                if s_literals is not None:
                        s_ports_list.extend(get_ports(fmc, s_literals))
        if d_ports is not None:
                d_objects = d_ports.get('objects', None)
                d_literals = d_ports.get('literals', None)
                if d_objects is not None:
                        d_ports_list.extend(get_ports(fmc, d_objects))
                if d_literals is not None:
                        d_ports_list.extend(get_ports(fmc, d_literals))
                        
        return s_ports_list, d_ports_list
    
def get_networks_by_rule(fmc, rule):
        s_networks = rule.get('sourceNetworks', None)
        d_networks = rule.get('destinationNetworks', None)
        s_networks_list = []
        d_networks_list = []
        if s_networks is not None:
                s_objects = s_networks.get('objects', None)
                s_literals = s_networks.get('literals', None)
                if s_objects is not None:
                        for s_network in s_objects:
                                s_networks_list.extend(get_networks(fmc, [s_network]))
                if s_literals is not None:
                        for s_network in s_literals:
                                s_networks_list.extend(get_networks(fmc, [s_network]))
        if d_networks is not None:
                d_objects = d_networks.get('objects', None)
                d_literals = d_networks.get('literals', None)
                if d_objects is not None:
                        for d_network in d_objects:
                                d_networks_list.extend(get_networks(fmc, [d_network]))
                if d_literals is not None:
                        for d_network in d_literals:
                                d_networks_list.extend(get_networks(fmc, [d_network]))
        
        return s_networks_list, d_networks_list


def port_object_count(obj, accessPolicy):
        for policy in accessPolicy:
                for rule in policy.rules:
                        for key in obj.keys():
                                if rule.port_used_in_rule(key):
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
                        port_obj_grp = fmcapi.PortObjectGroups(fmc, id=port_id).get()
                        group_name = port_obj_grp['name']
                        port_group = PortGroup(port_id, group_name)
                        port_group.ports.extend(get_ports(fmc, port_obj_grp['objects']))
                        port_objs.append(port_group)
        return port_objs

def _create_port(port_obj):
        port = Port(id=port_obj.get('id', None), name= port_obj.get('name', None), protocol=port_obj.get('protocol', None), port=port_obj.get('port', None))
        port.calculate_protocol_port_object_size()
        port.is_risky = port._is_risky_port([])
        return port

def equal_port_object_finder(ports):
        for i in range(len(ports) - 1):
                for j in range(i + 1, len(ports)):
                        if isinstance(ports[i], Port) and isinstance(ports[j], Port) and ports[i].__eq__(ports[j]):
                                ports[i].equal_with += "{}, ".format(ports[j].name)
                                ports[j].equal_with += "{}, ".format(ports[i].name)  
                        elif isinstance(ports[i], PortGroup) and isinstance(ports[j], PortGroup) and ports[i].__eq__(ports[j]):
                                ports[i].equal_with += "{}, ".format(ports[j].name)
                                ports[j].equal_with += "{}, ".format(ports[i].name)



def network_object_count(obj, accessPolicy):
        for policy in accessPolicy:
                for rule in policy.rules:
                        for key in obj.keys():
                                if rule.network_used_in_rule(key):
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

                if network_id is not None:
                        if network_type == 'Host':
                                host = fmcapi.Hosts(fmc, id=network_id).get()
                                result = _create_network(host)
                        elif network_type == 'Network':
                                net = fmcapi.Networks(fmc, id=network_id).get()
                                result = _create_network(net)
                        elif network_type == 'Range':
                                range = fmcapi.Ranges(fmc, id=network_id).get()
                                result = _create_network(range)
                        elif network_type == 'NetworkGroup':
                                networks_grp = fmcapi.NetworkGroups(fmc, id=network_id).get()
                                group_name = networks_grp.get('name', None)
                                network_group = NetworkGroup(network_id, group_name)
                                
                                if networks_grp.get('objects', None) is not None:
                                        for network_obj in networks_grp['objects']:
                                                group_result = get_networks(fmc, [network_obj])
                                                network_group.networks.extend(group_result)
                                        network_group.depth = network_group.get_network_depth()
                                        recursive_collector.append(network_group)
                                
                                if networks_grp.get('literals', None) is not None:
                                        network_literals = networks_grp['literals']
                                        for network_literal in network_literals:
                                                network_group.networks.append(_create_network(network_literal))
                                        recursive_collector.append(network_group)
                        if result:
                                recursive_collector.append(result)
                
        return recursive_collector

def _create_network(network_obj):
        network = Network(id=network_obj.get('id', None), type=network_obj.get('type', None), name=network_obj.get('name', None))
        network.calculate_network_size(network_obj)
        return network

def equal_network_object_finder(objs):
        for i in range(len(objs) - 1):
                for j in range(i + 1, len(objs)):
                        if isinstance(objs[i], Network) and isinstance(objs[j], Network) and objs[i].__eq__(objs[j]):
                                objs[i].equal_with += "{}, ".format(objs[j].name)
                                objs[j].equal_with += "{}, ".format(objs[i].name)
                        elif isinstance(objs[i], NetworkGroup) and isinstance(objs[j], NetworkGroup):
                                obj_i = objs[i].flat_network_object_grp()
                                obj_j = objs[j].flat_network_object_grp()
                                if obj_i.__eq__(obj_j):
                                        objs[i].equal_with += "{}, ".format(objs[j].name)
                                        objs[j].equal_with += "{}, ".format(objs[i].name)
                
if __name__ == "__main__":
        try:
                parser = argparse.ArgumentParser(description='FMC Analyser')
                parser.add_argument('-h', '--host', required=True, help='ip address of FMC')
                parser.add_argument('-u', '--username', required=True, help='enter username')
                parser.add_argument('-p', '--password', required=True, help='enter password')
                parser.add_argument('-a', '--acp', required=False, choices=['acp', 'ports', 'networks'], default='all', help='chose from list or leave it blank and run all by default')
                parser.add_argument('-c', '--config', required=False, default='config.ini', help='enter the configurationn file or leave it blank and run config.ini by default')

                parser.add_argument('-q', '--query', required=False, choices=['acp', 'ports', 'networks'], default='all', help='chose from list or leave blank and run all by default')
                ARGS = parser.parse_args()

                fmcloader = FMCLoader(ARGS.host, ARGS.username, ARGS.password, ARGS.query)
        except:
                fmcloader = FMCLoader('192.168.33.193', 'admin', 'GetCon135!!')
                #fmcloader = FMCLoader('192.168.33.193', 'farkas.balazs', 'Alma123!!')