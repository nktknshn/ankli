import argparse
import os
from typing import Any, Dict, TypedDict
import sys
import yaml
import tabulate
import tempfile

from anki import notes
from lib import ankicol

parser = argparse.ArgumentParser(add_help=False)
subparsers = parser.add_subparsers(dest="notes_type_command")
list_parser = subparsers.add_parser("list")
list_parser.add_argument(
    "--yaml", action="store_true", help="Output as YAML", default=False
)

list_parser.add_argument(
    "--notes-types",
    "-t",
    nargs="+",
    type=int,
    help="Note types to show",
)

list_parser.add_argument(
    "--exclude-empty",
    "-e",
    action="store_true",
    help="Exclude note types without notes",
    default=False,
)

list_parser.add_argument(
    "--long",
    "-l",
    action="store_true",
    help="Show full info about",
    default=False,
)

remove_parser = subparsers.add_parser("remove")
remove_parser.add_argument("note_type_ids", nargs="+", type=int)

edit_parser = subparsers.add_parser("edit")
edit_parser.add_argument("note_type_id", type=int)

new_parser = subparsers.add_parser("new")
new_parser.add_argument("name", type=str)


def handle_edit(acol: ankicol.AnkiCollection, args: argparse.Namespace):
    # nt_id = notes.NotetypeId(args.note_type_id)
    print("Not implemented")


NEW_TYPE_TEMPLATE = """Fields:
  - 
  - 
Cards:
  - Name: 
    Front: "{{}}"
    Back: "{{}}"
"""


class TemplateDictCardTyped(TypedDict):
    Name: str
    Front: str
    Back: str


class TemplateDictTyped(TypedDict):
    Fields: list[str]
    Cards: list[TemplateDictCardTyped]


def validate_dict(d: Any) -> str | TemplateDictTyped:

    if not isinstance(d, dict):
        return "Invalid yaml. Expected a dictionary."

    flds = d.get("Fields")

    if flds is None:
        print("No Fields found")

    if not isinstance(flds, list):
        return "Fields must be a list"

    if len(flds) < 2:
        return "At least 2 fields required"

    cards = d.get("Cards")

    if cards is None:
        return "No Cards found"

    if not isinstance(cards, list):
        return "Cards must be a list"

    if len(cards) < 1:
        return "At least 1 card required"

    for card in cards:
        if not isinstance(card, dict):
            return "Cards must be a list of dicts"

        if "Name" not in card:
            return "Cards must have a Name"

        if len(card["Name"].strip()) < 1:
            return "Cards must have a Name"

        if "Front" not in card:
            return "Cards must have a Front"

        if len(card["Front"].strip()) < 1:
            return "Cards must have a Front"

        if "Back" not in card:
            return "Cards must have a Back"

        if len(card["Back"].strip()) < 1:
            return "Cards must have a Back"

    return TemplateDictTyped(Fields=flds, Cards=cards)


def handle_new(acol: ankicol.AnkiCollection, args: argparse.Namespace):

    if acol.col.models.by_name(args.name):
        print(f"model `{args.name}` already exists")
        return

    with tempfile.TemporaryDirectory() as d:
        f_path = os.path.join(d, "note-type.yaml")
        # open as text file

        with open(f_path, "w", encoding="utf-8") as fname:
            fname.write(NEW_TYPE_TEMPLATE)

        while True:
            os.system(f"vim {f_path}")

            with open(f_path, "r", encoding="utf-8") as fname:
                content = fname.read()

            try:
                d = yaml.safe_load(content)
            except Exception as e:
                print(e)
                print("Invalid yaml")
                input("Press enter")
                continue

            td = validate_dict(d)

            if isinstance(td, str):
                print("Error: " + td)
                input("Press enter")
                continue

            break

    # print(td)

    if len(td["Fields"]) == 0:
        print("No fields found")
        return

    m = acol.col.models.new(args.name)

    for fname in td["Fields"]:
        fname = fname.strip()
        if not fname:
            continue

        f = acol.col.models.new_field(fname)
        acol.col.models.add_field(m, f)

    for card in td["Cards"]:
        name = card["Name"].strip()
        templ1 = acol.col.models.new_template(name)
        templ1["qfmt"] = card["Front"]
        templ1["afmt"] = card["Back"]
        acol.col.models.add_template(m, templ1)

    acol.col.models.save(m)


def handle_list_table_long(acol: ankicol.AnkiCollection, args: argparse.Namespace):
    table = []

    notes_types = acol.note_types_with_notes()

    for nt, notes in notes_types:

        if args.exclude_empty and len(notes) == 0:
            continue

        if args.notes_types and nt["id"] not in args.notes_types:
            continue

        table = []
        print(f"Note type: {nt['id']} ({nt['name']})")

        for f in nt["flds"]:
            table.append(
                [
                    f["id"],
                    f["name"],
                    f["ord"],
                    f["sticky"],
                    f["rtl"],
                    f["font"],
                    f["size"],
                    f["description"],
                    f["plainText"],
                    f["collapsed"],
                    f["excludeFromSearch"],
                    f["tag"],
                    f["preventDeletion"],
                ]
            )

        print(
            tabulate.tabulate(
                table,
                headers=[
                    "id",
                    "name",
                    "ord",
                    "sticky",
                    "rtl",
                    "font",
                    "size",
                    "description",
                    "plainText",
                    "collapsed",
                    "excludeFromSearch",
                    "tag",
                    "preventDeletion",
                ],
                tablefmt="rounded_grid",
            )
        )
        print()


def handle_list_table(acol: ankicol.AnkiCollection, args: argparse.Namespace):

    table = []

    notes_types = acol.note_types_with_notes()

    for nt, notes in notes_types:

        if args.exclude_empty and len(notes) == 0:
            continue

        fields = nt["flds"]
        fields_names = [f["name"] for f in fields]
        table.append(
            [
                nt["id"],
                nt["name"],
                len(notes),
                ", ".join(fields_names),
            ]
        )

    output = tabulate.tabulate(
        table,
        headers=["note_type_id", "name", "n", "fields"],
        maxcolwidths=[10, 50, 10, 60],
    )

    print(output)


def handle_list(acol: ankicol.AnkiCollection, args: argparse.Namespace):
    handle_list_table(acol, args)


def handle_remove(acol: ankicol.AnkiCollection, args: argparse.Namespace):
    nt_ids: list[notes.NotetypeId] = args.note_type_ids

    for nt_id in nt_ids:
        acol.col.models.remove(nt_id)


def handle_notes_types(col: ankicol.AnkiCollection, args: Any):
    if args.notes_type_command is None:
        print("No command specified")
        return

    if args.notes_type_command == "list":

        if args.long:
            return handle_list_table_long(col, args)

        return handle_list(col, args)
    elif args.notes_type_command == "remove":
        return handle_remove(col, args)
    elif args.notes_type_command == "edit":
        return handle_edit(col, args)
    elif args.notes_type_command == "new":
        return handle_new(col, args)
