import argparse
from dataclasses import dataclass
from typing import Any, Dict
from lib import ankicol
from anki import models, notetypes_pb2, notes, decks

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--dry-run", "-d", action="store_true", help="Dry run")


def convert(acol: ankicol.AnkiCollection, src: "Source") -> "Dest":
    return Dest(
        Word=src.Front,
        Front_1=src.Front,
        Back_1=src.Back,
        Def_1=src.Definition,
        Example_1=src.Examples,
        Front_2="",
        Back_2="",
        Def_2="",
    )


def handle_script(acol: ankicol.AnkiCollection, args: Any):

    source_ntid = 1728033131170
    dest_ntid = notes.NotetypeId(1728126797964)
    [dest_nt] = acol.get_note_types([dest_ntid])

    src_notes = acol.note_type_notes(source_ntid)

    dest_note = []

    for note in src_notes:
        src = Source.from_note(note)
        dst = convert(acol, src)
        dest_note.append(dst)

    # for dn in dest_note:
    #     n = notes.Note(acol.col, model=dest_ntid)
    #     n.fields = dn.to_fields_values()
    #     acol.col.add_note(n, decks.DeckId(0))

    print("Done")


@dataclass
class Source:
    id: notes.NoteId
    Front: str
    Back: str
    Pronunciation: str
    Definition: str
    Examples: str
    Notes: str

    @staticmethod
    def from_note(n: notes.Note):
        return Source(
            id=n.id,
            Front=n.fields[0],
            Back=n.fields[1],
            Pronunciation=n.fields[2],
            Definition=n.fields[3],
            Examples=n.fields[4],
            Notes=n.fields[5],
        )


@dataclass
class Dest:
    Word: str
    Front_1: str
    Back_1: str
    Def_1: str
    Example_1: str
    Front_2: str
    Back_2: str
    Def_2: str

    @staticmethod
    def to_dict(d: "Dest") -> Dict[str, str]:
        return {
            "Word": d.Word,
            "Front 1": d.Front_1,
            "Back 1": d.Back_1,
            "Def 1": d.Def_1,
            "Example 1": d.Example_1,
            "Front 2": d.Front_2,
            "Back 2": d.Back_2,
            "Def 2": d.Def_2,
        }

    def to_fields_values(self) -> list[str]:
        return [
            self.Word,
            self.Front_1,
            self.Back_1,
            self.Def_1,
            self.Example_1,
            self.Front_2,
            self.Back_2,
            self.Def_2,
        ]
