class Port:
    def __init__(self, id, name, protocol, port):
        self.id = id
        self.name = name
        self.protocol = protocol
        self.port = port
        self.size = self.calculate_protocol_port_object_size()
        self.is_risky = self._is_risky_port([])
        self.equal_with = ""
    
    def __eq__(self, __value: object) -> bool:
        return self.protocol == __value.protocol and self.port == __value.port
    
    def calculate_protocol_port_object_size(self):
        size = 1
        if "-" in self.port:
            size = int(self.port.split("-")[1]) - (int(self.port.split("-")[0]) - 1)
        return size

    def _is_risky_port(self, risky_ports):
        for port in risky_ports:
             if self.protocol == str(port).split(' ')[0] and self.port == str(port).split(' ')[1]:
                  return True
        return False
    
    def get_size(self):
        return int(self.size)