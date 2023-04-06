#!/usr/bin/env python3

import argparse
from pathlib import Path
import subprocess
import re
import json
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

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
    dir_p = Path(dir)
    if dir_p.is_dir():
        return True
    else:
        return False

def get_ami_dict(filepaths: list) -> dict:
    ami_dict = dict()
    expected = r'\d{6}'
    media_exts = ['.mp4', '.wav', '.flac']
    media_paths = [x for x in filepaths if x.suffix.lower() in media_exts]
    json_paths = [x for x in filepaths if x.suffix.lower() == '.json']

    for media_p in media_paths:
        filename = media_p.stem
        for json_p in json_paths:
            if json_p.stem == filename:
                id = re.search(expected, media_p.stem).group(0)
                if id:
                    ami_dict[id] = [media_p, json_p]

    return ami_dict

def validate_filename(filepath: Path) -> bool:
    fn_convention = r'(\w{3}_\d{6}_\w+_(sc|em))'
    match = re.fullmatch(fn_convention, filepath.stem)
    if match:
        return True
    else:
        return False

def validate_json_ref_filename(media_p: Path, json_p: Path) -> bool:
    with open(json_p, "r", encoding='utf-8-sig') as jsonFile:
        data = json.load(jsonFile)
        json_name = data['asset']['referenceFilename']
    if json_name == media_p.name:
        return True
    else:
        return False

def validate_json_barcode(json_p: Path) -> bool:
    with open(json_p, "r", encoding='utf-8-sig') as jsonFile:
        data = json.load(jsonFile)
        barcode = data['bibliographic']['barcode']
        match = re.match(r'33433', barcode)
        # re.match() matches the beginning of the string

    if match:
        return True
    else:
        return False

def absent_in_bucket(filepath: Path) -> list:
    absent = []
    check_cmd = ['aws', 's3api', 'head-object',
                '--bucket', 'ami-carnegie-servicecopies',
                '--key', '']
    if filepath.suffix.lower() == '.flac' or filepath.suffix.lower() == '.wav':
        check_cmd[-1] = filepath.name
        print(check_cmd)
        output_original_media = subprocess.run(check_cmd,
                                               capture_output=True).stdout
        if not output_original_media:
            mp4_key = filepath.name.replace('flac', 'mp4').replace('wav', 'mp4')
            check_cmd[-1] = mp4_key
            print(check_cmd)
            output_mp4 = subprocess.run(check_cmd, capture_output=True).stdout
            if not output_mp4:
                absent.append(filepath)
    if filepath.suffic.lower() == '.json':
        check_cmd[-1] = filepath.name
        print(check_cmd)
        output_json_mp4 = subprocess.run(cmd, capture_output=True).stdout
        if not output_json_mp4:
            absent.append(filepath)

    return absent

def main():
    '''
    1. get a directory of files V
    2. validate filename convention
    3. get the filename from the media and the AMI ID (stem) V
    4. check the media file has a corresponding json V
    5. validate json referenceFilename field
    6. validate json barcode field (starts with 33433)
    7. create a check_bucket function for check_only arg

    '''
    args = get_args()
    dir = args.directory

    if validate_dir(dir):
        all_filepaths = [x for x in Path(dir).iterdir() if x.is_file()]
        ami_dict = get_ami_dict(all_filepaths)

        for ami_key in ami_dict:
            if not len(ami_dict[ami_key]) == 2:
                LOGGER.error(f'{ami_key} does not have both media and json file')

            media_p, json_p = ami_dict[ami_key][0], ami_dict[ami_key][1]

            if (validate_filename(media_p) and
                validate_filename(json_p) and
                validate_json_ref_filename(media_p, json_p) and
                validate_json_barcode(json_p)):












if __name__ == '__main__':
    main()