#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import Window._ReplacePanel as _ReplacePanel
else:
    from . import _ReplacePanel

import re

from PySide.QtCore import QSettings
from PySide.QtGui import QApplication, QTextCursor, QWidget

import Lib
import Xix.Searcher
from Const import FilterKind, say, SearchFieldKind


class Options:

    def __init__(self, *, pattern, literal, replacement, ignorecase,
                 wholewords, filter, match, terms, pages, notes):
        # self.pattern and str.literal are mutually exclusive
        self.pattern = pattern # str: if regex is checked
        self.literal = literal # str: if literal is checked
        self.replacement = replacement # str: may be empty to delete
        self.ignorecase = ignorecase # bool
        self.wholewords = wholewords # bool
        self.filter = filter # FilterKind if searching filtered else None
        self.match = match # str: for filter (may be empty)
        self.terms = terms # bool: search terms
        self.pages = pages # bool: search pages
        self.notes = notes # bool: search notes


    def __str__(self):
        return "{!r}→{!r} IC={} WW={} f={} m={} T={} P={} N={}".format(
            self.pattern or self.literal, self.replacement,
            self.ignorecase, self.wholewords, self.filter, self.match,
            self.terms, self.pages, self.notes)


@Lib.updatable_tooltips
class Panel(QWidget, _ReplacePanel.Mixin):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.stopped = False
        self.searcher = Xix.Searcher.Searcher(
            self.state.window.reportProgress)
        self.searchMatch = None
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.tooltips.append((self,
                              "<p><b>Search and Replace panel</b></p>"))


    def showEvent(self, event):
        self.updateUi()
        super().showEvent(event)


    def saveSettings(self):
        settings = QSettings()
        settings.setValue("RP/All",
                          int(self.allEntriesRadioButton.isChecked()))
        settings.setValue("RP/Filtered",
                          int(self.filteredEntriesRadioButton.isChecked()))
        settings.setValue("RP/Literal",
                          int(self.literalRadioButton.isChecked()))
        settings.setValue("RP/Regex",
                          int(self.regexRadioButton.isChecked()))
        settings.setValue("RP/ICase",
                          int(self.ignoreCaseCheckBox.isChecked()))
        settings.setValue("RP/WW", int(self.wholeWordsCheckBox.isChecked()))
        settings.setValue("RP/Terms",
                          int(self.replaceInTermsCheckBox.isChecked()))
        settings.setValue("RP/Pages",
                          int(self.replaceInPagesCheckBox.isChecked()))
        settings.setValue("RP/Notes",
                          int(self.replaceInNotesCheckBox.isChecked()))


    def replace(self):
        editor = self._searchEditor()
        if editor is not None:
            editor.setHtml(self.searchMatch.text)
            keepSortAs = self.searchMatch.field is SearchFieldKind.TERM
            self.state.maybeSave(keepSortAs=keepSortAs)
            # Uses an undoable EditEntry
            self._search()


    def skip(self):
        self._search() # Just find the next match if there is one


    def start(self):
        if self.regexRadioButton.isChecked():
            try:
                re.compile(self.searchLineEdit.text())
            except re.error as err:
                say("Invalid regex pattern: {}".format(err))
                return
        self.stopped = False
        say("Searching…")
        self.searcher.prepare(self.state.model, self.options())
        self.updateUi()
        self._search(started=True)


    def stop(self, msg="Search stopped"):
        self.stopped = True
        self.searcher.stop()
        self.updateUi()
        say(msg)


    def _search(self, *, started=False):
        self.searchMatch = self.searcher.search()
        if self.stopped:
            return # Already handled
        if self.searchMatch is None:
            self.stop("None found" if started else "No (more) found")
        else:
            if self.filteredEntriesRadioButton.isChecked():
                self.state.viewFilteredPanel.view.gotoEid(
                    self.searchMatch.eid)
            self.state.viewAllPanel.view.gotoEid(self.searchMatch.eid)
            editor = self._searchEditor()
            if editor is not None:
                cursor = editor.textCursor()
                cursor.setPosition(self.searchMatch.start)
                cursor.setPosition(self.searchMatch.end,
                                   QTextCursor.KeepAnchor)
                editor.setTextCursor(cursor)
            say("Found: Click Replace or Skip or Stop Search")
        self.updateUi()


    def _searchEditor(self):
        if self.searchMatch.field is SearchFieldKind.TERM:
            return self.state.entryPanel.termEdit
        elif self.searchMatch.field is SearchFieldKind.PAGES:
            return self.state.entryPanel.pagesEdit
        if self.searchMatch.field is SearchFieldKind.NOTES:
            return self.state.entryPanel.notesEdit


    def updateUi(self):
        if not bool(self.state.model) or len(self.state.model) < 2:
            self.setEnabled(False)
        else:
            self.setEnabled(True)
            if not self.searcher.running:
                filtered = (0 if not bool(self.state.model) else
                            self.state.viewFilteredPanel.view.count())
                if filtered:
                    self.filteredEntriesRadioButton.setEnabled(True)
                else:
                    self.filteredEntriesRadioButton.setEnabled(False)
                    self.allEntriesRadioButton.setChecked(True)
            for widget in (self.searchLineEdit, self.replaceLineEdit,
                           self.allEntriesRadioButton,
                           self.filteredEntriesRadioButton,
                           self.literalRadioButton,
                           self.regexRadioButton,
                           self.wholeWordsCheckBox,
                           self.ignoreCaseCheckBox,
                           self.replaceInTermsCheckBox,
                           self.replaceInPagesCheckBox,
                           self.replaceInNotesCheckBox):
                widget.setDisabled(self.searcher.running)
            if self.regexRadioButton.isChecked():
                self.wholeWordsCheckBox.setDisabled(True)
            self.startButton.setEnabled(
                bool(self.searchLineEdit.text()) and
                (self.replaceInTermsCheckBox.isChecked() or
                 self.replaceInPagesCheckBox.isChecked() or
                 self.replaceInNotesCheckBox.isChecked()))
            self.replaceButton.setEnabled(self.searchMatch is not None)
            self.skipButton.setEnabled(self.searchMatch is not None)
            self.stopButton.setEnabled(self.searcher.running)


    def options(self):
        pattern = literal = None
        if self.literalRadioButton.isChecked():
            literal = self.searchLineEdit.text()
        else:
            pattern = self.searchLineEdit.text()
        ignorecase = self.ignoreCaseCheckBox.isChecked()
        wholewords = self.wholeWordsCheckBox.isChecked()
        filter = None
        match = ""
        if self.filteredEntriesRadioButton.isChecked():
            filter = self.state.viewFilteredPanel.view.filter
            match = self.state.viewFilteredPanel.view.match
        terms = self.replaceInTermsCheckBox.isChecked()
        pages = self.replaceInPagesCheckBox.isChecked()
        notes = self.replaceInNotesCheckBox.isChecked()
        return Options(pattern=pattern, literal=literal,
                       replacement=self.replaceLineEdit.text(),
                       ignorecase=ignorecase, wholewords=wholewords,
                       filter=filter, match=match, terms=terms,
                       pages=pages, notes=notes)


if __name__ == "__main__":
    import collections
    import Qrc # noqa
    import HelpForm
    import Saf
    Entry = collections.namedtuple(
        "Entry", "eid saf sortas term pages notes peid")
    class FakeModel:
        def entries(self, *args, **kwargs):
            for x in (1, 5, 7, 11):
                yield 0, x
        def filteredEntries(self, *args, **kwargs):
            for x in (8, 16, 31, 4):
                yield x
        def entry(self, eid):
            if eid == 1:
                return Entry(eid, Saf.AUTO, "henry 0008 of agincourt",
                             "<b>Henry VIII</b> of Agincourt",
                             "1, 14, 24, <i>35-38</i>, 91, <b>103t</b>",
                             "No interesting notes <i>at all!</>", 0)
            return Entry(eid, Saf.AUTO, "0020 century",
                         "<b>XX Century Timeline</b>",
                         "31, 34, <i>45-48</i>, 191, <b>108f</b>",
                         "Just some uninteresting notes<p>that's all.", 0)
        def __len__(self):
            return 4
    class FakeView:
        def __init__(self):
            self.filter = FilterKind.TERMS_MATCHING
            self.match = ""
        def count(self):
            return 3
    class FakeFilteredPanel:
        def __init__(self):
            self.view = FakeView()
    class FakeWindow:
        def reportProgress(self, *args):
            pass
    class FakeState:
        def __init__(self):
            self.model = FakeModel()
            self.stdFontFamily = "Times New Roman"
            self.stdFontSize = 13
            self.altFontFamily = "Arial"
            self.altFontSize = 13
            self.monoFontFamily = "Courier New"
            self.monoFontSize = 12
            self.viewFilteredPanel = FakeFilteredPanel()
            self.window = FakeWindow()
            self.helpForm = None
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
    form = Panel(state)
    state.window = form
    form.show()
    app.exec_()
