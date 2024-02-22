class PortObject:
    def __init__(self, id, group_name, ports):
        self.id = id
        self.group_name = group_name
        self.ports = ports
    
    def __eq__(self, __value: object) -> bool:
        counter = 0
        if len(self.ports) == len(__value.ports):
            for i in range(len(self.ports)):
                for j in range(len(__value.ports)):
                    if self.ports[i].__eq__(__value.ports[j]):
                        counter += 1
                        if counter == len(self.ports):
                            return True
        else:
            return False