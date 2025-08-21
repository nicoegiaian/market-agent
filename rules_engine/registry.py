RULES_REGISTRY = {}

def register(id_):
    def deco(cls):
        RULES_REGISTRY[id_] = cls
        return cls
    return deco
