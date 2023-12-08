import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from collections.abc import Generator


def child_dirs(path: Path) -> Generator[Path, bool|None, None]:
    for p in path.iterdir():
        try:
            # TODO: skip if symlink? p.is_symlink()
            if not p.is_dir():
                continue

            # check if we have right to read from directory
            list(p.iterdir())
        except PermissionError:
            continue

        go_down = (yield p)

        if go_down is True:
            yield from child_dirs(p)


def print_venv_table() -> Generator[None, Path | None, None]:
    print('{:30} {:8} {:10}'.format('Path', 'Broken', 'Size'))

    total_size = 0
    path = (yield)
    while path is not None:
        size = get_dir_size(path)
        size_str = bytes_to_str(size)
        broken = is_broken_venv(path)
        total_size += size

        path = str(path)
        if len(path) > 30:
            path = '...' + path[len(path)-27:]

        print('{:30} {:8} {:10}'.format(path, str(broken), size_str))

        path = (yield)

    total_size_str = bytes_to_str(total_size)
    print('{:39} {:10}'.format('Total size', total_size_str))


def get_dir_size(path: Path) -> int:
    size = path.lstat().st_size

    for p in path.iterdir():
        if not p.is_symlink() and p.is_dir():
            size += get_dir_size(p)
        else:
            size += p.lstat().st_size

    return size


def with_bin_path(path: Path) -> Path:
    return path / ('bin' if sys.platform != 'win32' else 'Scripts')

def with_python_path(path: Path) -> Path:
    path = with_bin_path(path)
    return path / ('python' if sys.platform != 'win32' else 'python.exe')

def with_pip_path(path: Path) -> Path:
    path = with_bin_path(path)
    return path / ('pip3' if sys.platform != 'win32' else 'pip3.exe')


def is_virtualenv(path: Path) -> bool:
    bin = with_bin_path(path)
    python = with_python_path(path)
    
    try:
        has_bin = bin.is_dir()
        has_python = python.is_file()
        has_pyvenv_cfg = path.joinpath('pyvenv.cfg').is_file()
    except PermissionError:
        return False
    
    return has_bin and has_python and has_pyvenv_cfg


def is_broken_venv(path: Path) -> bool:
    command = [with_pip_path(path)]
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return True

    return False


def get_freeze(path: Path) -> str:
    command = [with_pip_path(path), 'freeze']
    res = subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return res.stdout


def get_venv_name(path: Path) -> str:
    return path.name


def rm_venv(path: Path) -> None:
    shutil.rmtree(path)


def read_action(backup=True) -> str:
    question = 'Do you want to delete this virtual environment?'
    if backup:
        print(question + ' (Y)es/(N)o/(B)ackup and delete')
        answer = input('[y/N/b] > ').lower()
        if answer == 'y':
            return 'y'
        elif answer == 'b':
            return 'b'
        else:
            return 'n'
    else:
        print(question + ' (Y)es/(N)o')
        answer = input('[y/N] > ').lower()
        if answer == 'y':
            return 'y'
        else:
            return 'n'

def create_requirements_backup(path: Path) -> Path:
    date_str = datetime.now().strftime('%y-%m-%d-%H-%M-%S')
    req_name = f'requirements-backup-{date_str}.txt'
    req_path = path.with_name(req_name)
    freeze = get_freeze(path)
    req_path.write_text(freeze)
    return req_path


def bytes_to_str(size: int, full=False) -> str:
    si_prefixes = (
        ('k', 'kilo'),
        ('M', 'mega'),
        ('G', 'giga'),
        ('T', 'tera'),
        ('P', 'peta'),
    )

    prefix = ''
    name = 'byte(s)' if full else 'B'

    i = 0
    nsize = float(size)
    while nsize >= 1024:
        nsize /= 1024
        prefix = si_prefixes[i][1] if full else si_prefixes[i][0]
        i += 1

    return f'{nsize:.2f} {prefix}{name}'

