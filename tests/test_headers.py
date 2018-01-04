# This Python file uses the following encoding: utf-8

from unittest import TestCase
from panflute import *

import pandoc_numbering

def test_headers():
    markdown = '''
# Title 1

## Subtitle1

# Title 2

## Subtitle 2

# Title 3 {.unnumbered}
'''
    doc = Doc(*convert_text(markdown))
    pandoc_numbering.main(doc)
    assert doc.headers == [2, 1, 0, 0, 0, 0]

