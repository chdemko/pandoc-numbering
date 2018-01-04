# This Python file uses the following encoding: utf-8

from unittest import TestCase
from panflute import *

import pandoc_numbering

def test_sharp_sharp():
    definition = '''
Example ##
'''
    doc = Doc(*convert_text(definition))
    pandoc_numbering.main(doc)
    assert doc.content[0].content[-1].text == '#'

