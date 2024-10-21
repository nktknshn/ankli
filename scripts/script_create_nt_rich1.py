from typing import Any
from lib import ankicol


def handle_script(acol: ankicol.AnkiCollection, args: Any):

    name = "Rich English Card With Multiple Definitions"

    m = acol.col.models.by_name(name)

    if m:
        print(f"model `{name}` already exists")
        return

    m = acol.col.models.new("Rich English Card With Multiple Definitions")

    f_word = acol.col.models.new_field("Word")

    f_front1 = acol.col.models.new_field("Front 1")
    f_back1 = acol.col.models.new_field("Back 1")
    f_def1 = acol.col.models.new_field("Definition 1")
    f_example1 = acol.col.models.new_field("Example 1")

    f_front2 = acol.col.models.new_field("Front 2")
    f_back2 = acol.col.models.new_field("Back 2")
    f_def2 = acol.col.models.new_field("Definition 2")
    f_example2 = acol.col.models.new_field("Example 2")

    f_front3 = acol.col.models.new_field("Front 3")
    f_back3 = acol.col.models.new_field("Back 3")
    f_def3 = acol.col.models.new_field("Definition 3")
    f_example3 = acol.col.models.new_field("Example 3")

    acol.col.models.add_field(m, f_word)
    acol.col.models.add_field(m, f_front1)
    acol.col.models.add_field(m, f_back1)
    acol.col.models.add_field(m, f_def1)
    acol.col.models.add_field(m, f_example1)

    acol.col.models.add_field(m, f_front2)
    acol.col.models.add_field(m, f_back2)
    acol.col.models.add_field(m, f_def2)
    acol.col.models.add_field(m, f_example2)

    acol.col.models.add_field(m, f_front3)
    acol.col.models.add_field(m, f_back3)
    acol.col.models.add_field(m, f_def3)
    acol.col.models.add_field(m, f_example3)

    templ1 = acol.col.models.new_template("Front 1")
    templ2 = acol.col.models.new_template("Front 2")
    templ3 = acol.col.models.new_template("Front 3")

    templ1["qfmt"] = "{{Front 1}}"
    templ2["qfmt"] = "{{Front 2}}"
    templ3["qfmt"] = "{{Front 3}}"

    templ1["afmt"] = "{{Front 1}}\n\n{{Back 1}}"
    templ2["afmt"] = "{{Front 2}}\n\n{{Back 2}}"
    templ3["afmt"] = "{{Front 3}}\n\n{{Back 3}}"

    acol.col.models.add_template(m, templ1)
    acol.col.models.add_template(m, templ2)
    acol.col.models.add_template(m, templ3)

    acol.col.models.save(m)

    print(f"model id: {m['id']}")
