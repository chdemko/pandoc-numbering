from unittest import TestCase

from pandoc_numbering import Numbered


class AccentTest(TestCase):
    def test__remove_accents(self):
        self.assertEqual(Numbered._remove_accents("Êà"), "Ea")
