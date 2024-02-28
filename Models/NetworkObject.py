class NetworkObject:
    usageCount = 0

    def __init__(self, id, group_name, networks, depth, **kwargs):
        self.id = id
        self.group_name = group_name
        #c = kwargs.get('c', None)
        self.networks = networks
        self.depth = depth

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