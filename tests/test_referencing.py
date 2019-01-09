# This Python file uses the following encoding: utf-8

from unittest import TestCase
from panflute import *

import pandoc_numbering
from helper import verify_conversion


def test_referencing_standard():
    verify_conversion(
        """
Header
======

Section
-------

Exercise (First title) -.+.#exercise:first

Exercise (Second title) -.+.#exercise:second

See [%D %d %T %t %g %s %n # %c](#exercise:first)

See [%D %d %T %t %g %s %n # %c](#exercise:second)
        """,
        """
Header
======

Section
-------

[**Exercise 1.1** *(First title)*]{#exercise:first .pandoc-numbering-text .exercise}

[**Exercise 1.2** *(Second title)*]{#exercise:second .pandoc-numbering-text .exercise}

See [Exercise exercise First title first title 1.1.1 1.1 1.1 1.1 2](#exercise:first)

See [Exercise exercise Second title second title 1.1.2 1.1 1.2 1.2 2](#exercise:second)
        """,
    )


def test_referencing_latex():
    verify_conversion(
        """
Title
=====

Exercise -.#first

Exercise (Title) -.#second

See [%D %d %T %t %g %s %n # %c %p](#exercise:first)

See [%D %d %T %t %g %s %n # %c %p](#exercise:second)
        """,
        """
Title
=====

\\phantomsection\\addcontentsline{exercise}{exercise}{\\protect\\numberline {1.1}{\\ignorespaces {Exercise}}}[\\label{exercise:first}**Exercise 1**]{#exercise:first .pandoc-numbering-text .exercise}

\\phantomsection\\addcontentsline{exercise}{exercise}{\\protect\\numberline {1.2}{\\ignorespaces {Title}}}[\\label{exercise:second}**Exercise 2** *(Title)*]{#exercise:second .pandoc-numbering-text .exercise}

See [Exercise exercise 1.1 1 1 1 2 \pageref{exercise:first}](#exercise:first)

See [Exercise exercise Title title 1.2 1 2 2 2 \pageref{exercise:second}](#exercise:second)
        """,
        "latex",
    )
