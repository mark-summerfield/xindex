#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import collections
import re

from PySide.QtCore import QSettings, Qt
from PySide.QtGui import (
    QApplication, QCheckBox, QFormLayout, QHBoxLayout, QIcon, QLabel,
    QListWidgetItem, QToolButton, QVBoxLayout, QWidget)

import Lib
import Saf
import Spell
import State
import Widgets
from Config import Gopt
from Const import (
    CANCEL_ADD, ModeKind, ROOT, TOOLTIP_IMAGE_SIZE, XREF_INDICATOR,
    XrefKind)


Positions = collections.namedtuple("Positions", "term sortas pages notes")

COMPLETE_WORD_RX = re.compile(r"^[[]Ctrl[+]\d[]]\s*")


@Lib.updatable_tooltips
class Panel(QWidget):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.entry = None
        self.saf = Saf.AUTO
        self.peid = ROOT
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.showOrHideNotes()
        self.showOrHideSortAs()
        self.termEdit.setFocus()


    def createWidgets(self):
        self.helpButton = QToolButton()
        self.helpButton.setIcon(QIcon(":/help.svg"))
        self.helpButton.setFocusPolicy(Qt.NoFocus)
        self.tooltips.append((self.helpButton, "Help on the Entry panel."))
        self.addingLabel = Widgets.Label.HtmlLabel(CANCEL_ADD)
        self.addingLabel.hide()
        self.termLabel = QLabel("&Term")
        self.termEdit = Widgets.LineEdit.HtmlLineEdit(self.state)
        self.tooltips.append((self.termEdit, """\
<p><b>Term editor</b> (Alt+T)</p>
<p>The entry's term text styled (e.g., <b>bold</b>, <i>italic</i>), as
it should appear in the final index.</p>"""))
        self.spellHighlighter = Widgets.SpellHighlighter.Highlighter(
            self.state, self.termEdit.document())
        self.termLabel.setBuddy(self.termEdit)
        self.pagesLabel = QLabel("&Pages")
        self.pagesEdit = Widgets.LineEdit.HtmlPagesLineEdit(self.state,
                                                            maxLines=3)
        self.tooltips.append((self.pagesEdit, """\
<p><b>Pages editor</b> (Alt+P)</p>
<p>The entry's pages styled (e.g., <b>bold</b>, <i>italic</i>), as they
should appear in the final index.</p> <p>The pages are automatically
sorted, and exact duplicates are automatically removed.</p> <p>See also
<b>Index→Combine Overlapping Pages</b> and <b>Index→Renumber
Pages</b>.</p>"""))
        self.pagesLabel.setBuddy(self.pagesEdit)
        self.calcSortAsCheckBox = QCheckBox(
            "&Automatically Calculate Sort As")
        self.tooltips.append((self.calcSortAsCheckBox, """\
<p><b>Automatically Calculate Sort As</b> (Alt+A)</p>
<p>This checkbox controls how the Sort As text is created.</p>
<p>If checked, {} will either automatically create the sort as
text, or will present some choices from which to choose the sort as
text, depending on the term text.</p>
<p>If unchecked, the sort as text should be entered
manually.</p>""".format(QApplication.applicationName())))
        self.calcSortAsCheckBox.setChecked(True)
        self.sortAsHelpButton = QToolButton()
        self.sortAsHelpButton.setIcon(QIcon(":/help.svg"))
        self.sortAsHelpButton.setFocusPolicy(Qt.NoFocus)
        self.tooltips.append((self.sortAsHelpButton,
                              "Help on the Sort As text."))
        self.sortAsEdit = Widgets.LineEdit.LineEdit(self.state)
        self.tooltips.append((self.sortAsEdit, """\
<p><b>Sort As editor</b> (Alt+S)</p>
<p>The entry's sort as text.</p>
<p>If the <b>Automatically Calculate Sort As</b> checkbox is unchecked,
manually enter the sort as text to use for sorting the entry.</p>
<p>Main entry's are sorted using the sort as text, so it is easy to
force a non-standard ordering by entering a custom sort as text.</p>
<p>Subentries are also sorted using the sort as text, but the first word
of a subentry will be ignored for sorting purposes if it is in the
Ignore Subentry Function words list (see <b>Index→Ignore Subentry
Function words</b>) <i>and</i> the <b>Index→Options, Rules,
Ignore Subenty Function Words</b> checkbox is checked for this
index.</p>"""))
        self.sortAsEdit.setEnabled(False)
        self.sortAsLabel = QLabel("&Sort As")
        self.sortAsLabel.setBuddy(self.sortAsEdit)
        self.sortAsLabel.setEnabled(False)
        self.xrefLabel = QLabel("&Cross-references")
        self.xrefList = Widgets.List.HtmlListWidget(self.state, minLines=4)
        self.tooltips.append((self.xrefList, """\
<p><b>Cross-references list</b> (Alt+C)</p>
<p>The list of the entry's see and see also cross-references, both
generic and to other entries.</p>
<p>To add a cross-reference to an entry, circle the <i>to</i> entry
(<b>Entry→Circle</b>), then go to the <i>from</i> entry and click
<img src=":/xref-add.svg" width={0} height={0}> or press
<b>Entry→Add Cross-reference</b> (See also the <b>Entry</b>
menu.)</p>""".format(TOOLTIP_IMAGE_SIZE)))
        self.xrefLabel.setBuddy(self.xrefList)
        self.notesLabel = QLabel("&Notes")
        self.notesEdit = Widgets.LineEdit.MultilineHtmlEdit(self.state)
        self.tooltips.append((self.notesEdit, """\
<p><b>Notes editor</b> (Alt+N)</p>
<p>The entry's notes.</p>
<p>The notes shown here are never output as part of
the index so may be freely used for any purpose.</p>
<p>If the notes facility isn't wanted, the notes can be hidden by
unchecking the <b>Index→Options, General, Show Notes</b>
checkbox.</p>"""))
        self.notesLabel.setBuddy(self.notesEdit)


    def layoutWidgets(self):
        form = QFormLayout()
        form.addRow(self.addingLabel)
        hbox = QHBoxLayout()
        hbox.addWidget(self.termEdit, 1)
        hbox.addWidget(self.helpButton)
        form.addRow(self.termLabel, hbox)
        form.addRow(self.pagesLabel, self.pagesEdit)
        hbox = QHBoxLayout()
        hbox.addWidget(self.calcSortAsCheckBox, 1)
        hbox.addWidget(self.sortAsHelpButton)
        form.addRow(hbox)
        form.addRow(self.sortAsLabel, self.sortAsEdit)
        vbox = QVBoxLayout()
        vbox.addLayout(form)
        vbox.addWidget(self.xrefLabel)
        vbox.addWidget(self.xrefList, 1)
        vbox.addWidget(self.notesLabel)
        vbox.addWidget(self.notesEdit, 1)
        self.setLayout(vbox)


    def createConnections(self):
        self.helpButton.clicked.connect(self.help)
        self.sortAsHelpButton.clicked.connect(
            lambda: self.help("xix_ref_sortas.html"))
        self.termEdit.textChanged.connect(self.termChanged)
        self.termEdit.cursorPositionChanged.connect(
            self.maybeSetSuggestions)
        self.termEdit.textChanged.connect(self.updateMode)
        self.termEdit.lostFocus.connect(self.maybeSave)
        self.termEdit.enterPressed.connect(
            lambda: self.tabAndMaybeSave(self.pagesEdit))
        self.pagesEdit.textChanged.connect(self.updateMode)
        self.pagesEdit.lostFocus.connect(self.maybeSave)
        self.pagesEdit.enterPressed.connect(
            lambda: self.tabAndMaybeSave(self.calcSortAsCheckBox))
        self.calcSortAsCheckBox.toggled.connect(self.calcSortAsToggled)
        self.sortAsEdit.textChanged.connect(self.updateMode)
        self.sortAsEdit.lostFocus.connect(self.maybeSave)
        self.sortAsEdit.enterPressed.connect(
            lambda: self.tabAndMaybeSave(self.xrefList))
        self.notesEdit.textChanged.connect(self.updateMode)
        self.notesEdit.lostFocus.connect(self.maybeSave)


    def help(self, page="xix_ref_panel_entry.html"):
        self.state.help(page)


    def tabAndMaybeSave(self, widget):
        self.maybeSave()
        widget.setFocus()


    def updateUi(self):
        enable = self.state.mode not in {ModeKind.NO_INDEX, ModeKind.CHANGE}
        self.setEnabled(enable)
        if enable:
            enable = (self.state.mode in {ModeKind.ADD, ModeKind.EDIT} or
                      not self.termEdit.isEmpty())
            for widget in (self.termEdit, self.pagesEdit,
                           self.calcSortAsCheckBox, self.xrefList,
                           self.notesEdit):
                widget.setEnabled(enable)
            self.sortAsEdit.setEnabled(
                enable and not self.calcSortAsCheckBox.isChecked())
            if self.state.mode is ModeKind.ADD:
                self.state.window.modeLabel.setText(
                    "<font color=green>Adding</font>")


    def updateDisplayFonts(self):
        for widget in (self.termEdit, self.sortAsEdit, self.pagesEdit,
                       self.notesEdit, self.xrefList):
            widget.updateDisplayFonts()


    def populateEditors(self, editors):
        editors |= {self.termEdit, self.sortAsEdit, self.pagesEdit,
                    self.notesEdit}


    def maybeSave(self):
        if self.hasChanged():
            if not bool(self.sortAsEdit.toPlainText().strip()):
                sortas = self.state.model.sortBy(
                    self.termEdit.toHtml(), self.saf, self.peid is not ROOT)
                self.sortAsEdit.setPlainText(sortas)
            self.state.save()


    def hasChanged(self):
        term = self.termEdit.toHtml()
        sortas = self.sortAsEdit.toPlainText().strip()
        pages = self.pagesEdit.toHtml()
        notes = self.notesEdit.toHtml()
        if self.entry is None:
            return bool(term or sortas or pages or notes)
        return (self.entry.term != term or self.entry.sortas != sortas or
                self.entry.pages != pages or self.entry.notes != notes or
                self.entry.saf != self.saf)


    def updateMode(self):
        if (self.state.mode not in {ModeKind.NO_INDEX, ModeKind.ADD,
                                    ModeKind.EDIT, ModeKind.CHANGE} and
                self.hasChanged()):
            self.state.setMode(ModeKind.EDIT)


    def clearForm(self):
        self.state.spellPanel.clearSuggestions()
        self.state.groupsPanel.clear()
        positions = Positions(self.termEdit.textCursor().position(),
                              self.sortAsEdit.textCursor().position(),
                              self.pagesEdit.textCursor().position(),
                              self.notesEdit.textCursor().position())
        self.termEdit.clear()
        self.calcSortAsCheckBox.setChecked(True)
        self.sortAsEdit.clear()
        self.pagesEdit.clear()
        self.xrefList.clear()
        self.notesEdit.clear()
        return positions


    def setEntry(self, entry):
        positions = self.clearForm()
        self.entry = entry
        if entry is not None:
            self.termEdit.setHtml(entry.term, positions.term)
            self.saf = entry.saf or Saf.AUTO
            self.calcSortAsCheckBox.setChecked(self.saf != Saf.CUSTOM)
            self.sortAsEdit.setPlainText(entry.sortas, positions.sortas)
            self.pagesEdit.setHtml(entry.pages, positions.pages)
            self.notesEdit.setHtml(entry.notes, positions.notes)
            for xref in list(self.state.model.xrefs(entry.eid)):
                kind = "See" if xref.kind is XrefKind.SEE else "See also"
                term = Lib.elidePatchHtml(
                    self.state.model.termPath(xref.to_eid), self.state,
                    maxlen=None)
                item = QListWidgetItem("{} <i>{}</i> {}".format(
                                       XREF_INDICATOR, kind, term))
                item.setData(Qt.UserRole, xref)
                self.xrefList.addItem(item)
            for xref in list(self.state.model.generic_xrefs(entry.eid)):
                kind = ("See (generic)" if xref.kind is
                        XrefKind.SEE_GENERIC else "See also (generic)")
                item = QListWidgetItem("{} <i>{}</i> {}".format(
                                       XREF_INDICATOR, kind, xref.term))
                item.setData(Qt.UserRole, xref)
                self.xrefList.addItem(item)
            if self.xrefList.count():
                self.xrefList.setCurrentRow(0)
            self.state.updateGotoEids(entry.eid)
        self.state.groupsPanel.updateGroups()
        self.state.updateNavigationStatus()
        self.state.setMode(ModeKind.VIEW)


    @property
    def unknownWords(self):
        return self.spellHighlighter.unknownWords


    def termChanged(self):
        if self.addingLabel.isVisible():
            self.addingLabel.setText(CANCEL_ADD)
            text = self.termEdit.toPlainText()
            if bool(self.state.model):
                while text:
                    eid = self.state.model.firstForPrefix(text)
                    if eid is not None:
                        term = Lib.elidePatchHtml(
                            self.state.model.term(eid), self.state)
                        self.addingLabel.setText(
                            CANCEL_ADD + " and goto “{}”".format(term))
                        break
                    text = text[:-1]
        self.maybeSetSuggestions()


    def maybeSetSuggestions(self):
        word, _ = self.termEdit.wordAndPosition()
        if word:
            if self.termEdit.hasFocus():
                replacement = self.state.model.autoReplacementFor(word)
                if replacement is not None:
                    self.termEdit.replaceWord(replacement)
                    return
            self.state.spellPanel.populateSuggestions(word)
        else:
            self.state.spellPanel.clearSuggestions()


    def rememberWord(self):
        word = self.findNearestUnknownWord()
        if word:
            Spell.add(word, self.state.language.value)
            self.state.model.addSpellWord(word)
            self.spellHighlighter.rehighlight()


    def ignoreWord(self):
        word = self.findNearestUnknownWord()
        if word:
            self.spellHighlighter.wordsToIgnore.add(word)
            self.spellHighlighter.rehighlight()


    def findNearestUnknownWord(self):
        pos = self.termEdit.textCursor().position()
        where = -1
        unknownWord = None
        unknownWords = sorted(self.unknownWords)
        for i, word in unknownWords:
            if i > where and i <= pos:
                where = i
                unknownWord = word
            if i > pos:
                break
        if unknownWord is None and unknownWords:
            unknownWord = unknownWords[-1][1]
        return unknownWord


    def completeWithSuggested(self):
        index = self.state.spellPanel.currentRow()
        self.complete(index)


    def complete(self, i):
        item = self.state.spellPanel.item(i)
        if item:
            word = self.state.spellPanel.item(i).text()
            self.completeWord(word)


    def completeWord(self, word):
        word = COMPLETE_WORD_RX.sub("", word)
        if word:
            self.termEdit.replaceWord(word)


    def showOrHideNotes(self):
        settings = QSettings()
        visible = bool(int(settings.value(Gopt.Key.ShowNotes,
                                          Gopt.Default.ShowNotes)))
        self.notesLabel.setVisible(visible)
        self.notesEdit.setVisible(visible)


    def showOrHideSortAs(self):
        settings = QSettings()
        alwaysShowSortAs = bool(int(settings.value(
            Gopt.Key.AlwaysShowSortAs, Gopt.Default.AlwaysShowSortAs)))
        editable = not self.calcSortAsCheckBox.isChecked()
        visible = alwaysShowSortAs or editable
        for widget in (self.sortAsLabel, self.sortAsEdit):
            widget.setVisible(visible)
            widget.setEnabled(editable)


    def calcSortAsToggled(self):
        self.showOrHideSortAs()
        self.updateMode()
        if self.calcSortAsCheckBox.isChecked():
            saf = self.saf if self.saf != Saf.CUSTOM else Saf.AUTO
            self.state.calculateSortAs(saf, force=True)
        else:
            self.saf = Saf.CUSTOM


if __name__ == "__main__":
    import sys
    import unittest.mock
    app = QApplication(sys.argv)
    app.setOrganizationName("Qtrac Ltd.")
    app.setOrganizationDomain("qtrac.eu")
    app.setApplicationName("XindeX-Test")
    app.setApplicationVersion("1.0.0")
    class Window:
        pass
    window = Window()
    window.font = unittest.mock.MagicMock(return_value=app.font())
    window.formatActions = unittest.mock.MagicMock()
    state = State.State(window)
    state.spellPanel = unittest.mock.MagicMock()
    state.spellPanel.clearSuggestions = unittest.mock.MagicMock()
    panel = Panel(state)
    panel.show()
    app.exec_()
