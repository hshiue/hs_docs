import argparse
import bagit
import logging
from pathlib import Path
import re

def _make_parser():
    parser = argparse.ArgumentParser(
                        description='''Compare AMI bags in two locations:
                        first, check the bag is really in both locations;
                        second, compare duplicated ones using their payload
                        manifest entries''')
    parser.add_argument('-d_dupe', '--directory_duplicate',
                        help = '''required. Directory one is the directory with
                        potential duplicated bags. It should be a path to a
                        directory of bags or a hard drive.''',
                        required=True)
    parser.add_argument('-d_main', '--directory_main',
                        help = f'''required. Directory two is the directory to
                        be compared against, supposedly having the authoritative
                        source. It should be a path to a directory of bags or a
                        hard drive.''',
                        required=True)

    return parser

def _configure_logging(args):
    fn = Path(args.directory_main).name

    logging.basicConfig(level=logging.WARNING,
                        format = "%(asctime)s - %(levelname)8s - %(message)s",
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=f'{fn}.log',
                        encoding='utf-8'
                        )

def validate_dir_paths(args) -> bool:
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

def find_bags_in_dir(dir: str) -> dict[str, Path]:
    path = Path(dir)
    bags_dict = dict()
    pattern = '^\d{6}$'

    if re.match(pattern, path.name): # this identifies single bag
        bags_dict[path.name] = path

    for p in path.rglob('*'): # this identifies a dir of bags
        if p.is_dir() and re.match(pattern, p.name):
            bags_dict[p.name] = p

    return bags_dict

def compare_bags_dicts(dict_d: dict, dict_m: dict) -> tuple[set, set, set]:
    keys_d = set(dict_d.keys())
    keys_m = set(dict_m.keys())

    only_in_d = keys_d - keys_m
    only_in_m = keys_m - keys_d
    real_dups = keys_d.intersection(keys_m)

    return only_in_d, only_in_m, real_dups

def validate_bag(bags_dict: dict, bag_id: str) -> bool:
    bag_path = bags_dict[bag_id]
    bag_to_validate = bagit.Bag(str(bag_path))

    try:
        # print(f'checking {bag_to_validate}')
        bag_to_validate.validate(completeness_only = True)
        return True
    except bagit.BagValidationError as e:
        logging.warning("Bag incomplete or invalid oxum: {0}".format(e.message))
        return False

def identify_duplication(bag_key, dir_d_dict, dir_m_dict):
    d_bag = bagit.Bag(str(dir_d_dict[bag_key]))
    m_bag = bagit.Bag(str(dir_m_dict[bag_key]))
    d_entries = d_bag.payload_entries()
    m_entries = m_bag.payload_entries()

    if d_entries == m_entries:
        return True

    else:
        d_fn_set = set(d_entries.keys())
        m_fn_set = set(m_entries.keys())

        if d_fn_set == m_fn_set:
            for fn in d_entries:
                if d_entries[fn] != m_entries[fn]: # same key, but different checksums
                    file_path = dir_m_dict[bag_key] / fn
                    logging.error(f'{file_path} is authoritative source file')

        else: # if the set of keys (filenames) are different, you need to look at it individually
            logging.error(f'There are different filenames for {bag_key}')

        return False

def main():
    parser = _make_parser()
    args = parser.parse_args()
    _configure_logging(args)

    if validate_dir_paths(args):
        bags_d_dict = find_bags_in_dir(args.directory_duplicate)
        bags_m_dict = find_bags_in_dir(args.directory_main)

        only_in_d, only_in_m, real_dups = compare_bags_dicts(bags_d_dict, bags_m_dict)

        invalid_main = []
        invalid_dup = []
        invalid_both = []
        identical_bags = []
        unidentical_bags = []

        for dup_id in real_dups:

            if validate_bag(bags_d_dict, dup_id) and validate_bag(bags_m_dict, dup_id):
                if identify_duplication(dup_id, bags_d_dict, bags_m_dict):
                    identical_bags.append(dup_id)
                else:
                    unidentical_bags.append(dup_id)
            elif validate_bag(bags_d_dict, dup_id) == False and validate_bag(bags_m_dict, dup_id) == False:
                invalid_both.append(dup_id)
            elif validate_bag(bags_d_dict, dup_id) == True and validate_bag(bags_m_dict, dup_id) == False:
                invalid_main.append(dup_id)
            else:
                invalid_dup.append(dup_id)

        logging.error(f'{only_in_d} ONLY in duplication directory')
        logging.error(f'{only_in_m} ONLY in main directory')

        print(f'''
        {len(only_in_d)} bags ONLY in duplication directory: {only_in_d};
        {len(only_in_m)} bags ONLY in main directory: {only_in_m}
        {len(real_dups)} bags in BOTH directories: {real_dups}

        Checked {len(real_dups)} duplicated bags: {real_dups}

        First check -- validate the bag in both directories:
            {len(invalid_both)} bags are invalid in both directories, review manually: {invalid_both}
            {len(invalid_main)} bags are invalid in the main directory, review manually: {invalid_main}
            {len(invalid_dup)} bags are invalid in the dup directory, review manually: {invalid_dup}''')

        print(f'''
        Second check -- for valid bags in both directories
        compare versions using payload manifests:
            {len(identical_bags)} bags are identical {identical_bags};

            {len(unidentical_bags)} bags are not identical: {unidentical_bags};
            check the log file in present directory''')

if __name__ == "__main__":
    main()