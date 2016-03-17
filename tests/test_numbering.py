from unittest import TestCase

import pandoc_numbering

def test_numbering():
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    assert pandoc_numbering.numbering(
        'Para',
        [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '#'}],
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
        [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '#'}],
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
        [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '#'}],
        '',
        {}
    )
    assert pandoc_numbering.numbering(
        'Para',
        [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '#'}],
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
            {'t': 'Str', 'c': 'Exercise'},
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

def test_referencing_simple():
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    pandoc_numbering.numbering(
        'Para',
        [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '#exercise:first'}],
        '',
        {}
    )
    if pandoc_numbering.pandoc_version() < '1.16':
        link = [[], ['#exercise:first', '']]
        pandoc_numbering.referencing('Link', link, '', {})
        assert link[0] == [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '1'}]
    else:
        link = [['', [], []], [], ['#exercise:first', '']]
        pandoc_numbering.referencing('Link', link, '', {})
        assert link[1] == [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '1'}]

def test_referencing_title():
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    pandoc_numbering.numbering(
        'Para',
        [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '#exercise:first'}],
        '',
        {}
    )
    if pandoc_numbering.pandoc_version() < '1.16':
        link = [[], ['#exercise:first', 'This is the exercise #']]
        pandoc_numbering.referencing('Link', link, '', {})
        assert link[1] == ['#exercise:first', 'This is the exercise 1']
    else:
        link = [['', [], []], [], ['#exercise:first', 'This is the exercise #']]
        pandoc_numbering.referencing('Link', link, '', {})
        assert link[2] == ['#exercise:first', 'This is the exercise 1']

def test_referencing_label():
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    pandoc_numbering.numbering(
        'Para',
        [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '#exercise:first'}],
        '',
        {}
    )
    if pandoc_numbering.pandoc_version() < '1.16':
        link = [
            [{'t': 'Str', 'c': 'exercise'}, {'t': 'Space', 'c': []},{'t': 'Str', 'c': '#'}],
            ['#exercise:first', '']
        ]
        pandoc_numbering.referencing('Link', link, '', {})
        assert link[0] == [{'t': 'Str', 'c': 'exercise'}, {'t': 'Space', 'c': []},{'t': 'Str', 'c': '1'}]
    else:
        link = [
            ['', [], []],
            [{'t': 'Str', 'c': 'exercise'}, {'t': 'Space', 'c': []},{'t': 'Str', 'c': '#'}],
            ['#exercise:first', '']
        ]
        pandoc_numbering.referencing('Link', link, '', {})
        assert link[1] == [{'t': 'Str', 'c': 'exercise'}, {'t': 'Space', 'c': []},{'t': 'Str', 'c': '1'}]

def test_referencing_unexisting():
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    pandoc_numbering.numbering(
        'Para',
        [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []}, {'t': 'Str', 'c': '#'}],
        '',
        {}
    )
    if pandoc_numbering.pandoc_version() < '1.16':
        link1 = [
            [],
            ['#exercise:1', '']
        ]
        pandoc_numbering.referencing('Link', link1, '', {})
        assert link1[0] == [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []},{'t': 'Str', 'c': '1'}]

        link2 = [
            [],
            ['#exercise:second', '']
        ]
        pandoc_numbering.referencing('Link', link2, '', {})
        assert link2[0] == []
    else:
        link1 = [
            ['', [], []],
            [],
            ['#exercise:1', '']
        ]
        pandoc_numbering.referencing('Link', link1, '', {})
        assert link1[1] == [{'t': 'Str', 'c': 'Exercise'}, {'t': 'Space', 'c': []},{'t': 'Str', 'c': '1'}]

        link2 = [
            ['', [], []],
            [],
            ['#exercise:second', '']
        ]
        pandoc_numbering.referencing('Link', link2, '', {})
        assert link2[1] == []

