import re


def remove_style_block(text: str) -> str:
    """Remove style block from text"""
    return re.sub(r"<style>.*?</style>", "", text, flags=re.DOTALL)


def remove_html_tags(text: str) -> str:
    """Remove html tags from text"""
    return re.compile(r"<.*?>").sub("", text)


# re.DOTALL. By default, the dot matches any character except for newline.


def strip_html(text: str) -> str:

    no_style = remove_style_block(text)
    hr_to_dashes = re.sub(r"<hr.*?>", "---", no_style, flags=re.DOTALL)
    no_html = remove_html_tags(hr_to_dashes)
    no_newlines = re.sub(r"\n+", " \\\\n ", no_html, flags=re.DOTALL)

    return no_newlines


def int_or_str(val: str) -> int | str:
    try:
        return int(val)
    except ValueError:
        return val
