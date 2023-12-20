from pathlib import Path
from collections.abc import Generator


def child_dirs(path: Path) -> Generator[Path, bool|None, None]:
    go_down = None
    for p in path.iterdir():
        try:
            # TODO: skip if symlink? p.is_symlink()
            if not p.is_dir():
                continue

            # check if we have right to read from directory
            list(p.iterdir())
        except PermissionError:
            continue

        while go_down is None:
            go_down = (yield p)

        if go_down is True:
            yield from child_dirs(p)

        go_down = None


def get_dir_size(path: Path) -> int:
    size = path.lstat().st_size

    for p in path.iterdir():
        if not p.is_symlink() and p.is_dir():
            size += get_dir_size(p)
        else:
            size += p.lstat().st_size

    return size


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

