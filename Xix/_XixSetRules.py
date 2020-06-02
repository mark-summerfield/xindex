#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import logging

import Lib
import Saf
import Sql
import Pages
import SortAs
from Config import Gconf, Gopt


class Mixin:


    def setSortAsRules(self, name, prefix=None, reportProgress=None):
        total = len(self)
        percents = set()
        sortBy = SortAs.RulesForName[name].function
        ignored = self.ignoredFirstsWords()
        ignoreFirsts = bool(self.config(Gconf.Key.IgnoreSubFirsts,
                                        Gopt.Default.IgnoreSubFirsts))
        pad_digits = self.config(Gconf.Key.PadDigits,
                                 Gopt.Default.PadDigits)
        with Lib.Timer("Changed Sort As in", 0.2):
            with Lib.Transaction.Transaction(self) as cursor:
                cursor.execute(Sql.UPDATE_CONFIG,
                               dict(key=Gconf.Key.SortAsRules, value=name))
                records = list(cursor.execute(Sql.GET_SORTAS_DATA))
                for i, record in enumerate(records):
                    percent = int(min(100, i * 100 // total))
                    if percent not in percents: # report every 1% done
                        if reportProgress is not None:
                            reportProgress("{} {}%".format(prefix, percent))
                        percents.add(percent)
                    eid, istop, term, saf, sortas = record
                    if saf != Saf.CUSTOM:
                        sortas = sortBy(term, saf, pad_digits=pad_digits,
                                        ignored=None
                                        if (istop or ignoreFirsts)
                                        else ignored)
                    cursor.execute(Sql.UPDATE_SORTAS_DATA,
                                   dict(sortas=sortas, eid=eid))
        self._cache_clear()


    def setPageRangeRules(self, name, prefix=None, reportProgress=None):
        total = len(self)
        percents = set()
        pageRange = Pages.RulesForName[name].function
        with Lib.Timer("Changed Pages in", 0.2):
            with Lib.Transaction.Transaction(self) as cursor:
                cursor.execute(Sql.UPDATE_CONFIG,
                               dict(key=Gconf.Key.PageRangeRules,
                                    value=name))
                for i, record in enumerate(cursor.execute(
                        Sql.UNORDERED_PAGES)):
                    percent = int(min(100, i * 100 // total))
                    if percent not in percents: # report every 1% done
                        if reportProgress is not None:
                            reportProgress("{} {}%".format(prefix, percent))
                        percents.add(percent)
                    eid = record[0]
                    pages = record[1]
                    if pages is not None:
                        try:
                            pages = Pages.sortedPages(pages, pageRange)
                            subcursor = self.db.cursor()
                            subcursor.execute(Sql.UPDATE_PAGES,
                                              dict(pages=pages, eid=eid))
                        except Pages.Error as err:
                            logging.error("Xix.setPageRangeRules failed: {}"
                                          .format(err))
        self._cache_clear()
