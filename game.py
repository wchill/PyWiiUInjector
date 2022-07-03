import io
import logging
import os
import shutil
import tempfile
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Literal, Tuple

import requests

from dol_copier import DolCopier
from nfs_iso_converter import NfsIsoConverter
from nus_downloader import NUSDownloader
from nus_packer import NUSPackerWrapper
from tga_converter import TgaConverter
from wit import WiimsISOToolsWrapper
from xml_templater import XMLTemplate

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


def create_title(iso_path: str, iso_path_2: Optional[str] = None, **kwargs: Any) -> "Title":
    with open(iso_path, "rb") as f:
        magic_header = f.read(4)
        title_id = int.from_bytes(magic_header, byteorder="little")

        if title_id == 65536:
            # This is a DOL file (aka homebrew)
            f.seek(0x2A0)
            title_id = int.from_bytes(f.read(4), byteorder="little")
            internal_game_name = "N/A"
            # TODO: Unimplemented
            raise NotImplementedError
        elif magic_header == b"WBFS":
            # TODO: Unimplemented
            """
            FlagWBFS = true;
            reader.BaseStream.Position = 0x200;
            TitleIDInt = reader.ReadInt32();
            reader.BaseStream.Position = 0x218;
            GameType = reader.ReadInt64();
            TempString = "";
            reader.BaseStream.Position = 0x220;
            while ((int)(TempChar = reader.ReadChar()) != 0) TempString = TempString + TempChar;
            InternalGameName = TempString;
            TempString = "";
            reader.BaseStream.Position = 0x200;
            while ((int)(TempChar = reader.ReadChar()) != 0) TempString = TempString + TempChar;
            CucholixRepoID = TempString;
            """
            raise NotImplementedError
        else:
            start_offset = 0

            if f.read(4) == b"NKIT":
                # TODO: Unimplemented
                raise NotImplementedError
            elif magic_header == b"WII5":
                # TODO: Unimplemented
                """
                if (idString == "WII5")
                {
                    FlagNASOS = true;
                    startOffset = 0x1182800;
                }
                """
                raise NotImplementedError
            elif magic_header == b"WII9":
                # TODO: Unimplemented
                """
                else if (idString == "WII9")
                {
                    FlagNASOS = true;
                    startOffset = 0x1FB5000;
                }
                """
                raise NotImplementedError

            f.seek(start_offset)
            title_id = int.from_bytes(f.read(4), byteorder="little")

            f.seek(start_offset + 0x18)
            game_type = int.from_bytes(f.read(8), byteorder="little")

            bio = io.BytesIO()
            while True:
                ch = f.read(1)
                if ch == b'\x00':
                    break
                bio.write(ch)
            game_name = bio.getvalue().decode("utf-8")

            f.seek(start_offset)
            bio = io.BytesIO()
            while True:
                ch = f.read(1)
                if ch == b'\x00':
                    break
                bio.write(ch)
            full_game_id = bio.getvalue().decode("utf-8")

            if game_type == 2745048157:
                return WiiRetailTitle(iso_path, title_id, game_name, full_game_id, **kwargs)
            elif game_type == 4440324665927270400:
                return GamecubeRetailTitle(iso_path, iso_path_2, title_id, game_name, full_game_id, **kwargs)

            raise NotImplementedError


class Title(ABC):
    BASE_URL = "https://raw.githubusercontent.com/cucholix/wiivc-bis/master/"
    SYSTEM_TYPE = None

    def __init__(self, iso_path: str, title_id: int, game_name: str, full_game_id: str):
        self.iso_path = iso_path
        self.title_id = title_id
        self.game_name = game_name
        self.full_game_id = full_game_id

    @staticmethod
    @abstractmethod
    def get_possible_image_ids(game_id) -> List[str]:
        raise NotImplementedError

    def get_candidate_urls(self) -> List[str]:
        possible_ids = self.get_possible_image_ids(self.full_game_id)
        return [self.BASE_URL + self.SYSTEM_TYPE + "/image/" + pid + "/" for pid in possible_ids]

    def fetch_images(self) -> Tuple[bytes, bytes]:
        icon = None
        banner = None
        urls = self.get_candidate_urls()
        for url in urls:
            r1 = requests.get(url + "iconTex.png")
            r2 = requests.get(url + "bootTvTex.png")
            if r1.status_code == 200:
                icon = r1.content
            if r2.status_code == 200:
                banner = r2.content

            if icon is not None and banner is not None:
                break

        if icon is None:
            raise ValueError("Unable to retrieve icon")

        if banner is None:
            raise ValueError("Unable to retrieve banner")

        return icon, banner

    def build(self, output_dir: str, icon_path: Optional[str] = None, banner_path: Optional[str] = None) -> str:
        root_logger.handlers = []
        fh = logging.FileHandler(os.path.join(output_dir, f"WUP-N-{self.title_id_text}_00050002{self.title_id_hex}.log"))
        fh.setLevel(logging.DEBUG)
        root_logger.addHandler(fh)

        output_path = os.path.join(output_dir, f"WUP-N-{self.title_id_text}_00050002{self.title_id_hex}")
        if os.path.isdir(output_path):
            logger.warning(f"Refusing to write to existing path {output_path}, exiting")
            return output_path

        with tempfile.TemporaryDirectory(
                prefix=f"build_{self.title_id_text}_") as temp_build_dir,\
            tempfile.TemporaryDirectory(
                prefix=f"work_{self.title_id_text}_") as temp_work_dir:
            build_meta_dir = os.path.join(temp_build_dir, "meta")
            build_code_dir = os.path.join(temp_build_dir, "code")

            logger.info("Getting files from NUS/cache")
            base_file_path = os.path.join(temp_work_dir, "base_files")
            NUSDownloader.copy_files(base_file_path)

            logger.info("Copying base files to build directory")
            shutil.copytree(os.path.join(base_file_path, NUSDownloader.RhythmHeavenFeverName), temp_build_dir,
                            dirs_exist_ok=True)

            logger.info("Generating app.xml")
            with open(os.path.join(build_code_dir, "app.xml"), "w") as f:
                f.write(self.build_app_xml())

            logger.info("Generating meta.xml")
            with open(os.path.join(build_meta_dir, "meta.xml"), "w") as f:
                f.write(self.build_meta_xml(self.drcuse, self.game_name, self.game_name))

            # Convert PNG to TGA
            logger.info("Converting icon/banner to TGA")
            temp_image_dir = os.path.join(temp_work_dir, "imgs")
            os.makedirs(temp_image_dir, exist_ok=True)

            if icon_path is None:
                fname = os.path.splitext(os.path.basename(self.iso_path))[0] + ".png"
                alt_icon_path = os.path.join(os.path.dirname(self.iso_path), "icons", fname)
                if not os.path.isfile(alt_icon_path):
                    icon_path = None
                else:
                    icon_path = os.path.join(temp_image_dir, "iconTex.png")
                    shutil.copyfile(alt_icon_path, icon_path)

            if banner_path is None:
                fname = os.path.splitext(os.path.basename(self.iso_path))[0] + ".png"
                alt_banner_path = os.path.join(os.path.dirname(self.iso_path), "banners", fname)
                if not os.path.isfile(alt_banner_path):
                    banner_path = None
                else:
                    banner_path = os.path.join(temp_image_dir, "bootTvTex.png")
                    shutil.copyfile(alt_banner_path, banner_path)

            if icon_path is None or banner_path is None:
                icon, banner = self.fetch_images()

                if icon_path is None:
                    icon_path = os.path.join(temp_image_dir, "iconTex.png")
                    with open(icon_path, "wb") as f:
                        f.write(icon)

                if banner_path is None:
                    banner_path = os.path.join(temp_image_dir, "bootTvTex.png")
                    with open(banner_path, "wb") as f:
                        f.write(banner)

            TgaConverter.convert(icon_path, "iconTex.tga", build_meta_dir, width=128, height=128, bits_per_pixel=32)
            TgaConverter.convert(banner_path, "bootTvTex.tga", build_meta_dir, width=1280, height=720, bits_per_pixel=24)

            # For gamepad, use existing banner if separate image not provided
            logger.info("Converting gamepad banner to TGA")
            gamepad_banner_path = os.path.join(os.path.dirname(banner_path), "bootDrcTex.png")
            shutil.copyfile(banner_path, gamepad_banner_path)
            TgaConverter.convert(gamepad_banner_path, "bootDrcTex.tga", build_meta_dir, width=854, height=480, bits_per_pixel=24)

            # Boot logo. Not mandatory
            # TODO: Plumb this path
            """
            logger.info("Converting boot logo to TGA")
            TgaConverter.convert(logo_path, "bootLogoTex.tga", build_meta_dir, width=170, height=42, bits_per_pixel=32)
            """

            # Convert boot sound if provided
            # TODO: Implement
            """
            logger.info("Converting boot sound to BTSND")
            //Convert Boot Sound if provided by user
            if (FlagBootSoundSpecified)
            {
                BuildStatus.Text = "Converting user-provided sound to btsnd format...";
                BuildStatus.Refresh();
                LauncherExeFile = TempToolsPath + "SOX\\sox.exe";
                LauncherExeArgs = 
                    "\"" + OpenBootSound.FileName + "\" -b 16 \"" + TempSoundPath + "\" channels 2 rate 48k trim 0 6";
                LaunchProgram();
                File.Delete(TempBuildPath + "meta\\bootSound.btsnd");
                LauncherExeFile = TempToolsPath + "JAR\\wav2btsnd.exe";
                LauncherExeArgs = 
                    "-in \"" + TempSoundPath + "\" -out \"" + TempBuildPath + "meta\\bootSound.btsnd\"" + LoopString;
                LaunchProgram();
                File.Delete(TempSoundPath);
            }
            """

            # Build ISO
            logger.info("Building ISO from extracted files")
            iso_path = self.prepare_iso(temp_work_dir)
            WiimsISOToolsWrapper.extract_tickets(iso_path, build_code_dir)

            # Convert ISO to NFS
            # TODO: Handle LR patch (L & R -> ZL & ZR) by adding -lrpatch flag
            content_path = os.path.join(temp_build_dir, "content")
            NfsIsoConverter.convert_iso_to_nfs(iso_path, content_path, self.get_nfs_patch_flags())

            # Encrypt with NUSPacker
            logger.info("Encrypting contents into installable WUP package")
            NUSPackerWrapper.pack(temp_build_dir, output_path, NUSDownloader.WiiUCommonKey)

            return output_path

    @abstractmethod
    def prepare_iso(self, temp_work_dir: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_nfs_patch_flags(self) -> List[str]:
        raise NotImplementedError

    @property
    def drcuse(self) -> Literal[1, 65537]:
        return 65537

    def build_meta_xml(self, drc_use: Literal[1, 65537], long_name: str,
                       short_name: Optional[str] = None) -> str:
        if short_name is None:
            short_name = long_name

        template = XMLTemplate("meta.xml.template")

        # This goes to meta/meta.xml
        return template.generate(
            title_id_text=self.title_id_text,
            title_id_hex=self.title_id_hex,
            drc_use=drc_use,
            long_name=long_name,
            short_name=short_name
        )

    def build_app_xml(self) -> str:
        template = XMLTemplate("app.xml.template")

        # This goes to code/app.xml
        return template.generate(title_id_hex=self.title_id_hex)

    @property
    def title_id_hex(self) -> str:
        s = f"{self.title_id:0>8X}"
        return "".join(reversed([s[i:i+2] for i in range(0, len(s), 2)]))

    @property
    def title_id_text(self) -> str:
        raise NotImplementedError


class WiiRetailTitle(Title):
    SYSTEM_TYPE = "wii"

    # vmc ntsc to pal
    # pal to ntsc
    # bunch of other video modes

    def __init__(self, iso_path: str, title_id: int, game_name: str, full_game_id: str, use_wiimmfi: bool = False,
                 vmc_mode: Optional[str] = None):
        super().__init__(iso_path, title_id, game_name, full_game_id)
        self.use_wiimmfi = use_wiimmfi

        assert vmc_mode is None, "Video Mode Changer support unimplemented"

    @property
    def drcuse(self) -> Literal[1, 65537]:
        # TODO: handle gamepad emulation
        return 1

    @staticmethod
    def get_possible_image_ids(game_id: str) -> List[str]:
        return [game_id[:3] + region + game_id[4:6] for region in [game_id[3], "E", "P", "J"]]

    @property
    def title_id_text(self) -> str:
        return bytes.fromhex(self.title_id_hex).decode("ascii")

    def prepare_iso(self, temp_work_dir: str) -> str:
        # TODO: if trimming disabled, skip everything
        logger.info("Extracting game for NFS conversion")
        with tempfile.TemporaryDirectory(dir=temp_work_dir) as temp_dir_name:
            WiimsISOToolsWrapper.extract_iso(self.iso_path, temp_dir_name)

            # TODO: if classic controller forced, run stuff
            """
            LauncherExeFile = TempToolsPath + "EXE\\GetExtTypePatcher.exe";
            LauncherExeArgs = "\"" + TempSourcePath + "ISOEXTRACT\\sys\\main.dol\" -nc";
            """

            # TODO: if VMC specified, run stuff
            """
            LauncherExeFile = TempToolsPath + "EXE\\wii-vmc.exe";
            LauncherExeArgs = "\"" + TempSourcePath + "ISOEXTRACT\\sys\\main.dol\"";
            """

            return WiimsISOToolsWrapper.rebuild_iso(temp_dir_name, os.path.join(temp_work_dir, "game.iso"),
                                                    self.use_wiimmfi)

    def get_nfs_patch_flags(self) -> List[str]:
        # TODO: Handle gamepad patches (nfspatchflag)
        return ["-enc"]


class GamecubeRetailTitle(Title):
    SYSTEM_TYPE = "gcn"

    def __init__(self, iso_path: str, iso_path_2: Optional[str], title_id: int, game_name: str, full_game_id: str,
                 force_43: bool = False, custom_forwarder: Optional[str] = None, disable_autoboot: bool = False):
        super().__init__(iso_path, title_id, game_name, full_game_id)
        self.iso_path_2 = iso_path_2
        self.force_43 = force_43
        self.custom_forwarder = custom_forwarder
        self.disable_autoboot = disable_autoboot

    @staticmethod
    def get_possible_image_ids(game_id: str) -> List[str]:
        return [game_id[:3] + region + game_id[4:6] for region in [game_id[3], "E", "P", "J"]]

    @property
    def title_id_text(self) -> str:
        return bytes.fromhex(self.title_id_hex).decode("ascii")

    def prepare_iso(self, temp_work_dir: str) -> str:
        with tempfile.TemporaryDirectory(dir=temp_work_dir) as temp_dir:
            DolCopier.copy_base(temp_dir)
            main_dol_path = os.path.join(temp_dir, "sys", "main.dol")
            if self.force_43:
                DolCopier.copy_dol("FIX94_nintendont_force43_autoboot.dol", main_dol_path)
            elif self.custom_forwarder:
                shutil.copyfile(self.custom_forwarder, main_dol_path)
            elif self.disable_autoboot:
                DolCopier.copy_dol("FIX94_nintendont_forwarder.dol", main_dol_path)
            else:
                DolCopier.copy_dol("FIX94_nintendont_default_autoboot.dol", main_dol_path)

            shutil.copyfile(self.iso_path, os.path.join(temp_dir, "files", "game.iso"))
            if self.iso_path_2:
                shutil.copyfile(self.iso_path_2, os.path.join(temp_dir, "files", "disc2.iso"))

            return WiimsISOToolsWrapper.rebuild_iso(temp_dir, os.path.join(temp_work_dir, "game.iso"), False)

    def get_nfs_patch_flags(self) -> List[str]:
        return ["-enc", "-homebrew", "-passthrough"]


class WiiWareTitle(Title, ABC):
    SYSTEM_TYPE = "wiiware"

    def __init__(self, title_id: int, force_43: bool = False):
        # idk
        super().__init__(None, title_id, None)
        self.force_43 = force_43

    @staticmethod
    def get_possible_image_ids(game_id: str) -> List[str]:
        return [game_id[:3] + region for region in [game_id[3], "E", "P", "J"]]

    @property
    def title_id_text(self) -> str:
        return bytes.fromhex(self.title_id_hex).decode("ascii")


class WiiHomebrewTitle(Title, ABC):
    SYSTEM_TYPE = "dol"
    ANCAST_KEY = None  # if (AncastKeyHash == "31-8D-1F-9D-98-FB-08-E7-7C-7F-E1-77-AA-49-05-43")

    def __init__(self, title_id: int, no_remote_passthrough: bool = False, no_gamepad: bool = False,
                 enable_cafe2wii_patching: bool = False):
        # idk
        super().__init__(None, title_id, "N/A")
        self.no_remote_passthrough = no_remote_passthrough
        self.no_gamepad = no_gamepad

        assert not enable_cafe2wii_patching, "Cafe2Wii patching is unsupported"

    @staticmethod
    def get_possible_image_ids(game_id: str) -> List[str]:
        return []

    @property
    def title_id_text(self) -> str:
        return "BOOT"
