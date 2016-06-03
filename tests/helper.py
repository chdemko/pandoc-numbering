# This Python file uses the following encoding: utf-8

from pandocfilters import Link, Str, Space

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

def createMetaList(data):
    return {'t': 'MetaList', 'c': data}

def createMetaMap(data):
    return {'t': 'MetaMap', 'c': data}

def createMetaInlines(string):
    return {'t': 'MetaInlines', 'c': createListStr(string)}

def createMetaString(string):
    return {'t': 'MetaString', 'c': string}

def createMetaBool(boolean):
    return {'t': 'MetaBool', 'c': boolean}

def createListStr(string):
    elements = string.split(' ')
    result = [Str(elements[0])]
    for elt in elements[1:]:
        result.append(Space())
        result.append(Str(elt))
    return result

