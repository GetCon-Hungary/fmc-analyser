class NetworkObject:
    usageCount = 0

    def __init__(self, id, name, **kwargs):
        self.id = id
        self.name = name
        #c = kwargs.get('c', None)