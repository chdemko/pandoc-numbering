# This Python file uses the following encoding: utf-8

from unittest import TestCase
from panflute import *

import pandoc_numbering

from helper import verify_conversion

def test_term():
    verify_conversion(
'''
Definition #
:   This is the definition
''',
'''
[**Definition 1**]{#definition:1 .pandoc-numbering-text .definition}
:   This is the definition
''')

def test_term_title():
    verify_conversion(
'''
Definition (This is the title) #
:   This is the definition
''',
'''
[**Definition 1** *(This is the title)*]{#definition:1 .pandoc-numbering-text .definition}
:   This is the definition
''')

