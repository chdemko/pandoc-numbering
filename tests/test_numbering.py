# This Python file uses the following encoding: utf-8
from unittest import TestCase

import pandoc_numbering

def test_numbering():
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    assert pandoc_numbering.numbering(
        'Para',
        [{'t': 'Str', 'c': u'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '#'}],
        '',
        {}
    ) == {
        't': 'Para',
        'c': [{
            't': 'Span',
            'c': (
                ['exercise:1', [], []],
                [{
                    't': 'Strong',
                    'c': [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '1'}]
                }]
            ),
        }]
    }

def test_numbering_latex():
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    assert pandoc_numbering.numbering(
        'Para',
        [{'t': 'Str', 'c': u'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '#'}],
        'latex',
        {}
    ) == {
        't': 'Para',
        'c': [
            {
                't': 'RawInline',
                'c': ('tex', '\\phantomsection'),
            },
            {
                't': 'Span',
                'c': (
                    ['exercise:1', [], []],
                    [{
                        't': 'Strong',
                        'c': [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '1'}]
                    }]
                ),
            }
        ]
    }

def test_numbering_double():
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    pandoc_numbering.numbering(
        'Para',
        [{'t': 'Str', 'c': u'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '#'}],
        '',
        {}
    )
    assert pandoc_numbering.numbering(
        'Para',
        [{'t': 'Str', 'c': u'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '#'}],
        '',
        {}
    ) == {
        't': 'Para',
        'c': [{
            't': 'Span',
            'c': (
                ['exercise:2', [], []],
                [{
                    't': 'Strong',
                    'c': [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '2'}]
                }]
            ),
        }]
    }

def test_numbering_title():
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    assert pandoc_numbering.numbering(
        'Para',
        [
            {'t': 'Str', 'c': u'Exercise'},
            {'t': 'Space', 'c': []},
            {'t': 'Str', 'c': '(The'},
            {'t': 'Space', 'c': []},
            {'t': 'Str', 'c': 'title)'},
            {'t': 'Space', 'c': []},
            {'t': 'Str', 'c': '#'}
        ],
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
                    },
                    {
                        't': 'Space',
                        'c': []
                    },
                    {
                        't': 'Emph',
                        'c': [{'t': 'Str', 'c': '(The'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': 'title)'}]
                    },
                ]
            ),
        }]
    }

def test_numbering_level():
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    pandoc_numbering.headers = [0, 0, 0, 0, 0, 0]
    assert pandoc_numbering.numbering(
        'Para',
        [
            {'t': 'Str', 'c': u'Exercise'},
            {'t': 'Space', 'c': []},
            {'t': 'Str', 'c': '#.#.#'}
        ],
        '',
        {}
    ) == {
        't': 'Para',
        'c': [{
            't': 'Span',
            'c': (
                ['exercise:0.0.1', [], []],
                [
                    {
                        't': 'Strong',
                        'c': [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '0.0.1'}]
                    }
                ]
            ),
        }]
    }
    pandoc_numbering.numbering(
        'Header',
        [1, ['firs-chapter', [], []], [{'t': 'Str', 'c': 'First'}, {'t': 'Space', 'c': []},{'t': 'Str', 'c': 'chapter'}]],
        '',
        {}
    )
    pandoc_numbering.numbering(
        'Header',
        [2, ['first-section', [], []], [{'t': 'Str', 'c': 'First'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': 'section'}]],
        '',
        {}
    )
    assert pandoc_numbering.numbering(
        'Para',
        [
            {'t': 'Str', 'c': u'Exercise'},
            {'t': 'Space', 'c': []},
            {'t': 'Str', 'c': '#.#.#'}
        ],
        '',
        {}
    ) == {
        't': 'Para',
        'c': [{
            't': 'Span',
            'c': (
                ['exercise:1.1.1', [], []],
                [
                    {
                        't': 'Strong',
                        'c': [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '1.1.1'}]
                    }
                ]
            ),
        }]
    }
    assert pandoc_numbering.numbering(
        'Para',
        [
            {'t': 'Str', 'c': u'Exercise'},
            {'t': 'Space', 'c': []},
            {'t': 'Str', 'c': '#.#.#'}
        ],
        '',
        {}
    ) == {
        't': 'Para',
        'c': [{
            't': 'Span',
            'c': (
                ['exercise:1.1.2', [], []],
                [
                    {
                        't': 'Strong',
                        'c': [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '1.1.2'}]
                    }
                ]
            ),
        }]
    }
    pandoc_numbering.numbering(
        'Header',
        [2, ['second-section', [], []], [{'t': 'Str', 'c': 'Second'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': 'section'}]],
        '',
        {}
    )
    assert pandoc_numbering.numbering(
        'Para',
        [
            {'t': 'Str', 'c': u'Exercise'},
            {'t': 'Space', 'c': []},
            {'t': 'Str', 'c': '#.#.#'}
        ],
        '',
        {}
    ) == {
        't': 'Para',
        'c': [{
            't': 'Span',
            'c': (
                ['exercise:1.2.1', [], []],
                [
                    {
                        't': 'Strong',
                        'c': [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '1.2.1'}]
                    }
                ]
            ),
        }]
    }

def test_numbering_unnumbered():
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    pandoc_numbering.headers = [0, 0, 0, 0, 0, 0]
    pandoc_numbering.numbering(
        'Header',
        [1, ['chapter', ['unnumbered'], []], [{'t': 'Str', 'c': 'Unnumbered'}, {'t': 'Space', 'c': []},{'t': 'Str', 'c': 'chapter'}]],
        '',
        {}
    )
    assert pandoc_numbering.numbering(
        'Para',
        [
            {'t': 'Str', 'c': u'Exercise'},
            {'t': 'Space', 'c': []},
            {'t': 'Str', 'c': '#.#'}
        ],
        '',
        {}
    ) == {
        't': 'Para',
        'c': [{
            't': 'Span',
            'c': (
                ['exercise:0.1', [], []],
                [
                    {
                        't': 'Strong',
                        'c': [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '0.1'}]
                    }
                ]
            ),
        }]
    }

def test_numbering_hidden():
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

