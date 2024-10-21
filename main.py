import os
import sys
import yaml
import argparse
from dataclasses import dataclass
from anki import storage, notes, cards, template
from lib import ankicol
from commands import (
    cmd_backup,
    cmd_cards,
    cmd_notes_types,
    cmd_cards_types,
    cmd_notes,
    cmd_script,
    cmd_sync,
)

from typing import Any, Callable, TypeGuard


def is_exception(obj: Any) -> TypeGuard[Exception]:
    return isinstance(obj, Exception)


def args_parser():
    parser = argparse.ArgumentParser(description="ANKI CLI")

    # -s storage_path
    parser.add_argument(
        "-s",
        "--storage-path",
        help="Path to Anki2 storage (env var ANKI2_STORAGE_PATH)",
        default=os.environ.get("ANKI2_STORAGE_PATH"),
        dest="storage_path",
    )

    subparsers = parser.add_subparsers(dest="command")
    notes_type_parser = subparsers.add_parser(
        "notes-types", parents=[cmd_notes_types.parser]
    )
    card_type_parser = subparsers.add_parser(
        "cards-types", parents=[cmd_cards_types.parser]
    )
    cards_parser = subparsers.add_parser("cards", parents=[cmd_cards.parser])
    notes_parser = subparsers.add_parser("notes", parents=[cmd_notes.parser])
    scheme_parser = subparsers.add_parser("scheme")
    script_parser = subparsers.add_parser("script", parents=[cmd_script.parser])
    sync_parser = subparsers.add_parser("sync", parents=[cmd_sync.parser])
    backup_parser = subparsers.add_parser("backup", parents=[cmd_backup.parser])

    return parser


def handle_notes(col: ankicol.AnkiCollection, args: Any):
    notes = col.find_notes("")

    for note in notes:
        print(note.fields)


def handle_scheme(col: ankicol.AnkiCollection, args: Any):
    scheme = col.scheme()

    # print(f"note types: {scheme.note_types_dict}")
    print("note types:")

    for key, value in scheme.note_types_dict.items():
        print(f"    {key}: {value}")


def print_card(c: cards.Card):
    print(f"card: {c.id}")
    print(f"note: {c.note()}")
    print(f"question: {c.question()}")
    print(f"answer: {c.answer()}")


def main():
    parser = args_parser()
    args = parser.parse_args()

    storage_path = args.storage_path

    if storage_path is None:
        print("ANKI2_STORAGE_PATH not set or missing -s argument")
        sys.exit(1)

    if args.command == "notes-types":
        handle_command(storage_path, cmd_notes_types.handle_notes_types, args)
    elif args.command == "cards-types":
        handle_command(storage_path, cmd_cards_types.handle_cards_types, args)
    elif args.command == "notes":
        handle_command(storage_path, cmd_notes.handle_notes, args)
    elif args.command == "cards":
        handle_command(storage_path, cmd_cards.handle_cards, args)
    elif args.command == "scheme":
        handle_command(storage_path, handle_scheme, args)
    elif args.command == "script":
        handle_command(storage_path, cmd_script.handle_script, args)
    elif args.command == "sync":
        handle_command(storage_path, cmd_sync.handle_sync, args)
    elif args.command == "backup":
        handle_command(storage_path, cmd_backup.handle_backup, args)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


def handle_command(
    collection_path: str,
    command: Callable[[ankicol.AnkiCollection, Any], None],
    args: Any,
):
    col = ankicol.AnkiCollection.load(collection_path)
    acol = ankicol.AnkiCollection(col)

    return command(acol, args)


if __name__ == "__main__":
    main()
