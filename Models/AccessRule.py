class AccessRule:
    def __init__(self, access_policy, id, name, action, enabled, source_networks, source_zones, source_ports, destination_networks, destination_zones, destination_ports):
        self.access_policy = access_policy
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

    def get_source_size(self):
        summ = 0
        for network in self.source_networks:
            summ += network.get_size()

        return summ
    
    def get_destination_size(self):
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