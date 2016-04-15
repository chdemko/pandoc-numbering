#!/usr/bin/env python

"""
Pandoc filter to number all kinds of things.
"""

from pandocfilters import toJSONFilters, walk, stringify, Str, Space, Para, Strong, Span, Link, Emph, RawInline
from functools import reduce
import sys
import json
import io
import codecs
import re
import unicodedata
import subprocess

count = {}
information = {}
headers = [0, 0, 0, 0, 0, 0]

def removeAccents(string):
    nfkd_form = unicodedata.normalize('NFKD', string)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def toIdentifier(string):
    # replace invalid characters by dash
    string = re.sub('[^0-9a-zA-Z_-]+', '-', removeAccents(string.lower()))

    # Remove leading digits
    string = re.sub('^[^a-zA-Z]+', '', string)

    return string

def numbering(key, value, format, meta):
    if key == 'Header':
        [level, [id, classes, attributes], content] = value
        if 'unnumbered' not in classes:
            headers[level - 1] = headers[level - 1] + 1
            for index in range(level, 6):
                headers[index] = 0
    elif key == 'Para':
        length = len(value)
        if length >= 3 and value[-2] == Space() and value[-1]['t'] == 'Str':
            last = value[-1]['c']

            match = re.match('^((?P<header>(?P<hidden>(-\.)*)(#\.)*)#)(?P<prefix>[a-zA-Z][\w.-]*:)?(?P<name>[a-zA-Z][\w:.-]*)?$', last)

            if match:
                # Is it a Para and the last element is an identifier beginning with '#'
                global count, information

                # Detect the title
                title = None
                if value[-3]['t'] == 'Str' and value[-3]['c'][-1:] == ')':
                    for (i, item) in enumerate(value):
                        if item['t'] == 'Str' and item['c'][0] == '(':
                            title = Emph(value[i:-2])
                            value = value[:i - 1] + value[length - 2:]
                            length = i + 1
                            break

                # Compute the basicCategory and the category
                if match.group('prefix') == None:
                    basicCategory = toIdentifier(stringify(value[:-2])) + ':'
                else:
                    basicCategory = match.group('prefix')

                # Compute the levelInf and levelSup values
                levelInf = len(match.group('hidden')) // 2
                levelSup = len(match.group('header')) // 2

                # Get the default inf and sup level
                if levelInf == 0 and levelSup == 0:
                    [levelInf, levelSup] = getDefaultLevels(basicCategory[:-1], meta)

                # Compute the leading (composed of the section numbering)
                if levelSup != 0:
                    leading = '.'.join(map(str, headers[:levelSup])) + '.'
                else:
                    leading = ''

                category = basicCategory + leading

                # Is it a new category?
                if category not in count:
                    count[category] = 0

                count[category] = count[category] + 1

                # Get the number
                number = str(count[category])

                # Determine the final tag
                if match.group('name') == None:
                    tag = category + number
                else:
                    tag = basicCategory + match.group('name')

                # Replace the '#.#...#' by the category count (omitting the hidden part)
                value[-1]['c'] = '.'.join(map(str, headers[levelInf:levelSup] + [number]))

                # Prepare the final text
                text = [Strong(value)]

                # Add the title to the final text
                if title != None:
                    text.append(Space())
                    text.append(title)

                # Store the numbers and the label for automatic numbering (See referencing function)
                information[tag] = {'number': value[-1]['c'], 'text': value}

                # Prepare the contents
                contents = [Span([tag, [], []], text)]

                # Special case for LaTeX
                if format == 'latex':
                    contents.insert(0, RawInline('tex', '\\phantomsection'))

                # Return the contents in a Para element
                return Para(contents)
            elif re.match('^##([a-zA-Z][\w:.-]*)?$', last):
                # Special case where the last element is '##...'
                value[-1]['c'] = value[-1]['c'].replace('##', '#', 1)
                return Para(value)

replace = None

def referencing(key, value, format, meta):
    global information, replace

    # Is it a link with a right reference?
    if key == 'Link':
        if pandocVersion() < '1.16':
            # pandoc 1.15
            [text, [reference, title]] = value
        else:
            # pandoc 1.16
            [attributes, text, [reference, title]] = value

        if re.match('^#([a-zA-Z][\w:.-]*)?$', reference):
            # Compute the name
            tag = reference[1:]

            if tag in information:
                if pandocVersion() < '1.16':
                    # pandoc 1.15

                    # Replace all '#' with the corresponding number in the title
                    value[1][1] = title.replace('#', information[tag]['number'])
                    if text == []:
                        # The link text is empty, replace it with the default label
                        value[0] = information[tag]['text']
                    else:
                        # The link text is not empty, replace all '#' with the corresponding number
                        replace = information[tag]['number']
                        value[0] = walk(text, replacing, format, meta)
                else:
                    # pandoc 1.16

                    # Replace all '#' with the corresponding number in the title
                    value[2][1] = title.replace('#', information[tag]['number'])
                    if text == []:
                        # The link text is empty, replace it with the default label
                        value[1] = information[tag]['text']
                    else:
                        # The link text is not empty, replace all '#' with the corresponding number
                        replace = information[tag]['number']
                        value[1] = walk(text, replacing, format, meta)
    elif key == 'Cite':
        if hasCiteShortCut(meta):
            match = re.match('^@(?P<tag>[a-zA-Z][\w.-]*:(([a-zA-Z][\w.-]*)|(\d*(\.\d*)*)))$', value[1][0]['c'])
            if match != None:
                # Deal with @prefix:name shortcut
                tag = match.group('tag')
                if tag in information:
                    if pandocVersion() < '1.16':
                        return Link([Str(information[tag]['number'])], ['#' + tag, ''])
                    else:
                        return Link(['', [], []], [Str(information[tag]['number'])], ['#' + tag, ''])

def replacing(key, value, format, meta):
    global replace
    if key == 'Str' and value == '#':
        return Str(replace)

def hasCiteShortCut(meta):
    if not hasattr(hasCiteShortCut, 'value'):
        if 'pandoc-numbering' in meta and \
            meta['pandoc-numbering']['t'] == 'MetaMap' and \
            'cite-shortcut' in meta['pandoc-numbering']['c'] and\
            meta['pandoc-numbering']['c']['cite-shortcut']['t'] == 'MetaBool' and\
            meta['pandoc-numbering']['c']['cite-shortcut']['c']:
            hasCiteShortCut.value = True
        else:
            hasCiteShortCut.value = False
    return hasCiteShortCut.value


def getDefaultLevels(category, meta):
    if not hasattr(getDefaultLevels, 'value'):
        getDefaultLevels.value = {}
    if category not in getDefaultLevels.value:
        levelInf = 0
        levelSup = 0
        if 'pandoc-numbering' in meta and \
            meta['pandoc-numbering']['t'] == 'MetaMap' and \
            'categories' in meta['pandoc-numbering']['c'] and\
            meta['pandoc-numbering']['c']['categories']['t'] == 'MetaMap' and\
            category in meta['pandoc-numbering']['c']['categories']['c'] and\
            meta['pandoc-numbering']['c']['categories']['c'][category]['t'] == 'MetaInlines':
            if len(meta['pandoc-numbering']['c']['categories']['c'][category]['c']) == 1 and\
               meta['pandoc-numbering']['c']['categories']['c'][category]['c'][0]['t'] == 'Str':
                match = re.match(
                    '^(?P<header>(?P<hidden>(-\.)*)(#\.)*)$',
                    meta['pandoc-numbering']['c']['categories']['c'][category]['c'][0]['c']
                )
                if match:
                    # Compute the levelInf and levelSup values
                    levelInf = len(match.group('hidden')) // 2
                    levelSup = len(match.group('header')) // 2
        getDefaultLevels.value[category] = [levelInf, levelSup]
    return getDefaultLevels.value[category]

def pandocVersion():
    if not hasattr(pandocVersion, 'value'):
        p = subprocess.Popen(['pandoc', '-v'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = p.communicate()
        pandocVersion.value = re.search(b'pandoc (?P<version>.*)', out).group('version').decode('utf-8')
    return pandocVersion.value

def main():
    toJSONFilters([numbering, referencing])

if __name__ == '__main__':
    main()
