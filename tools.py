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
        return pathlib.Path(__file__).parent / "tool_bin"

    @classmethod
    def get_tool(cls: Type["Tool"], path: str, tool_name: str) -> "Tool":
        return cls(cls.get_tooldir() / path, tool_name)

    def _run(self, args: List[str], **kwargs: Any) -> subprocess.CompletedProcess:
        logger.info(f"Running {' '.join(args)}")
        print(' '.join(args))
        p = subprocess.run(args, **kwargs, capture_output=True)
        if p.stdout:
            logger.debug(f'stdout: {p.stdout.decode("utf-8", errors="replace")}')
        if p.stderr:
            logger.debug(f'stderr: {p.stderr.decode("utf-8", errors="replace")}')
        return p

    def run(self, args: List[str], **kwargs: Any) -> subprocess.CompletedProcess:
        complete_args = [self.path] + args
        return self._run(complete_args, **kwargs)


class JarTool(Tool):
    def run(self, args: List[str], **kwargs: Any) -> subprocess.CompletedProcess:
        complete_args = ["java", "-jar", self.path] + args
        return self._run(complete_args, **kwargs)


# C2W_Patcher = Tool.get_tool("C2W", "c2w_patcher.exe")

# GetExtTypePatcher = Tool.get_tool("EXE", "GetExtTypePatcher")
Nfs2Iso2Nfs = Tool.get_tool("nfs2iso2nfs", "nfs2iso2nfs")
# WBFS_File = Tool.get_tool("EXE", "wbfs_file")
# WiiVMC = Tool.get_tool("EXE", "wii-vmc")

# Png2Tga = Tool.get_tool("IMG", "png2tgacmd")
# Tga2Png = Tool.get_tool("IMG", "tga2pngcmd")

JNUSTool = JarTool.get_tool("JNUSTool", "jnustool.jar")
NUSPacker = Tool.get_tool("CNUS_Packer", "CNUSPACKER")
# Wav2Btsnd = Tool.get_tool("JAR", "wav2btsnd")

# NKit2ISO = Tool.get_tool("NKIT", "ConvertToISO")

# Sox = Tool.get_tool("SOX", "sox")

WiimsISOTools = Tool.get_tool("wit", "wit")
