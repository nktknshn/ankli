import argparse
from typing import Any

from lib import ankicol

parser = argparse.ArgumentParser(add_help=False)
subparsers = parser.add_subparsers(dest="script_command")

run_parser = subparsers.add_parser("run")
run_parser.add_argument("script", help="script file")
# run_parser.add_argument("--args", nargs="*", help="script arguments")
run_parser.add_argument("remaining", nargs=argparse.REMAINDER)


def handle_script(acol: ankicol.AnkiCollection, args: Any) -> None:

    with open(args.script, "r") as f:
        script_code = f.read()

    script_code += "\n\n"
    script_code += "handle_script(acol, args)"

    exec(script_code, {"acol": acol, "args": args.remaining})
