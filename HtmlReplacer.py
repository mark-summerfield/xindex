#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

"""
This module assumes that each line is an HTML fragment at most
surrounded by <p>...</p> (although usually not). The reason this holds
in XindeX is that the Widgets/LineEdit/HtmlLineEdit.py classes have
their own custom toHtml() method (rather than using Qt's standard one),
that returns extremely pared-down HTML.

Usage:

    text = HtmlReplacer.sub("year", "2016", line)

    # or:

    replacer = HtmlReplacer.Replacer(literal="year", replacement="2016")
    replacer.setHtml(line)
    paraMatch = None
    while True:
        paraMatch = replacer.search()
        if paraMatch is None:
            break # No (more) found
        if not replacer.replace():
            break # No (more) to be replaced
    text = replacer.html # Result

"""

import collections
import copy
import re
import html
import html.parser

from Const import PartKind


ParaMatch = collections.namedtuple(
    "ParaMatch", "replacement text start end")
_ParaMatch = collections.namedtuple(
    "_ParaMatch", "replacement text partOffset textOffset start end")


class Replacer(html.parser.HTMLParser):

    def __init__(self, *, pattern=None, literal=None, replacement="",
                 wholewords=False, ignorecase=False):
        super().__init__(convert_charrefs=True)
        self.clear()
        flags = re.MULTILINE | re.DOTALL
        if ignorecase:
            flags |= re.IGNORECASE
        if literal is not None:
            self.literal = True
            fmt = r"\b{}\b" if wholewords else "{}"
            self.regex = re.compile(fmt.format(re.escape(literal)), flags)
        else:
            self.literal = False
            self.regex = re.compile(pattern, flags)
        self.replacement = replacement


    def setHtml(self, text, start=0):
        self.clear()
        self.start = start
        if text is None:
            text = "<p></p>"
        elif not text.lstrip().startswith(("<p>", "<P>")):
            text = "<p>{}</p>".format(text)
        super().feed(text)


    @property
    def html(self):
        return self._htmlForParts(self.parts)


    def _htmlForParts(self, parts):
        if not parts:
            return ""
        if parts[0][PartKind.TEXT] in {"<p>", "<P>"}:
            parts = parts[1:]
        if parts[-1][PartKind.TEXT] in {"</p>", "</P>"}:
            parts = parts[:-1]
        return "".join(text for tag, text in parts)


    def search(self):
        text = html.unescape("".join(text for tag, text in self.parts
                                     if tag is PartKind.TEXT))
        if not text:
            return None
        self.paraMatch = None
        match = self.regex.search(text, self.start)
        if match is not None:
            replacement = (self.replacement if self.literal else
                           match.expand(self.replacement))
            partOffset, textOffset = self._offsetForIndex(match.start())
            text = self._htmlIfReplaced(partOffset, textOffset,
                                        match.start(), match.end(),
                                        replacement)
            self.paraMatch = _ParaMatch(replacement, text, partOffset,
                                        textOffset, match.start(),
                                        match.end())
            self.start = match.start() + 1
        if self.paraMatch is None:
            return None
        return ParaMatch(self.paraMatch.replacement, self.paraMatch.text,
                         self.paraMatch.start, self.paraMatch.end)


    def _htmlIfReplaced(self, partOffset, textOffset, start, end,
                        replacement):
        parts = copy.deepcopy(self.parts)
        self._replaceText(parts, partOffset, textOffset, start, end,
                          replacement)
        return self._htmlForParts(parts)


    def _replaceText(self, parts, partOffset, textOffset, start, end,
                     replacement):
        text = html.unescape(parts[partOffset][PartKind.TEXT])
        start -= textOffset
        end -= textOffset
        text = text[:start] + replacement + text[end:]
        parts[partOffset] = (PartKind.TEXT, html.escape(text))


    def _offsetForIndex(self, start):
        textOffset = end = 0
        for partOffset, (tag, text) in enumerate(self.parts):
            if tag is PartKind.TEXT:
                textOffset = end
                end += len(text)
                if textOffset <= start < end:
                    return partOffset, textOffset


    def replace(self):
        if self.paraMatch is None:
            return False
        match = self.paraMatch
        self._replaceText(self.parts, match.partOffset, match.textOffset,
                          match.start, match.end, match.replacement)
        self.skip()
        return True


    def skip(self):
        self.paraMatch = None
        self.start += 1



    def clear(self):
        self.close()
        self.start = 0
        self.parts = []
        self.paraMatch = None


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
        self.parts.append((PartKind.TEXT, html.escape(data, quote=False)))


def sub(pattern, replacement, text):
    replacer = Replacer(pattern=pattern, replacement=replacement)
    replacer.setHtml(text)
    paraMatch = None
    while True:
        paraMatch = replacer.search()
        if paraMatch is None:
            break # No (more) found
        if not replacer.replace():
            break # No (more) to be replaced
    return replacer.html # Result
