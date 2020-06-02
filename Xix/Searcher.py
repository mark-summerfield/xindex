#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import collections

import HtmlReplacer
from Const import EntryDataKind, SearchFieldKind


Match = collections.namedtuple("Match", "eid field text start end")


class Finished(Exception):
    pass


class Searcher:

    def __init__(self, reportProgress):
        self.reportProgress = reportProgress
        self._initialize()


    def _initialize(self, model=None, options=None, *, running=False):
        self.model = model
        self.options = options
        self.total = 1
        self.running = running
        self.percents = set()
        self.start = 0
        self.entry = None
        self.field = None
        self.eids = []
        self.eidIndex = None
        self.replacer = None


    def prepare(self, model, options):
        self._initialize(model, options, running=True)
        if self.options.filter is None: # All entries
            self.eids = [eid for indent, eid in self.model.entries()]
        else: # Filtered entries
            self.eids = list(self.model.filteredEntries(
                filter=self.options.filter, match=self.options.match,
                entryData=EntryDataKind.EID))
        self.total = max(1, len(self.eids))
        self.eidIndex = 0 if len(self.eids) else None


    def stop(self):
        self.running = False


    def search(self):
        try:
            while True:
                self._checkProgress()
                if self.entry is None:
                    self._nextEntry()
                if self.field is None:
                    self._nextField()
                    if self.field is None:
                        continue
                match = self._searchField()
                if match is None:
                    self._nextField()
                else:
                    return match
        except Finished:
            self._initialize()
            # return None # No (more) found or user canceled


    def _checkProgress(self):
        percent = (100 if self.eidIndex is None else # Shouldn't happen
                   int(min(100, self.eidIndex * 100 // self.total)))
        if percent not in self.percents: # report every 1% done
            self.reportProgress("Searching {}%".format(percent))
            self.percents.add(percent)
            if not self.running:
                raise Finished()


    def _nextEntry(self):
        if self.eidIndex is None or self.eidIndex >= len(self.eids):
            raise Finished() # No (more) found
        self.entry = self.model.entry(self.eids[self.eidIndex])
        if self.entry is None:
            raise Finished() # No (more) found
        self.eidIndex += 1
        self.field = None


    def _nextField(self):
        self.start = 0
        self.replacer = HtmlReplacer.Replacer(
            pattern=self.options.pattern, literal=self.options.literal,
            replacement=self.options.replacement,
            wholewords=self.options.wholewords,
            ignorecase=self.options.ignorecase)
        if self.field is None and self.options.terms:
            self.field = SearchFieldKind.TERM
            return
        if self.field is None or self.field is SearchFieldKind.TERM:
            if self.options.pages:
                self.field = SearchFieldKind.PAGES
                return
            elif self.options.notes:
                self.field = SearchFieldKind.NOTES
                return
        if self.field is SearchFieldKind.PAGES and self.options.notes:
            self.field = SearchFieldKind.NOTES
            return
        self.field = None
        self.entry = None


    def _searchField(self):
        self.entry = self.model.entry(self.entry.eid) # Refresh
        text = None
        if self.field is SearchFieldKind.TERM:
            text = self.entry.term
        elif self.field is SearchFieldKind.PAGES:
            text = self.entry.pages
        elif self.field is SearchFieldKind.NOTES:
            text = self.entry.notes
        self.replacer.setHtml(text, self.start)
        paraMatch = self.replacer.search()
        if paraMatch is not None:
            self.start = paraMatch.start + 1
            return Match(self.entry.eid, self.field, paraMatch.text,
                         paraMatch.start, paraMatch.end)
        # return None # No match found
