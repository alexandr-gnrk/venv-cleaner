import argparse
from os import curdir
from pathlib import Path

import utils


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

start_dir = Path(args.path)
if not start_dir.is_dir():
    print('Error: specified path must be a directory')
    exit(1)

dir_gen = utils.child_dirs(start_dir)
go_down = None  # None value to start generator
while True:
    try:
        curr_dir = dir_gen.send(go_down)
        print(curr_dir)
        go_down = True
    except StopIteration:
        break
