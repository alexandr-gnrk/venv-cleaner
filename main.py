import argparse

parser = argparse.ArgumentParser(
    prog='Venv cleaner',
    description='A utility that helps to remove unnecessary python virtual environments.'
)
parser.add_argument(
    'path',
    type=str,
    help='path to directory where the search starts',
)

args = parser.parse_args()
