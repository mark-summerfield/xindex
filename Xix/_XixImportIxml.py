#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import datetime
import xml.etree.ElementTree as ET
import xml.parsers.expat

import Lib
import Pages
import Saf
import SortAs
import Sql
import Xix.Util
from Config import Gconf
from Const import error, ROOT, XrefKind


# Ignores <text> tag's color and smallcaps attributes.
# Ignores <literal> tags.
# Doesn't handle xrefs to subentries.


def importIndex(cursor, inFilename):
    parser = parseIxml(inFilename)
    if parser is None:
        return False
    setFonts(cursor, parser.fonts)
    for entry in parser.entries():
        addEntry(cursor, entry)
    for xref in parser.xrefs:
        addXref(cursor, xref)
    return True


def setFonts(cursor, fonts):
    for font, key in zip(fonts, (Gconf.Key.AltFont, Gconf.Key.MonoFont)):
        if font is not None:
            value = Xix.Util.to_basic_type(font)
            cursor.execute(Sql.UPDATE_CONFIG, dict(key=key, value=value))


def addEntry(cursor, entry):
    if not entry.sortas:
        sortas = SortAs.wordByWordCMS16(entry.term, entry.saf)
    else:
        sortas = Lib.htmlToPlainText(entry.sortas)
    pages = Pages.sortedPages(entry.pages, Pages.pageRangeCMS16)
    cursor.execute(Sql.REINSERT_ENTRY_WITH_DATES, dict(
        eid=entry.eid, saf=entry.saf, sortas=sortas, term=entry.term,
        pages=pages, notes=None, peid=entry.peid, created=entry.created,
        updated=entry.updated))


def addXref(cursor, xref):
    if xref.kind in {XrefKind.SEE_GENERIC, XrefKind.SEE_ALSO_GENERIC}:
        sql = Sql.INSERT_GENERIC_XREF
        d = dict(from_eid=xref.from_eid, term=xref.term, kind=xref.kind)
    else:
        if xref.from_eid == xref.to_eid:
            return # No cross-references to self
        sql = Sql.INSERT_XREF
        d = dict(from_eid=xref.from_eid, to_eid=xref.to_eid, kind=xref.kind)
    cursor.execute(sql, d)


class Entry:

    def __init__(self, peid, eid, term, saf=Saf.AUTO, sortas="", pages="",
                 see="", seealso=""):
        self.peid = peid
        self.eid = eid
        self.term = term
        self.saf = saf
        self.sortas = sortas
        self.pages = pages
        self.see = see
        self.seealso = seealso
        now = str(datetime.datetime.now())[:19]
        self.created = now
        self.updated = now


    def __lt__(self, other):
        if self.peid != other.peid:
            return self.peid < other.peid
        return self.eid < other.eid


    def __str__(self): # DEBUG
        sortas = " s«{}»".format(self.sortas) if self.sortas else ""
        return "{} → {} T«{}» P«{}»{}".format(self.peid, self.eid,
                                              self.term, self.pages, sortas)


by_from_eid = lambda self, other: self.from_eid < other.from_eid


class GenericSee:

    def __init__(self, from_eid, term):
        self.from_eid = from_eid
        self.term = term
        self.kind = XrefKind.SEE_GENERIC


    __lt__ = by_from_eid


    def __str__(self):
        return "from {} see {}".format(self.from_eid, self.term)


class GenericSeeAlso(GenericSee):


    def __init__(self, from_eid, term):
        super().__init__(from_eid, term)
        self.kind = XrefKind.SEE_ALSO_GENERIC


    def __str__(self):
        return "from {} see also {}".format(self.from_eid, self.term)


class See:

    def __init__(self, from_eid, to_eid):
        self.from_eid = from_eid
        self.to_eid = to_eid
        self.kind = XrefKind.SEE


    __lt__ = by_from_eid


    def __str__(self):
        return "from {} see {}".format(self.from_eid, self.to_eid)


class SeeAlso(See):

    def __init__(self, from_eid, to_eid):
        super().__init__(from_eid, to_eid)
        self.kind = XrefKind.SEE_ALSO


    def __str__(self):
        return "from {} see also {}".format(self.from_eid, self.to_eid)


class Record:

    def __init__(self):
        self.fields = [] # Fields or LocatorFields
        self.time = None


class Field:

    def __init__(self):
        self.text = ""
        self.sortas = ""


class LocatorField:

    def __init__(self):
        self.text = ""


class IxmlParser:

    Eid = 0

    def __init__(self):
        self.entryForTerm = {} # key = tuple of terms, value = entry
        self.eidForTerm = {}
        self.fontForId = {}
        self.xrefs = None
        self.clearRecord()


    @property
    def fonts(self):
        if self.fontForId:
            return [i[1] for i in sorted(self.fontForId.items())][:3]
        return []


    def clearField(self):
        self.fontId = None
        self.inFont = False
        self.inTextTag = False
        self.inNoSort = False
        self.inSort = False
        self.endTextTag = ""
        self.texts = []
        self.sortas = []


    def clearRecord(self):
        self.clearField()
        self.record = None


    def start(self, tag, attr):
        if tag == "font":
            self.inFont = True
        elif tag in {"fname", "aname"}:
            self.fontId = attr.get("id", 1)
        elif tag == "record":
            self.record = Record()
            self.record.time = (attr.get("time") or
                                str(datetime.datetime.now())[:19])
        elif tag == "field":
            self.startField(attr)
        elif tag == "text":
            self.startText(attr)
        elif tag == "hide":
            self.inNoSort = True
        elif tag == "sort":
            self.inSort = True


    def end(self, tag):
        if tag == "font":
            self.fontId = None
            self.inFont = False
        elif tag in {"fname", "aname"}:
            self.fontId = None
        elif tag == "record":
            self.endRecord()
        elif tag == "field":
            self.endField()
        elif tag == "text":
            self.endText()
        elif tag == "hide":
            self.inNoSort = False
        elif tag == "sort":
            self.inSort = False


    def endRecord(self):
        peid = ROOT
        entry = None
        terms = []
        for field in self.record.fields:
            if isinstance(field, Field):
                term = " ".join(field.text.split())
                terms.append(term)
                entry = self.entryForTerm.get(tuple(terms))
                if entry is None:
                    IxmlParser.Eid += 1
                    sortas = " ".join(field.sortas.split())
                    entry = Entry(peid, IxmlParser.Eid, term, sortas)
                    entry.created = entry.updated = self.record.time
                    self.entryForTerm[tuple(terms)] = entry
                    self.eidForTerm[tuple(terms)] = entry.eid
                peid = entry.eid
            elif entry is not None and isinstance(field, LocatorField):
                locator = " ".join(field.text.split())
                if locator:
                    if locator.casefold().startswith("see also"):
                        if entry.seealso:
                            entry.seealso += "; "
                        entry.seealso += locator[8:].lstrip()
                    elif locator.casefold().startswith("see"):
                        if entry.see:
                            entry.see += "; "
                        entry.see += locator[3:].lstrip()
                    else:
                        if entry.pages:
                            entry.pages += ", "
                        entry.pages += locator
        self.clearRecord()


    def startField(self, attr):
        field = (LocatorField() if attr.get("class") == "locator" else
                 Field())
        self.record.fields.append(field)


    def endField(self):
        field = self.record.fields[-1]
        field.text = "".join(self.texts)
        if hasattr(field, "sortas") and self.sortas:
            field.sortas = "".join(self.sortas)
        self.clearField()


    def startText(self, attr):
        startTextTag = ""
        style = attr.get("style", None)
        if style == "b":
            startTextTag, self.endTextTag = "<b>", "</b>"
        elif style == "i":
            startTextTag, self.endTextTag = "<i>", "</i>"
        elif style == "u":
            startTextTag, self.endTextTag = "<u>", "</u>"
        elif style == "bi":
            startTextTag, self.endTextTag = "<b><i>", "</i></b>"
        elif style == "bu":
            startTextTag, self.endTextTag = "<b><u>", "</u></b>"
        elif style == "iu":
            startTextTag, self.endTextTag = "<i><u>", "</u></i>"
        elif style == "biu":
            startTextTag, self.endTextTag = "<b><i><u>", "</u></i></b>"
        offset = attr.get("offset", None)
        if offset == "u":
            startTextTag += "<sup>"
            self.endTextTag += "</sup>"
        elif offset == "d":
            startTextTag += "<sub>"
            self.endTextTag += "</sub>"
        fontId = attr.get("font", None)
        font = self.fontForId.get(fontId)
        if font is not None:
            startTextTag += """<span style="font-size: 13pt; \
font-family: '{}';">""".format(font)
            self.endTextTag += "</span>"
        if startTextTag:
            self.texts.append(startTextTag)
            self.inTextTag = True


    def endText(self):
        if self.inTextTag:
            self.inTextTag = False
        else:
            if self.endTextTag:
                self.texts.append(self.endTextTag)
                self.endTextTag = ""


    def data(self, data):
        if self.fontId is not None:
            if self.fontId not in self.fontForId:
                self.fontForId[self.fontId] = data
        if self.record is not None and self.record.fields:
            field = self.record.fields[-1]
            if isinstance(field, LocatorField):
                self.texts.append(data)
            elif isinstance(field, Field):
                if self.inNoSort:
                    sortas = " ".join(self.texts)
                    self.sortas.append(Lib.htmlToPlainText(sortas))
                    self.texts.append(data)
                elif self.inSort:
                    sortas = " ".join(self.texts)
                    self.sortas += [Lib.htmlToPlainText(sortas), data]
                else:
                    if self.sortas:
                        self.sortas.append(Lib.htmlToPlainText(data))
                    self.texts.append(data)


    def entries(self):
        for entry in sorted(self.entryForTerm.values()):
            yield entry


    def finalize(self):
        self._populateXRefs()


    def _populateXRefs(self):
        self.xrefs = []
        for entry in self.entries():
            if entry.see:
                for see in entry.see.split(";"):
                    see = see.strip()
                    eid = self.eidForTerm.get((see,))
                    if eid is not None:
                        self.xrefs.append(See(entry.eid, eid))
                    else:
                        self.xrefs.append(GenericSee(entry.eid, see))
            if entry.seealso:
                for seealso in entry.seealso.split(";"):
                    seealso = seealso.strip()
                    eid = self.eidForTerm.get((seealso,))
                    if eid is not None:
                        self.xrefs.append(SeeAlso(entry.eid, eid))
                    else:
                        self.xrefs.append(GenericSeeAlso(entry.eid,
                                                         seealso))
        self.xrefs.sort()


def parseIxml(inFilename):
    parser = IxmlParser()
    xmlParser = ET.XMLParser(target=parser)
    try:
        with Lib.uopen(inFilename, "rt") as file:
            for line in file: # Memory-parsimonious reading
                xmlParser.feed(line)
        parser.finalize()
        return parser
    except (OSError, ET.ParseError, xml.parsers.expat.ExpatError) as err:
        error("Failed to read “{}”: {}".format(inFilename, err))
