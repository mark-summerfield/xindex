#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

# Kinds.py

import collections
import logging
import re
import sys

from .Kinds import (ModeKind, CountKind, CommandKind, LanguageKind, # noqa
                    FilterKind, IndentKind, XrefKind,
                    SeeAlsoPositionKind, StyleKind, XRefToSubentryKind,
                    FileKind, PaperSizeKind, EntryDataKind,
                    SearchFieldKind, PartKind, CandidateKind,
                    PagesOrderKind)


WIN = sys.platform.startswith("win")

ROOT = 0
UNLIMITED = -1
SAY_TIMEOUT = 5000
MAX_DYNAMIC_ACTIONS = 26
MIN_FONT_SIZE = 6
MAX_FONT_SIZE = 72
MAX_RECENT = 10
DEFAULT_ELIDE_LEN = 50
DEFAULT_PAD_DIGITS = 4
TOOLTIP_IMAGE_SIZE = 18
VISUAL_SPACE = "\u25CF"     # ●
EN_DASH = "\u2013"          # –
MAIN_INDICATOR = "\u25B6"   # ▶
SUB_INDICATOR = "\u25B7"    # ▷
XREF_INDICATOR = "\u261E"   # ☞
UUID = "UUID"
BLANK_SPACE_HTML = ("""
<p>(Each blank space is shown as a <font color=cyan>{}</font>.)</p>"""
                    .format(VISUAL_SPACE))
STRIP_AT_RX = re.compile(r"@\d+(\.\d+)*")
DELETE_IGNORED_FIRSTS_TEMPLATE = r"(?i)^(?:{0})\b(?:\s+(?:{0})\b)*\s+(?=\S)"
COUNT_LABEL_TEMPLATE = """\
<p><font color=steelblue>Total {:,} &bull;</font>
<font color=steelblue>Main {:,} &bull;</font>
<font color=steelblue>New {:,} &bull;</font>
<font color=steelblue>Filtered {:,}</font></p>"""
LABEL_TEMPLATE = "<font color=steelblue>{}</font>"
CANCEL_ADD = "Cancel Add <font color=darkgreen>(Ctrl+0)</font>"

UTF8 = "UTF-8"
IS64BIT = sys.maxsize > 2 ** 32

EXTENSION = ".xix"
IMPORT_EXTENSIONS = collections.OrderedDict((
    (".ximl", "XindeX XML Interchange Format"),
    (".ixml", "Index Data Exchange Format"),
    ))
EXPORT_EXTENSIONS = collections.OrderedDict((
    (".rtf", "Rich Text Format"),
    (".docx", "Word Format (OOXML)"),
    (".txt", "Plain Text (no formatting)"),
    (".pdf", "Portable Document Format"),
    (".html", "HyperText Markup Language"),
    (".ximl", "XindeX XML Format"),
    (".ixml", "Index Data Exchange Format"),
    (".*", "User Defined Markup"),
    ))

MARKUP_NAMES = (
    "escapefunction",
    "DocumentStart", "DocumentEnd",
    "Note",
    "SectionStart", "SectionEnd",
    "MainStart", "MainEnd",
    "Sub1Start", "Sub1End",
    "Sub2Start", "Sub2End",
    "Sub3Start", "Sub3End",
    "Sub4Start", "Sub4End",
    "Sub5Start", "Sub5End",
    "Sub6Start", "Sub6End",
    "Sub7Start", "Sub7End",
    "Sub8Start", "Sub8End",
    "Sub9Start", "Sub9End",
    "Encoding",
    "RangeSeparator",
    "Tab",
    "Newline",
    "AltFontStart", "AltFontEnd",
    "MonoFontStart", "MonoFontEnd",
    "StdFontStart", "StdFontEnd",
    "BoldStart", "BoldEnd",
    "ItalicStart", "ItalicEnd",
    "SubscriptEnd", "SubscriptStart",
    "SuperscriptStart", "SuperscriptEnd",
    "UnderlineStart", "UnderlineEnd",
    "StrikeoutStart", "StrikeoutEnd")


RenumberOptions = collections.namedtuple(
    "RenumberOptions", ("romanfrom", "romanto", "romanchange",
                        "decimalfrom", "decimalto", "decimalchange",))

Query = collections.namedtuple("Query", "sql params")


def say(message, timeout=0):
    logging.info(message)


def error(message):
    logging.warning(message)
