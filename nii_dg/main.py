import json
from nii_dg.generate import add_entities_to_crate, read_dmp, set_dmp_format


def generate_rocrate(dmp_path=None, dir_path=None):
    try:
        metadata = read_dmp(dmp_path)
        crate = set_dmp_format(metadata)

        add_entities_to_crate(crate)

        if dir_path is None:
            crate.load_data_dir(dir_path)

        roc = crate.generate()

        with open('ro-crate-metadata.json', 'w') as f:
            json.dump(roc, f, indent=4)
    except Exception as e:
        print('Error occured!: ' + e)


if __name__ == "__main__":
    generate_rocrate()