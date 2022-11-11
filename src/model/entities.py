from collections.abc import MutableMapping

class Entity(MutableMapping):

    def __init__(self):
        pass


class ContextEntity(Entity):

    def __init__(self):
        super().__init__(self)    