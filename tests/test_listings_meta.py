# This Python file uses the following encoding: utf-8

from unittest import TestCase

from helper import verify_conversion


class ListingsTest(TestCase):
    def test_listing_classic(self):
        verify_conversion(
            self,
            r"""
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
---

Exercise #

Exercise (Title) #
            """,
            r"""
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
---

# List of exercises {#list-of-exercises .pandoc-numbering-listing .exercise .unnumbered .unlisted}

-   [[Exercise 1]{.pandoc-numbering-entry .exercise}](#exercise:1)
-   [[Title]{.pandoc-numbering-entry .exercise}](#exercise:2)

[]{#exercise:1}[**Exercise 1**]{#exercise:1 .pandoc-numbering-text .exercise}

[]{#exercise:title}[**Exercise 2** *(Title)*]{#exercise:2 .pandoc-numbering-text .exercise}
            """,
        )

    def test_listing_identifier_false(self):
        verify_conversion(
            self,
            r"""
---
pandoc-numbering:
  exercise:
    general:
      listing-identifier: False
      listing-title: List of exercises
---

Exercise #

Exercise (Title) #
            """,
            r"""
---
pandoc-numbering:
  exercise:
    general:
      listing-identifier: false
      listing-title: List of exercises
---

# List of exercises {.pandoc-numbering-listing .exercise .unnumbered .unlisted}

-   [[Exercise 1]{.pandoc-numbering-entry .exercise}](#exercise:1)
-   [[Title]{.pandoc-numbering-entry .exercise}](#exercise:2)

[]{#exercise:1}[**Exercise 1**]{#exercise:1 .pandoc-numbering-text .exercise}

[]{#exercise:title}[**Exercise 2** *(Title)*]{#exercise:2 .pandoc-numbering-text .exercise}
            """,
        )

    def test_listing_identifier(self):
        verify_conversion(
            self,
            r"""
---
pandoc-numbering:
  exercise:
    general:
      listing-identifier: myident
      listing-title: List of exercises
---

Exercise #

Exercise (Title) #
            """,
            r"""
---
pandoc-numbering:
  exercise:
    general:
      listing-identifier: myident
      listing-title: List of exercises
---

# List of exercises {#myident .pandoc-numbering-listing .exercise .unnumbered .unlisted}

-   [[Exercise 1]{.pandoc-numbering-entry .exercise}](#exercise:1)
-   [[Title]{.pandoc-numbering-entry .exercise}](#exercise:2)

[]{#exercise:1}[**Exercise 1**]{#exercise:1 .pandoc-numbering-text .exercise}

[]{#exercise:title}[**Exercise 2** *(Title)*]{#exercise:2 .pandoc-numbering-text .exercise}
            """,
        )

    def test_listing_options(self):
        verify_conversion(
            self,
            r"""
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
      listing-unlisted: False
      listing-unnumbered: False
---

Exercise #

Exercise (Title) #
            """,
            r"""
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
      listing-unlisted: false
      listing-unnumbered: false
---

# List of exercises {#list-of-exercises .pandoc-numbering-listing .exercise}

-   [[Exercise 1]{.pandoc-numbering-entry .exercise}](#exercise:1)
-   [[Title]{.pandoc-numbering-entry .exercise}](#exercise:2)

[]{#exercise:1}[**Exercise 1**]{#exercise:1 .pandoc-numbering-text .exercise}

[]{#exercise:title}[**Exercise 2** *(Title)*]{#exercise:2 .pandoc-numbering-text .exercise}
            """,
        )

    def test_listing_latex(self):
        verify_conversion(
            self,
            r"""
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
---

Exercise #

Exercise (Title) #
            """,
            r"""
---
header-includes:
- "`\\usepackage{tocloft}`{=tex}"
- "`\\usepackage{etoolbox}`{=tex}"
- "`\\newlistof{exercise}{exercise}{List of exercises}\\renewcommand{\\cftexercisetitlefont}{\\cfttoctitlefont}`{=tex}"
- "`\\ifdef{\\mainmatter}{\\let\\oldmainmatter\\mainmatter\\renewcommand{\\mainmatter}[0]{\\listofexercise\\oldmainmatter}}{}`{=tex}"
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
---

`\usepackage{tocloft}`{=tex}

`\usepackage{etoolbox}`{=tex}

`\newlistof{exercise}{exercise}{List of exercises}\renewcommand{\cftexercisetitlefont}{\cfttoctitlefont}`{=tex}

`\ifdef{\mainmatter}{\let\oldmainmatter\mainmatter\renewcommand{\mainmatter}[0]{\listofexercise\oldmainmatter}}{}`{=tex}

```{=tex}
\ifdef{\mainmatter}{}{\listofexercise}
```
`\phantomsection\addcontentsline{exercise}{exercise}{\protect\numberline {1}{\ignorespaces {Exercise}}}`{=tex}[]{#exercise:1}[`\label{exercise:1}`{=tex}`\label{exercise:1}`{=tex}**Exercise 1**]{#exercise:1 .pandoc-numbering-text .exercise}

`\phantomsection\addcontentsline{exercise}{exercise}{\protect\numberline {2}{\ignorespaces {Title}}}`{=tex}[]{#exercise:title}[`\label{exercise:2}`{=tex}`\label{exercise:title}`{=tex}**Exercise 2** *(Title)*]{#exercise:2 .pandoc-numbering-text .exercise}
            """,
            "latex",
        )

    def test_listing_classic_format(self):
        verify_conversion(
            self,
            r"""
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
    standard:
      format-entry-classic: '%g %D'
      format-entry-title: '%g %D (%T)'
---

Exercise #

Exercise (Title) #
            """,
            r"""
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
    standard:
      format-entry-classic: "%g %D"
      format-entry-title: %g %D (%T)
---

# List of exercises {#list-of-exercises .pandoc-numbering-listing .exercise .unnumbered .unlisted}

-   [[1 Exercise]{.pandoc-numbering-entry .exercise}](#exercise:1)
-   [[2 Exercise (Title)]{.pandoc-numbering-entry .exercise}](#exercise:2)

[]{#exercise:1}[**Exercise 1**]{#exercise:1 .pandoc-numbering-text .exercise}

[]{#exercise:title}[**Exercise 2** *(Title)*]{#exercise:2 .pandoc-numbering-text .exercise}
            """,
        )

    def test_listing_latex_format(self):
        verify_conversion(
            self,
            r"""
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
    latex:
      entry-space: 3
      entry-tab: 2
      format-entry-classic: '%D'
      format-entry-title: '%D (%T)'
toccolor: blue
---

Exercise #

Exercise (Title) #
            """,
            r"""
---
header-includes:
- "`\\usepackage{tocloft}`{=tex}"
- "`\\usepackage{etoolbox}`{=tex}"
- "`\\newlistof{exercise}{exercise}{List of exercises}\\renewcommand{\\cftexercisetitlefont}{\\cfttoctitlefont}`{=tex}"
- "`\\ifdef{\\mainmatter}{\\let\\oldmainmatter\\mainmatter\\renewcommand{\\mainmatter}[0]{\\listofexercise\\oldmainmatter}}{}`{=tex}"
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
    latex:
      entry-space: 3
      entry-tab: 2
      format-entry-classic: "%D"
      format-entry-title: %D (%T)
toccolor: blue
---

`\usepackage{tocloft}`{=tex}

`\usepackage{etoolbox}`{=tex}

`\newlistof{exercise}{exercise}{List of exercises}\renewcommand{\cftexercisetitlefont}{\cfttoctitlefont}`{=tex}

`\ifdef{\mainmatter}{\let\oldmainmatter\mainmatter\renewcommand{\mainmatter}[0]{\listofexercise\oldmainmatter}}{}`{=tex}

```{=tex}
\ifdef{\mainmatter}{}{\listofexercise}
```
`\phantomsection\addcontentsline{exercise}{exercise}{\protect\numberline {1}{\ignorespaces {Exercise}}}`{=tex}[]{#exercise:1}[`\label{exercise:1}`{=tex}`\label{exercise:1}`{=tex}**Exercise 1**]{#exercise:1 .pandoc-numbering-text .exercise}

`\phantomsection\addcontentsline{exercise}{exercise}{\protect\numberline {2}{\ignorespaces {Exercise (Title)}}}`{=tex}[]{#exercise:title}[`\label{exercise:2}`{=tex}`\label{exercise:title}`{=tex}**Exercise 2** *(Title)*]{#exercise:2 .pandoc-numbering-text .exercise}
            """,
            "latex",
        )
