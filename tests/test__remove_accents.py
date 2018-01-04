# This Python file uses the following encoding: utf-8
from unittest import TestCase

from pandoc_numbering import Numbered

def test__remove_accents():
    assert Numbered._remove_accents(u'Êà') == 'Ea'


