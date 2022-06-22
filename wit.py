from tools import WiimsISOTools
import os
import tempfile


class WiimsISOToolsWrapper:
    @staticmethod
    def extract_tickets(source_iso: str, output_folder: str) -> str:
        with tempfile.TemporaryDirectory() as tempdir_name:
            ticket_dir = os.path.join(tempdir_name, "tickets")
            WiimsISOTools.run(["extract", source_iso, "--psel", "data", "--psel", "-update", "--files", "+tmd.bin", "--files", "+ticket.bin", "--dest", ticket_dir, "-vv1"])
            os.makedirs(output_folder, exist_ok=True)
            try:
                os.replace(os.path.join(ticket_dir, "tmd.bin"), os.path.join(output_folder, "rvlt.tmd"))
                os.replace(os.path.join(ticket_dir, "ticket.bin"), os.path.join(output_folder, "rvlt.tik"))
            except FileNotFoundError:
                os.replace(os.path.join(ticket_dir, "DATA", "tmd.bin"), os.path.join(output_folder, "rvlt.tmd"))
                os.replace(os.path.join(ticket_dir, "DATA", "ticket.bin"), os.path.join(output_folder, "rvlt.tik"))
            return output_folder

    @staticmethod
    def extract_iso(source_iso: str, output_folder: str) -> str:
        os.makedirs(output_folder, exist_ok=True)
        WiimsISOTools.run(["extract", source_iso, "--dest", output_folder, "--psel", "data,-update", "-ovv"])
        return output_folder

    @staticmethod
    def rebuild_iso(source_folder: str, output_iso: str, use_wiimmfi: bool) -> str:
        args = ["copy", source_folder, "--dest", output_iso, "-ovv", "--links", "--iso"]
        if use_wiimmfi:
            args.append("--wiimmfi")
        WiimsISOTools.run(args)
        return output_iso
