from unittest import TestCase

from .helper import verify_conversion


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
[]{#definition:this-is-the-title}[**Definition 1** *(This is the title)*]{#definition:1 .pandoc-numbering-text .definition}
:   This is the definition
            """,
        )

    def test_term_issues_13(self):
        # See https://github.com/chdemko/pandoc-numbering/issues/13
        verify_conversion(
            self,
            """
Assumption #big

:   Big assumption

Lemma #

:   A random lemma

Lemma #

:   A random lemma

Now we derive a result which uses [Assumption #](#assumption:big).

Lemma #

:   Under [Assumption #](#assumption:big), we have ... 
            """,
            """
[]{#assumption:1}[**Assumption 1**]{#assumption:big .pandoc-numbering-text .assumption}

:   Big assumption

[**Lemma 1**]{#lemma:1 .pandoc-numbering-text .lemma}

:   A random lemma

[**Lemma 2**]{#lemma:2 .pandoc-numbering-text .lemma}

:   A random lemma

Now we derive a result which uses [Assumption 1](#assumption:big).

[**Lemma 3**]{#lemma:3 .pandoc-numbering-text .lemma}

:   Under [Assumption 1](#assumption:big), we have ...
            """,
        )
