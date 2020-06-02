#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import QSettings, Qt
from PySide.QtGui import (
    QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QIcon, QLineEdit,
    QSpinBox, QVBoxLayout, QWidget)

from Config import Gconf, Gopt
import Lib
from Const import LanguageKind


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
        creator = settings.value(Gopt.Key.Creator, self.state.user)
        self.creatorLineEdit = QLineEdit()
        self.creatorLineEdit.setText(creator)
        self.form.tooltips.append((self.creatorLineEdit, """\
<p><b>Creator</b></p>
<p>The indexer's name.</p>"""))
        initials = ""
        if creator:
            initials = Lib.initials(creator)
        initials = settings.value(Gopt.Key.Initials, initials)
        self.initialsLineEdit = QLineEdit()
        self.initialsLineEdit.setMaximumWidth(
            self.initialsLineEdit.fontMetrics().width("W") * 4)
        self.initialsLineEdit.setText(initials)
        self.form.tooltips.append((self.initialsLineEdit, """\
<p><b>Initials</b></p>
<p>The indexer's initials.</p>"""))

        self.languageGroupBox = QGroupBox("&Language")
        defaultLanguage = LanguageKind(settings.value(
            Gopt.Key.Language, Gopt.Default.Language))
        thisLanguage = self.config.get(Gconf.Key.Language, defaultLanguage)
        self.defaultLanguageComboBox = QComboBox()
        self.form.tooltips.append((self.defaultLanguageComboBox, """\
<p><b>Language, Default</b></p>
<p>The default setting for the <b>Language, For This Index</b> combobox
for new indexes.</p>"""))
        self.thisLanguageComboBox = QComboBox()
        self.form.tooltips.append((self.thisLanguageComboBox, """\
<p><b>Language, For This Index</b></p>
<p>The language to use for spellchecking and suggestions for this
index.</p>"""))
        self.populateLanguageComboBox(self.defaultLanguageComboBox,
                                      defaultLanguage)
        self.populateLanguageComboBox(self.thisLanguageComboBox,
                                      thisLanguage)

        self.limitsGroupBox = QGroupBox("Publisher's Limits for this Index")
        self.highestPageSpinBox = QSpinBox()
        self.highestPageSpinBox.setAlignment(Qt.AlignRight)
        self.highestPageSpinBox.setRange(10, 26000)
        self.highestPageSpinBox.setValue(self.config.get(
            Gconf.Key.HighestPageNumber, Gconf.Default.HighestPageNumber))
        self.form.tooltips.append((self.highestPageSpinBox, """\
<p><b>Highest Page Number</b></p>
<p>Any entries which contain a page number greater than this one will be
shown in the Filtered view if you use the “Too High Page Number”
filter.</p>"""))
        self.largestPageRangeSpinBox = QSpinBox()
        self.largestPageRangeSpinBox.setAlignment(Qt.AlignRight)
        self.largestPageRangeSpinBox.setRange(2, 1000)
        self.largestPageRangeSpinBox.setValue(self.config.get(
            Gconf.Key.LargestPageRange, Gconf.Default.LargestPageRange))
        self.form.tooltips.append((self.largestPageRangeSpinBox, """\
<p><b>Largest Page Range Span</b></p>
<p>Any entries which contain a page range that spans more pages than
this will be shown in the Filtered view if you use the “Too Large
Page Range” filter.</p>"""))
        self.mostPagesSpinBox = QSpinBox()
        self.mostPagesSpinBox.setAlignment(Qt.AlignRight)
        self.mostPagesSpinBox.setRange(2, 100)
        self.mostPagesSpinBox.setValue(self.config.get(
            Gconf.Key.MostPages, Gconf.Default.MostPages))
        self.form.tooltips.append((self.mostPagesSpinBox, """\
<p><b>Most Pages per Entry</b></p>
<p>Any entries which contain more pages and page ranges this will be
shown in the Filtered view if you use the “Too Many Pages”
filter.</p>"""))


    def layoutWidgets(self):
        layout = QVBoxLayout()

        form = QFormLayout()
        form.addRow("C&reator", self.creatorLineEdit)
        form.addRow("&Initials", self.initialsLineEdit)
        layout.addLayout(form)

        form = QFormLayout()
        form.addRow("For This Index", self.thisLanguageComboBox)
        form.addRow("Default", self.defaultLanguageComboBox)
        self.languageGroupBox.setLayout(form)
        layout.addWidget(self.languageGroupBox)

        form = QFormLayout()
        form.addRow("&Highest Page Number", self.highestPageSpinBox)
        form.addRow("Largest &Page Range Span",
                    self.largestPageRangeSpinBox)
        form.addRow("&Most Pages per Entry", self.mostPagesSpinBox)
        self.limitsGroupBox.setLayout(form)
        hbox = QHBoxLayout()
        hbox.addWidget(self.limitsGroupBox)
        hbox.addStretch()
        layout.addLayout(hbox)

        layout.addStretch()
        self.setLayout(layout)


    def createConnections(self):
        self.creatorLineEdit.textChanged.connect(self.updateInitials)
        self.defaultLanguageComboBox.currentIndexChanged.connect(
            self.setDefaultLanguage)
        self.thisLanguageComboBox.currentIndexChanged.connect(
            self.setThisLanguage)


    def updateInitials(self):
        text = self.creatorLineEdit.text()
        if text:
            initials = Lib.initials(text)
            if initials:
                self.initialsLineEdit.setText(initials)


    def populateLanguageComboBox(self, combobox, theLanguage):
        index = -1
        for i, language in enumerate(LanguageKind):
            if language is theLanguage:
                index = i
            name = language.value
            combobox.addItem(
                QIcon(":/{}.svg".format(name.replace(" ", "_"))), name,
                language)
        combobox.setCurrentIndex(index)


    def setDefaultLanguage(self, index):
        language = self.defaultLanguageComboBox.itemData(index)
        settings = QSettings()
        settings.setValue(Gopt.Key.Language, language.value)


    def setThisLanguage(self, index):
        language = self.defaultLanguageComboBox.itemData(index)
        self.state.model.setConfig(Gconf.Key.Language, language)
        self.state.entryPanel.spellHighlighter.rehighlight()
        self.state.window.updateLanguageIndicator()
