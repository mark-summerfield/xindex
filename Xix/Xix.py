#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

import atexit
import functools
import os
import re
import time

import apsw

import Lib
import Output.Markup
import Pages
import Sql
import SortAs
from Config import Config, Gconf, Gopt
from Const import (
    CommandKind, CountKind, EntryDataKind, FileKind, FilterKind,
    MARKUP_NAMES)
from . import Util
from . import _XixEntry
from . import _XixGroups
from . import _XixIter
from . import _XixSetRules
from . import _XixSequence
from . import _XixImport


VERSION = 100


SANITIZE_MATCH_RX = re.compile(r"[()']")
MAX_OPENED = 11


class Xix(_XixEntry.Mixin, _XixGroups.Mixin, _XixIter.Mixin,
          _XixSetRules.Mixin, _XixSequence.Mixin, _XixImport.Mixin):

    Xixs = set()

    def __init__(self, filename=None, username=None, language=None,
                 sortAsRules=Gopt.Default.SortAsRules,
                 pageRangeRules=Gopt.Default.PageRangeRules):
        self.db = None
        self.username = username
        self.error = None # For Transaction
        self.monotime = 0
        if filename is not None:
            self.open(filename, language, sortAsRules, pageRangeRules)


    def open(self, filename, language, sortAsRules, pageRangeRules):
        self.close()
        create = not os.path.exists(filename)
        self.db = apsw.Connection(filename)
        Util.register_functions(self.db)
        Util.register_rules(self.db, SortAs, Pages)
        cursor = self.db.cursor()
        cursor.execute(Sql.PREPARE_XIX) # Can't be done in a transaction
        with Lib.Transaction.Transaction(self) as cursor:
            if create:
                Util.create_xix(VERSION, self.username, cursor, language,
                                sortAsRules, pageRangeRules)
            else:
                user_version = self.version(cursor)
                Util.open_xix(user_version, VERSION, self.username, cursor,
                              self.db, pageRangeRules)
        cursor.execute(Sql.CREATE_XIX_CACHES)
        self._create_page_number_sequences(cursor)
        self.monotime = time.monotonic()
        self._cache_clear()
        Xix.Xixs.add(self)


    def version(self, cursor=None):
        return Sql.first(cursor or self.db.cursor(), Sql.GET_VERSION,
                         default=100) # default is the first ever version


    def _cache_clear(self): # Must be called whenever the db is changed
        if self.db is not None:
            cursor = self.db.cursor()
            cursor.execute(Sql.CACHES_CLEAR)
        for method in (self.hasDeletedEntry, self.deletedEntry,
                       self.hasEntry, self.entry, self.term,
                       self.termPath, self.eidForEid, self.config,
                       self.sortAsRules, self.pageRangeRules, self.count,
                       self.firstForPrefix, self.firstForLetter,
                       self.parentEntries, self.parentOf,
                       self.filteredCount, self.xrefOptions,
                       self.spellWords, self.ignoredFirstsWords):
            method.cache_clear()


    @functools.lru_cache(maxsize=None)
    def config(self, key, default=None):
        """Returns the key's value (which has the correct type, enum,
        bool, int, str, etc."""
        record = None
        with Lib.Transaction.Transaction(self) as cursor:
            record = cursor.execute(Sql.GET_CONFIG_VALUE,
                                    dict(key=key)).fetchone()
        if record is None:
            return default
        return Util.from_basic_type(key, record[0])


    def setConfig(self, key, value):
        with Lib.Transaction.Transaction(self) as cursor:
            value = Util.to_basic_type(value)
            cursor.execute(Sql.UPDATE_CONFIG, dict(key=key, value=value))
        self.config.cache_clear()


    def setConfigs(self, config):
        with Lib.Transaction.Transaction(self) as cursor:
            for key, value in config:
                value = Util.to_basic_type(value)
                cursor.execute(Sql.UPDATE_CONFIG, dict(key=key,
                                                       value=value))
        self.config.cache_clear()


    def configs(self):
        """All the values have the correct type, enum, bool, int, str,
        etc."""
        config = Config()
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.CONFIGS):
                key, value = record
                setattr(config, key, Util.from_basic_type(key, value))
        return config


    @functools.lru_cache(maxsize=None)
    def xrefOptions(self):
        d = {}
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.XREF_OPTIONS):
                key, value = record
                d[key] = Util.from_basic_type(key, value)
        return d


    @functools.lru_cache(maxsize=None)
    def sortAsRules(self):
        return self.config(Gconf.Key.SortAsRules, Gopt.Default.SortAsRules)


    @functools.lru_cache(maxsize=None)
    def pageRangeRules(self):
        return self.config(Gconf.Key.PageRangeRules,
                           Gopt.Default.PageRangeRules)


    def __len__(self):
        return self.count(CountKind.ENTRIES)


    @functools.lru_cache(maxsize=None)
    def count(self, filter, eid=None):
        sql, d = Util.sql_for_count(filter, eid)
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, sql, d, default=0)


    @functools.lru_cache(maxsize=None)
    def firstForPrefix(self, prefix):
        match = SANITIZE_MATCH_RX.search(prefix)
        if match is not None:
            prefix = prefix[:match.start()].rstrip()
        prefix = "^{}*".format(prefix.strip("^*"))
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.FIRST_FOR_PREFIX,
                             dict(prefix=prefix))


    @functools.lru_cache(maxsize=None)
    def firstForLetter(self, letter):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.FIRST_FOR_LETTER,
                             dict(letter=letter))


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


    def __iter__(self):
        for entry in self.entries(entryData=EntryDataKind.ALL_DATA):
            yield entry


    def doCommand(self, command):
        if isinstance(command, Lib.Command.Macro):
            return self._executeMacro(CommandKind.DO, command)
        return self._executeCommand(CommandKind.DO, command)


    def undoCommand(self, command):
        if isinstance(command, Lib.Command.Macro):
            return self._executeMacro(CommandKind.UNDO, command)
        return self._executeCommand(CommandKind.UNDO, command)


    def _executeCommand(self, kind, command):
        self._cache_clear()
        if kind is CommandKind.DO:
            query = command.do()
            if ((hasattr(command, "eid") and command.eid is not None) or
                    (hasattr(command, "gid") and command.gid is not None)):
                action = "(Re)did "
            else:
                action = "Did "
        else:
            query = command.undo()
            action = "Undid "
        record = None
        with Lib.Transaction.Transaction(self) as cursor:
            record = cursor.execute(query.sql, query.params).fetchone()
        if record is not None: # Allow for AddEntry/AddGroup
            command.eid = command.gid = record[0]
        return action + command.description


    def _executeMacro(self, kind, macro):
        self._cache_clear()
        if kind is CommandKind.DO:
            sequence = macro.do_sequence
            action = "Did "
        else:
            sequence = macro.undo_sequence
            action = "Undid "
        with Lib.Transaction.Transaction(self) as cursor:
            for command in sequence():
                query = (command.do() if kind is CommandKind.DO else
                         command.undo())
                record = cursor.execute(query.sql, query.params).fetchone()
                if record is not None: # Allow for AddEntry/AddGroup
                    command.eid = command.gid = record[0]
        return action + macro.description


    def addSpellWord(self, word):
        with Lib.Transaction.Transaction(self) as cursor:
            cursor.execute(Sql.ADD_SPELL_WORD, dict(word=word))
        self.spellWords.cache_clear()


    def removeSpellWord(self, word):
        with Lib.Transaction.Transaction(self) as cursor:
            cursor.execute(Sql.REMOVE_SPELL_WORD, dict(word=word))
        self.spellWords.cache_clear()


    @functools.lru_cache(maxsize=None)
    def spellWords(self):
        with Lib.Transaction.Transaction(self) as cursor:
            return [record[0] for record in
                    cursor.execute(Sql.GET_SPELL_WORDS)]


    @functools.lru_cache(maxsize=None)
    def ignoredFirstsWords(self):
        with Lib.Transaction.Transaction(self) as cursor:
            return frozenset(record[0] for record in
                             cursor.execute(Sql.GET_IGNORED_FIRSTS_WORDS))


    def markups(self):
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.MARKUPS):
                yield record[0]


    def markup(self, extension):
        markup = Output.Markup.Markup(FileKind.USER)
        with Lib.Transaction.Transaction(self) as cursor:
            for name in MARKUP_NAMES:
                record = cursor.execute(
                    Sql.MARKUP_FIELD.format(name.lower()),
                    dict(extension=extension)).fetchone()
                if record is not None:
                    setattr(markup, name, record[0])
        return markup if hasattr(markup, "escapefunction") else None


    def updateMarkup(self, extension, markup):
        d = dict(extension=extension)
        for name in MARKUP_NAMES:
            d[name.lower()] = getattr(markup, name, "")
        with Lib.Transaction.Transaction(self) as cursor:
            cursor.execute(Sql.UPDATE_MARKUP, d)


    def deleteMarkup(self, extension):
        with Lib.Transaction.Transaction(self) as cursor:
            cursor.execute(Sql.DELETE_MARKUP, dict(extension=extension))


    def bookmarks(self):
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.BOOKMARKS):
                yield record # (eid, term, istop)


    def addBookmark(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            cursor.execute(Sql.ADD_BOOKMARK, dict(eid=eid))


    def removeBookmark(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            cursor.execute(Sql.REMOVE_BOOKMARK, dict(eid=eid))


    def bookmarked(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.HAS_BOOKMARK, dict(eid=eid),
                             default=False, Class=bool)


    def hasBookmarks(self):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.HAS_BOOKMARKS, default=False,
                             Class=bool)


    def autoReplacementFor(self, word):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.GET_AUTO_REPLACE, dict(word=word),
                             Class=str)


    def optimize(self):
        cursor = self.db.cursor()
        cursor.execute(Sql.OPTIMIZE)


    def backup(self, filename, prefix, reportProgress):
        reportProgress("{} …".format(prefix))
        try:
            db = apsw.Connection(filename)
            with db.backup("main", self.db, "main") as bak:
                while not bak.done:
                    bak.step(64) # 64K at a time
                    percent = ((bak.pagecount - bak.remaining) /
                               bak.pagecount * 100)
                    reportProgress("{} {:.0f}%".format(prefix, percent))
        finally:
            db.close()


    def close(self):
        self._cache_clear()
        if self.db is not None:
            cursor = self.db.cursor()
            if Sql.first(cursor, Sql.GET_CONFIG_VALUE, dict(key="Opened"),
                         default=0) > MAX_OPENED:
                cursor.execute(Sql.OPTIMIZE)
            with Lib.Transaction.Transaction(self) as cursor:
                cursor.execute(Sql.CLOSE,
                               dict(seconds=round(time.monotonic() -
                                    self.monotime)))
            self.db.close()
            self.db = None
        Xix.Xixs.discard(self)


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def cleanup():
    for db in Xix.Xixs.copy():
        db.close()


atexit.register(cleanup)
