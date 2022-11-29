import os

from nii_dg.model.entities import (ContextEntity, DataEntity, Metadata,
                             RootDataEntity)

FREEACCESS = {"free":"true", "consideration":"false"}

def get_dir_size(path:str) -> int:
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total

class ValidationError(Exception):
    pass


class ROCrate():

    def __init__(self) -> None:
        self.metadata = Metadata()
        self.rootdataentity = RootDataEntity()
        self.entities = [self.metadata, self.rootdataentity]
        self.data_entities = []

    def get_by_type(self, e_type:str):
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

    def get_by_id(self, e_id):
        for e in self.entities:
            if e.get("@id") == e_id:
                return e
        return None

    def add_entity(self, id, e_type, properties) ->None:
        e = ContextEntity(id, e_type)
        e.add_properties(properties)
        self.entities.append(e)

    def add_dataentity(self, id, e_type, properties) ->None:
        e = DataEntity(id, e_type)
        e.add_properties(properties)
        self.data_entities.append(e)

    def update_entity(self, entity, properties) ->None:
        entity.add_properties(properties)

    def generate(self):
        graph = []
        for entity in self.entities:
            graph.append(entity.get_jsonld())
        context = f'{self.metadata.PROFILE}/context'
        if self.data_entities:
            for entity in self.data_entities:
                graph.append(entity.get_jsonld())
        if self.extra_terms:
            context = [context, self.extra_terms]
        return {'@context': context, '@graph': graph}


class NIIROCrate(ROCrate):
    EXTRA_TERMS = {
        "accessRights": "http://purl.org/dc/terms/accessRights",
        "dmpFormat": "https://example.com/dmpFormat",  # to be updated
        "dmpDataNumber": "https://example.com/dataManagementPlan"  # to be updated
    }

    def __init__(self, dmp, dmpf):
        super().__init__()
        self.extra_terms = self.EXTRA_TERMS
        self.dmp = dmp
        self.update_entity(self.rootdataentity,{"dmpFormat":dmpf})

    def convert_name_to_id(self, namedict):
        e = self.get_by_name(namedict["name"])
        e_id = e.get("@id")
        return {"@id" : e_id} 

    def add_entity_by_url(self, dict_, type_):
        id_ = dict_.get('url')
        if id_ is None:
            raise ValidationError('property "url" is missing.')
        properties = {k: v for k, v in dict_.items() if v != id_}
        
        if self.get_by_id(id_):
            self.get_by_id(id_).add_properties(properties)
        else:
            self.add_entity(id_, type_, properties)
        return {"@id":id_}

    def load_data_dir(self, data_dir):
        file_list = []

        if data_dir is None:
            return

        for root, dirs, files in os.walk(data_dir, topdown=False):

            for f in files:
                if f == 'ro-crate-metadata.json':
                    continue
                f_path = os.path.join(root, f)
                abs_path = f_path.replace(data_dir +'/', '')
                self.add_dataentity(abs_path, 'File', 
                {"name":f, "fileSize": str(os.path.getsize(f_path))+'B'})
                file_list.append({"@id": abs_path})
                
            for dir in dirs:
                d_path = os.path.join(root, dir)
                abs_path = d_path.replace(data_dir, '') + '/'
                self.add_dataentity(abs_path, 'Dataset', 
                {"name":dir,"fileSize": str(get_dir_size(d_path)) +'B'})
                file_list.append({"@id": abs_path})        

        self.rootdataentity.add_properties({'hasPart': file_list})

    def set_publisheddate(self):
        pd = self.dmp.get("published_date")
        cd = self.rootdataentity.get("datePublished")
        self.update_entity(self.rootdataentity,{"dateCreated":cd})

        if pd:
            self.update_entity(self.rootdataentity,{"datePublished":cd})

    def set_project_name(self):
        self.rootdataentity._jsonld["name"] = self.dmp["project_name"]

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

    def set_repo(self):
        repo = self.dmp.get("repository")

        id_ = self.add_entity_by_url(repo, "RepositoryObject")

        ids = self.rootdataentity.get("identifier")
        if ids is None:
            ids = []
        ids.append(id_)
        self.rootdataentity.add_properties({"identifier": ids})


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
        field = self.dmp.get('research_fieled')

        if field:
            self.rootdataentity.add_properties({'keywords': field})

    def set_creators(self):
        creators = self.dmp.get("creator")
        creator_list = []

        for creator in creators:
            ids = [item for item in [creator.get("orcid"), creator.get("url")] if item]
            if len(ids) == 0:
                raise ValidationError('Either property "orcid" or "url" is required for creators')
            aff_name = creator["affiliation"].get("name")
            try:
                aff_e = self.get_by_name(aff_name)
                aff_id = aff_e.get("@id")
                aff_name = {"@id":aff_id}
            except ValidationError:
                pass

            em = creator["email"]
            properties = {
                "name": creator["name"],
                "email": em,
                "affiliation": aff_name
            }

            if creator.get("phone_number"):
                contact ={
                    "email": em,
                    "telephone":creator["phone_number"]
                }
                self.add_entity(f"#mailto:{em}","ContactPoint", contact)
                properties["contactPoint"] = {"@id":f"#mailto:{em}"}

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
        affiliations = self.dmp.get("affiliation")

        for affiliation in affiliations:
            try:
                aff_name = affiliation.get("name")
                aff_e = self.get_by_name(aff_name)
                properties = {k: v for k, v in affiliation.items() if v != affiliation["@id"]}
                self.update_entity(aff_e, properties)
            except Exception:
                ids = [item for item in [affiliation.get("ror"), affiliation.get("url")] if item]
                if len(ids) == 0:
                    raise ValidationError('Either property "ror" or "url" is required for affiliation')

                properties = {k: v for k, v in affiliation.items() if v != ids[0]}
                if len(ids) == 2:
                    properties.pop("url")
                    properties["sameAs"] = ids[1]

                self.add_entity(ids[0], 'Organization', properties)
    
    def set_license(self):
        license_ = self.dmp.get("license")
        id_ = self.add_entity_by_url(license_, "CreativeWork")

        self.rootdataentity.add_properties({'license': id_})

    def set_dmplist(self):
        if self.dmp.get("repository").get("name") == 'Gakunin RDM':
            self.set_grdm()
        else:
            pass
    
    def set_grdm(self):
        dmpset = self.dmp.get("dataset")
        i = 1

        for dmp in dmpset:
            id_ = "#dmp:" + str(dmp.get("data_number"))
            maintainer = []

            properties = {
                "name":dmp.get("title"),
                "description":dmp.get("description"),
                "contentSize":dmp.get("max_filesize")
            }

            creators = dmp.get('creator')
            if creators:
                c_list = []
                for creator in creators:
                    c_id = self.convert_name_to_id(creator)
                    c_list.append(c_id)
                properties["creator"] = c_list

            if dmp.get("hosting_institution"):
                hi = self.convert_name_to_id(dmp["hosting_institution"])
                maintainer.append(hi)
            if dmp.get("data_manager"):
                dm = self.convert_name_to_id(dmp["data_manager"])
                maintainer.append(dm)

                dm_e = self.get_by_name(dmp["data_manager"].get("name"))
                cp = dm_e.get("contactPoint")
                if cp is None:
                    em = dm_e.get("email")
                    self.add_entity(f"#mailto:{em}","ContactPoint", {"email":em})
                    cp = {"@id": f"#mailto:{em}"}
                properties["contactPoint"] = cp

            if len(maintainer) > 0:
                properties["maintainer"] = maintainer

            iaf = dmp.get("free_or_consideration")
            if iaf:
                properties["isAccessibleForFree"] = FREEACCESS.get(iaf)

            if dmp.get("license"):
                try:
                    lic = self.convert_name_to_id(dmp["license"])
                except Exception:
                    lic = self.add_entity_by_url(dmp["license"], "CreativeWork")

                properties["license"] = lic

            if dmp.get("access_rights"):
                properties["accessRights"] = dmp.get("access_rights")

            ui = dmp.get("citation_info")
            if ui:
                self.add_entity(f"#usageInfo:{i}", "CreativeWork", {"description":ui})
                properties["usageInfo"] = {"@id":f"#usageInfo:{i}"},
                i += 1

            self.add_entity(id_, "CreativeWork", properties)

            filepath = dmp.get("url")
            if filepath.find('/dir/osfstorage') > 0:
                dir = filepath[filepath.find('osfstorage')+11:]
                data_properties = {
                    "name":dir[:-1],
                    "contentSize":dmp.get("size"),
                    "dmpDataNumber":{"@id":id_}
                }
                self.add_entity(dir, "Dataset", data_properties)

                if self.rootdataentity.get('hasPart'):
                    self.rootdataentity.get('hasPart').append({"@id":dir})
                else:
                    haspart = []
                    haspart.append({"@id":dir})
                    self.rootdataentity.add_properties({"hasPart":haspart})

    def overwrite(self):
        persons = self.get_by_type("Person")

        if len(persons) == 0:
            return

        for p in persons:
            aff = p.get("affiliation")
            if type(aff) is str:
                aff_e = self.get_by_name(aff)
                if aff_e is None:
                    raise ValidationError(f'affiliation {aff} input is not found')
                aff_id = aff_e.get('@id')
                p.add_properties({'affiliation': {"@id": aff_id}})
