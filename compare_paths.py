import argparse
import logging
from pathlib import Path

def _make_parser():
    parser = argparse.ArgumentParser(description='Compare two directories using rglob all')
    parser.add_argument('-d_one', '--directory_one',
                        help = '''required. First directory to compare''',
                        required=True)
    parser.add_argument('-d_two', '--directory_two',
                        help = f'''required. Second directory to compare.''',
                        required=True)

    return parser

def find_all_paths(dir):
    path_set = set()
    for item in dir.rglob('*'):
        if not item.name.startswith('.') and not item.name == 'Thumbs.db':
            item
            path_set.add(item)
    return path_set




def main():
    parser = _make_parser()
    args = parser.parse_args()

    dir_one_set = find_all_paths(args.directory_one)
    dir_two_set = find_all_paths(args.directory_two)

    if not dir_one_set == dir_two_set:
        logging.error(f'These two directories are different')


if __name__ == "__main__":
    main()