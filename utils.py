from pathlib import Path


def child_dirs(path: Path):
    # if not path.is_dir():
    #     return
    for p in path.iterdir():
        if not p.is_dir():
            continue

        go_down = (yield p)

        if go_down is True:
            yield from child_dirs(p)

