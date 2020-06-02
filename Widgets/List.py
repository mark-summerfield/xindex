#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import QRect, QSize, Qt
from PySide.QtGui import (
    QComboBox, QFont, QLabel, QListWidget, QPalette, QPixmap, QStyle,
    QStyledItemDelegate, QStyleOptionComboBox, QStylePainter, QWidget)

import Lib


class HtmlDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel()
        self.label.setTextFormat(Qt.RichText)
        self.label.setWordWrap(False)


    def paint(self, painter, option, index):
        selected = bool(int(option.state) & int(QStyle.State_Selected))
        palette = option.palette
        bg = (palette.highlight().color() if selected else
              palette.base().color())
        fg = (palette.highlightedText().color() if selected else
              palette.text().color())
        palette.setColor(QPalette.Active, QPalette.Window, bg)
        palette.setColor(QPalette.Active, QPalette.WindowText, fg)
        self.label.setPalette(palette)
        self.label.setFixedSize(option.rect.width(), option.rect.height())
        self.label.setText(index.model().data(index))
        pixmap = QPixmap(self.label.size())
        self.label.render(pixmap)
        painter.drawPixmap(option.rect, pixmap)


    def sizeHint(self, option, index):
        text = Lib.htmlToPlainText(index.model().data(index)) + "WW"
        return QSize(option.fontMetrics.width(text),
                     option.fontMetrics.height())


class HtmlListWidget(QListWidget):

    def __init__(self, state, minLines=4, parent=None):
        super().__init__(parent)
        self.state = state
        self.minLines = minLines + 1 # To allow for the horizontal scrollbar
        self.updateDisplayFonts()
        self.setItemDelegate(HtmlDelegate())


    def minimumSizeHint(self):
        size = self.sizeHint()
        height = self.fontMetrics().height() * self.minLines
        return QSize(size.width(), height)


    def sizeHint(self):
        size = super().minimumSizeHint()
        width = 0
        for i in range(self.count()):
            text = Lib.htmlToPlainText(self.item(i).text())
            w = self.fontMetrics().width(text)
            if w > width:
                width = w
        return QSize(width + self.fontMetrics().width("WW"), size.height())


    def updateDisplayFonts(self):
        self.setFont(QFont(self.state.stdFontFamily,
                           self.state.stdFontSize))


class HtmlComboBox(QComboBox):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.updateDisplayFonts()
        self.label = QLabel()
        self.label.setTextFormat(Qt.RichText)
        self.setEditable(False)
        self.setItemDelegate(HtmlDelegate())


    def updateDisplayFonts(self):
        self.setFont(QFont(self.state.stdFontFamily,
                           self.state.stdFontSize))


    def minimumSizeHint(self):
        return self.sizeHint()


    def sizeHint(self):
        size = super().minimumSizeHint()
        width = 0
        for i in range(self.count()):
            text = Lib.htmlToPlainText(self.itemText(i))
            w = self.fontMetrics().width(text)
            if w > width:
                width = w
        width += self.fontMetrics().width("W" * 3)
        return QSize(width, size.height())


    def paintEvent(self, event):
        painter = QStylePainter(self)
        painter.setPen(self.palette().color(QPalette.Text))
        # Draw the combobox frame, focus rect, selected etc.
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        opt.currentText = "" # Don't draw the raw HTML
        painter.drawComplexControl(QStyle.CC_ComboBox, opt)
        # Draw the icon and text
        painter.drawControl(QStyle.CE_ComboBoxLabel, opt)
        # Draw the HTML
        self.label.setText(self.currentText())
        self.label.adjustSize()
        pixmap = QPixmap(self.label.width(), self.label.height())
        pixmap.fill(Qt.transparent)
        self.label.render(pixmap, renderFlags=QWidget.RenderFlags(0))
        rect = QRect(opt.rect)
        y = (rect.height() - self.label.height()) / 2
        rect.setX(self.fontMetrics().width("n"))
        rect.setY(y)
        rect.setHeight(pixmap.height())
        rect.setWidth(pixmap.width())
        painter.drawPixmap(rect, pixmap, pixmap.rect())
