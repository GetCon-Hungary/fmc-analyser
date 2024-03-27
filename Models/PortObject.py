#ToDo: rename PortGroup make subclass of Port
class PortObject:
    def __init__(self, id, name, ports):
        self.id = id
        self.name = name
        self.ports = ports
        self.equal_with = ""
    
    def __eq__(self, __value: object) -> bool:
        counter = 0
        if len(self.ports) == len(__value.ports):
            for i in range(len(self.ports)):
                for j in range(len(__value.ports)):
                    if self.ports[i].__eq__(__value.ports[j]):
                        counter += 1
                        if counter == len(self.ports):
                            return True
            return False
        else:
            return False
        
    def get_size(self):
        summ = 0
        for port in self.ports:
            summ += port.get_size()

        return summ
