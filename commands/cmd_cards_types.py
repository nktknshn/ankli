import argparse
from typing import Any, Dict
import sys
import yaml

from anki import cards
from lib import ankicol
import tabulate

parser = argparse.ArgumentParser(add_help=False)
subparsers = parser.add_subparsers(dest="cards_type_command")
list_parser = subparsers.add_parser("list")
list_parser.add_argument(
    "--yaml", action="store_true", help="Output as YAML", default=False
)
list_parser.add_argument(
    "--note-types", "-t", type=int, nargs="+", help="Note types to list"
)

remove_parser = subparsers.add_parser("remove")
remove_parser.add_argument("card_type_ids", nargs="+", type=int)


def handle_list(acol: ankicol.AnkiCollection, args: argparse.Namespace):

    table = []

    for note_type, card_type in acol.card_types():

        if args.note_types is not None and note_type["id"] not in args.note_types:
            continue

        table.append(
            [
                card_type["id"],
                note_type["id"],
                note_type["name"],
                card_type["qfmt"],
                card_type["afmt"],
            ]
        )

    print(
        tabulate.tabulate(
            table,
            headers=["card_type_id", "note_type_id", "name", "qfmt", "afmt"],
            maxcolwidths=[10, 10, 50, 50, 50],
        )
    )


def handle_remove(acol: ankicol.AnkiCollection, args: argparse.Namespace):
    pass


def handle_cards_types(col: ankicol.AnkiCollection, args: Any):
    if args.cards_type_command is None:
        print("No command specified")
        return

    # cards_types = col.card_types()

    if args.cards_type_command == "list":
        return handle_list(col, args)
    elif args.cards_type_command == "remove":
        return handle_remove(col, args)
