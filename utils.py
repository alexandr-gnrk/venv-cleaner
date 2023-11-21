import sys
from pathlib import Path
from collections.abc import Generator


def child_dirs(path: Path) -> Generator[Path, bool|None, None]:
    for p in path.iterdir():
        # TODO: skip if symlink? p.is_symlink()
        if not p.is_dir():
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


def is_virtualenv(path: Path) -> bool:
    if sys.platform != 'win32':
        bin = path / 'bin'
        python = bin / 'python'
    else:
        bin = path / 'Sripts'
        python = bin / 'python.exe'
    
    has_bin = bin.is_dir()
    has_python = python.is_file()
    has_pyvenv_cfg = path.joinpath('pyvenv.cfg').is_file()
    
    return has_bin and has_python and has_pyvenv_cfg

def bytes_to_str(size: int, full=False) -> str:
    si_prefixes = (
        ('k', 'kilo'),
        ('M', 'mega'),
        ('G', 'giga'),
        ('T', 'tera'),
        ('P', 'peta'),
    )

    prefix = ''
    name = 'byte' if full else 'B'

    i = 0
    nsize = float(size)
    while nsize >= 1024:
        nsize /= 1024
        prefix = si_prefixes[i][1] if full else si_prefixes[i][0]
        i += 1

    return f'{nsize:.2f} {prefix}{name}'

