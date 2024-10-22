from unittest import TestCase

from .helper import verify_conversion


class ReferencingMetaTest(TestCase):
    def test_referencing_link_standard(self):
        verify_conversion(
            self,
            r"""
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
            r"""
---
pandoc-numbering:
  exercise:
    general:
      cite-shortcut: true
    standard:
      format-link-classic: "**%D %d %g %s %n %c**"
      format-link-title: "**%D %d %T %t %g %s %n %c**"
---

# Title

[]{#exercise:title.1}[**Exercise 1**]{#exercise:first .pandoc-numbering-text .exercise}

[]{#exercise:title.title}[**Exercise 2** *(Title)*]{#exercise:second .pandoc-numbering-text .exercise}

See [[**Exercise exercise 1.1 1 1 2**]{.pandoc-numbering-link .exercise}](#exercise:first "Exercise 1")

See [[**Exercise exercise Title title 1.2 1 2 2**]{.pandoc-numbering-link .exercise}](#exercise:second "Exercise 2 (Title)")
            """,
        )

    def test_referencing_link_latex(self):
        verify_conversion(
            self,
            r"""
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
pandoc-numbering:
  exercise:
    general:
      cite-shortcut: true
    latex:
      format-link-classic: "**%D %d %g %s %n %p**"
      format-link-title: "**%D %d %T %t %g %s %n %p**"
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

See [[**Exercise exercise 1.1 1 1 `\pageref{exercise:first}`{=tex}**]{.pandoc-numbering-link .exercise}](#exercise:first "Exercise 1")

See [[**Exercise exercise Title title 1.2 1 2 `\pageref{exercise:second}`{=tex}**]{.pandoc-numbering-link .exercise}](#exercise:second "Exercise 2 (Title)")
            """,
            "latex",
        )

    def test_referencing_caption_standard(self):
        verify_conversion(
            self,
            r"""
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
            r"""
---
pandoc-numbering:
  exercise:
    general:
      cite-shortcut: true
    standard:
      format-caption-classic: "%D %d %g %s %n %c"
      format-caption-title: "%D %d %T %t %g %s %n %c"
---

# Title

[]{#exercise:title.1}[**Exercise 1**]{#exercise:first .pandoc-numbering-text .exercise}

[]{#exercise:title.title}[**Exercise 2** *(Title)*]{#exercise:second .pandoc-numbering-text .exercise}

See [[Exercise 1]{.pandoc-numbering-link .exercise}](#exercise:first "Exercise exercise 1.1 1 1 2")

See [[Exercise 2 (Title)]{.pandoc-numbering-link .exercise}](#exercise:second "Exercise exercise Title title 1.2 1 2 2")
            """,
        )

    def test_referencing_caption_latex(self):
        verify_conversion(
            self,
            r"""
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
pandoc-numbering:
  exercise:
    general:
      cite-shortcut: true
    latex:
      format-caption-classic: "%D %d %g %s %n %c %p"
      format-caption-title: "%D %d %T %t %g %s %n %c %p"
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

See [[Exercise 1]{.pandoc-numbering-link .exercise}](#exercise:first "Exercise exercise 1.1 1 1 2 \pageref{exercise:first}")

See [[Exercise 2 (Title)]{.pandoc-numbering-link .exercise}](#exercise:second "Exercise exercise Title title 1.2 1 2 2 \pageref{exercise:second}")
            """,
            "latex",
        )
