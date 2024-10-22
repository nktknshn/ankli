import argparse
from typing import Any

from lib import ankicol

parser = argparse.ArgumentParser(add_help=False)
subparsers = parser.add_subparsers(dest="script_command")

run_parser = subparsers.add_parser("run")
run_parser.add_argument("script", help="script file")
run_parser.add_argument("remaining", nargs=argparse.REMAINDER)


def handle_script(acol: ankicol.AnkiCollection, args: Any) -> None:

    script_code = "parser = None\n\n"

    with open(args.script, "r") as f:
        script_code += f.read()

    script_code += "\n\n"
    script_code += "if parser is not None:\n"
    script_code += "    args = parser.parse_args(remaining)\n"
    script_code += "\n\n"
    script_code += "handle_script(acol, args)"

    exec(script_code, {"acol": acol, "remaining": args.remaining, "args": args})
