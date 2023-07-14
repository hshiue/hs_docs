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
    return parser

def find_bags(dir_path: str) -> dict:
    bag_dict = dict()
    basepath = Path(dir_path) # /Volumes/parking/lpa/1_prestaging/2023-06-07
    for pjpath in basepath.iterdir():
        for ami_bag in pjpath.iterdir():
            bag_dict[ami_bag.name] = ami_bag

    return bag_dict








def main():
    parser = _make_parser()
    args = parser.parse_args()

    bag_dict = find_bags(args.origin)



if __name__ == "__main__":
    main()
