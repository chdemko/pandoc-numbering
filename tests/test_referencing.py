from unittest import TestCase

from helper import verify_conversion


class ReferencincTest(TestCase):
    def test_referencing_standard(self):
        verify_conversion(
            self,
            r"""
Header
======

Section
-------

Exercise (First title) -.+.#exercise:first

Exercise (Second title) -.+.#exercise:second

See [%D %d %T %t %g %s %n # %c](#exercise:first)

See [%D %d %T %t %g %s %n # %c](#exercise:second)
            """,
            r"""
# Header

## Section

[]{#exercise:header.section.first-title}[**Exercise 1.1** *(First title)*]{#exercise:first .pandoc-numbering-text .exercise}

[]{#exercise:header.section.second-title}[**Exercise 1.2** *(Second title)*]{#exercise:second .pandoc-numbering-text .exercise}

See [Exercise exercise First title first title 1.1.1 1.1 1.1 1.1 2](#exercise:first)

See [Exercise exercise Second title second title 1.1.2 1.1 1.2 1.2 2](#exercise:second)
            """,
        )

    def test_referencing_latex(self):
        verify_conversion(
            self,
            r"""
Title
=====

Exercise -.#first

Exercise (Title) -.#second

See [%D %d %T %t %g %s %n # %c %p](#exercise:first)

See [%D %d %T %t %g %s %n # %c %p](#exercise:second)
            """,
            r"""
---
header-includes:
- |
  `
  \makeatletter
  \@ifpackageloaded{subfig}{
      \usepackage[subfigure]{tocloft}
  }{
      \usepackage{tocloft}
  }
  \makeatother
  `{=tex}
- "`\\usepackage{etoolbox}`{=tex}"
- "`\\ifdef{\\mainmatter}{\\let\\oldmainmatter\\mainmatter\\renewcommand{\\mainmatter}[0]{\\oldmainmatter}}{}`{=tex}"
---

`
\makeatletter
\@ifpackageloaded{subfig}{
    \usepackage[subfigure]{tocloft}
}{
    \usepackage{tocloft}
}
\makeatother
`{=tex}

`\usepackage{etoolbox}`{=tex}

`\ifdef{\mainmatter}{\let\oldmainmatter\mainmatter\renewcommand{\mainmatter}[0]{\oldmainmatter}}{}`{=tex}

`\ifdef{\mainmatter}{}{}`{=tex}

# Title

`\phantomsection\addcontentsline{exercise}{exercise}{\protect\numberline {1.1}{\ignorespaces {Exercise}}}`{=tex}[]{#exercise:title.1}[**Exercise 1**]{#exercise:first .pandoc-numbering-text .exercise}

`\phantomsection\addcontentsline{exercise}{exercise}{\protect\numberline {1.2}{\ignorespaces {Title}}}`{=tex}[]{#exercise:title.title}[**Exercise 2** *(Title)*]{#exercise:second .pandoc-numbering-text .exercise}

See [Exercise exercise 1.1 1 1 1 2 `\pageref{exercise:first}`{=tex}](#exercise:first)

See [Exercise exercise Title title 1.2 1 2 2 2 `\pageref{exercise:second}`{=tex}](#exercise:second)
            """,
            "latex",
        )
