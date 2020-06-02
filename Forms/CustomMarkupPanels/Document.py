#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Signal
from PySide.QtGui import (
    QFormLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget)

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
        self.documentStartEdit = self.makeEditor("""\
<p><b>Document, Start, Document</b></p>
<p>The markup to use at the start of the index.</p>
<p>If “{{title}}” is present it will be replaced by the Output Options
Title. Also, “{{nl}}” will be replaced by a newline and “{{bom}}” by the
UTF-8 byte-order mark.{}""".format(BLANK_SPACE_HTML))
        self.documentEndEdit = self.makeEditor("""\
<p><b>Document, End, Document</b></p><p>The markup to use at the end of
the index.</p>{}""".format(BLANK_SPACE_HTML))
        self.noteEdit = self.makeEditor("""\
<p><b>Document, Note</b></p>
<p>The markup for the index's note. If “{{note}}” is present it will be
replaced by the <b>Output Options, Index
Note</b>.</p>{}""".format(BLANK_SPACE_HTML))
        self.sectionStartEdit = self.makeEditor("""\
<p><b>Document, Start, Section</b></p>
<p>The markup to use at the start of each section.</p> <p>If “{{nl}}”
is present it will be replaced by a newline.{}""".format(BLANK_SPACE_HTML))
        self.sectionEndEdit = self.makeEditor("""\
<p><b>Document, End, Section</b></p>
<p>The markup to use at the end of each section.</p> <p>If “{{nl}}”
is present it will be replaced by a newline.{}""".format(BLANK_SPACE_HTML))
        self.mainStartEdit = self.makeEditor("""\
<p><b>Document, Start, Main</b></p>
<p>The markup to use at the start of each entry.</p> <p>If “{{nl}}”
is present it will be replaced by a newline.{}""".format(BLANK_SPACE_HTML))
        self.mainEndEdit = self.makeEditor("""\
<p><b>Document, End, Main</b></p>
<p>The markup to use at the end of each entry.</p> <p>If “{{nl}}”
is present it will be replaced by a newline.{}""".format(BLANK_SPACE_HTML))
        self.sub1StartEdit = self.makeEditor("""\
<p><b>Document, Start, First-Level Subentry</b></p>
<p>The markup to use at the start of each first-level subentry.</p>
<p>If “{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub1EndEdit = self.makeEditor("""\
<p><b>Document, End, First-Level Subentry</b></p>
<p>The markup to use at the end of each first-level subentry.</p> <p>If
“{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub2StartEdit = self.makeEditor("""\
<p><b>Document, Start, Second-Level Subentry</b></p>
<p>The markup to use at the start of each second-level subentry.</p>
<p>If “{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub2EndEdit = self.makeEditor("""\
<p><b>Document, End, Second-Level Subentry</b></p>
<p>The markup to use at the end of each second-level subentry.</p> <p>If
“{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub3StartEdit = self.makeEditor("""\
<p><b>Document, Start, Third-Level Subentry</b></p>
<p>The markup to use at the start of each third-level subentry.</p>
<p>If “{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub3EndEdit = self.makeEditor("""\
<p><b>Document, End, Third-Level Subentry</b></p>
<p>The markup to use at the end of each third-level subentry.</p> <p>If
“{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub4StartEdit = self.makeEditor("""\
<p><b>Document, Start, Fourth-Level Subentry</b></p>
<p>The markup to use at the start of each fourth-level subentry.</p>
<p>If “{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub4EndEdit = self.makeEditor("""\
<p><b>Document, End, Fourth-Level Subentry</b></p>
<p>The markup to use at the end of each fourth-level subentry.</p> <p>If
“{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub5StartEdit = self.makeEditor("""\
<p><b>Document, Start, Fifth-Level Subentry</b></p>
<p>The markup to use at the start of each fifth-level subentry.</p>
<p>If “{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub5EndEdit = self.makeEditor("""\
<p><b>Document, End, Fifth-Level Subentry</b></p>
<p>The markup to use at the end of each fifth-level subentry.</p> <p>If
“{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub6StartEdit = self.makeEditor("""\
<p><b>Document, Start, Sixth-Level Subentry</b></p>
<p>The markup to use at the start of each sixth-level subentry.</p>
<p>If “{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub6EndEdit = self.makeEditor("""\
<p><b>Document, End, Sixth-Level Subentry</b></p>
<p>The markup to use at the end of each sixth-level subentry.</p> <p>If
“{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub7StartEdit = self.makeEditor("""\
<p><b>Document, Start, Seventh-Level Subentry</b></p>
<p>The markup to use at the start of each seventh-level subentry.</p>
<p>If “{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub7EndEdit = self.makeEditor("""\
<p><b>Document, End, Seventh-Level Subentry</b></p>
<p>The markup to use at the end of each seventh-level subentry.</p>
<p>If “{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub8StartEdit = self.makeEditor("""\
<p><b>Document, Start, Eighth-Level Subentry</b></p>
<p>The markup to use at the start of each eighth-level subentry.</p>
<p>If “{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub8EndEdit = self.makeEditor("""\
<p><b>Document, End, Eighth-Level Subentry</b></p>
<p>The markup to use at the end of each eighth-level subentry.</p> <p>If
“{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub9StartEdit = self.makeEditor("""\
<p><b>Document, Start, Ninth-Level Subentry</b></p>
<p>The markup to use at the start of each ninth-level subentry.</p>
<p>If “{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))
        self.sub9EndEdit = self.makeEditor("""\
<p><b>Document, End, Ninth-Level Subentry</b></p>
<p>The markup to use at the end of each ninth-level subentry.</p> <p>If
“{{nl}}” is present it will be replaced by a
newline.{}""".format(BLANK_SPACE_HTML))

        self.topForm = QFormLayout()
        self.topForm.addRow("&Note", self.noteEdit)
        self.startForm = QFormLayout()

        self.startForm.addRow("", QLabel("Start"))
        self.startForm.addRow("Doc&ument", self.documentStartEdit)
        self.startForm.addRow("&Section", self.sectionStartEdit)
        self.startForm.addRow("&Main", self.mainStartEdit)
        self.startForm.addRow("Sub &1", self.sub1StartEdit)
        self.startForm.addRow("Sub &2", self.sub2StartEdit)
        self.startForm.addRow("Sub &3", self.sub3StartEdit)
        self.startForm.addRow("Sub &4", self.sub4StartEdit)
        self.startForm.addRow("Sub &5", self.sub5StartEdit)
        self.startForm.addRow("Sub &6", self.sub6StartEdit)
        self.startForm.addRow("Sub &7", self.sub7StartEdit)
        self.startForm.addRow("Sub &8", self.sub8StartEdit)
        self.startForm.addRow("Sub &9", self.sub9StartEdit)

        self.endForm = QFormLayout()
        self.endForm.addRow("", QLabel("End"))
        self.endForm.addRow(self.documentEndEdit)
        self.endForm.addRow(self.sectionEndEdit)
        self.endForm.addRow(self.mainEndEdit)
        self.endForm.addRow(self.sub1EndEdit)
        self.endForm.addRow(self.sub2EndEdit)
        self.endForm.addRow(self.sub3EndEdit)
        self.endForm.addRow(self.sub4EndEdit)
        self.endForm.addRow(self.sub5EndEdit)
        self.endForm.addRow(self.sub6EndEdit)
        self.endForm.addRow(self.sub7EndEdit)
        self.endForm.addRow(self.sub8EndEdit)
        self.endForm.addRow(self.sub9EndEdit)


    def layoutWidgets(self):
        vbox = QVBoxLayout()
        vbox.addLayout(self.topForm)
        hbox = QHBoxLayout()
        hbox.addLayout(self.startForm)
        hbox.addLayout(self.endForm)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setTabOrder(self.documentStartEdit, self.documentEndEdit)
        self.setTabOrder(self.sectionStartEdit, self.sectionEndEdit)
        self.setTabOrder(self.mainStartEdit, self.mainEndEdit)
        self.setTabOrder(self.sub1StartEdit, self.sub1EndEdit)
        self.setTabOrder(self.sub2StartEdit, self.sub2EndEdit)
        self.setTabOrder(self.sub3StartEdit, self.sub3EndEdit)
        self.setTabOrder(self.sub4StartEdit, self.sub4EndEdit)
        self.setTabOrder(self.sub5StartEdit, self.sub5EndEdit)
        self.setTabOrder(self.sub6StartEdit, self.sub6EndEdit)
        self.setTabOrder(self.sub7StartEdit, self.sub7EndEdit)
        self.setTabOrder(self.sub8StartEdit, self.sub8EndEdit)
        self.setTabOrder(self.sub9StartEdit, self.sub9EndEdit)


    def createConnections(self):
        self.documentStartEdit.textChanged.connect(self.changed)
        self.documentEndEdit.textChanged.connect(self.changed)
        self.noteEdit.textChanged.connect(self.changed)
        self.sectionStartEdit.textChanged.connect(self.changed)
        self.sectionEndEdit.textChanged.connect(self.changed)
        self.mainStartEdit.textChanged.connect(self.changed)
        self.mainEndEdit.textChanged.connect(self.changed)
        self.sub1StartEdit.textChanged.connect(self.changed)
        self.sub1EndEdit.textChanged.connect(self.changed)
        self.sub2StartEdit.textChanged.connect(self.changed)
        self.sub2EndEdit.textChanged.connect(self.changed)
        self.sub3StartEdit.textChanged.connect(self.changed)
        self.sub3EndEdit.textChanged.connect(self.changed)
        self.sub4StartEdit.textChanged.connect(self.changed)
        self.sub4EndEdit.textChanged.connect(self.changed)
        self.sub5StartEdit.textChanged.connect(self.changed)
        self.sub5EndEdit.textChanged.connect(self.changed)
        self.sub6StartEdit.textChanged.connect(self.changed)
        self.sub6EndEdit.textChanged.connect(self.changed)
        self.sub7StartEdit.textChanged.connect(self.changed)
        self.sub7EndEdit.textChanged.connect(self.changed)
        self.sub8StartEdit.textChanged.connect(self.changed)
        self.sub8EndEdit.textChanged.connect(self.changed)
        self.sub9StartEdit.textChanged.connect(self.changed)
        self.sub9EndEdit.textChanged.connect(self.changed)


    def populateFromMarkup(self, markup):
        with Lib.BlockSignals(self):
            self.documentStartEdit.setPlainText(markup.DocumentStart)
            self.documentEndEdit.setPlainText(markup.DocumentEnd)
            self.noteEdit.setPlainText(markup.Note)
            self.sectionStartEdit.setPlainText(markup.SectionStart)
            self.sectionEndEdit.setPlainText(markup.SectionEnd)
            self.mainStartEdit.setPlainText(markup.MainStart)
            self.mainEndEdit.setPlainText(markup.MainEnd)
            self.sub1StartEdit.setPlainText(markup.Sub1Start)
            self.sub1EndEdit.setPlainText(markup.Sub1End)
            self.sub2StartEdit.setPlainText(markup.Sub2Start)
            self.sub2EndEdit.setPlainText(markup.Sub2End)
            self.sub3StartEdit.setPlainText(markup.Sub3Start)
            self.sub3EndEdit.setPlainText(markup.Sub3End)
            self.sub4StartEdit.setPlainText(markup.Sub4Start)
            self.sub4EndEdit.setPlainText(markup.Sub4End)
            self.sub5StartEdit.setPlainText(markup.Sub5Start)
            self.sub5EndEdit.setPlainText(markup.Sub5End)
            self.sub6StartEdit.setPlainText(markup.Sub6Start)
            self.sub6EndEdit.setPlainText(markup.Sub6End)
            self.sub7StartEdit.setPlainText(markup.Sub7Start)
            self.sub7EndEdit.setPlainText(markup.Sub7End)
            self.sub8StartEdit.setPlainText(markup.Sub8Start)
            self.sub8EndEdit.setPlainText(markup.Sub8End)
            self.sub9StartEdit.setPlainText(markup.Sub9Start)
            self.sub9EndEdit.setPlainText(markup.Sub9End)


    def updateMarkup(self, markup):
        markup.DocumentStart = self.documentStartEdit.toPlainText()
        markup.DocumentEnd = self.documentEndEdit.toPlainText()
        markup.Note = self.noteEdit.toPlainText()
        markup.SectionStart = self.sectionStartEdit.toPlainText()
        markup.SectionEnd = self.sectionEndEdit.toPlainText()
        markup.MainStart = self.mainStartEdit.toPlainText()
        markup.MainEnd = self.mainEndEdit.toPlainText()
        markup.Sub1Start = self.sub1StartEdit.toPlainText()
        markup.Sub1End = self.sub1EndEdit.toPlainText()
        markup.Sub2Start = self.sub1StartEdit.toPlainText()
        markup.Sub2End = self.sub1EndEdit.toPlainText()
        markup.Sub3Start = self.sub1StartEdit.toPlainText()
        markup.Sub3End = self.sub1EndEdit.toPlainText()
        markup.Sub4Start = self.sub1StartEdit.toPlainText()
        markup.Sub4End = self.sub1EndEdit.toPlainText()
        markup.Sub5Start = self.sub1StartEdit.toPlainText()
        markup.Sub5End = self.sub1EndEdit.toPlainText()
        markup.Sub6Start = self.sub1StartEdit.toPlainText()
        markup.Sub6End = self.sub1EndEdit.toPlainText()
        markup.Sub7Start = self.sub1StartEdit.toPlainText()
        markup.Sub7End = self.sub1EndEdit.toPlainText()
        markup.Sub8Start = self.sub1StartEdit.toPlainText()
        markup.Sub8End = self.sub1EndEdit.toPlainText()
        markup.Sub9Start = self.sub1StartEdit.toPlainText()
        markup.Sub9End = self.sub1EndEdit.toPlainText()
