#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import string

import Lib
import Sql
from . import Output
from . import Util
from Const import EntryDataKind, FilterKind, ROOT, UNLIMITED, XrefKind


SYMBOL = "@"


class Mixin:

    def xrefs(self, eid, *, transaction=True):
        if transaction:
            with Lib.Transaction.Transaction(self) as cursor:
                yield from _xrefs(eid, cursor)
        else:
            cursor = self.db.cursor()
            yield from _xrefs(eid, cursor)


    def generic_xrefs(self, eid, *, transaction=True):
        if transaction:
            with Lib.Transaction.Transaction(self) as cursor:
                yield from _generic_xrefs(eid, cursor)
        else:
            cursor = self.db.cursor()
            yield from _generic_xrefs(eid, cursor)


    def all_xrefs(self, eid, *, transaction=True):
        if transaction:
            with Lib.Transaction.Transaction(self) as cursor:
                yield from _all_xrefs(eid, cursor)
        else:
            cursor = self.db.cursor()
            yield from _all_xrefs(eid, cursor)


    def subentries(self, eid):
        """Immediate subentries i.e., not recursive -- see entries()"""
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.GET_SUBENTRIES,
                                         dict(peid=eid)):
                yield record[0] # EID


    def deletableXRefs(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.DELETABLE_XREFS,
                                         dict(eid=eid)):
                yield Util.xref_for_record(record)


    def deletedXRefs(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.DELETED_XREFS, dict(eid=eid)):
                yield Util.xref_for_record(record)


    def deletableGenericXRefs(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.DELETABLE_GENERIC_XREFS,
                                         dict(eid=eid)):
                yield Util.generic_xref_for_record(eid, record)


    def deletedGenericXRefs(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.DELETED_GENERIC_XREFS,
                                         dict(eid=eid)):
                yield Util.generic_xref_for_record(eid, record)


    def deletableEntries(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.DELETABLE_EIDS,
                                         dict(peid=eid)):
                yield record[0] # EID


    def deletedEntries(self):
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.DELETED_ENTRIES):
                yield Util.DeletedEntry(*record)


    def deletedSubentries(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.DELETED_SUBENTRIES,
                                         dict(eid=eid)):
                yield record[0] # EID


    def filteredEntries(self, *, filter=FilterKind.TERMS_MATCHING, match="",
                        offset=0, limit=UNLIMITED,
                        entryData=EntryDataKind.EID):
        """Yields up to limit entries that match"""
        cursor, sql, d = self._filteredQuery(filter, match, offset, limit)
        for record in cursor.execute(sql, d):
            eid = record[0]
            if eid == ROOT:
                continue
            if entryData is EntryDataKind.EID:
                yield eid
            else:
                # It is much faster to use a subquery only for the needed
                # rows with a main query that just picks up eids
                subcursor = self.db.cursor()
                if entryData in {EntryDataKind.ALL_DATA,
                                 EntryDataKind.ALL_DATA_AND_XREF}:
                    record = subcursor.execute(Sql.GET_ENTRY,
                                               dict(eid=eid)).fetchone()
                    eid, saf, sortas, term, pages, notes, peid = record
                    if entryData is EntryDataKind.ALL_DATA_AND_XREF:
                        xrefCount = self._xrefCount(eid, subcursor)
                    else:
                        xrefCount = 0
                    yield Util.Entry(eid, saf, sortas, term, pages, notes,
                                     peid=peid, xrefCount=xrefCount)
                elif entryData is EntryDataKind.ALL_DATA_AND_DATES:
                    record = subcursor.execute(Sql.GET_ENTRY_AND_DATES,
                                               dict(eid=eid)).fetchone()
                    eid, saf, sortas, term, pages, notes, peid, created, \
                        updated = record
                    yield Util.Entry(eid, saf, sortas, term, pages, notes,
                                     peid=peid, created=created,
                                     updated=updated)


    def _filteredQuery(self, filter, match, offset, limit):
        # If there is a limit, and it includes the ROOT, we must add one
        # to the limit, since we skip the ROOT
        limit1 = limit + 1 if limit != UNLIMITED else limit
        sql, d = Util.sql_for_iterate(filter, match, offset, limit1)
        cursor = self.db.cursor()
        if filter is FilterKind.HAS_OVERLAPPING_PAGES:
            if not Sql.first(cursor, Sql.HAS_OVERLAPPING_PAGES_CACHE_COUNT,
                             default=False, Class=bool):
                cursor.execute(Sql.HAS_OVERLAPPING_PAGES_CACHE_REFRESH)
            sql = Sql.HAS_OVERLAPPING_PAGES_CACHE_EIDS
        elif filter is FilterKind.SAME_TERM_TEXTS:
            if not Sql.first(cursor, Sql.SAME_TERM_TEXTS_CACHE_COUNT,
                             default=False, Class=bool):
                cursor.execute(Sql.SAME_TERM_TEXTS_CACHE_REFRESH)
            sql = Sql.SAME_TERM_TEXTS_CACHE_EIDS
        return cursor, sql, d


    def entries(self, *, offset=0, limit=UNLIMITED,
                entryData=EntryDataKind.INDENT_AND_EID, peid=ROOT):
        """Yields up to limit subentries of peid"""
        cursor, sql, d = self._entriesQuery(offset, limit, peid)
        for record in cursor.execute(sql, d):
            indent, eid = record
            if eid == ROOT:
                continue
            if entryData is EntryDataKind.INDENT_AND_EID:
                yield indent, eid
            else:
                # It is much faster to use a subquery only for the needed
                # rows with a main query that just picks up indents and eids
                subcursor = self.db.cursor()
                if entryData in {EntryDataKind.ALL_DATA,
                                 EntryDataKind.ALL_DATA_AND_XREF}:
                    record = subcursor.execute(Sql.GET_ENTRY,
                                               dict(eid=eid)).fetchone()
                    eid, saf, sortas, term, pages, notes, peid = record
                    if entryData is EntryDataKind.ALL_DATA_AND_XREF:
                        xrefCount = self._xrefCount(eid, subcursor)
                    else:
                        xrefCount = 0
                    yield Util.Entry(eid, saf, sortas, term, pages, notes,
                                     peid=peid, xrefCount=xrefCount,
                                     indent=indent)
                elif entryData is EntryDataKind.ALL_DATA_AND_DATES:
                    record = subcursor.execute(Sql.GET_ENTRY_AND_DATES,
                                               dict(eid=eid)).fetchone()
                    eid, saf, sortas, term, pages, notes, peid, created, \
                        updated = record
                    yield Util.Entry(eid, saf, sortas, term, pages, notes,
                                     peid=peid, indent=indent,
                                     created=created, updated=updated)


    def _entriesQuery(self, offset, limit, peid):
        # If there is a limit, and it includes the ROOT, we must add one
        # to the limit, since we skip the ROOT
        limit1 = limit + 1 if limit != UNLIMITED else limit
        d = dict(offset=offset, limit=limit1)
        cursor = self.db.cursor()
        if peid == ROOT:
            if not Sql.first(cursor, Sql.ENTRIES_CACHE_COUNT,
                             default=False, Class=bool):
                cursor.execute(Sql.ENTRIES_CACHE_REFRESH)
            sql = Sql.ENTRIES_CACHE_EIDS
        else:
            sql = Sql.ENTRY_EIDS
            d.update(peid=peid)
        return cursor, sql, d


    def outputEntries(self, config):
        xrefSql = Sql.OUTPUT_XREFS.format(sortAs=config.SortAsRules)
        letter = None
        yield Output.Start(config.Title, config.Note)
        cursor = self.db.cursor()
        for record in cursor.execute(Sql.OUTPUT_ENTRIES):
            entry = Output.Entry(*record)
            if entry.indent == 0:
                char = _getChar(letter, entry)
                if char != letter:
                    if not config.SectionTitles:
                        yield Output.Section()
                    else:
                        if letter is None and char == SYMBOL:
                            yield Output.Section(config.SectionSpecialTitle)
                        else:
                            yield Output.Section(char.upper())
                    letter = char
            subcursor = self.db.cursor()
            entry.childcount = Sql.first(subcursor, Sql.COUNT_SUBENTRIES,
                                         dict(peid=entry.eid), default=0)
            self._populateXRefs(subcursor, entry, xrefSql)
            yield entry
        yield Output.End()


    def allEntriesWithPages(self):
        cursor = self.db.cursor()
        for record in cursor.execute(Sql.ENTRIES_WITH_PAGES):
            eid, saf, sortas, term, pages, notes, peid = record
            yield Util.Entry(eid, saf, sortas, term, pages, notes,
                             peid=peid)


    def _populateXRefs(self, subcursor, entry, xrefSql):
        entry.xrefs = []
        for xref in list(subcursor.execute(xrefSql, dict(eid=entry.eid))):
            kind, toterm, to_eid = xref
            totermparent = self.topLevelParentTerm(to_eid)
            kind = XrefKind(kind)
            if kind is XrefKind.SEE:
                Class = Output.See
            elif kind is XrefKind.SEE_ALSO:
                Class = Output.SeeAlso
            elif kind is XrefKind.SEE_GENERIC:
                Class = Output.SeeGeneric
            elif kind is XrefKind.SEE_ALSO_GENERIC:
                Class = Output.SeeAlsoGeneric
            entry.xrefs.append(Class(toterm, totermparent))


def _xrefs(eid, cursor):
    for record in cursor.execute(Sql.GET_XREFS, dict(eid=eid)):
        yield Util.Xref(eid, record[0], None, XrefKind(record[1]))


def _generic_xrefs(eid, cursor):
    for record in cursor.execute(Sql.GET_GENERIC_XREFS, dict(eid=eid)):
        yield Util.generic_xref_for_record(eid, record)


def _all_xrefs(eid, cursor):
    for record in cursor.execute(Sql.GET_ALL_XREFS, dict(eid=eid)):
        from_eid, to_eid, term, kind = record
        yield Util.Xref(from_eid, to_eid, term, XrefKind(kind))


def _getChar(letter, entry):
    term = Lib.htmlToPlainText(entry.term)
    char = term[0].casefold()
    if char not in string.ascii_lowercase:
        if letter is None:
            char = SYMBOL
        elif letter == SYMBOL:
            char = letter
        else:
            for c in entry.sortas:
                if c.isalpha():
                    char = c.casefold()
                    break
    return char
