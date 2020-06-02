#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import string
import unicodedata

from PySide.QtCore import QSize, Qt, Signal
from PySide.QtGui import QFont, QTextCursor, QTextEdit


class LineEdit(QTextEdit):

    lostFocus = Signal()
    wordCompleted = Signal()
    enterPressed = Signal() # Only if allowNewlines is True


    def __init__(self, state, parent=None, *, maxLines=1,
                 allowNewlines=False, formatActions=None):
        super().__init__(parent)
        self.state = state
        self.formatActions = formatActions
        self.maxLines = maxLines
        self.allowNewlines = allowNewlines
        self._multiline = False
        self.setAcceptRichText(False)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setTabChangesFocus(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFont(QFont(self.state.stdFontFamily,
                           self.state.stdFontSize))


    def isEmpty(self):
        return not bool(self.toPlainText().strip())


    def setPlainText(self, text, position=None):
        super().setPlainText(text)
        self._restorePosition(position)


    def _restorePosition(self, position):
        if position is not None:
            chars = self.document().characterCount()
            if position == -1:
                position = chars - 1
            elif position >= chars:
                position = max(0, chars - 1)
            cursor = self.textCursor()
            cursor.setPosition(position)
            self.setTextCursor(cursor)


    def wordAndPosition(self):
        pos = self.textCursor().position()
        text = self.toPlainText()
        before = text[:pos]
        after = text[pos:].rstrip()
        word = None
        endOfLineOrWord = not after or after != after.lstrip()
        atEndOfWord = before and before == before.rstrip()
        if endOfLineOrWord and atEndOfWord:
            word = before.split()[-1]
        return word, pos


    def setFont(self, font):
        super().setFont(font)
        fm = self.fontMetrics()
        h = round(fm.height() * 1.5)
        self.setMinimumHeight(h)
        if self.maxLines is not None:
            self.setMaximumHeight(h * self.maxLines)


    def updateDisplayFonts(self):
        self.setFont(QFont(self.state.stdFontFamily,
                           self.state.stdFontSize))


    def sizeHint(self):
        return QSize(self.document().idealWidth() + 5,
                     self.maximumHeight())


    def minimumSizeHint(self):
        return QSize(self.fontMetrics().width("W" * 15),
                     self.minimumHeight())


    def keyPressEvent(self, event):
        key = event.key()
        if not self.allowNewlines and key in {Qt.Key_Enter,
                                              Qt.Key_Return}:
            self.enterPressed.emit()
            event.ignore()
            return
        done = False
        ctrl = bool(int(event.modifiers()) & int(Qt.ControlModifier))
        if ctrl and key in {Qt.Key_Home, Qt.Key_End, Qt.Key_PageUp,
                            Qt.Key_PageDown}:
            if key == Qt.Key_Home:
                self.state.viewAllPanel.view.goHome()
            elif key == Qt.Key_End:
                self.state.viewAllPanel.view.goEnd()
            elif key == Qt.Key_PageUp:
                self.state.viewAllPanel.view.goPageUp()
            elif key == Qt.Key_PageDown:
                self.state.viewAllPanel.view.goPageDown()
            done = True
        if key in {Qt.Key_Apostrophe, Qt.Key_QuoteDbl}:
            self.insertPlainText(self.quoteForQuote(key))
            done = True
        if done:
            event.ignore()
            return
        super().keyPressEvent(event)


    def quoteForQuote(self, quote):
        openQuote = False
        cursor = self.textCursor()
        if cursor.atStart() or cursor.atBlockStart():
            openQuote = True
        else:
            cursor.clearSelection()
            cursor.setPosition(cursor.position() - 1,
                               QTextCursor.KeepAnchor)
            if is_whitespace(cursor.selectedText()):
                openQuote = True
        if openQuote:
            if quote == Qt.Key_Apostrophe:
                q = "\u2018" # ‘
            else:
                q = "\u201C" # “
        else:
            if quote == Qt.Key_Apostrophe:
                q = "\u2019" # ’
            else:
                q = "\u201D" # ”
        return q


    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if event.reason() not in {Qt.PopupFocusReason,
                                  Qt.MenuBarFocusReason,
                                  Qt.ActiveWindowFocusReason}:
            if self.state.window is not None:
                if self.formatActions is None:
                    self.formatActions = self.state.window.formatActions
                if self.formatActions is not None:
                    self.formatActions.updateEnabled()
            self.lostFocus.emit()


    def insertFromMimeData(self, mimeData):
        if (not self._multiline and not mimeData.hasHtml() and
                mimeData.hasText()):
            self.insertPlainText(mimeData.text().replace("\n", " ").strip())
        else:
            super().insertFromMimeData(mimeData)


def is_whitespace(c):
    return c in string.whitespace or unicodedata.category(c) in {"Zl", "Zp",
                                                                 "Zs"}
