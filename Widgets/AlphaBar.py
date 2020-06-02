#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import string

from PySide.QtCore import QRectF, QSize, Qt, QTimer, Signal
from PySide.QtGui import (
    QApplication, QFont, QMainWindow, QPainter, QPen, QSizePolicy,
    QToolBar)

if __name__ == "__main__":
    clamp = lambda mn, va, mx: mn if va < mn else mx if va > mx else va
else:
    from Lib import clamp


H_GAP_PC = 1.5
V_GAP_PC = 1.25
HANDLE_OFFSET = 8
X_OFFSET = 2


class Bar(QToolBar):

    clicked = Signal(str)

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(parent)
        self.setOrientation(orientation)
        policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed,
                             QSizePolicy.ButtonBox)
        policy.setHeightForWidth(True)
        policy.setWidthForHeight(True)
        self.setSizePolicy(policy)
        self.setFloatable(False)
        self.setToolTip("""<p><b>Goto Letter</b></p>
<p>Left-click a letter to navigate to the first entry starting with that
letter.</p>
<p>Right-click a letter to navigate to the first entry starting with the
most recently left-clicked letter, plus any subsequent right-clicked
letters, and this letter.</p>
<p>(One left-click or a fifth right-click clears the previous letters.)</p>
<p>For example, left-click <i>S</i> to go to the first “s” entry. Then
right-click <i>A</i> to go to the first “sa” entry, then right-click
<i>T</i> to go to the first “sat” entry.</p>""")
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.onTimeout)
        size = self.font().pointSizeF()
        strategy = QFont.StyleStrategy(QFont.PreferOutline |
                                       QFont.PreferAntialias |
                                       QFont.PreferQuality)
        self.mainFont = QFont("courier new")
        self.mainFont.setFixedPitch(True)
        self.mainFont.setStyleStrategy(strategy)
        self.mainFont.setStyleHint(QFont.Monospace)
        self.mainFont.setPointSizeF(size * 1.5)
        self.mainFont.setBold(True)
        self.mainFont.setItalic(False)
        self.setFont(self.mainFont)
        self.smallFont = QFont("helvetica")
        self.smallFont.setStyleStrategy(strategy)
        self.smallFont.setStyleHint(QFont.Times)
        self.smallFont.setPointSizeF(size * 1.25)
        self.smallFont.setBold(False)
        self.smallFont.setItalic(False)
        self.letters = string.ascii_uppercase
        self.word = None


    def sizeHint(self):
        return self.minimumSizeHint()


    def minimumSizeHint(self):
        count = len(self.letters)
        widthAll = self.fontMetrics().width(self.letters) * H_GAP_PC
        widthW = self.fontMetrics().width("WW")
        heightOne = self.fontMetrics().height()
        if self.orientation == Qt.Vertical:
            return QSize(widthW, (heightOne * count) + HANDLE_OFFSET)
        return QSize(widthAll + HANDLE_OFFSET, heightOne * V_GAP_PC)


    def paintEvent(self, event):
        super().paintEvent(event)
        letterPen = QPen(Qt.darkGreen if self.isEnabled() else Qt.lightGray)
        wordPen = QPen(Qt.darkCyan if self.isEnabled() else Qt.lightGray)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.TextAntialiasing)
        painter.setPen(letterPen)
        heightOne = self.fontMetrics().height()
        widthOne = self.fontMetrics().width("W")
        if self.orientation == Qt.Vertical:
            y = HANDLE_OFFSET
            for c in self.letters:
                rect = QRectF(X_OFFSET, y, widthOne, heightOne)
                painter.drawText(rect, Qt.AlignCenter, c)
                y += heightOne
            if self.word is not None:
                painter.setFont(self.smallFont)
                painter.setPen(wordPen)
                rect = self.rect().adjusted(0, HANDLE_OFFSET,
                                            -widthOne / 3, 0)
                painter.drawText(rect, Qt.AlignTop | Qt.AlignRight |
                                 Qt.TextWordWrap,
                                 "\n".join(self.word.lower()))
                painter.setPen(letterPen)
                painter.setFont(self.mainFont)
        else:
            widthOne *= H_GAP_PC
            x = HANDLE_OFFSET
            for c in self.letters:
                rect = QRectF(x, 0, widthOne, heightOne * V_GAP_PC)
                painter.drawText(rect, Qt.AlignCenter, c)
                x += widthOne
            if self.word is not None:
                painter.setFont(self.smallFont)
                painter.setPen(wordPen)
                rect = self.rect().adjusted(HANDLE_OFFSET, 0, 0, 0)
                painter.drawText(rect, Qt.AlignBottom | Qt.AlignLeft,
                                 self.word.lower())
                painter.setPen(letterPen)
                painter.setFont(self.mainFont)


    def mousePressEvent(self, event):
        if self.orientation == Qt.Vertical:
            if event.y() < HANDLE_OFFSET:
                event.ignore()
                return
            heightOne = self.fontMetrics().height()
            i = clamp(0, int((event.y() - HANDLE_OFFSET) / heightOne),
                      len(self.letters) - 1)
        else:
            if event.x() < HANDLE_OFFSET:
                event.ignore()
                return
            widthOne = self.fontMetrics().width("W") * H_GAP_PC
            i = clamp(0, int((event.x() - HANDLE_OFFSET) / widthOne),
                      len(self.letters) - 1)
        event.accept()
        word = self.letters[i]
        if event.button() == Qt.LeftButton or self.word is None:
            self.word = word
        elif event.button() == Qt.RightButton:
            if len(self.word) >= 4:
                self.word = word
            elif self.word is not None:
                self.word += word
        if self.word is not None:
            self.clicked.emit(self.word.lower())
            self.timer.start(10000)
        self.update()


    def contextMenuEvent(self, event):
        if ((self.orientation == Qt.Vertical and
                event.y() < HANDLE_OFFSET) or
                (self.orientation == Qt.Horizontal and
                    event.x() < HANDLE_OFFSET)):
            event.ignore()
        else:
            event.accept()


    def setOrientation(self, orientation):
        self.orientation = orientation
        self.update()


    def heightForWidth(self, width):
        count = len(self.letters)
        heightOne = self.fontMetrics().height()
        widthAll = self.fontMetrics().width(self.letters) * H_GAP_PC
        if widthAll > width: # Needs to be vertical
            return heightOne * count
        return heightOne * V_GAP_PC # Needs to be horizontal


    def onTimeout(self):
        self.timer.stop()
        if self.word is not None:
            self.word = None
            self.update()


if __name__ == "__main__":
    app = QApplication([])
    win = QMainWindow()
    def clickedBar(x):
        print(("clicked", x))
    bar = Bar()
    bar.clicked.connect(clickedBar)
    tb = win.addToolBar("Tools")
    tb.addWidget(bar)
    tb.setFloatable(False)
    tb.orientationChanged.connect(bar.setOrientation)
    win.show()
    app.exec_()
