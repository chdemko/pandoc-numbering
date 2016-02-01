from unittest import TestCase

from pandoc_numbering import toIdentifier

def test_toIdentifier():
    assert toIdentifier('0123   Ê   à') == 'e-a'


