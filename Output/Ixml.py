#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import datetime
import html

from PySide.QtGui import QApplication

import Lib
import Pages
import Saf
from Const import EntryDataKind, STRIP_AT_RX, XrefKind
from . import Markup


DOCUMENT_START = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE indexdata [
<!ELEMENT indexdata (source, fonts, records) >
<!ELEMENT source EMPTY >
<!ATTLIST source
    creator CDATA #REQUIRED
    version CDATA #REQUIRED
    time CDATA #REQUIRED >
<!-- time value is UTC in this format: 2011-03-03T03:41:14 -->
<!ELEMENT fonts (font+) >
<!ELEMENT font (fname, aname) >
<!ATTLIST font
    id CDATA #REQUIRED >
<!ELEMENT fname (#PCDATA) >
<!ELEMENT aname (#PCDATA) >
<!ELEMENT records (record)* >
<!ATTLIST records
    type CDATA #IMPLIED >
<!ELEMENT record (field+) >
<!ATTLIST record
    time CDATA #REQUIRED
    user CDATA #IMPLIED
    label CDATA #IMPLIED
    deleted (y | n) #IMPLIED
    type CDATA #IMPLIED >
<!-- time value is UTC in this format: 2008-08-02T16:27:44 -->
<!-- label value is integer -->
<!-- type value can be "generated" (automatically generated) -->
<!ELEMENT field (#PCDATA | text | esc | literal | hide | sort)* >
<!ATTLIST field
    class CDATA #IMPLIED >
<!-- class value can be "locator" -->
<!ELEMENT text EMPTY >
<!ATTLIST text
    font CDATA #IMPLIED
    color CDATA #IMPLIED
    smallcaps ( y | n ) #IMPLIED
    style ( b | i | u | bi | bu | iu | biu ) #IMPLIED
    offset ( u | d ) #IMPLIED
>
<!-- font and color attribute values are integers in range 0-31 -->
<!ELEMENT literal EMPTY >
<!-- literal: forces the succeeding character to be used in sort -->
<!ELEMENT hide (#PCDATA) >
<!-- hide: contains text to be ignored in sorting -->
<!ELEMENT sort (#PCDATA) >
<!-- sort: contains text to be used in sorting but not displayed -->
]>
<indexdata>
<source creator="XindeX" version="{version}" time="{utc}"/>
<fonts>
<font id="0">
    <fname>{fname0}</fname>
    <aname>{fname0}</aname>
</font>
<font id="1">
    <fname>{fname1}</fname>
    <aname>{fname1}</aname>
</font>
</fonts>
<records>
"""

DOCUMENT_END = "</records>\n</indexdata>\n"

RECORD_START = """<record time="{utc}">\n"""
RECORD_END = "</record>\n"
TERM = "    <field>{term}</field>\n"
TERMX = "    <field><sort>{sortas}</sort>{term}</field>\n"
PAGE = """    <field class="locator">{page}</field>\n"""


def outputEntries(model, config, prefix, reportProgress):
    markup = _markup(config)
    total = len(model)
    percents = set()
    utc = datetime.datetime.now().isoformat()[:19]
    with Lib.uopen(config.Filename, "wt") as file:
        file.write(DOCUMENT_START.format(
            version=QApplication.applicationVersion(), utc=utc,
            fname0=config.AltFont, fname1=config.MonoFont))
        fields = []
        indent = 0
        for i, entry in enumerate(list(model.entries(
                entryData=EntryDataKind.ALL_DATA_AND_DATES))):
            percent = int(min(100, i * 100 // total))
            if percent not in percents: # report every 1% done
                reportProgress("{} {}%".format(prefix, percent))
                percents.add(percent)
            term = _term(entry, markup, config)
            if entry.indent == 0:
                fields = [term]
                indent = 0
            elif entry.indent > indent:
                fields.append(term)
                indent += 1
            else:
                while len(fields) > entry.indent:
                    fields.pop()
                indent = entry.indent
                fields.append(term)
            _writeEntry(file, fields, entry, model, markup, config)
        file.write(DOCUMENT_END)


def _term(entry, markup, config):
    term = Markup.markedUpFromHtml(entry.term, markup, config)
    if entry.saf != Saf.CUSTOM:
        return TERM.format(term=term)
    return TERMX.format(sortas=entry.sortas, term=term)


def _writeEntry(file, fields, entry, model, markup, config):
    locators = []
    if entry.pages:
        for page in Pages.toIndividualHtmlPages(STRIP_AT_RX.sub(
                                                "", entry.pages)):
            text = Markup.markedUpFromHtml(page, markup, config)
            locators.append(PAGE.format(page=text))
    _add_xrefs(locators, entry, model, markup, config)
    utc = entry.updated.replace(" ", "T")
    if not locators:
        file.write(RECORD_START.format(utc=utc))
        for field in fields:
            file.write(field)
        file.write(RECORD_END)
    else:
        for locator in locators:
            file.write(RECORD_START.format(utc=utc))
            for field in fields:
                file.write(field)
            file.write(locator)
            file.write(RECORD_END)


def _add_xrefs(locators, entry, model, markup, config):
    for xref in list(model.all_xrefs(entry.eid)):
        if xref.kind in {XrefKind.SEE_GENERIC, XrefKind.SEE_ALSO_GENERIC}:
            text = ("see " if xref.kind is XrefKind.SEE_GENERIC else
                    "see also ")
            text += Markup.markedUpFromHtml(xref.term, markup, config)
            locators.append(PAGE.format(page=text))
        else:
            text = "see " if xref.kind is XrefKind.SEE else "see also "
            text += Markup.markedUpFromHtml(model.term(xref.to_eid),
                                            markup, config)
            locators.append(PAGE.format(page=text))


def _markup(config):
    end = "<text/>"
    markup = Markup.Markup(Markup.FileKind.IXML)
    markup.escape = html.escape
    markup.AltFontStart = """<text font="0"/>"""
    markup.AltFontEnd = end
    markup.MonoFontStart = """<text font="1"/>"""
    markup.MonoFontEnd = end
    markup.StdFontStart = ""
    markup.StdFontEnd = ""
    markup.BoldStart = """<text style="b"/>"""
    markup.BoldEnd = end
    markup.ItalicStart = """<text style="i"/>"""
    markup.ItalicEnd = end
    markup.SubscriptStart = """<text offset="d"/>"""
    markup.SubscriptEnd = end
    markup.SuperscriptStart = """<text offset="u"/>"""
    markup.SuperscriptEnd = end
    markup.UnderlineStart = """<text style="u"/>"""
    markup.UnderlineEnd = end
    markup.StrikeoutStart = ""
    markup.StrikeoutEnd = ""
    markup.RangeSeparator = "-"
    return markup
