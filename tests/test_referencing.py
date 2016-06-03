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

    src = Para(createListStr('Exercise #exercise:first'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(
        ['', [], []],
        [],
        [u'#exercise:first', u'']
    )))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        createListStr('Exercise 1'),
        [u'#exercise:first', u'']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert json.loads(json.dumps(src)) == dest

def test_referencing_title():
    init()

    src = Para(createListStr('Exercise (The title) -.+.#exercise:first'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(
        ['', [], []],
        [],
        [u'#exercise:first', u'#d #D #t #T #s #g #c #n #']
    )))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        createListStr('Exercise 0.1'),
        [u'#exercise:first', u'exercise Exercise the title The title 0.0 0.0.1 1 0.1 0.1']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert json.loads(json.dumps(src)) == dest

def test_referencing_prefix():
    init()

    src = Para(createListStr('Exercise (The title) #exercise:first'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(
        ['', [], []],
        createListStr('#d#D#t#T#n#'),
        [u'#exercise:first', u'']
    )))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        createListStr('exercise') +
        createListStr('Exercise') +
        createListStr('the title') +
        createListStr('The title') +
        createListStr('1') +
        createListStr('1'),
        [u'#exercise:first', u'']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert src == dest

def test_referencing_prefix_single():
    init()

    src = Header(1, [u'first-chapter', [], []], createListStr('First chapter'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = Para(createListStr('Exercise +.#ex:'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(['', [], []], createListStr('exercise #'), [u'#ex:1.1', u''])))
    dest = json.loads(json.dumps(createLink(['', [], []], createListStr('exercise 1.1'), [u'#ex:1.1', u''])))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert src == dest

def test_referencing_name():
    init()

    src = Para(createListStr('Exercise #first'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(['', [], []], createListStr('exercise #'), [u'#exercise:first', u''])))
    dest = json.loads(json.dumps(createLink(['', [], []], createListStr('exercise 1'), [u'#exercise:first', u''])))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert src == dest

def test_referencing_automatic():
    init()

    src = Para(createListStr('Exercise #'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(['', [], []], [], [u'#exercise:1', u''])))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        createListStr('Exercise 1'),
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

    src = Header(1, [u'first-chapter', [], []], createListStr('First chapter'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = Para(createListStr('Theorem +.#theorem:first'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = json.loads(json.dumps(createLink(['', [], []], [], [u'#theorem:first', u''])))
    dest = json.loads(json.dumps(createLink(
        ['', [], []],
        createListStr('Theorem 1.1'),
        [u'#theorem:first', u'']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert json.loads(json.dumps(src)) == dest

    src = json.loads(json.dumps(createLink(
        ['', [], []],
        createListStr('See theorem #'),
        [u'#theorem:first', u'theorem #']
    )))
    dest = json.loads(json.dumps(
        createLink(['', [], []],
        createListStr('See theorem 1.1'),
        [u'#theorem:first', u'theorem 1.1']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', {})
    assert src == dest

def test_referencing_without_cite_shortcut():
    init()

    src = Para(createListStr('Theorem #theorem:first'))
    pandoc_numbering.numbering(src['t'], src['c'], u'', {})

    src = Cite([], createListStr('@theorem:first'))
    dest = Cite([], createListStr('@theorem:first'))

    assert pandoc_numbering.referencing(src['t'], src['c'], '', {}) == None
    assert src == dest

def test_referencing_with_cite_shortcut():
    init()

    meta = getMeta1()

    src = Para(createListStr('Theorem #theorem:first'))
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
                    Span(['', ['description'], []], createListStr('Exercise')),
                    Span(['', ['title'], []], []),
                    Span(['', ['local'], []], createListStr('1')),
                    Span(['', ['global'], []], createListStr('1')),
                    Span(['', ['section'], []], createListStr('')),
                ]
            )
        ],
        [u'#exercise:1', u'']
    )))

    pandoc_numbering.referencing(src['t'], src['c'], '', meta)

    assert json.loads(json.dumps(src)) == dest


