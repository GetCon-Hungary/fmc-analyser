from netaddr import IPNetwork, IPRange

class Network:
    def __init__(self, id: str, type: str, name: str, value: str):
        self.id = id
        self.type = type
        self.name = name
        self.value = self.create_network_value(value)
        self.size = self.value.size
        self.equal_with = ""
    
    def __eq__(self, __value: object) -> bool:
        return self.type == __value.type and self.value == __value.value

    def create_network_value(self, network_value: str):
        value = None
        if '-' in network_value:
            value = IPRange(network_value.split('-')[0], network_value.split('-')[1])
        else:
            value = IPNetwork(network_value)
        return value

    def get_size(self):
        return self.size