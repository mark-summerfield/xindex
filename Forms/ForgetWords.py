#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import QSettings
from PySide.QtGui import (
    QApplication, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
    QIcon, QLabel, QPushButton, QVBoxLayout)

import Lib
import Spell
from Config import Gopt


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        self.setWindowTitle("Forget Spelling Words — {}".format(
                            QApplication.applicationName()))
        words = sorted(
            self.state.entryPanel.spellHighlighter.wordsToIgnore |
            set(self.state.model.spellWords()), key=str.casefold)
        if words:
            self.initialize(words)
        else:
            self.nowords()
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def nowords(self):
        label = QLabel("<p>No ignored or index dictionary words to "
                       "remove")
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.helpButton.clicked.connect(self.help)
        self.tooltips.append((self.helpButton,
                              "Help on the Forget Spelling Words dialog"))
        closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                  "&Close")
        self.tooltips.append((closeButton, """<p><b>Close</b></p>
<p>Close the dialog.</p>"""))
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(closeButton, QDialogButtonBox.RejectRole)
        buttonBox.rejected.connect(self.reject)
        buttonBox.addButton(self.helpButton, QDialogButtonBox.HelpRole)
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(buttonBox)
        self.setLayout(layout)


    def initialize(self, words):
        self.removeComboBox = QComboBox()
        self.removeComboBox.addItems(words)
        self.tooltips.append((self.removeComboBox, """\
<p><b>Spelling Words combobox</b></p>
<p>This index's list of words that have been remembered as correctly
spelled or to be ignored even though they aren't in the dictionary for
the index's language.</p>"""))
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.tooltips.append((self.helpButton,
                              "Help on the Forget Spelling Words dialog"))
        self.removeButton = QPushButton(QIcon(":/spelling-remove.svg"),
                                        "&Forget")
        self.tooltips.append((self.removeButton, """\
<p><b>Forget</b></p>
<p>Permanently forget the selected word from the index's spelling words
list. Afterwards, if this word appears in any entry, it will be
highlighted as misspelled.</p>"""))
        closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                  "&Close")
        self.tooltips.append((closeButton, """<p><b>Close</b></p>
<p>Close the dialog.</p>"""))
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton(closeButton, QDialogButtonBox.RejectRole)
        self.buttonBox.addButton(
            self.removeButton, QDialogButtonBox.ApplyRole)
        self.buttonBox.addButton(self.helpButton, QDialogButtonBox.HelpRole)
        layout = QFormLayout()
        layout.addRow("F&orget", self.removeComboBox)
        layout.addRow(self.buttonBox)
        self.setLayout(layout)
        self.helpButton.clicked.connect(self.help)
        self.removeButton.clicked.connect(self.remove)
        self.buttonBox.rejected.connect(self.reject)


    def help(self):
        self.state.help("xix_ref_dlg_spelldel.html")


    def remove(self):
        word = self.removeComboBox.currentText()
        if word:
            i = self.removeComboBox.currentIndex()
            self.removeComboBox.removeItem(i)
            self.state.entryPanel.spellHighlighter.wordsToIgnore.discard(
                word)
            self.state.model.removeSpellWord(word)
            Spell.remove(word, self.state.language.value)
            self.state.entryPanel.spellHighlighter.rehighlight()
            if not self.removeComboBox.count():
                self.accept()
