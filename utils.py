from re import sub
import sys
import subprocess
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


def activate_venv(path: Path) -> str:
    command = [with_pip_path(path), 'freeze']
    res = subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return res.stdout


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

