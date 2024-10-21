from typing import Any
from lib import ankicol
import argparse


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("arg1", type=int)


def handle_script(acol: ankicol.AnkiCollection, args: Any):
    args = parser.parse_args(args)
    print(args.arg1)