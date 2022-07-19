import os
from PIL import Image


class TgaConverter:

    @staticmethod
    def convert(img_path: str, output_filename: str, output_folder: str, width: int, height: int, bits_per_pixel: int) -> str:
        im = Image.open(img_path)
        resized = im.resize((width, height), Image.LANCZOS)

        if bits_per_pixel == 24:
            resized.mode = "RGB"
        elif bits_per_pixel == 32:
            resized.mode = "RGBA"
        elif bits_per_pixel == 8:
            resized.mode = "LA"
        else:
            raise ValueError(f"Don't know how to convert to {bits_per_pixel}bpp")

        """
        SAVE = {
            "1": ("1", 1, 0, 3),
            "L": ("L", 8, 0, 3),
            "LA": ("LA", 16, 0, 3),
            "P": ("P", 8, 1, 1),
            "RGB": ("BGR", 24, 0, 2),
            "RGBA": ("BGRA", 32, 0, 2),
        }
        rawmode, bits, colormaptype, imagetype = SAVE[im.mode]
        """

        # Explicitly save uncompressed
        output_path = os.path.join(output_folder, output_filename)
        resized.save(output_path, compression=None)

        """
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
        """
        return output_path
