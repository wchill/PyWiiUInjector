import os
import tempfile
from game import create_title
import concurrent.futures
from nus_downloader import NUSDownloader
import logging
import shutil
import argparse


logger = logging.getLogger(__name__)

project_root = os.path.dirname(os.path.abspath(__file__))


def build_title(title, output_dir, work_dir):
    tempfile.tempdir = os.path.normpath(work_dir)
    print(f"Starting {os.path.basename(title.iso_path)}")
    return title.build(output_dir)


def main(in_dirs, out_dir, work_dir, processes):
    tempfile.tempdir = os.path.normpath(work_dir)
    os.makedirs(tempfile.tempdir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    try:
        NUSDownloader.copy_files()

        titles = []
        for in_path in in_dirs:
            if os.path.isfile(in_path):
                titles.append(create_title(os.path.normpath(in_path)))
            else:
                with os.scandir(in_path) as it:
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
        print(f"Converting {len(titles)} titles")

        with concurrent.futures.ProcessPoolExecutor(max_workers=processes) as executor:
            # Start the load operations and mark each future with its URL
            future_to_title = {executor.submit(build_title, title, out_dir, work_dir): title for title in titles}
            for future in concurrent.futures.as_completed(future_to_title):
                title = future_to_title[future]
                try:
                    output_path = future.result()
                    print(f"{os.path.basename(title.iso_path)} -> {output_path}")
                except Exception as e:
                    print('%r generated an exception: %s' % (title.iso_path, e))
                    failed_titles.append(title)

        print([title.iso_path for title in failed_titles])
    finally:
        try:
            shutil.rmtree(tempfile.tempdir)
        except Exception:
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Package Wii/Gamecube software into Wii U Package (WUP) files.')
    parser.add_argument('--input', type=str, nargs='+', required=True,
                        help='Paths to input files/folders.')
    parser.add_argument('--output', type=str, nargs='?', default=os.path.abspath("output"),
                        help=f'Path to output folder. Default output folder is {os.path.abspath("output")}.')
    parser.add_argument('--temp', type=str, nargs='?', default=tempfile.gettempdir(),
                        help='Path to folder to use for temp storage. Default folder is the system temp directory.')
    parser.add_argument('--processes', type=int, nargs='?', default=1,
                        help='Number of concurrent processes. Default is 1')
    args = parser.parse_args()

    main(args.input, args.output, args.temp, args.processes)
