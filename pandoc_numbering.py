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
        if length >= 3 and value[length - 2] == Space() and value[length - 1]['t'] == 'Str':
            last = value[length - 1]['c']

            match = re.match('^((?P<header>(?P<hidden>(_\.)*)(#\.)*)#)(?P<tag>[a-zA-Z][\w:.-]*)?$', last)
            if match:
                # Is it a Para and the last element is an identifier beginning with '#'
                global count, information

                # Detect the title
                title = None
                if value[length - 3]['t'] == 'Str' and value[length - 3]['c'][-1:] == ')':
                    for (i, item) in enumerate(value):
                        if item['t'] == 'Str' and item['c'][0] == '(':
                            title = Emph(value[i:length - 2])
                            value = value[:i - 1] + value[length - 2:]
                            length = i + 1
                            break

                # Convert the value to a name
                levelInf = len(match.group('hidden')) // 2
                levelSup = len(match.group('header')) // 2
                name = toIdentifier(stringify(value[:length - 2])) + ':'
                if levelSup != 0:
                    name = name + '.'.join(map(str, headers[:levelSup])) + '.'

                # Is it a new category?
                if name not in count:
                    count[name] = 0

                count[name] = count[name] + 1

                # Get the number
                number = str(count[name])

                # Determine the tag
                if match.group('tag') == None:
                    tag = name + number
                else:
                    tag = match.group('tag')

                # Replace the '#.#...#' by the name count
                value[length - 1]['c'] = '.'.join(map(str, headers[levelInf:levelSup] + [number]))

                # Prepare the final text
                text = [Strong(value)]

                # Add the title to the final text
                if title != None:
                    text.append(Space())
                    text.append(title)

                # Store the numbers and the label for automatic numbering (See referencing function)
                information[tag] = {'number': value[length - 1]['c'], 'text': value}

                # Prepare the contents
                contents = [Span([tag, [], []], text)]

                # Special case for LaTeX
                if format == 'latex':
                    contents.insert(0, RawInline('tex', '\\phantomsection'))

                # Return the contents in a Para element
                return Para(contents)
            elif re.match('^##([a-zA-Z][\w:.-]*)?$', last):
                # Special case where the last element is '##...'
                value[length - 1]['c'] = value[length - 1]['c'].replace('##', '#', 1)
                return Para(value)

replace = None

def referencing(key, value, format, meta):
    global information, replace

    # Is it a link with a right reference?
    if key == 'Link':
        if pandoc_version() < '1.16':
            # pandoc 1.15
            [text, [reference, title]] = value
        else:
            # pandoc 1.16
            [attributes, text, [reference, title]] = value

        if re.match('^#([a-zA-Z][\w:.-]*)?$', reference):
            # Compute the name
            tag = reference[1:]

            if tag in information:
                if pandoc_version() < '1.16':
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

def replacing(key, value, format, meta):
    global replace
    if key == 'Str' and value == '#':
        return Str(replace)

def pandoc_version():
    if not hasattr(pandoc_version, "version"):
        p = subprocess.Popen(['pandoc', '-v'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = p.communicate()
        pandoc_version.version = re.search(b'pandoc (?P<version>.*)', out).group('version').decode('utf-8')
    return pandoc_version.version

def main():
    toJSONFilters([numbering, referencing])

if __name__ == '__main__':
    main()
