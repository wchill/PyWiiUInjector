from tools import NUSPacker


class NUSPackerWrapper:
    @staticmethod
    def pack(source_folder: str, output_folder: str, common_key: str) -> None:
        NUSPacker.run(["-in", source_folder, "-out", output_folder, "-encryptKeyWith", common_key])
