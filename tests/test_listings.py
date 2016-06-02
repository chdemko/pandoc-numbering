# This Python file uses the following encoding: utf-8

from unittest import TestCase
from pandocfilters import Para, Str, Space, Header, BulletList, Span, Strong, Plain, Link, RawBlock

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

def createLink(attributes, text, reference_title):
    if pandoc_numbering.pandocVersion() < '1.16':
        return Link(text, reference_title)
    else:
        return Link(attributes, text, reference_title)

def test_listing_classic():
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
                        'listing': {
                            't': 'MetaInlines',
                            'c': [Str('Listings'), Space(), Str('of'), Space(), Str('exercises')]
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

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)
    src = Para([Str(u'Exercise'), Space(), Str('(test)'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], '', meta)

    doc = [[{'unMeta': meta}], []]
    pandoc_numbering.addListings(doc, '', meta)

    dest = [
        Header(
			1,
			['', ['unnumbered'], []],
	        [Str('Listings'), Space(), Str('of'), Space(), Str('exercises')]
	    ),
	    BulletList([
	    	[Plain([createLink(['', [], []], [Str('0.0.1'), Space(), Str('Exercise')], ['#exercise:0.0.1', ''])])],
	    	[Plain([createLink(['', [], []], [Str('0.0.2'), Space(), Str('test')], ['#exercise:0.0.2', ''])])]
	    ])
	]

    assert json.loads(json.dumps(doc[1])) == json.loads(json.dumps(dest))

def test_listing_latex():
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
                        'listing': {
                            't': 'MetaInlines',
                            'c': [Str('Listings'), Space(), Str('of'), Space(), Str('exercises')]
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

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)
    src = Para([Str(u'Exercise'), Space(), Str('(test)'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)

    doc = [[{'unMeta': meta}], []]
    pandoc_numbering.addListings(doc, 'latex', meta)

    dest = [
        Header(1, ['', ['unnumbered'], []], [Str('Listings'), Space(), Str('of'), Space(), Str('exercises')]),
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

    meta = {
        'toccolor': {
            't': 'MetaInlines',
            'c': [Str('blue')]
        },
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
                        'listing': {
                            't': 'MetaInlines',
                            'c': [Str('Listings'), Space(), Str('of'), Space(), Str('exercises')]
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

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)
    src = Para([Str(u'Exercise'), Space(), Str('(test)'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)

    doc = [[{'unMeta': meta}], []]
    pandoc_numbering.addListings(doc, 'latex', meta)

    dest = [
        Header(1, ['', ['unnumbered'], []], [Str('Listings'), Space(), Str('of'), Space(), Str('exercises')]),
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
                        'listing': {
                            't': 'MetaInlines',
                            'c': [Str('Listings'), Space(), Str('of'), Space(), Str('exercises')]
                        },
                        'sectioning': {
                            't': 'MetaInlines',
                            'c': [Str('-.+.')]
                        },
                        'tab': {
                            't': 'MetaString',
                            'c': '2'
                        },
                        'space': {
                            't': 'MetaString',
                            'c': '4'
                        }
                    }
                }
            ]
        }
    }

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)
    src = Para([Str(u'Exercise'), Space(), Str('(test)'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)

    doc = [[{'unMeta': meta}], []]
    pandoc_numbering.addListings(doc, 'latex', meta)

    dest = [
        Header(1, ['', ['unnumbered'], []], [Str('Listings'), Space(), Str('of'), Space(), Str('exercises')]),
        RawBlock(
            'tex',
            '\\hypersetup{linkcolor=black}\\makeatletter\\newcommand*\\l@exercise{\\@dottedtocline{1}{2.0em}{4.0em}}\\@starttoc{exercise}\\makeatother'
        )
    ]

    assert json.loads(json.dumps(doc[1])) == json.loads(json.dumps(dest))

def test_listing_latex_tab_space_error():
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
                        'listing': {
                            't': 'MetaInlines',
                            'c': [Str('Listings'), Space(), Str('of'), Space(), Str('exercises')]
                        },
                        'sectioning': {
                            't': 'MetaInlines',
                            'c': [Str('-.+.')]
                        },
                        'tab': {
                            't': 'MetaString',
                            'c': 'a'
                        },
                        'space': {
                            't': 'MetaString',
                            'c': 'b'
                        }
                    }
                }
            ]
        }
    }

    src = Para([Str(u'Exercise'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)
    src = Para([Str(u'Exercise'), Space(), Str('(test)'), Space(), Str(u'#')])
    pandoc_numbering.numbering(src['t'], src['c'], 'latex', meta)

    doc = [[{'unMeta': meta}], []]
    pandoc_numbering.addListings(doc, 'latex', meta)

    dest = [
        Header(1, ['', ['unnumbered'], []], [Str('Listings'), Space(), Str('of'), Space(), Str('exercises')]),
        RawBlock(
            'tex',
            '\\hypersetup{linkcolor=black}\\makeatletter\\newcommand*\\l@exercise{\\@dottedtocline{1}{1.5em}{3.3em}}\\@starttoc{exercise}\\makeatother'
        )
    ]

    assert json.loads(json.dumps(doc[1])) == json.loads(json.dumps(dest))

