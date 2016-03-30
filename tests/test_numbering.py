# This Python file uses the following encoding: utf-8
from unittest import TestCase

import pandoc_numbering
import pypandoc
import os

def test_numbering():
    assert pypandoc.convert(
        u'Exercise #\n',
        'md',
        format = 'md',
        filters = [os.getcwd() + '/pandoc_numbering.py']
    ) == '<span id="exercise:1">**Exercise 1**</span>\n'

def test_numbering_latex():
    assert pypandoc.convert(
        u'Exercise #\n',
        'latex',
        format = 'md',
        filters = [os.getcwd() + '/pandoc_numbering.py']
    ) == '\\phantomsection\\protect\\hypertarget{exercise:1}{}{\\textbf{Exercise 1}}\n'

def test_numbering_double():
    assert pypandoc.convert(
        u'Exercise #\n\nExercise #\n',
        'md',
        format = 'md',
        filters = [os.getcwd() + '/pandoc_numbering.py']
    ) == '<span id="exercise:1">**Exercise 1**</span>\n\n<span id="exercise:2">**Exercise 2**</span>\n'

def test_numbering_title():
    assert pypandoc.convert(
        u'Exercise (The title) #\n',
        'md',
        format = 'md',
        filters = [os.getcwd() + '/pandoc_numbering.py']
    ) == '<span id="exercise:1">**Exercise 1** *(The title)*</span>\n'

def test_numbering_level():
    assert pypandoc.convert(
        u'Exercise #.#.#\n',
        'md',
        format = 'md',
        filters = [os.getcwd() + '/pandoc_numbering.py']
    ) == '<span id="exercise:0.0.1">**Exercise 0.0.1**</span>\n'

    assert pypandoc.convert(u"""First chapter
=============

First section
-------------

Exercise #.#.#

Exercise #.#.#

Second section
--------------

Exercise #.#.#
""",
        'md',
        format = 'md',
        filters = [os.getcwd() + '/pandoc_numbering.py']
    ) == """First chapter
=============

First section
-------------

<span id="exercise:1.1.1">**Exercise 1.1.1**</span>

<span id="exercise:1.1.2">**Exercise 1.1.2**</span>

Second section
--------------

<span id="exercise:1.2.1">**Exercise 1.2.1**</span>
"""

def test_numbering_unnumbered():
    assert pypandoc.convert(u"""First chapter{-}
=============

Exercise #.#
""",
        'md',
        format = 'md',
        filters = [os.getcwd() + '/pandoc_numbering.py']
    ) == """First chapter {#first-chapter .unnumbered}
=============

<span id="exercise:0.1">**Exercise 0.1**</span>
"""

def test_numbering_hidden():
    assert pypandoc.convert(u"""First chapter
=============

Exercise _.#
""",
        'md',
        format = 'md',
        filters = [os.getcwd() + '/pandoc_numbering.py']
    ) == """First chapter
=============

<span id="exercise:1.1">**Exercise 1**</span>
"""
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    pandoc_numbering.headers = [0, 0, 0, 0, 0, 0]
    pandoc_numbering.numbering(
        'Header',
        [1, ['first-chapter', [], []], [{'t': 'Str', 'c': 'First'}, {'t': 'Space', 'c': []},{'t': 'Str', 'c': 'chapter'}]],
        '',
        {}
    )
    assert pandoc_numbering.numbering(
        'Para',
        [{'c': u'Exercise', 't': 'Str'}, {'c': [], 't': 'Space'}, {'c': '_.#exercise:one','t': 'Str'}],
        '',
        {}
    ) == {
        't': 'Para',
        'c': [{
            't': 'Span',
            'c': (
                ['exercise:one', [], []],
                [
                    {
                        't': 'Strong',
                        'c': [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '1'}]
                    }
                ]
            ),
        }]
    }
    assert pandoc_numbering.numbering(
        'Para',
        [{'c': u'Exercise', 't': 'Str'}, {'c': [], 't': 'Space'}, {'c': '_.#','t': 'Str'}],
        '',
        {}
    ) == {
        't': 'Para',
        'c': [{
            't': 'Span',
            'c': (
                ['exercise:1.2', [], []],
                [
                    {
                        't': 'Strong',
                        'c': [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '2'}]
                    }
                ]
            ),
        }]
    }
    pandoc_numbering.numbering(
        'Header',
        [1, ['second-chapter', [], []], [{'t': 'Str', 'c': 'Second'}, {'t': 'Space', 'c': []},{'t': 'Str', 'c': 'chapter'}]],
        '',
        {}
    )
    assert pandoc_numbering.numbering(
        'Para',
        [{'c': u'Exercise', 't': 'Str'}, {'c': [], 't': 'Space'}, {'c': '_.#','t': 'Str'}],
        '',
        {}
    ) == {
        't': 'Para',
        'c': [{
            't': 'Span',
            'c': (
                ['exercise:2.1', [], []],
                [
                    {
                        't': 'Strong',
                        'c': [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '1'}]
                    }
                ]
            ),
        }]
    }
    assert pandoc_numbering.numbering(
        'Para',
        [{'c': u'Exercise', 't': 'Str'}, {'c': [], 't': 'Space'}, {'c': '#.#','t': 'Str'}],
        '',
        {}
    ) == {
        't': 'Para',
        'c': [{
            't': 'Span',
            'c': (
                ['exercise:2.2', [], []],
                [
                    {
                        't': 'Strong',
                        'c': [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '2.2'}]
                    }
                ]
            ),
        }]
    }
    assert pandoc_numbering.numbering(
        'Para',
        [{'c': u'Exercise', 't': 'Str'}, {'c': [], 't': 'Space'}, {'c': '#','t': 'Str'}],
        '',
        {}
    ) == {
        't': 'Para',
        'c': [{
            't': 'Span',
            'c': (
                ['exercise:1', [], []],
                [
                    {
                        't': 'Strong',
                        'c': [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '1'}]
                    }
                ]
            ),
        }]
    }

