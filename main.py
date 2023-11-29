import argparse
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
total_size = 0
freed_size = 0
while True:
    try:
        curr_dir = dir_gen.send(go_down)
        is_venv = utils.is_virtualenv(curr_dir)

        if is_venv is False:
            go_down = True
            continue
        else:
            go_down = False

        size = utils.get_dir_size(curr_dir)
        total_size += size

        is_broken = utils.is_broken_venv(curr_dir)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('Path:', curr_dir)
        print('Name:', utils.get_venv_name(curr_dir))
        print('Size:', utils.bytes_to_str(size))
        print('Is broken:', is_broken)

        action = utils.read_action(backup=not is_broken)

        if action == 'y':  # delete
            utils.rm_venv(curr_dir)
            freed_size += size
        elif action == 'b':  # backup
            utils.get_freeze(curr_dir)
            backup_path = utils.create_requirements_backup(curr_dir)
            print('Requirements backup location:', backup_path)
            utils.rm_venv(curr_dir)
            freed_size += size
        else:  # skip
            pass
    except (StopIteration, KeyboardInterrupt):
        print('Total size:', utils.bytes_to_str(total_size))
        print('Freed size:', utils.bytes_to_str(freed_size))
        break
