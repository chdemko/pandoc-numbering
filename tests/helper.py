from panflute import convert_text

import pandoc_numbering


def conversion(markdown, format="markdown"):
    doc = convert_text(markdown, standalone=True)
    doc.format = format
    pandoc_numbering.main(doc)
    return doc


def verify_conversion(test, markdown, expected, format="markdown"):
    doc = conversion(markdown, format)
    text = convert_text(
        doc,
        input_format="panflute",
        output_format="markdown",
        extra_args=["--wrap=none"],
        standalone=True,
    )
    print(text.strip())
    print(expected.strip())
    test.assertEqual(text.strip(), expected.strip())
