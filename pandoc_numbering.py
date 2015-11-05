#!/usr/bin/env python

"""
Pandoc filter to number all kinds of things.
"""

from pandocfilters import walk, stringify, Str, Space, Para, Strong, Span, Link, Emph
import sys
import json
import io
import codecs

count = {}
numbers = {}
labels = {}

def toJSONFilters(actions):
    """Converts a list of actions into a filter
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

    json.dump(altered, sys.stdout)

def numbering(key, value, format, meta):
    if key == 'Para':
        length = len(value)
        if length >= 3 and value[length - 2] == Space() and value[length - 1]['t'] == 'Str':
            last = value[length - 1]['c']
            if last[0] == '#':
                tag = last

                # Is it a Para and the last element is an identifier beginning with '#'
                if len(last) == 1 or last[1] != '#':
                    global count, numbers, labels

                    # Detect the title
                    title = None
                    if value[length - 3]['t'] == 'Str' and value[length - 3]['c'][-1:] == ')':
                        for (i, item) in enumerate(value):
                            if item['t'] == 'Str' and item['c'][0] == '(':
                                title = Emph(value[i - 1:length - 2])
                                value = value[:i - 1] + value[length - 2:]
                                length = i + 1
                                break

                    # Convert the value to a category (eliminating the '#')
                    category = stringify(value[:length - 2])
                    if category not in count:
                        count[category] = 0
                    count[category] = count[category] + 1

                    # Replace the '#' by the category count
                    value[length - 1]['c'] = str(count[category])

                    # Prepare the final text
                    text = [Strong(value)]

                    # Add the title to the final text
                    if title != None:
                        text.append(title)

                    if tag != '#':
                        # Store the numbers and the label for automatic numbering (See referencing function)
                        numbers[tag] = value[length - 1]['c']
                        labels[tag] = value

                        # Return the final text in a Span element embedded in a Para element
                        return Para([Span([tag[1:], [], []], text)])
                    else:
                        # Return the final text in a Para element
                        return Para(text)
                else:
                    # Special case where the last element is '##...'
                    value[length - 1]['c'].replace('##', '#', 1)
                    return Para(value)

def referencing(key, value, format, meta):
    global numbers, labels

    # Is it a link with a right tag?
    if key == 'Link' and value[1][0] in numbers:
       # Replace all '#' with the corresponding number in the title
       value[1][1] = value[1][1].replace('#', numbers[value[1][0]])

       if value[0] == []:
           # The link text is empty, replace it with the default label
           return Link(labels[value[1][0]], value[1])
       else:
           # The link text is not empty, replace all '#' with the corresponding number
           for (i, item) in enumerate(value[0]):
               if item == Str('#'):
                   value[0][i]['c'] = numbers[value[1][0]]
           return Link(value[0], value[1])

def main():
    toJSONFilters([numbering, referencing])

if __name__ == '__main__':
    main()
