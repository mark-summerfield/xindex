#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import datetime
import xml.etree.ElementTree as ET
import xml.parsers.expat

import apsw

import SortAs
import Sql
import Xix.Util
from Config import Gconf
from Const import error, VISUAL_SPACE, XrefKind


def importIndex(cursor, inFilename):
    try:
        tree = ET.parse(inFilename)
    except (OSError, ET.ParseError, xml.parsers.expat.ExpatError) as err:
        error("Failed to read “{}”: {}".format(inFilename, err))
        return False
    root = tree.getroot()
    # version = root.get("version") # May be needed if the format changes
    cursor.execute("DELETE FROM groups")
    cursor.execute("DELETE FROM grouped")
    cursor.execute("DELETE FROM spelling")
    cursor.execute("DELETE FROM ignored_firsts")
    _addGroups(cursor, root.find("groups"))
    _addWords(cursor, root.find("spelling"), "spell", Sql.ADD_SPELL_WORD)
    _addWords(cursor, root.find("ignored_firsts"), "ignore_firsts",
              Sql.ADD_IGNORED_FIRSTS_WORD)
    _addConfigs(cursor, root.find("configs"))
    _addEntries(cursor, root.find("entries"))
    return True


def _addGroups(cursor, root):
    if root is not None:
        for element in root.iter("group"):
            gid = int(element.get("gid"))
            linked = int(element.get("linked"))
            name = element.text
            if name is not None:
                cursor.execute(Sql.RE_ADD_GROUP, dict(gid=gid, name=name))
                if linked:
                    cursor.execute(Sql.UPDATE_GROUP, dict(gid=gid,
                                                          linked=1))


def _addWords(cursor, root, tag, sql):
    if root is not None:
        for element in root.iter(tag):
            word = element.get("word")
            if word is not None:
                cursor.execute(sql, dict(word=word))


def _addConfigs(cursor, root):
    if root is not None:
        for element in root.iter("config"):
            key = element.get("key")
            value = element.text
            if value is not None:
                value = value.replace(VISUAL_SPACE, " ")
            cursor.execute(Sql.INSERT_CONFIG, dict(key=key, value=value))


def _addEntries(cursor, root):
    if root is not None:
        xrefs = []
        groups = []
        sortBy = SortAs.RulesForName[Gconf.Default.SortAsRules].function
        entryForEid = {}
        for element in root.iter("entry"):
            entry = _entry(element, sortBy)
            if entry.term is None:
                continue # Ignore invalid terms
            entryForEid[(entry.peid, entry.eid)] = entry
            _appendXrefs(xrefs, entry.eid, element.find("xrefs"))
            groups.append((entry.eid, element.get("gids")))
        _populateEntries(cursor, entryForEid)
        _addXrefs(cursor, xrefs)
        _addToGroups(cursor, groups)


def _entry(element, sortBy):
    eid = int(element.get("eid"))
    peid = int(element.get("peid"))
    now = str(datetime.datetime.now())[:19]
    created = element.get("created") or now
    updated = element.get("updated") or now
    term = element.find("term")
    term = term.text if term is not None else ""
    sortas = element.find("sortas")
    saf = sortas.get("saf")
    sortas = sortas.text
    pages = element.find("pages")
    pages = pages.text if pages is not None else ""
    notes = element.find("notes")
    notes = notes.text if notes is not None else ""
    return Xix.Util.Entry(eid, saf, sortas, term, pages, notes, peid=peid,
                          created=created, updated=updated)


def _populateEntries(cursor, entryForEid):
    pending = []
    for key, entry in sorted(entryForEid.items()):
        peid, eid = key
        try:
            cursor.execute(Sql.REINSERT_ENTRY_WITH_DATES, dict(
                eid=eid, saf=entry.saf, sortas=entry.sortas,
                term=entry.term, pages=entry.pages, notes=entry.notes,
                peid=peid, created=entry.created,
                updated=entry.updated))
        except apsw.ConstraintError:
            pending.append((peid, eid, entry))
    for peid, eid, entry in sorted(pending):
        cursor.execute(Sql.REINSERT_ENTRY_WITH_DATES, dict(
            eid=eid, saf=entry.saf, sortas=entry.sortas,
            term=entry.term, pages=entry.pages, notes=entry.notes,
            peid=peid, created=entry.created,
            updated=entry.updated))


def _appendXrefs(xrefs, from_eid, root):
    if root is not None:
        for xref in root.iter("see"):
            to_eid = xref.get("to_eid")
            if to_eid is None:
                xrefs.append(Xix.Util.Xref(from_eid, None, xref.text,
                             XrefKind.SEE_GENERIC))
            else:
                xrefs.append(Xix.Util.Xref(from_eid, int(to_eid), None,
                                           XrefKind.SEE))
        for xref in root.iter("seealso"):
            to_eid = xref.get("to_eid")
            if to_eid is None:
                xrefs.append(Xix.Util.Xref(from_eid, None, xref.text,
                             XrefKind.SEE_ALSO_GENERIC))
            else:
                xrefs.append(Xix.Util.Xref(from_eid, int(to_eid), None,
                                           XrefKind.SEE_ALSO))


def _addXrefs(cursor, xrefs):
    for xref in xrefs:
        if xref.kind in {XrefKind.SEE, XrefKind.SEE_ALSO}:
            sql = Sql.INSERT_XREF
            d = dict(from_eid=xref.from_eid, to_eid=xref.to_eid,
                     kind=xref.kind)
        else:
            sql = Sql.INSERT_GENERIC_XREF
            d = dict(from_eid=xref.from_eid, term=xref.term, kind=xref.kind)
        cursor.execute(sql, d)


def _addToGroups(cursor, groups):
    if groups:
        for eid, gids in groups:
            if gids:
                for gid in gids.split(","):
                    cursor.execute(Sql.ADD_TO_GROUP, dict(gid=int(gid),
                                                          eid=eid))
