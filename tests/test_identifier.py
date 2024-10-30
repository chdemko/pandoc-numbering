from unittest import TestCase

from pandoc_numbering import Numbered


class IdentifierTest(TestCase):
    def test_identifier(self):
        self.assertEqual(Numbered.identifier("0123   Ê   à"), "e-a")
