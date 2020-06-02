#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import html

import Lib
import Xix
import Xix.Util
from Const import EntryDataKind, STRIP_AT_RX, VISUAL_SPACE, XrefKind


CONFIG_INTERNAL = frozenset({"Filename", "Worktime", "Opened"})
NEED_VISUAL_SPACE = frozenset({
    "GenericConjunction", "RunInSeparator", "SeePrefix", "SeeSeparator",
    "SeeSuffix", "SubSeePrefix", "SubSeeSeparator", "SubSeeSuffix",
    "SeeAlsoPrefix", "SeeAlsoSeparator", "SeeAlsoSuffix",
    "SubSeeAlsoPrefix", "SubSeeAlsoSeparator", "SubSeeAlsoSuffix",
    "TermPagesSeparator"})


DOCUMENT_START = """\
<?xml version="1.0" encoding="UTF-8"?>
<XindeX version="{version}">
"""
DOCUMENT_END = "</XindeX>\n"
ENTRY = """<entry eid="{eid}" peid="{peid}" created="{created}" \
updated="{updated}" gids="{gids}">
    <term>{term}</term>
    <sortas saf="{saf}">{sortas}</sortas>{pages}{notes}{xrefs}
</entry>
"""
SEETO = """        <see to_eid="{}"/>\n"""
SEEALSOTO = """        <seealso to_eid="{}"/>\n"""
SEEGENERIC = """        <see>{}</see>\n"""
SEEALSOGENERIC = """        <seealso>{}</seealso>\n"""
GROUP = """    <group gid="{gid}" linked="{linked}">{name}</group>\n"""
SPELL = """    <spell word="{}"/>\n"""
IGNORE = """    <ignore_firsts word="{}"/>\n"""
CONFIG = """    <config key="{key}">{value}</config>\n"""


def outputEntries(model, config, prefix, reportProgress):
    total = len(model)
    percents = set()
    with Lib.uopen(config.Filename, "wt") as file:
        file.write(DOCUMENT_START.format(version=Xix.VERSION))
        _writeGroups(file, list(model.allGroups()), "groups", GROUP)
        file.write("<entries>\n")
        for i, entry in enumerate(list(model.entries(
                entryData=EntryDataKind.ALL_DATA_AND_DATES))):
            percent = int(min(100, i * 100 // total))
            if percent not in percents: # report every 1% done
                reportProgress("{} {}%".format(prefix, percent))
                percents.add(percent)
            _writeEntry(file, model, entry)
        file.write("</entries>\n")
        _writeWords(file, sorted(model.spellWords()), "spelling", SPELL)
        _writeWords(file, sorted(model.ignoredFirstsWords()),
                    "ignored_firsts", IGNORE)
        _writeConfig(file, config)
        file.write(DOCUMENT_END)


def _writeEntry(file, model, entry):
    xrefs = _xrefs(model, entry)
    sortas = html.escape(entry.sortas)
    pages = ("\n    <pages>{}</pages>".format(html.escape(
             STRIP_AT_RX.sub("", entry.pages))) if entry.pages else "")
    notes = ("\n    <notes>{}</notes>".format(html.escape(entry.notes))
             if entry.notes else "")
    gids = []
    for gid, _ in model.groupsForEid(entry.eid):
        gids.append(str(gid))
    file.write(ENTRY.format(eid=entry.eid, peid=entry.peid, saf=entry.saf,
               sortas=sortas, term=html.escape(entry.term or ""),
               pages=pages, notes=notes, xrefs=xrefs,
               created=entry.created, updated=entry.updated,
               gids=",".join(gids)))


def _xrefs(model, entry):
    xrefs = []
    for xref in list(model.all_xrefs(entry.eid)):
        if xref.from_eid != entry.eid:
            continue # We only want those *from* this entry
        if xref.kind is XrefKind.SEE:
            xrefs.append(SEETO.format(xref.to_eid))
        elif xref.kind is XrefKind.SEE_ALSO:
            xrefs.append(SEEALSOTO.format(xref.to_eid))
        elif xref.kind is XrefKind.SEE_GENERIC:
            xrefs.append(SEEGENERIC.format(html.escape(xref.term)))
        elif xref.kind is XrefKind.SEE_ALSO_GENERIC:
            xrefs.append(SEEALSOGENERIC.format(html.escape(xref.term)))
    if xrefs:
        xrefs = "".join(xrefs)
        return "\n    <xrefs>\n" + xrefs + "    </xrefs>"
    return ""


def _writeGroups(file, groups, tag, template):
    if groups:
        file.write("<{}>\n".format(tag))
        for gid, name, linked in groups:
            file.write(template.format(gid=gid, linked=int(linked),
                                       name=html.escape(name)))
        file.write("</{}>\n".format(tag))


def _writeWords(file, words, tag, template):
    if words:
        file.write("<{}>\n".format(tag))
        for word in words:
            file.write(template.format(html.escape(word, True)))
        file.write("</{}>\n".format(tag))


def _writeConfig(file, config):
    file.write("<configs>\n")
    for key, value in config:
        if key in CONFIG_INTERNAL:
            continue
        if value is None:
            value = ""
        else:
            value = str(Xix.Util.to_basic_type(value))
            if key in NEED_VISUAL_SPACE:
                value = value.replace(" ", VISUAL_SPACE)
        file.write(CONFIG.format(key=key, value=html.escape(value)))
    file.write("</configs>\n")
