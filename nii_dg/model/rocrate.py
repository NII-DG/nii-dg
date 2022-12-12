import os
from typing import Optional
from nii_dg.model.entities import (Entity, Metadata, RootDataEntity)
from nii_dg import const


def get_dir_size(path:str) -> int:
    '''
    ディレクトリに含まれるファイルサイズの合計を算出する
    '''
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
    '''
    基底クラス
    '''
    def __init__(self) -> None:
        self.metadata = Metadata()
        self.rootdataentity = RootDataEntity()
        self.entities = [self.metadata, self.rootdataentity]
        self.extra_terms = None

    def get_by_type(self, e_type:str) -> list:
        '''
        @typeが引数に一致するエンティティをリストで返す
        '''
        ents = []
        for e in self.entities:
            if e.get("@type") == e_type:
                ents.append(e)
        return ents

    def get_by_name(self, e_name:str) -> Optional[Entity]:
        '''
        nameが引数に一致するエンティティを返す
        各エンティティでnameはユニークになる前提
        '''
        for e in self.entities:
            if e.get("name") == e_name:
                return e
        return None

    def get_by_id(self, e_id:str) -> Optional[Entity]:
        '''
        @idが引数に一致するエンティティを返す
        各エンティティでpidはユニークになる前提
        '''
        for e in self.entities:
            if e.get("@id") == e_id:
                return e
        return None

    def convert_name_to_id(self, namedict:dict) -> Optional[dict]:
        '''
        {name: xxx} の辞書を引数として、nameが一致するエンティティが存在する時
        そのエンティティの@idを辞書で返す
        '''
        name = namedict.get("name")
        if name is None:
            raise TypeError("key 'name' is not found in the dictionary")

        e = self.get_by_name(name)
        if e is None:
            return None
        return e.get_id_dict()

    def add_entity(self, id_:str, e_type:str, properties:dict) -> dict:
        '''
        @idが一致するエンティティが存在しない場合、エンティティを新規作成
        存在する場合はプロパティを更新
        いずれも該当するエンティティの@id key-valueを辞書で返す
        '''
        if self.get_by_id(id_) is None:
            e = Entity(id_, e_type)
            self.entities.append(e)
        else:
            e = self.get_by_id(id_)

        e.add_properties(properties)
        return e.get_id_dict()

    def add_entity_by_name(self, e_type:str, properties:dict) -> dict:
        '''
        nameが一致するエンティティが存在しない場合、エンティティを新規作成
        存在する場合はプロパティを更新
        いずれも該当するエンティティの@id key-valueを辞書で返す
        '''
        name = properties.get("name")
        if name is None:
            raise ValidationError('key "name" is required.')
        if self.get_by_name(name) is None:
            e = Entity('#' + name, e_type)
            self.entities.append(e)
        else:
            e = self.get_by_name(name)

        e.add_properties(properties)
        return e.get_id_dict()

    def generate(self) -> dict:
        '''
        各エンティティからRO-Crate形式のJSON-LDを作成
        '''
        graph = []
        for entity in self.entities:
            graph.append(entity.get_jsonld())
        context = f'{const.PROFILE}/context'
        if self.extra_terms is not None:
            context = [context, self.extra_terms]
        return {'@context': context, '@graph': graph}


class NIIROCrate(ROCrate):
    '''
    RO-Crateクラスを拡張しNII標準独自のメソッド・インスタンス変数を追加
    '''

    def __init__(self, dmp:str):
        super().__init__()
        self.extra_terms = const.EXTRA_TERMS
        self.dmp = dmp
        self.dmp_format = dmp.get("dmpFormat")
        self.rootdataentity.add_properties({"dmpFormat":self.dmp_format})


    def add_entity_by_url(self, dict_:dict, type_:str) -> dict:
        '''
        url キーを含む辞書から、urlのvalueを@idとしてエンティティ作成
        '''

        id_ = dict_.get('url')
        if id_ is None:
            raise ValidationError('key "url" is not found.')
        properties = {k: v for k, v in dict_.items() if v != id_}
        
        return self.add_entity(id_, type_, properties)


    def add_erad(self, erad:str, erad_type:str) -> dict:
        '''
        e-Rad番号のエンティティを追加
        プロジェクトIDか研究者番号かを引数で指定
        '''
        properties = {'value': erad}

        if erad_type == 'project':
            properties["name"] = 'e-Rad Project ID'
        elif erad_type == 'researcher':
            properties["name"] = 'e-Rad researcher number'
        else:
            raise ValidationError('e-rad type should be "project" or "researcher".')

        return self.add_entity(f'#e-Rad:{erad}', 'PropertyValue', properties)


    def add_contactpoint(self, cp:dict) -> dict:
        '''
        ContactPointエンティティを作成する
        IDはemail valueから生成
        '''

        properties = {k: v for k, v in cp.items() if k in ["email", "telephone","contactType"]}
        em = properties["email"]
        return self.add_entity(f"#mailto:{em}","ContactPoint", properties)


    def add_organization(self, org:dict) -> dict:
        '''
        Organizationエンティティを作成する
        @idはrorもしくはurlのvalueとし、両方ある場合はrorを優先
        '''

        # when "ror" is missing, "url" is adopted as @id property
        ids = [item for item in [org.get("ror"), org.get("url")] if item is not None]
        if len(ids) == 0:
            raise ValidationError('Either property "ror" or "url" is required for organization entity')

        properties = {k: v for k, v in org.items() if v != ids[0]}
        if len(ids) == 2:
            properties.pop("url")
            properties["sameAs"] = ids[1]

        return self.add_entity(ids[0], 'Organization', properties)


    def add_person(self, person:dict) -> dict:
        '''
        Personエンティティを作成する
        @idはorcidもしくはurlのvalueとし、rorを優先
        '''

        properties = {k: v for k, v in person.items() if k in ["name","description","email","jobTitle"]}

        # when "orcid" is missing, "url" is adopted as @id property
        ids = [item for item in [person.get("orcid"), person.get("url")] if item is not None]
        if len(ids) == 0:
            raise ValidationError('Either property "orcid" or "url" is required for person entity')
        if len(ids) == 2:
            properties["sameAs"] = ids[1]

        # add affiliation entity
        affiliation = person.get("affiliation")
        if self.get_by_name(affiliation.get("name")) is None:
            properties["affiliation"] = self.add_organization(affiliation)
        else:
            properties["affiliation"] = self.add_entity_by_name("Organization",affiliation)

        # when there is "telephone", add ContactPoint entity
        if person.get("telephone") is not None:
            properties["contactPoint"] = self.add_contactpoint(person)

        # when there is e-rad ID, add an entity
        erad = person.get('e-RadResearcherNumber')
        if erad is not None:
            properties["identifier"] = self.add_erad(erad, 'researcher')

        return self.add_entity(ids[0], 'Person', properties)


    def load_data_dir(self, data_dir:str):
        '''
        ローカルのディレクトリを読み、データエンティティを作成
        '''

        file_list = []

        if data_dir is None:
            return

        for root, dirs, files in os.walk(data_dir, topdown=False):

            for file in files:
                if file == 'ro-crate-metadata.json':
                    continue
                f_path = os.path.join(root, file)
                abs_path = f_path.replace(data_dir +'/', '')
                self.add_entity(abs_path, 'File',
                {"name":file, "fileSize": str(os.path.getsize(f_path))+'B'})
                file_list.append({"@id": abs_path})

            for dir_ in dirs:
                d_path = os.path.join(root, dir_)
                abs_path = d_path.replace(data_dir, '') + '/'
                self.add_entity(abs_path, 'Dataset',
                {"name":dir_,"fileSize": str(get_dir_size(d_path)) +'B'})
                file_list.append({"@id": abs_path})

        self.rootdataentity.add_properties({'hasPart': file_list})


    def set_publisheddate(self) -> None:
        '''
        publishedDate プロパティをルートエンティティに追加
        '''
        pd = self.dmp.get("publishedDate")
        cd = self.rootdataentity.get("datePublished")
        self.rootdataentity.add_properties({"dateCreated":cd})

        if pd is not None:
            self.rootdataentity.add_properties({"datePublished":cd})

    def set_project_name(self, name:str) -> None:
        '''
        name プロパティをルートエンティティに追加
        '''
        self.rootdataentity.set_name(name)

    def set_funder(self, funders:list) -> None:
        '''
        funder プロパティをルートエンティティに追加
        '''
        funder_list = []

        for fa in funders:
            fa_id = self.add_organization(fa)
            funder_list.append(fa_id)

        self.rootdataentity.add_properties({'funder': funder_list})

    def set_repo(self, repository:dict) -> None:
        '''
        リポジトリURLをルートエンティティにidentifierとして追加
        '''
        id_ = self.add_entity_by_url(repository, "RepositoryObject")

        ids = self.rootdataentity.get("identifier")
        if ids is None:
            ids = []
        ids.append(id_)
        self.rootdataentity.add_properties({"identifier": ids})


    def set_erad(self, erad) -> None:
        '''
        e-Rad project プロジェクトIDをルートエンティティにidentifierとして追加
        '''
        erad_id = self.add_erad(erad, 'project')

        ids = self.rootdataentity.get("identifier")
        if ids is None:
            ids = []
        ids.append(erad_id)
        self.rootdataentity.add_properties({"identifier": ids})


    def set_field(self, field:str) -> None:
        '''
        研究分野をルートエンティティにkeywordsとして追加
        '''
        self.rootdataentity.add_properties({'keywords': field})


    def set_creators(self, creators:list) -> None:
        '''
        creatorをルートエンティティに追加
        '''
        creator_list = []

        for creator in creators:
            if self.get_by_name(creator["name"]) is None:
                id_ = self.add_person(creator)
                creator_list.append(id_)

        self.rootdataentity.add_properties({'creator': creator_list})

    def set_affiliations(self, affiliations:list) -> None:
        '''
        Add "affiliation" entity
        '''

        for affiliation in affiliations:
            aff_e = self.get_by_name(affiliation["name"])
            if aff_e is None:
                self.add_organization(affiliation)
            else:
                properties = {k: v for k, v in affiliation.items() if k not in ["ror", "url"]}
                aff_e.add_properties(properties)


    def set_license(self, license_:dict, entity: Entity = None) -> None:
        '''
        ライセンスのエンティティを追加
        '''
        if entity is None:
            entity = self.rootdataentity

        license_id = self.add_entity_by_url(license_, "CreativeWork")
        entity.add_properties({'license': license_id})


    def set_dmp_common(self) -> None:
        '''
        DMPの内容を番号ごとにエンティティとして追加: common metadata形式
        '''
        dmpset = self.dmp.get("dmp")
        i = 1

        for dmp in dmpset:
            id_ = "#dmp:" + str(dmp.get("dataNumber"))
            maintainer = []

            properties = {
                "name":dmp.get("title"),
                "description":dmp.get("description"),
                "contentSize":dmp.get("maxFilesize")
            }

            if dmp.get('creator') is not None:
                c_list = []
                for creator in dmp.get('creator'):
                    if self.get_by_name(creator["name"]):
                        c_id = self.get_by_name(creator["name"]).get_id_dict()
                    else:
                        c_id = self.add_person(creator)
                    c_list.append(c_id)
                properties["creator"] = c_list

            if dmp.get("hosting_institution") is not None:
                hi = self.convert_name_to_id(dmp["hostingInstitution"])
                maintainer.append(hi)
            if dmp.get("data_manager") is not None:
                dm = self.convert_name_to_id(dmp["dataManager"])
                maintainer.append(dm)

                dm_e = self.get_by_name(dmp["dataManager"].get("name"))
                cp = dm_e.get("contactPoint")
                if cp is None:
                    cp = self.add_contactpoint(dm_e.get_jsonld())
                    dm_e.add_properties({"contactPoint":cp})
                properties["contactPoint"] = cp

            if len(maintainer) > 0:
                properties["maintainer"] = maintainer

            iaf = dmp.get("freeOrConsideration")
            if iaf is not None:
                properties["isAccessibleForFree"] = const.FREEACCESS.get(iaf)

            if dmp.get("license") is not None:
                lic = self.convert_name_to_id(dmp["license"])
                if lic is None:
                    lic = self.add_entity_by_url(dmp["license"], "CreativeWork")

                properties["license"] = lic

            if dmp.get("accessRights") is not None:
                properties["accessRights"] = dmp.get("accessRights")

            ui = dmp.get("citationInfo")
            if ui is not None:
                properties["usageInfo"] = self.add_entity(f"#usageInfo:{i}", "CreativeWork", {"description":ui})
                i += 1

            self.add_entity(id_, "CreativeWork", properties)


    def set_data(self, datalist:list = None) -> None:
        '''
        JSON内のディレクトリ・ファイル情報をデータエンティティとして追加
        '''

        if datalist is None:
            datalist = self.dmp.get("dataset")

        if self.rootdataentity.get('hasPart') is None:
            self.rootdataentity.add_properties({"hasPart":[]})

        for data in datalist:
            properties = {k: v for k, v in data.items() if k in ["name", "url"]}
            properties["contentSize"] = data.get("size")

            dmp_id = "#dmp:" + str(data.get("dmp"))
            dmp_id_dict = self.get_by_id(dmp_id).get_id_dict()
            if dmp_id_dict is None:
                raise ValidationError(f'The given dmp data number {dmp_id} is not found.')
            properties["dmpDataNumber"] = dmp_id_dict

            id_ = data.get("path")
            if id_.endswith("/"):
                data_id = self.add_entity(id_, "Dataset", properties)
            else:
                if data.get("format") is not None:
                    properties["encodingFormat"] = data.get("format")
                data_id = self.add_entity(id_, "File", properties)
        
            self.rootdataentity.get('hasPart').append(data_id)