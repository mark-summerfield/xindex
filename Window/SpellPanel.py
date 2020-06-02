#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Qt
from PySide.QtGui import (
    QHBoxLayout, QIcon, QLabel, QToolButton, QVBoxLayout, QWidget)

import Lib
import Spell
import Widgets
from Const import ModeKind


@Lib.updatable_tooltips
class Panel(QWidget):

    def __init__(self, state, parent=None):
        super().__init__(parent=parent)
        self.state = state
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.initialize()


    def createWidgets(self):
        self.label = QLabel("Suggestions")
        self.spellList = Widgets.List.HtmlListWidget(self.state)
        self.tooltips.append((self.spellList, """
<p><b>Suggestions</b> (Alt+N,Tab)</p>
<p>A (possibly empty) list of completions or replacements for the word
being typed in the <b>Term</b> editor.</p>"""))
        self.label.setBuddy(self.spellList)
        self.closeButton = QToolButton()
        self.closeButton.setIcon(QIcon(":/hide.svg"))
        self.closeButton.setFocusPolicy(Qt.NoFocus)
        self.tooltips.append((self.closeButton, """<p><b>Hide</b></p>
<p>Hide the Suggestions panel.</p>
<p>Use <b>Spelling→Show Suggestions and Groups</b> to show it
again.</p>"""))
        self.helpButton = QToolButton()
        self.helpButton.setIcon(QIcon(":/help.svg"))
        self.helpButton.setFocusPolicy(Qt.NoFocus)
        self.tooltips.append((self.helpButton,
                              "Help on the Suggestions panel."))

    def layoutWidgets(self):
        layout = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addStretch()
        hbox.addWidget(self.closeButton)
        hbox.addWidget(self.helpButton)
        layout.addLayout(hbox)
        layout.addWidget(self.spellList)
        self.setLayout(layout)


    def createConnections(self):
        self.closeButton.clicked.connect(self.state.window.closeSuggestions)
        self.helpButton.clicked.connect(self.help)


    def initialize(self):
        self.spellList.itemDoubleClicked.connect(self.complete)
        self.tooltips.append((self, """<p><b>Suggestions panel</b></p>
<p>When the text cursor is at the end of a word in the term line edit,
any suggestions for completing the word are listed here. To accept a
suggestion press <b>Ctrl+<i>number</i></b> or click one of the
<b>Spelling→Replace</b> menu options.</p>"""))


    def complete(self, item):
        self.state.entryPanel.completeWord(item.text())


    def updateUi(self):
        enable = self.state.mode not in {ModeKind.NO_INDEX, ModeKind.CHANGE}
        self.setEnabled(enable)


    def populateSuggestions(self, word):
        self.clearSuggestions()
        self.spellList.clear()
        actions = self.state.window.spellingActions.completionActions
        suggestions = Spell.suggest(word, self.state.language.value)
        try:
            suggestions.remove(word)
        except ValueError:
            pass # OK if word isn't in suggestions
        for i, suggestion in enumerate(suggestions):
            if i < 9:
                text = "[Ctrl+{}] {}".format(i + 1, suggestion)
                actions[i].setText("&{} Replace with “{}”".format(i + 1,
                                   suggestion))
                actions[i].setVisible(True)
            else:
                text = suggestion
            self.spellList.addItem(text)
        self.spellList.setCurrentRow(0 if self.spellList.count() else -1)
        self.state.window.spellingActions.updateUi()


    def clearSuggestions(self):
        self.spellList.clear()
        for action in self.state.window.spellingActions.completionActions:
            action.setVisible(False)
        self.state.window.spellingActions.updateUi()


    def help(self):
        self.state.help("xix_ref_panel_sug.html")


    def __getattr__(self, name):
        return getattr(self.spellList, name)
