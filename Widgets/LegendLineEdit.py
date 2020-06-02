#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.
# Copied from dcb1

from PySide.QtCore import Qt
from PySide.QtGui import QLineEdit, QPainter


class LineEdit(QLineEdit):

    def __init__(self, legend, parent=None):
        super().__init__(parent)
        self.legend = legend


    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.text().strip():
            fm = self.fontMetrics()
            painter = QPainter(self)
            painter.setRenderHint(QPainter.TextAntialiasing)
            painter.setPen(Qt.lightGray)
            painter.drawText(fm.width("n"), fm.height(), self.legend)


    def focusInEvent(self, event):
        self.selectAll()
        super().focusInEvent(event)
