#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import string

from PySide.QtCore import Qt
from PySide.QtGui import QApplication

from Config import Gconf
import Lib
from Const import (
    EntryDataKind, FilterKind, MAIN_INDICATOR, ROOT, SUB_INDICATOR,
    UNLIMITED)
from .Base import AbstractView


FIND_BG = """qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
    stop: 0 #FFDDFF, stop: 1 #FF55FF);""" # Magenta


class View(AbstractView):

    def __init__(self, state, parent=None):
        super().__init__(state, parent)
        self.clear()
        self.pane.doubleClickLine.connect(self.gotoLino)


    def clear(self):
        self.filter = FilterKind.TERMS_MATCHING
        self.match = ""
        super().clear()


    def query(self, filter, match=""):
        self.filter = filter
        if self.filter is FilterKind.TOO_HIGH_PAGE:
            self.match = self.state.model.config(
                Gconf.Key.HighestPageNumber,
                Gconf.Default.HighestPageNumber)
        elif self.filter is FilterKind.TOO_LARGE_PAGE_RANGE:
            self.match = self.state.model.config(
                Gconf.Key.LargestPageRange, Gconf.Default.LargestPageRange)
        elif self.filter is FilterKind.TOO_MANY_PAGES:
            self.match = self.state.model.config(Gconf.Key.MostPages,
                                                 Gconf.Default.MostPages)
        else:
            self.match = match
        self.refresh(selectFirst=True)


    def gotoEid(self, eid):
        found = False
        if self.state.model.hasEntry(eid):
            for offset, entryEid in enumerate(
                self.state.model.filteredEntries(
                    filter=self.filter, match=self.match, offset=0,
                    limit=UNLIMITED, entryData=EntryDataKind.EID)):
                if eid == entryEid:
                    halfPage = self.scrollbar.pageStep() // 2
                    if offset > halfPage: # Keep some context
                        offset -= halfPage
                    else:
                        offset = 0
                    with Lib.BlockSignals(self.scrollbar):
                        self.scrollbar.setValue(offset)
                    self.selectedLino = None
                    self.selectedEid = eid
                    found = True
                    break
        if found:
            self.refresh()


    def gotoLetter(self, letter):
        found = False
        for offset, eid in enumerate(
            self.state.model.filteredEntries(
                filter=self.filter, match=self.match, offset=0,
                limit=UNLIMITED, entryData=EntryDataKind.EID)):
            term = Lib.htmlToPlainText(self.state.model.term(
                                       eid))[:1].upper()
            if term and term in string.ascii_uppercase and term >= letter:
                halfPage = self.scrollbar.pageStep() // 2
                if offset > halfPage: # Keep some context
                    offset -= halfPage
                else:
                    offset = 0
                with Lib.BlockSignals(self.scrollbar):
                    self.scrollbar.setValue(offset)
                self.selectedLino = None
                self.selectedEid = eid
                found = True
                break
        if found:
            self.refresh()


    def count(self):
        total = 0
        if self.filter in {FilterKind.TERMS_MATCHING,
                           FilterKind.NOTES_MATCHING,
                           FilterKind.ENTRIES_WITH_PAGES,
                           FilterKind.IN_NORMAL_GROUP,
                           FilterKind.IN_LINKED_GROUP,
                           FilterKind.PAGES_ORDER,
                           FilterKind.TOO_HIGH_PAGE,
                           FilterKind.TOO_LARGE_PAGE_RANGE,
                           FilterKind.TOO_MANY_PAGES}:
            total = self.state.model.filteredCount(self.match, self.filter)
        else:
            total = self.state.model.count(self.filter)
        return total


    def refresh(self, *, selectFirst=False):
        if self.busy:
            return
        self.busy = True
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.state.window.reportProgress("Filtering…")
            self.cache.clear()
            self.pane.clear()
            if not self.state.model:
                self.refreshed.emit()
                return
            total = self.count()
            self.state.window.updateIndicatorCounts()
            if not total:
                self.scrollbar.setMaximum(0)
                self.refreshed.emit()
                return
            with Lib.Timer("Filtered in", 0.2):
                lines = self.pane.maxVisibleLines
                self.scrollbar.setMaximum(total)
                self.scrollbar.setPageStep(lines - 1) # Keep some context
                if selectFirst:
                    self.scrollbar.setValue(0)
                offset = self.scrollbar.value()
                limit = min(lines, total)
                for lino, entry in enumerate(
                        self.state.model.filteredEntries(
                            filter=self.filter, match=self.match,
                            offset=offset, limit=limit,
                            entryData=EntryDataKind.ALL_DATA_AND_XREF)):
                    if lino == lines:
                        break
                    if lino == 0 and selectFirst:
                        self.selectedLino = 0
                        self.selectedEid = entry.eid
                    elif self.selectedLino is None:
                        if entry.eid == self.selectedEid:
                            self.selectedLino = lino
                        elif lino == lines:
                            self.selectedLino = lino
                            self.selectedEid = entry.eid
                    html = self.htmlForEntry(entry, self.prefix(entry))
                    self.cache.append((entry.eid, html))
                    self.pane.appendHtml(self.styledHtml(html, lino,
                                         entry.eid))
                self.pane.unscroll()
            if not self.selectedEid or self.selectedLino is None:
                self.selectedLino = 0
                self.busy = False
                try:
                    self.refreshFromCache()
                finally:
                    self.busy = True
            else:
                self.refreshed.emit()
            self.selectedEidChanged.emit(self.selectedEid)
        finally:
            QApplication.restoreOverrideCursor()
            self.state.updateNavigationStatus()
            self.busy = False


    def prefix(self, entry):
        return "{} ".format(MAIN_INDICATOR if entry.peid == ROOT else
                            SUB_INDICATOR)


    def styledHtml(self, html, lino, eid):
        style = None
        char = "\u25A0"
        if lino == self.selectedLino:
            style = FIND_BG
            self.selectedEid = eid
        if style is None:
            return '<font color=transparent>{}</font> {}'.format(char, html)
        return '<span style="background-color: {};">{} {}</span>'.format(
            style, char, html)


    def gotoLino(self, lino):
        for alino, (eid, _) in enumerate(self.cache):
            if alino == lino:
                self.state.window.gotoActions.gotoEid(eid)
                break
