import argparse
from typing import Any
from lib import ankicol

parser = argparse.ArgumentParser(add_help=False)

parser.add_argument("from_note_type_id", type=int, help="note type id")
parser.add_argument("to_note_type_id", type=int, help="note type id")


SCRIPT_TEMPLATE = """import argparse
from dataclasses import dataclass
from typing import Any, Dict
from lib import ankicol
from anki import models, notetypes_pb2, notes, decks

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--dry-run", "-d", action="store_true", help="Dry run")

def handle_script(acol: ankicol.AnkiCollection, args: Any):

    source_ntid = {{.SourceID}}
    dest_ntid = notes.NotetypeId({{.DestID}})
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


{{.Generated}}
"""


def handle_script(acol: ankicol.AnkiCollection, args: Any):
    """Generate typed from a to b"""

    source_ntid = args.from_note_type_id
    dest_ntid = args.to_note_type_id

    [src_nt, dst_nt] = acol.get_note_types([source_ntid, dest_ntid])

    generated = ""

    dataclass_src = make_source_class(src_nt)
    dataclass_dst = make_dest_class(dst_nt)

    generated += dataclass_src
    generated += "\n"
    generated += dataclass_dst
    generated += "\n\n"

    convert_function = "def convert(acol: ankicol.AnkiCollection, src: Source) -> Dest:\n    return Dest(\n"

    for field in dst_nt["flds"]:
        convert_function += f"        {sp(field['name'])}=\n"

    convert_function += "    )\n"

    generated += convert_function

    result = SCRIPT_TEMPLATE.replace("{{.SourceID}}", str(source_ntid))
    result = result.replace("{{.DestID}}", str(dest_ntid))
    result = result.replace("{{.Generated}}", generated)

    print(result)


def sp(name: str) -> str:
    name = name.replace(" ", "_")
    name = name.replace("+", "_plus")

    return name


def make_source_class(src_nt: ankicol.NotetypeDictTyped) -> str:
    dataclass_src = "@dataclass\n"
    dataclass_src += "class Source:\n"
    dataclass_src += "    id: notes.NoteId\n"

    for field in src_nt["flds"]:
        dataclass_src += f"    {sp(field['name'])}: str\n"

    dataclass_src += "\n"

    dataclass_src += "    @staticmethod\n"
    dataclass_src += "    def from_note(n: notes.Note):\n"
    dataclass_src += "        return Source(\n"
    dataclass_src += "            id=n.id,\n"

    for field in src_nt["flds"]:
        dataclass_src += f"            {sp(field['name'])}=n.fields[{field['ord']}],\n"

    dataclass_src += "        )"

    return dataclass_src


def make_dest_class(dst_nt: ankicol.NotetypeDictTyped) -> str:
    dataclass_dst = "@dataclass\n"
    dataclass_dst += "class Dest:\n"

    for field in dst_nt["flds"]:
        dataclass_dst += f"    {sp(field['name'])}: str\n"

    dataclass_dst += "\n"
    dataclass_dst += "    @staticmethod\n"
    dataclass_dst += "    def to_dict(d: 'Dest') -> Dict[str, str]:\n"
    dataclass_dst += "        return {\n"

    for field in dst_nt["flds"]:
        dataclass_dst += f"            '{field['name']}': d.{sp(field['name'])},\n"

    dataclass_dst += "        }"
    dataclass_dst += "\n"
    dataclass_dst += "\n"

    dataclass_dst += "    def to_fields_values(self) -> list[str]:\n"
    dataclass_dst += f"        return [\n"

    for field in sorted(dst_nt["flds"], key=lambda x: x["ord"]):
        dataclass_dst += f"            self.{sp(field['name'])},\n"

    dataclass_dst += "        ]"

    return dataclass_dst
