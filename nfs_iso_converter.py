from typing import List
from tools import Nfs2Iso2Nfs
import os
from contextlib import contextmanager


@contextmanager
def chdir(directory):
    cwd = os.getcwd()
    try:
        os.chdir(directory)
        yield directory
    except FileNotFoundError:
        yield
    finally:
        os.chdir(cwd)


class NfsIsoConverter:
    @staticmethod
    def convert_iso_to_nfs(source_iso: str, output_path: str, flags: List[str]):
        with chdir(output_path):
            p = Nfs2Iso2Nfs.run([*flags, "-iso", source_iso])
            p.check_returncode()

        return output_path
