#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import functools

import Lib
import Sql
from Const import ROOT, SUB_INDICATOR
from . import Util


class Mixin:

    @functools.lru_cache(maxsize=None)
    def hasDeletedEntry(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.HAS_DELETED_ENTRY, dict(eid=eid),
                             default=False, Class=bool)


    @functools.lru_cache(maxsize=None)
    def deletedEntry(self, eid):
        record = None
        with Lib.Transaction.Transaction(self) as cursor:
            record = cursor.execute(Sql.GET_DELETED_ENTRY, dict(eid=eid)
                                    ).fetchone()
        if record is not None:
            eid, saf, sortas, term, pages, notes, peid = record
            return Util.Entry(eid, saf, sortas, term, pages, notes,
                              peid=peid)


    @functools.lru_cache(maxsize=None)
    def hasEntry(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.HAS_ENTRY, dict(eid=eid),
                             default=False, Class=bool)


    @functools.lru_cache(maxsize=None)
    def entry(self, eid, *, withIndent=False, withXrefIndicator=False,
              transaction=True):
        if transaction:
            with Lib.Transaction.Transaction(self) as cursor:
                return self._entry(eid, withIndent, withXrefIndicator,
                                   cursor)
        else:
            cursor = self.db.cursor()
            return self._entry(eid, withIndent, withXrefIndicator, cursor)


    def _entry(self, eid, withIndent, withXrefIndicator, cursor):
        record = cursor.execute(Sql.GET_ENTRY, dict(eid=eid)).fetchone()
        if record is not None:
            eid, saf, sortas, term, pages, notes, peid = record
            if withXrefIndicator:
                xrefCount = self._xrefCount(eid, cursor)
            else:
                xrefCount = 0
            if not withIndent:
                return Util.Entry(eid, saf, sortas, term, pages, notes,
                                  peid=peid, xrefCount=xrefCount)
            if peid == ROOT:
                return Util.Entry(eid, saf, sortas, term, pages, notes,
                                  peid=peid, xrefCount=xrefCount, indent=0)
            indent = 0
            originalEid = eid
            while True:
                record = cursor.execute(Sql.GET_PEID,
                                        dict(eid=eid)).fetchone()
                if record is None:
                    break
                indent += 1
                eid = record[0]
            return Util.Entry(originalEid, saf, sortas, term, pages, notes,
                              peid=peid, xrefCount=xrefCount,
                              indent=max(0, indent - 2))


    @functools.lru_cache(maxsize=None)
    def term(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.GET_TERM, dict(eid=eid), Class=str)


    @functools.lru_cache(maxsize=None)
    def termPath(self, eid, term=None, *, sep=" {} ".format(SUB_INDICATOR)):
        """Return term ▷ subterm... for the given eid.

        If term is given this means we want the full path to the eid
        with term added on (i.e., when we're about to add a new subentry)
        """
        terms = [entry.term for entry in self.parentEntries(eid)]
        if term is not None:
            terms.append(term)
        return sep.join(terms)


    def hasSubentry(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.HAS_SUBENTRY, dict(eid=eid),
                             default=False, Class=bool)


    def deleteDeletedEntry(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            cursor.execute(Sql.DELETE_DELETED_ENTRY, dict(eid=eid))


    @functools.lru_cache(maxsize=None)
    def eidForEid(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            record = cursor.execute(Sql.GET_EID_FOR_EID, dict(eid=eid)
                                    ).fetchone()
            if record is not None:
                eid = record[0]
            if not Sql.first(cursor, Sql.HAS_ENTRY, dict(eid=eid),
                             default=False, Class=bool):
                eid = ROOT
            return eid


    def setEidForEid(self, old_eid, new_eid):
        with Lib.Transaction.Transaction(self) as cursor:
            cursor.execute(Sql.SET_EID_FOR_EID, dict(old_eid=old_eid,
                                                     new_eid=new_eid))


    @functools.lru_cache(maxsize=None)
    def parentOf(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.GET_PEID, dict(eid=eid),
                             default=ROOT)


    @functools.lru_cache(maxsize=None)
    def parentEntries(self, eid):
        entries = []
        with Lib.Transaction.Transaction(self) as cursor:
            while eid != ROOT:
                record = cursor.execute(Sql.GET_ENTRY,
                                        dict(eid=eid)).fetchone()
                if record is not None:
                    eid, saf, sortas, term, pages, notes, peid = record
                    entry = Util.Entry(eid, saf, sortas, term, pages, notes,
                                       peid=peid)
                    entries.append(entry)
                    eid = entry.peid
        entries.reverse()
        return entries


    def topLevelParentTerm(self, eid):
        entries = self.parentEntries(eid)
        return entries[0].term if len(entries) > 1 else None


    def _xrefCount(self, eid, cursor):
        return Sql.first(cursor, Sql.XREF_COUNT, dict(eid=eid), default=0)
