#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import re

import roman

import Lib
import Normalize
from Const import EN_DASH
from . import Util


NOT_LETTER_OR_DIGIT_RX = re.compile(r"[^0-9a-z]")
NUMERIC_END_RX = re.compile(r"[cdilmvx]+\b$|[0-9]+$")
PARENTHESES_RX = re.compile(r"[()]")
ROMAN_INSIDE_RX = re.compile(r"^(.*?)\b([cdilmvx]+)\b(.*?)")
WORD_RX = re.compile(r"^[^\d;:.][\w;:.]{3,}$")


class Page:

    __slots__ = ("text", "bold", "fontfamily", "fontsize", "italic",
                 "subscript", "superscript", "underline", "numeric",
                 "to_page", "sep", "prefix", "children", "_span",
                 "_casefold", "_sort_value")

    def __init__(self, text, bold=False, fontfamily=None, fontsize=None,
                 italic=False, subscript=False, superscript=False,
                 underline=False, numeric=False):
        self.text = text
        self.bold = bold
        self.fontfamily = fontfamily
        self.fontsize = fontsize
        self.italic = italic
        self.subscript = subscript
        self.superscript = superscript
        self.underline = underline
        self.numeric = numeric
        self.to_page = None
        self.sep = EN_DASH
        self.prefix = ""
        self.children = []
        self._span = None
        self._casefold = False
        self._sort_value = None


    @property
    def sort_value(self):
        if self._sort_value is None:
            self._computeSortValue()
        return self._sort_value


    def __iter__(self):
        yield self
        for child in self.children:
            yield from iter(child)


    def iterate(self, depth=0):
        yield (depth, self)
        for child in self.children:
            yield from child.iterate(depth + 1)


    @property
    def _details(self):
        return "{}:{}:{}:{}:{}:{}:{}:{}".format(
            int(self.bold), self.fontfamily, self.fontsize,
            int(self.italic), int(self.subscript),
            int(self.superscript), int(self.underline),
            int(self.to_page is not None))


    def __eq__(self, other): # Potentially expensive
        if self.text != other.text:
            return False
        if self._details != other._details:
            return False
        if self.to_page != other.to_page:
            return False
        child_info = []
        for child in iter(self.children):
            child_info.append((child.text, child._details))
        other_info = []
        for other in iter(other.children):
            other_info.append((other.text, other._details))
        return child_info == other_info


    def __lt__(self, other):
        return self.sort_value < other.sort_value


    def __str__(self):
        parts = ["«{}»".format(self.text)]
        if self.subscript:
            parts.append("sub")
        if self.superscript:
            parts.append("sup")
        if self.underline:
            parts.append("under")
        if self.italic:
            parts.append("italic")
        if self.bold:
            parts.append("bold")
        if self.fontfamily is not None:
            parts.append(self.fontfamily)
            parts.append(self.fontsize)
        if self.to_page is not None:
            parts.extend((self.sep, str(self.to_page)))
            if self.to_page.children:
                parts.extend([str(child) for child in
                              self.to_page.children])
        return " ".join(parts)


    def toHtml(self, from_value=None, *, pageRange=None):
        pre = []
        post = []
        if self.subscript:
            pre.append("<sub>")
            post.append("</sub>")
        if self.superscript:
            pre.append("<sup>")
            post.append("</sup>")
        if self.underline:
            pre.append("<u>")
            post.append("</u>")
        if self.italic:
            pre.append("<i>")
            post.append("</i>")
        if self.bold:
            pre.append("<b>")
            post.append("</b>")
        if self.fontfamily is not None:
            pre.append(
                """<span style="font-size: {}; font-family: '{}';">"""
                .format(Lib.sanePointSize(self.fontsize), self.fontfamily))
            post.append("</span>")
        text = self.text
        if from_value and Util.isdigit(text):
            to_value = Util.valueOf(self.text) or 0
            text = pageRange(from_value, to_value)
        parts = pre + [text] + list(reversed(post))
        prefix = ""
        prev = self.text
        parentheses = text.count("(") - text.count(")")
        for child in self.children:
            if parentheses:
                prefix = (" " if NUMERIC_END_RX.search(prev) is None else
                          ", ")
            elif (not child.superscript and not child.subscript and
                  WORD_RX.match(child.text) is not None):
                prefix = " "
            text = child.toHtml(pageRange=pageRange)
            if parts[-1].endswith(("(", EN_DASH)):
                prefix = ""
            parts.extend((prefix, text))
            prev = child.text
            prefix = ""
            parentheses += text.count("(") - text.count(")")
        if self.to_page is not None:
            from_value = Util.valueOf(self.text) or 0
            sep = self.sep
            if self.underline and self.to_page.underline:
                sep = "<u>{}</u>".format(sep)
            if self.italic and self.to_page.italic:
                sep = "<i>{}</i>".format(sep)
            if self.bold and self.to_page.bold:
                sep = "<b>{}</b>".format(sep)
            parts.extend((sep, self.to_page.toHtml(from_value,
                         pageRange=pageRange)))
        return "".join(parts)


    def _computeSortValue(self):
        def numberForText(text):
            if not text:
                return 0
            text = text.upper()
            if len(text) == 1:
                return 100 * ord(text[0])
            return (100 * ord(text[0])) + ord(text[1])

        texts = []
        for child in self:
            text = Normalize.normalize(child.text.casefold())
            i = text.rfind("@")
            if i > -1:
                text = text[i + 1:]
            texts.append(PARENTHESES_RX.sub(" ", text))
        values = []
        for text in NOT_LETTER_OR_DIGIT_RX.split(" ".join(texts)):
            if text:
                value = Util.valueOf(text, addOffset=True)
                if value is not None:
                    values.append(value)
                else:
                    if Util.isdigit(text[0]):
                        index = 1
                        while (index < len(text) and
                                Util.isdigit(text[index])):
                            index += 1
                        values.append(int(text[:index]) +
                                      Util.INTEGER_OFFSET)
                        rest = text[index:]
                        if rest:
                            try:
                                values.append(roman.fromRoman(
                                              rest.upper()) +
                                              Util.ROMAN_OFFSET)
                            except roman.RomanError:
                                values.append(numberForText(rest))
                    elif text[0] in "cdilmvx":
                        match = ROMAN_INSIDE_RX.search(text)
                        if match is not None:
                            before = match.group(1)
                            if before:
                                values.append(numberForText(before))
                            try:
                                digits = match.group(2)
                                values.append(roman.fromRoman(
                                              digits.upper()) +
                                              Util.ROMAN_OFFSET)
                            except roman.RomanError:
                                values.append(numberForText(digits))
                            after = match.group(3)
                            if after:
                                values.append(numberForText(after))
                        else:
                            values.append(numberForText(text))
                    else:
                        values.append(numberForText(text))
        values = values + (
            [0] * (Util.SORT_VALUE_COMPONENT_COUNT - len(values)))
        self._sort_value = " ".join(("{:010}".format(value) for value in
                                    values))
