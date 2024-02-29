class Network:
    def __init__(self, id, type, name, value, size, mask):
        self.id = id
        self.type = type
        self.name = name
        self.value = value
        self.size = size
        self.mask = mask
        self.equal_with = ""
    
    def __eq__(self, __value: object) -> bool:
        return self.type == __value.type and self.value == __value.value