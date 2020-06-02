#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import collections
import functools
import html
import inspect
import math
import os
import pathlib
import re
import sys

import HtmlReplacer
from Config import Gopt
from Const import (EXTENSION, SUB_INDICATOR, UTF8, VISUAL_SPACE,
                   DEFAULT_ELIDE_LEN, MIN_FONT_SIZE)


KEY_VALUE_RX = re.compile(r"\s*(?P<key>[-\w]+):\s*(?P<value>[^;]+);\s*")
HTML_TAGS_RX = re.compile(r"<[^>]*?>")
HTML_TAGS_CAP_RX = re.compile(r"(<[^>]*?>)")
SPACE_CAP_RX = re.compile(r"(\s+)")
EMPTY_TAGS = re.compile(r"<(?P<tag>[A-Za-z]+)[^>]*?></(?P=tag)>")
STRIP_PARA = re.compile(r"^\s*(?:<[Pp]>)?(.*)(?:<\/[Pp]>)?\s*$")
STRIP_INC_RX = re.compile(r"(?:\s*[(]\d+[)])?[.][Xx][Ii][Xx]$")
NAME_ABBREV_RX = re.compile(
    r"^(?P<name>[^\xAB\n]+)(?:\xAB(?P<abbrev>[^\xBB]+)\xBB)?\n")
MONO_FONT_RX = re.compile(r"""\bmono|\bcourier|\btypewriter|\bconsolas|
\bletter\sgothic|\blucida\sconsole|\bmonaco|\bpica\b|\bprestige\selite""",
                          re.MULTILINE | re.IGNORECASE | re.VERBOSE)
ACRONYM_SWAP_RX = re.compile(r"([^(]+)(\([^)]+\))")

# Eliminates any attributes except size and family, and is order independent
PATCH_FONT_RX = re.compile(r"""
<span\s+?style=(?P<quote>["'])
[^\1]*?
(?:
    font-size:\s*?(?P<size1>\d+)pt;
    [^\1]*?
    font-family:\s*?(?P<family1>[^;]+);
|
    font-family:\s*?(?P<family2>[^;]+);
    [^\1]*?
    font-size:\s*?(?P<size2>\d+)pt;
)
[^\1]*?
(?P=quote)>
""", re.MULTILINE | re.VERBOSE)


def sanePointSize(size):
    if isinstance(size, str) and size.endswith("pt"):
        points = int(size[:-2])
        return "{}pt".format(Gopt.StdFontSize if points <= 0 else
                             max(MIN_FONT_SIZE, points))
    size = int(size)
    return max(MIN_FONT_SIZE, Gopt.StdFontSize if size <= 0 else size)


@functools.lru_cache(maxsize=None)
def htmlToPlainText(htmlText):
    return "" if not htmlText else html.unescape(
        HTML_TAGS_RX.sub("", htmlText.replace(VISUAL_SPACE, " ")))


@functools.lru_cache(maxsize=None)
def htmlToCanonicalText(htmlText):
    return "" if not htmlText else html.unescape(
        HTML_TAGS_RX.sub("", htmlText.replace(VISUAL_SPACE,
                                              " "))).casefold()


@functools.lru_cache(maxsize=None)
def elide(text, maxlen=DEFAULT_ELIDE_LEN):
    if maxlen is None:
        return text
    text = htmlToPlainText(text)
    if len(text) <= maxlen:
        return text
    ellipsis = "…{}".format(SUB_INDICATOR) if SUB_INDICATOR in text else "…"
    return "{}{}{}".format(text[:maxlen // 2], ellipsis,
                           text[-maxlen // 2:])


@functools.lru_cache(maxsize=None)
def elideHtml(text, maxlen=DEFAULT_ELIDE_LEN, *, allowPara=True):
    if maxlen is None:
        return STRIP_PARA.sub(r"\1", text) if not allowPara else text
    plain = htmlToPlainText(text)
    if len(plain) <= maxlen:
        return STRIP_PARA.sub(r"\1", text) if not allowPara else text
    ellipsis = "…"
    maxlen -= 1 # Account for the ellipsis that's added
    chunks = []
    for chunk in HTML_TAGS_CAP_RX.split(text):
        if chunk.startswith("<"):
            chunks.append(chunk)
        else:
            chunks += SPACE_CAP_RX.split(chunk)
    left = []
    right = []
    count = 0
    which = left
    while chunks:
        chunk = chunks.pop(0 if which is left else -1)
        if chunk.startswith("<"):
            which.append(chunk)
        elif count + len(chunk) <= maxlen:
            which.append(chunk)
            count += len(chunk)
        elif count + len(chunk) > maxlen and count < maxlen:
            text = (chunk[:maxlen - count] if which is left else
                    chunk[-(maxlen - count):])
            which.append(text)
            count += len(text)
        if count >= maxlen and ellipsis is not None:
            left.append(ellipsis)
            ellipsis = None
        which = left if which is right else right
    text = EMPTY_TAGS.sub("", "".join(left + list(reversed(right))))
    return STRIP_PARA.sub(r"\1", text) if not allowPara else text


def spellNumber(n, *, limit=None):
    nums = ("zero", "one", "two", "three", "four", "five", "six",
            "seven", "eight", "nine", "ten", "eleven", "twelve",
            "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
            "eighteen", "nineteen")
    tens = (None, None, "twenty", "thirty", "forty", "fifty", "sixty",
            "seventy", "eighty", "ninety")
    if limit is not None and n >= limit:
        return "{:,}".format(n)
    if n < 0:
        return "minus " + spellNumber(abs(n))
    if n < 20:
        return nums[n]
    if n < 100: # and n >= 20
        s = tens[n // 10]
        if n % 10:
            s += " " + nums[n % 10]
        return s
    if n < 1000: # and n >= 100
        s = nums[n // 100] + " hundred"
        if n % 100:
            s += " " + spellNumber(n - (n // 100) * 100)
        return s
    if n < 1000000: # and n >= 1000
        s = spellNumber(n // 1000) + " thousand"
        if n % 1000:
            s += " " + spellNumber(n - (n // 1000) * 1000)
        return s
    if n < 1000000000: # and n >= 1000000
        s = spellNumber(n // 1000000) + " million"
        if n % 1000000:
            s += " " + spellNumber(n - (n // 1000000) * 1000000)
        return s
    if n < 1000000000000: # and n >= 1000000000
        s = spellNumber(n // 1000000000) + " billion"
        if n % 1000000000:
            s += " " + spellNumber(n - (n // 1000000000) * 1000000000)
        return s
    if n < 1000000000000000: # and n >= 1000000000
        s = spellNumber(n // 1000000000000) + " trillion"
        if n % 1000000000000:
            s += " " + spellNumber(n - (n // 1000000000000) * 1000000000000)
        return s
    return "{:,}".format(n)


Rules = collections.namedtuple("Rules", "name function tip abbrev")


def registerRules(collection, function, reorder=False):
    tip = inspect.getdoc(function)
    match = NAME_ABBREV_RX.search(tip)
    name = match.group("name")
    abbrev = match.group("abbrev") or ""
    key = function.__name__
    rules = Rules(name, function, tip, abbrev)
    if reorder: # Reorder the rules each time (by function name)
        items = [(key, rules)]
        while collection:
            items.append(collection.popitem())
        for item in sorted(items):
            key, value = item
            collection[key] = value
    else:
        collection[key] = rules
    return function


def initials(name):
    if not name:
        return ""
    return "".join(word[0].upper() for word in name.split())


def incrementedFilename(filename):
    path = os.path.dirname(filename)
    barename = STRIP_INC_RX.sub("", os.path.basename(filename))
    n = 1
    while True:
        name = os.path.join(path, "{} ({}){}".format(barename, n,
                                                     EXTENSION))
        if not os.path.exists(name):
            return name
        n += 1


def patchFont(match, stdFontFamily, stdFontSize, altFontFamily,
              altFontSize, monoFontFamily, monoFontSize):
    size = int(match.group("size1") or match.group("size2"))
    family = (match.group("family1") or match.group("family2")
              ).strip(" \"'")
    if MONO_FONT_RX.search(family) is not None:
        size = monoFontSize
        family = monoFontFamily
    elif family.casefold() == altFontFamily.casefold():
        size = altFontSize
        family = altFontFamily
    else: # If the regex matches and it isn't mono or alt, must be std.
        size = stdFontSize
        family = stdFontFamily
    return ("""<span style="font-size: {}pt; font-family: '{}';">"""
            .format(sanePointSize(size), family))


# TODO Replace with math.isclose() when 3.5 is deployed
def isclose(a, b):
    """Returns True if a and b are equal to the limits of the machine's
    accuracy

    >>> isclose(.1, .1), isclose(.000000000001, .000000000001)
    (True, True)
    >>> isclose(.00000000000101, .00000000000101)
    True
    >>> isclose(.0000000000000101, .0000000000000102)
    False
    """
    return math.fabs(a - b) <= (sys.float_info.epsilon *
                                min(math.fabs(a), math.fabs(b)))


def get_path(filename=None):
    if getattr(sys, "frozen", False): # if we're frozen
        path = os.path.dirname(sys.executable)
    else:
        path = os.path.join(os.path.dirname(__file__), "..")
    path = os.path.abspath(path)
    return path if filename is None else os.path.join(path, filename)


def replace_extension(filename, extension):
    return str(pathlib.Path(filename).with_suffix(extension))


def clamp(minimum, value, maximum):
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def swapAcronym(text):
    plainText = htmlToPlainText(text)
    match = ACRONYM_SWAP_RX.match(plainText)
    if match is not None:
        left = match.group(1)
        right = match.group(2)
        if left and right:
            left = left.strip()
            right = right.strip()
            if left and right:
                L = "«1l»"
                text = HtmlReplacer.sub(left, L, text)
                text = HtmlReplacer.sub(right, left, text)
                return HtmlReplacer.sub(L, right.strip("()").strip(), text)
    return text


def remove_file(filename):
    """Removes the given filename if it exists and returns True, or
    harmlessly does nothing if the file doesn't exist and returns False.
    Otherwise raises some kind of OSError, so safe to ignore the return
    value.
    """
    try:
        os.remove(filename)
        return True
    except FileNotFoundError:
        return False # All other exceptions are passed to the caller


uopen = functools.partial(open, encoding=UTF8)


class MonitorFile:

    def __init__(self, filename):
        self.filename = os.path.abspath(filename)
        try:
            self.size = os.path.getsize(self.filename)
            self.mtime = os.path.getmtime(self.filename)
        except OSError:
            self.size = self.mtime = -1 # New file


    @property
    def changed(self):
        return (self.size != os.path.getsize(self.filename) or
                self.mtime != os.path.getmtime(self.filename))


class CopyInfo:

    def __init__(self, eid, peid, copyxrefs=False, copygroups=False,
                 copysubentries=False, link=False, withsee=False,
                 description="copy"):
        self.eid = eid
        self.peid = peid
        self.copyxrefs = copyxrefs
        self.copygroups = copygroups
        self.copysubentries = copysubentries
        self.link = link
        self.withsee = withsee
        self.description = description


    def sanitize(self):
        if self.withsee:
            self.copyxrefs = self.copygroups = self.copysubentries = False
            self.link = False
        if self.link:
            self.copygroups = True


    def __repr__(self):
        return ("{}(eid={!r},peid={!r},copyxrefs={!r},copygroups={!r},"
                "copysubentries={!r},link={!r},withsee={!r},"
                "description={!r})".format(
                    self.__class__.__name__, self.eid, self.peid,
                    self.copyxrefs, self.copygroups, self.copysubentries,
                    self.link, self.withsee, self.description))
