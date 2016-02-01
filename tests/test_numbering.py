from unittest import TestCase

from pandoc_numbering import numbering

def test_numbering():
     assert numbering(
         'Para',
         [{'t': 'Str', 'c': 'Exercice'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '#'}],
         '',
         {}
     ) == {
         't': 'Para',
         'c': [{
             't': 'Span',
             'c': (
                 ['exercice:1', [], []],
                 [{
                     't': 'Strong',
                     'c': [{'t': 'Str', 'c': 'Exercice'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '1'}]
                 }]
             ),
         }]
     }

