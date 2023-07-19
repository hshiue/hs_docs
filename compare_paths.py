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




def main():
    parser = _make_parser()
    args = parser.parse_args()



if __name__ == "__main__":
    main()