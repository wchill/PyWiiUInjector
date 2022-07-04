from typing import Optional
import os.path
from tools import JNUSTool
import concurrent.futures
import hashlib
import shutil
import tempfile
import json
from config import Config


# if (WiiUCommonKeyHash == "35-AC-59-94-97-22-79-33-1D-97-09-4F-A2-FB-97-FC")
# if (TitleKeyHash == "F9-4B-D8-8E-BB-7A-A9-38-67-E6-30-61-5F-27-1C-9F")
class NUSDownloader:
    NUSUrl = "http://ccs.cdn.wup.shop.nintendo.net/ccs/download"

    OSv0TitleId = "0005001010004000"
    OSv0Name = OSv0TitleId
    OSv0FileList = {
        "/code/deint.txt": "E707A62EE5491DD16E5494631EA9870A",
        "/code/font.bin": "CDDAC70FDDB9428F220B048102DAAD40"
    }

    OSv1TitleId = "0005001010004001"
    OSv1Name = OSv1TitleId
    OSv1FileList = {
        "/code/c2w.img": "FC5EE480F58796C3681BEE78BD3E5D1C",
        "/code/boot.bin": "F4D5F095CBA9504A5CB8A94A4781114C",
        "/code/dmcu.d.hex": "E32FCBCC817C443E0832DE5CA9032808"
    }

    RhythmHeavenFeverName = "Rhythm Heaven Fever [VAKE01]"
    RhythmHeavenFeverTitleId = "00050000101b0700"
    RhythmHeavenFeverFileList = {
        "/code/cos.xml": "42215713D951C2023F90164ED9DF900F",
        "/code/frisbiiU.rpx": "69E191E8B0DF1D5304B36F1375C4F127",
        "/code/fw.img": "3CAF52A9A440EEE4F125A3AD22E305C8",
        "/code/fw.tmd": "AE4E06CAD3BEF60AE5C49E22CCDC3254",
        "/code/htk.bin": "C99CAF5995E395F39C3FCAB4A8AF20E0",
        "/code/nn_hai_user.rpl": "C4BF586BA0071BD8477986C1AA37E1F1",
        "/content/assets/shaders/cafe/banner.gsh": "5F2FA196DFC158F0FCC69272073AE07E",
        "/content/assets/shaders/cafe/fade.gsh": "307221985A7B46F0386A2637DC15DA3E",
        "/meta/bootMovie.h264": "CA0DAC3E3C5654209C754357EF5A2507",
        "/meta/bootLogoTex.tga": "67B312145ECB70514D5BD36FCAAE0193",
        "/meta/bootSound.btsnd": "43CD445B8569A445F97ECCC098C93B38"
    }

    @classmethod
    def write_config(cls, path: str) -> None:
        config = [
            cls.NUSUrl,
            Config.WiiUCommonKey
        ]
        with open(os.path.join(path, "config"), "w") as f:
            f.write('\n'.join(config))

    @classmethod
    def download_file(cls, title_id: str, filename: str, output_dir: str, md5_hash: str,
                      title_key: Optional[str] = None) -> str:
        rel_path = os.path.normpath(os.path.join(output_dir, filename[1:]))
        output_path = os.path.abspath(os.path.join(JNUSTool.directory, rel_path))

        if not os.path.exists(output_path):
            args = [title_id]
            if title_key:
                args.append(title_key)
            args += ["-file", filename]
            p = JNUSTool.run(args, cwd=JNUSTool.directory)
            p.check_returncode()

            assert os.path.exists(output_path), f"{output_path} does not exist"
            assert cls.verify_md5_hash(output_path, md5_hash)

        return rel_path

    @classmethod
    def check_if_files_exist(cls, directory: str) -> bool:
        directory = os.path.abspath(directory)
        for name, md5_hash in cls.OSv0FileList.items():
            path = os.path.join(directory, cls.OSv0Name, name[1:])
            if not (os.path.exists(path) and cls.verify_md5_hash(path, md5_hash)):
                return False
        for name, md5_hash in cls.OSv1FileList.items():
            path = os.path.join(directory, cls.OSv1Name, name[1:])
            if not (os.path.exists(path) and cls.verify_md5_hash(path, md5_hash)):
                return False
        for name, md5_hash in cls.RhythmHeavenFeverFileList.items():
            path = os.path.join(directory, cls.RhythmHeavenFeverName, name[1:])
            if not (os.path.exists(path) and cls.verify_md5_hash(path, md5_hash)):
                return False

        return True

    @staticmethod
    def verify_md5_hash(filename: str, md5_hash: str) -> bool:
        hash_obj = hashlib.md5()
        with open(filename, "rb") as f:
            buf = f.read()
            hash_obj.update(buf)
        return hash_obj.hexdigest().lower() == md5_hash.lower()

    @classmethod
    def download_all_files(cls, output_directory: str) -> None:
        if cls.check_if_files_exist(output_directory):
            return

        output_directory = os.path.abspath(output_directory)
        cls.write_config(JNUSTool.directory)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for name, md5_hash in cls.OSv0FileList.items():
                futures.append(executor.submit(cls.download_file, cls.OSv0TitleId, name, cls.OSv0Name, md5_hash))
            for name, md5_hash in cls.OSv1FileList.items():
                futures.append(executor.submit(cls.download_file, cls.OSv1TitleId, name, cls.OSv1Name, md5_hash))
            for name, md5_hash in cls.RhythmHeavenFeverFileList.items():
                futures.append(
                    executor.submit(cls.download_file, cls.RhythmHeavenFeverTitleId, name, cls.RhythmHeavenFeverName,
                                    md5_hash, Config.RhythmHeavenFeverTitleKey))

        assert all(f.result() is not None for f in futures)
        os.unlink(os.path.join(JNUSTool.directory, "config"))

        os.makedirs(output_directory, exist_ok=True)
        for d in [cls.OSv0Name, cls.OSv1Name, cls.RhythmHeavenFeverName]:
            dst_d = os.path.join(output_directory, d)
            src_d = os.path.join(JNUSTool.directory, d)
            shutil.rmtree(dst_d, ignore_errors=True)
            shutil.copytree(src_d, dst_d)
            shutil.rmtree(src_d)

    @classmethod
    def get_tempdir(cls) -> str:
        sys_tempdir = tempfile.gettempdir()
        return os.path.normpath(os.path.join(sys_tempdir, cls.__name__))

    @classmethod
    def copy_files(cls, output_dir: Optional[str] = None) -> str:
        tempdir = cls.get_tempdir()
        cls.download_all_files(tempdir)
        if output_dir is not None:
            download_dir = os.path.normpath(os.path.join(tempdir, output_dir))
            shutil.copytree(tempdir, download_dir, dirs_exist_ok=True)
            return download_dir
        else:
            return tempdir


if __name__ == "__main__":
    NUSDownloader.copy_files("z:/temp")
