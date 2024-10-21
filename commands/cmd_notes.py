import time
import tempfile
import argparse
import os
from typing import Any, Dict
import sys
import yaml

from anki import notes, decks
from commands import util
from lib import ankicol

import tabulate

parser = argparse.ArgumentParser(add_help=False)
subparsers = parser.add_subparsers(dest="notes_command")
list_parser = subparsers.add_parser("list")

list_parser.add_argument("query", nargs="?", default="")

list_parser.add_argument(
    "--yaml", action="store_true", help="Output as YAML", default=False
)
list_parser.add_argument(
    "--limit-width", "-w", type=int, help="Limit width of output", default=None
)

# list of ints
list_parser.add_argument(
    "--note-types", "-t", type=int, nargs="+", help="Note types to list"
)

list_parser.add_argument(
    "--table-format", "-T", type=str, help="Table format", default="simple"
)

list_parser.add_argument(
    "--table-bordered", "-b", action="store_true", help="Table bordered"
)

list_parser.add_argument(
    "--strip-html",
    "-s",
    action="store_true",
    help="Strip HTML from fields",
    default=False,
)


remove_parser = subparsers.add_parser("remove")
remove_parser.add_argument("note_ids", nargs="+", type=int)

create_parser = subparsers.add_parser("create")
create_parser.add_argument("note_type_id", type=int)

update_parser = subparsers.add_parser("set-field")
update_parser.add_argument("note_id", type=int)
update_parser.add_argument("field", type=int)

edit_parser = subparsers.add_parser("edit")
edit_parser.add_argument("note_id", type=util.int_or_str)

new_parser = subparsers.add_parser("new")
new_parser.add_argument("note_type_id", type=int)


def make_edit_file_content(note: notes.Note) -> str:
    fields = note.items()
    content_dict = {k: v for k, v in fields}

    return yaml.dump(
        content_dict,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )


def handle_new(acol: ankicol.AnkiCollection, args: argparse.Namespace):
    [nt] = acol.get_note_types([args.note_type_id])

    n = notes.Note(acol.col, model=nt["id"])

    acol.col.add_note(n, decks.DeckId(0))

    print(n.id)

    if not note_edit(acol, n.id):
        acol.col.remove_notes([n.id])


def parse_yaml_dict(content: str) -> Any:
    return yaml.safe_load(content)


def read_note_fields(note: notes.Note, fields_dict: Any) -> list[str]:
    result = []

    if not isinstance(fields_dict, dict):
        raise Exception("Invalid YAML. Expected a dictionary.")

    for k, v in fields_dict.items():
        if isinstance(v, list):
            fields_dict[k] = "<ul>"
            for el in v:
                fields_dict[k] += f"<li>{el}</li>"
            fields_dict[k] += "</ul>"
            continue

        if not isinstance(v, str):
            fields_dict[k] = str(v)
            continue

        fields_dict[k] = str(v)

    for field in note.keys():
        if field not in fields_dict:
            raise Exception(f"Unknown field: {field}")

        if not isinstance(fields_dict[field], str):
            raise Exception(f"Field {field} is not a string")

        result.append(fields_dict[field])

    return result


def note_edit(acol: ankicol.AnkiCollection, note_id: notes.NoteId) -> bool:

    note = acol.get_note(note_id)

    with tempfile.TemporaryDirectory() as d:
        f_path = os.path.join(d, f"note.yaml")

        with open(f_path, "w", encoding="utf-8") as f:
            f.write(make_edit_file_content(note))

        while True:
            os.system(f"vim {f_path}")

            with open(f_path, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                parsed_yaml = parse_yaml_dict(content)
                fields_values = read_note_fields(note, parsed_yaml)
            except Exception as e:
                print(e)
                print("Invalid note")
                # sleep for a second
                time.sleep(0.5)
                continue

            # if all fields empty
            if all(v == "" for v in fields_values):
                print("All fields empty, skipping")
                return False

            note.fields = fields_values
            acol.col.update_note(note)

            return True


def handle_edit(acol: ankicol.AnkiCollection, args: argparse.Namespace):

    note_id_or_word = args.note_id

    if isinstance(note_id_or_word, str):
        matching_notes = acol.find_notes(note_id_or_word)

        if len(matching_notes) == 0:
            print(f"No notes found for {note_id_or_word}")
            return

        if len(matching_notes) > 1:
            print(f"Multiple notes found for {note_id_or_word}: {matching_notes}")
            return

        note_id = matching_notes[0].id

    elif isinstance(note_id_or_word, int):
        note_id = notes.NoteId(note_id_or_word)
    else:
        raise Exception("invalid note id")

    note_edit(acol, note_id)


def handle_list(acol: ankicol.AnkiCollection, args: argparse.Namespace):
    matched_notes = acol.find_notes(args.query)
    matched_notes_ids = list(map(lambda n: n.id, matched_notes))

    for nt, notes in acol.note_types_with_notes():
        table = []
        headers = [
            "note_id",
            *map(lambda d: f'({d["ord"]}) {d["name"]}', nt["flds"]),
        ]

        if args.note_types is not None and nt["id"] not in args.note_types:
            continue

        if len(notes) == 0:
            continue

        for note in notes:

            if note.id not in matched_notes_ids:
                continue

            fields = note.fields
            if args.strip_html:
                fields = map(lambda f: util.strip_html(f), fields)

            if args.limit_width is not None:
                fields = map(lambda f: f[: args.limit_width], fields)

            table.append([note.id, *fields])

        if len(table) == 0:
            continue

        print(f"Note type: {nt['id']} ({nt['name']})")
        print(
            tabulate.tabulate(
                table,
                headers=headers,
                maxcolwidths=[10, *map(lambda d: 20, nt["flds"])],
                tablefmt="rounded_grid" if args.table_bordered else args.table_format,
            ),
        )
        print()

    # for note in notes:
    #     print(f"{note.id} {note.mid} {note.fields[:2]}")


def handle_remove(acol: ankicol.AnkiCollection, args: argparse.Namespace):
    acol.col.remove_notes(args.note_ids)


def handle_create(acol: ankicol.AnkiCollection, args: argparse.Namespace):
    note_type = acol.col.models.get(args.note_type_id)

    if note_type is None:
        print(f"note type {args.note_type_id} not found")
        return

    fields = note_type["flds"]

    for field in fields:
        print(f"{field['name']}: {field['ord']}")


def handle_notes(col: ankicol.AnkiCollection, args: Any) -> None:
    if args.notes_command is None:
        print("No command specified")
        return

    notes = col.find_notes("")

    if args.notes_command == "list":
        return handle_list(col, args)
    elif args.notes_command == "remove":
        return handle_remove(col, args)
    elif args.notes_command == "create":
        return handle_create(col, args)
    elif args.notes_command == "edit":
        return handle_edit(col, args)
    elif args.notes_command == "new":
        return handle_new(col, args)
