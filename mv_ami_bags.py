import argparse
import logging
import re
from pathlib import Path
import subprocess

def _make_parser():
    parser = argparse.ArgumentParser(description='move AMI bags from a hard drive to ICA')
    parser.add_argument('--drive', '-d',
                        help = '''required. /Volumes/____''',
                        required=True)
    parser.add_argument('--destination', '-des',
                        help = '''required. Path to 0_waiting_for_preservica''',
                        required=False)
    return parser

def find_bag(drive_path):
    pattern = r"[0-9]{6}"
    bags = [b for b in drive_path.rglob("*") if b.is_dir() and re.fullmatch(pattern, b.name)]

    return bags

def main():
    parser = _make_parser()
    args = parser.parse_args()
    drive_p = Path(args.drive)
    bags_ls = find_bag(drive_p)

    for bag in bags_ls:
        ami_id = str(bag.name)
        destination_p = Path(args.destination) / ami_id[0:3] / ami_id
        if destination_p.is_dir():
            logging.error(f"{destination_p} exists. Did not rsync")
        else:
            cmd = ["rsync", "-arP", f"{bag}/", destination_p]
            print(cmd)
            proc = subprocess.run(cmd, capture_output=True)


if __name__ == "__main__":
    main()