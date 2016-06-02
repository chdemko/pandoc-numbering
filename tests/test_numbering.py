# This Python file uses the following encoding: utf-8

from unittest import TestCase
from pandocfilters import Para, Str, Space, Span, Strong, RawInline, Emph, Header

import json

import pandoc_numbering

def init():
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    pandoc_numbering.collections = {}
    pandoc_numbering.headers = [0, 0, 0, 0, 0, 0]
    if hasattr(pandoc_numbering.getCiteShortCut, 'value'):
        delattr(pandoc_numbering.getCiteShortCut, 'value')
    if hasattr(pandoc_numbering.getDefaultLevels, 'value'):
        delattr(pandoc_numbering.getDefaultLevels, 'value')
    if hasattr(pandoc_numbering.getClasses, 'value'):
        delattr(pandoc_numbering.getClasses, 'value')
    if hasattr(pandoc_numbering.getFormat, 'value'):
        delattr(pandoc_numbering.getFormat, 'value')

def test_numbering():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = Para([
        Span(
            [u'exercise:1', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

def test_numbering_prefix_single():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'#ex:')])
    dest = Para([
        Span(
            [u'ex:1', ['pandoc-numbering-text', 'ex'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = Para([
        Span(
            [u'exercise:1', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

def test_numbering_latex():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = Para([
        RawInline(u'tex', u'\\phantomsection\\addcontentsline{exercise}{exercise}{\\protect\\numberline {1}{\\ignorespaces Exercise}}'),
        Span(
            [u'exercise:1', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1')])
            ]
       )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], 'latex', {}) == dest

    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'(The'), Space(), Str(u'title)'), Space(), Str(u'#')])
    dest = Para([
        RawInline(u'tex', u'\\phantomsection\\addcontentsline{exercise}{exercise}{\\protect\\numberline {1}{\\ignorespaces The title}}'),
        Span(
            [u'exercise:1', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1')]),
                Space(),
                Emph([Str(u'('), Str(u'The'), Space(), Str(u'title'), Str(u')')])
            ]
       )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], 'latex', {}) == dest

def test_numbering_double():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = Para([
        Span(
            [u'exercise:2', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'2')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

def test_numbering_title():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'(The'), Space(), Str(u'title)'), Space(), Str(u'#')])
    dest = Para([
        Span(
            [u'exercise:1', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1')]),
                Space(),
                Emph([Str(u'('), Str(u'The'), Space(), Str(u'title'), Str(u')')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

def test_numbering_level():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'+.+.#')])
    dest = Para([
        Span(
            [u'exercise:0.0.1', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'0.0.1')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Header(1, [u'first-chapter', [], []], [Str(u'First'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    src = Header(2, [u'first-section', [], []], [Str(u'First'), Space(), Str('section')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    src = Para([Str(u'Exercise'), Space(), Str(u'+.+.#')])
    dest = Para([
        Span(
            [u'exercise:1.1.1', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1.1.1')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Para([Str(u'Exercise'), Space(), Str(u'+.+.#')])
    dest = Para([
        Span(
            [u'exercise:1.1.2', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1.1.2')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Header(2, [u'second-section', [], []], [Str(u'Second'), Space(), Str('section')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    src = Para([Str(u'Exercise'), Space(), Str(u'+.+.#')])
    dest = Para([
        Span(
            [u'exercise:1.2.1', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1.2.1')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

def test_numbering_unnumbered():
    init()

    src = Header(1, [u'unnumbered-chapter', [u'unnumbered'], []], [Str(u'Unnumbered'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    src = Para([Str(u'Exercise'), Space(), Str(u'+.#')])
    dest = Para([
        Span(
            [u'exercise:0.1', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'0.1')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

def test_numbering_hidden():
    init()

    src = Header(1, [u'first-chapter', [], []], [Str(u'First'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    src = Para([Str(u'Exercise'), Space(), Str(u'-.#exercise:one')])
    dest = Para([
        Span(
            [u'exercise:one', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Para([Str(u'Exercise'), Space(), Str(u'-.#')])
    dest = Para([
        Span(
            [u'exercise:1.2', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'2')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Header(1, [u'second-chapter', [], []], [Str(u'Second'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    src = Para([Str(u'Exercise'), Space(), Str(u'-.#')])
    dest = Para([
        Span(
            [u'exercise:2.1', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Para([Str(u'Exercise'), Space(), Str(u'+.#')])
    dest = Para([
        Span(
            [u'exercise:2.2', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'2.2')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = Para([
        Span(
            [u'exercise:1', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

def test_numbering_sharp_sharp():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'##')])
    dest = Para([Str(u'Exercise'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    assert src == dest

def test_numbering_sectioning_string():
    init()

    meta = {
        'pandoc-numbering': {
            't': 'MetaList',
            'c': [
                {
                    't': 'MetaMap',
                    'c': {
                        'category': {
                            't': 'MetaInlines',
                            'c': [Str('exercise')]
                        },
                        'sectioning': {
                            't': 'MetaInlines',
                            'c': [Str('-.+.')]
                        }
                    }
                }
            ]
        }
    }

    src = Header(1, [u'first-chapter', [], []], [Str(u'First'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)

    src = Header(1, [u'second-chapter', [], []], [Str(u'Second'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)

    src = Header(2, [u'first-section', [], []], [Str(u'First'), Space(), Str('section')])
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)

    src = Header(2, [u'second-section', [], []], [Str(u'Second'), Space(), Str('section')])
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = Para([
        Span(
            [u'exercise:2.2.1', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'2.1')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', meta) == dest

def test_numbering_sectioning_map():
    init()

    meta = {
        'pandoc-numbering': {
            't': 'MetaList',
            'c': [
                {
                    't': 'MetaMap',
                    'c': {
                        'category': {
                            't': 'MetaInlines',
                            'c': [Str('exercise')]
                        },
                        'first': {
                            'c': 2,
                            't': 'MetaString'
                        },
                        'last': {
                            'c': 2,
                            't': 'MetaString'
                        }
                    }
                }
            ]
        }
    }

    src = Header(1, [u'first-chapter', [], []], [Str(u'First'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)

    src = Header(1, [u'second-chapter', [], []], [Str(u'Second'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)

    src = Header(2, [u'first-section', [], []], [Str(u'First'), Space(), Str('section')])
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)

    src = Header(2, [u'second-section', [], []], [Str(u'Second'), Space(), Str('section')])
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = Para([
        Span(
            [u'exercise:2.2.1', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'2.1')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', meta) == dest

def test_numbering_sectioning_map_error():
    init()

    meta = {
        'pandoc-numbering': {
            't': 'MetaList',
            'c': [
                {
                    't': 'MetaMap',
                    'c': {
                        'category': {
                            't': 'MetaInlines',
                            'c': [Str('exercise')]
                        },
                        'first': {
                            'c': 'a',
                            't': 'MetaString'
                        },
                        'last': {
                            'c': 'b',
                            't': 'MetaString'
                        }
                    }
                }
            ]
        }
    }

    src = Header(1, [u'first-chapter', [], []], [Str(u'First'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)

    src = Header(1, [u'second-chapter', [], []], [Str(u'Second'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)

    src = Header(2, [u'first-section', [], []], [Str(u'First'), Space(), Str('section')])
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)

    src = Header(2, [u'second-section', [], []], [Str(u'Second'), Space(), Str('section')])
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = Para([
        Span(
            [u'exercise:1', ['pandoc-numbering-text', 'exercise'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', meta) == dest

def test_classes():
    init()

    meta = {
        'pandoc-numbering': {
            't': 'MetaList',
            'c': [
                {
                    't': 'MetaMap',
                    'c': {
                        'category': {
                            't': 'MetaInlines',
                            'c': [Str('exercise')]
                        },
                        'classes': {
                            't': 'MetaList',
                            'c': [{'t': 'MetaInlines', 'c': [{'t': 'Str', 'c': 'my-class'}]}]
                        }
                    }
                }
            ]
        }
    }

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = Para([
        Span(
            [u'exercise:1', ['pandoc-numbering-text', 'my-class'], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', meta) == dest

def test_format():
    init()

    meta = {
        'pandoc-numbering': {
            't': 'MetaMap',
            'c': {
                'format': {
                    't': 'MetaMap',
                    'c': {
                        'exercise': {
                            'c': False,
                            't': 'MetaBool'
                        }
                    }
                }
            }
        }
    }
    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = json.loads(json.dumps(Para([
        Span(
            [u'exercise:1', ['pandoc-numbering-text', 'exercice'], []],
            [
                Span(['', ['description'], []], [Str(u'Exercise')]),
                Span(['', ['number'], []], [Str(u'1')]),
                Span(['', ['title'], []], [])
            ]
        )
    ])))

    json.loads(json.dumps(pandoc_numbering.numbering(src['t'], src['c'], '', meta))) == dest

