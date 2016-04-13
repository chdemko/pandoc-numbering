# This Python file uses the following encoding: utf-8
from unittest import TestCase
from pandocfilters import Para, Str, Space, Span, Strong, RawInline, Emph, Header

import pandoc_numbering

def init():
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    pandoc_numbering.headers = [0, 0, 0, 0, 0, 0]

def test_numbering():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = Para([Span([u'exercise:1', [], []], [Strong([Str(u'Exercise'), Space(), Str(u'1')])])])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

def test_numbering_prefix_single():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'#ex:')])
    dest = Para([Span([u'ex:1', [], []], [Strong([Str(u'Exercise'), Space(), Str(u'1')])])])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = Para([Span([u'exercise:1', [], []], [Strong([Str(u'Exercise'), Space(), Str(u'1')])])])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

def test_numbering_latex():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = Para([
        RawInline(u'tex', u'\\phantomsection'),
        Span([u'exercise:1', [], []], [Strong([Str(u'Exercise'), Space(), Str(u'1')])])
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], 'latex', {}) == dest

def test_numbering_double():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = Para([Span([u'exercise:2', [], []], [Strong( [Str(u'Exercise'), Space(), Str(u'2')])])])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

def test_numbering_title():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'(The'), Space(), Str(u'title)'), Space(), Str(u'#')])
    dest = Para([
        Span(
            [u'exercise:1', [], []],
            [
                Strong([Str(u'Exercise'), Space(), Str(u'1')]),
                Space(),
                Emph([Str(u'(The'), Space(), Str(u'title)')])
            ]
        )
    ])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

def test_numbering_level():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'#.#.#')])
    dest = Para([Span([u'exercise:0.0.1', [], []], [Strong([Str(u'Exercise'), Space(), Str(u'0.0.1')])])])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Header(1, [u'first-chapter', [], []], [Str(u'First'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    src = Header(2, [u'first-section', [], []], [Str(u'First'), Space(), Str('section')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    src = Para([Str(u'Exercise'), Space(), Str(u'#.#.#')])
    dest = Para([Span( [u'exercise:1.1.1', [], []], [Strong([Str(u'Exercise'), Space(), Str(u'1.1.1')])])])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Para([Str(u'Exercise'), Space(), Str(u'#.#.#')])
    dest = Para([Span([u'exercise:1.1.2', [], []], [Strong([Str(u'Exercise'), Space(), Str(u'1.1.2')])])])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Header(2, [u'second-section', [], []], [Str(u'Second'), Space(), Str('section')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    src = Para([Str(u'Exercise'), Space(), Str(u'#.#.#')])
    dest = Para([Span([u'exercise:1.2.1', [], []], [Strong( [Str(u'Exercise'), Space(), Str(u'1.2.1')])])])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

def test_numbering_unnumbered():
    init()

    src = Header(1, [u'unnumbered-chapter', [u'unnumbered'], []], [Str(u'Unnumbered'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    src = Para([Str(u'Exercise'), Space(), Str(u'#.#')])
    dest = Para([Span([u'exercise:0.1', [], []], [Strong([Str(u'Exercise'), Space(), Str(u'0.1')])])])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

def test_numbering_hidden():
    init()

    src = Header(1, [u'first-chapter', [], []], [Str(u'First'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    src = Para([Str(u'Exercise'), Space(), Str(u'_.#exercise:one')])
    dest = Para([Span([u'exercise:one', [], []], [Strong([Str(u'Exercise'), Space(), Str(u'1')])])])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Para([Str(u'Exercise'), Space(), Str(u'_.#')])
    dest = Para([Span([u'exercise:1.2', [], []], [Strong([Str(u'Exercise'), Space(), Str(u'2')])])])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Header(1, [u'second-chapter', [], []], [Str(u'Second'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    src = Para([Str(u'Exercise'), Space(), Str(u'_.#')])
    dest = Para([Span([u'exercise:2.1', [], []], [Strong([Str(u'Exercise'), Space(), Str(u'1')])])])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Para([Str(u'Exercise'), Space(), Str(u'#.#')])
    dest = Para([Span([u'exercise:2.2', [], []], [Strong([Str(u'Exercise'), Space(), Str(u'2.2')])])])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    dest = Para([Span([u'exercise:1', [], []], [Strong([Str(u'Exercise'), Space(), Str(u'1')])])])

    assert pandoc_numbering.numbering(src['t'], src['c'], '', {}) == dest

def test_numbering_sharp_sharp():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'##')])
    dest = Para([Str(u'Exercise'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], '', {})

    assert src == dest


