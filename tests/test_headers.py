# This Python file uses the following encoding: utf-8

from unittest import TestCase

from panflute import Doc, convert_text

import pandoc_numbering


class HeadersTest(TestCase):
    def test_headers(self):
        markdown = r"""
# Title 1

## Subtitle1

# Title 2

## Subtitle 2

# Title 3 {.unnumbered}
        """
        doc = Doc(*convert_text(markdown))
        pandoc_numbering.main(doc)
        self.assertEqual(doc.headers, [2, 1, 0, 0, 0, 0])
