import argparse
import bagit
import logging
from pathlib import Path
import re
import pprint as pp

def _make_parser():
    parser = argparse.ArgumentParser(description='''Compare AMI bags in two locations
                                     using their payload manifest entries''')
    parser.add_argument('-d_dupe', '--directory_duplicate',
                        help = '''required. Directory one is the directory with potential
                        duplicated bags. It should be a path to a directory of bags or a hard drive.''',
                        required=True)
    parser.add_argument('-d_main', '--directory_main',
                        help = f'''required. Directory two is the directory to be compared against,
                        supposedly having the authoritative source.
                        It should be a path to a directory of bags or a hard drive.''',
                        required=True)

    return parser

def validate_dir_paths(args):
    path_dup = Path(args.directory_duplicate)
    path_main = Path(args.directory_main)

    if not path_dup.is_dir() and not path_main.is_dir():
        logging.error('Both directories are invalid')
    elif not path_dup.is_dir():
        logging.error('Please try with a valid duplicate directory')
        return False
    elif not path_main.is_dir():
        logging.error('Please try with a valid main directory')
        return False
    else:
        return True

def find_bags_in_dupe_dir(args):
    path_dup = Path(args.directory_duplicate)
    bag_paths = []
    bag_ids = []
    pattern = '^\d{6}$'

    for p in path_dup.rglob('*'):
        if p.is_dir() and re.match(pattern, p.name):
            bag_paths.append(p)
            bag_ids.append(p.name)

    return bag_paths, bag_ids

def check_dupe_status_in_main(args, bag_ids):
    path_main = Path(args.directory_main)

    bags_not_in_main = []
    bags_to_validate = []

    for b in bag_ids:
        bag_path = [x for x in path_main.rglob(b) if x.is_dir()]
        if not bag_path:
            bags_not_in_main.append(b)
        else:
            bags_to_validate.append(bag_path[0])

    return bags_not_in_main, bags_to_validate

def validate_bags_in_main(bags_to_validate):
    valid_in_main = dict()
    invalid_in_main = []

    for bag_path in bags_to_validate:
        bag_in_main = bagit.Bag(str(bag_path))
        try:
            print(f'checking {bag_in_main}')
            bag_in_main.validate(completeness_only = True)
            valid_in_main[bag_path.name] = bag_in_main
        except bagit.BagValidationError as e:
            logging.warning("Bag incomplete or invalid oxum: {0}".format(e.message))
            invalid_in_main.append(bag_path.name)

    return valid_in_main, invalid_in_main

def compare_payload_manifests(valid_in_main, bag_paths):
    dup_missing_file = dict()
    unequal_hash = dict()
    identical_bag = []

    for bag_key in valid_in_main:
        main_entries = valid_in_main[bag_key].payload_entries()

        for i in [x for x in bag_paths if x.name == bag_key]:
            dup_bag = bagit.Bag(str(i))

        dup_entries = dup_bag.payload_entries()

        counter = 0
        for e in main_entries:
            if not e in dup_entries:
                if not bag_key in dup_missing_file:
                    dup_missing_file[bag_key] = []
                dup_missing_file[bag_key].append(e)
                counter += 1
            elif not main_entries[e] == dup_entries[e]:
                if not bag_key in unequal_hash:
                    unequal_hash[bag_key] = []
                unequal_hash[bag_key].append(e)
                counter += 1
        if counter == 0:
            identical_bag.append(bag_key)


    return dup_missing_file, unequal_hash, identical_bag

def main():
    parser = _make_parser()
    args = parser.parse_args()
    if validate_dir_paths(args):
        bag_paths, bag_ids = find_bags_in_dupe_dir(args)
        print(f'''{bag_ids}, {len(bag_ids)} will be checked in the main directory''')

        bags_not_in_main, bags_to_validate = check_dupe_status_in_main(args, bag_ids)
        valid_main, invalid_main = validate_bags_in_main(bags_to_validate)
        dup_missing_file, unequal_hash, identical = compare_payload_manifests(valid_main, bag_paths)

        print(f'''
        Checked {len(bag_ids)} bags: {bag_ids}

        {len(bags_not_in_main)} bags are not duplication, not in the main directory: {bags_not_in_main}
        {len(bags_to_validate)} bags are potentially duplicated: {[b.name for b in bags_to_validate]}
        First check -- validate the bag in main:
            {len(invalid_main)} bags are invalid in the main directory, review manually: {invalid_main}''')

        print(f'''
        Second check -- compare versions using payload manifests:
            {len(valid_main)} are valid in main: {valid_main.keys()}
            Duplicate location is missing these file(s) {pp.pformat(dup_missing_file)}
            These hashes are different in the two location {pp.pformat(unequal_hash)}
            These bags are identical {identical}''')

if __name__ == "__main__":
    main()