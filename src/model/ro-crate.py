from entities import Entity, DataEntity, ContextEntity, RootDataEntity, Metadata
import json
import const


class ROCrate():

    def __init__(self):
        self.metadata = Metadata()
        self.rootdataentity = RootDataEntity()
        self.entities = [self.metadata, self.rootdataentity]
    
    def generate(self):
        graph = []
        for entity in self.entities:
            graph.append(entity.get_jsonld())
        context = f'{const.PROFILE}/context'
        if self.extra_terms:
            context = [context, self.extra_terms]
        return {'@context': context, '@graph': graph}


class NIIROCrate(ROCrate):

    def __init__(self):
        super().__init__()
        self.extra_terms = const.EXTRA_TERMS