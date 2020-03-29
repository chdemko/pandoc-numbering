# This Python file uses the following encoding: utf-8

from unittest import TestCase

from helper import verify_conversion


class TermTest(TestCase):
    def test_term(self):
        verify_conversion(
            self,
            r"""
Definition #
:   This is the definition
            """,
            r"""
[**Definition 1**]{#definition:1 .pandoc-numbering-text .definition}
:   This is the definition
            """,
        )

    def test_term_title(self):
        verify_conversion(
            self,
            r"""
Definition (This is the title) #
:   This is the definition
            """,
            r"""
[**Definition 1** *(This is the title)*]{#definition:1 .pandoc-numbering-text .definition}
:   This is the definition
            """,
        )
