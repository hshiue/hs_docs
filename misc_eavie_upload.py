#!/usr/bin/env python3

import argparse
from pathlib import Path
import subprocess
import re
import json
import warnings

def get_args():
    parser = argparse.ArgumentParser(description='''Upload access copies and JSON
                                     directly from a folder to EAVie. Perform
                                     necessary checks before upload. Or use the
                                     check_only arg to check if the files are
                                     on EAVie''')
    parser.add_argument('-d', '--directory',
                        help = '''required. A path to directory of access files
                        and corresponding JSONs''',
                        required=True)
    parser.add_argument('-c', '--check_only',
                        action='store_true',
                        help = f'''check if all files from the directory
                        are in the AWS bucket; check if there is any filename or
                        metadata mismatch; print out check result on the terminal''')
    parser.add_argument('--check_and_upload',
                        action='store_true',
                        help=f'''check if all files from the directory
                        are in the AWS bucket; check if there is any filename or
                        metadata mismatch;and upload ONLY the valid ones not in
                        the AWS bucket''')
    args = parser.parse_args()
    return args

def validate_dir(dir: Path) -> bool:
    if dir.is_dir():
        return True
    else:
        return False

def validate_filename(filepaths: list) -> bool:
    fn_convention = r'(\w{3}_\d{6}_\w+_(sc|em))'
    for fp in filepaths:
        match = re.fullmatch(fn_convention, fp.stem)
        if match:
            return True
        else:
            return False

def main():
    '''
    1. get a directory of files
    2. validate filename convention
    3. get the filename from the media and the AMI ID (stem)
    4. check the media file has a corresponding json (set comparison)
    5. validate json referenceFilename field
    6. validate json barcode field (starts with 33433)
    7. create a check_bucket function for check_only arg

    '''
    args = get_args()
    dir = args.directory

    if validate_dir(dir):
        all_filepaths = [x for x in dir.iterdir() if x.is_file()]





if __name__ == '__main__':
    main()