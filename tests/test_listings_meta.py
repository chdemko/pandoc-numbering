# This Python file uses the following encoding: utf-8

from unittest import TestCase
from panflute import *

import pandoc_numbering
from helper import verify_conversion

def test_listing_classic():
    verify_conversion(
        '''
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
---

Exercise #

Exercise (Title) #
        ''',
        '''
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
---

List of exercises {#list-of-exercises .pandoc-numbering-listing .exercise .unnumbered .unlisted}
=================

-   [[Exercise 1]{.pandoc-numbering-entry .exercise}](#exercise:1)
-   [[Title]{.pandoc-numbering-entry .exercise}](#exercise:2)

[**Exercise 1**]{#exercise:1 .pandoc-numbering-text .exercise}

[**Exercise 2** *(Title)*]{#exercise:2 .pandoc-numbering-text .exercise}
        '''
    )

def test_listing_options():
    verify_conversion(
        '''
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
        ''',
        '''
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
      listing-unlisted: False
      listing-unnumbered: False
---

List of exercises {#list-of-exercises .pandoc-numbering-listing .exercise}
=================

-   [[Exercise 1]{.pandoc-numbering-entry .exercise}](#exercise:1)
-   [[Title]{.pandoc-numbering-entry .exercise}](#exercise:2)

[**Exercise 1**]{#exercise:1 .pandoc-numbering-text .exercise}

[**Exercise 2** *(Title)*]{#exercise:2 .pandoc-numbering-text .exercise}
        '''
    )

def test_listing_latex():
    verify_conversion(
        '''
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
---

Exercise #

Exercise (Title) #
        ''',
        '''
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
---

List of exercises {#list-of-exercises .pandoc-numbering-listing .exercise .unnumbered .unlisted}
=================

\\hypersetup{linkcolor=black}\\makeatletter\\newcommand*\\l@exercise{\\@dottedtocline{1}{1.5em}{2.3em}}\\@starttoc{exercise}\\makeatother
\\phantomsection\\addcontentsline{exercise}{exercise}{\\protect\\numberline {1}{\\ignorespaces {Exercise}}}[\\label{exercise:1}**Exercise 1**]{#exercise:1 .pandoc-numbering-text .exercise}

\\phantomsection\\addcontentsline{exercise}{exercise}{\\protect\\numberline {2}{\\ignorespaces {Title}}}[\\label{exercise:2}**Exercise 2** *(Title)*]{#exercise:2 .pandoc-numbering-text .exercise}
        ''',
        'latex'
    )
    
def test_listing_classic_format():
    verify_conversion(
        '''
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
        ''',
        '''
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
    standard:
      format-entry-classic: '\%g %D'
      format-entry-title: '\%g %D (%T)'
---

List of exercises {#list-of-exercises .pandoc-numbering-listing .exercise .unnumbered .unlisted}
=================

-   [[1 Exercise]{.pandoc-numbering-entry .exercise}](#exercise:1)
-   [[2 Exercise (Title)]{.pandoc-numbering-entry .exercise}](#exercise:2)

[**Exercise 1**]{#exercise:1 .pandoc-numbering-text .exercise}

[**Exercise 2** *(Title)*]{#exercise:2 .pandoc-numbering-text .exercise}
        '''
    )

def test_listing_latex_format():
    verify_conversion(
        '''
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
        ''',
        '''
---
pandoc-numbering:
  exercise:
    general:
      listing-title: List of exercises
    latex:
      entry-space: 3
      entry-tab: 2
      format-entry-classic: '\%D'
      format-entry-title: '\%D (%T)'
toccolor: blue
---

List of exercises {#list-of-exercises .pandoc-numbering-listing .exercise .unnumbered .unlisted}
=================

\\hypersetup{linkcolor=blue}\\makeatletter\\newcommand*\\l@exercise{\\@dottedtocline{1}{2.0em}{3.0em}}\\@starttoc{exercise}\\makeatother
\\phantomsection\\addcontentsline{exercise}{exercise}{\\protect\\numberline {1}{\\ignorespaces {Exercise}}}[\\label{exercise:1}**Exercise 1**]{#exercise:1 .pandoc-numbering-text .exercise}

\\phantomsection\\addcontentsline{exercise}{exercise}{\\protect\\numberline {2}{\\ignorespaces {Exercise (Title)}}}[\\label{exercise:2}**Exercise 2** *(Title)*]{#exercise:2 .pandoc-numbering-text .exercise}
        ''',
        'latex'
    )
