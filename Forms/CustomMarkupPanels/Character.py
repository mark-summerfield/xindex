#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Signal
from PySide.QtGui import (
    QComboBox, QFormLayout, QGridLayout, QLabel, QVBoxLayout, QWidget)

import Lib
import Widgets
from Const import BLANK_SPACE_HTML


class Panel(QWidget):

    changed = Signal()

    def __init__(self, state, parent):
        super().__init__(parent)
        self.state = state
        self.form = parent
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()


    def makeEditor(self, tip=None):
        editor = Widgets.LineEdit.SpacesHtmlLineEdit(self.state, None)
        if tip is not None:
            self.form.tooltips.append((editor, tip))
        return editor


    def createWidgets(self):
        self.escapeFunctionComboBox = QComboBox()
        self.escapeFunctionComboBox.addItem(
            "HTML:  &→&amp;  <→&lt;  >→&gt;")
        self.escapeFunctionComboBox.addItem("UCP:  <→<<>  >→<>>")
        self.form.tooltips.append((self.escapeFunctionComboBox, """\
<p><b>Escape</b></p>
<p>The character escaping to use.</p>"""))

        self.pageRangeSeparatorEdit = Widgets.LineEdit.SpacesHtmlLineEdit(
            self.state, 8)
        self.form.tooltips.append((self.pageRangeSeparatorEdit, """\
<p><b>Page Range Separator</b></p>
<p>The character or text to use in page ranges (e.g., an en-dash
“\u2013”).</p>"""))

        self.stdFontStartEdit = self.makeEditor("""\
<p><b>Character, Start, Std. Font</b></p>
<p>The markup to use to start using the standard font family and
size.</p>{}""".format(BLANK_SPACE_HTML))
        self.stdFontEndEdit = self.makeEditor("""\
<p><b>Character, End, Std. Font</b></p>
<p>The markup to use to end using the standard font family and
size.</p>{}""".format(BLANK_SPACE_HTML))
        self.altFontStartEdit = self.makeEditor("""\
<p><b>Character, Start, Alt. Font</b></p>
<p>The markup to use to start using the alternative font family and
size.</p>{}""".format(BLANK_SPACE_HTML))
        self.altFontEndEdit = self.makeEditor("""\
<p><b>Character, End, Alt. Font</b></p>
<p>The markup to use to end using the alternative font family and
size.</p>{}""".format(BLANK_SPACE_HTML))
        self.monoFontStartEdit = self.makeEditor("""\
<p><b>Character, Start, Mono. Font</b></p>
<p>The markup to use to start using the monospaced font family and
size.</p>{}""".format(BLANK_SPACE_HTML))
        self.monoFontEndEdit = self.makeEditor("""\
<p><b>Character, End, Mono. Font</b></p>
<p>The markup to use to end using the monospaced font family and
size.</p>{}""".format(BLANK_SPACE_HTML))
        self.boldStartEdit = self.makeEditor("""\
<p><b>Character, Start, Bold</b></p>
<p>The markup to use to start bold text.</p>{}""".format(BLANK_SPACE_HTML))
        self.boldEndEdit = self.makeEditor("""\
<p><b>Character, End, Bold</b></p>
<p>The markup to use to end bold text.</p>{}""".format(BLANK_SPACE_HTML))
        self.italicStartEdit = self.makeEditor("""\
<p><b>Character, Start, Italic</b></p>
<p>The markup to use to start italic
text.</p>{}""".format(BLANK_SPACE_HTML))
        self.italicEndEdit = self.makeEditor("""\
<p><b>Character, End, Italic</b></p>
<p>The markup to use to end italic text.</p>{}""".format(BLANK_SPACE_HTML))
        self.subscriptStartEdit = self.makeEditor("""\
<p><b>Character, Start, Subscript</b></p>
<p>The markup to use to start subscript
text.</p>{}""".format(BLANK_SPACE_HTML))
        self.subscriptEndEdit = self.makeEditor("""\
<p><b>Character, End, Subscript</b></p>
<p>The markup to use to end subscript
text.</p>{}""".format(BLANK_SPACE_HTML))
        self.superscriptStartEdit = self.makeEditor("""\
<p><b>Character, Start, Superscript</b></p>
<p>The markup to use to start superscript
text.</p>{}""".format(BLANK_SPACE_HTML))
        self.superscriptEndEdit = self.makeEditor("""\
<p><b>Character, End, Superscript</b></p>
<p>The markup to use to end superscript
text.</p>{}""".format(BLANK_SPACE_HTML))
        self.underlineStartEdit = self.makeEditor("""\
<p><b>Character, Start, Underline</b></p>
<p>The markup to use to start underlined
text.</p>{}""".format(BLANK_SPACE_HTML))
        self.underlineEndEdit = self.makeEditor("""\
<p><b>Character, End, Underline</b></p>
<p>The markup to use to end underlined
text.</p>{}""".format(BLANK_SPACE_HTML))
        self.strikeoutStartEdit = self.makeEditor("""\
<p><b>Character, Start, Strikeout</b></p>
<p>The markup to use to start strikeout
text.</p>{}""".format(BLANK_SPACE_HTML))
        self.strikeoutEndEdit = self.makeEditor("""\
<p><b>Character, End, Strikeout</b></p>
<p>The markup to use to end strikeout
text.</p>{}""".format(BLANK_SPACE_HTML))

        self.topLeftForm = QFormLayout()
        self.topLeftForm.addRow("E&scape", self.escapeFunctionComboBox)
        self.topRightForm = QFormLayout()
        self.topRightForm.addRow("&Page Range Separator",
                                 self.pageRangeSeparatorEdit)

        self.startForm = QFormLayout()
        self.startForm.addRow("", QLabel("Start"))
        self.startForm.addRow("Std. Fo&nt", self.stdFontStartEdit)
        self.startForm.addRow("Alt. &Font", self.altFontStartEdit)
        self.startForm.addRow("&Mono. Font", self.monoFontStartEdit)
        self.startForm.addRow("&Bold", self.boldStartEdit)
        self.startForm.addRow("&Italic", self.italicStartEdit)
        self.startForm.addRow("Subscrip&t", self.subscriptStartEdit)
        self.startForm.addRow("Supe&rscript", self.superscriptStartEdit)
        self.startForm.addRow("&Underline", self.underlineStartEdit)
        self.startForm.addRow("Stri&keout", self.strikeoutStartEdit)

        self.endForm = QFormLayout()
        self.endForm.addRow("", QLabel("End"))
        self.endForm.addRow(self.stdFontEndEdit)
        self.endForm.addRow(self.altFontEndEdit)
        self.endForm.addRow(self.monoFontEndEdit)
        self.endForm.addRow(self.boldEndEdit)
        self.endForm.addRow(self.italicEndEdit)
        self.endForm.addRow(self.subscriptEndEdit)
        self.endForm.addRow(self.superscriptEndEdit)
        self.endForm.addRow(self.underlineEndEdit)
        self.endForm.addRow(self.strikeoutEndEdit)


    def layoutWidgets(self):
        vbox = QVBoxLayout()
        grid = QGridLayout()
        grid.addLayout(self.topLeftForm, 0, 0)
        grid.addLayout(self.topRightForm, 0, 1)
        grid.addLayout(self.startForm, 1, 0)
        grid.addLayout(self.endForm, 1, 1)
        vbox.addLayout(grid)
        vbox.addStretch()

        self.setLayout(vbox)
        self.setTabOrder(self.stdFontStartEdit, self.stdFontEndEdit)
        self.setTabOrder(self.altFontStartEdit, self.altFontEndEdit)
        self.setTabOrder(self.monoFontStartEdit, self.monoFontEndEdit)
        self.setTabOrder(self.boldStartEdit, self.boldEndEdit)
        self.setTabOrder(self.italicStartEdit, self.italicEndEdit)
        self.setTabOrder(self.subscriptStartEdit, self.subscriptEndEdit)
        self.setTabOrder(self.superscriptStartEdit, self.superscriptEndEdit)
        self.setTabOrder(self.underlineStartEdit, self.underlineEndEdit)
        self.setTabOrder(self.strikeoutStartEdit, self.strikeoutEndEdit)


    def createConnections(self):
        self.escapeFunctionComboBox.currentIndexChanged.connect(
            self.changed)
        self.pageRangeSeparatorEdit.textChanged.connect(self.changed)
        self.stdFontStartEdit.textChanged.connect(self.changed)
        self.stdFontEndEdit.textChanged.connect(self.changed)
        self.altFontStartEdit.textChanged.connect(self.changed)
        self.altFontEndEdit.textChanged.connect(self.changed)
        self.monoFontStartEdit.textChanged.connect(self.changed)
        self.monoFontEndEdit.textChanged.connect(self.changed)
        self.boldStartEdit.textChanged.connect(self.changed)
        self.boldEndEdit.textChanged.connect(self.changed)
        self.italicStartEdit.textChanged.connect(self.changed)
        self.italicEndEdit.textChanged.connect(self.changed)
        self.subscriptStartEdit.textChanged.connect(self.changed)
        self.subscriptEndEdit.textChanged.connect(self.changed)
        self.superscriptStartEdit.textChanged.connect(self.changed)
        self.superscriptEndEdit.textChanged.connect(self.changed)
        self.underlineStartEdit.textChanged.connect(self.changed)
        self.underlineEndEdit.textChanged.connect(self.changed)
        self.strikeoutStartEdit.textChanged.connect(self.changed)
        self.strikeoutEndEdit.textChanged.connect(self.changed)


    def populateFromMarkup(self, markup):
        with Lib.BlockSignals(self):
            self.escapeFunctionComboBox.setCurrentIndex(
                0 if markup.escapefunction == "html" else 1)
            self.pageRangeSeparatorEdit.setPlainText(markup.RangeSeparator)
            self.stdFontStartEdit.setPlainText(markup.StdFontStart)
            self.stdFontEndEdit.setPlainText(markup.StdFontEnd)
            self.altFontStartEdit.setPlainText(markup.AltFontStart)
            self.altFontEndEdit.setPlainText(markup.AltFontEnd)
            self.monoFontStartEdit.setPlainText(markup.MonoFontStart)
            self.monoFontEndEdit.setPlainText(markup.MonoFontEnd)
            self.boldStartEdit.setPlainText(markup.BoldStart)
            self.boldEndEdit.setPlainText(markup.BoldEnd)
            self.italicStartEdit.setPlainText(markup.ItalicStart)
            self.italicEndEdit.setPlainText(markup.ItalicEnd)
            self.subscriptStartEdit.setPlainText(markup.SubscriptStart)
            self.subscriptEndEdit.setPlainText(markup.SubscriptEnd)
            self.superscriptStartEdit.setPlainText(markup.SuperscriptStart)
            self.superscriptEndEdit.setPlainText(markup.SuperscriptEnd)
            self.underlineStartEdit.setPlainText(markup.UnderlineStart)
            self.underlineEndEdit.setPlainText(markup.UnderlineEnd)
            self.strikeoutStartEdit.setPlainText(markup.StrikeoutStart)
            self.strikeoutEndEdit.setPlainText(markup.StrikeoutEnd)


    def updateMarkup(self, markup):
        markup.escapefunction = (
            "html" if self.escapeFunctionComboBox.currentIndex() == 0 else
            "ucp")
        markup.RangeSeparator = self.pageRangeSeparatorEdit.toPlainText()
        markup.AltFontStart = self.altFontStartEdit.toPlainText()
        markup.AltFontEnd = self.altFontEndEdit.toPlainText()
        markup.MonoFontStart = self.monoFontStartEdit.toPlainText()
        markup.MonoFontEnd = self.monoFontEndEdit.toPlainText()
        markup.StdFontStart = self.stdFontStartEdit.toPlainText()
        markup.StdFontEnd = self.stdFontEndEdit.toPlainText()
        markup.BoldStart = self.boldStartEdit.toPlainText()
        markup.BoldEnd = self.boldEndEdit.toPlainText()
        markup.ItalicStart = self.italicStartEdit.toPlainText()
        markup.ItalicEnd = self.italicEndEdit.toPlainText()
        markup.SubscriptEnd = self.subscriptStartEdit.toPlainText()
        markup.SubscriptStart = self.subscriptEndEdit.toPlainText()
        markup.SuperscriptEnd = self.superscriptStartEdit.toPlainText()
        markup.SuperscriptStart = self.superscriptEndEdit.toPlainText()
        markup.UnderlineStart = self.underlineStartEdit.toPlainText()
        markup.UnderlineEnd = self.underlineEndEdit.toPlainText()
        markup.StrikeoutStart = self.strikeoutStartEdit.toPlainText()
        markup.StrikeoutEnd = self.stdFontEndEdit.toPlainText()
