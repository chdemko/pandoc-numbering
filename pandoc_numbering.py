#!/usr/bin/env python

"""
Pandoc filter to number all kinds of things.
"""

from panflute import *
from functools import partial
import re
import unicodedata
import copy
import itertools

class Numbered(object):
    __slots__ = [
        '_elem',
        '_doc',
        '_match',
        '_tag',
        '_entry',
        '_link',
        '_title',
        '_description',
        '_category',
        '_basic_category',
        '_first_section_level',
        '_last_section_level',
        '_leading',
        '_number',
        '_global_number',
        '_section_number',
        '_local_number',
    ]

    @property
    def tag(self):
        return self._tag

    @property
    def entry(self):
        return self._entry

    @property
    def link(self):
        return self._link

    @property
    def title(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def global_number(self):
        return self._global_number

    @property
    def section_number(self):
        return self._section_number

    @property
    def local_number(self):
        return self._local_number

    number_regex = '#((?P<prefix>[a-zA-Z][\w.-]*):)?(?P<name>[a-zA-Z][\w:.-]*)?'
    _regex = '(?P<header>(?P<hidden>(-\.)*)(\+\.)*)'
    header_regex = '^' + _regex + '$'
    marker_regex = '^' + _regex + number_regex + '$'
    double_sharp_regex = '^' + _regex + '#' + number_regex + '$'

    @staticmethod
    def _remove_accents(string):
        nfkd_form = unicodedata.normalize('NFKD', string)
        return u''.join([c for c in nfkd_form if not unicodedata.combining(c)])

    @staticmethod
    def _identifier(string):
        # replace invalid characters by dash
        string = re.sub('[^0-9a-zA-Z_-]+', '-', Numbered._remove_accents(string.lower()))

        # Remove leading digits
        string = re.sub('^[^a-zA-Z]+', '', string)

        return string

    def __init__(self, elem, doc):
        self._elem = elem
        self._doc = doc
        self._entry = Span(classes=['pandoc-numbering-entry'])
        self._link = Span(classes=['pandoc-numbering-link'])
        self._tag = None
        if len(self._get_content()) > 0 and isinstance(self._get_content()[-1], Str):
            self._match = re.match(Numbered.marker_regex, self._get_content()[-1].text)
            if self._match:
                self._replace_marker()
            elif re.match(Numbered.double_sharp_regex, self._get_content()[-1].text):
                self._replace_double_sharp()

    def _set_content(self, content):
        if isinstance(self._elem, Para):
            self._elem.content = content
        elif isinstance(self._elem, DefinitionItem):
            self._elem.term = content

    def _get_content(self):
        if isinstance(self._elem, Para):
            return self._elem.content
        elif isinstance(self._elem, DefinitionItem):
            return self._elem.term

    def _replace_double_sharp(self):
        self._get_content()[-1].text = self._get_content()[-1].text.replace('##', '#', 1)

    def _replace_marker(self):
        self._compute_title()
        self._compute_description()
        self._compute_basic_category()
        self._compute_levels()
        self._compute_section_number()
        self._compute_leading()
        self._compute_category()
        self._compute_number()
        self._compute_tag()
        self._compute_local_number()
        self._compute_global_number()
        self._compute_data()

    def _compute_title(self):
        self._title = []
        if isinstance(self._get_content()[-3], Str) and self._get_content()[-3].text[-1:] == ')':
            for (i, item) in enumerate(self._get_content()):
                if isinstance(item, Str) and item.text[0] == '(':
                    self._title = self._get_content()[i:-2]
                    # Detach from original parent
                    self._title.parent = None
                    self._title[0].text = self._title[0].text[1:]
                    self._title[-1].text = self._title[-1].text[:-1]
                    del self._get_content()[i-1:-2]
                    break
        self._title = list(self._title)
        
    def _compute_description(self):
        self._description = self._get_content()[:-2]
        # Detach from original parent
        self._description.parent = None
        self._description = list(self._description)

    def _compute_basic_category(self):
        if self._match.group('prefix') == None:
            self._basic_category = Numbered._identifier(''.join(map(stringify, self._description)))
        else:
            self._basic_category = self._match.group('prefix')
        if self._basic_category not in self._doc.defined:
            define(self._basic_category, self._doc)

    def _compute_levels(self):
        # Compute the first and last section level values
        self._first_section_level = len(self._match.group('hidden')) // 2
        self._last_section_level = len(self._match.group('header')) // 2

        # Get the default first and last section level
        if self._first_section_level == 0 and self._last_section_level == 0:
            self._first_section_level = self._doc.defined[self._basic_category]['first-section-level']
            self._last_section_level = self._doc.defined[self._basic_category]['last-section-level']

    def _compute_section_number(self):
        self._section_number = '.'.join(map(str, self._doc.headers[:self._last_section_level]))

    def _compute_leading(self):
        # Compute the leading (composed of the section numbering and a dot)
        if self._last_section_level != 0:
            self._leading = self._section_number + '.'
        else:
            self._leading =  ''

    def _compute_category(self):
        self._category = self._basic_category + ':' + self._leading

        # Is it a new category?
        if self._category not in self._doc.count:
            self._doc.count[self._category] = 0

        self._doc.count[self._category] = self._doc.count[self._category] + 1

    def _compute_number(self):
        self._number = str(self._doc.count[self._category])

    def _compute_tag(self):
        # Determine the final tag
        if self._match.group('name') == None:
            self._tag = self._category + self._number
        else:
            self._tag = self._basic_category + ':' + self._match.group('name')

        # Compute collections
        if self._basic_category not in self._doc.collections:
            self._doc.collections[self._basic_category] = []

        self._doc.collections[self._basic_category].append(self._tag)

    def _compute_local_number(self):
        # Replace the '-.-.+.+...#' by the category count (omitting the hidden part)
        self._local_number = '.'.join(map(str, self._doc.headers[self._first_section_level:self._last_section_level] + [self._number]))

    def _compute_global_number(self):
        # Compute the global number
        if self._section_number:
            self._global_number = self._section_number + '.' + self._number
        else:
            self._global_number = self._number

    def _compute_data(self):
        classes = self._doc.defined[self._basic_category]['classes']
        self._set_content([Span(
            classes=['pandoc-numbering-text'] + classes,
            identifier=self._tag
        )])
        self._link.classes = self._link.classes + classes
        self._entry.classes = self._entry.classes + classes

        # Prepare the final data
        if self._title: 
            self._get_content()[0].content = copy.deepcopy(self._doc.defined[self._basic_category]['format-text-title'])
            self._link.content = copy.deepcopy(self._doc.defined[self._basic_category]['format-link-title'])
            self._entry.content = copy.deepcopy(self._doc.defined[self._basic_category]['format-entry-title'])
        else:
            self._get_content()[0].content = copy.deepcopy(self._doc.defined[self._basic_category]['format-text-classic'])
            self._link.content = copy.deepcopy(self._doc.defined[self._basic_category]['format-link-classic'])
            self._entry.content = copy.deepcopy(self._doc.defined[self._basic_category]['format-entry-classic'])

        # Compute content
        replace_description(self._elem, self._description)
        replace_title(self._elem, self._title)
        replace_global_number(self._elem, self._global_number)
        replace_section_number(self._elem, self._section_number)
        replace_local_number(self._elem, self._local_number)

        ## Compute link
        replace_description(self._link, self._description)
        replace_title(self._link, self._title)
        replace_global_number(self._link, self._global_number)
        replace_section_number(self._link, self._section_number)
        replace_local_number(self._link, self._local_number)
        if self._doc.format == 'latex':
            replace_page_number(self._link, self._tag)

        # Compute entry
        replace_description(self._entry, self._description)
        replace_title(self._entry, self._title)
        replace_global_number(self._entry, self._global_number)
        replace_section_number(self._entry, self._section_number)
        replace_local_number(self._entry, self._local_number)
        
        # Finalize the content
        if self._doc.format == 'latex':
            self._get_content()[0].content.insert(0, RawInline('\\label{' + self._tag + '}', 'tex'))

            latex_category = re.sub('[^a-z]+', '', self._basic_category)
            latex = '\\phantomsection\\addcontentsline{' + \
                latex_category + \
                '}{' + \
                latex_category + \
                '}{\\protect\\numberline {' + \
                self._leading + \
                self._number + \
                '}{\ignorespaces ' + \
                to_latex(self._entry) + \
                '}}'
            self._get_content().insert(0, RawInline(latex, 'tex'))

def replace_description(where, description):
    where.walk(partial(replacing, search='%D', replace=copy.deepcopy(description)))
    where.walk(partial(replacing, search='%d', replace=list(item.walk(lowering) for item in copy.deepcopy(description))))

def replace_title(where, title):
    where.walk(partial(replacing, search='%T', replace=copy.deepcopy(title)))
    where.walk(partial(replacing, search='%t', replace=list(item.walk(lowering) for item in copy.deepcopy(title))))

def replace_section_number(where, section_number):
    where.walk(partial(replacing, search='%s', replace=[Str(section_number)]))

def replace_global_number(where, global_number):
    where.walk(partial(replacing, search='%g', replace=[Str(global_number)]))

def replace_local_number(where, local_number):
    where.walk(partial(replacing, search='%n', replace=[Str(local_number)]))
    where.walk(partial(replacing, search='#', replace=[Str(local_number)]))

def replace_page_number(where, tag):
    where.walk(partial(replacing, search='%p', replace=[RawInline('\\pageref{' + tag + '}', 'tex')]))

def to_latex(elem):
    return convert_text(Plain(elem), input_format='panflute', output_format='latex', extra_args=['--no-highlight'])

def define(category, doc):
    doc.defined[category] = {
        'first-section-level':  0,
        'last-section-level':   0,
        'format-text-classic':  [Strong(Str('%D'), Space(), Str('%n'))],
        'format-text-title':    [Strong(Str('%D'), Space(), Str('%n')), Space(), Emph(Str('(%T)'))],
        'format-link-classic':  [Str('%D'), Space(), Str('%n')],
        'format-link-title':    [Str('%D'), Space(), Str('%n'), Space(), Str('(%T)')],
        'format-entry-title':   [Str('%T')],
        'classes':              [category],
        'cite-shortcut':        False,
        'listing-title':        None,
        'entry-tab':            1.5,
        'entry-space':          2.3,
    }
    if doc.format == 'latex':
        doc.defined[category]['format-entry-classic'] = [Str('%D')]
        doc.defined[category]['entry-tab'] = 1.5
        doc.defined[category]['entry-space'] = 2.3
    else:
        doc.defined[category]['format-entry-classic'] = [Str('%D'), Space(), Str('%g')]

def lowering(elem, doc):
    if isinstance(elem, Str):
        elem.text = elem.text.lower()

def replacing(elem, doc, search=None, replace=None):
    if isinstance(elem, Str):
        prepare = elem.text.split(search)
        if len(prepare) > 1:

            text = []

            if prepare[0] != '':
                text.append(Str(prepare[0]))

            for string in prepare[1:]:
                text.extend(replace)
                if string != '':
                    text.append(Str(string))

            return text

    return [elem]

def numbering(elem, doc):
    if isinstance(elem, Header):
        update_header_numbers(elem, doc)
    elif isinstance(elem, (Para, DefinitionItem)):
        numbered = Numbered(elem, doc)
        if numbered.tag is not None:
            doc.information[numbered.tag] = numbered

def referencing(elem, doc):
    if isinstance(elem, Link):
        return referencing_link(elem, doc)
    elif isinstance(elem, Cite):
        return referencing_cite(elem, doc)

def referencing_link(elem, doc):
    match = re.match('^#(?P<tag>([a-zA-Z][\w:.-]*))$', elem.url)
    if match:
        tag = match.group('tag')
        if tag in doc.information:
            if bool(elem.content):
                replace_title(elem, doc.information[tag].title)
                replace_description(elem, doc.information[tag].description)
                replace_global_number(elem, doc.information[tag].global_number)
                replace_section_number(elem, doc.information[tag].section_number)
                replace_local_number(elem, doc.information[tag].local_number)
            else:
                elem.content = [doc.information[tag].link]

def referencing_cite(elem, doc):
    if len(elem.content) == 1 and isinstance(elem.content[0], Str):
        match = re.match('^(@(?P<tag>(?P<category>[a-zA-Z][\w.-]*):(([a-zA-Z][\w.-]*)|(\d*(\.\d*)*))))$', elem.content[0].text)
        if match:
            category = match.group('category')
            if category in doc.defined and doc.defined[category]['cite-shortcut']:
                # Deal with @prefix:name shortcut
                tag = match.group('tag')
                if tag in doc.information:
                    return Link(doc.information[tag].link, url = '#' + tag)

def update_header_numbers(elem, doc):
    if 'unnumbered' not in elem.classes:
        doc.headers[elem.level - 1] = doc.headers[elem.level - 1] + 1
        for index in range(elem.level, 6):
            doc.headers[index] = 0

def prepare(doc):
    doc.headers = [0, 0, 0, 0, 0, 0]
    doc.information = {}
    doc.defined = {}

    if 'pandoc-numbering' in doc.metadata.content and isinstance(doc.metadata.content['pandoc-numbering'], MetaMap):
        for category, definition in doc.metadata.content['pandoc-numbering'].content.items():
            if isinstance(definition, MetaMap):
                add_definition(category, definition, doc)

    doc.count = {}
    doc.collections = {}

def add_definition(category, definition, doc):
    # Create the category with options by default
    define(category, doc)

    # Detect general options
    if 'general' in definition:
        meta_cite(category, definition['general'], doc.defined)
        meta_listing_title(category, definition['general'], doc.defined)
        meta_levels(category, definition['general'], doc.defined)
        meta_classes(category, definition['general'], doc.defined)

    # Detect LaTeX options
    if doc.format == 'latex':
        if 'latex' in definition:
            meta_format_text(category, definition['latex'], doc.defined)
            meta_format_link(category, definition['latex'], doc.defined)
            meta_format_entry(category, definition['latex'], doc.defined)
            meta_entry_tab(category, definition['latex'], doc.defined)
            meta_entry_space(category, definition['latex'], doc.defined)            
    # Detect standard options
    else:
        if 'standard' in definition:
            meta_format_text(category, definition['standard'], doc.defined)
            meta_format_link(category, definition['standard'], doc.defined)
            meta_format_entry(category, definition['standard'], doc.defined)

def meta_cite(category, definition, defined):
    if 'cite-shortcut' in definition:
        if isinstance(definition['cite-shortcut'], MetaBool):
            defined[category]['cite-shortcut'] = definition['cite-shortcut'].boolean
        else:
            debug('[WARNING] pandoc-numbering: cite-shortcut is not correct for category ' + category)

def meta_listing_title(category, definition, defined):
    if 'listing-title' in definition:
        if isinstance(definition['listing-title'], MetaInlines):
            defined[category]['listing-title'] = definition['listing-title'].content
            # Detach from original parent
            defined[category]['listing-title'].parent = None
        else:
            debug('[WARNING] pandoc-numbering: listing-title is not correct for category ' + category)

def meta_format_text(category, definition, defined):
    if 'format-text-classic' in definition:
        if isinstance(definition['format-text-classic'], MetaInlines):
            defined[category]['format-text-classic'] = definition['format-text-classic'].content
            # Detach from original parent
            defined[category]['format-text-classic'].parent = None
        else:
            debug('[WARNING] pandoc-numbering: format-text-classic is not correct for category ' + category)

    if 'format-text-title' in definition:
        if isinstance(definition['format-text-title'], MetaInlines):
            defined[category]['format-text-title'] = definition['format-text-title'].content
            # Detach from original parent
            defined[category]['format-text-title'].parent = None
        else:
            debug('[WARNING] pandoc-numbering: format-text-title is not correct for category ' + category)

def meta_format_link(category, definition, defined):
    if 'format-link-classic' in definition:
        if isinstance(definition['format-link-classic'], MetaInlines):
            defined[category]['format-link-classic'] = definition['format-link-classic'].content
            # Detach from original parent
            defined[category]['format-link-classic'].parent = None
        else:
            debug('[WARNING] pandoc-numbering: format-link-classic is not correct for category ' + category)

    if 'format-link-title' in definition:
        if isinstance(definition['format-link-title'], MetaInlines):
            defined[category]['format-link-title'] = definition['format-link-title'].content
            # Detach from original parent
            defined[category]['format-link-title'].parent = None
        else:
            debug('[WARNING] pandoc-numbering: format-link-title is not correct for category ' + category)

def meta_format_entry(category, definition, defined):
    if 'format-entry-classic' in definition:
        if isinstance(definition['format-entry-classic'], MetaInlines):
            defined[category]['format-entry-classic'] = definition['format-entry-classic'].content
            # Detach from original parent
            defined[category]['format-entry-classic'].parent = None
        else:
            debug('[WARNING] pandoc-numbering: format-entry-classic is not correct for category ' + category)

    if 'format-entry-title' in definition:
        if isinstance(definition['format-entry-title'], MetaInlines):
            defined[category]['format-entry-title'] = definition['format-entry-title'].content
            # Detach from original parent
            defined[category]['format-entry-title'].parent = None
        else:
            debug('[WARNING] pandoc-numbering: format-entry-title is not correct for category ' + category)

def meta_entry_tab(category, definition, defined):
    if 'entry-tab' in definition and isinstance(definition['entry-tab'], MetaString):
        # Get the tab
        try:
            tab = float(definition['entry-tab'].text)
            if tab > 0:
                defined[category]['entry-tab'] = tab
            else:
                debug('[WARNING] pandoc-numbering: entry-tab must be positive for category ' + category)
        except ValueError:
            debug('[WARNING] pandoc-numbering: entry-tab is not correct for category ' + category)

def meta_entry_space(category, definition, defined):
    if 'entry-space' in definition and isinstance(definition['entry-space'], MetaString):
        # Get the space
        try:
            space = float(definition['entry-space'].text)
            if space > 0:
                defined[category]['entry-space'] = space
            else:
                debug('[WARNING] pandoc-numbering: entry-space must be positive for category ' + category)
        except ValueError:
            debug('[WARNING] pandoc-numbering: entry-space is not correct for category ' + category)

def meta_levels(category, definition, defined):
    if 'sectioning-levels' in definition and isinstance(definition['sectioning-levels'], MetaInlines) and len(definition['sectioning-levels'].content) == 1:
        match = re.match(Numbered.header_regex, definition['sectioning-levels'].content[0].text)
        if match:
            # Compute the first and last levels section
            defined[category]['first-section-level'] =  len(match.group('hidden')) // 2
            defined[category]['last-section-level'] = len(match.group('header')) // 2
    if 'first-section-level' in definition and isinstance(definition['first-section-level'], MetaString):
        # Get the level
        try:
            level = int(definition['first-section-level'].text) - 1
            if level >= 0 and level <= 6 :
                defined[category]['first-section-level'] = level
            else:
                debug('[WARNING] pandoc-numbering: first-section-level must be positive or zero for category ' + category)
        except ValueError:
            debug('[WARNING] pandoc-numbering: first-section-level is not correct for category ' + category)
    if 'last-section-level' in definition and isinstance(definition['last-section-level'], MetaString):
        # Get the level
        try:
            level = int(definition['last-section-level'].text)
            if level >= 0 and level <= 6 :
                defined[category]['last-section-level'] = level
            else:
                debug('[WARNING] pandoc-numbering: last-section-level must be positive or zero for category ' + category)
        except ValueError:
            debug('[WARNING] pandoc-numbering: last-section-level is not correct for category ' + category)

def meta_classes(category, definition, defined):
    if 'classes' in definition and isinstance(definition['classes'], MetaList):
        classes = []
        for elt in definition['classes'].content:
            classes.append(stringify(elt))
        defined[category]['classes'] = classes

def finalize(doc):
    listings = []
    # Loop on all listings definition
    i = 0
    for category, definition in doc.defined.items():
        if definition['listing-title'] is not None:
            classes = ['pandoc-numbering-listing', 'unnumbered', 'unlisted'] + definition['classes']
            doc.content.insert(i, Header(*definition['listing-title'], level=1, classes=classes))
            i = i + 1

            if doc.format == 'latex':
                table = table_latex(doc, category, definition)
            else:
                table = table_other(doc, category, definition)

            if table:
                doc.content.insert(i, table)
                i = i + 1

def table_other(doc, category, definition):
    if category in doc.collections:
        # Prepare the list
        elements = []
        # Loop on the collection
        for tag in doc.collections[category]:
            # Add an item to the list
            elements.append(ListItem(Plain(Link(doc.information[tag].entry, url='#' + tag))))
        # Return a bullet list
        return BulletList(*elements)
    else:
        return None

def table_latex(doc, category, definition):
    latex_category = re.sub('[^a-z]+', '', category)
    latex = [
        link_color(doc),
        '\\makeatletter',
        '\\newcommand*\\l@' + latex_category + '{\\@dottedtocline{1}{' + str(definition['entry-tab']) + 'em}{'+ str(definition['entry-space']) +'em}}',
        '\\@starttoc{' + latex_category + '}',
        '\\makeatother'
    ]
    # Return a RawBlock
    return RawBlock(''.join(latex), 'tex')

def link_color(doc):
    # Get the link color
    metadata = doc.get_metadata()
    if 'toccolor' in metadata:
        return '\\hypersetup{linkcolor=' + str(metadata['toccolor']) + '}'
    else:
        return '\\hypersetup{linkcolor=black}'

def main(doc = None):
    run_filters([numbering, referencing], prepare = prepare, doc = doc, finalize = finalize)

if __name__ == '__main__':
    main()
