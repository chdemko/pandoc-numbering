# This Python file uses the following encoding: utf-8

from unittest import TestCase
from pandocfilters import Para, Str, Space, Link, Header, Cite, Span
import json

import pandoc_numbering

def init():
    pandoc_numbering.count = {}
    pandoc_numbering.information = {}
    pandoc_numbering.headers = [0, 0, 0, 0, 0, 0]
    if hasattr(pandoc_numbering.getCiteShortCut, 'value'):
        delattr(pandoc_numbering.getCiteShortCut, 'value')
    if hasattr(pandoc_numbering.getDefaultLevels, 'value'):
        delattr(pandoc_numbering.getDefaultLevels, 'value')
    if hasattr(pandoc_numbering.getClasses, 'value'):
        delattr(pandoc_numbering.getClasses, 'value')
    if hasattr(pandoc_numbering.getFormat, 'value'):
        delattr(pandoc_numbering.getFormat, 'value')

def createLink(attributes, text, reference_title):
    if pandoc_numbering.pandocVersion() < '1.16':
        return Link(text, reference_title)
    else:
        return Link(attributes, text, reference_title)

def test_referencing_simple():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'#exercise:first')])
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(
        ['', [], []],
        [],
        [u'#exercise:first', u'']
    )))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        [
            Str(u'Exercise'),
            Space(),
            Str(u'1')
        ],
        [u'#exercise:first', u'']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert json.loads(json.dumps(src)) == dest

def test_referencing_title():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'(The'), Space(), Str(u'title)'), Space(), Str(u'-.+.#exercise:first')])
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(
        ['', [], []],
        [],
        [u'#exercise:first', u'#d #D #t #T #s #g #c #n #']
    )))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        [
            Str(u'Exercise'),
            Space(),
            Str(u'0.1')
        ],
        [u'#exercise:first', u'exercise Exercise the title The title 0.0 0.0.1 1 0.1 0.1']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert json.loads(json.dumps(src)) == dest

def test_referencing_prefix():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'(The'), Space(), Str(u'title)'), Space(), Str(u'#exercise:first')])
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(
        ['', [], []],
        [Str(u'#d#D#t#T#n#')],
        [u'#exercise:first', u'']
    )))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        [
            Str(u'exercise'),
            Str(u'Exercise'),
            Str(u'the'),
            Space(),
            Str(u'title'),
            Str(u'The'),
            Space(),
            Str(u'title'),
            Str(u'1'),
            Str(u'1')
        ],
        [u'#exercise:first', u'']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert src == dest

def test_referencing_prefix_single():
    init()

    src = Header(1, [u'first-chapter', [], []], [Str(u'First'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = Para([Str(u'Exercise'), Space(), Str(u'+.#ex:')])
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(['', [], []], [Str(u'exercise'), Space(), Str(u'#')], [u'#ex:1.1', u''])))
    dest = json.loads(json.dumps(createLink(['', [], []], [Str(u'exercise'), Space(), Str(u'1.1')], [u'#ex:1.1', u''])))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert src == dest

def test_referencing_name():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'#first')])
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(['', [], []], [Str(u'exercise'), Space(), Str(u'#')], [u'#exercise:first', u''])))
    dest = json.loads(json.dumps(createLink(['', [], []], [Str(u'exercise'), Space(), Str(u'1')], [u'#exercise:first', u''])))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert src == dest

def test_referencing_automatic():
    init()

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(['', [], []], [], [u'#exercise:1', u''])))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        [
            Str(u'Exercise'),
            Space(),
            Str(u'1')
        ],
        [u'#exercise:1', u'']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert json.loads(json.dumps(src)) == dest

def test_referencing_unexisting():
    init()

    src = json.loads(json.dumps(createLink(['', [], []], [], [u'#exercise:second', u''])))
    dest = json.loads(json.dumps(createLink(['', [], []], [], [u'#exercise:second', u''])))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert src == dest

def test_referencing_headers():
    init()

    src = Header(1, [u'first-chapter', [], []], [Str(u'First'), Space(), Str('chapter')])
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = Para([Str(u'Theorem'), Space(), Str(u'+.#theorem:first')])
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(['', [], []], [], [u'#theorem:first', u''])))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        [
            Str(u'Theorem'),
            Space(),
            Str(u'1.1')
        ],
        [u'#theorem:first', u'']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert json.loads(json.dumps(src)) == dest

    src = json.loads(json.dumps(createLink(
        ['', [], []],
        [Str(u'See'), Space(), Str(u'theorem'), Space(), Str(u'#')],
        [u'#theorem:first', u'theorem #']
    )))
    dest = json.loads(json.dumps(
        createLink(['', [], []],
        [Str(u'See'), Space(), Str(u'theorem'), Space(), Str(u'1.1')],
        [u'#theorem:first', u'theorem 1.1']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert src == dest

def test_referencing_without_cite_shortcut():
    init()

    src = Para([Str(u'Theorem'), Space(), Str(u'#theorem:first')])
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = Cite([], [Str(u'@theorem:first')])
    dest = Cite([], [Str(u'@theorem:first')])

    assert pandoc_numbering.referencing(src['t'], src['c'], '', {}) == None
    assert src == dest

def test_referencing_with_cite_shortcut():
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
                            'c': [Str('theorem')]
                        },
                        'cite-shortcut': {
                            't': 'MetaBool',
                            'c': True
                        }
                    }
                }
            ]
        }
    }

    src = Para([Str(u'Theorem'), Space(), Str(u'#theorem:first')])
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(Cite([], [Str(u'@theorem:first')])))
    dest = json.loads(json.dumps(createLink(['', [], []], [Str(u'1')], [u'#theorem:first', u''])))

    assert json.loads(json.dumps(pandoc_numbering.referencing(src['t'], src['c'], '', meta))) == dest

def test_referencing_format():
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
                        'format': {
                            't': 'MetaBool',
                            'c': False
                        }
                    }
                }
            ]
        }
    }

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], u'', meta)

    src = json.loads(json.dumps(createLink(['', [], []], [], [u'#exercise:1', u''])))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        [
            Span(
                ['', ['pandoc-numbering-link', 'exercise'], []],
                [
                    Span(['', ['description'], []], [Str(u'Exercise')]),
                    Span(['', ['title'], []], []),
                    Span(['', ['local'], []], [Str(u'1')]),
                    Span(['', ['global'], []], [Str(u'1')]),
                    Span(['', ['section'], []], [Str(u'')]),
                ]
            )
        ],
        [u'#exercise:1', u'']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', meta)

    assert json.loads(json.dumps(src)) == dest


