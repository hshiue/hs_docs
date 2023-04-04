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

def get_media_and_json_filepaths(dir: Path) -> tuple:
    media_ext = ['.mp4', '.wav', '.flac']
    media_fps = [x for x in dir.iterdir() if x.suffix.lower() in media_ext]
    json_fps = [x for x in dir.iterdir() if x.suffix.lower() == '.json']

    return media_fps, json_fps

def main():
    '''
    1. get a directory of files
    2. validate filename convention
    3. get the filename from the media and the AMI ID
    4. check the media file has a corresponding json (set comparison)
    5. validate json referenceFilename field
    6. validate json barcode field (starts with 33433)
    7. create a check_bucket function for check_only arg

    '''
    args = get_args()
    if validate_dir(args.directory):
        media_filepaths, json_filepaths = get_media_and_json_filepaths(args.directory)



if __name__ == '__main__':
    main()