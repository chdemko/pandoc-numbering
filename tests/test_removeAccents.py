from unittest import TestCase

from pandoc_numbering import removeAccents

def test_removeAccents():
    assert removeAccents('Êà') == 'Ea'


