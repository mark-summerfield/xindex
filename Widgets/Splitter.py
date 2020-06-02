#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Qt
from PySide.QtGui import QPainter, QPen, QSplitter, QSplitterHandle


class Splitter(QSplitter):

    def createHandle(self):
        return SplitterHandle(self.orientation(), self)


class SplitterHandle(QSplitterHandle):

    def paintEvent(self, event):
        rect = self.rect()
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.darkGreen, 0, Qt.DotLine))

        if self.orientation() == Qt.Horizontal:
            # Visually vertical
            offset = round(rect.height() * 0.05)
            x = rect.x() + (rect.width() / 2)
            y = rect.y() + offset
            painter.drawLine(x, y, x, rect.height() - offset)
        else:
            # Visually horizontal
            offset = round(rect.width() * 0.05)
            y = rect.y() + (rect.height() / 2)
            painter.drawLine(offset, y, rect.width() - offset, y)
