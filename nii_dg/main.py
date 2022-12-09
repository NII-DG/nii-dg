import json
import sys
from nii_dg.generate import add_entities_to_crate, read_dmp, generate_crate_instance, ValidationError
from nii_dg import const


def generate_rocrate(dmp_path, dir_path=None):
    try:
        crate = generate_crate_instance( read_dmp(dmp_path) )
        add_entities_to_crate(crate)

        if dir_path is None:
            crate.set_data()
        else:
            crate.load_data_dir(dir_path)

        roc = crate.generate()
        with open(const.BASENAME, 'w', encoding="utf-8") as f:
            json.dump(roc, f, indent=4)

        sys.exit(0)

    except (FileNotFoundError, ValidationError) as e:
        print(type(e).__name__ + ' occured!: ' + str(e))
        sys.exit(1)


if __name__ == "__main__":
    generate_rocrate(sys.argv[0], sys.argv[1])