class Port:
    def __init__(self, id, group_name, name, protocol, port, size, is_risky):
        self.id = id
        self.group_name = group_name
        self.name = name
        self.protocol = protocol
        self.port = port
        self.size = size
        self.is_risky = is_risky