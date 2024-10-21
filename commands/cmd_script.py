import argparse
from typing import Any

from lib import ankicol

parser = argparse.ArgumentParser(add_help=False)
subparsers = parser.add_subparsers(dest="script_command")
run_parser = subparsers.add_parser("run")
run_parser.add_argument("script", help="script file")


def handle_script(acol: ankicol.AnkiCollection, args: Any) -> None:
    # exec args.script
    with open(args.script, "r") as f:
        script_code = f.read()

    code = script_code
    code += "\n\n"
    code += "handle_script(acol, args)"

    exec(
        code,
        {
            "acol": acol,
            "args": args,
        },
    )
