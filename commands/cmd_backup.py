import argparse
from typing import Any, Dict
import sys
import yaml

from anki import cards
from lib import ankicol


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("backup_folder", help="Backup folder", type=str)


def handle_backup(acol: ankicol.AnkiCollection, args: Any) -> None:
    res = acol.col.create_backup(
        backup_folder=args.backup_folder, wait_for_completion=True, force=True
    )

    print(res)
