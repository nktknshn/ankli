import sys
import yaml
import argparse
from dataclasses import dataclass
from anki import storage, notes, cards, template

from typing import Any, Callable, Sequence, TypeGuard, TypedDict, cast


@dataclass
class Scheme:
    note_types_dict: dict[str, str]
    # notes_types: list[notes.NotetypeDict]


@dataclass
class CardView:
    id: int
    fields: dict[str, str]


class NoteTypeFieldDictTyped(TypedDict):
    id: int
    name: str
    ord: int
    sticky: bool
    rtl: bool
    font: str
    size: int
    description: str
    plainText: bool
    collapsed: bool
    excludeFromSearch: bool
    tag: str
    preventDeletion: bool


class TemplateDictTyped(TypedDict):
    id: int
    name: str
    qfmt: str
    afmt: str
    did: int


class NotetypeDictTyped(TypedDict):
    """Typed NoteTypeDict"""

    id: notes.NotetypeId
    name: str
    type: int
    mod: int
    usn: int
    sortf: int
    did: int | None
    tmpls: list
    flds: list[NoteTypeFieldDictTyped]
    css: str
    latexPre: str
    latexPost: str
    latexsvg: bool
    req: list
    originalStockKind: int


class AnkiCollection:

    @staticmethod
    def load(path: str) -> storage.Collection:
        return storage.Collection(path)

    def __init__(self, col: storage.Collection):
        self.col = col

    def backup(self, backup_folder: str) -> bool:
        return self.col.create_backup(
            backup_folder=backup_folder,
            wait_for_completion=True,
            force=True,
        )

    def find_cards(self, query: str) -> list[cards.Card]:
        result = []
        cards_ids = self.col.find_cards(query)

        for card_id in cards_ids:
            card = self.col.get_card(card_id)
            result.append(card)

        return result

    def get_note(self, note_id: int) -> notes.Note:
        return self.col.get_note(notes.NoteId(note_id))

    def find_notes(self, query: str) -> list[notes.Note]:
        result = []
        notes_ids = self.col.find_notes(query)

        for note_id in notes_ids:
            note = self.col.get_note(note_id)
            result.append(note)

        return result

    def note_types_with_notes(
        self,
    ) -> list[tuple[NotetypeDictTyped, list[notes.Note]]]:
        result = []

        for note_type in self.get_note_types():
            notes = self.note_type_notes(note_type["id"])
            result.append((note_type, notes))

        return result

    def get_note_types(
        self, note_types_ids: list[int] | None = None
    ) -> list[NotetypeDictTyped]:
        nts = []

        if note_types_ids is None:
            return cast(list[NotetypeDictTyped], self.col.models.all())

        for ntid in note_types_ids:
            nt = self.col.models.get(cast(notes.NotetypeId, ntid))

            if nt is None:
                raise LookupError(f"Note type {ntid} not found")

            nts.append(nt)

        return cast(list[NotetypeDictTyped], nts)

    def note_type_notes(self, ntid: int) -> list[notes.Note]:
        result = []

        for nid in self.col.models.nids(cast(notes.NotetypeId, ntid)):
            note = self.col.get_note(nid)
            result.append(note)

        return result

    def card_types(
        self,
        *,
        cards_types_ids: list[int] | None = None,
        notes_types_ids: list[int] | None = None,
    ) -> list[tuple[NotetypeDictTyped, TemplateDictTyped]]:
        result: list[tuple[NotetypeDictTyped, TemplateDictTyped]] = []

        for note_type in self.get_note_types():

            if notes_types_ids is not None and note_type["id"] not in notes_types_ids:
                continue

            result.extend([(note_type, template) for template in note_type["tmpls"]])

        if cards_types_ids is not None:
            result = [(nt, ct) for nt, ct in result if ct["id"] in cards_types_ids]

        return result

    def scheme(self) -> Scheme:
        tps = self.get_note_types()
        tp = tps[0]

        notes_types = self.get_note_types()

        return Scheme(
            {k: v.__class__.__name__ for k, v in tp.items()},
            # notes_types,
        )

    def cards_by_note_type(self, note_type_id: int) -> list[cards.Card]:
        cards = self.find_cards("")

        return [card for card in cards if card.note_type()["id"] == note_type_id]

    def notes_type_create(self, name: str, fields: list[str]):
        pass

    # def cards_views(self) -> list[CardView]:
    #     cards = self.find_cards("")

    #     for card in cards:
    #         card.type()

    # return [CardView(card.id, card.fields) for card in c]
