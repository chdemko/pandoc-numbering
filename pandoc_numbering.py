#!/usr/bin/env python

"""
Pandoc filter to number all kinds of things.
"""

from __future__ import print_function

from pandocfilters import walk, stringify, Str, Space, Para, BulletList, Plain, Strong, Span, Link, Emph, RawInline, RawBlock, Header
from functools import reduce
import json
import io
import sys
import codecs
import re
import unicodedata
import subprocess

def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

count = {}
information = {}
collections = {}
headers = [0, 0, 0, 0, 0, 0]
headerRegex = '(?P<header>(?P<hidden>(-\.)*)(\+\.)*)'

def toJSONFilters(actions):
    """Generate a JSON-to-JSON filter from stdin to stdout

    The filter:

    * reads a JSON-formatted pandoc document from stdin
    * transforms it by walking the tree and performing the actions
    * returns a new JSON-formatted pandoc document to stdout

    The argument `actions` is a list of functions of the form
    `action(key, value, format, meta)`, as described in more
    detail under `walk`.

    This function calls `applyJSONFilters`, with the `format`
    argument provided by the first command-line argument,
    if present.  (Pandoc sets this by default when calling
    filters.)
    """
    try:
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    except AttributeError:
        # Python 2 does not have sys.stdin.buffer.
        # REF: https://stackoverflow.com/questions/2467928/python-unicodeencode
        input_stream = codecs.getreader("utf-8")(sys.stdin)

    source = input_stream.read()
    if len(sys.argv) > 1:
        format = sys.argv[1]
    else:
        format = ""

    sys.stdout.write(applyJSONFilters(actions, source, format))

def applyJSONFilters(actions, source, format=""):
    """Walk through JSON structure and apply filters

    This:

    * reads a JSON-formatted pandoc document from a source string
    * transforms it by walking the tree and performing the actions
    * returns a new JSON-formatted pandoc document as a string

    The `actions` argument is a list of functions (see `walk`
    for a full description).

    The argument `source` is a string encoded JSON object.

    The argument `format` is a string describing the output format.

    Returns a the new JSON-formatted pandoc document.
    """

    doc = json.loads(source)

    if 'meta' in doc:
        meta = doc['meta']
    elif doc[0]:  # old API
        meta = doc[0]['unMeta']
    else:
        meta = {}
    altered = doc
    for action in actions:
        altered = walk(altered, action, format, meta)

    if 'meta' in altered:
        meta = altered['meta']
    elif meta[0]:  # old API
        meta = altered[0]['unMeta']
    else:
        meta = {}

    addListings(altered, format, meta)

    return json.dumps(altered)

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
    if key == 'Header':
        return numberingHeader(value)
    elif key == 'Para':
        return numberingPara(value, format, meta)

def numberingHeader(value):
    [level, [id, classes, attributes], content] = value
    if 'unnumbered' not in classes:
        headers[level - 1] = headers[level - 1] + 1
        for index in range(level, 6):
            headers[index] = 0

def numberingPara(value, format, meta):
    if len(value) >= 3 and value[-2]['t'] == 'Space' and value[-1]['t'] == 'Str':
        last = value[-1]['c']
        match = re.match('^' + headerRegex + '#((?P<prefix>[a-zA-Z][\w.-]*):)?(?P<name>[a-zA-Z][\w:.-]*)?$', last)
        if match:
            # Is it a Para and the last element is an identifier beginning with '#'
            return numberingEffective(match, value, format, meta)
        elif re.match('^' + headerRegex + '##(?P<prefix>[a-zA-Z][\w.-]*:)?(?P<name>[a-zA-Z][\w:.-]*)?$', last):
            # Special case where the last element is '...##...'
            return numberingSharpSharp(value)

def numberingEffective(match, value, format, meta):
    title = computeTitle(value)
    description = computeDescription(value)
    basicCategory = computeBasicCategory(match, description)
    [levelInf, levelSup] = computeLevels(match, basicCategory, meta)
    sectionNumber = computeSectionNumber(levelSup)
    leading = computeLeading(levelSup, sectionNumber)
    category = computeCategory(basicCategory, leading)
    number = str(count[category])
    tag = computeTag(match, basicCategory, category, number)
    localNumber = computeLocalNumber(levelInf, levelSup, number)
    globalNumber = computeGlobalNumber(sectionNumber, number)
    [text, link, toc] = computeTextLinkToc(meta, basicCategory, description, title, localNumber, globalNumber, sectionNumber)

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
        addLaTeX(contents, basicCategory, title, description, leading, number)

    # Return the contents in a Para element
    return Para(contents)

def computeTitle(value):
    title = []
    if value[-3]['t'] == 'Str' and value[-3]['c'][-1:] == ')':
        for (i, item) in enumerate(value):
            if item['t'] == 'Str' and item['c'][0] == '(':
                title = value[i:-2]
                title[0]['c'] = title[0]['c'][1:]
                title[-1]['c'] = title[-1]['c'][:-1]
                del value[i-1:-2]
                break
    return title

def computeDescription(value):
    return value[:-2]

def computeBasicCategory(match, description):
    if match.group('prefix') == None:
        return toIdentifier(stringify(description))
    else:
        return match.group('prefix')

def computeLevels(match, basicCategory, meta):
    # Compute the levelInf and levelSup values
    levelInf = len(match.group('hidden')) // 2
    levelSup = len(match.group('header')) // 2

    # Get the default inf and sup level
    if levelInf == 0 and levelSup == 0:
        [levelInf, levelSup] = getDefaultLevels(basicCategory, meta)

    return [levelInf, levelSup]

def computeSectionNumber(levelSup):
    return '.'.join(map(str, headers[:levelSup]))

def computeLeading(levelSup, sectionNumber):
    # Compute the leading (composed of the section numbering and a dot)
    if levelSup != 0:
        return sectionNumber + '.'
    else:
        return ''

def computeCategory(basicCategory, leading):
    category = basicCategory + ':' + leading

    # Is it a new category?
    if category not in count:
        count[category] = 0

    count[category] = count[category] + 1

    return category

def computeTag(match, basicCategory, category, number):
    # Determine the final tag
    if match.group('name') == None:
        return category + number
    else:
        return basicCategory + ':' + match.group('name')

def computeLocalNumber(levelInf, levelSup, number):
    # Replace the '-.-.+.+...#' by the category count (omitting the hidden part)
    return '.'.join(map(str, headers[levelInf:levelSup] + [number]))

def computeGlobalNumber(sectionNumber, number):
    # Compute the globalNumber
    if sectionNumber:
        return sectionNumber + '.' + number
    else:
        return number

def computeTextLinkToc(meta, basicCategory, description, title, localNumber, globalNumber, sectionNumber):
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
    return [text, link, toc]

def addLaTeX(contents, basicCategory, title, description, leading, number):
    latexCategory = re.sub('[^a-z]+', '', basicCategory)
    if title:
      entry = title
    else:
      entry = description
    latex = '\\phantomsection\\addcontentsline{' + latexCategory + '}{' + latexCategory + '}{\\protect\\numberline {' + \
        leading + number + '}{\ignorespaces ' + toLatex(entry) + '}}'
    contents.insert(0, RawInline('tex', latex))

def numberingSharpSharp(value):
    value[-1]['c'] = value[-1]['c'].replace('##', '#', 1)

replace = None
search = None

def lowering(key, value, format, meta):
    if key == 'Str':
        return Str(value.lower())

def referencing(key, value, format, meta):
    if key == 'Link':
        return referencingLink(value, format, meta)
    elif key == 'Cite':
        return referencingCite(value, format, meta)

def referencingLink(value, format, meta):
    global replace, search
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

def referencingCite(value, format, meta):
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

def hasMeta(meta):
    return 'pandoc-numbering' in meta and meta['pandoc-numbering']['t'] == 'MetaList'

def isCorrect(definition):
    return definition['t'] == 'MetaMap' and\
        'category' in definition['c'] and\
        definition['c']['category']['t'] == 'MetaInlines' and\
        len(definition['c']['category']['c']) == 1 and\
        definition['c']['category']['c'][0]['t'] == 'Str'

def hasProperty(definition, name, type):
    return name in definition['c'] and definition['c'][name]['t'] == type

def getProperty(definition, name):
    return definition['c'][name]['c']

def getFirstValue(definition, name):
	return getProperty(definition, name)[0]['c']

def addListings(doc, format, meta):
    if hasMeta(meta):
        listings = []

        # Loop on all listings definition
        for definition in meta['pandoc-numbering']['c']:
            if isCorrect(definition) and hasProperty(definition, 'listing', 'MetaInlines'):

                # Get the category name
                category = getFirstValue(definition, 'category')

                # Get the title
                title = getProperty(definition, 'listing')

                listings.append(Header(1, ['', ['unnumbered'], []], title))

                if format == 'latex':
                    extendListingsLaTeX(listings, meta, definition, category)
                else:
                    extendListingsOther(listings, meta, definition, category)

        # Add listings to the document
        if 'blocks' in doc:
            doc['blocks'][0:0] = listings
        else:  # old API
            doc[1][0:0] = listings

def extendListingsLaTeX(listings, meta, definition, category):
    space = getSpace(definition, category)
    tab = getTab(definition, category)
    # Add a RawBlock
    latexCategory = re.sub('[^a-z]+', '', category)
    latex = [
        getLinkColor(meta),
        '\\makeatletter',
        '\\newcommand*\\l@' + latexCategory + '{\\@dottedtocline{1}{' + str(tab) + 'em}{'+ str(space) +'em}}',
        '\\@starttoc{' + latexCategory + '}',
        '\\makeatother'
    ]
    listings.append(RawBlock('tex', ''.join(latex)))

def getLinkColor(meta):
    # Get the link color
    if 'toccolor' in meta:
        return '\\hypersetup{linkcolor=' + stringify(meta['toccolor']['c']) + '}'
    else:
        return '\\hypersetup{linkcolor=black}'

def getTab(definition, category):
    # Get the tab
    if hasProperty(definition, 'tab', 'MetaString'):
        try:
            tab = float(getProperty(definition, 'tab'))
        except ValueError:
            tab = None
    else:
        tab = None

    # Deal with default tab length
    if tab == None:
        return 1.5
    else:
        return tab

def getSpace(definition, category):
    # Get the space
    if hasProperty(definition, 'space', 'MetaString'):
        try:
            space = float(getProperty(definition, 'space'))
        except ValueError:
            space = None
    else:
        space = None

    # Deal with default space length
    if space == None:
        level = 0
        if category in collections:
            # Loop on the collection
            for tag in collections[category]:
                level = max(level, information[tag]['section'].count('.'))
        return level + 2.3
    else:
        return space

def extendListingsOther(listings, meta, definition, category):
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
        listings.append(BulletList(elements))

def getValue(category, meta, fct, default, analyzeDefinition):
    if not hasattr(fct, 'value'):
        fct.value = {}
        if hasMeta(meta):
            # Loop on all listings definition
            for definition in meta['pandoc-numbering']['c']:
                if isCorrect(definition):
                    analyzeDefinition(definition)

    if not category in fct.value:
        fct.value[category] = default

    return fct.value[category]

def getFormat(category, meta):
    def analyzeDefinition(definition):
        if hasProperty(definition, 'format', 'MetaBool'):
            getFormat.value[getFirstValue(definition, 'category')] = getProperty(definition, 'format')
        
    return getValue(category, meta, getFormat, True, analyzeDefinition)

def getCiteShortCut(category, meta):
    def analyzeDefinition(definition):
        if hasProperty(definition, 'cite-shortcut', 'MetaBool'):
            getCiteShortCut.value[getFirstValue(definition, 'category')] = getProperty(definition, 'cite-shortcut')

    return getValue(category, meta, getCiteShortCut, False, analyzeDefinition)

def getLevelsFromYaml(definition):
    levelInf = 0
    levelSup = 0
    if hasProperty(definition, 'first', 'MetaString'):
        try:
            levelInf = max(min(int(getProperty(definition, 'first')) - 1, 6), 0)
        except ValueError:
            pass
    if hasProperty(definition, 'last', 'MetaString'):
        try:
            levelSup = max(min(int(getProperty(definition, 'last')), 6), levelInf)
        except ValueError:
            pass
    return [levelInf, levelSup]

def getLevelsFromRegex(definition):
    match = re.match('^' + headerRegex + '$', getFirstValue(definition, 'sectioning'))
    if match:
        # Compute the levelInf and levelSup values
        return [len(match.group('hidden')) // 2, len(match.group('header')) // 2]
    else:
        return [0, 0]

def getDefaultLevels(category, meta):
    def analyzeDefinition(definition):
        if hasProperty(definition, 'sectioning', 'MetaInlines') and\
           len(getProperty(definition, 'sectioning')) == 1 and\
           getProperty(definition, 'sectioning')[0]['t'] == 'Str':

            getDefaultLevels.value[getFirstValue(definition, 'category')] = getLevelsFromRegex(definition)
        else:
            getDefaultLevels.value[getFirstValue(definition, 'category')] = getLevelsFromYaml(definition)

    return getValue(category, meta, getDefaultLevels, [0, 0], analyzeDefinition)

def getClasses(category, meta): 
    def analyzeDefinition(definition):
        if hasProperty(definition, 'classes', 'MetaList'):
            classes = []
            for elt in getProperty(definition, 'classes'):
                classes.append(stringify(elt))
            getClasses.value[getFirstValue(definition, 'category')] = classes

    return getValue(category, meta, getClasses, [category], analyzeDefinition)

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
