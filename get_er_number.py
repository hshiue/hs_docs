import argparse
import logging
import re
import requests

def _make_parser():
    parser = argparse.ArgumentParser(description='get all ER number from NYPL Finding Aid')
    parser.add_argument('--collectionID', '-c',
                        help = '''required. number only, e.g. 18400 for M18400''',
                        required=True)

    return parser




def main():
    """
    Insert a collection ID number (only) to get all ER, coded in
    'local_mss_er'

    1. add to a list
    2. extract the number
    3. sort the list from small to large number
    4. check the number is subsequent
    5. give out the total number, which should equal the length of the list
    """

    parser = _make_parser()
    args = parser.parse_args()

    url = f"https://nyplorg-data-archives.s3.amazonaws.com/uploads/collection/generated_xml/mss{args.collectionID}.xml"

if __name__ == "__main__":
    main()