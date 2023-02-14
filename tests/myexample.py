import ast

from nii_dg.entity import Entity
from nii_dg.error import EntityError, GovernanceError, PropsError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import (ContactPoint, Dataset, Organization, Person,
                                RootDataEntity)
from nii_dg.schema.ginfork import File, GinMonitoring
from nii_dg.utils import check_required_props, load_entity_def_from_schema_file

# from nii_dg.schema.ginfork import File as GinFile
# from nii_dg.schema.ginfork import GinMonitoring


def main() -> None:
    p = Person(id="invalid_url", props={"invalid_key": "invalid_value"})
    p.check_props()


if __name__ == "__main__":
    main()
