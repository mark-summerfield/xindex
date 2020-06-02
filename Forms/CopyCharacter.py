#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unicodedata

from PySide.QtCore import QSettings, QSize, Qt, Signal
from PySide.QtGui import (
    QApplication, QClipboard, QComboBox, QDialog, QDialogButtonBox,
    QFont, QFontComboBox, QFontDatabase, QFontMetrics, QHBoxLayout,
    QIcon, QKeySequence, QLabel, QLineEdit, QPainter, QPushButton,
    QScrollArea, QShortcut, QSizePolicy, QToolTip, QVBoxLayout, QWidget)

import Lib
from Config import Gopt
from Const import say, SAY_TIMEOUT, WIN


SQUARE_SIZE = 32
COLUMNS = 16
MAX_CHAR = 65536


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.setWindowTitle("Copy Character — {}".format(
                            QApplication.applicationName()))
        QShortcut(QKeySequence(QKeySequence.FindNext), self, self.findNext)
        self.state = state
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.findSizes(self.fontComboBox.currentFont())
        self.setToFamily(self.state.stdFontFamily)
        self.setToNearestSize(self.state.stdFontSize)
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        self.fontLabel = QLabel("Fon&t:")
        self.fontComboBox = QFontComboBox()
        self.tooltips.append((self.fontComboBox, """\
<p><b>Font</b></p>
<p>The font for displaying the characters.</p>"""))
        self.fontLabel.setBuddy(self.fontComboBox)
        self.sizeLabel = QLabel("&Size:")
        self.sizeComboBox = QComboBox()
        self.tooltips.append((self.sizeComboBox, """\
<p><b>Size</b></p>
<p>The size of font for displaying the characters.</p>"""))
        self.sizeLabel.setBuddy(self.sizeComboBox)
        self.scrollArea = QScrollArea()
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.panel = Panel()
        self.scrollArea.setWidget(self.panel)
        self.copyTextLabel = QLabel("Copy T&ext")
        self.copyTextLineEdit = QLineEdit()
        self.tooltips.append((self.copyTextLineEdit, """\
<p><b>Copy Text editor</b></p>
<p>The text for copying to the clipboard when <b>Copy</b> is
pressed.</p>"""))
        self.copyTextLabel.setBuddy(self.copyTextLineEdit)
        self.findTextLabel = QLabel("&Find Text")
        self.findTextLineEdit = QLineEdit()
        self.tooltips.append((self.findTextLineEdit, """\
<p><b>Find Text editor</b></p>
<p>The name or partial name of Unicode characters to be found, e.g.,
“star” will match many characters, including U+22C6 “Star
operator”.</p>"""))
        self.findTextLabel.setBuddy(self.findTextLineEdit)
        self.buttonBox = QDialogButtonBox()
        self.addSelectedButton = QPushButton(QIcon(":/add.svg"),
                                             "&Add Selected")
        self.tooltips.append((self.addSelectedButton, """\
<p><b>Add Selected</b></p>
<p>Append the selected character to the <b>Copy Text</b> editor.</p>"""))
        self.buttonBox.addButton(self.addSelectedButton,
                                 QDialogButtonBox.ActionRole)
        self.findNextButton = QPushButton(QIcon(":/edit-find.svg"),
                                          "Find &Next")
        self.tooltips.append((self.findNextButton, """\
<p><b>Find Next</b></p>
<p>Find the next character whose Unicode name contains or equals the
<b>Find Text</b>.</p>"""))
        self.buttonBox.addButton(self.findNextButton,
                                 QDialogButtonBox.ActionRole)
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.tooltips.append((self.helpButton,
                              "Help on the Copy Character dialog"))
        self.buttonBox.addButton(self.helpButton,
                                 QDialogButtonBox.HelpRole)
        self.closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                       "&Close")
        self.tooltips.append((self.closeButton, """<p><b>Cancel</b></p>
<p>Close the dialog.</p>"""))
        self.buttonBox.addButton(self.closeButton,
                                 QDialogButtonBox.RejectRole)


    def layoutWidgets(self):
        topLayout = QHBoxLayout()
        topLayout.addWidget(self.fontLabel)
        topLayout.addWidget(self.fontComboBox, 1)
        topLayout.addWidget(self.sizeLabel)
        topLayout.addWidget(self.sizeComboBox)

        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(self.copyTextLabel)
        bottomLayout.addWidget(self.copyTextLineEdit)
        bottomLayout.addWidget(self.findTextLabel)
        bottomLayout.addWidget(self.findTextLineEdit)

        layout = QVBoxLayout()
        layout.addLayout(topLayout)
        layout.addWidget(self.scrollArea, 1)
        layout.addLayout(bottomLayout)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


    def createConnections(self):
        self.fontComboBox.activated[str].connect(self.panel.updateFont)
        self.sizeComboBox.currentIndexChanged[str].connect(
            self.panel.updateSize)
        self.panel.characterSelected.connect(self.copyTextLineEdit.insert)
        self.panel.fontResized.connect(self.updateSize)
        self.addSelectedButton.clicked.connect(self.addSelected)
        self.helpButton.clicked.connect(self.help)
        self.buttonBox.rejected.connect(self.accept)
        self.findNextButton.clicked.connect(self.findNext)
        self.findTextLineEdit.returnPressed.connect(self.findNext)


    def help(self):
        self.state.help("xix_ref_dlg_copychr.html")


    def findSizes(self, font):
        fontDatabase = QFontDatabase()
        currentSize = self.sizeComboBox.currentText()
        with Lib.BlockSignals(self.sizeComboBox):
            self.sizeComboBox.clear()
            if fontDatabase.isSmoothlyScalable(
                    font.family(), fontDatabase.styleString(font)):
                for size in QFontDatabase.standardSizes():
                    self.sizeComboBox.addItem(str(size))
            else:
                for size in fontDatabase.smoothSizes(
                        font.family(), fontDatabase.styleString(font)):
                    self.sizeComboBox.addItem(str(size))
            self.sizeComboBox.setEditable(False)
        sizeIndex = self.sizeComboBox.findText(currentSize)
        if sizeIndex == -1:
            self.sizeComboBox.setCurrentIndex(
                max(0, self.sizeComboBox.count() / 3))
        else:
            self.sizeComboBox.setCurrentIndex(sizeIndex)


    def accept(self):
        clipboard = QApplication.clipboard()
        text = self.copyTextLineEdit.text() or self.panel.currentChar
        clipboard.setText(text, QClipboard.Clipboard)
        clipboard.setText(text, QClipboard.Selection)
        if text:
            say("Copied “{}” to the clipboard".format(text), SAY_TIMEOUT)
        super().accept()


    def addSelected(self):
        char = self.panel.currentChar
        if char:
            self.copyTextLineEdit.setText(self.copyTextLineEdit.text() +
                                          char)
        self.findNextButton.setFocus()


    def setToFamily(self, family):
        family = family.casefold()
        for i in range(self.fontComboBox.count()):
            if self.fontComboBox.itemText(i).casefold() == family:
                self.fontComboBox.setCurrentIndex(i)
                break


    def setToNearestSize(self, size):
        below = 0
        belowIndex = -1
        above = 999
        aboveIndex = -1
        for i in range(self.sizeComboBox.count()):
            sz = int(self.sizeComboBox.itemText(i))
            if sz == size:
                self.sizeComboBox.setCurrentIndex(i)
                break
            if sz < size and sz > below:
                below = sz
                belowIndex = i
            if sz > size and sz < above:
                above = sz
                aboveIndex = i
        else:
            if abs(size - below) < abs(size - above):
                self.sizeComboBox.setCurrentIndex(belowIndex)
            else:
                self.sizeComboBox.setCurrentIndex(aboveIndex)


    def findNext(self):
        text = self.findTextLineEdit.text().strip().casefold()
        if text:
            start = self.panel.currentChar
            start = ord(start) if start else ord(" ")
            for i in range(start + 1, MAX_CHAR):
                try:
                    char = chr(i)
                    name = unicodedata.name(char).casefold()
                    if text in name:
                        self.panel.currentChar = char
                        self.panel.update()
                        y = (self.panel.squareSize * i) // COLUMNS
                        self.scrollArea.ensureVisible(0, y)
                        break
                except ValueError:
                    pass
            else:
                self.panel.currentChar = " "
                self.findNext()


    def keyPressEvent(self, event):
        key = event.key()
        if key in {Qt.Key_Enter, Qt.Key_Return}:
            if self.findTextLineEdit.text().strip():
                self.findNext()
            else:
                self.addSelectedButton.setFocus()


    def updateSize(self, squareSize):
        self.setMinimumWidth((COLUMNS + (1.5 if WIN else 1)) * squareSize)


class Panel(QWidget):

    characterSelected = Signal(str)
    fontResized = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.displayFont = QFont()
        self.displayFont.setStyleStrategy(QFont.PreferDefault)
        self.updateFont(self.displayFont.family())
        self.currentChar = ""
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)


    def updateFont(self, family):
        self.displayFont.setFamily(family)
        self.updateSize(self.displayFont.pointSize())


    def updateSize(self, size):
        size = int(size)
        self.displayFont.setPointSize(size)
        self.squareSize = max(SQUARE_SIZE,
                              QFontMetrics(self.displayFont).xHeight() * 3)
        self.fontResized.emit(self.squareSize)
        self.adjustSize()
        self.update()


    def minimumWidth(self):
        return COLUMNS * self.squareSize


    def sizeHint(self):
        return QSize(self.minimumWidth(),
                     (MAX_CHAR / COLUMNS) * self.squareSize)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.currentChar = chr((event.y() // self.squareSize) *
                                   COLUMNS + event.x() // self.squareSize)
            if not unicodedata.category(self.currentChar).startswith("C"):
                self.characterSelected.emit(self.currentChar)
            self.update()
        else:
            super().mousePressEvent(event)


    def mouseMoveEvent(self, event):
        pos = self.mapFromGlobal(event.globalPos())
        code = ((pos.y() // self.squareSize) *
                COLUMNS + pos.x() // self.squareSize)
        name = "unnamed"
        try:
            name = unicodedata.name(chr(code)).capitalize()
        except ValueError:
            pass
        text = """<p><span style="font-size: 18pt;">{0:c}</span></p>
<p><span style="font-size: 13pt;">U+{0:04X}<br>{1}</span></p>""".format(
            code, name)
        QToolTip.showText(event.globalPos(), text, self)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.white)
        painter.setFont(self.displayFont)

        redrawRect = event.rect()
        beginRow = redrawRect.top() // self.squareSize
        endRow = redrawRect.bottom() // self.squareSize
        beginColumn = redrawRect.left() // self.squareSize
        endColumn = redrawRect.right() // self.squareSize

        painter.setPen(Qt.gray)
        for row in range(beginRow, endRow + 1):
            for column in range(beginColumn, endColumn + 1):
                painter.drawRect(column * self.squareSize,
                                 row * self.squareSize, self.squareSize,
                                 self.squareSize)

        fontMetrics = QFontMetrics(self.displayFont)
        painter.setPen(Qt.black)
        for row in range(beginRow, endRow + 1):
            for column in range(beginColumn, endColumn + 1):
                char = chr(row * COLUMNS + column)
                painter.setClipRect(column * self.squareSize,
                                    row * self.squareSize, self.squareSize,
                                    self.squareSize)
                if char == self.currentChar:
                    painter.fillRect(column * self.squareSize + 1,
                                     row * self.squareSize + 1,
                                     self.squareSize, self.squareSize,
                                     Qt.green)
                painter.drawText(
                    column * self.squareSize + (self.squareSize / 2) -
                    fontMetrics.width(char) / 2,
                    row * self.squareSize + 4 + fontMetrics.ascent(), char)


if __name__ == '__main__':
    import sys
    import Qrc # noqa
    import HelpForm
    class FakeState:
        def __init__(self):
            self.window = None
            self.helpForm = None
            self.stdFontFamily = "Times New Roman"
            self.stdFontSize = 13
        def help(self, page=None):
            if self.helpForm is None:
                self.helpForm = HelpForm.Form("xix_help.html", self.window)
            if page is not None:
                self.helpForm.changePage(page)
            self.helpForm.show()
            self.helpForm.raise_()
            self.helpForm.activateWindow()
    app = QApplication([])
    app.setOrganizationName("Qtrac Ltd.")
    app.setOrganizationDomain("qtrac.eu")
    app.setApplicationName("XindeX-Test")
    app.setApplicationVersion("1.0.0")
    state = FakeState()
    form = Form(state)
    form.show()
    app.exec_()
