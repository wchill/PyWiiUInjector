import os
from tools import Png2Tga


class TgaConverter:

    @staticmethod
    def convert(img_path: str, output_filename: str, output_folder: str, width: int, height: int, bits_per_pixel: int) -> str:
        Png2Tga.run([
            "-i",
            os.path.abspath(img_path),
            "-o",
            os.path.abspath(output_folder),
            f"--width={width}",
            f"--height={height}",
            f"--tga-bpp={bits_per_pixel}",
            "--tga-compression=none"
        ])

        new_filename = os.path.splitext(os.path.basename(img_path))[0] + ".tga"
        return os.path.abspath(os.path.join(output_folder, new_filename))
