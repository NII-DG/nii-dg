from .entities import Entity, DataEntity, ContextEntity, RootDataEntity, Metadata
import json


class ROCrate():

    def __init__(self):
        self.metadata = Metadata()
        self.rootdataentity = RootDataEntity()
        self.entities = [self.metadata, self.rootdataentity]
    
    def generate(self):
        graph = []
        for entity in self.entities:
            graph.append(entity.get_jsonld())
        context = f'{self.metadata.PROFILE}/context'
        if self.extra_terms:
            context = [context, self.extra_terms]
        return {'@context': context, '@graph': graph}


class NIIROCrate(ROCrate):
    EXTRA_TERMS = {
        "accessRights":"http://purl.org/dc/terms/accessRights",
        "dmpFormat":"https://example.com/dmpFormat", # to be updated
        "dataManagementPlan":"https://example.com/dataManagementPlan" # to be updated
    }

    def __init__(self, dmp):
        super().__init__()
        self.extra_terms = self.EXTRA_TERMS
        self.dmp = dmp