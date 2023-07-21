import argparse
import logging
import re
import sys
from pathlib import Path
import filecmp

def _make_parser():
    parser = argparse.ArgumentParser(description='Compare two directories using rglob all')
    parser.add_argument('-d_one', '--directory_one',
                        help = '''required. First directory to compare''',
                        required=True)
    parser.add_argument('-d_two', '--directory_two',
                        help = f'''required. Second directory to compare.''',
                        required=True)

    return parser

def parts_tuple_to_path(tuple) -> Path:
    newpath = Path()
    for item in tuple:
        newpath = newpath / item

    return newpath

def find_all_paths(dir):
    path_set = set()
    parent_path = ''
    dir = Path(dir)

    if dir_is_empty(dir):
        sys.exit(f'{dir} is empty')

    for item in dir.rglob('*'):
        if not item.name.startswith('.') and not item.name == 'Thumbs.db':
            item_parts = item.parts # item_parts is a tuple
            for part in item_parts:
                if re.match('^M\d+$', part):
                    ind = item_parts.index(part)
                    part_path = parts_tuple_to_path(item_parts[ind:])
                    if not parent_path:
                        parent_path = parts_tuple_to_path(item_parts[0:ind])
                        # this is for reconstructing the original path for file comparison later
                    path_set.add(part_path)

    return path_set, parent_path

def dir_is_empty(dir: Path) -> bool:
    if not any(dir.iterdir()):
        return True
    else:
        return False

def main():
    parser = _make_parser()
    args = parser.parse_args()

    dir_one_set, parent_one = find_all_paths(args.directory_one)
    dir_two_set, parent_two = find_all_paths(args.directory_two)


    print(f'''Direcotry one set:
              {dir_one_set}''')

    print(f'''Direcotry two set:
              {dir_two_set}''')

    if not dir_one_set == dir_two_set:
        print(dir_one_set.symmetric_difference(dir_two_set))
        logging.error(f'These two directories are different')
    else:
        print('These two directories are the same, now compare files')
        mismatch_ls = list()
        for item in dir_one_set:
            item_one_path = parent_one / item
            item_two_path = parent_two / item
            if item_one_path.is_file() and item_two_path.is_file():
                if not filecmp.cmp(item_one_path, item_two_path, shallow=True):
                    mismatch_ls.append(item)
        if mismatch_ls:
            logging.error(f'Mismatch: {mismatch_ls}')
        else:
            print(f'Both directories files are the same')


if __name__ == "__main__":
    main()