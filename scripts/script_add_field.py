import argparse
from dataclasses import field
from typing import Any
from lib import ankicol
from anki import notes, models

parser = argparse.ArgumentParser(add_help=False)

parser.add_argument("note_type_id", type=int, help="note type id")
parser.add_argument("field_name", type=str, help="field name")


def handle_script(acol: ankicol.AnkiCollection, args: Any):
    """Add Exmple 2"""

    print(f"note type id: {args.note_type_id}")
    print(f"field name: {args.field_name}")

    nt_id = notes.NotetypeId(args.note_type_id)

    note_type = acol.get_note_types([nt_id])[0]

    field1 = acol.col.models.new_field(args.field_name)

    field1["ord"] = len(note_type["flds"])
    field1["font"] = "Liberation Sans"
    field1["size"] = 20

    acol.col.models.add_field(
        notes.NotetypeDict(note_type),
        models.FieldDict(field1),
    )

    # save the note type
    acol.col.models.save(notes.NotetypeDict(note_type))
