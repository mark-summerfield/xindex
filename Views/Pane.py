#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Qt, Signal
from PySide.QtGui import QFrame, QPlainTextEdit, QTextCursor

from Const import WIN


class Pane(QPlainTextEdit):

    clickLine = Signal(int)
    ctrlClickLine = Signal(int)
    doubleClickLine = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setTabChangesFocus(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.NoFocus)
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)
        self.setBackgroundVisible(True)
        self.viewport().setCursor(Qt.ArrowCursor)


    def mousePressEvent(self, event):
        cursor = self.cursorForPosition(event.pos())
        lino = cursor.blockNumber()
        if event.button() == Qt.LeftButton: # Save right click for poss.
            if event.modifiers() & Qt.ControlModifier: # context menu
                self.ctrlClickLine.emit(lino)
            else:
                self.clickLine.emit(lino)
            event.accept()


    def mouseDoubleClickEvent(self, event):
        cursor = self.cursorForPosition(event.pos())
        lino = cursor.blockNumber()
        self.doubleClickLine.emit(lino)
        event.accept()


    @property
    def maxVisibleLines(self):
        height = self.viewport().height()
        fm = self.fontMetrics()
        lineHeight = fm.lineSpacing() + fm.leading()
        lines, remainder = divmod(height, lineHeight)
        if WIN:
            lines = 1 + (height // lineHeight)
        else:
            lines = (height // lineHeight) - round(remainder / lineHeight)
        return lines


    def gotoLastLine(self):
        cursor = self.textCursor()
        if not cursor.atEnd():
            cursor.movePosition(QTextCursor.End)
            self.setTextCursor(cursor)
            self.ensureCursorVisible()
            lino = cursor.blockNumber()
            self.clickLine.emit(lino)


    def unscroll(self):
        self.moveCursor(QTextCursor.Start)
        self.ensureCursorVisible()
