import fmcapi
from AccessPolicy import AccessPolicy
from AccessRule import AccessRule
import pandas as pd
from pprint import pprint

def fmc_init():
    with fmcapi.FMC(
        host='192.168.33.193',
        username='admin',#input('Enter the username: '),
        password='GetCon135!',#input('Enter the password: '),
        autodeploy=False,
    ) as fmc:
        headers = ['Access Policy', 'Access Rule', 'Action', 'Enabled', 'Source Networks', 'Source Zones', 'Destination Networks', 'Destination Zones', 'Destination Ports']
        #policies = get_access_policies(fmc)
        #rules = []
        #for policy in policies:
        #      rules.extend(get_access_rules(fmc, policy.id, policy.name))
        #export_to_excel(rules, headers)
        #equal_port_object_finder(fmc)
        equal_network_object_finder(fmc)
        print('Done')

def get_access_policies(fmc):
        acp = fmcapi.AccessPolicies(fmc)
        policies = []
        for acp in acp.get()['items']:
            id = acp.get('id', None)
            name = acp.get('name', None)
            policies.append(AccessPolicy(id, name))
        
        return policies


def get_access_rules(fmc, acp_id, acp_name):
        accessrule = fmcapi.AccessRules(fmc, acp_id=acp_id)
        rules = []
        for rule in accessrule.get()['items']:
                access_policy = acp_name
                id = rule.get('id', None)
                name = rule.get('name', None)
                action = rule.get('action', None)
                enabled = rule.get('enabled', None)
                source_network, destination_networks = get_networks(fmc, rule)
                source_zones, destination_zones = get_name_from_zones(rule)
                destination_ports = get_ports(fmc, rule)
                rules.append(AccessRule(access_policy, id, name, action, enabled, source_network, source_zones, destination_networks, destination_ports, destination_zones))
        return rules

def get_name_from_zones(rule):
        s_zones = rule.get('sourceZones', None)
        d_zones = rule.get('destinationZones', None)
        if s_zones is not None:
                s_zones =  s_zones['objects'][0]['name']
        if d_zones is not None:
                d_zones =  d_zones['objects'][0]['name']
        return s_zones, d_zones

def get_ports(fmc, rule):
        d_ports = rule.get('destinationPorts', None)
        d_ports_list = []
        if d_ports is not None:
                for d_port in d_ports['objects']:
                        d_port_obj = []
                        d_ports_id = d_port['id']
                        d_ports_type = d_port['type']
                        if d_ports_type == 'ProtocolPortObject':
                                d_port_obj.append(fmcapi.ProtocolPortObjects(fmc, id=d_ports_id).get())
                        elif d_ports_type == 'PortObjectGroup':
                                d_port_obj_group = fmcapi.PortObjectGroups(fmc, id=d_ports_id).get()
                                for d_port in d_port_obj_group['objects']:
                                        d_ports_id = d_port['id']
                                        d_port_obj.append(fmcapi.ProtocolPortObjects(fmc, id=d_ports_id).get())
                        for d_port in d_port_obj:
                                d_ports_name = d_port['name']
                                d_ports_port = d_port['port']
                                d_ports_protocol = d_port['protocol']
                                d_ports_list.append('{} - {} {}'.format(d_ports_name, d_ports_protocol, d_ports_port))
        return d_ports_list

def get_networks(fmc, rule):
        s_networks = rule.get('sourceNetworks', None)
        d_networks = rule.get('destinationNetworks', None)
        s_networks_list = []
        d_networks_list = []
        if s_networks is not None:
                for s_network in s_networks['objects']:
                        recursive_collector_source = []
                        s_networks_list.extend(recursive(fmc, s_network, recursive_collector_source))
        if d_networks is not None:
                for d_network in d_networks['objects']:
                        recursive_collector_destination = []
                        d_networks_list.extend(recursive(fmc, d_network, recursive_collector_destination))
        
        return s_networks_list, d_networks_list

def recursive(fmc, network, recursive_collector):
        networks = []
        networks_grp = None

        network_name = network['name']
        network_id = network['id']
        network_type = network['type']

        if network_type == 'Host':
                networks.append(fmcapi.Hosts(fmc, id=network_id).get())
        elif network_type == 'Network':
                networks.append(fmcapi.Networks(fmc, id=network_id).get())
        elif network_type == 'NetworkGroup':
                networks_grp = fmcapi.NetworkGroups(fmc, id=network_id).get()

                if networks_grp.get('objects', None) is not None:
                        for network_obj in networks_grp['objects']:
                                recursive(fmc, network_obj, recursive_collector)

                if networks_grp.get('literals', None) is not None:
                        networks = networks_grp['literals']

        for network in networks:
                network_value = network.get('value', None)
                recursive_collector.append('{} - {}'.format(network_name, network_value))

        return recursive_collector

def equal_port_object_finder(fmc):
        final = []
        port_objs =  fmcapi.ProtocolPortObjects(fmc).get()
        for i in range(len(port_objs['items']) - 1):
                for j in range(i + 1, len(port_objs['items'])):
                        if port_objs['items'][i]['protocol'] == port_objs['items'][j]['protocol'] and port_objs['items'][i]['port'] == port_objs['items'][j]['port']:
                                final.append('Port Object: {} = {}'.format(port_objs['items'][i]['name'], port_objs['items'][j]['name']))

        port_obj_groups = fmcapi.PortObjectGroups(fmc).get()
        for i in range(len(port_obj_groups['items']) - 1):
                for j in range(i + 1, len(port_obj_groups['items'])):
                        counter = 0
                        if len(port_obj_groups['items'][i]['objects']) == len(port_obj_groups['items'][j]['objects']):
                                for port_obj_i in port_obj_groups['items'][i]['objects']:
                                        port_id_i = port_obj_i['id']
                                        protocol_port_obj_i = fmcapi.ProtocolPortObjects(fmc, id=port_id_i).get()
                                        for port_obj_j in port_obj_groups['items'][j]['objects']:
                                                port_id_j = port_obj_j['id']
                                                protocol_port_obj_j = fmcapi.ProtocolPortObjects(fmc, id=port_id_j).get()
                                                if protocol_port_obj_i['protocol'] == protocol_port_obj_j['protocol'] and protocol_port_obj_i['port'] == protocol_port_obj_j['port']:
                                                        counter += 1
                                                        if counter == len(port_obj_groups['items'][i]['objects']):
                                                                final.append('Port Object Group: {} = {}'.format(port_obj_groups['items'][i]['name'], port_obj_groups['items'][j]['name']))
                                                        break
        pprint(final)
        return final

def equal_network_object_finder(fmc):
        final = []
        host_objs =  fmcapi.Hosts(fmc).get()
        final.extend(network_object_helper(host_objs))
        network_objs =  fmcapi.Networks(fmc).get()
        final.extend(network_object_helper(network_objs))
                       
        pprint(final)
        return final

def network_object_helper(objs):
        final = []
        for i in range(len(objs['items']) - 1):
                for j in range(i + 1, len(objs['items'])):
                        if objs['items'][i]['value'] == objs['items'][j]['value']:
                                final.append('{} = {}'.format(objs['items'][i]['name'], objs['items'][j]['name']))
        return final

def test(fmc):
        final = []
        network_obj_groups = fmcapi.NetworkGroups(fmc).get()
        for i in range(len(network_obj_groups['items']) - 1):
                list_i = []
                network_obj_groups_collector_i = []
                for j in range(i + 1, len(network_obj_groups['items'])):
                        counter = 0
                        list_j = []
                        network_obj_groups_collector_j = []
                        if network_obj_groups['items'][i].get('objects', None) is not None and network_obj_groups['items'][j].get('objects', None) is not None:
                                if len(network_obj_groups['items'][i]['objects']) == len(network_obj_groups['items'][j]['objects']):
                                        for network_obj_i in network_obj_groups['items'][i]['objects']:
                                                list_i.extend(recursive(fmc, network_obj_i, network_obj_groups_collector_i))
                                                for network_obj_j in network_obj_groups['items'][j]['objects']:
                                                        list_j.extend(recursive(fmc, network_obj_j, network_obj_groups_collector_j))
                                                        if len(list_i) == len(list_j):
                                                                for a in list_i:
                                                                        for b in list_j:
                                                                                if a == b:
                                                                                        counter +=1
                                                                                        if counter == len(list_i):
                                                                                                final.append('Network Group: {} = {}'.format(network_obj_groups['items'][i]['name'], network_obj_groups['items'][j]['name']))
                                                                                        break


                        elif network_obj_groups['items'][i].get('literals', None) is not None and network_obj_groups['items'][j].get('literals', None) is not None:
                                if len(network_obj_groups['items'][i]['literals']) == len(network_obj_groups['items'][j]['literals']):
                                        for network_obj_i in network_obj_groups['items'][i]['literals']:
                                                list_i.extend(recursive(fmc, network_obj_i, network_obj_groups_collector_i))
                                                for network_obj_j in network_obj_groups['items'][j]['literals']:
                                                        list_j.extend(recursive(fmc, network_obj_j, network_obj_groups_collector_j))
                                                        if len(list_i) == len(list_j):
                                                                for a in list_i:
                                                                        for b in list_j:
                                                                                if a == b:
                                                                                        counter +=1
                                                                                        if counter == len(list_i):
                                                                                                final.append('Network Group: {} = {}'.format(network_obj_groups['items'][i]['name'], network_obj_groups['items'][j]['name']))
                                                                                        break
        

def export_to_excel(rules, headers):
        data = [(rule.access_policy, rule.name, rule.action, rule.enabled, rule.source_networks, rule.source_zones, rule.destination_networks, rule.destination_zones, rule.destination_ports) for rule in rules]
        df = pd.DataFrame(data, columns=headers)
        df.to_excel('access_rules.xlsx')


def get_data_by_name(data, name):
        for item in data['items']:
                 if item['name'] == name:
                        return item
        return None


def process_network_literals(literal):
        resultlist = []
        for item in literal:
                if item['type'] == 'Network': 
                        result = item['value']

                elif item['type'] == 'Host': 
                        result = item['value']
                else: 
                      raise TypeError('Only Network and Host type supported')
                resultlist.append(result)
        return resultlist


def process_network_objects(object, network_groups, networks, hosts, flattened_groups: dict ):
        resultlist = []
        for item in object:
                result = None
                if item['type'] == 'Network': 
                        network = get_data_by_name(networks,item['name'])
                        if network:
                                result = network['value']
                elif item['type'] == 'Host': 
                        host = get_data_by_name(hosts,item['name'])
                        if host:
                                result = host['value']
                elif item['type'] == 'NetworkGroup': 
                        if flattened_groups and item['name'] in flattened_groups: # get from already flattened group
                                group_result = flattened_groups[item['name']]
                        else: #group not processed yet
                                network_group = get_data_by_name(network_groups, item['name'])
                                if network_group:
                                        group_result = process_network_objects(network_group['objects'],network_groups,networks,hosts,flattened_groups)
                        resultlist.extend(group_result)
                else:
                        raise TypeError('Only NetworkGroup, Network and Host type supported')
                if result:
                        resultlist.append(result)
        return resultlist

def flatten_networks(network_groups,networks,hosts):
        result = {}
        for network_group in network_groups['items']:
            objects = network_group.get('objects', None)
            literals = network_group.get('literals', None)
            
            if objects: 
                value_1 = process_network_objects(objects,network_groups,networks,hosts,result)
                result[network_group['name']] = value_1
            if literals:
                value_2 = process_network_literals(literals)
                result[network_group['name']] = value_2
        return result

def test01():
    with fmcapi.FMC(
        host='192.168.33.193',
        username='admin',#input('Enter the username: '),
        password='GetCon135!',#input('Enter the password: '),
        autodeploy=False,
    ) as fmc:
        hosts = fmcapi.Hosts(fmc=fmc).get()
        networks = fmcapi.Networks(fmc=fmc).get()
        network_groups = fmcapi.NetworkGroups(fmc=fmc).get()
        result = flatten_networks(network_groups,networks,hosts)


        #print(hosts)
        #print(networks)
        #print(network_groups)
        print(result)



test01()
