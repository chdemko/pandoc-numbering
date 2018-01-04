# This Python file uses the following encoding: utf-8
from unittest import TestCase

from pandoc_numbering import Numbered

def test__identifier():
    assert Numbered._identifier(u'0123   Ê   à') == 'e-a'


