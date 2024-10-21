import argparse
from typing import Any, Dict
import sys
import yaml

from anki import notes, cards
from commands import util
from lib import ankicol

import tabulate

parser = argparse.ArgumentParser(add_help=False)
subparsers = parser.add_subparsers(dest="cards_command")
list_parser = subparsers.add_parser("list")
list_parser.add_argument(
    "--yaml", action="store_true", help="Output as YAML", default=False
)
list_parser.add_argument(
    "--note-types", "-t", type=int, nargs="+", help="Note types to list"
)

remove_parser = subparsers.add_parser("remove")
remove_parser.add_argument("cards_ids", nargs="+", type=int)


create_parser = subparsers.add_parser("create")
# create_parser.add_argument("cards_types", nargs="+", type=int)
create_parser.add_argument("notes_ids", nargs="+", type=int)


def card_to_str(card: cards.Card, *, multiline=False) -> str:

    q = util.strip_html(card.question())
    a = util.strip_html(card.answer())

    if multiline:
        return (
            f"card_id: {card.id}"
            f"note_id: {card.nid}\n"
            f"question: {q}\n"
            f"answer: {a}\n"
        )

    return f"card_id: {card.id} note_id: {card.nid} note_type: {card.note_type()['id']} QUESTION: {q} ANSWER:{a}"


def handle_list(acol: ankicol.AnkiCollection, args: argparse.Namespace):
    cards = acol.find_cards("")

    table = []

    for card in cards:

        nt = card.note_type()
        ntid = nt["id"]

        if args.note_types is not None and ntid not in args.note_types:
            continue

        q = util.strip_html(card.question())
        a = util.strip_html(card.answer())[0:25]

        table.append(
            [
                card.id,
                card.nid,
                ntid,
                q,
                a,
            ]
        )

    table.sort(key=lambda x: x[2])

    output = tabulate.tabulate(
        table,
        headers=[
            "card_id",
            "note_id",
            "note_type_id",
            "question",
            "answer",
        ],
    )

    print(output)


def handle_remove(acol: ankicol.AnkiCollection, args: argparse.Namespace):

    if len(args.cards_ids) == 0:
        print("No cards specified")
        return

    acol.col.remove_cards_and_orphaned_notes(args.cards_ids)


def handle_create(acol: ankicol.AnkiCollection, args: argparse.Namespace):

    acol.col.after_note_updates(args.notes_ids, generate_cards=True, mark_modified=True)
    # cts = acol.card_types(cards_types_ids=args.cards_types)

    # for nt, ct in cts:
    #     print(f"note type: {nt['id']} {nt['name']}")

    # note = acol.col.get_note(args.cards_types)

    # print(f"note_id: {note.id}")

    # card = cards.Card(acol.col)
    # card.note_id = note.id

    # acol.col.models.add


def handle_cards(col: ankicol.AnkiCollection, args: Any):
    if args.cards_command is None:
        print("No command specified")
        return

    if args.cards_command == "list":
        return handle_list(col, args)
    elif args.cards_command == "remove":
        return handle_remove(col, args)
    elif args.cards_command == "create":
        return handle_create(col, args)
