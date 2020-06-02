#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Qt, Signal

import Lib
from Const import CountKind, EntryDataKind, UNLIMITED, WIN
from .Base import AbstractView


SELECTED_BG = """qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
    stop: 0 #FFFFCC, stop: 1 #D0D000);""" # Yellow
CIRCLED_BG = """qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #CCFFFF, stop: 1 #00D0D0);""" # Cyan
CIRCLED_AND_SELECTED_BG = """qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #CCFFCC, stop: 1 #00DD00);""" # Yellow + Cyan = Green


class View(AbstractView):

    circledEidChanged = Signal(int)

    def __init__(self, state, parent=None):
        super().__init__(state, parent)
        self.methodForKeyPress[Qt.Key_Space] = self.circle
        self.clear()


    def clear(self):
        self.circledEid = None
        super().clear()


    def createConnections(self):
        super().createConnections()
        self.pane.doubleClickLine.connect(self.setCircledLino)


    def setCircledLino(self, lino):
        oldEid = self.circledEid
        newEid = None
        for alino, (eid, html) in enumerate(self.cache):
            if alino == lino:
                newEid = eid
                break
        self._toggleCircled(oldEid, newEid)


    def circle(self, ctrl=False):
        oldEid = self.circledEid
        self._toggleCircled(oldEid, self.selectedEid)


    def _toggleCircled(self, oldEid, newEid):
        if oldEid == newEid:
            self.circledEid = None
            eid = oldEid
        else:
            eid = self.circledEid = newEid
        self.refreshFromCache()
        self.circledEidChanged.emit(eid)


    def gotoEid(self, eid):
        if self.state.model.hasEntry(eid):
            for offset, (indent, entryEid) in enumerate(
                    self.state.model.entries(offset=0, limit=UNLIMITED)):
                if entryEid == eid:
                    halfPage = self.scrollbar.pageStep() // 2
                    if offset > halfPage: # Keep some context
                        offset -= halfPage
                    else:
                        offset = 0
                    with Lib.BlockSignals(self.scrollbar):
                        self.scrollbar.setValue(offset)
                    self.selectedLino = None
                    self.selectedEid = eid
                    break
        self.refresh()


    def gotoLetter(self, letter):
        self.state.window.gotoActions.gotoPrefix(letter)


    def styledHtml(self, html, lino, eid):
        style = None
        char = "\u25CF"
        if eid == self.circledEid and lino == self.selectedLino:
            style = CIRCLED_AND_SELECTED_BG
            char = "\u25C9" if WIN else "\u2299"
        elif eid == self.circledEid:
            style = CIRCLED_BG
            char = "\u25CB"
        elif lino == self.selectedLino:
            style = SELECTED_BG
            self.selectedEid = eid
        if style is None:
            return '<font color=transparent>{}</font> {}'.format(char, html)
        return '<span style="background-color: {};">{} {}</span>'.format(
            style, char, html)


    def refresh(self):
        if self.busy:
            return
        self.busy = True
        try:
            self.cache.clear()
            self.pane.clear()
            if not self.state.model:
                self.refreshed.emit()
                return
            total = self.state.model.count(CountKind.ENTRIES)
            if not total:
                self.refreshed.emit()
                return
            with Lib.Timer("Refreshed in", 0.2):
                lines = self.pane.maxVisibleLines
                self.scrollbar.setMaximum(total)
                self.scrollbar.setPageStep(lines - 1) # Keep some context
                offset = self.scrollbar.value()
                limit = min(lines, total)
                for lino, entry in enumerate(self.state.model.entries(
                    offset=offset, limit=limit,
                        entryData=EntryDataKind.ALL_DATA_AND_XREF)):
                    if lino == lines:
                        break
                    if (self.selectedLino is None and
                            entry.eid == self.selectedEid):
                        self.selectedLino = lino
                    elif lino == lines and self.selectedLino is None:
                        self.selectedLino = lino
                        self.selectedEid = entry.eid
                    html = self.htmlForEntry(entry, self.prefix(entry))
                    self.cache.append((entry.eid, html))
                    self.pane.appendHtml(self.styledHtml(html, lino,
                                         entry.eid))
                self.pane.unscroll()
                self.selectedEidChanged.emit(self.selectedEid)
                self.refreshed.emit()
        finally:
            self.busy = False


    def prefix(self, entry):
        return (4 * entry.indent) * "&nbsp;"
