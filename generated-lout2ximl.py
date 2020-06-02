#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

# WARNING This is very buggy!

import datetime
import html
import os
import pathlib
import re
import sys

import SortAs

DEBUG = 0


def main():
    if len(sys.argv) < 2 or not sys.argv[1].endswith(".lout"):
        raise SystemExit("usage: {} file.lout [file.ximl]".format(
                         os.path.basename(sys.argv[0])))
    loutfilename = sys.argv[1]
    ximlfilename = (sys.argv[2] if len(sys.argv) == 3 and
                    sys.argv[2].endswith(".ximl") else
                    pathlib.PurePath(loutfilename).with_suffix(".ximl"))
    entries = read_lout(loutfilename)
    resolve_xrefs(entries)
    repair(entries)
    write_ximl(ximlfilename, entries)


"""
@x main entry
@xs main entry; see ???
@xst main entry: see main entry [generic]
@xx subentry
@xxs subentry; see ???
@xxst subentry: see main entry [generic]
@xxx subsubentry
@xxxs subsubentry; see ???
@xxxst subsubentry: see main entry [generic]
"""


def read_lout(filename):
    entries = {} # key=bare term, value=Entry
    peids = [0]
    with open(filename, "rt", encoding="latin1", errors="ignore") as file:
        for line in file:
            line = line.rstrip()
            match = LINE_RX.match(line)
            if match is None:
                continue
            i = len(match.group("indent")) // 4
            entry = Entry(match.group("term"))
            if i == 0: # main entry
                peids = [0, entry.eid]
            else: # subentry
                entry.peid = peids[i]
                if i < len(peids):
                    peids.append(entry.eid)
            entry.term = lout_to_html(entry.term)
            if match.group("kind").endswith("xst"):
                entry.xrefs.append(GenericSeeXref("main entry"))
            pages = match.group("pages")
            if match.group("kind").endswith("s"):
                entry.xrefs.append(SeeXref(lout_to_html(pages)))
            else:
                entry.pages, xrefs = pages_and_xrefs(pages)
                entry.xrefs += xrefs
            entries[bare(entry.term)] = entry
    return entries


def bare(text):
    return html.unescape(re.sub(r"<.*?>", "", text)).casefold()


def pages_and_xrefs(pages):
    xrefs = []
    if pages.startswith("@I"):
        xrefs = [pages]
        pages = ""
    else:
        parts = pages.split(";")
        if len(parts) > 1:
            pages = ""
            for part in parts:
                part = part.strip(";").strip()
                if part.startswith("@I"):
                    xrefs.append(part)
                else:
                    pages += " " + part
    for i in range(len(xrefs)):
        xref = lout_to_html(re.sub(r"@I\{alias of\}|@I\{inherits\}",
                                   "@I{see also}", xrefs[i]))
        if xref.startswith("<i>see also</i>"):
            xref = SeeAlsoXref(xref[15:].strip())
        elif xref.startswith("<i>see</i>"):
            xref = SeeXref(xref[10:].strip())
        elif DEBUG:
            print("INVALID XREF", xref)
        xrefs[i] = xref
    return lout_to_html(pages), xrefs


def resolve_xrefs(entries):
    for entry in entries.values():
        for xref in entry.xrefs:
            if isinstance(xref, (SeeXref, SeeAlsoXref)):
                if xref.toeid is None:
                    term = bare(xref.term)
                    eid = entries.get(term)
                    if eid is not None:
                        xref.toeid = eid
                        if DEBUG:
                            print("FOUND XREF TO", term, eid)
                    else:
                        if DEBUG:
                            print("FAILED TO FIND XREF TO", term)


def repair(entries):
    eids = {0}
    peids = set()
    for entry in entries.values():
        eids.add(entry.eid)
        peids.add(entry.peid)
    missing = peids - eids
    if missing:
        for entry in entries.values():
            if entry.peid in missing:
                peid = entry.peid
                while True:
                    peid -= 1
                    if peid in eids or peid == 0:
                        entry.peid = peid
                        break


def write_ximl(filename, entries):
    now = str(datetime.datetime.now())[:19]
    with open(filename, "wt", encoding="utf-8") as file:
        file.write(HEADER)
        for entry in sorted(entries.values(),
                            key=lambda e: (e.eid, e.peid)):
            sortas = SortAs.wordByWordCMS16(entry.term)
            xrefs = ""
            file.write("""\
<entry eid="{eid}" peid="{peid}" created="{created}" updated="{updated}">
    <term>{term}</term>
    <sortas saf="A">{sortas}</sortas>
    <pages>{pages}</pages>{xrefs}
</entry>
""".format(eid=entry.eid, peid=entry.peid, created=now, updated=now,
           term=html.escape(entry.term).strip(),
           pages=html.escape(entry.pages).strip(),
           sortas=sortas, xrefs=xrefs)) # noqa
        file.write(FOOTER)


def lout_to_html(lout):
    text = re.sub(r'"([^"]+)"', r"\1", lout)
    text = html.escape(text)
    text = text.replace("---", "&mdash;")
    text = text.replace("--", "&ndash;")
    text = text.replace("{@Ptr{@Ptr}}", "**")
    text = text.replace("{@Ptr}", "*")
    text = re.sub(r"@F{(.*?)}",
                  r"""<span style="font-size: 11pt; font-family: """
                  r"""'Courier New';">\1</span>""", text)
    text = re.sub(r"@B{(.*?)}", r"<b>\1</b>", text)
    text = re.sub(r"@I{(.*?)}", r"<i>\1</i>", text)
    return text


LINE_RX = re.compile(
    r"^(?P<indent>\s*)"
    r"\{(?P<term>.+)\}(?P<kind>@x[a-z]*)"
    r"\{(?P<pages>.*)\}@nl")


class Entry:

    Eid = 1

    def __init__(self, term, pages="", peid=0):
        self.eid = Entry.Eid
        Entry.Eid += 1
        self.peid = peid
        self.term = term
        self.pages = pages
        self.xrefs = []


    def __str__(self):
        return "EID={} PEID={} TERM={!r} PAGES={!r}".format(
            self.eid, self.peid, self.term, self.pages)


class GenericSeeXref:

    def __init__(self, term):
        self.term = term


    def __str__(self):
        return "GX={!r}".format(self.term)


class SeeXref(GenericSeeXref):

    def __init__(self, term):
        super().__init__(term)
        self.toeid = None

    def __str__(self):
        return "SX={}({!r})".format(self.toeid, self.term)


class SeeAlsoXref(SeeXref):

    def __str__(self):
        return "AX={}({!r})".format(self.toeid, self.term)


HEADER = """\
<?xml version="1.0" encoding="UTF-8"?>
<XindeX version="100">
<entries>
"""

FOOTER = """\
</entries>
<spelling>
    <spell word="(datetime.datetime"/>
    <spell word="Bresenham"/>
    <spell word="datetime"/>
    <spell word="docstring"/>
    <spell word="tkinter"/>
    <spell word="tuple"/>
</spelling>
<ignored_firsts>
    <ignore_firsts word="a"/>
    <ignore_firsts word="abaft"/>
    <ignore_firsts word="abeam"/>
    <ignore_firsts word="aboard"/>
    <ignore_firsts word="about"/>
    <ignore_firsts word="above"/>
    <ignore_firsts word="absent"/>
    <ignore_firsts word="according to"/>
    <ignore_firsts word="across"/>
    <ignore_firsts word="afore"/>
    <ignore_firsts word="after"/>
    <ignore_firsts word="against"/>
    <ignore_firsts word="ahead of"/>
    <ignore_firsts word="along"/>
    <ignore_firsts word="alongside"/>
    <ignore_firsts word="amid"/>
    <ignore_firsts word="amidst"/>
    <ignore_firsts word="among"/>
    <ignore_firsts word="amongst"/>
    <ignore_firsts word="an"/>
    <ignore_firsts word="and"/>
    <ignore_firsts word="apart from"/>
    <ignore_firsts word="apropos"/>
    <ignore_firsts word="around"/>
    <ignore_firsts word="as"/>
    <ignore_firsts word="as far as"/>
    <ignore_firsts word="as for"/>
    <ignore_firsts word="as long as"/>
    <ignore_firsts word="as of"/>
    <ignore_firsts word="as opposed to"/>
    <ignore_firsts word="as per"/>
    <ignore_firsts word="as regards"/>
    <ignore_firsts word="as soon as"/>
    <ignore_firsts word="as well as"/>
    <ignore_firsts word="aside"/>
    <ignore_firsts word="aside from"/>
    <ignore_firsts word="astern of"/>
    <ignore_firsts word="astride"/>
    <ignore_firsts word="at"/>
    <ignore_firsts word="athwart"/>
    <ignore_firsts word="atop"/>
    <ignore_firsts word="back to"/>
    <ignore_firsts word="barring"/>
    <ignore_firsts word="because of"/>
    <ignore_firsts word="before"/>
    <ignore_firsts word="behind"/>
    <ignore_firsts word="below"/>
    <ignore_firsts word="beneath"/>
    <ignore_firsts word="beside"/>
    <ignore_firsts word="besides"/>
    <ignore_firsts word="between"/>
    <ignore_firsts word="beyond"/>
    <ignore_firsts word="but"/>
    <ignore_firsts word="by"/>
    <ignore_firsts word="circa"/>
    <ignore_firsts word="close to"/>
    <ignore_firsts word="concerning"/>
    <ignore_firsts word="despite"/>
    <ignore_firsts word="down"/>
    <ignore_firsts word="due to"/>
    <ignore_firsts word="during"/>
    <ignore_firsts word="except"/>
    <ignore_firsts word="except for"/>
    <ignore_firsts word="excluding"/>
    <ignore_firsts word="failing"/>
    <ignore_firsts word="far from"/>
    <ignore_firsts word="following"/>
    <ignore_firsts word="for"/>
    <ignore_firsts word="from"/>
    <ignore_firsts word="given"/>
    <ignore_firsts word="in"/>
    <ignore_firsts word="in to"/>
    <ignore_firsts word="including"/>
    <ignore_firsts word="inside"/>
    <ignore_firsts word="inside of"/>
    <ignore_firsts word="instead of"/>
    <ignore_firsts word="into"/>
    <ignore_firsts word="left of"/>
    <ignore_firsts word="like"/>
    <ignore_firsts word="mid"/>
    <ignore_firsts word="midst"/>
    <ignore_firsts word="minus"/>
    <ignore_firsts word="modulo"/>
    <ignore_firsts word="near"/>
    <ignore_firsts word="near to"/>
    <ignore_firsts word="next"/>
    <ignore_firsts word="next to"/>
    <ignore_firsts word="nor"/>
    <ignore_firsts word="notwithstanding"/>
    <ignore_firsts word="of"/>
    <ignore_firsts word="off"/>
    <ignore_firsts word="on"/>
    <ignore_firsts word="on to"/>
    <ignore_firsts word="onto"/>
    <ignore_firsts word="opposite"/>
    <ignore_firsts word="opposite of"/>
    <ignore_firsts word="opposite to"/>
    <ignore_firsts word="or"/>
    <ignore_firsts word="out"/>
    <ignore_firsts word="out from"/>
    <ignore_firsts word="out of"/>
    <ignore_firsts word="outside"/>
    <ignore_firsts word="outside of"/>
    <ignore_firsts word="over"/>
    <ignore_firsts word="owing to"/>
    <ignore_firsts word="pace"/>
    <ignore_firsts word="past"/>
    <ignore_firsts word="per"/>
    <ignore_firsts word="plus"/>
    <ignore_firsts word="prior to"/>
    <ignore_firsts word="pro"/>
    <ignore_firsts word="pursuant to"/>
    <ignore_firsts word="qua"/>
    <ignore_firsts word="rather than"/>
    <ignore_firsts word="regarding"/>
    <ignore_firsts word="regardless of"/>
    <ignore_firsts word="right of"/>
    <ignore_firsts word="round"/>
    <ignore_firsts word="sans"/>
    <ignore_firsts word="save"/>
    <ignore_firsts word="since"/>
    <ignore_firsts word="so"/>
    <ignore_firsts word="subsequent to"/>
    <ignore_firsts word="such as"/>
    <ignore_firsts word="than"/>
    <ignore_firsts word="thanks to"/>
    <ignore_firsts word="that of"/>
    <ignore_firsts word="the"/>
    <ignore_firsts word="through"/>
    <ignore_firsts word="throughout"/>
    <ignore_firsts word="times"/>
    <ignore_firsts word="to"/>
    <ignore_firsts word="toward"/>
    <ignore_firsts word="towards"/>
    <ignore_firsts word="under"/>
    <ignore_firsts word="underneath"/>
    <ignore_firsts word="unlike"/>
    <ignore_firsts word="until"/>
    <ignore_firsts word="up"/>
    <ignore_firsts word="up to"/>
    <ignore_firsts word="upon"/>
    <ignore_firsts word="versus"/>
    <ignore_firsts word="via"/>
    <ignore_firsts word="vice"/>
    <ignore_firsts word="with"/>
    <ignore_firsts word="within"/>
    <ignore_firsts word="without"/>
    <ignore_firsts word="worth"/>
    <ignore_firsts word="yet"/>
</ignored_firsts>
<configs>
    <config key="AltFont">Arial</config>
    <config key="AltFontSize">9</config>
    <config key="Created">2015-06-15 13:06:35</config>
    <config key="Creator">Mark Summerfield</config>
    <config key="GenericConjunction">●and●</config>
    <config key="IgnoreSubFirsts">1</config>
    <config key="Indent">4</config>
    <config key="Initials">MS</config>
    <config key="Language">American</config>
    <config key="MonoFont">Courier New</config>
    <config key="MonoFontAsStrikeout">0</config>
    <config key="MonoFontSize">9</config>
    <config key="Note">&lt;p&gt;&lt;span style=&quot;font-size: 11pt; font-family: &#x27;Times New Roman&#x27;;&quot;&gt;&lt;i&gt;Page numbers that end with ‘t’ refer to tables, and that end with ‘f’ refer to figures.&lt;/i&gt;&lt;/span&gt;&lt;/p&gt;</config>
    <config key="PadDigits">4</config>
    <config key="PageRangeRules">pageRangeCMS16</config>
    <config key="RunInSeparator">;●</config>
    <config key="SectionPostLines">1</config>
    <config key="SectionPreLines">1</config>
    <config key="SectionSpecialTitle">&lt;span style=&quot;font-size: 11pt; font-family: &#x27;Arial&#x27;;&quot;&gt;&lt;b&gt;Symbols &amp;amp; Numbers&lt;/b&gt;&lt;/span&gt;</config>
    <config key="SectionTitles">1</config>
    <config key="See">&lt;i&gt;See&lt;/i&gt; </config>
    <config key="SeeAlso">&lt;i&gt;See also&lt;/i&gt; </config>
    <config key="SeeAlsoPosition">1</config>
    <config key="SeeAlsoPrefix">.●</config>
    <config key="SeeAlsoSeparator">;●</config>
    <config key="SeeAlsoSuffix"></config>
    <config key="SeePosition">1</config>
    <config key="SeePrefix">.●</config>
    <config key="SeeSeparator">;●</config>
    <config key="SeeSuffix"></config>
    <config key="SortAsRules">wordByWordCMS16</config>
    <config key="StdFont">Times New Roman</config>
    <config key="StdFontSize">10</config>
    <config key="Style">-1</config>
    <config key="SubSee">&lt;i&gt;see&lt;/i&gt; </config>
    <config key="SubSeeAlso">&lt;i&gt;see also&lt;/i&gt; </config>
    <config key="SubSeeAlsoPosition">1</config>
    <config key="SubSeeAlsoPrefix">●(</config>
    <config key="SubSeeAlsoSeparator">;●</config>
    <config key="SubSeeAlsoSuffix">)</config>
    <config key="SubSeePosition">1</config>
    <config key="SubSeePrefix">●(</config>
    <config key="SubSeeSeparator">;●</config>
    <config key="SubSeeSuffix">)</config>
    <config key="SuggestSpelled">1</config>
    <config key="TermPagesSeparator">,●</config>
    <config key="Title">&lt;span style=&quot;font-size: 14pt; font-family: &#x27;Times New Roman&#x27;;&quot;&gt;Index&lt;/span&gt;</config>
    <config key="UUID">EC02CA63050746EC8D92509BC789E0D4</config>
    <config key="Updated">2016-02-24 09:23:25</config>
    <config key="XRefToSubentry">0</config>
</configs>
</XindeX>
""" # noqa


if __name__ == "__main__":
    main()
