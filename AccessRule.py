class AccessRule:
    def __init__(self, access_policy, id, name, action, enabled, source_networks, source_zones, destination_networks, destination_ports, destination_zones):
        self.access_policy = access_policy
        self.id = id
        self.name = name
        self.action = action
        self.enabled = enabled
        self.source_networks = source_networks
        self.source_zones = source_zones
        self.destination_networks = destination_networks
        self.destination_ports = destination_ports
        self.destination_zones = destination_zones 
