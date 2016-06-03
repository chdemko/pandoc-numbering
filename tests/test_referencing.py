# This Python file uses the following encoding: utf-8

from unittest import TestCase
from pandocfilters import Para, Str, Space, Link, Header, Cite, Span
import json

import pandoc_numbering

from helper import init, createLink, createMetaList, createMetaMap, createMetaInlines, createListStr, createMetaString, createMetaBool

def getMeta1():
    return {
        'pandoc-numbering': createMetaList([
            createMetaMap({
                'category': createMetaInlines(u'theorem'),
                'cite-shortcut': createMetaBool(True)
            })
        ])
    }

def getMeta2():
    return {
        'pandoc-numbering': createMetaList([
            createMetaMap({
                'category': createMetaInlines(u'exercise'),
                'format': createMetaBool(False)
            })
        ])
    }

def test_referencing_simple():
    init()

    src = Para(createListStr(u'Exercise #exercise:first'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(
        ['', [], []],
        [],
        [u'#exercise:first', u'']
    )))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        createListStr(u'Exercise 1'),
        [u'#exercise:first', u'']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert json.loads(json.dumps(src)) == dest

def test_referencing_title():
    init()

    src = Para(createListStr(u'Exercise (The title) -.+.#exercise:first'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(
        ['', [], []],
        [],
        [u'#exercise:first', u'#d #D #t #T #s #g #c #n #']
    )))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        createListStr(u'Exercise 0.1'),
        [u'#exercise:first', u'exercise Exercise the title The title 0.0 0.0.1 1 0.1 0.1']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert json.loads(json.dumps(src)) == dest

def test_referencing_prefix():
    init()

    src = Para(createListStr(u'Exercise (The title) #exercise:first'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(
        ['', [], []],
        createListStr(u'#d#D#t#T#n#'),
        [u'#exercise:first', u'']
    )))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        createListStr(u'exercise') +
        createListStr(u'Exercise') +
        createListStr(u'the title') +
        createListStr(u'The title') +
        createListStr(u'1') +
        createListStr(u'1'),
        [u'#exercise:first', u'']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert src == dest

def test_referencing_prefix_single():
    init()

    src = Header(1, [u'first-chapter', [], []], createListStr(u'First chapter'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = Para(createListStr(u'Exercise +.#ex:'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(['', [], []], createListStr(u'exercise #'), [u'#ex:1.1', u''])))
    dest = json.loads(json.dumps(createLink(['', [], []], createListStr(u'exercise 1.1'), [u'#ex:1.1', u''])))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert src == dest

def test_referencing_name():
    init()

    src = Para(createListStr(u'Exercise #first'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(['', [], []], createListStr(u'exercise #'), [u'#exercise:first', u''])))
    dest = json.loads(json.dumps(createLink(['', [], []], createListStr(u'exercise 1'), [u'#exercise:first', u''])))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert src == dest

def test_referencing_automatic():
    init()

    src = Para(createListStr(u'Exercise #'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(['', [], []], [], [u'#exercise:1', u''])))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        createListStr(u'Exercise 1'),
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

    src = Header(1, [u'first-chapter', [], []], createListStr(u'First chapter'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = Para(createListStr(u'Theorem +.#theorem:first'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(['', [], []], [], [u'#theorem:first', u''])))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        createListStr(u'Theorem 1.1'),
        [u'#theorem:first', u'']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert json.loads(json.dumps(src)) == dest

    src = json.loads(json.dumps(createLink(
        ['', [], []],
        createListStr(u'See theorem #'),
        [u'#theorem:first', u'theorem #']
    )))
    dest = json.loads(json.dumps(
        createLink(['', [], []],
        createListStr(u'See theorem 1.1'),
        [u'#theorem:first', u'theorem 1.1']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert src == dest

def test_referencing_without_cite_shortcut():
    init()

    src = Para(createListStr(u'Theorem #theorem:first'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = Cite([], createListStr(u'@theorem:first'))
    dest = Cite([], createListStr(u'@theorem:first'))

    assert pandoc_numbering.referencing(src['t'], src['c'], '', {}) == None
    assert src == dest

def test_referencing_with_cite_shortcut():
    init()

    meta = getMeta1()

    src = Para(createListStr(u'Theorem #theorem:first'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(Cite([], [Str(u'@theorem:first')])))
    dest = json.loads(json.dumps(createLink(['', [], []], [Str(u'1')], [u'#theorem:first', u''])))

    assert json.loads(json.dumps(pandoc_numbering.referencing(src['t'], src['c'], '', meta))) == dest

def test_referencing_format():
    init()

    meta = getMeta2()

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], u'', meta)

    src = json.loads(json.dumps(createLink(['', [], []], [], [u'#exercise:1', u''])))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        [
            Span(
                ['', ['pandoc-numbering-link', 'exercise'], []],
                [
                    Span(['', ['description'], []], createListStr(u'Exercise')),
                    Span(['', ['title'], []], []),
                    Span(['', ['local'], []], createListStr(u'1')),
                    Span(['', ['global'], []], createListStr(u'1')),
                    Span(['', ['section'], []], createListStr(u'')),
                ]
            )
        ],
        [u'#exercise:1', u'']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', meta)

    assert json.loads(json.dumps(src)) == dest


