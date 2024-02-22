class Port:
    def __init__(self, id, name, protocol, port, size, is_risky):
        self.id = id
        #self.group_name = group_name
        self.name = name
        self.protocol = protocol
        self.port = port
        self.size = size
        self.is_risky = is_risky
    
    def __eq__(self, __value: object) -> bool:
        return self.protocol == __value.protocol and self.port == __value.port