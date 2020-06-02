#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import string

from PySide.QtCore import Qt, QTimer, Signal
from PySide.QtGui import (
    QFont, QHBoxLayout, QPalette, QScrollBar, QVBoxLayout, QWidget)

import Lib
from .Pane import Pane
from Config import Gconf
from Const import ModeKind, XREF_INDICATOR


class AbstractView(QWidget):

    selectedEidChanged = Signal(int)
    clickedEid = Signal(int)
    refreshed = Signal()

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.state = state
        self.clear()
        self.methodForKeyPress = self.mapMethodToKeyPress()
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.setFocusPolicy(Qt.WheelFocus)
        QTimer.singleShot(250, lambda: self._setBackgroundColor(False))


    def focusInEvent(self, event):
        self._setBackgroundColor(True)
        super().focusInEvent(event)


    def focusOutEvent(self, event):
        self._setBackgroundColor(False)
        super().focusOutEvent(event)


    def _setBackgroundColor(self, hasFocus):
        if hasFocus:
            brush = self.palette().base()
        else:
            brush = self.palette().alternateBase()
        palette = self.pane.palette()
        palette.setBrush(QPalette.Base, brush)
        self.pane.viewport().setPalette(palette)


    def clear(self):
        self.selectedEid = None
        self.selectedLino = 0
        self.busy = False
        self.cache = []


    def mapMethodToKeyPress(self):
        return {
            Qt.Key_Home: self.goHome,
            Qt.Key_End: self.goEnd,
            Qt.Key_Up: self.goUp,
            Qt.Key_Down: self.goDown,
            Qt.Key_PageUp: self.goPageUp,
            Qt.Key_PageDown: self.goPageDown,
            Qt.Key_Left: self.goLeft,
            Qt.Key_Right: self.goRight,
            }


    def createWidgets(self):
        self.pane = Pane(self)
        self.pane.setFont(QFont(self.state.stdFontFamily,
                                self.state.stdFontSize))
        self.scrollbar = QScrollBar(Qt.Vertical)
        self.scrollbar.setRange(0, 0)
        self.scrollbar.setValue(0)
        self.scrollbar.setFocusPolicy(Qt.NoFocus)
        size = self.pane.fontMetrics().height()
        self.square = QWidget() # Could be used as an indicator?
        self.square.setMaximumSize(size, size)
        self.square.setContentsMargins(0, 0, 0, 0)


    def layoutWidgets(self):
        layout = QHBoxLayout()
        layout.addWidget(self.pane, 1)
        vbox = QVBoxLayout()
        vbox.addWidget(self.scrollbar)
        vbox.addWidget(self.square)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(vbox)
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)


    def createConnections(self):
        self.state.model.loaded.connect(self.refresh)
        self.state.model.changed.connect(self.gotoEid)
        self.scrollbar.valueChanged.connect(self.refresh)
        self.pane.clickLine.connect(self.clickSelectedLino)


    def updateUi(self):
        enable = self.state.mode not in {ModeKind.NO_INDEX, ModeKind.CHANGE}
        self.setEnabled(enable)


    def updateDisplayFonts(self):
        self.pane.setFont(QFont(self.state.stdFontFamily,
                                self.state.stdFontSize))
        self.refresh()


    def gotoEid(self, eid):
        raise NotImplementedError


    def refresh(self):
        raise NotImplementedError


    def refreshFromCache(self):
        if self.busy:
            return
        self.busy = True
        try:
            self.pane.clear()
            selectedChanged = False
            for lino, (eid, html) in enumerate(self.cache):
                if lino == self.selectedLino and eid != self.selectedEid:
                    self.selectedEid = eid
                    selectedChanged = True
                self.pane.appendHtml(self.styledHtml(html, lino, eid))
            self.pane.unscroll()
            self.refreshed.emit()
            if selectedChanged:
                self.selectedEidChanged.emit(self.selectedEid)
        finally:
            self.busy = False


    @property
    def lineCount(self):
        return len(self.cache)


    def updateCache(self, entry):
        changed = False
        for i in range(len(self.cache)):
            if self.cache[i][0] == entry.eid:
                html = self.htmlForEntry(entry, self.prefix(entry))
                self.cache[i] = (entry.eid, html)
                changed = True
                break
        if changed:
            self.refreshFromCache()


    def prefix(self, entry):
        raise NotImplementedError


    def htmlForEntry(self, entry, prefix):
        patcher = lambda match: Lib.patchFont(
            match, self.state.stdFontFamily, self.state.stdFontSize,
            self.state.altFontFamily, self.state.altFontSize,
            self.state.monoFontFamily, self.state.monoFontSize)
        pages = ""
        if entry.pages:
            if not bool(self.state.model):
                sep = ", "
            else:
                sep = self.state.model.config(Gconf.Key.TermPagesSeparator,
                                              ", ")
            pages = "{}{}".format(sep, entry.pages)
        xref = ""
        if entry.xrefCount:
            xref = " {} …".format(XREF_INDICATOR * entry.xrefCount)
        text = "{}{}{}{}".format(prefix, entry.term, pages, xref)
        return Lib.PATCH_FONT_RX.sub(patcher, text)


    def styledHtml(self, html, lino, eid):
        return NotImplementedError


    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.state.model:
            self.refresh()


    def clickSelectedLino(self, lino):
        if lino != self.selectedLino and self.cache and self.cache[lino]:
            oldEid = self.selectedEid
            self.selectedLino = lino
            eid = self.cache[lino][0]
            self.gotoEidInCache(eid)
            self.clickedEid.emit(oldEid) # Maintain goto EIDs list


    def gotoEidInCache(self, eid):
        for lino, (ceid, _) in enumerate(self.cache):
            if ceid == eid:
                oldEid = self.selectedEid
                self.selectedLino = lino
                self.refreshFromCache()
                if oldEid != self.selectedEid:
                    self.selectedEidChanged.emit(self.selectedEid)
                return True
        return False


    def setSelectedLino(self, lino):
        if lino != self.selectedLino:
            oldEid = self.selectedEid
            self.selectedLino = lino
            self.refreshFromCache()
            if oldEid != self.selectedEid:
                self.selectedEidChanged.emit(self.selectedEid)


    def keyPressEvent(self, event):
        if self.state.model:
            method = self.methodForKeyPress.get(event.key())
            if method is not None:
                method(bool(int(event.modifiers()) &
                            int(Qt.ControlModifier)))
                event.ignore() # We've handled it
                return
            letter = event.text().upper()
            if letter and letter in string.ascii_uppercase:
                self.gotoLetter(letter)
        super().keyPressEvent(event)


    def goUp(self, ctrl=False):
        if not self.cache:
            return
        if self.selectedLino <= 0: # Scroll
            overlap = self.scrollbar.pageStep() // 3
            offset = self.scrollbar.value() - overlap
            if offset > 0:
                self.scrollbar.setValue(offset)
                self.setSelectedLino(overlap - 1)
            else:
                self.scrollbar.setValue(0)
                self.setSelectedLino(0)
        else: # Move highlight
            self.selectedLino -= 1
            self.refreshFromCache()
            self.selectedEidChanged.emit(self.selectedEid)


    def goDown(self, ctrl=False):
        if not self.cache:
            return
        if self._onLastLine:
            self.setSelectedLino(self.lineCount - 1)
            return
        lino = self.selectedLino + 1
        if lino < self.lineCount:
            self.setSelectedLino(lino)
        else:
            lines = max(1, self.scrollbar.pageStep() // 3)
            offset = self.scrollbar.value() + lines
            if offset > self.scrollbar.maximum():
                lines = ((self.scrollbar.maximum() - self.scrollbar.value()
                          ) // 2)
                offset = self.scrollbar.value() + lines
            with Lib.BlockSignals(self.scrollbar):
                self.scrollbar.setValue(offset)
            excess = 1 if lines == offset else 0
            self.selectedLino = self.lineCount - lines + excess
            self.selectedEid = None
            self.refresh()


    def goPageUp(self, ctrl=False):
        if not self.cache:
            return
        if ctrl: # Top of Page
            self.setSelectedLino(0)
        else: # Page Up
            offset = self.scrollbar.value() - self.scrollbar.pageStep()
            if offset < 0:
                offset = 0
            self.scrollbar.setValue(offset)


    def goPageDown(self, ctrl=False):
        if not self.cache:
            return
        if ctrl: # Bottom of Page
            self.pane.gotoLastLine()
        else: # Page Down
            offset = self.scrollbar.value() + self.scrollbar.pageStep()
            if offset < self.scrollbar.maximum():
                self.scrollbar.setValue(offset)
            else:
                self.pane.gotoLastLine()


    def goHome(self, ctrl=False):
        if not self.cache:
            return
        self.selectedLino = 0
        with Lib.BlockSignals(self.scrollbar):
            self.scrollbar.setValue(0)
        self.refresh()


    def goEnd(self, ctrl=False):
        if not self.cache:
            return
        if self._onLastLine:
            pass
        elif self._onLastPage:
            self.setSelectedLino(self.lineCount - 1)
        else:
            offset = self.scrollbar.maximum() - self.lineCount + 1
            self.scrollbar.setValue(offset)
            self.pane.gotoLastLine()


    def goLeft(self, ctrl=False):
        if not self.cache:
            return
        self._goLeftOrRight(-1)


    def goRight(self, ctrl=False):
        if not self.cache:
            return
        self._goLeftOrRight(1)


    def _goLeftOrRight(self, sign):
        scrollbar = self.pane.horizontalScrollBar()
        step = (scrollbar.pageStep() // 4) * sign
        scrollbar.setValue(Lib.clamp(0, scrollbar.value() + step,
                           scrollbar.maximum()))


    def gotoLetter(self, letter):
        raise NotImplementedError


    def wheelEvent(self, event):
        if not self.cache:
            return
        offset = (self.scrollbar.pageStep() *
                  (1 if event.delta() < 0 else -1)) // 2
        offset += self.scrollbar.value()
        self.scrollbar.setValue(Lib.clamp(0, offset,
                                self.scrollbar.maximum()))
        event.ignore()


    @property
    def _onLastPage(self):
        return (self.scrollbar.maximum() - self.scrollbar.value() <=
                self.lineCount)


    @property
    def _onLastLine(self):
        return self._onLastPage and self.selectedLino == self.lineCount - 1
