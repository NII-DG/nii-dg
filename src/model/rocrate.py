from .entities import Entity, DataEntity, ContextEntity, RootDataEntity, Metadata
import json

class ValidationError(Exception):
    pass

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

    def set_project_name(self):
        self.rootdataentity._jsonld["project_name"] = self.dmp["project_name"]

    def set_funder(self):
        funders = self.dmp.get("funding_agency")

        if funders:
            funder_list = []

            for fa in funders:
                ids = [item for item in [fa.get("ror"), fa.get("url")] if item]
                if len(ids) == 0:
                    raise ValidationError('Either property "ror" or "url" is required for funding agancy')

                funder = ContextEntity(ids[0], 'Organization')
                funder.set_name(fa["name"])
                funder.add_properties({'identifier':ids})
                self.entities.append(funder)
                funder_list.append({"@id":ids[0]})

            self.rootdataentity.add_properties({'funder':funder_list})

    def set_erad(self):
        erad = self.dmp.get("e-Rad_project_id")

        if erad:
            erad_e = ContextEntity(f'#e-Rad:{erad}', 'PropertyValue')
            erad_e.set_name('e-Rad Project ID')
            erad_e.add_properties({'value':erad})
            self.entities.append(erad_e)

            ids = self.rootdataentity.get("identifier")
            if ids:
                ids.append({"@id":erad_e.id})
            else:
                ids = []
            self.rootdataentity.add_properties({"identifier":ids})

    def set_field(self):
        field = self.dmp.get('research_filed')

        if field:
            self.rootdataentity.add_properties({'keywords':field})