from Models.NetworkGroup import NetworkGroup
from Models.PortGroup import PortGroup

class AccessRule:
    def __init__(self, id, name, action, enabled):
        self.id = id
        self.name = name
        self.action = action
        self.enabled = enabled
        self.source_networks = []
        self.source_zones = []
        self.source_ports = []
        self.destination_networks = []
        self.destination_zones = []
        self.destination_ports = []
    
    def get_zones_by_rule(self, rule):
        s_zones = rule.get('sourceZones', None)
        d_zones = rule.get('destinationZones', None)
        s_zones_list = []
        d_zones_list = []
        if s_zones is not None:
                s_zones_list = [(s_zone['name']) for s_zone in s_zones['objects']]
        if d_zones is not None:
                d_zones_list = [(d_zone['name']) for d_zone in d_zones['objects']]
        return s_zones_list, d_zones_list
    
    def get_ports_by_rule(self, rule, ports):
        s_ports = rule.get('sourcePorts', None)
        d_ports = rule.get('destinationPorts', None)
        s_ports_list = []
        d_ports_list = []
        if s_ports is not None:
                s_objects = s_ports.get('objects', None)
                s_literals = s_ports.get('literals', None)
                if s_objects is not None:
                        s_ports_list.extend(self.find_port_by_id(s_objects, ports))
                if s_literals is not None:
                        s_ports_list.extend(self.find_port_by_id(s_objects, ports))
        if d_ports is not None:
                d_objects = d_ports.get('objects', None)
                d_literals = d_ports.get('literals', None)
                if d_objects is not None:
                        d_ports_list.extend(self.find_port_by_id(s_objects, ports))
                if d_literals is not None:
                        d_ports_list.extend(self.find_port_by_id(s_objects, ports))
                        
        return s_ports_list, d_ports_list
    
    def find_port_by_id(self, rule_ports, ports):
        final = []
        for port_i in rule_ports:
                port_id_i = port_i.get('id', None)
                if port_id_i is not None:
                     for port_j in ports:
                          if port_id_i == port_j.id:
                               final.append(port_j)
        return final
                     
         
    def get_networks_by_rule(self, rule, networks):
        s_networks = rule.get('sourceNetworks', None)
        d_networks = rule.get('destinationNetworks', None)
        s_networks_list = []
        d_networks_list = []
        if s_networks is not None:
                s_objects = s_networks.get('objects', None)
                s_literals = s_networks.get('literals', None)
                if s_objects is not None:
                        for s_network in s_objects:
                                s_networks_list.extend(self.find_network_by_id([s_network], networks))
                if s_literals is not None:
                        for s_network in s_literals:
                                s_networks_list.extend(self.find_network_by_id([s_network], networks))
        if d_networks is not None:
                d_objects = d_networks.get('objects', None)
                d_literals = d_networks.get('literals', None)
                if d_objects is not None:
                        for d_network in d_objects:
                                d_networks_list.extend(self.find_network_by_id([d_networks], networks))
                if d_literals is not None:
                        for d_network in d_literals:
                                d_networks_list.extend(self.find_network_by_id([d_networks], networks))
        
        return s_networks_list, d_networks_list

    def find_network_by_id(self, rule_networks, networks):
        final = []
        for network_i in rule_networks:
                network_id_i = network_i.get('id', None)
                if network_id_i is not None:
                     for network_j in networks:
                          if network_id_i == network_j.id:
                               final.append(network_j)
        return final
    
    def port_used(self, xPort, ports):
        for port in ports:
            if xPort == port.name:
                return True
        
        return False
    
    def port_used_in_rule(self, port):
        return self.port_used(port, self.source_ports) or self.port_used(port, self.destination_ports)
    
    def network_used(self, xNetwork, networks):
        for network in networks:
            if xNetwork == network.name:
                return True
        
        return False
    
    def network_used_in_rule(self, network):
        return self.network_used(network, self.source_networks) or self.network_used(network, self.destination_networks)

    def get_source_network_size(self):
        summ = 0
        for network in self.source_networks:
            summ += network.get_size()

        return summ
    
    def get_destination_network_size(self):
        summ = 0
        for network in self.destination_networks:
            summ += network.get_size()

        return summ
    
    def get_source_port_size(self):
        summ = 0
        for port in self.source_ports:
            summ += port.get_size()

        return summ
    
    def get_destination_port_size(self):
        summ = 0
        for port in self.destination_ports:
            summ += port.get_size()

        return summ
    
    def risk_category_by_port(self):
        if len(self.destination_ports) > 0:
            if len(self.destination_ports) == 1 and isinstance(self.destination_ports[0], PortGroup):
                    flattened_ports = self.destination_ports[0].flat_port_object_grp()
                    return self._return_risk(flattened_ports)
            else:
                return self._return_risk(self.destination_ports)
        else:
            return 'High'
    
    def _return_risk(self, ports: list):
        if len(ports) > 10:
            return 'High'
        elif len(ports) > 5:
            return 'Medium'
        else:
            return 'Low'

    def risk_category_by_network(self):
        if len(self.source_networks) > 0:
            for network in self.source_networks:
                if isinstance(network, NetworkGroup):
                    flattened_networks = network.flat_network_object_grp()
                    for flat_network in flattened_networks:
                        if 'any' in str(flat_network.name).lower():
                            return 'High'
                    return 'Low'
                else:
                    if 'any' in str(network.name).lower():
                        return 'High'
            return 'Low'
        else:
            return 'High'
            