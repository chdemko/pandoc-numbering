# This Python file uses the following encoding: utf-8

from unittest import TestCase
from panflute import *

import pandoc_numbering
from helper import verify_conversion

def test_referencing_cite():
    verify_conversion(
        '''
---
pandoc-numbering:
  exercise:
    general:
      cite-shortcut: True
    standard:
      format-link-classic: '**%D %d %g %s %n**' 
      format-link-title: '**%D %d %T %t %g %s %n**' 
---

Title
=====

Exercise -.#first

Exercise (Title) -.#second

See @exercise:first

See @exercise:second
        ''',
        '''
---
pandoc-numbering:
  exercise:
    general:
      cite-shortcut: True
    standard:
      format-link-classic: '**%D %d %g %s %n**'
      format-link-title: '**%D %d %T %t %g %s %n**'
---

Title
=====

[**Exercise 1**]{#exercise:first .pandoc-numbering-text .exercise}

[**Exercise 2** *(Title)*]{#exercise:second .pandoc-numbering-text .exercise}

See [[**Exercise exercise 1.1 1 1**]{.pandoc-numbering-link .exercise}](#exercise:first)

See [[**Exercise exercise Title title 1.2 1 2**]{.pandoc-numbering-link .exercise}](#exercise:second)
        '''
    )

def test_referencing_latex():
    verify_conversion(
        '''
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
        ''',
        '''
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

See [[**Exercise exercise 1.1 1 1 \\pageref{exercise:first}**]{.pandoc-numbering-link .exercise}](#exercise:first)

See [[**Exercise exercise Title title 1.2 1 2 \\pageref{exercise:second}**]{.pandoc-numbering-link .exercise}](#exercise:second)
        ''',
        'latex'
   )
   
