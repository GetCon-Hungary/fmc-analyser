class Port:
    def __init__(self, id, name, protocol, port, size, is_risky):
        self.id = id
        self.name = name
        self.protocol = protocol
        self.port = port
        self.size = size
        self.is_risky = is_risky
        self.equal_with = ""
    
    def __eq__(self, __value: object) -> bool:
        return self.protocol == __value.protocol and self.port == __value.port