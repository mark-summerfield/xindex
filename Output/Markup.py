#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import collections
import codecs
import datetime
import html.parser
import io
import re

from PySide.QtCore import QSettings
from PySide.QtGui import QApplication

import Lib
from Config import Gconf, Gopt
from Const import (
    EN_DASH, FileKind, IndentKind, StyleKind, UTF8, VISUAL_SPACE)
from . import Iter
from ._Markup import Markup, MarkupForExtension, user_markup # noqa


NON_DIGITS_RX = re.compile(r"\D+")
RTF_HIDDEN_RX = re.compile(r"\\v (?:main|sub[1-9])\\v0") # \\ for literal \
RTF_INDENT_RX = re.compile(r"\\fi-1000\\li(?P<level>\d+)")
HTML_HIDDEN_RX = re.compile(r"<!-- (?:main|sub[1-9]) -->")


Font = collections.namedtuple("Font", "fnum family size bold italic")


def outputEntries(model, markup, config, prefix, reportProgress):
    bom = ""
    if markup.Encoding == UTF8 and markup.kind is FileKind.TXT:
        bom = codecs.BOM_UTF8.decode(markup.Encoding)
    indent = indentForExtension(markup, config)
    file = io.StringIO()
    _outputEntries(file, bom, indent, model, markup, config, prefix,
                   reportProgress)
    text = file.getvalue()
    if config.Style is not StyleKind.INDENTED:
        if markup.kind is FileKind.TXT:
            regex = runInForIndentedRegex(markup, config.Style, indent)
        else:
            regex = runInForStyledRegex(markup, config, indent)
        text = regex.sub(config.RunInSeparator, text)
        if markup.kind is FileKind.RTF:
            text = RTF_HIDDEN_RX.sub("", text)
        elif markup.kind in {FileKind.HTML, FileKind.PDF, FileKind.PRINT}:
            text = HTML_HIDDEN_RX.sub("", text)
    elif markup.kind is FileKind.RTF:
        text = maybeFixRtfIndent(text)
    if markup.kind in {FileKind.DOCX, FileKind.PDF, FileKind.PRINT}:
        return text
    else:
        with open(config.Filename, "wt", encoding=markup.Encoding) as file:
            file.write(text) # implicitly returns None


def _outputEntries(file, bom, indent, model, markup, config, prefix,
                   reportProgress):
    total = len(model)
    percents = set()
    font = sectionFont(config)
    for i, item in enumerate(Iter.outputEntries(model, config)):
        percent = int(min(100, i * 100 // total)) if total else 100
        if percent not in percents: # report every 1% done
            reportProgress("{} {}%".format(prefix, percent))
            percents.add(percent)
        # Ordered from most to least frequently occurring
        if isinstance(item, Iter.Line): # Start/End Entry
            if item.line:
                start, end = startAndEndForIndent(indent, item, markup,
                                                  config)
                file.write(start)
                file.write(markedUpFromHtml(item.line, markup, config))
                file.write(end)
        elif isinstance(item, Iter.Section): # Start/End Section
            writeSection(file, item.line, font, markup, config)
        elif isinstance(item, Iter.Start): # Start Document
            writeDocumentStart(file, bom, item, font, markup, config)
        elif isinstance(item, Iter.End): # End Document
            file.write(markup.DocumentEnd.format(nl="\n"))


def runInForIndentedRegex(markup, style, indent):
    if style is StyleKind.RUN_IN_FROM_MAIN:
        pattern = (markup.MainEnd.format(nl="\n") +
                   markup.Sub1Start.format(indent=indent))
    elif style is StyleKind.RUN_IN_FROM_SUBENTRY1:
        pattern = (markup.Sub1End.format(nl="\n") +
                   markup.Sub2Start.format(indent=2 * indent))
    elif style is StyleKind.RUN_IN_FROM_SUBENTRY2:
        pattern = (markup.Sub2End.format(nl="\n") +
                   markup.Sub3Start.format(indent=3 * indent))
    elif style is StyleKind.RUN_IN_FROM_SUBENTRY3:
        pattern = (markup.Sub3End.format(nl="\n") +
                   markup.Sub4Start.format(indent=4 * indent))
    elif style is StyleKind.RUN_IN_FROM_SUBENTRY4:
        pattern = (markup.Sub4End.format(nl="\n") +
                   markup.Sub5Start.format(indent=5 * indent))
    elif style is StyleKind.RUN_IN_FROM_SUBENTRY5:
        pattern = (markup.Sub5End.format(nl="\n") +
                   markup.Sub6Start.format(indent=6 * indent))
    return re.compile(r"{}(?!{})".format(re.escape(pattern),
                      re.escape(indent)), re.MULTILINE)


def runInForStyledRegex(markup, config, indent):
    size = "XxXxX"
    family = config.StdFont
    style = config.Style
    if style is StyleKind.RUN_IN_FROM_MAIN:
        first = markup.MainEnd.format(nl="\n")
        second = markup.Sub1Start.format(size=size, family=family)
        third = markup.Sub1End.format(nl="\n")
    elif style is StyleKind.RUN_IN_FROM_SUBENTRY1:
        first = markup.Sub1End.format(nl="\n")
        second = markup.Sub2Start.format(size=size, family=family)
        third = markup.Sub2End.format(nl="\n")
    elif style is StyleKind.RUN_IN_FROM_SUBENTRY2:
        first = markup.Sub2End.format(nl="\n")
        second = markup.Sub3Start.format(size=size, family=family)
        third = markup.Sub3End.format(nl="\n")
    elif style is StyleKind.RUN_IN_FROM_SUBENTRY3:
        first = markup.Sub3End.format(nl="\n")
        second = markup.Sub4Start.format(size=size, family=family)
        third = markup.Sub4End.format(nl="\n")
    elif style is StyleKind.RUN_IN_FROM_SUBENTRY4:
        first = markup.Sub4End.format(nl="\n")
        second = markup.Sub5Start.format(size=size, family=family)
        third = markup.Sub5End.format(nl="\n")
    elif style is StyleKind.RUN_IN_FROM_SUBENTRY5:
        first = markup.Sub5End.format(nl="\n")
        second = markup.Sub6Start.format(size=size, family=family)
        third = markup.Sub6End.format(nl="\n")
    first = re.escape(first.rstrip("\n"))
    second = re.escape(second).replace(size, r"\d+")
    third = re.escape(third.rstrip("\n"))
    pattern1 = first + r"\s*" + second
    pattern2 = third + r"\s*" + second
    pattern = "(?:{}|{})".format(pattern1, pattern2)
    return re.compile(pattern, re.MULTILINE)


def maybeFixRtfIndent(text):
    settings = QSettings()
    indent = IndentKind(int(settings.value(Gopt.Key.IndentRTF,
                                           Gopt.Default.IndentRTF)))
    if indent is not IndentKind.TAB:
        spaces = " " * int(indent)

        def fixIndent(match):
            indent = int(match.group("level")) - 1000
            if not indent:
                return ""
            return spaces * (indent // 400)

        text = RTF_INDENT_RX.sub(fixIndent, text)
    return text


def indentForExtension(markup, config):
    indent = getattr(markup, "Indent", None)
    if indent is not None:
        if markup.kind in {FileKind.RTF, FileKind.DOCX}:
            return markup.Indent
        if config.Indent is IndentKind.TAB:
            return markup.Tab
        return indent * int(config.Indent)
    else:
        return ("\t" if config.Indent is IndentKind.TAB else
                " " * int(config.Indent))


def startAndEndForIndent(indent, item, markup, config):
    if item.indent == 0:
        start = markup.MainStart
        end = markup.MainEnd
    else:
        start = getattr(markup, "Sub{}Start".format(item.indent))
        end = getattr(markup, "Sub{}End".format(item.indent))
    if markup.kind in {FileKind.RTF, FileKind.DOCX}:
        size = config.StdFontSize * 2
    else:
        size = ""
    start = start.format(indent=indent * item.indent, nl="\n", size=size,
                         family=config.StdFont)
    end = end.format(nl="\n")
    if config.Style is StyleKind.INDENTED:
        if markup.kind is FileKind.RTF:
            start = RTF_HIDDEN_RX.sub("", start)
            end = RTF_HIDDEN_RX.sub("", end)
        elif markup.kind in {FileKind.HTML, FileKind.PDF, FileKind.PRINT}:
            start = HTML_HIDDEN_RX.sub("", start)
            end = HTML_HIDDEN_RX.sub("", end)
    return start, end


def writeSection(file, line, font, markup, config):
    for _ in range(config.SectionPreLines):
        file.write(markup.Newline) # blank line
    if config.SectionTitles:
        file.write(markup.SectionStart.format(
            nl="\n", family=font.family, fnum=font.fnum,
            size=font.size * 2))
        if markup.kind is not FileKind.HTML:
            if len(line) == 1: # 'A'...'Z'
                if font.italic:
                    line = "<i>{}</i>".format(line)
                if font.bold:
                    line = "<b>{}</b>".format(line)
                line = """<span style="font-size: {}pt; \
font-family: '{}';">{}</span>""".format(font.size, font.family, line)
        file.write(markedUpFromHtml(line, markup, config, keepFonts=True))
        file.write(markup.SectionEnd.format(nl="\n"))
    for _ in range(config.SectionPostLines):
        file.write(markup.Newline) # blank line


def sectionFont(config):
    fnum = 0
    family = config.StdFont
    size = config.StdFontSize
    text = config.SectionSpecialTitle or Gconf.Default.SectionSpecialTitle
    bold = "<b>" in text
    italic = "<i>" in text
    match = Lib.PATCH_FONT_RX.search(text)
    if match is not None:
        size = int(match.group("size1") or match.group("size2"))
        family = (match.group("family1") or match.group("family2")
                  ).strip(" \"'")
        fnum = 0
        if family.casefold() == config.AltFont.casefold():
            fnum = 1
        elif family.casefold() == config.MonoFont.casefold():
            fnum = 2
    return Font(fnum, family, size, bold, italic)


def writeDocumentStart(file, bom, item, font, markup, config):
    title = markedUpFromHtml(item.title, markup, config, keepFonts=True)
    if markup.kind is FileKind.DOCX:
        text = markup.DocumentStart.format(title=title)
    else:
        text = markup.DocumentStart.format(
            version=QApplication.applicationVersion(),
            creator=markup.escape(config.Creator),
            date=datetime.date.today(), bom=bom,
            plaintitle=Lib.htmlToPlainText(item.title),
            title=title, encoding=markup.Encoding, nl="\n",
            stdfont=config.StdFont, stdfontsize=config.StdFontSize,
            altfont=config.AltFont, monofont=config.MonoFont,
            sectfont=font.family, sectfontsize=font.size)
    file.write(text)
    if item.note:
        note = markedUpFromHtml(item.note, markup, config, keepFonts=True)
        file.write(markup.Note.format(
            note=note, nl="\n", family=config.StdFont,
            size=config.StdFontSize * 2))


def markedUpFromHtml(text, markup, config, *, keepFonts=False):
    if not keepFonts:
        patcher = lambda match: Lib.patchFont(
            match, config.StdFont, config.StdFontSize, config.AltFont,
            config.AltFontSize, config.MonoFont, config.MonoFontSize)
        text = Lib.PATCH_FONT_RX.sub(patcher, text)
    parser = Parser(markup, config)
    parser.feed("<p>{}</p>".format(text))
    return parser.text


class Parser(html.parser.HTMLParser):

    def __init__(self, markup, config):
        super().__init__(convert_charrefs=True)
        self.markup = markup
        self.config = config
        self.pending = []
        self.texts = []
        self.altFont = config.AltFont.casefold()
        self.monoFont = config.MonoFont.casefold()


    @property
    def text(self):
        if self.pending:
            self.texts += reversed(self.pending)
        return "".join(self.texts)


    def handle_starttag(self, tag, attrs):
        if tag == "b":
            self.texts.append(self.markup.BoldStart)
        elif tag == "i":
            self.texts.append(self.markup.ItalicStart)
        elif tag == "span":
            for name, value in attrs:
                if name == "style":
                    family = ""
                    size = ""
                    for match in Lib.KEY_VALUE_RX.finditer(value):
                        key = match.group("key")
                        if key == "font-family":
                            family = match.group("value").casefold().strip(
                                "'\" ")
                        elif key == "font-size":
                            size = match.group("value").strip("'\" ")
                            if self.markup.kind in {FileKind.RTF,
                                                    FileKind.DOCX}:
                                size = Lib.sanePointSize(
                                    int(NON_DIGITS_RX.sub("", size)) * 2)
                    if family:
                        self._addFontStartAndEnd(family, size)
        elif tag == "sub":
            self.texts.append(self.markup.SubscriptStart)
        elif tag == "sup":
            self.texts.append(self.markup.SuperscriptStart)
        elif tag == "u":
            self.texts.append(self.markup.UnderlineStart)


    def _addFontStartAndEnd(self, family, size):
        if family == self.altFont:
            start = self.markup.AltFontStart.format(family=family,
                                                    size=size)
            end = self.markup.AltFontEnd
            if self.markup.kind is FileKind.RTF:
                end = end.format(size=self.config.StdFontSize * 2)
        elif family == self.monoFont:
            if self.config.MonoFontAsStrikeout:
                start = self.markup.StrikeoutStart
                end = self.markup.StrikeoutEnd
            else:
                start = self.markup.MonoFontStart.format(family=family,
                                                         size=size)
                end = self.markup.MonoFontEnd
                if self.markup.kind is FileKind.RTF:
                    end = end.format(size=self.config.StdFontSize * 2)
        else:
            start = self.markup.StdFontStart.format(family=family,
                                                    size=size)
            end = self.markup.StdFontEnd
        self.texts.append(start)
        self.pending.append(end)


    def handle_endtag(self, tag):
        if tag == "b":
            self.texts.append(self.markup.BoldEnd)
        elif tag == "i":
            self.texts.append(self.markup.ItalicEnd)
        elif tag == "span":
            if self.pending:
                self.texts.append(self.pending.pop())
        elif tag == "sub":
            self.texts.append(self.markup.SubscriptEnd)
        elif tag == "sup":
            self.texts.append(self.markup.SuperscriptEnd)
        elif tag == "u":
            self.texts.append(self.markup.UnderlineEnd)


    def handle_data(self, data):
        if EN_DASH != self.markup.RangeSeparator:
            text = data.replace(EN_DASH, self.markup.RangeSeparator)
        text = data.replace(VISUAL_SPACE, " ")
        escape = self.markup.escape
        if escape is not None:
            text = escape(text)
        self.texts.append(text)
