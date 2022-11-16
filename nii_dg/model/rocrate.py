import json

from .entities import (ContextEntity, DataEntity, Entity, Metadata,
                       RootDataEntity)


class ValidationError(Exception):
    pass


class ROCrate():

    def __init__(self):
        self.metadata = Metadata()
        self.rootdataentity = RootDataEntity()
        self.entities = [self.metadata, self.rootdataentity]

    def get_by_type(self, e_type):
        ents = []
        for e in self.entities:
            if e.get("@type") == e_type:
                ents.append(e)
        return ents

    def get_by_name(self, e_name):
        for e in self.entities:
            if e.get("name") == e_name:
                return e
        raise ValidationError(f'entity with name "{e_name}" is not found')

    def add_entity(self, id, e_type, properties):
        e = ContextEntity(id, e_type)
        e.add_properties(properties)
        self.entities.append(e)

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
        "accessRights": "http://purl.org/dc/terms/accessRights",
        "dmpFormat": "https://example.com/dmpFormat",  # to be updated
        "dataManagementPlan": "https://example.com/dataManagementPlan"  # to be updated
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

                properties = {
                    "name": fa["name"]
                }
                if len(ids) == 2:
                    properties["sameAs"] = ids[1]

                self.add_entity(ids[0], 'Organization', properties)
                funder_list.append({"@id": ids[0]})

            self.rootdataentity.add_properties({'funder': funder_list})

    def add_erad(self, erad, erad_type):
        erad_e = ContextEntity(f'#e-Rad:{erad}', 'PropertyValue')
        if erad_type == 'project':
            erad_e.set_name('e-Rad Project ID')
        elif erad_type == 'researcher':
            erad_e.set_name('e-Rad researcher number')
        else:
            raise ValidationError('e-rad type should be "project" or "researcher".')
        erad_e.add_properties({'value': erad})
        self.entities.append(erad_e)
        return erad_e

    def set_erad(self):
        erad = self.dmp.get("e-Rad_project_id")

        if erad:
            erad_e = self.add_erad(erad, 'project')

            ids = self.rootdataentity.get("identifier")
            if ids is None:
                ids = []
            ids.append({"@id": erad_e.id})
            self.rootdataentity.add_properties({"identifier": ids})

    def set_field(self):
        field = self.dmp.get('research_filed')

        if field:
            self.rootdataentity.add_properties({'keywords': field})

    def set_creators(self):
        creators = self.dmp.get("creators")
        creator_list = []

        for creator in creators:
            ids = [item for item in [creator.get("orcid"), creator.get("url")] if item]
            if len(ids) == 0:
                raise ValidationError('Either property "orcid" or "url" is required for creators')

            properties = {
                "name": creator["name"],
                "email": creator["email"],
                "affiliation": creator["affiliation"]
            }

            erad = creator.get('e-Rad_researcher_number')
            if erad:
                properties["identifier"] = {"@id": f"#e-Rad:{erad}"}
                self.add_erad(erad, 'researcher')

            if len(ids) == 2:
                properties["sameAs"] = ids[1]

            self.add_entity(ids[0], 'Person', properties)
            creator_list.append({"@id": ids[0]})

        self.rootdataentity.add_properties({'creator': creator_list})

    def set_affiliations(self):
        affiliations = self.dmp.get("affiliations")

        for affiliation in affiliations:
            ids = [item for item in [affiliation.get("ror"), affiliation.get("url")] if item]
            if len(ids) == 0:
                raise ValidationError('Either property "ror" or "url" is required for affiliations')

            properties = {
                "name": affiliation["name"]
            }
            if len(ids) == 2:
                properties["sameAs"] = ids[1]

            self.add_entity(ids[0], 'Organization', properties)

    def overwrite(self):
        persons = self.get_by_type("Person")

        if len(persons) == 0:
            return

        for p in persons:
            aff = p.get("affiliation")
            if type(aff) is str:
                aff_e = self.get_by_name(aff)
                aff_id = aff_e.get('@id')
                p.add_properties({'affiliation': {"@id": aff_id}})
