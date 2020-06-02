#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import QSettings, Qt
from PySide.QtGui import (
    QButtonGroup, QCheckBox, QFormLayout, QHBoxLayout, QIcon, QLabel,
    QLineEdit, QPushButton, QRadioButton, QToolButton)

from Const import TOOLTIP_IMAGE_SIZE


class Mixin:


    def createWidgets(self):
        settings = QSettings()

        self.searchLabel = QLabel("Search For")
        self.searchLineEdit = QLineEdit()
        self.tooltips.append((self.searchLineEdit, """\
<p><b>Search For editor</b></p>
<p>The text or regular expression to search for.</p>"""))
        self.searchLabel.setBuddy(self.searchLineEdit)
        self.replaceLabel = QLabel("Replace With")
        self.replaceLineEdit = QLineEdit()
        self.tooltips.append((self.replaceLineEdit, """\
<p><b>Replace With editor</b></p>
<p>The replacement text (which may include backreferences, \\1, \\2,
etc., if a regular expression search is being made).</p>"""))
        self.replaceLabel.setBuddy(self.replaceLineEdit)

        self.allEntriesRadioButton = QRadioButton("All Entries")
        self.allEntriesRadioButton.setChecked(
            bool(int(settings.value("RP/All", 1))))
        self.tooltips.append((self.allEntriesRadioButton, """\
<p><b>All Entries</b></p>
<p>If checked, the search will consider every entry in the index.</p>"""))
        self.filteredEntriesRadioButton = QRadioButton("Filtered Entries")
        self.filteredEntriesRadioButton.setChecked(bool(int(settings.value(
                                                   "RP/Filtered", 0))))
        self.tooltips.append((self.filteredEntriesRadioButton, """\
<p><b>Filtered Entries</b></p>
<p>If checked, the search will consider only those entries that are in
the current filtered view.</p>"""))
        self.considerLabel = QLabel("Consider")
        self.scopeGroup = QButtonGroup()
        self.scopeGroup.addButton(self.allEntriesRadioButton)
        self.scopeGroup.addButton(self.filteredEntriesRadioButton)

        self.literalRadioButton = QRadioButton("Literal")
        self.literalRadioButton.setChecked(
            bool(int(settings.value("RP/Literal", 1))))
        self.tooltips.append((
            self.literalRadioButton, """<p><b>Literal</b></p>
<p>If checked, the <b>Search For</b> text will be searched for
literally.</p>"""))
        self.regexRadioButton = QRadioButton("Regex")
        self.regexRadioButton.setChecked(
            bool(int(settings.value("RP/Regex", 0))))
        self.tooltips.append((self.regexRadioButton, """<p><b>Regex</b></p>
<p>If checked, the <b>Search For</b> text will be searched for
as a regular expression pattern.</p>"""))
        self.matchAsGroup = QButtonGroup()
        self.matchAsGroup.addButton(self.literalRadioButton)
        self.matchAsGroup.addButton(self.regexRadioButton)
        self.ignoreCaseCheckBox = QCheckBox("Ignore Case")
        self.ignoreCaseCheckBox.setChecked(
            bool(int(settings.value("RP/ICase", 0))))
        self.tooltips.append((self.ignoreCaseCheckBox, """\
<p><b>Ignore Case</b></p>
<p>If checked, the <b>Search For</b> text will be searched for
case-insensitively.</p>"""))
        self.wholeWordsCheckBox = QCheckBox("Whole Words")
        self.wholeWordsCheckBox.setChecked(
            bool(int(settings.value("RP/WW", 0))))
        self.tooltips.append((self.wholeWordsCheckBox, """\
<p><b>Whole Words</b></p>
<p>If checked&mdash;and when <b>Literal</b> is checked&mdash;the
<b>Search For</b> text will be matched as whole words.</p>
<p>For example, “habit” will not match “habitat” when whole words is
checked.</p>
<p>(For regular expressions use \\b before and after each word to get
whole word matches.)</p>"""))

        self.replaceInLabel = QLabel("Look In")
        self.replaceInTermsCheckBox = QCheckBox("Terms")
        self.replaceInTermsCheckBox.setChecked(bool(int(settings.value(
                                               "RP/Terms", 1))))
        self.tooltips.append((self.replaceInTermsCheckBox, """\
<p><b>Terms</b></p>
<p>If checked, the search will look in term texts.</p>"""))
        self.replaceInPagesCheckBox = QCheckBox("Pages")
        self.replaceInPagesCheckBox.setChecked(bool(int(settings.value(
                                               "RP/Pages", 0))))
        self.tooltips.append((self.replaceInPagesCheckBox, """\
<p><b>Pages</b></p>
<p>If checked, the search will look in pages texts.</p>"""))
        self.replaceInNotesCheckBox = QCheckBox("Notes")
        self.replaceInNotesCheckBox.setChecked(bool(int(settings.value(
                                               "RP/Notes", 0))))
        self.tooltips.append((self.replaceInNotesCheckBox, """\
<p><b>Notes</b></p>
<p>If checked, the search will look in notes texts.</p>"""))
        self.startButton = QPushButton(QIcon(":/edit-find.svg"),
                                       "Start Search")
        self.tooltips.append((
            self.startButton, """<p><b>Start Search</b></p>
<p>Start the search from the first entry in the index or the first entry
in the filtered view's entries.</p>"""))
        self.replaceButton = QPushButton(QIcon(":/edit-find-replace.svg"),
                                         "Replace")
        self.tooltips.append((self.replaceButton, """<p><b>Replace</b></p>
<p>Replace the highlighted text with the <b>Replace With</b> text (using
backreferences if they are in the replacement text and a <b>Regex</b>
search is underway), and then try to find the next matching text.</p>"""))
        self.skipButton = QPushButton(QIcon(":/skip.svg"), "S&kip")
        self.tooltips.append((self.skipButton, """<p><b>Skip</b></p>
<p>Skip the highlighted text and try to find the next matching
text.</p>"""))
        self.stopButton = QPushButton(QIcon(":/process-stop.svg"),
                                      "Stop Search")
        self.tooltips.append((self.stopButton, """<p><b>Stop Search</b></p>
<p>Stop the current search. This allows the search options to be
changed.</p>"""))
        self.closeButton = QToolButton()
        self.closeButton.setIcon(QIcon(":/hide.svg"))
        self.closeButton.setFocusPolicy(Qt.NoFocus)
        self.tooltips.append((self.closeButton, """<p><b>Hide</b></p>
<p>Hide the Search and Replace panel.</p>
<p>Press <b>Ctrl+H</b> or click <img src=":/edit-find-replace.svg"
width={0} height={0}> or click <b>Edit→Search and Replace</b> to show it
again.</p>""".format(TOOLTIP_IMAGE_SIZE)))
        self.helpButton = QToolButton()
        self.helpButton.setIcon(QIcon(":/help.svg"))
        self.helpButton.setFocusPolicy(Qt.NoFocus)
        self.tooltips.append((self.helpButton,
                             "Help on the Search and Replace panel."))


    def layoutWidgets(self):
        form = QFormLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.searchLineEdit)
        hbox.addWidget(self.closeButton)
        form.addRow(self.searchLabel, hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(self.replaceLineEdit)
        hbox.addWidget(self.helpButton)
        form.addRow(self.replaceLabel, hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(self.allEntriesRadioButton)
        hbox.addWidget(self.filteredEntriesRadioButton)
        hbox.addStretch()
        form.addRow(self.considerLabel, hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(self.literalRadioButton)
        hbox.addWidget(self.regexRadioButton)
        hbox.addStretch(1)
        hbox.addWidget(self.ignoreCaseCheckBox)
        hbox.addWidget(self.wholeWordsCheckBox)
        hbox.addStretch(5)
        form.addRow(QLabel("Match"), hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(self.replaceInTermsCheckBox)
        hbox.addWidget(self.replaceInPagesCheckBox)
        hbox.addWidget(self.replaceInNotesCheckBox)
        hbox.addStretch()
        form.addRow(self.replaceInLabel, hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(self.startButton)
        hbox.addWidget(self.replaceButton)
        hbox.addWidget(self.skipButton)
        hbox.addWidget(self.stopButton)
        hbox.addStretch()
        form.addRow(hbox)
        self.setLayout(form)


    def createConnections(self):
        self.helpButton.clicked.connect(self.help)
        self.stopButton.clicked.connect(self.stop)
        self.startButton.clicked.connect(self.start)
        self.replaceButton.clicked.connect(self.replace)
        self.skipButton.clicked.connect(self.skip)
        self.searchLineEdit.textChanged.connect(self.updateUi)
        self.searchLineEdit.returnPressed.connect(self.doAction)
        self.replaceLineEdit.textChanged.connect(self.updateUi)
        self.replaceLineEdit.returnPressed.connect(self.doAction)
        for button in (self.literalRadioButton, self.regexRadioButton,
                       self.ignoreCaseCheckBox, self.wholeWordsCheckBox,
                       self.replaceInTermsCheckBox,
                       self.replaceInPagesCheckBox,
                       self.replaceInNotesCheckBox):
            button.clicked.connect(self.updateUi)


    def doAction(self):
        button = None
        if self.skipButton.isEnabled():
            button = self.skipButton
        elif self.startButton.isEnabled():
            button = self.startButton
        if button is not None:
            button.setFocus()
            button.click()
        if self.skipButton.isEnabled():
            self.skipButton.setFocus()


    def help(self):
        self.state.help("xix_ref_panel_replace.html")
