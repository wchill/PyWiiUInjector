import os
import tempfile
from game import create_title
import concurrent.futures
from nus_downloader import NUSDownloader
import logging
import shutil


logger = logging.getLogger(__name__)

project_root = os.path.dirname(os.path.abspath(__file__))

work_dir = os.path.join(project_root, "temp")
out_dir = os.path.join(project_root, "output")
in_dir = os.path.join(project_root, "input")


def build_title(title, output_dir):
    tempfile.tempdir = os.path.normpath(work_dir)
    print(f"Starting {os.path.basename(title.iso_path)}")
    return title.build(output_dir)


def main():
    tempfile.tempdir = os.path.normpath(work_dir)
    os.makedirs(tempfile.tempdir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    try:
        NUSDownloader.copy_files()

        titles = []
        with os.scandir(in_dir) as it:
            for entry in it:
                if (not entry.name.startswith(".")) and entry.is_file() and os.path.splitext(entry.name)[-1] == ".iso":
                    if "(Disc 2)" in entry.name:
                        continue
                    elif "(Disc 1)" in entry.name:
                        disc_1_path = os.path.normpath(entry.path)
                        disc_2_path = disc_1_path.replace("(Disc 1)", "(Disc 2)")
                        titles.append(create_title(disc_1_path, disc_2_path))
                    else:
                        titles.append(create_title(os.path.normpath(entry.path)))

        failed_titles = []

        with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            # Start the load operations and mark each future with its URL
            future_to_title = {executor.submit(build_title, title, out_dir): title for title in titles}
            for future in concurrent.futures.as_completed(future_to_title):
                title = future_to_title[future]
                try:
                    output_path = future.result()
                    print(f"{os.path.basename(title.iso_path)} -> {output_path}")

                    from pathlib import Path

                    root_directory = Path(output_path)
                    folder_size = sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())

                    if folder_size < 50 * 1024 * 1024:
                        logger.warning(f"{output_path} has bad size")
                except Exception as e:
                    import traceback
                    # print('%r generated an exception: %s' % (title.iso_path, traceback.format_exc()))
                    print('%r generated an exception: %s' % (title.iso_path, e))
                    failed_titles.append(title)

        print([title.iso_path for title in failed_titles])
    finally:
        try:
            shutil.rmtree(tempfile.tempdir)
        except Exception:
            pass


if __name__ == '__main__':
    main()
