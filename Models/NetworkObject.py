from Models.Network import Network

class NetworkObject:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.networks = []
        self.depth = 0
        self.equal_with = ""

    def __eq__(self, __value: object) -> bool:
        counter = 0
        if len(self.networks) == len(__value.networks):
            for i in range(len(self.networks)):
                for j in range(len(__value.networks)):
                    if self.networks[i].__eq__(__value.networks[j]):
                        counter += 1
                        if counter == len(self.networks):
                            return True
            return False
        else:
            return False
    
    def flat_network_object_grp(self, network_obj_group):
        final = []
        for network_obj in network_obj_group.networks:
                if isinstance(network_obj, Network):
                        final.append(network_obj)
                elif isinstance(network_obj, NetworkObject):
                        self.depth += 1
                        final = self.flat_network_object_grp(network_obj)
        return final