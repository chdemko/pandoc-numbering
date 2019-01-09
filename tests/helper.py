# This Python file uses the following encoding: utf-8

from panflute import *

import pandoc_numbering


def conversion(markdown, format="markdown"):
    doc = convert_text(markdown, standalone=True)
    doc.format = format
    pandoc_numbering.main(doc)
    return doc


def verify_conversion(markdown, expected, format="markdown"):
    doc = conversion(markdown, format)
    text = convert_text(
        doc,
        input_format="panflute",
        output_format="markdown",
        extra_args=["--wrap=none"],
        standalone=True,
    )
    debug("**computed**")
    debug(text.strip())
    debug("**expected**")
    debug(expected.strip())
    assert text.strip() == expected.strip()
