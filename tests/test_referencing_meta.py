# This Python file uses the following encoding: utf-8

from unittest import TestCase
from panflute import *

import pandoc_numbering
from helper import verify_conversion


def test_referencing_link_standard():
    verify_conversion(
        """
---
pandoc-numbering:
  exercise:
    general:
      cite-shortcut: True
    standard:
      format-link-classic: '**%D %d %g %s %n %c**' 
      format-link-title: '**%D %d %T %t %g %s %n %c**' 
---

Title
=====

Exercise -.#first

Exercise (Title) -.#second

See @exercise:first

See @exercise:second
        """,
        """
---
pandoc-numbering:
  exercise:
    general:
      cite-shortcut: True
    standard:
      format-link-classic: '**%D %d %g %s %n %c**'
      format-link-title: '**%D %d %T %t %g %s %n %c**'
---

Title
=====

[**Exercise 1**]{#exercise:first .pandoc-numbering-text .exercise}

[**Exercise 2** *(Title)*]{#exercise:second .pandoc-numbering-text .exercise}

See [[**Exercise exercise 1.1 1 1 2**]{.pandoc-numbering-link .exercise}](#exercise:first "Exercise 1")

See [[**Exercise exercise Title title 1.2 1 2 2**]{.pandoc-numbering-link .exercise}](#exercise:second "Exercise 2 (Title)")
        """,
    )


def test_referencing_link_latex():
    verify_conversion(
        """
---
pandoc-numbering:
  exercise:
    general:
      cite-shortcut: True
    latex:
      format-link-classic: '**%D %d %g %s %n %p**'
      format-link-title: '**%D %d %T %t %g %s %n %p**'
---

Title
=====

Exercise -.#first

Exercise (Title) -.#second

See @exercise:first

See @exercise:second
        """,
        """
---
pandoc-numbering:
  exercise:
    general:
      cite-shortcut: True
    latex:
      format-link-classic: '**%D %d %g %s %n %p**'
      format-link-title: '**%D %d %T %t %g %s %n %p**'
---

Title
=====

\\phantomsection\\addcontentsline{exercise}{exercise}{\\protect\\numberline {1.1}{\\ignorespaces {Exercise}}}[\\label{exercise:first}**Exercise 1**]{#exercise:first .pandoc-numbering-text .exercise}

\\phantomsection\\addcontentsline{exercise}{exercise}{\\protect\\numberline {1.2}{\\ignorespaces {Title}}}[\\label{exercise:second}**Exercise 2** *(Title)*]{#exercise:second .pandoc-numbering-text .exercise}

See [[**Exercise exercise 1.1 1 1 \\pageref{exercise:first}**]{.pandoc-numbering-link .exercise}](#exercise:first "Exercise 1")

See [[**Exercise exercise Title title 1.2 1 2 \\pageref{exercise:second}**]{.pandoc-numbering-link .exercise}](#exercise:second "Exercise 2 (Title)")
        """,
        "latex",
    )


def test_referencing_caption_standard():
    verify_conversion(
        """
---
pandoc-numbering:
  exercise:
    general:
      cite-shortcut: True
    standard:
      format-caption-classic: '%D %d %g %s %n %c'
      format-caption-title: '%D %d %T %t %g %s %n %c'
---

Title
=====

Exercise -.#first

Exercise (Title) -.#second

See @exercise:first

See @exercise:second
        """,
        """
---
pandoc-numbering:
  exercise:
    general:
      cite-shortcut: True
    standard:
      format-caption-classic: '\%D %d %g %s %n %c'
      format-caption-title: '\%D %d %T %t %g %s %n %c'
---

Title
=====

[**Exercise 1**]{#exercise:first .pandoc-numbering-text .exercise}

[**Exercise 2** *(Title)*]{#exercise:second .pandoc-numbering-text .exercise}

See [[Exercise 1]{.pandoc-numbering-link .exercise}](#exercise:first "Exercise exercise 1.1 1 1 2")

See [[Exercise 2 (Title)]{.pandoc-numbering-link .exercise}](#exercise:second "Exercise exercise Title title 1.2 1 2 2")
        """,
    )


def test_referencing_caption_latex():
    verify_conversion(
        """
---
pandoc-numbering:
  exercise:
    general:
      cite-shortcut: True
    latex:
      format-caption-classic: '%D %d %g %s %n %c %p'
      format-caption-title: '%D %d %T %t %g %s %n %c %p'
---

Title
=====

Exercise -.#first

Exercise (Title) -.#second

See @exercise:first

See @exercise:second
        """,
        """
---
pandoc-numbering:
  exercise:
    general:
      cite-shortcut: True
    latex:
      format-caption-classic: '\%D %d %g %s %n %c %p'
      format-caption-title: '\%D %d %T %t %g %s %n %c %p'
---

Title
=====

\\phantomsection\\addcontentsline{exercise}{exercise}{\\protect\\numberline {1.1}{\\ignorespaces {Exercise}}}[\\label{exercise:first}**Exercise 1**]{#exercise:first .pandoc-numbering-text .exercise}

\\phantomsection\\addcontentsline{exercise}{exercise}{\\protect\\numberline {1.2}{\\ignorespaces {Title}}}[\\label{exercise:second}**Exercise 2** *(Title)*]{#exercise:second .pandoc-numbering-text .exercise}

See [[Exercise 1]{.pandoc-numbering-link .exercise}](#exercise:first "Exercise exercise 1.1 1 1 2 \pageref{exercise:first}")

See [[Exercise 2 (Title)]{.pandoc-numbering-link .exercise}](#exercise:second "Exercise exercise Title title 1.2 1 2 2 \pageref{exercise:second}")
        """,
        "latex",
    )
