from dataclasses import field
from typing import Any
from lib import ankicol
from anki import notes, models


def handle_script(acol: ankicol.AnkiCollection, args: Any):
    """Add Exmple 2"""
    nt_id = notes.NotetypeId(1728126797964)

    note_type = acol.get_note_types([nt_id])[0]

    field1 = acol.col.models.new_field("Example 2")
    field1["ord"] = len(note_type["flds"])
    field1["font"] = "Liberation Sans"
    field1["size"] = 20

    acol.col.models.add_field(
        notes.NotetypeDict(note_type),
        models.FieldDict(field1),
    )

    # save the note type
    acol.col.models.save(notes.NotetypeDict(note_type))
