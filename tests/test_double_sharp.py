# This Python file uses the following encoding: utf-8

from unittest import TestCase

from panflute import Doc, convert_text

import pandoc_numbering


class SharpTest(TestCase):
    def test_sharp_sharp(self):
        definition = r"Example ##"
        doc = Doc(*convert_text(definition))
        pandoc_numbering.main(doc)
        self.assertEqual(doc.content[0].content[-1].text, "#")
