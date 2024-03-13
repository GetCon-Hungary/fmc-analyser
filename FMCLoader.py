import fmcapi
from Models.AccessPolicy import AccessPolicy
from Models.AccessRule import AccessRule
from Models.Port import Port
from Models.PortGroup import PortGroup
from Models.Network import Network
from Models.NetworkGroup import NetworkGroup

class FMCLoader():
    def __init__(self, fmc_host, username, password):
        with fmcapi.FMC(fmc_host,username=username, password=password, autodeploy=False) as fmc:

            acps = fmcapi.AccessPolicies(fmc).get()
            protocol_port_objs = fmcapi.ProtocolPortObjects(fmc).get()
            port_obj_groups = fmcapi.PortObjectGroups(fmc).get()
            hosts = fmcapi.Hosts(fmc).get()
            networks = fmcapi.Networks(fmc).get()
            ranges = fmcapi.Ranges(fmc).get()
            network_groups = fmcapi.NetworkGroups(fmc).get()

            #self.port_objs = []
            #self.port_objs.extend(self.get_ports(fmc, protocol_port_objs['items']))
            #self.port_objs.extend(self.get_ports(fmc, port_obj_groups['items']))
            self.port_objs = {}
            self.port_objs.extend(self.get_ports(fmc, protocol_port_objs['items']))

            self.network_objs = []
            #self.network_objs.extend(self.get_networks(fmc, hosts['items']))
            #self.network_objs.extend(self.get_networks(fmc, networks['items']))
            #self.network_objs.extend(self.get_networks(fmc, ranges['items']))
            self.network_objs.extend(self.get_networks(fmc, network_groups['items']))

            self.policies = self.get_access_policies(fmc, acps['items'])
    
    def get_access_policies(self, fmc, acps):
        policies = []
        for acp in acps:
            id = acp.get('id', None)
            name = acp.get('name', None)
            accessrules = fmcapi.AccessRules(fmc, acp_id=id).get()
            rules = self.get_access_rules(fmc, accessrules['items'])
            policies.append(AccessPolicy(id, name, rules))
        
        return policies
    
    def get_access_rules(self, fmc, accessrules):
        rules = []
        for rule in accessrules:
                id = rule.get('id', None)
                name = rule.get('name', None)
                action = rule.get('action', None)
                enabled = rule.get('enabled', None)
                ac_rule = AccessRule(id, name, action, enabled)
                ac_rule.source_zones, ac_rule.destination_zones = ac_rule.get_zones_by_rule(rule)
                ac_rule.source_networks, ac_rule.destination_networks = ac_rule.get_networks_by_rule(rule, self.network_objs)
                ac_rule.source_ports, ac_rule.destination_ports = ac_rule.get_ports_by_rule(rule, self.port_objs)
                rules.append(ac_rule)
        
        return rules
    
    def get_ports(self, fmc, ports):
        port_objs = []
        for port in ports:
                port_id = port.get('id', None)
                port_type = port.get('type', None)
                port_protocol = port.get('protocol', None)
                if port_id is not None:
                    if port_type == 'ProtocolPortObject':
                            if port_protocol is None:
                                port = fmcapi.ProtocolPortObjects(fmc, id=port_id).get()
                            port_objs.append(self._create_port(port))
                    elif port_type == 'PortObjectGroup':
                            group_name = port['name']
                            port_group = PortGroup(port_id, group_name)
                            port_group.ports.extend(self.get_ports(fmc, port['objects']))
                            port_objs.append(port_group)
        return port_objs
    

          
    
    def _create_port(self, port_obj):
        port = Port(id=port_obj.get('id', None), name= port_obj.get('name', None), protocol=port_obj.get('protocol', None), port=port_obj.get('port', None))
        port.calculate_protocol_port_object_size()
        port.is_risky = port._is_risky_port([])
        return port
    
    def get_networks(self, fmc, networks):
        recursive_collector = []
        result = None
        for network in networks:
                network_id = network.get('id', None)
                network_type = network.get('type', None)
                network_value = network.get('value', None)
                if network_id is not None:
                        if network_type == 'Host':
                                if network_value is None:
                                      network = fmcapi.Hosts(fmc, id=network_id).get()
                                result = self._create_network(network)
                        elif network_type == 'Network':
                                if network_value is None:
                                      network = fmcapi.Networks(fmc, id=network_id).get()
                                result = self._create_network(network)
                        elif network_type == 'Range':
                                if network_value is None:
                                      network = fmcapi.Ranges(fmc, id=network_id).get()
                                result = self._create_network(network)
                        elif network_type == 'NetworkGroup':
                                group_name = network.get('name', None)
                                network_group = NetworkGroup(network_id, group_name)
                                
                                if network.get('objects', None) is not None:
                                        for network_obj in network['objects']:
                                                group_result = self.get_networks(fmc, [network_obj])
                                                network_group.networks.extend(group_result)
                                        network_group.depth = network_group.get_network_depth()
                                        recursive_collector.append(network_group)
                                
                                if network.get('literals', None) is not None:
                                        for network_literal in network['literals']:
                                                network_group.networks.append(self._create_network(network_literal))
                                        recursive_collector.append(network_group)
                        if result:
                                recursive_collector.append(result)
                
        return recursive_collector
    
    def _create_network(self, network_obj):
        network = Network(id=network_obj.get('id', None), type=network_obj.get('type', None), name=network_obj.get('name', None))
        network.calculate_network_size(network_obj)
        return network