import argparse
from pathlib import Path
from collections.abc import Generator

import utils
from venv import Venv


def take_action(venv: Venv) -> int:
    freed_size = 0
    action = utils.read_action(backup=not venv.is_broken())

    if action == 'y':  # delete
        freed_size = venv.rm()
    elif action == 'b':  # backup
        backup_path = venv.save_requirements()
        print('Requirements backup location:', backup_path)
        freed_size = venv.rm()

    return freed_size


def print_venv_table() -> Generator[None, Venv | None, None]:
    print('{:30} {:8} {:10}'.format('Path', 'Broken', 'Size'))

    total_size = 0
    venv = (yield)
    while venv is not None:
        size = venv.size()
        size_str = utils.bytes_to_str(size)
        broken = venv.is_broken()
        total_size += size

        path = str(venv.path)
        if len(path) > 30:
            path = '...' + path[len(path)-27:]

        print('{:30} {:8} {:10}'.format(path, str(broken), size_str))

        venv = (yield)

    total_size_str = utils.bytes_to_str(total_size)
    print('{:39} {:10}'.format('Total size', total_size_str))


def main():
    parser = argparse.ArgumentParser(
        prog='Venv cleaner',
        description='A utility that helps to remove unnecessary python virtual environments.'
    )
    parser.add_argument(
        '-a', '--analyze',
        action='store_true',
        default=False,
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
    total_size = 0
    freed_size = 0
    if args.analyze is True:
        printer = print_venv_table()
        next(printer)
    else:
        printer = None

    for curr_dir in dir_gen:
        is_venv = Venv.is_venv(curr_dir)
        try:
            dir_gen.send(not is_venv)
        except StopIteration:
            pass
        if not is_venv:
            continue

        venv = Venv(curr_dir)
        if printer is not None:
            printer.send(venv)
            continue

        venv.print_info()
        total_size += venv.size()

        freed_size += take_action(venv)

    if printer is not None:
        try:
            printer.send(None)
        except StopIteration:
            pass
    else:
        print('Total size:', utils.bytes_to_str(total_size))
        print('Freed size:', utils.bytes_to_str(freed_size))


if __name__ == "__main__":
    main()

