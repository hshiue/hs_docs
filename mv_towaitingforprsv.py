import argparse
import logging
from pathlib import Path
import re
import subprocess

def _make_parser():
    parser = argparse.ArgumentParser(description='Move AMI bags from one directory to 0_waiting_for_preservica')
    parser.add_argument('-o', '--origin',
                        help = '''required. The original directory that contains the AMI bag''',
                        required=True)
    parser.add_argument('-d', '--destination',
                        help = '''required. The direct path to 0_waiting_for_preservica''',
                        required=True)
    return parser

def find_bags(ori_path: str) -> dict:
    bag_dict = dict()
    basepath = Path(ori_path) # /Volumes/parking/lpa/1_prestaging/2023-06-07
    for pjpath in basepath.iterdir():
        for ami_bag in pjpath.iterdir():
            bag_dict[ami_bag.name] = []
            bag_dict[ami_bag.name].append(ami_bag)

    return bag_dict

def add_dest_to_dict(bag_dict, dest_dir) -> str:
    basetarget = Path(dest_dir) # /Volumes/parking/lpa/0_waiting_for_preservica
    for id in bag_dict:
        first_three = id[0:3]
        dest_path = basetarget / first_three / id
        bag_dict[id].append(dest_path)

    return bag_dict








def main():
    parser = _make_parser()
    args = parser.parse_args()

    bag_dict = find_bags(args.origin)
    updated_bag_dict = add_dest_to_dict(bag_dict, args.destination)



if __name__ == "__main__":
    main()
