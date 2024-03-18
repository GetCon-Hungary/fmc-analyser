from Models.Port import Port

class PortGroup:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.ports = []
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
        
    def flat_port_object_grp(self):
        final = []
        for port_obj in self.ports:
                if isinstance(port_obj, Port):
                        final.append(port_obj)
                elif isinstance(port_obj, PortGroup):
                        final.extend(port_obj.flat_port_object_grp())
        return final
        
    def get_size(self):
        summ = 0
        for port in self.ports:
            summ += port.get_size()

        return summ