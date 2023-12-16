from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import sys

import utils


class Venv:

    def __init__(self, path: Path) -> None:
        self.path = path
        self.name = path.name

    def freeze(self) -> str:
        command = [self.__with_pip_path(self.path), 'freeze']
        res = subprocess.run(
            command,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        return res.stdout

    def rm(self) -> int:
        size = self.size()
        shutil.rmtree(self.path)
        return size

    def size(self) -> int:
        return utils.get_dir_size(self.path)

    def size_str(self) -> str:
        return utils.bytes_to_str(self.size())

    def is_broken(self) -> bool:
        command = [self.__with_pip_path(self.path)]
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

    def save_requirements(self, path: Path | None = None) -> Path:
        if path is None:
            path = self.path

        date_str = datetime.now().strftime('%y-%m-%d-%H-%M-%S')
        req_name = f'requirements-backup-{date_str}.txt'
        req_path = path.with_name(req_name)
        freeze = self.freeze()
        req_path.write_text(freeze)
        return req_path

    def print_info(self) -> None:
        print('-------------------------------------')
        print('Path:', self.path)
        print('Name:', self.name)
        print('Size:', self.size_str())
        print('Is broken:', self.is_broken())

    @classmethod
    def is_venv(cls, path: Path) -> bool:
        bin = cls.__with_bin_path(path)
        python = cls.__with_python_path(path)
        
        try:
            has_bin = bin.is_dir()
            has_python = python.is_file()
            has_pyvenv_cfg = path.joinpath('pyvenv.cfg').is_file()
        except PermissionError:
            return False
        
        return has_bin and has_python and has_pyvenv_cfg

    @classmethod
    def __with_bin_path(cls, path) -> Path:
        return path / ('bin' if sys.platform != 'win32' else 'Scripts')

    @classmethod
    def __with_python_path(cls, path) -> Path:
        path = cls.__with_bin_path(path)
        return path / ('python' if sys.platform != 'win32' else 'python.exe')

    @classmethod
    def __with_pip_path(cls, path) -> Path:
        path = cls.__with_bin_path(path)
        return path / ('pip3' if sys.platform != 'win32' else 'pip3.exe')

