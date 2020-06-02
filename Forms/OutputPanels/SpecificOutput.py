#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import QSettings
from PySide.QtGui import (
    QComboBox, QGroupBox, QHBoxLayout, QLabel, QRadioButton,
    QVBoxLayout, QWidget)

from Config import Gconf, Gopt
from Const import IndentKind, PaperSizeKind


class Panel(QWidget):

    def __init__(self, state, config, parent):
        super().__init__(parent)
        self.state = state
        self.config = config
        self.form = parent
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()


    def createWidgets(self):
        settings = QSettings()

        self.txtGroupBox = QGroupBox("Plain Text Format (.txt)")
        self.indentLabel = QLabel("&Indent")
        self.indentComboBox = QComboBox()
        self.indentLabel.setBuddy(self.indentComboBox)
        oldIndent = IndentKind.TAB
        oldIndent = self.config.get(Gconf.Key.Indent, oldIndent)
        index = -1
        for i, indent in enumerate(IndentKind):
            text = indent.name.replace("_", " ").title()
            self.indentComboBox.addItem(text, indent.value)
            if indent is oldIndent:
                index = i
        self.indentComboBox.setCurrentIndex(index)
        self.form.tooltips.append((self.indentComboBox, """\
<p><b>Indent</b></p>
<p>The indentation to use when outputting an indented-style index in
plain text format for each level of indentation.</p>"""))

        self.rtfGroupBox = QGroupBox("Rich Text Format (.rtf)")
        self.rtfIndentLabel = QLabel("I&ndent")
        self.rtfIndentComboBox = QComboBox()
        self.rtfIndentLabel.setBuddy(self.rtfIndentComboBox)
        oldIndent = IndentKind(int(settings.value(Gopt.Key.IndentRTF,
                                                  Gopt.Default.IndentRTF)))
        index = -1
        for i, indent in enumerate(IndentKind):
            text = ("Indent" if i == 0 else
                    indent.name.replace("_", " ").title())
            self.rtfIndentComboBox.addItem(text, indent.value)
            if indent is oldIndent:
                index = i
        self.rtfIndentComboBox.setCurrentIndex(index)
        self.form.tooltips.append((self.rtfIndentComboBox, """\
<p><b>Indent</b></p>
<p>The indentation to use when outputting an indented-style index in
rich text format for each level of indentation.</p>"""))

        self.pdfGroupBox = QGroupBox("Portable Document Format (.pdf)")
        self.paperSizeLabel = QLabel("Paper Size")
        self.letterRadioButton = QRadioButton("&Letter")
        self.a4RadioButton = QRadioButton("&A4")
        size = PaperSizeKind(int(settings.value(Gopt.Key.PaperSize,
                                                Gopt.Default.PaperSize)))
        if size is PaperSizeKind.LETTER:
            self.letterRadioButton.setChecked(True)
        else:
            self.a4RadioButton.setChecked(True)
        self.form.tooltips.append((self.letterRadioButton, """\
<p><b>Paper Size, Letter</b></p>
<p>If checked, when outputting a PDF of the index, US Letter
8.5"x11"-sized pages will be used.</p>"""))
        self.form.tooltips.append((self.a4RadioButton, """\
<p><b>Paper Size, A4</b></p>
<p>If checked, when outputting a PDF of the index, European A4-sized
pages will be used.</p>"""))


    def layoutWidgets(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self.indentLabel)
        hbox.addWidget(self.indentComboBox)
        hbox.addStretch()
        self.txtGroupBox.setLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.rtfIndentLabel)
        hbox.addWidget(self.rtfIndentComboBox)
        hbox.addStretch()
        self.rtfGroupBox.setLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.paperSizeLabel)
        hbox.addWidget(self.letterRadioButton)
        hbox.addWidget(self.a4RadioButton)
        hbox.addStretch()
        self.pdfGroupBox.setLayout(hbox)

        vbox = QVBoxLayout()
        vbox.addWidget(self.rtfGroupBox)
        vbox.addWidget(self.txtGroupBox)
        vbox.addWidget(self.pdfGroupBox)
        vbox.addStretch()

        self.setLayout(vbox)


    def createConnections(self):
        self.indentComboBox.currentIndexChanged.connect(self.setIndent)
        self.rtfIndentComboBox.currentIndexChanged.connect(
            self.setIndentRTF)


    def setIndent(self, index):
        index = self.indentComboBox.currentIndex()
        indent = int(self.indentComboBox.itemData(index))
        if bool(self.state.model):
            self.state.model.setConfig(Gconf.Key.Indent, indent)


    def setIndentRTF(self, index):
        index = self.rtfIndentComboBox.currentIndex()
        indent = int(self.rtfIndentComboBox.itemData(index))
        settings = QSettings()
        settings.setValue(Gopt.Key.IndentRTF, indent)
