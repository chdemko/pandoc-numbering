# This Python file uses the following encoding: utf-8
from unittest import TestCase

from pandoc_numbering import removeAccents

def test_removeAccents():
    assert removeAccents('Êà') == 'Ea'


