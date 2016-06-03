# This Python file uses the following encoding: utf-8

from unittest import TestCase
from pandocfilters import Para, Str, Space, Header, BulletList, Span, Strong, Plain, Link, RawBlock

import json

import pandoc_numbering

from helper import init, createLink, createMetaList, createMetaMap, createMetaInlines, createListStr, createMetaString

def getMeta1():
    return {
        'pandoc-numbering': createMetaList([
            createMetaMap({
                'category': createMetaInlines(u'exercise'),
                'listing': createMetaInlines(u'Listings of exercises'),
                'sectioning': createMetaInlines(u'-.+.')
            })
        ])
    }

def getMeta2():
    return {
        'pandoc-numbering': createMetaList([
            createMetaMap({
                'category': createMetaInlines(u'exercise'),
                'listing': createMetaInlines(u'Listings of exercises'),
                'sectioning': createMetaInlines(u'-.+.'),
                'tab': createMetaString(u'2'),
                'space': createMetaString(u'4'),
            })
        ])
    }

def getMeta3():
    return {
        'pandoc-numbering': createMetaList([
            createMetaMap({
                'category': createMetaInlines(u'exercise'),
                'listing': createMetaInlines(u'Listings of exercises'),
                'sectioning': createMetaInlines(u'-.+.'),
                'tab': createMetaString(u'a'),
                'space': createMetaString(u'b'),
            })
        ])
    }

def test_listing_classic():
    init()

    meta = getMeta1()

    src = Para(createListStr(u'Exercise #'))
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)
    src = Para(createListStr(u'Exercise (test) #'))
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)

    doc = [[{'unMeta': meta}], []]
    pandoc_numbering.addListings(doc, '', meta)

    dest = [
        Header(1, ['', ['unnumbered'], []], createListStr(u'Listings of exercises')),
	    BulletList([
	    	[Plain([createLink(['', [], []], createListStr(u'0.0.1 Exercise'), ['#exercise:0.0.1', ''])])],
	    	[Plain([createLink(['', [], []], createListStr(u'0.0.2 test'), ['#exercise:0.0.2', ''])])]
	    ])
	]

    assert json.loads(json.dumps(doc[1])) == json.loads(json.dumps(dest))

def test_listing_latex():
    init()

    meta = getMeta1()

    src = Para(createListStr(u'Exercise #'))
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)
    src = Para(createListStr(u'Exercise (test) #'))
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)

    doc = [[{'unMeta': meta}], []]
    pandoc_numbering.addListings(doc, 'latex', meta)

    dest = [
        Header(1, ['', ['unnumbered'], []], createListStr(u'Listings of exercises')),
        RawBlock(
            'tex',
            ''.join([
                '\\hypersetup{linkcolor=black}',
                '\\makeatletter',
                '\\newcommand*\\l@exercise{\\@dottedtocline{1}{1.5em}{3.3em}}',
                '\\@starttoc{exercise}',
                '\\makeatother'
            ])
        )
    ]

    assert json.loads(json.dumps(doc[1])) == json.loads(json.dumps(dest))

def test_listing_latex_color():
    init()

    meta = getMeta1()
    meta['toccolor']= createMetaInlines(u'blue')

    src = Para(createListStr(u'Exercise #'))
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)
    src = Para(createListStr(u'Exercise (test) #'))
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)

    doc = [[{'unMeta': meta}], []]
    pandoc_numbering.addListings(doc, 'latex', meta)

    dest = [
        Header(1, ['', ['unnumbered'], []], createListStr(u'Listings of exercises')),
        RawBlock(
            'tex',
            ''.join([
                '\\hypersetup{linkcolor=blue}',
                '\\makeatletter',
                '\\newcommand*\\l@exercise{\\@dottedtocline{1}{1.5em}{3.3em}}',
                '\\@starttoc{exercise}',
                '\\makeatother'
            ])
        )
    ]

    assert json.loads(json.dumps(doc[1])) == json.loads(json.dumps(dest))

def test_listing_latex_tab_space():
    init()

    meta = getMeta2()

    src = Para(createListStr(u'Exercise #'))
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)
    src = Para(createListStr(u'Exercise (test) #'))
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)

    doc = [[{'unMeta': meta}], []]
    pandoc_numbering.addListings(doc, 'latex', meta)

    dest = [
        Header(1, ['', ['unnumbered'], []], createListStr(u'Listings of exercises')),
        RawBlock(
            'tex',
            '\\hypersetup{linkcolor=black}\\makeatletter\\newcommand*\\l@exercise{\\@dottedtocline{1}{2.0em}{4.0em}}\\@starttoc{exercise}\\makeatother'
        )
    ]

    assert json.loads(json.dumps(doc[1])) == json.loads(json.dumps(dest))

def test_listing_latex_tab_space_error():
    init()

    meta = getMeta3()
    src = Para(createListStr(u'Exercise #'))
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)
    src = Para(createListStr(u'Exercise (test) #'))
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)

    doc = [[{'unMeta': meta}], []]
    pandoc_numbering.addListings(doc, 'latex', meta)

    dest = [
        Header(1, ['', ['unnumbered'], []], createListStr(u'Listings of exercises')),
        RawBlock(
            'tex',
            '\\hypersetup{linkcolor=black}\\makeatletter\\newcommand*\\l@exercise{\\@dottedtocline{1}{1.5em}{3.3em}}\\@starttoc{exercise}\\makeatother'
        )
    ]

    assert json.loads(json.dumps(doc[1])) == json.loads(json.dumps(dest))

