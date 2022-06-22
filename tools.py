from typing import Any, Type, List
import pathlib
import subprocess
import logging

logger = logging.getLogger(__name__)


class Tool:

    def __init__(self, path: pathlib.Path, tool_name: str):
        self.path = str(path / tool_name)
        self.directory = str(path)

    @staticmethod
    def get_tooldir() -> pathlib.Path:
        return pathlib.Path(__file__).parent / "TOOLDIR"

    @classmethod
    def get_tool(cls: Type["Tool"], path: str, tool_name: str) -> "Tool":
        return cls(cls.get_tooldir() / path, tool_name)

    def run(self, args: List[str], **kwargs: Any) -> subprocess.CompletedProcess:
        complete_args = [self.path] + args
        logger.info(f"Running {' '.join(complete_args)}")
        p = subprocess.run(complete_args, **kwargs, capture_output=True)
        logger.debug(f'stdout: {p.stdout.decode("utf-8", errors="replace")}')
        logger.debug(f'stderr: {p.stderr.decode("utf-8", errors="replace")}')
        return p


C2W_Patcher = Tool.get_tool("C2W", "c2w_patcher.exe")

GetExtTypePatcher = Tool.get_tool("EXE", "GetExtTypePatcher.exe")
Nfs2Iso2Nfs = Tool.get_tool("EXE", "nfs2iso2nfs.exe")
WBFS_File = Tool.get_tool("EXE", "wbfs_file.exe")
WiiVMC = Tool.get_tool("EXE", "wii-vmc.exe")

Png2Tga = Tool.get_tool("IMG", "png2tgacmd.exe")
Tga2Png = Tool.get_tool("IMG", "tga2pngcmd.exe")

JNUSTool = Tool.get_tool("JAR", "jnustool.exe")
NUSPacker = Tool.get_tool("JAR", "nuspacker.exe")
Wav2Btsnd = Tool.get_tool("JAR", "wav2btsnd.exe")

NKit2ISO = Tool.get_tool("NKIT", "ConvertToISO.exe")

Sox = Tool.get_tool("SOX", "sox.exe")

WiimsISOTools = Tool.get_tool("WIT", "wit.exe")
