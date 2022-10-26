# This Python file uses the following encoding: utf-8
from unittest import TestCase

from pandoc_numbering import Numbered


class IdentifierTest(TestCase):
    def test__identifier(self):
        self.assertEqual(Numbered._identifier("0123   Ê   à"), "e-a")
