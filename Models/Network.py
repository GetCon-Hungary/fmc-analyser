from netaddr import IPNetwork, IPRange
class Network:
    def __init__(self, id, type, name):
        self.id = id
        self.type = type
        self.name = name
        self.value = None
        self.size = None
        self.equal_with = None
    
    def __eq__(self, __value: object) -> bool:
        return self.type == __value.type and self.value == __value.value

    def calculate_network_size(self, network_obj):
        if '-' in network_obj['value']:
                self.value = IPRange(network_obj['value'].split('-')[0], network_obj['value'].split('-')[1])
        else:
                self.value = IPNetwork(network_obj['value'])
        self.size = self.value.size

    def get_size(self):
        return self.size