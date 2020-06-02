#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Qt
from PySide.QtGui import (
    QCheckBox, QComboBox, QFont, QFormLayout, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QSpinBox, QTextEdit, QTextOption, QVBoxLayout,
    QWidget)

from Config import Gconf
import Lib
import Widgets
from Const import BLANK_SPACE_HTML, StyleKind, WIN


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
        self.formatPanel = Widgets.FormatPanel.Panel(
            self.state, self, editableFontSize=True)
        formatActions = self.formatPanel.formatActions

        self.titleLabel = QLabel("&Index Title")
        self.titleTextEdit = Widgets.LineEdit.HtmlLineEdit(
            self.state, formatActions=formatActions)
        self.titleLabel.setBuddy(self.titleTextEdit)
        self.titleTextEdit.setHtml(self.config.get(Gconf.Key.Title))
        self.form.tooltips.append((self.titleTextEdit, """\
<p><b>Index Title</b></p>
<p>The index's title. Leave blank if the title is to be added directly
in the output file.</p>"""))

        self.noteLabel = QLabel("Index &Note")
        self.noteTextEdit = Widgets.LineEdit.MultilineHtmlEdit(
            self.state, maxLines=8, formatActions=formatActions)
        self.noteLabel.setBuddy(self.noteTextEdit)
        self.noteTextEdit.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.noteTextEdit.setLineWrapColumnOrWidth(60)
        self.noteTextEdit.setWordWrapMode(QTextOption.WordWrap)
        self.noteTextEdit.setHtml(self.config.get(Gconf.Key.Note))
        self.form.tooltips.append((self.noteTextEdit, """\
<p><b>Index Note</b></p>
<p>The index's note. Leave blank if no note is required or if the note
is to be added directly in the output file.</p>"""))

        self.sectionsGroupBox = QGroupBox("Sections")
        self.blankBeforeLabel = QLabel("&Blank Lines Before")
        self.blankBeforeSpinBox = QSpinBox()
        self.blankBeforeSpinBox.setAlignment(Qt.AlignRight)
        self.blankBeforeLabel.setBuddy(self.blankBeforeSpinBox)
        self.blankBeforeSpinBox.setRange(0, 3)
        self.blankBeforeSpinBox.setValue(self.config.get(
                                         Gconf.Key.SectionPreLines))
        self.form.tooltips.append((self.blankBeforeSpinBox, """\
<p><b>Blank Lines Before</b></p>
<p>How many blank lines to output before a section. (A section is a
distinct part of the index, e.g., the ‘A’s.)</p>"""))
        self.blankAfterLabel = QLabel("Blank &Lines After")
        self.blankAfterSpinBox = QSpinBox()
        self.blankAfterSpinBox.setAlignment(Qt.AlignRight)
        self.blankAfterLabel.setBuddy(self.blankAfterSpinBox)
        self.blankAfterSpinBox.setRange(0, 3)
        self.blankAfterSpinBox.setValue(self.config.get(
                                        Gconf.Key.SectionPostLines))
        self.form.tooltips.append((self.blankAfterSpinBox, """\
<p><b>Blank Lines After</b></p>
<p>How many blank lines to output before after section's title. (A
section is a distinct part of the index, e.g., the ‘A’s.)</p>"""))
        self.sectionTitlesCheckBox = QCheckBox("&Output Titles")
        self.sectionTitlesCheckBox.setChecked(
            self.config.get(Gconf.Key.SectionTitles))
        self.form.tooltips.append((self.sectionTitlesCheckBox, """\
<p><b>Output Titles</b></p>
<p>If checked, section titles are output before each section, e.g., ‘A’,
before the As, ‘B’, before the Bs, and so on.</p>"""))
        self.sectionSpecialTitleLabel = QLabel("Special Section &Title")
        self.sectionSpecialTitleTextEdit = Widgets.LineEdit.HtmlLineEdit(
            self.state, formatActions=formatActions)
        self.sectionSpecialTitleLabel.setBuddy(
            self.sectionSpecialTitleTextEdit)
        self.sectionSpecialTitleTextEdit.setHtml(
            self.config.get(Gconf.Key.SectionSpecialTitle))
        self.form.tooltips.append((self.sectionSpecialTitleTextEdit, """\
<p><b>Special Section Title</b></p>
<p>If there are entries which precede the ‘A’ section, then this section
title will be used for them.</p>
<p>Note that even if this title isn't used, its font name and size will
be used for all the other section titles.</p>"""))

        size = self.font().pointSize() + (1 if WIN else 2)
        family = self.config.get(Gconf.Key.StdFont)
        size = self.config.get(Gconf.Key.StdFontSize, size)
        Lib.createFontBoxesFor(self, "Std", family, size,
                               tooltips=self.form.tooltips, which="Std.")
        self.onStdFontChange(False)
        family = self.config.get(Gconf.Key.AltFont)
        size = self.config.get(Gconf.Key.AltFontSize, size)
        Lib.createFontBoxesFor(self, "Alt", family, size,
                               tooltips=self.form.tooltips, which="Alt.")
        self.onAltFontChange(False)
        family = self.config.get(Gconf.Key.MonoFont)
        size = self.config.get(Gconf.Key.MonoFontSize, size)
        Lib.createFontBoxesFor(self, "Mono", family, size, mono=True,
                               tooltips=self.form.tooltips, which="Mono.")
        self.onMonoFontChange(False)

        self.monoFontAsStrikeoutCheckbox = QCheckBox(
            "Output Mono. &Font as Strikeout")
        self.form.tooltips.append((self.monoFontAsStrikeoutCheckbox, """\
<p><b>Output Mono. Font as Strikeout</b></p>
<p>If checked, any text in the index that is styled as mono. font
family will be output using the std. font family&mdash;but with
<s>strikeout</s>.</p>"""))
        self.monoFontAsStrikeoutCheckbox.setChecked(
            self.config.get(Gconf.Key.MonoFontAsStrikeout))

        self.styleLabel = QLabel("St&yle")
        self.styleComboBox = QComboBox()
        self.styleLabel.setBuddy(self.styleComboBox)
        oldStyle = self.config.get(Gconf.Key.Style)
        index = -1
        for i, style in enumerate(StyleKind):
            self.styleComboBox.addItem(style.text, style.value)
            if style is oldStyle:
                index = i
        self.styleComboBox.setCurrentIndex(index)
        self.form.tooltips.append((self.styleComboBox, """\
<p><b>Style</b></p>
<p>The style of index to output.</p>"""))

        self.termPagesSepLabel = QLabel("T&erm-Pages Separator")
        self.termPagesSepTextEdit = Widgets.LineEdit.SpacesHtmlLineEdit(
            self.state, 3, formatActions=formatActions)
        self.termPagesSepLabel.setBuddy(self.termPagesSepTextEdit)
        self.termPagesSepTextEdit.setHtml(self.config.get(
                                          Gconf.Key.TermPagesSeparator))
        self.form.tooltips.append((self.termPagesSepTextEdit, """\
<p><b>Term-Pages Separator</b></p>
<p>The separator text to use between the end of an entry's term and its
pages.</p>{}""".format(BLANK_SPACE_HTML)))

        self.runInSepLabel = QLabel("&Run-in Separator")
        self.runInSepTextEdit = Widgets.LineEdit.SpacesHtmlLineEdit(
            self.state, 3, formatActions=formatActions)
        self.runInSepLabel.setBuddy(self.runInSepTextEdit)
        self.runInSepTextEdit.setHtml(self.config.get(
                                      Gconf.Key.RunInSeparator))
        self.form.tooltips.append((self.runInSepTextEdit, """\
<p><b>Run-in Separator</b></p>
<p>The separator text to use between run-in entries (for run-in style
index output).</p>{}""".format(BLANK_SPACE_HTML)))

        self.formatPanel.state.editors = [
            self.titleTextEdit, self.noteTextEdit,
            self.sectionSpecialTitleTextEdit, self.termPagesSepTextEdit,
            self.runInSepTextEdit]


    def layoutWidgets(self):
        form = QFormLayout()
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.formatPanel)
        form.addRow(hbox)
        form.addRow(self.titleLabel, self.titleTextEdit)
        form.addRow(self.noteLabel, self.noteTextEdit)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.blankBeforeLabel)
        hbox.addWidget(self.blankBeforeSpinBox)
        hbox.addWidget(self.blankAfterLabel)
        hbox.addWidget(self.blankAfterSpinBox)
        hbox.addStretch()
        vbox.addLayout(hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(self.sectionTitlesCheckBox)
        hbox.addStretch()
        hbox.addWidget(self.sectionSpecialTitleLabel)
        hbox.addWidget(self.sectionSpecialTitleTextEdit)
        vbox.addLayout(hbox)
        self.sectionsGroupBox.setLayout(vbox)
        form.addRow(self.sectionsGroupBox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.stdFontComboBox, 1)
        hbox.addWidget(self.stdFontSizeSpinBox)
        hbox.addStretch()
        label = QLabel("&Std. Font")
        label.setBuddy(self.stdFontComboBox)
        form.addRow(label, hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(self.altFontComboBox, 1)
        hbox.addWidget(self.altFontSizeSpinBox)
        hbox.addStretch()
        label = QLabel("&Alt. Font")
        label.setBuddy(self.altFontComboBox)
        form.addRow(label, hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(self.monoFontComboBox, 1)
        hbox.addWidget(self.monoFontSizeSpinBox)
        hbox.addStretch()
        label = QLabel("&Mono. Font")
        label.setBuddy(self.monoFontComboBox)
        form.addRow(label, hbox)

        grid = QGridLayout()
        grid.addWidget(self.monoFontAsStrikeoutCheckbox, 0, 0, 1, 2)
        grid.addWidget(self.termPagesSepLabel, 0, 2)
        grid.addWidget(self.termPagesSepTextEdit, 0, 3)
        grid.addWidget(self.styleLabel, 1, 0)
        grid.addWidget(self.styleComboBox, 1, 1)
        grid.addWidget(self.runInSepLabel, 1, 2)
        grid.addWidget(self.runInSepTextEdit, 1, 3)
        form.addRow(grid)
        self.setLayout(form)


    def createConnections(self):
        self.stdFontComboBox.currentFontChanged.connect(
            self.onStdFontChange)
        self.stdFontSizeSpinBox.valueChanged[int].connect(
            self.onStdFontChange)
        self.altFontComboBox.currentFontChanged.connect(
            self.onAltFontChange)
        self.altFontSizeSpinBox.valueChanged[int].connect(
            self.onAltFontChange)
        self.monoFontComboBox.currentFontChanged.connect(
            self.onMonoFontChange)
        self.monoFontSizeSpinBox.valueChanged[int].connect(
            self.onMonoFontChange)


    def onStdFontChange(self, propagate=True):
        font = QFont(self.stdFontComboBox.currentFont())
        font.setPointSize(self.stdFontSizeSpinBox.value())
        if propagate and bool(self.state.model):
            self.state.model.setConfig(Gconf.Key.StdFont, font.family())
            self.state.model.setConfig(Gconf.Key.StdFontSize,
                                       font.pointSize())


    def onAltFontChange(self, propagate=True):
        font = QFont(self.altFontComboBox.currentFont())
        font.setPointSize(self.altFontSizeSpinBox.value())
        if propagate and bool(self.state.model):
            self.state.model.setConfig(Gconf.Key.AltFont, font.family())
            self.state.model.setConfig(Gconf.Key.AltFontSize,
                                       font.pointSize())


    def onMonoFontChange(self, propagate=True):
        font = QFont(self.monoFontComboBox.currentFont())
        font.setPointSize(self.monoFontSizeSpinBox.value())
        if propagate and bool(self.state.model):
            self.state.model.setConfig(Gconf.Key.MonoFont, font.family())
            self.state.model.setConfig(Gconf.Key.MonoFontSize,
                                       font.pointSize())
