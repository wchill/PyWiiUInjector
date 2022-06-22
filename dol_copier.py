import os
import shutil


class DolCopier:
    @staticmethod
    def copy_dol(name: str, output_path: str) -> str:
        src = os.path.join(os.path.dirname(__file__), "TOOLDIR", "DOL", name)
        shutil.copyfile(src, output_path)
        return output_path

    @staticmethod
    def copy_base(output_path: str) -> str:
        src = os.path.join(os.path.dirname(__file__), "TOOLDIR", "BASE")
        shutil.copytree(src, output_path, dirs_exist_ok=True)
        return output_path
