from Models.PortGroup import PortGroup
import math
from Models.RiskEnum import Risk

class AccessRule:
    def __init__(self, id, name, action, enabled, source_networks, source_zones, source_ports, destination_networks, destination_zones, destination_ports):
        self.id = id
        self.name = name
        self.action = action
        self.enabled = enabled
        self.source_networks = source_networks
        self.source_zones = source_zones
        self.source_ports = source_ports
        self.destination_networks = destination_networks
        self.destination_zones = destination_zones
        self.destination_ports = destination_ports
    
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

    def get_source_networks_size(self):
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
            return Risk.High.name
    
    def _return_risk(self, ports: list):
        if len(ports) > 10:
            return Risk.High.name
        elif len(ports) > 5:
            return Risk.Medium.name
        else:
            return Risk.Low.name
    
    def risk_category_by_network_dynamic(self, acp):
        avg_ip_number = acp.calculate_avg_source_network_size_of_acp()
        if self.get_source_networks_size() > 10 * avg_ip_number:
            return Risk.High.name
        elif self.get_source_networks_size() > 5 * avg_ip_number:
            return Risk.Medium.name
        else:
            return Risk.Low.name
    
    def risk_category_by_network_static(self):
        ip_number = self.get_source_networks_size()
        mask = self._calculate_subnet_mask(ip_number)
        if mask > 21:
            return Risk.Low.name
        elif mask > 18:
            return Risk.Medium.name
        else:
            return Risk.High.name
    
    def _calculate_subnet_mask(self, ip_number):
        return 32 - math.ceil(math.log2(ip_number))