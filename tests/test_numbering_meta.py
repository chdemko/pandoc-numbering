# This Python file uses the following encoding: utf-8

from unittest import TestCase
from panflute import *

import pandoc_numbering
from helper import verify_conversion


def test_numbering_classes():
    verify_conversion(
        """
---
pandoc-numbering:
  exercise:
    general:
      classes:
      - myclass
---

Exercise #

Exercise (Title) #
        """,
        """
---
pandoc-numbering:
  exercise:
    general:
      classes:
      - myclass
---

[**Exercise 1**]{#exercise:1 .pandoc-numbering-text .myclass}

[**Exercise 2** *(Title)*]{#exercise:2 .pandoc-numbering-text .myclass}
        """,
    )


def test_numbering_text():
    verify_conversion(
        """
---
pandoc-numbering:
  exercise:
    standard:
      format-text-classic: '**%D %d %n/%c**'
      format-text-title: '**%D %d %n/%c: %T %t**'
---

Exercise #

Exercise (Title) #
        """,
        """
---
pandoc-numbering:
  exercise:
    standard:
      format-text-classic: '**%D %d %n/%c**'
      format-text-title: '**%D %d %n/%c: %T %t**'
---

[**Exercise exercise 1/2**]{#exercise:1 .pandoc-numbering-text .exercise}

[**Exercise exercise 2/2: Title title**]{#exercise:2 .pandoc-numbering-text .exercise}
        """,
    )


def test_numbering_levels():
    verify_conversion(
        """
---
pandoc-numbering: 
  exercise:
    general:
      first-section-level: 2
      last-section-level: 2
---

First chapter
=============

Second chapter
==============

First section
-------------

Second section
--------------

Exercise #

Exercise (Title) #
        """,
        """
---
pandoc-numbering:
  exercise:
    general:
      first-section-level: 2
      last-section-level: 2
---

First chapter
=============

Second chapter
==============

First section
-------------

Second section
--------------

[**Exercise 2.1**]{#exercise:2.2.1 .pandoc-numbering-text .exercise}

[**Exercise 2.2** *(Title)*]{#exercise:2.2.2 .pandoc-numbering-text .exercise}
        """,
    )


def test_numbering_sectioning():
    verify_conversion(
        """
---
pandoc-numbering: 
  exercise:
    general:
      sectioning-levels: '-.+.'
---

First chapter
=============

Second chapter
==============

First section
-------------

Second section
--------------

Exercise #

Exercise (Title) #
        """,
        """
---
pandoc-numbering:
  exercise:
    general:
      sectioning-levels: '-.+.'
---

First chapter
=============

Second chapter
==============

First section
-------------

Second section
--------------

[**Exercise 2.1**]{#exercise:2.2.1 .pandoc-numbering-text .exercise}

[**Exercise 2.2** *(Title)*]{#exercise:2.2.2 .pandoc-numbering-text .exercise}
        """,
    )
