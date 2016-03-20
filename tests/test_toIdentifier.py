# This Python file uses the following encoding: utf-8
from unittest import TestCase

from pandoc_numbering import toIdentifier

def test_toIdentifier():
    assert toIdentifier(u'0123   Ê   à') == 'e-a'


