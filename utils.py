import sys
from pathlib import Path
from collections.abc import Generator


def child_dirs(path: Path) -> Generator[Path, bool, None]:
    for p in path.iterdir():
        if not p.is_dir():
            continue

        go_down = (yield p)

        if go_down is True:
            yield from child_dirs(p)


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
