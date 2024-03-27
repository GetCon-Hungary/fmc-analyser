from Models.Network import Network

#ToDo: rename NetworkGroup make subclass of Network
class NetworkObject():
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
    
    def flat_network_object_grp(self):
        final = []
        for network_obj in self.networks:
                if isinstance(network_obj, Network):
                        final.append(network_obj)
                elif isinstance(network_obj, NetworkObject):
                        final.extend(network_obj.flat_network_object_grp())
        return final
    
    def set_network_depth(self):
        depth = 0
        for network_obj in self.networks:
             if isinstance(network_obj, NetworkObject):
                  depth += network_obj.set_network_depth()
                  depth += 1
        return depth
    
    def get_size(self):
        summ = 0
        for network in self.networks:
            summ += network.get_size()

        return summ
