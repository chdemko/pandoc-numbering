#!/usr/bin/env python

# pylint: disable=too-many-lines

"""Pandoc filter to number all kinds of things."""

import copy
import re
import unicodedata
from functools import partial
from textwrap import dedent
from typing import Any

from panflute import (
    BlockQuote,
    BulletList,
    Citation,
    Cite,
    CodeBlock,
    Definition,
    DefinitionItem,
    DefinitionList,
    Div,
    Doc,
    Element,
    Emph,
    Header,
    HorizontalRule,
    Image,
    LineBlock,
    LineBreak,
    LineItem,
    Link,
    ListItem,
    MetaBool,
    MetaInlines,
    MetaList,
    MetaMap,
    MetaString,
    Note,
    Para,
    Plain,
    RawBlock,
    RawInline,
    SoftBreak,
    Space,
    Span,
    Str,
    Strong,
    Table,
    TableCell,
    TableRow,
    convert_text,
    debug,
    run_filters,
    stringify,
)


# pylint: disable=bad-option-value,useless-object-inheritance
class Numbered:
    """
    Numbered elements.

    Arguments
    ---------
    elem
        An element.
    doc
        The document.
    """

    # pylint: disable=too-many-instance-attributes
    __slots__ = [
        "_elem",
        "_doc",
        "_match",
        "_tag",
        "_entry",
        "_link",
        "_caption",
        "_title",
        "_description",
        "_category",
        "_basic_category",
        "_classes",
        "_first_section_level",
        "_last_section_level",
        "_leading",
        "_number",
        "_global_number",
        "_section_number",
        "_local_number",
        "_section_alias",
        "_alias",
    ]

    @property
    def tag(self):
        """
        Get the tag property.

        Returns
        -------
            The tag property.
        """
        return self._tag

    @property
    def entry(self):
        """
        Get the entry property.

        Returns
        -------
            The entry property.
        """
        return self._entry

    @property
    def link(self):
        """
        Get the link property.

        Returns
        -------
            The link property.
        """
        return self._link

    @property
    def title(self):
        """
        Get the title property.

        Returns
        -------
            The title property.
        """
        return self._title

    @property
    def description(self):
        """
        Get the description property.

        Returns
        -------
            The description property.
        """
        return self._description

    @property
    def global_number(self):
        """
        Get the global_number property.

        Returns
        -------
            The global_number property.
        """
        return self._global_number

    @property
    def section_number(self):
        """
        Get the section_number property.

        Returns
        -------
            The section_number property.
        """
        return self._section_number

    @property
    def section_alias(self):
        """
        Get the section_alias property.

        Returns
        -------
            The section_alias property.
        """
        return self._section_alias

    @property
    def alias(self):
        """
        Get the alias property.

        Returns
        -------
            The alias property.
        """
        return self._alias

    @property
    def local_number(self):
        """
        Get the local_number property.

        Returns
        -------
            The local_number property.
        """
        return self._local_number

    @property
    def category(self):
        """
        Get the category property.

        Returns
        -------
            The category property.
        """
        return self._category

    @property
    def caption(self):
        """
        Get the caption property.

        Returns
        -------
            The caption property.
        """
        return self._caption

    number_regex = "#((?P<prefix>[a-zA-Z][\\w.-]*):)?(?P<name>[a-zA-Z][\\w:.-]*)?"
    _regex = "(?P<header>(?P<hidden>(-\\.)*)(\\+\\.)*)"
    header_regex = "^" + _regex + "$"
    marker_regex = "^" + _regex + number_regex + "$"
    double_sharp_regex = "^" + _regex + "#" + number_regex + "$"

    @staticmethod
    def _remove_accents(string):
        nfkd_form = unicodedata.normalize("NFKD", string)
        # pylint: disable=redundant-u-string-prefix
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    @staticmethod
    def identifier(string: str) -> str:
        """
        Convert a string to a valid identifier.

        Parameters
        ----------
        string
            A string to convert.

        Returns
        -------
        str
            The corresponding identifier
        """
        # replace invalid characters by dash
        string = re.sub(
            "[^0-9a-zA-Z_-]+", "-", Numbered._remove_accents(string.lower())
        )

        # Remove leading digits
        return re.sub("^[^a-zA-Z]+", "", string)

    def __init__(self, elem: Element, doc: Doc):
        self._elem = elem
        self._doc = doc
        self._tag = None
        self._entry = Span(classes=["pandoc-numbering-entry"])
        self._link = Span(classes=["pandoc-numbering-link"])
        self._caption = None
        self._title = None
        self._description = None
        self._category = None
        self._basic_category = None
        self._classes = None
        self._first_section_level = None
        self._last_section_level = None
        self._leading = None
        self._number = None
        self._global_number = None
        self._section_number = None
        self._local_number = None
        self._section_alias = None
        self._alias = None

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
        self._get_content()[-1].text = self._get_content()[-1].text.replace(
            "##", "#", 1
        )

    def _replace_marker(self):
        self._compute_title()
        self._compute_description()
        self._compute_basic_category()
        self._compute_levels()
        self._compute_section_number()
        self._compute_section_alias()
        self._compute_leading()
        self._compute_category()
        self._compute_number()
        self._compute_tag()
        self._compute_alias()
        self._compute_local_number()
        self._compute_global_number()
        self._compute_data()

    def _compute_title(self):
        self._title = []
        if (
            isinstance(self._get_content()[-3], Str)
            and self._get_content()[-3].text[-1:] == ")"
        ):
            for i, item in enumerate(self._get_content()):
                if isinstance(item, Str) and item.text[0] == "(":
                    self._title = self._get_content()[i:-2]
                    # Detach from original parent
                    self._title.parent = None
                    self._title[0].text = self._title[0].text[1:]
                    self._title[-1].text = self._title[-1].text[:-1]
                    del self._get_content()[i - 1 : -2]
                    break
        self._title = list(self._title)

    def _compute_description(self):
        self._description = self._get_content()[:-2]
        # Detach from original parent
        self._description.parent = None
        self._description = list(self._description)

    def _compute_basic_category(self):
        if self._match.group("prefix") is None:
            self._basic_category = Numbered.identifier(
                "".join(map(stringify, self._description))
            )
        else:
            self._basic_category = self._match.group("prefix")
        if self._basic_category not in self._doc.defined:
            define(self._basic_category, self._doc)

    def _compute_levels(self):
        # Compute the first and last section level values
        self._first_section_level = len(self._match.group("hidden")) // 2
        self._last_section_level = len(self._match.group("header")) // 2

        # Get the default first and last section level
        if self._first_section_level == self._last_section_level == 0:
            self._first_section_level = self._doc.defined[self._basic_category][
                "first-section-level"
            ]
            self._last_section_level = self._doc.defined[self._basic_category][
                "last-section-level"
            ]

    def _compute_section_number(self):
        self._section_number = ".".join(
            map(str, self._doc.headers[: self._last_section_level])
        )

    def _compute_section_alias(self):
        strings = list(map(str, self._doc.aliases[: self._last_section_level]))
        for index, string in enumerate(strings):
            if string == "":
                strings[index] = "0"
        self._section_alias = ".".join(strings)

    def _compute_leading(self):
        # Compute the leading (composed of the section numbering and a dot)
        if self._last_section_level != 0:
            self._leading = self._section_number + "."
        else:
            self._leading = ""

    def _compute_category(self):
        self._category = self._basic_category + ":" + self._leading

        # Is it a new category?
        if self._category not in self._doc.count:
            self._doc.count[self._category] = 0

        self._doc.count[self._category] = self._doc.count[self._category] + 1

    def _compute_number(self):
        self._number = str(self._doc.count[self._category])

    def _compute_tag(self):
        self._classes = [
            self._category[:-1].replace(":", "-").replace(".", "-") + "-" + self._number
        ]

        # Determine the final tag
        if self._match.group("name") is None:
            self._tag = self._category + self._number
        else:
            self._tag = self._basic_category + ":" + self._match.group("name")
            self._classes.append(self._basic_category + "-" + self._match.group("name"))

        # Compute collections
        if self._basic_category not in self._doc.collections:
            self._doc.collections[self._basic_category] = []

        self._doc.collections[self._basic_category].append(self._tag)

    def _compute_alias(self):
        # Determine the final alias
        if not self._title:
            if self._section_alias:
                self._alias = (
                    self._basic_category
                    + ":"
                    + self._section_alias
                    + "."
                    + self._number
                )
            else:
                self._alias = self._basic_category + ":" + self._number
        else:
            if self._section_alias:
                self._alias = (
                    self._basic_category
                    + ":"
                    + self._section_alias
                    + "."
                    + Numbered.identifier(stringify(Span(*self._title)))
                )
            else:
                self._alias = (
                    self._basic_category
                    + ":"
                    + Numbered.identifier(stringify(Span(*self._title)))
                )

    def _compute_local_number(self):
        # Replace the '-.-.+.+...#' by the category count (omitting the hidden part)
        self._local_number = ".".join(
            map(
                str,
                self._doc.headers[self._first_section_level : self._last_section_level]
                + [self._number],
            )
        )

    def _compute_global_number(self):
        # Compute the global number
        if self._section_number:
            self._global_number = self._section_number + "." + self._number
        else:
            self._global_number = self._number

    def _compute_data(self):
        # pylint: disable=too-many-statements,no-member
        classes = self._doc.defined[self._basic_category]["classes"]
        if self._alias == self._tag:
            self._set_content(
                [
                    Span(),
                    Span(
                        identifier=self._tag,
                        classes=["pandoc-numbering-text"] + classes + self._classes,
                    ),
                ]
            )
        else:
            self._set_content(
                [
                    Span(identifier=self._alias),
                    Span(
                        identifier=self._tag,
                        classes=["pandoc-numbering-text"] + classes + self._classes,
                    ),
                ]
            )
        self._link.classes = self._link.classes + classes
        self._entry.classes = self._entry.classes + classes

        # Prepare the final data
        if self._title:
            self._get_content()[1].content = copy.deepcopy(
                self._doc.defined[self._basic_category]["format-text-title"]
            )
            self._link.content = copy.deepcopy(
                self._doc.defined[self._basic_category]["format-link-title"]
            )
            self._entry.content = copy.deepcopy(
                self._doc.defined[self._basic_category]["format-entry-title"]
            )
            self._caption = self._doc.defined[self._basic_category][
                "format-caption-title"
            ]
        else:
            self._get_content()[1].content = copy.deepcopy(
                self._doc.defined[self._basic_category]["format-text-classic"]
            )
            self._link.content = copy.deepcopy(
                self._doc.defined[self._basic_category]["format-link-classic"]
            )
            self._entry.content = copy.deepcopy(
                self._doc.defined[self._basic_category]["format-entry-classic"]
            )
            self._caption = self._doc.defined[self._basic_category][
                "format-caption-classic"
            ]

        # Compute caption (delay replacing %c at the end)
        title = stringify(Span(*self._title))
        description = stringify(Span(*self._description))
        self._caption = self._caption.replace("%t", title.lower())
        self._caption = self._caption.replace("%T", title)
        self._caption = self._caption.replace("%d", description.lower())
        self._caption = self._caption.replace("%D", description)
        self._caption = self._caption.replace("%s", self._section_number)
        self._caption = self._caption.replace("%g", self._global_number)
        self._caption = self._caption.replace("%n", self._local_number)
        self._caption = self._caption.replace("#", self._local_number)
        if self._doc.format in {"tex", "latex"}:
            self._caption = self._caption.replace("%p", "\\pageref{" + self._tag + "}")

        # Compute content
        if isinstance(self._elem, DefinitionItem):
            replace_description(Plain(*self._elem.term), self._description)
            replace_title(Plain(*self._elem.term), self._title)
            replace_global_number(Plain(*self._elem.term), self._global_number)
            replace_section_number(Plain(*self._elem.term), self._section_number)
            replace_local_number(Plain(*self._elem.term), self._local_number)
        else:
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
        if self._doc.format in {"tex", "latex"}:
            replace_page_number(self._link, self._tag)

        # Compute entry
        replace_description(self._entry, self._description)
        replace_title(self._entry, self._title)
        replace_global_number(self._entry, self._global_number)
        replace_section_number(self._entry, self._section_number)
        replace_local_number(self._entry, self._local_number)

        # Finalize the content
        if self._doc.format in {"tex", "latex"}:
            latex_category = re.sub("[^a-z]+", "", self._basic_category)
            latex = (
                "\\phantomsection"
                f"\\addcontentsline{{{latex_category}}}{{{latex_category}}}"
                f"{{\\protect\\numberline {{{self._leading + self._number}}}"
                f"{{\\ignorespaces {to_latex(self._entry)}"
                "}}"
            )
            self._get_content().insert(0, RawInline(latex, "tex"))


def replace_description(where: Element, description: list[Element]) -> None:
    """
    Replace description in where.

    Arguments
    ---------
    where
        where to replace
    description
        replace %D and %d by description
    """
    where.walk(partial(replacing, search="%D", replace=copy.deepcopy(description)))
    where.walk(
        partial(
            replacing,
            search="%d",
            replace=[item.walk(lowering) for item in copy.deepcopy(description)],
        )
    )


def replace_title(where: Element, title: list[Element]) -> None:
    """
    Replace title in where.

    Arguments
    ---------
    where
        where to replace
    title
        replace %T and %t by title
    """
    where.walk(partial(replacing, search="%T", replace=copy.deepcopy(title)))
    where.walk(
        partial(
            replacing,
            search="%t",
            replace=[item.walk(lowering) for item in copy.deepcopy(title)],
        )
    )


def replace_section_number(where: Element, section_number: int) -> None:
    """
    Replace section number in where.

    Arguments
    ---------
    where
        where to replace
    section_number
        replace %s by section_number
    """
    where.walk(partial(replacing, search="%s", replace=[Str(section_number)]))


def replace_global_number(where: Element, global_number: int) -> None:
    """
    Replace global number in where.

    Arguments
    ---------
    where
        where to replace
    global_number
        replace %g by global_number
    """
    where.walk(partial(replacing, search="%g", replace=[Str(global_number)]))


def replace_local_number(where: Element, local_number: int) -> None:
    """
    Replace local number in where.

    Arguments
    ---------
    where
        where to replace
    local_number
        replace %n and # by local_number
    """
    where.walk(partial(replacing, search="%n", replace=[Str(local_number)]))
    where.walk(partial(replacing, search="#", replace=[Str(local_number)]))


def replace_page_number(where: Element, tag: str):
    """
    Replace page number in where.

    Arguments
    ---------
    where
        where to replace
    tag
        replace %p by tag
    """
    where.walk(
        partial(
            replacing, search="%p", replace=[RawInline("\\pageref{" + tag + "}", "tex")]
        )
    )


def replace_count(where: Element, count: str) -> None:
    """
    Replace count in where.

    Arguments
    ---------
    where
        where to replace
    count
        replace %c by count
    """
    where.walk(partial(replacing, search="%c", replace=[Str(count)]))


def remove_useless_latex(elem: Element, _) -> list[Element] | None:
    """
    Clean up LaTeX element for entries.

    Arguments
    ---------
    elem
        elem to scan

    Returns
    -------
    list[Element] | None
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
            TableRow,
        ),
    ):
        return []
    return None


def to_latex(elem: Element) -> Any:
    """
    Convert element to LaTeX.

    Arguments
    ---------
    elem
        elem to convert

    Returns
    -------
    Any
        LaTex string
    """
    return convert_text(
        run_filters([remove_useless_latex], doc=Plain(elem)),
        input_format="panflute",
        output_format="latex",
        extra_args=["--no-highlight"],
    )


def define(category: str, doc: Doc) -> None:
    """
    Define a category in document.

    Arguments
    ---------
    category
        category to define
    doc
        pandoc document
    """
    # pylint: disable=line-too-long
    doc.defined[category] = {
        "first-section-level": 0,
        "last-section-level": 0,
        "format-text-classic": [Strong(Str("%D"), Space(), Str("%n"))],
        "format-text-title": [
            Strong(Str("%D"), Space(), Str("%n")),
            Space(),
            Emph(Str("(%T)")),
        ],
        "format-link-classic": [Str("%D"), Space(), Str("%n")],
        "format-link-title": [Str("%D"), Space(), Str("%n"), Space(), Str("(%T)")],
        "format-caption-classic": "%D %n",
        "format-caption-title": "%D %n (%T)",
        "format-entry-title": [Str("%T")],
        "classes": [category],
        "cite-shortcut": True,
        "listing-title": None,
        "listing-unnumbered": True,
        "listing-unlisted": True,
        "listing-identifier": True,
        "entry-tab": 1.5,
        "entry-space": 2.3,
    }
    if doc.format == "latex":
        doc.defined[category]["format-entry-classic"] = [Str("%D")]
        doc.defined[category]["entry-tab"] = 1.5
        doc.defined[category]["entry-space"] = 2.3
    else:
        doc.defined[category]["format-entry-classic"] = [Str("%D"), Space(), Str("%g")]


def lowering(elem: Element, _) -> None:
    """
    Lower element.

    Arguments
    ---------
    elem
        element to lower
    """
    if isinstance(elem, Str):
        elem.text = elem.text.lower()


def replacing(
    elem: Element,
    _,
    search: str | None = None,
    replace: list[Any] | None = None,
) -> list[Element]:
    """
    Replace an element.

    Arguments
    ---------
    elem
        element to scan
    search
        string to search
    replace
        string to replace

    Returns
    -------
    list[Element]
        The modified elements.
    """
    if replace is None:
        replace = []
    if isinstance(elem, Str):
        search_splitted = elem.text.split(search)
        if len(search_splitted) > 1:
            text = []

            if search_splitted[0] != "":
                text.append(Str(search_splitted[0]))

            for string in search_splitted[1:]:
                text.extend(replace)
                if string != "":
                    text.append(Str(string))

            return text

    return [elem]


def numbering(elem: Element, doc: Doc) -> None:
    """
    Add the numbering of an element.

    Arguments
    ---------
    elem
        element to number
    doc
        pandoc document
    """
    if isinstance(elem, Header):
        update_header_numbers(elem, doc)
        update_header_aliases(elem, doc)
    elif isinstance(elem, (Para, DefinitionItem)):
        numbered = Numbered(elem, doc)
        if numbered.tag is not None:
            doc.information[numbered.tag] = numbered


def referencing(elem: Element, doc: Doc) -> Element | None:
    """
    Add a reference for an element.

    Arguments
    ---------
    elem
        element to reference
    doc
        pandoc document

    Returns
    -------
    Element | None
        A Link or None
    """
    if isinstance(elem, Link):
        referencing_link(elem, doc)
    if isinstance(elem, Cite):
        return referencing_cite(elem, doc)
    if isinstance(elem, Span) and elem.identifier in doc.information:
        replace_count(elem, str(doc.count[doc.information[elem.identifier].category]))
    return None


def referencing_link(elem: Element, doc: Doc) -> None:
    """
    Add a eference link.

    Arguments
    ---------
    elem
        element to reference
    doc
        pandoc document
    """
    match = re.match("^#(?P<tag>([a-zA-Z][\\w:.-]*))$", elem.url)
    if match:
        tag = match.group("tag")
        if tag in doc.information:
            replace_title(elem, doc.information[tag].title)
            replace_description(elem, doc.information[tag].description)
            replace_global_number(elem, doc.information[tag].global_number)
            replace_section_number(elem, doc.information[tag].section_number)
            replace_local_number(elem, doc.information[tag].local_number)
            replace_count(elem, str(doc.count[doc.information[tag].category]))
            if doc.format in {"tex", "latex"}:
                replace_page_number(elem, tag)

            title = stringify(Span(*doc.information[tag].title))
            description = stringify(Span(*doc.information[tag].description))
            elem.title = elem.title.replace("%t", title.lower())
            elem.title = elem.title.replace("%T", title)
            elem.title = elem.title.replace("%d", description.lower())
            elem.title = elem.title.replace("%D", description)
            elem.title = elem.title.replace("%s", doc.information[tag].section_number)
            elem.title = elem.title.replace("%g", doc.information[tag].global_number)
            elem.title = elem.title.replace("%n", doc.information[tag].local_number)
            elem.title = elem.title.replace("#", doc.information[tag].local_number)
            elem.title = elem.title.replace(
                "%c", str(doc.count[doc.information[tag].category])
            )
            if doc.format in {"tex", "latex"}:
                elem.title = elem.title.replace("%p", "\\pageref{" + tag + "}")


def referencing_cite(elem: Element, doc: Doc) -> Element | None:
    """
    Cite reference.

    Arguments
    ---------
    elem
        element to reference
    doc
        pandoc document

    Returns
    -------
    Element | None
        A Link or None
    """
    if len(elem.content) == 1 and isinstance(elem.content[0], Str):
        match = re.match(
            "^(@(?P<tag>(?P<category>[a-zA-Z][\\w.-]*):"
            "(([a-zA-Z][\\w.-]*)|(\\d*(\\.\\d*)*))))$",
            elem.content[0].text,
        )
        if match:
            category = match.group("category")
            if category in doc.defined and doc.defined[category]["cite-shortcut"]:
                # Deal with @prefix:name shortcut
                tag = match.group("tag")
                if tag in doc.information:
                    ret = Link(
                        doc.information[tag].link,
                        url="#" + tag,
                        title=doc.information[tag].caption.replace(
                            "%c", str(doc.count[doc.information[tag].category])
                        ),
                    )
                    replace_count(ret, str(doc.count[doc.information[tag].category]))
                    return ret
    return None


def update_header_numbers(elem: Element, doc: Doc) -> None:
    """
    Update header numbers.

    Arguments
    ---------
    elem
        element to update
    doc
        pandoc document
    """
    if "unnumbered" not in elem.classes:
        doc.headers[elem.level - 1] = doc.headers[elem.level - 1] + 1
        for index in range(elem.level, 6):
            doc.headers[index] = 0


def update_header_aliases(elem: Element, doc: Doc) -> None:
    """
    Update header aliases.

    Arguments
    ---------
    elem
        element to update
    doc
        pandoc document
    """
    doc.aliases[elem.level - 1] = elem.identifier
    for index in range(elem.level, 6):
        doc.aliases[index] = ""


def prepare(doc: Doc) -> None:
    """
    Prepare document.

    Arguments
    ---------
    doc
        pandoc document
    """
    doc.headers = [0, 0, 0, 0, 0, 0]
    doc.aliases = ["", "", "", "", "", ""]
    doc.information = {}
    doc.defined = {}

    if "pandoc-numbering" in doc.metadata.content and isinstance(
        doc.metadata.content["pandoc-numbering"], MetaMap
    ):
        for category, definition in doc.metadata.content[
            "pandoc-numbering"
        ].content.items():
            if isinstance(definition, MetaMap):
                add_definition(category, definition, doc)

    doc.count = {}
    doc.collections = {}


def add_definition(category: str, definition: dict[str, MetaList], doc: Doc):
    """
    Add definition for a category.

    Arguments
    ---------
    category
        The category
    definition
        The definition
    doc
        The pandoc document
    """
    # Create the category with options by default
    define(category, doc)

    # Detect general options
    if "general" in definition:
        meta_cite(category, definition["general"], doc.defined)
        meta_listing(category, definition["general"], doc.defined)
        meta_levels(category, definition["general"], doc.defined)
        meta_classes(category, definition["general"], doc.defined)

    # Detect LaTeX options
    if doc.format in {"tex", "latex"}:
        if "latex" in definition:
            meta_format_text(category, definition["latex"], doc.defined)
            meta_format_link(category, definition["latex"], doc.defined)
            meta_format_caption(category, definition["latex"], doc.defined)
            meta_format_entry(category, definition["latex"], doc.defined)
            meta_entry_tab(category, definition["latex"], doc.defined)
            meta_entry_space(category, definition["latex"], doc.defined)
    # Detect standard options
    else:
        if "standard" in definition:
            meta_format_text(category, definition["standard"], doc.defined)
            meta_format_link(category, definition["standard"], doc.defined)
            meta_format_caption(category, definition["standard"], doc.defined)
            meta_format_entry(category, definition["standard"], doc.defined)


def meta_cite(
    category: str,
    definition: dict[str, MetaList],
    defined: dict[str, dict[str, list[str]]],  # noqa: TAE002
) -> None:
    """
    Compute cite for a category.

    Arguments
    ---------
    category
        The category
    definition
        The definition
    defined
        The defined parameter
    """
    if "cite-shortcut" in definition:
        if isinstance(definition["cite-shortcut"], MetaBool):
            defined[category]["cite-shortcut"] = definition["cite-shortcut"].boolean
        else:
            debug(
                "[WARNING] pandoc-numbering: cite-shortcut is not correct for category "
                + category
            )


def meta_format(
    category: str,
    definition: dict[str, MetaList],
    defined: dict[str, dict[str, Element]],  # noqa: TAE002
    tag: str,
) -> None:
    """
    Compute format text for a category and a tag.

    Arguments
    ---------
    category
        The category
    definition
        The definition
    defined
        The defined parameter
    tag
        The tag parameter
    """
    if tag in definition:
        if isinstance(definition[tag], MetaInlines):
            # Detach from original parent
            defined[category][tag] = definition[tag].content
            defined[category][tag].parent = None
        else:
            debug(
                f"[WARNING] pandoc-numbering: "
                f"{tag} is not correct for category {category}"
            )


# pylint:disable=too-many-branches
def meta_listing(
    category: str,
    definition: dict[str, MetaList],
    defined: dict[str, dict[str, list[str]]],  # noqa: TAE002
) -> None:
    """
    Compute listing for a category.

    Arguments
    ---------
    category
        The category
    definition
        The definition
    defined
        The defined parameter
    """
    meta_format(category, definition, defined, "listing-title")
    for key in ("listing-unnumbered", "listing-unlisted"):
        if key in definition:
            if isinstance(definition[key], MetaBool):
                defined[category][key] = definition[key].boolean
            else:
                debug(
                    f"[WARNING] pandoc-numbering: "
                    f"{key} is not correct for category {category}"
                )
    if "listing-identifier" in definition:
        if isinstance(definition["listing-identifier"], MetaBool):
            defined[category]["listing-identifier"] = definition[
                "listing-identifier"
            ].boolean
        elif (
            isinstance(definition["listing-identifier"], MetaInlines)
            and len(definition["listing-identifier"].content) == 1
            and isinstance(definition["listing-identifier"].content[0], Str)
        ):
            defined[category]["listing-identifier"] = (
                definition["listing-identifier"].content[0].text
            )
        else:
            debug(
                "[WARNING] pandoc-numbering: "
                "listing-identifier is not correct for category " + category
            )


def meta_format_text(
    category: str,
    definition: dict[str, MetaList],
    defined: dict[str, dict[str, list[str]]],  # noqa: TAE002
) -> None:
    """
    Compute format text for a category.

    Arguments
    ---------
    category
        The category
    definition
        The definition
    defined
        The defined parameter
    """
    meta_format(category, definition, defined, "format-text-classic")
    meta_format(category, definition, defined, "format-text-title")


def meta_format_link(
    category: str,
    definition: dict[str, MetaList],
    defined: dict[str, dict[str, list[str]]],  # noqa: TAE002
) -> None:
    """
    Compute format link for a category.

    Arguments
    ---------
    category
        The category
    definition
        The definition
    defined
        The defined parameter
    """
    meta_format(category, definition, defined, "format-link-classic")
    meta_format(category, definition, defined, "format-link-title")


def meta_format_entry(
    category: str,
    definition: dict[str, MetaList],
    defined: dict[str, dict[str, list[str]]],  # noqa: TAE002
) -> None:
    """
    Compute format entry for a category.

    Arguments
    ---------
    category
        The category
    definition
        The definition
    defined
        The defined parameter
    """
    meta_format(category, definition, defined, "format-entry-classic")
    meta_format(category, definition, defined, "format-entry-title")


def meta_format_caption(
    category: str,
    definition: dict[str, MetaList],
    defined: dict[str, dict[str, list[str]]],  # noqa: TAE002
) -> None:
    """
    Compute format caption for a category.

    Arguments
    ---------
    category
        The category
    definition
        The definition
    defined
        The defined parameter
    """
    for tag in ("format-caption-classic", "format-caption-title"):
        if tag in definition:
            if isinstance(definition[tag], MetaInlines):
                defined[category][tag] = stringify(definition[tag])
            else:
                debug(
                    f"[WARNING] pandoc-numbering: "
                    f"{tag} is not correct for category {category}"
                )


def meta_entry(
    category: str,
    definition: dict[str, MetaList],
    defined: dict[str, dict[str, float]],  # noqa: TAE002
    tag: str,
) -> None:
    """
    Compute entry tab for a category.

    Arguments
    ---------
    category
        The category
    definition
        The definition
    defined
        The defined parameter
    tag
        The tag parameter
    """
    if tag in definition:
        if isinstance(definition[tag], MetaString):
            value = definition[tag].text
        elif (
            isinstance(definition[tag], MetaInlines)
            and len(definition[tag].content) == 1
        ):
            value = definition[tag].content[0].text
        else:
            debug(
                f"[WARNING] pandoc-numbering: "
                f"{tag} is not correct for category {category}"
            )
            return
        # Get the element
        try:
            element = float(value)
            if element > 0:
                defined[category][tag] = element
            else:
                debug(
                    f"[WARNING] pandoc-numbering: "
                    f"{tag} must be positive for category {category}"
                )
        except ValueError:
            debug(
                f"[WARNING] pandoc-numbering: "
                f"{tag} is not correct for category {category}"
            )


def meta_entry_tab(
    category: str,
    definition: dict[str, MetaList],
    defined: dict[str, dict[str, float]],  # noqa: TAE002
) -> None:
    """
    Compute entry tab for a category.

    Arguments
    ---------
    category
        The category
    definition
        The definition
    defined
        The defined parameter
    """
    meta_entry(category, definition, defined, "entry-tab")


def meta_entry_space(
    category: str,
    definition: dict[str, MetaList],
    defined: dict[str, dict[str, float]],  # noqa: TAE002
) -> None:
    """
    Compute entry space for a category.

    Arguments
    ---------
    category
        The category
    definition
        The definition
    defined
        The defined parameter
    """
    meta_entry(category, definition, defined, "entry-space")


def meta_levels(
    category: str,
    definition: dict[str, MetaList],
    defined: dict[str, dict[str, float]],  # noqa: TAE002
) -> None:
    """
    Compute level for a category.

    Arguments
    ---------
    category
        The category
    definition
        The definition
    defined
        The defined parameter
    """
    if (
        "sectioning-levels" in definition
        and isinstance(definition["sectioning-levels"], MetaInlines)
        and len(definition["sectioning-levels"].content) == 1
    ):
        match = re.match(
            Numbered.header_regex, definition["sectioning-levels"].content[0].text
        )
        if match:
            # Compute the first and last levels section
            defined[category]["first-section-level"] = len(match.group("hidden")) // 2
            defined[category]["last-section-level"] = len(match.group("header")) // 2
    if "first-section-level" in definition:
        if isinstance(definition["first-section-level"], MetaString):
            value = definition["first-section-level"].text
        elif (
            isinstance(definition["first-section-level"], MetaInlines)
            and len(definition["first-section-level"].content) == 1
        ):
            value = definition["first-section-level"].content[0].text
        else:
            debug(
                "[WARNING] pandoc-numbering: "
                "first-section-level is not correct for category " + category
            )
            return

        # Get the level
        try:
            level = int(value) - 1
        except ValueError:
            debug(
                "[WARNING] pandoc-numbering: "
                "first-section-level is not correct for category " + category
            )

        if 0 <= level <= 6:
            defined[category]["first-section-level"] = level
        else:
            # pylint: disable=line-too-long
            debug(
                "[WARNING] pandoc-numbering: "
                "first-section-level must be positive or zero for category " + category
            )

    if "last-section-level" in definition:
        if isinstance(definition["last-section-level"], MetaString):
            value = definition["last-section-level"].text
        elif (
            isinstance(definition["last-section-level"], MetaInlines)
            and len(definition["last-section-level"].content) == 1
        ):
            value = definition["last-section-level"].content[0].text
        else:
            debug(
                "[WARNING] pandoc-numbering: "
                "last-section-level is not correct for category " + category
            )
            return

        # Get the level
        try:
            level = int(value)
        except ValueError:
            debug(
                "[WARNING] pandoc-numbering: "
                "last-section-level is not correct for category " + category
            )

        if 0 <= level <= 6:
            defined[category]["last-section-level"] = level
        else:
            # pylint: disable=line-too-long
            debug(
                "[WARNING] pandoc-numbering: "
                "last-section-level must be positive or zero for category " + category
            )


def meta_classes(
    category: str,
    definition: dict[str, MetaList],
    defined: dict[str, dict[str, list[str]]],  # noqa: TAE002
):
    """
    Compute classes for a category.

    Arguments
    ---------
    category
        The category
    definition
        The definition
    defined
        The defined parameter
    """
    if "classes" in definition and isinstance(definition["classes"], MetaList):
        defined[category]["classes"] = [
            stringify(elt) for elt in definition["classes"].content
        ]


def finalize(doc: Doc):
    """
    Finalize document.

    Arguments
    ---------
    doc
        The pandoc document
    """
    # Loop on all listings definition

    if doc.format in {"tex", "latex"}:
        # Add header-includes if necessary
        if "header-includes" not in doc.metadata:
            doc.metadata["header-includes"] = MetaList()
        # Convert header-includes to MetaList if necessary
        elif not isinstance(doc.metadata["header-includes"], MetaList):
            doc.metadata["header-includes"] = MetaList(doc.metadata["header-includes"])

        doc.metadata["header-includes"].append(
            MetaInlines(
                RawInline(
                    dedent(
                        r"""
                        \makeatletter
                        \@ifpackageloaded{subfig}{
                            \usepackage[subfigure]{tocloft}
                        }{
                            \usepackage{tocloft}
                        }
                        \makeatother
                        """
                    ),
                    "tex",
                )
            )
        )
        doc.metadata["header-includes"].append(
            MetaInlines(RawInline(r"\usepackage{etoolbox}", "tex"))
        )

    i = 0
    listof = []
    for category, definition in doc.defined.items():
        if definition["listing-title"] is not None:
            # pylint: disable=consider-using-f-string
            if doc.format in {"tex", "latex"}:
                latex_category = re.sub("[^a-z]+", "", category)
                text = convert_text(
                    Plain(*definition["listing-title"]),
                    input_format="panflute",
                    output_format="latex",
                )
                latex = (
                    r"\newlistof{%s}{%s}{%s}"
                    r"\renewcommand{\cft%stitlefont}{\cfttoctitlefont}"
                    r"\setlength{\cft%snumwidth}{\cftfignumwidth}"
                    r"\setlength{\cft%sindent}{\cftfigindent}"
                    % (
                        latex_category,
                        latex_category,
                        text,
                        latex_category,
                        latex_category,
                        latex_category,
                    )
                )
                doc.metadata["header-includes"].append(
                    MetaInlines(RawInline(latex, "tex"))
                )
                if definition["listing-identifier"] is False:
                    listof.append(f"\\listof{latex_category}")
                elif definition["listing-identifier"] is True:
                    listof.append(
                        f"\\phantomsection\\label{{{Numbered.identifier(text)}}}"
                        f"\\listof{latex_category}"
                    )
                else:
                    listof.append(
                        f"\\phantomsection\\label{{{definition['listing-identifier']}}}"
                        f"\\listof{latex_category}"
                    )
            else:
                classes = ["pandoc-numbering-listing"] + definition["classes"]

                if definition["listing-unnumbered"]:
                    classes.append("unnumbered")

                if definition["listing-unlisted"]:
                    classes.append("unlisted")

                if definition["listing-identifier"] is False:
                    header = Header(
                        *definition["listing-title"], level=1, classes=classes
                    )
                elif definition["listing-identifier"] is True:
                    header = Header(
                        *definition["listing-title"], level=1, classes=classes
                    )
                    header = convert_text(
                        convert_text(
                            header, input_format="panflute", output_format="markdown"
                        ),
                        output_format="panflute",
                    )[0]
                else:
                    header = Header(
                        *definition["listing-title"],
                        level=1,
                        classes=classes,
                        identifier=definition["listing-identifier"],
                    )

                doc.content.insert(i, header)
                i = i + 1

                table = table_other(doc, category, definition)

                if table:
                    doc.content.insert(i, table)
                    i = i + 1

    if doc.format in {"tex", "latex"}:
        header = (
            r"\ifdef{\mainmatter}"
            r"{\let\oldmainmatter\mainmatter"
            r"\renewcommand{\mainmatter}[0]{%s\oldmainmatter}}"
            r"{}"
        )
        doc.metadata["header-includes"].append(
            MetaInlines(RawInline(header % "\n".join(listof), "tex"))
        )

        latex = r"\ifdef{\mainmatter}{}{%s}"
        doc.content.insert(0, Plain(RawInline(latex % "\n".join(listof), "tex")))


def table_other(doc: Doc, category: str, _) -> BulletList | None:
    """
    Compute other code for table.

    Arguments
    ---------
    doc
        pandoc document
    category
        category numbered

    Returns
    -------
    BulletList | None
        A BulletList or None
    """
    if category in doc.collections:
        # Return a bullet list
        return BulletList(
            *(
                ListItem(Plain(Link(doc.information[tag].entry, url="#" + tag)))
                for tag in doc.collections[category]
            )
        )
    return None


def link_color(doc: Doc) -> str:
    """
    Compute LaTeX code for toc.

    Arguments
    ---------
    doc
        pandoc document

    Returns
    -------
    str
        LaTeX code for links.
    """
    # Get the link color
    metadata = doc.get_metadata()
    if "toccolor" in metadata:
        return "\\hypersetup{linkcolor=" + str(metadata["toccolor"]) + "}"
    return "\\hypersetup{linkcolor=black}"


def main(doc: Doc | None = None) -> None:
    """
    Produce the final document.

    Parameters
    ----------
    doc
        pandoc document
    """
    run_filters([numbering, referencing], prepare=prepare, doc=doc, finalize=finalize)
