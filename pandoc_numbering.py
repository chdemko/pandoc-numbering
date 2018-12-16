#!/usr/bin/env python

# pylint: disable=too-many-lines

"""
Pandoc filter to number all kinds of things.
"""

from functools import partial
import re
import unicodedata
import copy

from panflute import \
    BlockQuote,\
    BulletList,\
    Citation,\
    Cite,\
    CodeBlock,\
    Definition,\
    DefinitionItem,\
    DefinitionList,\
    Div,\
    Emph,\
    Header,\
    HorizontalRule,\
    Image,\
    LineBlock,\
    LineBreak,\
    LineItem,\
    Link,\
    ListItem,\
    Note,\
    Para,\
    Plain,\
    RawBlock,\
    RawInline,\
    SoftBreak,\
    Space,\
    Span,\
    Str,\
    Strong,\
    Table,\
    TableCell,\
    TableRow,\
    MetaBool,\
    MetaInlines,\
    MetaList,\
    MetaMap,\
    MetaString,\
    run_filters,\
    stringify,\
    convert_text,\
    debug


# pylint: disable=bad-option-value,useless-object-inheritance
class Numbered(object):
    """
    Numbered elements
    """
    # pylint: disable=too-many-instance-attributes
    __slots__ = [
        '_elem',
        '_doc',
        '_match',
        '_tag',
        '_entry',
        '_link',
        '_caption',
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
        """
        Get tag property.
        """
        return self._tag

    @property
    def entry(self):
        """
        Get entry property.
        """
        return self._entry

    @property
    def link(self):
        """
        Get link property.
        """
        return self._link

    @property
    def title(self):
        """
        Get title property.
        """
        return self._title

    @property
    def description(self):
        """
        Get description property.
        """
        return self._description

    @property
    def global_number(self):
        """
        Get global_number property.
        """
        return self._global_number

    @property
    def section_number(self):
        """
        Get section_number property.
        """
        return self._section_number

    @property
    def local_number(self):
        """
        Get local_number property.
        """
        return self._local_number

    @property
    def category(self):
        """
        Get category property.
        """
        return self._category

    @property
    def caption(self):
        """
        Get caption property.
        """
        return self._caption

    number_regex = '#((?P<prefix>[a-zA-Z][\\w.-]*):)?(?P<name>[a-zA-Z][\\w:.-]*)?'
    _regex = '(?P<header>(?P<hidden>(-\\.)*)(\\+\\.)*)'
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
        self._tag = None
        self._entry = Span(classes=['pandoc-numbering-entry'])
        self._link = Span(classes=['pandoc-numbering-link'])
        self._caption = None
        self._title = None
        self._description = None
        self._category = None
        self._basic_category = None
        self._first_section_level = None
        self._last_section_level = None
        self._leading = None
        self._number = None
        self._global_number = None
        self._section_number = None
        self._local_number = None

        if self._get_content() and isinstance(self._get_content()[-1], Str):
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
        if isinstance(self._elem, DefinitionItem):
            return self._elem.term
        return None

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
                    del self._get_content()[i - 1:-2]
                    break
        self._title = list(self._title)

    def _compute_description(self):
        self._description = self._get_content()[:-2]
        # Detach from original parent
        self._description.parent = None
        self._description = list(self._description)

    def _compute_basic_category(self):
        if self._match.group('prefix') is None:
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
            self._first_section_level = \
                self._doc.defined[self._basic_category]['first-section-level']
            self._last_section_level = \
                self._doc.defined[self._basic_category]['last-section-level']

    def _compute_section_number(self):
        self._section_number = '.'.join(map(str, self._doc.headers[:self._last_section_level]))

    def _compute_leading(self):
        # Compute the leading (composed of the section numbering and a dot)
        if self._last_section_level != 0:
            self._leading = self._section_number + '.'
        else:
            self._leading = ''

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
        if self._match.group('name') is None:
            self._tag = self._category + self._number
        else:
            self._tag = self._basic_category + ':' + self._match.group('name')

        # Compute collections
        if self._basic_category not in self._doc.collections:
            self._doc.collections[self._basic_category] = []

        self._doc.collections[self._basic_category].append(self._tag)

    def _compute_local_number(self):
        # Replace the '-.-.+.+...#' by the category count (omitting the hidden part)
        self._local_number = '.'.join(map(
            str,
            self._doc.headers[self._first_section_level:self._last_section_level] + [self._number]
        ))

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
            self._get_content()[0].content = copy.deepcopy(
                self._doc.defined[self._basic_category]['format-text-title']
            )
            self._link.content = copy.deepcopy(
                self._doc.defined[self._basic_category]['format-link-title']
            )
            self._entry.content = copy.deepcopy(
                self._doc.defined[self._basic_category]['format-entry-title']
            )
            self._caption = \
                self._doc.defined[self._basic_category]['format-caption-title']
        else:
            self._get_content()[0].content = copy.deepcopy(
                self._doc.defined[self._basic_category]['format-text-classic']
            )
            self._link.content = copy.deepcopy(
                self._doc.defined[self._basic_category]['format-link-classic']
            )
            self._entry.content = copy.deepcopy(
                self._doc.defined[self._basic_category]['format-entry-classic']
            )
            self._caption = \
                self._doc.defined[self._basic_category]['format-caption-classic']

        # Compute caption (delay replacing %c at the end since it is not known for the moment)
        title = stringify(Span(*self._title))
        description = stringify(Span(*self._description))
        self._caption = self._caption.replace('%t', title.lower())
        self._caption = self._caption.replace('%T', title)
        self._caption = self._caption.replace('%d', description.lower())
        self._caption = self._caption.replace('%D', description)
        self._caption = self._caption.replace('%s', self._section_number)
        self._caption = self._caption.replace('%g', self._global_number)
        self._caption = self._caption.replace('%n', self._local_number)
        self._caption = self._caption.replace('#', self._local_number)
        if self._doc.format == 'latex':
            self._caption = self._caption.replace('%p', '\\pageref{' + self._tag + '}')

        # Compute content
        replace_description(self._elem, self._description)
        replace_title(self._elem, self._title)
        replace_global_number(self._elem, self._global_number)
        replace_section_number(self._elem, self._section_number)
        replace_local_number(self._elem, self._local_number)

        # Compute link
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
                '}{\\ignorespaces ' + \
                to_latex(self._entry) + \
                '}}'
            self._get_content().insert(0, RawInline(latex, 'tex'))


def replace_description(where, description):
    """
    Replace description in where.

    Arguments
    ---------
        where: where to replace
        description: replace %D and %d by description
    """
    where.walk(
        partial(
            replacing,
            search='%D',
            replace=copy.deepcopy(description)
        )
    )
    where.walk(
        partial(
            replacing,
            search='%d',
            replace=list(item.walk(lowering) for item in copy.deepcopy(description))
        )
    )


def replace_title(where, title):
    """
    Replace title in where.

    Arguments
    ---------
        where: where to replace
        title: replace %T and %t by title
    """
    where.walk(
        partial(
            replacing,
            search='%T',
            replace=copy.deepcopy(title)
        )
    )
    where.walk(
        partial(
            replacing,
            search='%t',
            replace=list(item.walk(lowering) for item in copy.deepcopy(title))
        )
    )


def replace_section_number(where, section_number):
    """
    Replace section number in where.

    Arguments
    ---------
        where: where to replace
        section_number: replace %s by section_number
    """
    where.walk(
        partial(
            replacing,
            search='%s',
            replace=[Str(section_number)]
        )
    )


def replace_global_number(where, global_number):
    """
    Replace global number in where.

    Arguments
    ---------
        where: where to replace
        global_number: replace %g by global_number
    """
    where.walk(
        partial(
            replacing,
            search='%g',
            replace=[Str(global_number)]
        )
    )


def replace_local_number(where, local_number):
    """
    Replace local number in where.

    Arguments
    ---------
        where: where to replace
        local_number: replace %n and # by local_number
    """
    where.walk(
        partial(
            replacing,
            search='%n',
            replace=[Str(local_number)]
        )
    )
    where.walk(
        partial(
            replacing,
            search='#',
            replace=[Str(local_number)]
        )
    )


def replace_page_number(where, tag):
    """
    Replace page number in where.

    Arguments
    ---------
        where: where to replace
        tag: replace %p by tag
    """
    where.walk(
        partial(
            replacing,
            search='%p',
            replace=[RawInline('\\pageref{' + tag + '}', 'tex')]
        )
    )


def replace_count(where, count):
    """
    Replace count in where.

    Arguments
    ---------
        where: where to replace
        count: replace %c by count
    """
    where.walk(
        partial(
            replacing,
            search='%c',
            replace=[Str(count)]
        )
    )


def remove_useless_latex(elem, _):
    """
    Clean up LaTeX element for entries.

    Arguments
    ---------
        elem: elem to scan

    Returns
    -------
        []: if elem is an instance to remove
        None: otherwise
    """
    if isinstance(
            elem,
            (
                BlockQuote,
                BulletList,
                Citation,
                Cite,
                CodeBlock,
                Definition,
                DefinitionItem,
                DefinitionList,
                Div,
                Header,
                HorizontalRule,
                Image,
                LineBlock,
                LineBreak,
                LineItem,
                ListItem,
                Note,
                Para,
                RawBlock,
                RawInline,
                SoftBreak,
                Table,
                TableCell,
                TableRow
            )
        ):

        return []
    return None


def to_latex(elem):
    """
    Convert element to LaTeX.

    Arguments
    ---------
        elem: elem to convert

    Returns
    -------
        LaTex string
    """
    return convert_text(
        run_filters(
            [remove_useless_latex],
            doc=Plain(elem)
        ),
        input_format='panflute',
        output_format='latex',
        extra_args=['--no-highlight']
    )


def define(category, doc):
    """
    Define a category in document.

    Arguments
    ---------
        category: category to define
        doc: pandoc document
    """
    # pylint: disable=line-too-long
    doc.defined[category] = {
        'first-section-level':    0,
        'last-section-level':     0,
        'format-text-classic':    [Strong(Str('%D'), Space(), Str('%n'))],
        'format-text-title':      [Strong(Str('%D'), Space(), Str('%n')), Space(), Emph(Str('(%T)'))],
        'format-link-classic':    [Str('%D'), Space(), Str('%n')],
        'format-link-title':      [Str('%D'), Space(), Str('%n'), Space(), Str('(%T)')],
        'format-caption-classic': '%D %n',
        'format-caption-title':   '%D %n (%T)',
        'format-entry-title':     [Str('%T')],
        'classes':                [category],
        'cite-shortcut':          True,
        'listing-title':          None,
        'listing-unnumbered':     True,
        'listing-unlisted':       True,
        'listing-identifier':     True,
        'entry-tab':              1.5,
        'entry-space':            2.3,
    }
    if doc.format == 'latex':
        doc.defined[category]['format-entry-classic'] = [Str('%D')]
        doc.defined[category]['entry-tab'] = 1.5
        doc.defined[category]['entry-space'] = 2.3
    else:
        doc.defined[category]['format-entry-classic'] = [Str('%D'), Space(), Str('%g')]


def lowering(elem, _):
    """
    Lower element.

    Arguments
    ---------
        elem: element to lower
    """
    if isinstance(elem, Str):
        elem.text = elem.text.lower()


def replacing(elem, _, search=None, replace=None):
    """
    Function to replace.

    Arguments
    ---------
        elem: element to scan

    Keyword arguments
    -----------------
        search: string to search
        replace: string to replace
    """
    if isinstance(elem, Str):
        search_splitted = elem.text.split(search)
        if len(search_splitted) > 1:

            text = []

            if search_splitted[0] != '':
                text.append(Str(search_splitted[0]))

            for string in search_splitted[1:]:
                text.extend(replace)
                if string != '':
                    text.append(Str(string))

            return text

    return [elem]


def numbering(elem, doc):
    """
    number element.

    Arguments
    ---------
        elem: element to number
        doc: pandoc document
    """
    if isinstance(elem, Header):
        update_header_numbers(elem, doc)
    elif isinstance(elem, (Para, DefinitionItem)):
        numbered = Numbered(elem, doc)
        if numbered.tag is not None:
            doc.information[numbered.tag] = numbered


def referencing(elem, doc):
    """
    reference element.

    Arguments
    ---------
        elem: element to reference
        doc: pandoc document
    """
    if isinstance(elem, Link):
        return referencing_link(elem, doc)
    if isinstance(elem, Cite):
        return referencing_cite(elem, doc)
    if isinstance(elem, Span) and elem.identifier in doc.information:
        replace_count(elem, str(doc.count[doc.information[elem.identifier].category]))
    return None


def referencing_link(elem, doc):
    """
    reference link.

    Arguments
    ---------
        elem: element to reference
        doc: pandoc document
    """
    match = re.match('^#(?P<tag>([a-zA-Z][\\w:.-]*))$', elem.url)
    if match:
        tag = match.group('tag')
        if tag in doc.information:
            replace_title(elem, doc.information[tag].title)
            replace_description(elem, doc.information[tag].description)
            replace_global_number(elem, doc.information[tag].global_number)
            replace_section_number(elem, doc.information[tag].section_number)
            replace_local_number(elem, doc.information[tag].local_number)
            replace_count(elem, str(doc.count[doc.information[tag].category]))
            if doc.format == 'latex':
                replace_page_number(elem, tag)

            title = stringify(Span(*doc.information[tag].title))
            description = stringify(Span(*doc.information[tag].description))
            elem.title = elem.title.replace('%t', title.lower())
            elem.title = elem.title.replace('%T', title)
            elem.title = elem.title.replace('%d', description.lower())
            elem.title = elem.title.replace('%D', description)
            elem.title = elem.title.replace('%s', doc.information[tag].section_number)
            elem.title = elem.title.replace('%g', doc.information[tag].global_number)
            elem.title = elem.title.replace('%n', doc.information[tag].local_number)
            elem.title = elem.title.replace('#', doc.information[tag].local_number)
            elem.title = elem.title.replace('%c', str(doc.count[doc.information[tag].category]))
            if doc.format == 'latex':
                elem.title = elem.title.replace('%p', '\\pageref{' + tag + '}')


def referencing_cite(elem, doc):
    """
    reference cite.

    Arguments
    ---------
        elem: element to reference
        doc: pandoc document
    """
    if len(elem.content) == 1 and isinstance(elem.content[0], Str):
        match = re.match(
            '^(@(?P<tag>(?P<category>[a-zA-Z][\\w.-]*):(([a-zA-Z][\\w.-]*)|(\\d*(\\.\\d*)*))))$',
            elem.content[0].text
        )
        if match:
            category = match.group('category')
            if category in doc.defined and doc.defined[category]['cite-shortcut']:
                # Deal with @prefix:name shortcut
                tag = match.group('tag')
                if tag in doc.information:
                    ret = Link(
                        doc.information[tag].link,
                        url='#' + tag,
                        title=doc.information[tag].caption.replace(
                            '%c',
                            str(doc.count[doc.information[tag].category])
                        )
                    )
                    replace_count(ret, str(doc.count[doc.information[tag].category]))
                    return ret
    return None


def update_header_numbers(elem, doc):
    """
    update header numbers.

    Arguments
    ---------
        elem: element to update
        doc: pandoc document
    """
    if 'unnumbered' not in elem.classes:
        doc.headers[elem.level - 1] = doc.headers[elem.level - 1] + 1
        for index in range(elem.level, 6):
            doc.headers[index] = 0


def prepare(doc):
    """
    Prepare document.

    Arguments
    ---------
        doc: pandoc document
    """
    doc.headers = [0, 0, 0, 0, 0, 0]
    doc.information = {}
    doc.defined = {}

    if 'pandoc-numbering' in doc.metadata.content\
            and isinstance(doc.metadata.content['pandoc-numbering'], MetaMap):
        for category, definition in doc.metadata.content['pandoc-numbering'].content.items():
            if isinstance(definition, MetaMap):
                add_definition(category, definition, doc)

    doc.count = {}
    doc.collections = {}


def add_definition(category, definition, doc):
    """
    Add definition for a category.

    Arguments
    ---------
        category:
        definition:
        defined:
    """
    # Create the category with options by default
    define(category, doc)

    # Detect general options
    if 'general' in definition:
        meta_cite(category, definition['general'], doc.defined)
        meta_listing(category, definition['general'], doc.defined)
        meta_levels(category, definition['general'], doc.defined)
        meta_classes(category, definition['general'], doc.defined)

    # Detect LaTeX options
    if doc.format == 'latex':
        if 'latex' in definition:
            meta_format_text(category, definition['latex'], doc.defined)
            meta_format_link(category, definition['latex'], doc.defined)
            meta_format_caption(category, definition['latex'], doc.defined)
            meta_format_entry(category, definition['latex'], doc.defined)
            meta_entry_tab(category, definition['latex'], doc.defined)
            meta_entry_space(category, definition['latex'], doc.defined)
    # Detect standard options
    else:
        if 'standard' in definition:
            meta_format_text(category, definition['standard'], doc.defined)
            meta_format_link(category, definition['standard'], doc.defined)
            meta_format_caption(category, definition['standard'], doc.defined)
            meta_format_entry(category, definition['standard'], doc.defined)


def meta_cite(category, definition, defined):
    """
    Compute cite for a category.

    Arguments
    ---------
        category:
        definition:
        defined:
    """
    if 'cite-shortcut' in definition:
        if isinstance(definition['cite-shortcut'], MetaBool):
            defined[category]['cite-shortcut'] = definition['cite-shortcut'].boolean
        else:
            debug(
                '[WARNING] pandoc-numbering: cite-shortcut is not correct for category '
                + category
            )


# pylint:disable=too-many-branches
def meta_listing(category, definition, defined):
    """
    Compute listing for a category.

    Arguments
    ---------
        category:
        definition:
        defined:
    """
    if 'listing-title' in definition:
        if isinstance(definition['listing-title'], MetaInlines):
            defined[category]['listing-title'] = definition['listing-title'].content
            # Detach from original parent
            defined[category]['listing-title'].parent = None
        else:
            debug(
                '[WARNING] pandoc-numbering: listing-title is not correct for category '
                + category
            )
    if 'listing-unnumbered' in definition:
        if isinstance(definition['listing-unnumbered'], MetaBool):
            defined[category]['listing-unnumbered'] = definition['listing-unnumbered'].boolean
        else:
            debug(
                '[WARNING] pandoc-numbering: listing-unnumbered is not correct for category '
                + category
            )
    if 'listing-unlisted' in definition:
        if isinstance(definition['listing-unlisted'], MetaBool):
            defined[category]['listing-unlisted'] = definition['listing-unlisted'].boolean
        else:
            debug(
                '[WARNING] pandoc-numbering: listing-unlisted is not correct for category '
                + category
            )
    if 'listing-identifier' in definition:
        if isinstance(definition['listing-identifier'], MetaBool):
            defined[category]['listing-identifier'] = definition['listing-identifier'].boolean
        elif isinstance(definition['listing-identifier'], MetaInlines)\
            and len(definition['listing-identifier'].content) == 1\
            and isinstance(definition['listing-identifier'].content[0], Str):
            defined[category]['listing-identifier'] = \
                definition['listing-identifier'].content[0].text
        else:
            debug(
                '[WARNING] pandoc-numbering: listing-identifier is not correct for category '
                + category
            )


def meta_format_text(category, definition, defined):
    """
    Compute format text for a category.

    Arguments
    ---------
        category:
        definition:
        defined:
    """
    if 'format-text-classic' in definition:
        if isinstance(definition['format-text-classic'], MetaInlines):
            defined[category]['format-text-classic'] = definition['format-text-classic'].content
            # Detach from original parent
            defined[category]['format-text-classic'].parent = None
        else:
            debug(
                '[WARNING] pandoc-numbering: format-text-classic is not correct for category '
                + category
            )

    if 'format-text-title' in definition:
        if isinstance(definition['format-text-title'], MetaInlines):
            defined[category]['format-text-title'] = definition['format-text-title'].content
            # Detach from original parent
            defined[category]['format-text-title'].parent = None
        else:
            debug(
                '[WARNING] pandoc-numbering: format-text-title is not correct for category '
                + category
            )


def meta_format_link(category, definition, defined):
    """
    Compute format link for a category.

    Arguments
    ---------
        category:
        definition:
        defined:
    """
    if 'format-link-classic' in definition:
        if isinstance(definition['format-link-classic'], MetaInlines):
            defined[category]['format-link-classic'] = definition['format-link-classic'].content
            # Detach from original parent
            defined[category]['format-link-classic'].parent = None
        else:
            debug(
                '[WARNING] pandoc-numbering: format-link-classic is not correct for category '
                + category
            )

    if 'format-link-title' in definition:
        if isinstance(definition['format-link-title'], MetaInlines):
            defined[category]['format-link-title'] = definition['format-link-title'].content
            # Detach from original parent
            defined[category]['format-link-title'].parent = None
        else:
            debug(
                '[WARNING] pandoc-numbering: format-link-title is not correct for category '
                + category
            )


def meta_format_caption(category, definition, defined):
    """
    Compute format caption for a category.

    Arguments
    ---------
        category:
        definition:
        defined:
    """
    if 'format-caption-classic' in definition:
        if isinstance(definition['format-caption-classic'], MetaInlines):
            defined[category]['format-caption-classic'] = \
                stringify(definition['format-caption-classic'])
        else:
            debug(
                '[WARNING] pandoc-numbering: format-caption-classic is not correct for category '
                + category
            )

    if 'format-caption-title' in definition:
        if isinstance(definition['format-caption-title'], MetaInlines):
            defined[category]['format-caption-title'] = \
                stringify(definition['format-caption-title'])
        else:
            debug(
                '[WARNING] pandoc-numbering: format-caption-title is not correct for category '
                + category
            )


def meta_format_entry(category, definition, defined):
    """
    Compute format entry for a category.

    Arguments
    ---------
        category:
        definition:
        defined:
    """
    if 'format-entry-classic' in definition:
        if isinstance(definition['format-entry-classic'], MetaInlines):
            defined[category]['format-entry-classic'] = definition['format-entry-classic'].content
            # Detach from original parent
            defined[category]['format-entry-classic'].parent = None
        else:
            debug(
                '[WARNING] pandoc-numbering: format-entry-classic is not correct for category '
                + category
            )

    if 'format-entry-title' in definition:
        if isinstance(definition['format-entry-title'], MetaInlines):
            defined[category]['format-entry-title'] = definition['format-entry-title'].content
            # Detach from original parent
            defined[category]['format-entry-title'].parent = None
        else:
            debug(
                '[WARNING] pandoc-numbering: format-entry-title is not correct for category '
                + category
            )


def meta_entry_tab(category, definition, defined):
    """
    Compute entry tab for a category.

    Arguments
    ---------
        category:
        definition:
        defined:
    """
    if 'entry-tab' in definition:
        if isinstance(definition['entry-tab'], MetaString):
            value = definition['entry-tab'].text
        elif isinstance(definition['entry-tab'], MetaInlines)\
            and len(definition['entry-tab'].content) == 1:
            value = definition['entry-tab'].content[0].text
        else:
            debug('[WARNING] pandoc-numbering: entry-tab is not correct for category ' + category)
            return
        # Get the tab
        try:
            tab = float(value)
            if tab > 0:
                defined[category]['entry-tab'] = tab
            else:
                debug(
                    '[WARNING] pandoc-numbering: entry-tab must be positive for category '
                    + category
                )
        except ValueError:
            debug('[WARNING] pandoc-numbering: entry-tab is not correct for category ' + category)


def meta_entry_space(category, definition, defined):
    """
    Compute entry space for a category.

    Arguments
    ---------
        category:
        definition:
        defined:
    """
    if 'entry-space' in definition:
        if isinstance(definition['entry-space'], MetaString):
            value = definition['entry-space'].text
        elif isinstance(definition['entry-space'], MetaInlines)\
            and len(definition['entry-space'].content) == 1:
            value = definition['entry-space'].content[0].text
        else:
            debug(
                '[WARNING] pandoc-numbering: entry-space is not correct for category '
                + category
            )
            return
        # Get the space
        try:
            space = float(value)
            if space > 0:
                defined[category]['entry-space'] = space
            else:
                debug(
                    '[WARNING] pandoc-numbering: entry-space must be positive for category '
                    + category
                )
        except ValueError:
            debug('[WARNING] pandoc-numbering: entry-space is not correct for category ' + category)


def meta_levels(category, definition, defined):
    """
    Compute level for a category.

    Arguments
    ---------
        category:
        definition:
        defined:
    """
    if 'sectioning-levels' in definition \
        and isinstance(definition['sectioning-levels'], MetaInlines) \
        and len(definition['sectioning-levels'].content) == 1:
        match = re.match(Numbered.header_regex, definition['sectioning-levels'].content[0].text)
        if match:
            # Compute the first and last levels section
            defined[category]['first-section-level'] = len(match.group('hidden')) // 2
            defined[category]['last-section-level'] = len(match.group('header')) // 2
    if 'first-section-level' in definition:
        if isinstance(definition['first-section-level'], MetaString):
            value = definition['first-section-level'].text
        elif isinstance(definition['first-section-level'], MetaInlines) \
            and len(definition['first-section-level'].content) == 1:
            value = definition['first-section-level'].content[0].text
        else:
            debug(
                '[WARNING] pandoc-numbering: first-section-level is not correct for category '
                + category
            )
            return

        # Get the level
        try:
            level = int(value) - 1
        except ValueError:
            debug(
                '[WARNING] pandoc-numbering: first-section-level is not correct for category '
                + category
            )

        if 0 <= level <= 6:
            defined[category]['first-section-level'] = level
        else:
            # pylint: disable=line-too-long
            debug(
                '[WARNING] pandoc-numbering: first-section-level must be positive or zero for category '
                + category
            )

    if 'last-section-level' in definition:
        if isinstance(definition['last-section-level'], MetaString):
            value = definition['last-section-level'].text
        elif isinstance(definition['last-section-level'], MetaInlines) \
            and len(definition['last-section-level'].content) == 1:
            value = definition['last-section-level'].content[0].text
        else:
            debug(
                '[WARNING] pandoc-numbering: last-section-level is not correct for category '
                + category
            )
            return

        # Get the level
        try:
            level = int(value)
        except ValueError:
            debug(
                '[WARNING] pandoc-numbering: last-section-level is not correct for category '
                + category
            )

        if 0 <= level <= 6:
            defined[category]['last-section-level'] = level
        else:
            # pylint: disable=line-too-long
            debug(
                '[WARNING] pandoc-numbering: last-section-level must be positive or zero for category '
                + category
            )


def meta_classes(category, definition, defined):
    """
    Compute classes for a category.

    Arguments
    ---------
        category:
        definition:
        defined:
    """
    if 'classes' in definition and isinstance(definition['classes'], MetaList):
        classes = []
        for elt in definition['classes'].content:
            classes.append(stringify(elt))
        defined[category]['classes'] = classes


def finalize(doc):
    """
    Finalize document.

    Arguments
    ---------
        doc: pandoc document
    """
    # Loop on all listings definition
    i = 0
    for category, definition in doc.defined.items():
        if definition['listing-title'] is not None:
            classes = ['pandoc-numbering-listing'] + definition['classes']

            if definition['listing-unnumbered']:
                classes.append('unnumbered')

            if definition['listing-unlisted']:
                classes.append('unlisted')

            if definition['listing-identifier'] is False:
                header = Header(*definition['listing-title'], level=1, classes=classes)
            elif definition['listing-identifier'] is True:
                header = Header(*definition['listing-title'], level=1, classes=classes)
                header = convert_text(
                    convert_text(header, input_format='panflute', output_format='markdown'),
                    output_format='panflute'
                )[0]
            else:
                header = Header(
                    *definition['listing-title'],
                    level=1,
                    classes=classes,
                    identifier=definition['listing-identifier']
                )

            doc.content.insert(i, header)
            i = i + 1

            if doc.format == 'latex':
                table = table_latex(doc, category, definition)
            else:
                table = table_other(doc, category, definition)

            if table:
                doc.content.insert(i, table)
                i = i + 1


def table_other(doc, category, _):
    """
    Compute other code for table.

    Arguments
    ---------
        doc: pandoc document
        category: category numbered
        definition: definition
    """
    if category in doc.collections:
        # Prepare the list
        elements = []
        # Loop on the collection
        for tag in doc.collections[category]:
            # Add an item to the list
            elements.append(ListItem(Plain(Link(doc.information[tag].entry, url='#' + tag))))
        # Return a bullet list
        return BulletList(*elements)
    return None


def table_latex(doc, category, definition):
    """
    Compute LaTeX code for table.

    Arguments
    ---------
        doc: pandoc document
        category: category numbered
        definition: definition
    """
    latex_category = re.sub('[^a-z]+', '', category)
    latex = [
        link_color(doc),
        '\\makeatletter',
        '\\newcommand*\\l@' \
            + latex_category \
            + '{\\@dottedtocline{1}{' \
            + str(definition['entry-tab']) \
            + 'em}{' \
            + str(definition['entry-space']) \
            + 'em}}',
        '\\@starttoc{' + latex_category + '}',
        '\\makeatother'
    ]
    # Return a RawBlock
    return RawBlock(''.join(latex), 'tex')


def link_color(doc):
    """
    Compute LaTeX code for toc.

    Arguments
    ---------
        doc: pandoc document
    """
    # Get the link color
    metadata = doc.get_metadata()
    if 'toccolor' in metadata:
        return '\\hypersetup{linkcolor=' + str(metadata['toccolor']) + '}'
    return '\\hypersetup{linkcolor=black}'


def main(doc=None):
    """
    main function.

    Arguments
    ---------
        doc: pandoc document
    """
    return run_filters([numbering, referencing], prepare=prepare, doc=doc, finalize=finalize)


if __name__ == '__main__':
    main()
