#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

import atexit
import functools
import os

import apsw

import Sql
from . import Util
from . import _XixIter
from . import _XixSequence
from Const import CountKind, FilterKind


class XixRO(_XixIter.Mixin, _XixSequence.Mixin):

    Xixs = set()

    def __init__(self):
        self.db = None


    def open(self, filename):
        self.close()
        if not os.path.exists(filename):
            return False
        self.db = apsw.Connection(
            filename, flags=apsw.SQLITE_OPEN_READONLY |
            apsw.SQLITE_OPEN_PRIVATECACHE)
        Util.register_functions(self.db)
        cursor = self.db.cursor()
        cursor.execute(Sql.PREPARE_XIX)
        cursor.execute(Sql.CREATE_XIX_CACHES)
        self._create_page_number_sequences(cursor)
        XixRO.Xixs.add(self)
        return True


    def __len__(self):
        return self.count(CountKind.ENTRIES)


    @functools.lru_cache(maxsize=None)
    def count(self, filter, eid=None):
        sql, d = Util.sql_for_count(filter, eid)
        return Sql.first(self.db.cursor(), sql, d, default=0)


    @functools.lru_cache(maxsize=None)
    def filteredCount(self, match, filter=FilterKind.TERMS_MATCHING):
        cursor = self.db.cursor()
        d = dict(match=match)
        if filter is FilterKind.PAGES_ORDER:
            sql = filter.sql_for_count(match)
            d = {}
        else:
            sql = getattr(Sql, "{}_COUNT".format(filter.name.upper()))
        return Sql.first(cursor, sql, d, default=0)


    def close(self):
        if self.db is not None:
            self.db.close()
            self.db = None
        XixRO.Xixs.discard(self)


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def cleanup():
    for db in XixRO.Xixs.copy():
        db.close()


atexit.register(cleanup)
