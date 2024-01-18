# This Python file uses the following encoding: utf-8

from unittest import TestCase

from helper import verify_conversion


class ParaTest(TestCase):
    def test_para_none(
        self,
    ):
        verify_conversion(self, "Not an example", "Not an example")

    def test_para(self):
        verify_conversion(
            self,
            r"""
Example #

Example #
            """,
            r"""
[**Example 1**]{#example:1 .pandoc-numbering-text .example}

[**Example 2**]{#example:2 .pandoc-numbering-text .example}
            """,
        )

    def test_para_title(
        self,
    ):
        verify_conversion(
            self,
            r"""
Example (This is the first title) #

Example (This is the second title) #
            """,
            r"""
[]{#example:this-is-the-first-title}[**Example 1** *(This is the first title)*]{#example:1 .pandoc-numbering-text .example}

[]{#example:this-is-the-second-title}[**Example 2** *(This is the second title)*]{#example:2 .pandoc-numbering-text .example}
            """,
        )

    def test_para_prefix_single(self):
        verify_conversion(
            self,
            "Example #ex:",
            "[**Example 1**]{#ex:1 .pandoc-numbering-text .ex}",
        )

    def test_para_double(self):
        verify_conversion(
            self,
            r"""
Example #

Example #
            """,
            r"""
[**Example 1**]{#example:1 .pandoc-numbering-text .example}

[**Example 2**]{#example:2 .pandoc-numbering-text .example}
            """,
        )

    def test_para_sectioning(self):
        verify_conversion(
            self,
            r"""
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
            r"""
# First chapter

# Second chapter

## First section

## Second section

[]{#exercise:second-chapter.second-section.1}[**Exercise 2.1**]{#exercise:2.2.1 .pandoc-numbering-text .exercise}
            """,
        )

    def test_para_numbering_hidden(self):
        verify_conversion(
            self,
            r"""
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
            r"""
# First chapter

[]{#exercise:first-chapter.1}[**Exercise 1**]{#exercise:one .pandoc-numbering-text .exercise}

[]{#exercise:first-chapter.2}[**Exercise 2**]{#exercise:1.2 .pandoc-numbering-text .exercise}

# Second chapter

[]{#exercise:second-chapter.1}[**Exercise 1**]{#exercise:2.1 .pandoc-numbering-text .exercise}

[]{#exercise:second-chapter.2}[**Exercise 2**]{#exercise:2.2 .pandoc-numbering-text .exercise}

[**Exercice 1**]{#exercice:1 .pandoc-numbering-text .exercice}
            """,
        )

    def test_para_sectioning_unnumbered(self):
        verify_conversion(
            self,
            r"""
Unnumbered chapter {#unnumbered-chapter .unnumbered}
==================

Exercise +.#
            """,
            r"""
# Unnumbered chapter {#unnumbered-chapter .unnumbered}

[]{#exercise:unnumbered-chapter.1}[**Exercise 0.1**]{#exercise:0.1 .pandoc-numbering-text .exercise}
            """,
        )

    def test_para_numbering_level(self):
        verify_conversion(
            self,
            r"""
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
            r"""
[**Exercise 0.0.1**]{#exercise:0.0.1 .pandoc-numbering-text .exercise}

# First chapter

## First section

[]{#exercise:first-chapter.first-section.1}[**Exercise 1.1.1**]{#exercise:1.1.1 .pandoc-numbering-text .exercise}

[]{#exercise:first-chapter.first-section.2}[**Exercise 1.1.2**]{#exercise:1.1.2 .pandoc-numbering-text .exercise}

## Second section

[]{#exercise:first-chapter.second-section.1}[**Exercise 1.2.1**]{#exercise:1.2.1 .pandoc-numbering-text .exercise}
            """,
        )

    def test_numbering_latex(self):
        verify_conversion(
            self,
            r"""
Exercise (Equation $a=b$) #
            """,
            r"""
---
header-includes:
- "`\\usepackage{tocloft}`{=tex}"
- "`\\usepackage{etoolbox}`{=tex}"
- "`\\ifdef{\\mainmatter}{\\let\\oldmainmatter\\mainmatter\\renewcommand{\\mainmatter}[0]{\\oldmainmatter}}{}`{=tex}"
---

`\usepackage{tocloft}`{=tex}

`\usepackage{etoolbox}`{=tex}

`\ifdef{\mainmatter}{\let\oldmainmatter\mainmatter\renewcommand{\mainmatter}[0]{\oldmainmatter}}{}`{=tex}

```{=tex}
\ifdef{\mainmatter}{}{}
```
`\phantomsection\addcontentsline{exercise}{exercise}{\protect\numberline {1}{\ignorespaces {Equation \(a=b\)}}}`{=tex}[]{#exercise:equation-a-b}[**Exercise 1** *(Equation $a=b$`<!-- -->`{=html})*]{#exercise:1 .pandoc-numbering-text .exercise}
            """,
            "latex",
        )
