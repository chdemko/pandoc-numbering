# This Python file uses the following encoding: utf-8

from unittest import TestCase
from panflute import *

import pandoc_numbering
from helper import verify_conversion


def test_para_none():
    verify_conversion("Not an example", "Not an example")


def test_para():
    verify_conversion(
        """
Example #

Example #
        """,
        """
[**Example 1**]{#example:1 .pandoc-numbering-text .example}

[**Example 2**]{#example:2 .pandoc-numbering-text .example}
        """,
    )


def test_para_title():
    verify_conversion(
        """
Example (This is the first title) #

Example (This is the second title) #
        """,
        """
[**Example 1** *(This is the first title)*]{#example:1 .pandoc-numbering-text .example}

[**Example 2** *(This is the second title)*]{#example:2 .pandoc-numbering-text .example}
        """,
    )


def test_para_prefix_single():
    verify_conversion(
        "Example #ex:", "[**Example 1**]{#ex:1 .pandoc-numbering-text .ex}"
    )


def test_para_double():
    verify_conversion(
        """
Example #

Example #
        """,
        """
[**Example 1**]{#example:1 .pandoc-numbering-text .example}

[**Example 2**]{#example:2 .pandoc-numbering-text .example}
        """,
    )


def test_para_sectioning():
    verify_conversion(
        """
First chapter
=============

Second chapter
==============

First section
-------------

Second section
--------------

Exercise -.+.#
        """,
        """
First chapter
=============

Second chapter
==============

First section
-------------

Second section
--------------

[**Exercise 2.1**]{#exercise:2.2.1 .pandoc-numbering-text .exercise}
        """,
    )


def test_para_numbering_hidden():
    verify_conversion(
        """
First chapter
=============

Exercise -.#exercise:one

Exercise -.#

Second chapter
==============

Exercise -.#

Exercise -.#

Exercice #
        """,
        """
First chapter
=============

[**Exercise 1**]{#exercise:one .pandoc-numbering-text .exercise}

[**Exercise 2**]{#exercise:1.2 .pandoc-numbering-text .exercise}

Second chapter
==============

[**Exercise 1**]{#exercise:2.1 .pandoc-numbering-text .exercise}

[**Exercise 2**]{#exercise:2.2 .pandoc-numbering-text .exercise}

[**Exercice 1**]{#exercice:1 .pandoc-numbering-text .exercice}
        """,
    )


def test_para_sectioning_unnumbered():
    verify_conversion(
        """
Unnumbered chapter {#unnumbered-chapter .unnumbered}
==================

Exercise +.#
        """,
        """
Unnumbered chapter {#unnumbered-chapter .unnumbered}
==================

[**Exercise 0.1**]{#exercise:0.1 .pandoc-numbering-text .exercise}
        """,
    )


def test_para_numbering_level():
    verify_conversion(
        """
Exercise +.+.#

First chapter
=============

First section
-------------

Exercise +.+.#

Exercise +.+.#

Second section
--------------

Exercise +.+.#
        """,
        """
[**Exercise 0.0.1**]{#exercise:0.0.1 .pandoc-numbering-text .exercise}

First chapter
=============

First section
-------------

[**Exercise 1.1.1**]{#exercise:1.1.1 .pandoc-numbering-text .exercise}

[**Exercise 1.1.2**]{#exercise:1.1.2 .pandoc-numbering-text .exercise}

Second section
--------------

[**Exercise 1.2.1**]{#exercise:1.2.1 .pandoc-numbering-text .exercise}
        """,
    )


def test_numbering_latex():
    verify_conversion(
        """
Exercise (Equation $a=b$) #
        """,
        """
\\phantomsection\\addcontentsline{exercise}{exercise}{\\protect\\numberline {1}{\\ignorespaces {Equation \(a=b\)}}}[\\label{exercise:1}**Exercise 1** *(Equation $a=b$)*]{#exercise:1 .pandoc-numbering-text .exercise}
        """,
        "latex",
    )
