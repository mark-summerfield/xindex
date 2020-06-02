#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import html.parser
import re

import roman

import Lib
from Const import EN_DASH, PartKind
from . import Util
from . import Page
from . import PageRange
from . import PreParser


IS_NUMERIC_RX = re.compile(
    r"[0-9]+|\b[CDILMVXcdilmvx]+\b|@([0-9]+(?:\.[0-9]+)*)$")
RANGE_RX = re.compile(r"([-" + EN_DASH + r"])")
COMMA_RX = re.compile(r",(?![^(]*[)])")

HYPHENS = "-" + EN_DASH


class Parser(list):

    def feed(self, text):
        parser = PreParser.Parser()
        parser.feed("<p>{}</p>".format(text))
        text = parser.toHtml()
        parser = _Parser()
        for chunk in COMMA_RX.split(text):
            parser.feed("<p>{}</p>".format(chunk.strip()))
            if parser.page is not None:
                self.append(parser.page)
        if not self:
            self[:] = [Page.Page(text.strip(HYPHENS))]


    def toHtml(self, pageRange=PageRange.pageRangeCMS16):
        self.sort()
        prev = None
        pages = []
        for page in self:
            if prev is None or page != prev:
                pages.append(page.toHtml(pageRange=pageRange))
                prev = page
        return ", ".join(pages).strip(", ").replace(", ,", ",")


    def toPlainText(self, pageRange=PageRange.pageRangeFull):
        def numeric(x):
            if x[0].isdigit():
                return int(x) + Util.INTEGER_OFFSET
            try:
                return roman.fromRoman(x)
            except roman.RomanError:
                return 0

        pages = set()
        for page in self:
            _populate_pages(page, pages, pageRange)
        return " ".join(sorted((str(x) for x in pages), key=numeric))


    def asNumberPairs(self):
        pages = set()
        for page in self:
            if page.text:
                start = Util.valueOf(page.text)
                if start is not None:
                    end = _end(start, page, PageRange.pageRangeFull)
                    pages.add((start, end))
        return pages


    def count(self):
        pages = set()
        for page in self:
            if page.text:
                pages.add(page.text)
        return len(pages)


    def hasOverlappingPages(self):
        pages = []
        for page in self:
            if not page.text:
                continue
            start = Util.valueOf(page.text)
            end = _end(start, page, PageRange.pageRangeFull)
            if page.text[0].isdigit(): # decimal
                page_range = {start}
                while start <= end:
                    page_range.add(start)
                    start += 1
                pages += list(page_range)
            else: # roman
                try:
                    page_range = {roman.toRoman(start)}
                    while start <= end:
                        page_range.add(roman.toRoman(start))
                        start += 1
                    pages += list(page_range)
                except roman.RomanError:
                    pages.append(page.text)
        return len(frozenset(pages)) != len(pages)


    def _combinedOverlappingPages(self):
        # This must use full page ranges: so the caller must wrap it in
        # a call to Pages.sortedPages(pages, pageRange) to get compact
        # page ranges.
        for page in self:
            if not page.text:
                continue
            page._span = None
            page._casefold = page.text.casefold() == page.text
            pages = set()
            _populate_pages(page, pages, PageRange.pageRangeFull)
            if pages and isCombinable(page.sort_value):
                page._span = frozenset(pages)
        replacer = RangeReplacer()
        combined = [self[0].toHtml(pageRange=PageRange.pageRangeFull)]
        prevIndex = 0
        for i, page in enumerate(self[1:], 1):
            prev = self[prevIndex]
            spanOK = page._span is not None and prev._span is not None
            if spanOK and page._span <= prev._span:
                continue # Completely contained in prev
            if spanOK and prev._span & page._span:
                span = prev._span | page._span # Overlapping
                text = prev.toHtml(pageRange=PageRange.pageRangeFull)
                if not RANGE_RX.search(Lib.htmlToPlainText(text)):
                    # Case: n, n-m
                    text = page.toHtml(pageRange=PageRange.pageRangeFull)
                replacer.setHtml(text)
                start = str(min(span))
                end = str(max(span))
                if prev._casefold:
                    start = start.casefold()
                    end = end.casefold()
                combined[-1] = replacer.replace(start, end)
                prev._span = span
            else:
                combined.append(page.toHtml(
                                pageRange=PageRange.pageRangeFull))
                prevIndex = i
        return ", ".join(combined).strip(", ").replace(", ,", ",")


    def renumbered(self, options, pageRange=PageRange.pageRangeCMS16):
        for page in self:
            self._renumber_page(page, options)
        return self.toHtml(pageRange)


    def _renumber_page(self, page, options, fromValue=None):
        if not page.text:
            return
        inRange = False
        originalFromValue = None
        page._sort_value = None # Force recalculation
        if page.text[0].isdigit(): # decimal
            if options.decimalchange:
                match = Util.LEADING_DIGITS_RX.search(page.text)
                if match is not None:
                    value = int(match.group(1))
                    if options.decimalfrom <= value <= options.decimalto:
                        inRange = True
                        originalFromValue = value
                        value = self._increment_page(fromValue, value,
                                                     options.decimalchange)
                        page.text = str(value) + page.text[match.end():]
        elif options.romanchange: # try roman
            match = Util.LEADING_ROMAN_RX.search(page.text)
            if match is not None:
                try:
                    text = match.group(1)
                    value = roman.fromRoman(text.upper())
                    if options.romanfrom <= value <= options.romanto:
                        inRange = True
                        originalFromValue = value
                        value = self._increment_page(fromValue, value,
                                                     options.romanchange)
                        value = roman.toRoman(value)
                        if text.lower() == text:
                            value = value.lower()
                        page.text = value + page.text[match.end():]
                except roman.RomanError:
                    pass # Shouldn't happen
        if inRange: # Winkle out the to page wherever it lurks!
            to_page = page.to_page
            if to_page is None:
                for child in page.children:
                    if child is not None and child.to_page is not None:
                        to_page = child.to_page
                        break
            if to_page is not None:
                self._renumber_page(to_page, options, originalFromValue)


    def _increment_page(self, fromValue, value, amount):
        if fromValue is not None:
            value = int(PageRange.pageRangeFull(fromValue, value))
        value += amount
        return max(1, value)


    def toIndividualHtmlPages(self, pageRange=PageRange.pageRangeCMS16):
        # Almost identical to .toHtml()
        self.sort()
        prev = None
        pages = []
        for page in self:
            if prev is None or page != prev:
                pages.append(page.toHtml(pageRange=pageRange))
                prev = page
        return pages


class _Parser(html.parser.HTMLParser):

    def __init__(self):
        super().__init__(convert_charrefs=True)
        # Preserve across feeds
        self.fontfamily = [] # Empty means std family
        self.fontsize = [] # Empty means std size
        self.bold = 0
        self.italic = 0
        self.subscript = 0
        self.superscript = 0
        self.underline = 0
        self.ids = []


    def feed(self, text):
        # Reset every feed
        self.page = None
        self.isToPage = False
        super().feed(text)


    def handle_starttag(self, tag, attrs):
        if tag == "b":
            self.bold += 1
        elif tag == "i":
            self.italic += 1
        elif tag == "span":
            for name, value in attrs:
                if name == "style":
                    for match in Lib.KEY_VALUE_RX.finditer(value):
                        key = match.group("key")
                        if key == "font-family":
                            self.ids.append("font")
                        if key == "font-family":
                            value = match.group("value").strip("'\" ")
                            self.fontfamily.append(value)
                        elif key == "font-size":
                            self.fontsize.append(match.group("value"))
        elif tag == "sub":
            self.subscript += 1
        elif tag == "sup":
            self.superscript += 1
        elif tag == "u":
            self.underline += 1


    def handle_endtag(self, tag):
        if tag == "b":
            self.bold -= 1
        elif tag == "i":
            self.italic -= 1
        elif tag == "span":
            id = self.ids.pop()
            if id == "font":
                self.fontfamily.pop()
                self.fontsize.pop()
        elif tag == "sub":
            self.subscript -= 1
        elif tag == "sup":
            self.superscript -= 1
        elif tag == "u":
            self.underline -= 1


    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        match = RANGE_RX.search(text)
        if match is not None:
            start = text[:match.start()]
            if start:
                self._process_text(start)
            self.isToPage = True
            end = text[match.end():]
            if end:
                self._process_text(end)
        else:
            self._process_text(text)


    def _process_text(self, text):
        fontfamily = self.fontfamily[-1] if self.fontfamily else None
        fontsize = (Lib.sanePointSize(self.fontsize[-1]) if self.fontsize
                    else None)
        numeric = isNumeric(text)
        page = Page.Page(text.strip(HYPHENS), self.bold > 0, fontfamily,
                         fontsize, self.italic > 0, self.subscript > 0,
                         self.superscript > 0, self.underline > 0,
                         numeric)
        if self.page is not None and self.isToPage:
            if self.page.to_page is None:
                # The strips are to ensure no whitespace before or after
                # range sep.
                if self.page.children:
                    self.page.children[-1].text = (
                        self.page.children[-1].text.rstrip())
                else:
                    self.page.text = self.page.text.rstrip()
                page.text = page.text.lstrip()
                self.page.to_page = page
            else:
                self.page.to_page.children.append(page)
        elif self.page is None:
            self.page = page
        else:
            self.page.children.append(page)


def isNumeric(text):
    return IS_NUMERIC_RX.search(text) is not None


def isCombinable(sort_value):
    """We can only combine simple whole number page numbers"""
    parts = [int(x) for x in sort_value.split()]
    return not sum(parts[1:])


def _end(start, page, pageRange):
    end = 0 if page.to_page is None else Util.valueOf(page.to_page.text)
    end = int(pageRange(start, end)) if end else 0
    return end


def _populate_pages(page, pages, pageRange):
    if not page.text:
        return
    start = Util.valueOf(page.text)
    end = _end(start, page, pageRange)
    if page.text[0].isdigit(): # decimal
        pages.add(start)
        while start <= end:
            pages.add(start)
            start += 1
    else: # roman
        try:
            pages.add(roman.toRoman(start))
            while start <= end:
                pages.add(roman.toRoman(start))
                start += 1
        except roman.RomanError:
            pages.add(page.text)


class RangeReplacer(html.parser.HTMLParser):

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.clear()


    def clear(self):
        self.close()
        self.hyphenIndex = None
        self.parts = []


    def replace(self, start, end):
        if self.hyphenIndex is not None:
            index = self.hyphenIndex - 1
            while index >= 0:
                if self.parts[index][0] is PartKind.TEXT:
                    self.parts[index] = (PartKind.TEXT, html.escape(start))
                    break
                index -= 1
            index = self.hyphenIndex + 1
            while index < len(self.parts):
                if self.parts[index][0] is PartKind.TEXT:
                    self.parts[index] = (PartKind.TEXT, html.escape(end))
                    break
                index += 1
        return self.html


    def setHtml(self, text):
        self.clear()
        if text is None:
            text = "<p></p>"
        elif not text.lstrip().startswith(("<p>", "<P>")):
            text = "<p>{}</p>".format(text)
        super().feed(text)


    @property
    def html(self):
        if not self.parts:
            return ""
        if self.parts[0][PartKind.TEXT] in {"<p>", "<P>"}:
            self.parts = self.parts[1:]
        if self.parts[-1][PartKind.TEXT] in {"</p>", "</P>"}:
            self.parts = self.parts[:-1]
        return "".join(text for tag, text in self.parts)


    def handle_starttag(self, tag, attrs):
        parts = ["<" + tag]
        for name, value in attrs:
            parts.append(' {}="{}"'.format(name, html.escape(value,
                                                             quote=False)))
        parts.append(">")
        self.parts.append((PartKind.TAG, "".join(parts)))


    def handle_endtag(self, tag):
        self.parts.append((PartKind.TAG, "</{}>".format(tag)))


    def handle_data(self, data):
        match = RANGE_RX.search(data)
        if match is not None:
            start = match.start()
            end = match.end()
            self.hyphenIndex = len(self.parts)
            text = data[:start]
            if text:
                self.parts.append((PartKind.TEXT,
                                   html.escape(text, quote=False)))
                self.hyphenIndex += 1
            text = data[start:end]
            if text:
                self.parts.append((PartKind.TEXT,
                                   html.escape(text, quote=False)))
            text = data[end:]
            if text:
                self.parts.append((PartKind.TEXT,
                                   html.escape(text, quote=False)))
        else:
            self.parts.append((PartKind.TEXT,
                               html.escape(data, quote=False)))
