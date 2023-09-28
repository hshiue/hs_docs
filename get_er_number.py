import argparse
import logging
import re
import requests
import xml.etree.ElementTree as ET

def _make_parser():
    parser = argparse.ArgumentParser(description='get all ER number from NYPL Finding Aid')
    parser.add_argument('--collectionID', '-c',
                        help = '''required. number only, e.g. 18400 for M18400''',
                        required=True)

    parser.add_argument('--find_dups', '-fd',
                        help="finding duplicates in the er, di and em list",
                        required=False,
                        action='store_true')

    return parser

def parse_xml_response(response):
    root = ET.fromstring(response.text)
    ns = f"{{urn:isbn:1-931666-22-9}}"

    er_no_ls = list()
    di_no_ls = list()
    em_no_ls = list()

    for i in root.iter(f"{ns}unitid"):
        if i.attrib["type"] == "local_mss_er":
            if "er" in i.text:
                er_no = re.search("\d+", i.text).group(0)
                er_no_ls.append(int(er_no))
            elif "di" in i.text:
                di_no = re.search("\d+", i.text).group(0)
                di_no_ls.append(int(di_no))
            elif "em" in i.text:
                em_no = re.search("\d+", i.text).group(0)
                em_no_ls.append(int(em_no))
            else:
                logging.info(f"the field does not include er, di or em str")
                er_no = re.search("\d+", i.text).group(0)
                er_no_ls.append(int(er_no))

    return er_no_ls, di_no_ls, em_no_ls

def check_consecutive(ls_no) -> bool:
    return sorted(ls_no) == list(range(min(ls_no), max(ls_no)+1))

def find_dups(ls) -> set:
    dups = {x for x in ls if ls.count(x) > 1}

    return dups





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
    response = requests.request("Get", url)
    er_no, di_no, em_no = parse_xml_response(response)
    if er_no and check_consecutive(er_no):
        print(f"""Total er: {len(er_no)}
                  numbers are consecutive""")
    elif not er_no:
        print(f"""no ERs in M{args.collectionID}""")
    else:
        print(f"""ER are not consecutive. Review list manually
              Total er: {len(er_no)}; largest er number: {er_no[-1]}""")

    if di_no and check_consecutive(di_no):
        print(f"""Total er: {len(di_no)}
                  numbers are consecutive""")
    elif not di_no:
        print(f"""no DIs in M{args.collectionID}""")
    else:
        print(f"""ER are not consecutive. Review list manually
              Total er: {len(di_no)}""")

    if em_no and check_consecutive(em_no):
        print(f"""Total er: {len(em_no)}
                  numbers are consecutive""")
    elif not em_no:
        print(f"""no EMs in M{args.collectionID}""")
    else:
        print(f"""ER are not consecutive. Review list manually
              Total er: {len(em_no)}""")

    print(f"""
            er_no: {er_no},
            di_no: {di_no},
            em_no: {em_no}
            """)
    if args.find_dups:
        print(f"""ER dups: {find_dups(er_no)}
                  DI dups: {find_dups(di_no)}
                  EM dups: {find_dups(em_no)}""")



if __name__ == "__main__":
    main()