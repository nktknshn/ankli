from typing import Any
from lib import ankicol

# from anki import models, notetypes_pb2, notes


def sp(name: str) -> str:
    return name.replace(" ", "_")


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


def handle_script(acol: ankicol.AnkiCollection, args: Any):
    """Generate typed from a to b"""

    source_ntid = 1728033131170
    dest_ntid = 1728126797964

    [src_nt, dst_nt] = acol.get_note_types([source_ntid, dest_ntid])

    print(src_nt["id"])
    print(dst_nt["id"])

    dataclass_src = make_source_class(src_nt)
    dataclass_dst = make_dest_class(dst_nt)

    print()
    print(dataclass_src)
    print()
    print(dataclass_dst)

    convert_function = "def convert(acol: ankicol.AnkiCollection, src: Source) -> Dest:\n    return Dest(\n"

    for field in dst_nt["flds"]:
        convert_function += f"        {sp(field['name'])}=\n"

    convert_function += "    )\n"

    print()
    print(convert_function)
