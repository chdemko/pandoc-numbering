from unittest import TestCase

from .helper import verify_conversion


class NumberingTests(TestCase):
    def test_numbering_classes(self):
        verify_conversion(
            self,
            r"""
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
            r"""
---
pandoc-numbering:
  exercise:
    general:
      classes:
      - myclass
---

[**Exercise 1**]{#exercise:1 .pandoc-numbering-text .myclass}

[]{#exercise:title}[**Exercise 2** *(Title)*]{#exercise:2 .pandoc-numbering-text .myclass}
            """,
        )

    def test_numbering_text(self):
        verify_conversion(
            self,
            r"""
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
            r"""
---
pandoc-numbering:
  exercise:
    standard:
      format-text-classic: "**%D %d %n/%c**"
      format-text-title: "**%D %d %n/%c: %T %t**"
---

[**Exercise exercise 1/2**]{#exercise:1 .pandoc-numbering-text .exercise}

[]{#exercise:title}[**Exercise exercise 2/2: Title title**]{#exercise:2 .pandoc-numbering-text .exercise}
            """,
        )

    def test_numbering_levels(self):
        verify_conversion(
            self,
            r"""
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
            r"""
---
pandoc-numbering:
  exercise:
    general:
      first-section-level: 2
      last-section-level: 2
---

# First chapter

# Second chapter

## First section

## Second section

[]{#exercise:second-chapter.second-section.1}[**Exercise 2.1**]{#exercise:2.2.1 .pandoc-numbering-text .exercise}

[]{#exercise:second-chapter.second-section.title}[**Exercise 2.2** *(Title)*]{#exercise:2.2.2 .pandoc-numbering-text .exercise}
            """,
        )

    def test_numbering_sectioning(self):
        verify_conversion(
            self,
            r"""
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
            r"""
---
pandoc-numbering:
  exercise:
    general:
      sectioning-levels: "-.+."
---

# First chapter

# Second chapter

## First section

## Second section

[]{#exercise:second-chapter.second-section.1}[**Exercise 2.1**]{#exercise:2.2.1 .pandoc-numbering-text .exercise}

[]{#exercise:second-chapter.second-section.title}[**Exercise 2.2** *(Title)*]{#exercise:2.2.2 .pandoc-numbering-text .exercise}
            """,
        )
