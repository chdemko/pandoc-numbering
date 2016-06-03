#!/usr/bin/env python

"""
Pandoc filter to number all kinds of things.
"""

from pandocfilters import walk, stringify, Str, Space, Para, BulletList, Plain, Strong, Span, Link, Emph, RawInline, RawBlock, Header
from functools import reduce
import json
import io
import sys
import codecs
import re
import unicodedata
import subprocess

count = {}
information = {}
collections = {}
headers = [0, 0, 0, 0, 0, 0]
headerRegex = '(?P<header>(?P<hidden>(-\.)*)(\+\.)*)'

def toJSONFilters(actions):
    """Converts a list of actions into a filter that reads a JSON-formatted
    pandoc document from stdin, transforms it by walking the tree
    with the actions, and returns a new JSON-formatted pandoc document
    to stdout.  The argument is a list of functions action(key, value, format, meta),
    where key is the type of the pandoc object (e.g. 'Str', 'Para'),
    value is the contents of the object (e.g. a string for 'Str',
    a list of inline elements for 'Para'), format is the target
    output format (which will be taken for the first command line
    argument if present), and meta is the document's metadata.
    If the function returns None, the object to which it applies
    will remain unchanged.  If it returns an object, the object will
    be replaced.    If it returns a list, the list will be spliced in to
    the list to which the target object belongs.    (So, returning an
    empty list deletes the object.)
    """
    try:
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    except AttributeError:
        # Python 2 does not have sys.stdin.buffer.
        # REF: http://stackoverflow.com/questions/2467928/python-unicodeencodeerror-when-reading-from-stdin
        input_stream = codecs.getreader("utf-8")(sys.stdin)

    doc = json.loads(input_stream.read())
    if len(sys.argv) > 1:
        format = sys.argv[1]
    else:
        format = ""
    altered = reduce(lambda x, action: walk(x, action, format, doc[0]['unMeta']), actions, doc)
    addListings(altered, format, altered[0]['unMeta'])
    json.dump(altered, sys.stdout)

def removeAccents(string):
    nfkd_form = unicodedata.normalize('NFKD', string)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def toIdentifier(string):
    # replace invalid characters by dash
    string = re.sub('[^0-9a-zA-Z_-]+', '-', removeAccents(string.lower()))

    # Remove leading digits
    string = re.sub('^[^a-zA-Z]+', '', string)

    return string

def toLatex(x):
    """Walks the tree x and returns concatenated string content,
    leaving out all formatting.
    """
    result = []

    def go(key, val, format, meta):
        if key in ['Str', 'MetaString']:
            result.append(val)
        elif key == 'Code':
            result.append(val[1])
        elif key == 'Math':
            # Modified from the stringify function in the pandocfilter package
            if format == 'latex':
                result.append('$' + val[1] + '$')
            else:
                result.append(val[1])
        elif key == 'LineBreak':
            result.append(" ")
        elif key == 'Space':
            result.append(" ")
        elif key == 'Note':
            # Do not stringify value from Note node
            del val[:]

    walk(x, go, 'latex', {})
    return ''.join(result)

def numbering(key, value, format, meta):
    global headerRegex
    if key == 'Header':
        [level, [id, classes, attributes], content] = value
        if 'unnumbered' not in classes:
            headers[level - 1] = headers[level - 1] + 1
            for index in range(level, 6):
                headers[index] = 0
    elif key == 'Para':
        if len(value) >= 3 and value[-2] == Space() and value[-1]['t'] == 'Str':
            last = value[-1]['c']

            match = re.match('^' + headerRegex + '#((?P<prefix>[a-zA-Z][\w.-]*):)?(?P<name>[a-zA-Z][\w:.-]*)?$', last)

            if match:
                # Is it a Para and the last element is an identifier beginning with '#'
                global count, information, collections

                # Detect the title
                title = []
                if value[-3]['t'] == 'Str' and value[-3]['c'][-1:] == ')':
                    for (i, item) in enumerate(value):
                        if item['t'] == 'Str' and item['c'][0] == '(':
                            title = value[i:-2]
                            title[0]['c'] = title[0]['c'][1:]
                            title[-1]['c'] = title[-1]['c'][:-1]
                            value = value[:i - 1] + value[-2:]
                            break

                # Compute the description
                description = value[:-2]

                # Compute the basicCategory and the category
                if match.group('prefix') == None:
                    basicCategory = toIdentifier(stringify(description))
                else:
                    basicCategory = match.group('prefix')

                # Compute the levelInf and levelSup values
                levelInf = len(match.group('hidden')) // 2
                levelSup = len(match.group('header')) // 2

                # Get the default inf and sup level
                if levelInf == 0 and levelSup == 0:
                    [levelInf, levelSup] = getDefaultLevels(basicCategory, meta)

                # Compute the section number
                sectionNumber = '.'.join(map(str, headers[:levelSup]))

                # Compute the leading (composed of the section numbering and a dot)
                if levelSup != 0:
                    leading = sectionNumber + '.'
                else:
                    leading = ''

                category = basicCategory + ':' + leading

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
                    tag = basicCategory + ':' + match.group('name')

                # Replace the '-.-.+.+...#' by the category count (omitting the hidden part)
                localNumber = '.'.join(map(str, headers[levelInf:levelSup] + [number]))

                # Compute the globalNumber
                if sectionNumber:
                    globalNumber = sectionNumber + '.' + number
                else:
                    globalNumber = number

                # Is the automatic formatting required for this category?
                if getFormat(basicCategory, meta):
                    # Prepare the final text
                    text = [Strong(description + [Space(), Str(localNumber)])]

                    # Add the title to the final text
                    if title:
                        text = text + [Space(), Emph([Str('(')] + title + [Str(')')])]

                    # Compute the link
                    link = description + [Space(), Str(localNumber)]

                    # Compute the toc
                    toc = [Str(globalNumber), Space()]
                    if title:
                        toc = toc + title
                    else:
                        toc = toc + description

                else:
                    # Prepare the final text
                    text = [
                        Span(['', ['description'], []], description),
                        Span(['', ['title'], []], title),
                        Span(['', ['local'], []], [Str(localNumber)]),
                        Span(['', ['global'], []], [Str(globalNumber)]),
                        Span(['', ['section'], []], [Str(sectionNumber)]),
                    ]

                    # Compute the link
                    link = [Span(['', ['pandoc-numbering-link'] + getClasses(basicCategory, meta), []], text)]

                    # Compute the toc
                    toc = [Span(['', ['pandoc-numbering-toc'] + getClasses(basicCategory, meta), []], text)]


                # Store the numbers and the label for automatic numbering (See referencing function)
                information[tag] = {
                    'section': sectionNumber,
                    'local': localNumber,
                    'global': globalNumber,
                    'count': number,
                    'description': description,
                    'title': title,
                    'link': link,
                    'toc': toc
                }

                # Prepare the contents
                contents = [Span([tag, ['pandoc-numbering-text'] + getClasses(basicCategory, meta), []], text)]

                # Compute collections
                if basicCategory not in collections:
                    collections[basicCategory] = []

                collections[basicCategory].append(tag)

                # Special case for LaTeX
                if format == 'latex' and getFormat(basicCategory, meta):
                    latexCategory = re.sub('[^a-z]+', '', basicCategory)
                    if title:
                      entry = title
                    else:
                      entry = description
                    latex = '\\phantomsection\\addcontentsline{' + latexCategory + '}{' + latexCategory + '}{\\protect\\numberline {' + \
                        leading + number + '}{\ignorespaces ' + toLatex(entry) + '}}'
                    contents.insert(0, RawInline('tex', latex))

                # Return the contents in a Para element
                return Para(contents)
            elif re.match('^' + headerRegex + '##(?P<prefix>[a-zA-Z][\w.-]*:)?(?P<name>[a-zA-Z][\w:.-]*)?$', last):
                # Special case where the last element is '...##...'
                value[-1]['c'] = value[-1]['c'].replace('##', '#', 1)
                return Para(value)

replace = None
search = None

def lowering(key, value, format, meta):
    if key == 'Str':
        return Str(value.lower())

def referencing(key, value, format, meta):
    global information, replace, search

    # Is it a link with a right reference?
    if key == 'Link':
        if pandocVersion() < '1.16':
            # pandoc 1.15
            [text, [reference, title]] = value
        else:
            # pandoc > 1.15
            [attributes, text, [reference, title]] = value

        if re.match('^(#([a-zA-Z][\w:.-]*))$', reference):
            # Compute the name
            tag = reference[1:]

            if tag in information:
                if pandocVersion() < '1.16':
                    # pandoc 1.15
                    i = 0
                else:
                    # pandoc > 1.15
                    i = 1

                # Replace all '#t', '#T', '#d', '#D', '#s', '#g', '#c', '#n', '#' with the corresponding text in the title
                value[i + 1][1] = value[i + 1][1].replace('#t', stringify(information[tag]['title']).lower())
                value[i + 1][1] = value[i + 1][1].replace('#T', stringify(information[tag]['title']))
                value[i + 1][1] = value[i + 1][1].replace('#d', stringify(information[tag]['description']).lower())
                value[i + 1][1] = value[i + 1][1].replace('#D', stringify(information[tag]['description']))
                value[i + 1][1] = value[i + 1][1].replace('#s', information[tag]['section'])
                value[i + 1][1] = value[i + 1][1].replace('#g', information[tag]['global'])
                value[i + 1][1] = value[i + 1][1].replace('#c', information[tag]['count'])
                value[i + 1][1] = value[i + 1][1].replace('#n', information[tag]['local'])
                value[i + 1][1] = value[i + 1][1].replace('#', information[tag]['local'])

                if text == []:
                    # The link text is empty, replace it with the default label
                    value[i] = information[tag]['link']
                else:
                    # The link text is not empty

                    #replace all '#t' with the title in lower case
                    replace = walk(information[tag]['title'], lowering, format, meta)
                    search = '#t'
                    value[i] = walk(value[i], replacing, format, meta)

                    #replace all '#T' with the title
                    replace = information[tag]['title']
                    search = '#T'
                    value[i] = walk(value[i], replacing, format, meta)

                    #replace all '#d' with the description in lower case
                    replace = walk(information[tag]['description'], lowering, format, meta)
                    search = '#d'
                    value[i] = walk(value[i], replacing, format, meta)

                    #replace all '#D' with the description
                    replace = information[tag]['description']
                    search = '#D'
                    value[i] = walk(value[i], replacing, format, meta)

                    #replace all '#s' with the corresponding number
                    replace = [Str(information[tag]['section'])]
                    search = '#s'
                    value[i] = walk(value[i], replacing, format, meta)

                    #replace all '#g' with the corresponding number
                    replace = [Str(information[tag]['global'])]
                    search = '#g'
                    value[i] = walk(value[i], replacing, format, meta)

                    #replace all '#c' with the corresponding number
                    replace = [Str(information[tag]['count'])]
                    search = '#c'
                    value[i] = walk(value[i], replacing, format, meta)

                    #replace all '#n' with the corresponding number
                    replace = [Str(information[tag]['local'])]
                    search = '#n'
                    value[i] = walk(value[i], replacing, format, meta)

                    #replace all '#' with the corresponding number
                    replace = [Str(information[tag]['local'])]
                    search = '#'
                    value[i] = walk(value[i], replacing, format, meta)

    elif key == 'Cite':
        match = re.match('^(@(?P<tag>(?P<category>[a-zA-Z][\w.-]*):(([a-zA-Z][\w.-]*)|(\d*(\.\d*)*))))$', value[1][0]['c'])
        if match != None and getCiteShortCut(match.group('category'), meta):

            # Deal with @prefix:name shortcut
            tag = match.group('tag')
            if tag in information:
                if pandocVersion() < '1.16':
                    # pandoc 1.15
                    return Link([Str(information[tag]['local'])], ['#' + tag, ''])
                else:
                    # pandoc > 1.15
                    return Link(['', [], []], [Str(information[tag]['local'])], ['#' + tag, ''])

def replacing(key, value, format, meta):
    global replace, search
    if key == 'Str':
        prepare = value.split(search)
        if len(prepare) > 1:

            ret = []

            if prepare[0] != '':
                ret.append(Str(prepare[0]))

            for string in prepare[1:]:
                ret.extend(replace)
                if string != '':
                    ret.append(Str(string))

            return ret

def addListings(doc, format, meta):
    global collections, information
    if 'pandoc-numbering' in meta and meta['pandoc-numbering']['t'] == 'MetaList':

        listings = []

        # Loop on all listings definition
        for definition in meta['pandoc-numbering']['c']:
            if definition['t'] == 'MetaMap' and\
               'category' in definition['c'] and\
               'listing' in definition['c'] and\
               definition['c']['category']['t'] == 'MetaInlines' and\
               definition['c']['listing']['t'] == 'MetaInlines' and\
               len(definition['c']['category']['c']) == 1 and\
               definition['c']['category']['c'][0]['t'] == 'Str':

                # Get the category name
                category = definition['c']['category']['c'][0]['c']

                # Get the title
                title = definition['c']['listing']['c']

                if format == 'latex':

                    # Special case for latex output

                    # Get the link color
                    if 'toccolor' in meta:
                        linkcolor = '\\hypersetup{linkcolor=' + stringify(meta['toccolor']['c']) + '}'
                    else:
                        linkcolor = '\\hypersetup{linkcolor=black}'

                    # Get the tab
                    if 'tab' in definition['c'] and definition['c']['tab']['t'] == 'MetaString':
                        try:
                            tab = float(definition['c']['tab']['c'])
                        except ValueError:
                            tab = None
                    else:
                        tab = None

                    # Get the space
                    if 'space' in definition['c'] and definition['c']['space']['t'] == 'MetaString':
                        try:
                            space = float(definition['c']['space']['c'])
                        except ValueError:
                            space = None
                    else:
                        space = None

                    # Deal with default tab length
                    if tab == None:
                        tab = 1.5

                    # Deal with default space length
                    if space == None:
                        level = 0
                        if category in collections:
                            # Loop on the collection
                            for tag in collections[category]:
                                level = max(level, information[tag]['section'].count('.'))
                        space = level + 2.3

                    # Add a RawBlock
                    latexCategory = re.sub('[^a-z]+', '', category)
                    latex = [
                        linkcolor,
                        '\\makeatletter',
                        '\\newcommand*\\l@' + latexCategory + '{\\@dottedtocline{1}{' + str(tab) + 'em}{'+ str(space) +'em}}',
                        '\\@starttoc{' + latexCategory + '}',
                        '\\makeatother'
                    ]
                    elt = [RawBlock('tex', ''.join(latex))]
                else:
                    if category in collections:
                        # Prepare the list
                        elements = []

                        # Loop on the collection
                        for tag in collections[category]:

                            # Add an item to the list
                            text = information[tag]['toc']

                            if pandocVersion() < '1.16':
                                # pandoc 1.15
                                link = Link(text, ['#' + tag, ''])
                            else:
                                # pandoc 1.16
                                link = Link(['', [], []], text, ['#' + tag, ''])

                            elements.append([Plain([link])])

                        # Add a bullet list
                        elt = [BulletList(elements)]
                    else:

                        # Add nothing
                        elt = []

                # Add a new listing
                listings = listings + [Header(1, ['', ['unnumbered'], []], title)] + elt

        # Add listings to the document
        doc[1] = listings + doc[1]

def getFormat(category, meta):
    if not hasattr(getFormat, 'value'):
        getFormat.value = {}

        if 'pandoc-numbering' in meta and meta['pandoc-numbering']['t'] == 'MetaList':

            # Loop on all listings definition
            for definition in meta['pandoc-numbering']['c']:

                if definition['t'] == 'MetaMap' and\
                   'format' in definition['c'] and\
                   'category' in definition['c'] and\
                   definition['c']['category']['t'] == 'MetaInlines' and\
                   len(definition['c']['category']['c']) == 1 and\
                   definition['c']['category']['c'][0]['t'] == 'Str' and\
                   definition['c']['format']['t'] == 'MetaBool':

                    getFormat.value[definition['c']['category']['c'][0]['c']] = definition['c']['format']['c']

    if not category in getFormat.value:

        getFormat.value[category] = True

    return getFormat.value[category]

def getCiteShortCut(category, meta):
    if not hasattr(getCiteShortCut, 'value'):
        getCiteShortCut.value = {}

        if 'pandoc-numbering' in meta and meta['pandoc-numbering']['t'] == 'MetaList':

            # Loop on all listings definition
            for definition in meta['pandoc-numbering']['c']:

                if definition['t'] == 'MetaMap' and\
                   'cite-shortcut' in definition['c'] and\
                   'category' in definition['c'] and\
                   definition['c']['category']['t'] == 'MetaInlines' and\
                   len(definition['c']['category']['c']) == 1 and\
                   definition['c']['category']['c'][0]['t'] == 'Str' and\
                   definition['c']['cite-shortcut']['t'] == 'MetaBool':

                    getCiteShortCut.value[definition['c']['category']['c'][0]['c']] = definition['c']['cite-shortcut']['c']

    if not category in getCiteShortCut.value:

        getCiteShortCut.value[category] = False

    return getCiteShortCut.value[category]

def getDefaultLevels(category, meta):
    if not hasattr(getDefaultLevels, 'value'):

        getDefaultLevels.value = {}

        if 'pandoc-numbering' in meta and meta['pandoc-numbering']['t'] == 'MetaList':

            # Loop on all listings definition
            for definition in meta['pandoc-numbering']['c']:

                if definition['t'] == 'MetaMap' and\
                   'category' in definition['c'] and\
                   definition['c']['category']['t'] == 'MetaInlines' and\
                   len(definition['c']['category']['c']) == 1 and\
                   definition['c']['category']['c'][0]['t'] == 'Str':

                    levelInf = 0
                    levelSup = 0

                    if 'sectioning' in definition['c'] and\
                       definition['c']['sectioning']['t'] == 'MetaInlines' and\
                       len(definition['c']['sectioning']['c']) == 1 and\
                       definition['c']['sectioning']['c'][0]['t'] == 'Str':

                        global headerRegex

                        match = re.match('^' + headerRegex + '$', definition['c']['sectioning']['c'][0]['c'])
                        if match:
                            # Compute the levelInf and levelSup values
                            levelInf = len(match.group('hidden')) // 2
                            levelSup = len(match.group('header')) // 2

                    else:

                        if 'first' in definition['c'] and definition['c']['first']['t'] == 'MetaString':
                            try:
                                levelInf = max(min(int(definition['c']['first']['c']) - 1, 6), 0)
                            except ValueError:
                                pass

                        if 'last' in definition['c'] and definition['c']['last']['t'] == 'MetaString':
                            try:
                                levelSup = max(min(int(definition['c']['last']['c']), 6), levelInf)
                            except ValueError:
                                pass

                    getDefaultLevels.value[definition['c']['category']['c'][0]['c']] = [levelInf, levelSup]

    if not category in getDefaultLevels.value:

        getDefaultLevels.value[category] = [0, 0]

    return getDefaultLevels.value[category]

def getClasses(category, meta):
    if not hasattr(getClasses, 'value'):

        getClasses.value = {}

        if 'pandoc-numbering' in meta and meta['pandoc-numbering']['t'] == 'MetaList':

            # Loop on all listings definition
            for definition in meta['pandoc-numbering']['c']:

                if definition['t'] == 'MetaMap' and\
                   'category' in definition['c'] and\
                   definition['c']['category']['t'] == 'MetaInlines' and\
                   len(definition['c']['category']['c']) == 1 and\
                   definition['c']['category']['c'][0]['t'] == 'Str':

                    if 'classes' in definition['c'] and definition['c']['classes']['t'] == 'MetaList':

                        classes = []

                        for elt in definition['c']['classes']['c']:
                            classes.append(stringify(elt))

                        getClasses.value[definition['c']['category']['c'][0]['c']] = classes

    if not category in getClasses.value:

        getClasses.value[category] = [category]

    return getClasses.value[category]

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
