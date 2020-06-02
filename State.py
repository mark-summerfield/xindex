#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import collections
import time

from PySide.QtCore import QObject, QSettings, Qt
from PySide.QtGui import QApplication, QDesktopServices

import Forms
import HelpForm
import Lib
import Pages
import Saf
import SortAs
import Username
import Xix
from Config import Gconf, Gopt
from Const import (
    CountKind, LABEL_TEMPLATE, LanguageKind, MAIN_INDICATOR,
    MAX_DYNAMIC_ACTIONS, ModeKind, ROOT, say, SAY_TIMEOUT,
    SUB_INDICATOR, WIN)


class State(QObject):

    def __init__(self, window, *, parent=None):
        super().__init__(parent)
        self.printer = None
        self.user = Username.name()
        self.indexPath = QDesktopServices.storageLocation(
            QDesktopServices.DocumentsLocation)
        self.outputPath = self.importPath = self.indexPath
        self.model = Xix.Model.Model(self.user)
        self.startCount = 0
        self.workTime = 0
        self.entryPanel = None
        self.spellPanel = None
        self.viewAllPanel = None
        self.viewFilteredPanel = None
        self.replacePanel = None
        self.window = window
        self.helpForm = None
        self.saving = False
        self.editors = set()
        self.gotoEids = collections.deque(maxlen=MAX_DYNAMIC_ACTIONS)
        self.mode = ModeKind.NO_INDEX
        self.spell = True
        self.pagesCache = ""
        self.showMessageTime = 10000
        self.initializeDisplayFonts()


    def initializeDisplayFonts(self):
        settings = QSettings()
        size = self.window.font().pointSize() + (1 if WIN else 2)
        self.stdFontFamily = settings.value(Gopt.Key.StdFont, Gopt.StdFont)
        self.stdFontSize = int(settings.value(Gopt.Key.StdFontSize, size))
        self.altFontFamily = settings.value(Gopt.Key.AltFont, Gopt.AltFont)
        self.altFontSize = int(settings.value(Gopt.Key.AltFontSize, size))
        self.monoFontFamily = settings.value(Gopt.Key.MonoFont,
                                             Gopt.MonoFont)
        self.monoFontSize = int(settings.value(Gopt.Key.MonoFontSize,
                                               size - 1))


    def updateDisplayFonts(self):
        self.initializeDisplayFonts()
        for widget in (self.viewFilteredPanel, self.viewAllPanel,
                       self.entryPanel):
            widget.updateDisplayFonts()


    @property
    def language(self):
        return (self.model.config(Gconf.Key.Language)
                if self.model else LanguageKind.AMERICAN)


    def createConnections(self):
        self.viewAllPanel.view.selectedEidChanged.connect(self.viewEntry)
        self.viewAllPanel.gotoLineEdit.textEdited.connect(
            self.window.gotoActions.gotoPrefix)
        self.model.loaded.connect(self.loaded)


    def loaded(self):
        if len(self.model):
            self.viewEntry(self.viewAllPanel.view.selectedEid)
        self.startCount = len(self.model)
        self.workTime = self.model.config(Gconf.Key.Worktime, 0)
        self.startTime = int(time.monotonic())


    def setMode(self, mode):
        self.entryPanel.addingLabel.setVisible(mode is ModeKind.ADD)
        self.mode = mode
        color = "green"
        if mode is ModeKind.VIEW:
            color = "navy"
        elif mode is ModeKind.CHANGE:
            color = "darkred"
        message = mode.value
        if mode is ModeKind.VIEW:
            if not len(self.model):
                color = "green"
                message = ("Press <b>F7</b> or click an "
                           "<b>Entry→Add</b>… action")
            elif self.entryPanel.entry is not None:
                top = ("<font color=#008080>Viewing {} Main Entry</font>"
                       .format(MAIN_INDICATOR))
                sub = ("<font color=#008F8F>Viewing {} Subentry</font>"
                       .format(SUB_INDICATOR))
                message = (top if self.entryPanel.entry.peid == ROOT else
                           sub)
        elif mode is ModeKind.NO_INDEX:
            message = "Press <b>Ctrl+N</b> or click <b>File→New Index</b>"
        self.window.modeLabel.setText("<font color={}>{}</font>".format(
                                      color, message))
        self.updateUi()


    def updateUi(self):
        restoreFocus = (self.mode in {ModeKind.ADD, ModeKind.EDIT} and
                        self.entryPanel.hasFocus())
        self.entryPanel.updateUi()
        self.spellPanel.updateUi()
        self.viewAllPanel.view.updateUi()
        self.viewFilteredPanel.view.updateUi()
        self.replacePanel.updateUi()
        self.window.updateUi()
        if restoreFocus:
            self.entryPanel.termEdit.setFocus()


    def close(self):
        self.window.close()


    def closeModel(self):
        self.maybeSave()
        self.model.close()


    def maybeSave(self, *, keepSortAs=False):
        if self.mode not in {ModeKind.NO_INDEX, ModeKind.VIEW,
                             ModeKind.CHANGE}:
            self.save(keepSortAs=keepSortAs)


    def save(self, *, keepSortAs=False, name=None):
        if self.saving:
            return
        self.saving = True
        try:
            if not keepSortAs:
                saf = self.entryPanel.saf
                if self.entryPanel.calcSortAsCheckBox.isChecked():
                    if saf == Saf.CUSTOM:
                        saf = Saf.AUTO
                else:
                    saf = Saf.CUSTOM
                sortas = self.entryPanel.sortAsEdit.toPlainText()
                if saf != Saf.CUSTOM or not sortas:
                    self.calculateSortAs(saf,
                                         force=self.mode is ModeKind.ADD)
            if self.mode is ModeKind.ADD:
                self.add()
            else:
                self.edit(name)
            pages = self.entryPanel.pagesEdit.toHtml()
            if pages:
                self.pagesCache = pages
        finally:
            self.saving = False
            self.setMode(ModeKind.VIEW)


    def calculateSortAs(self, saf, *, force=False):
        term = self.entryPanel.termEdit.toHtml()
        if not term:
            self.entryPanel.sortAsEdit.clear()
        else:
            isSubentry = (self.entryPanel.peid or ROOT
                          if self.mode is ModeKind.ADD else
                          self.entryPanel.entry.peid) is not ROOT
            candidates = self.model.sortByCandidates(term, isSubentry)
            sortas = self.entryPanel.sortAsEdit.toPlainText().strip()
            if not force and sortas:
                for candidate in candidates:
                    if sortas == candidate.candidate:
                        break # No need to force if we've matched
                else:
                    force = True
            if force or not sortas:
                self._calculateSortAs(term, candidates)


    def _calculateSortAs(self, term, candidates):
        widget = QApplication.focusWidget()
        if len(candidates) == 1:
            sortas = candidates[0].candidate
            saf = candidates[0].saf
        else:
            result = Forms.SortAs.Result()
            with Lib.Qt.DisableUI(*self.window.widgets(),
                                  forModalDialog=True):
                form = Forms.SortAs.Form(self, term, candidates, result,
                                         self.window)
                form.exec_()
            sortas = result.sortas
            saf = result.saf
        if saf == Saf.CUSTOM:
            with Lib.BlockSignals(self.entryPanel.calcSortAsCheckBox):
                self.entryPanel.calcSortAsCheckBox.setChecked(False)
        self.entryPanel.sortAsEdit.setPlainText(sortas)
        self.entryPanel.saf = saf
        self.maybeSave()
        Lib.restoreFocus(widget)


    def add(self):
        term = self.entryPanel.termEdit.toHtml()
        if not term:
            return
        saf = self.entryPanel.saf
        sortas = self.entryPanel.sortAsEdit.toPlainText()
        pages = self.entryPanel.pagesEdit.toHtml() or None
        if pages:
            pages = self._sortedPages(pages)
        notes = self.entryPanel.notesEdit.toHtml() or None
        peid = self.entryPanel.peid or ROOT
        entry = self.model.addEntry(saf, sortas, term, pages=pages,
                                    notes=notes, peid=peid)
        self.entryPanel.setEntry(entry)


    def edit(self, name=None):
        entry = self.entryPanel.entry
        if entry is None:
            return
        term = self.entryPanel.termEdit.toHtml()
        if not term:
            return
        changed = False
        if term != entry.term:
            changed = True
        sortas = self.entryPanel.sortAsEdit.toPlainText()
        saf = Saf.CUSTOM
        if self.entryPanel.calcSortAsCheckBox.isChecked():
            saf = self.entryPanel.saf or entry.saf or Saf.AUTO
        if saf != entry.saf or sortas != entry.sortas:
            changed = True
        pages = self.entryPanel.pagesEdit.toHtml()
        if pages is not None:
            oldPages = pages
            pages = self._sortedPages(pages)
            if oldPages != pages: # Update if visual but not internal change
                self.entryPanel.pagesEdit.setHtml(pages)
        if pages != entry.pages:
            changed = True
        notes = self.entryPanel.notesEdit.toHtml()
        if notes != entry.notes:
            changed = True
        if changed:
            self.model.editEntry(entry, saf, sortas, term, pages, notes,
                                 name=name)
            # No need to call setEntry() since refreshEntry() will be
            # called due to the changed signal.


    def _sortedPages(self, pages):
        try:
            pageRange = Pages.RulesForName[
                self.model.pageRangeRules()].function
            return Pages.sortedPages(pages, pageRange)
        except Pages.Error as err:
            say(err)


    def refreshEntry(self, eid):
        entry = self.model.entry(eid, withIndent=True,
                                 withXrefIndicator=True)
        if entry is not None:
            with Lib.BlockSignals(self.entryPanel):
                self.entryPanel.setEntry(entry)
            self.viewAllPanel.view.updateCache(entry)
            self.viewFilteredPanel.requery()
            self.viewFilteredPanel.view.updateCache(entry)
            self.updateUi()


    def viewEntry(self, eid=None):
        # Either we are editing or viewing (see also cancelAdd())
        if self.mode is not ModeKind.ADD or eid is None:
            if eid is None:
                eid = self.viewAllPanel.view.selectedEid
            with Lib.BlockSignals(self.entryPanel):
                self.entryPanel.setEntry(self.model.entry(eid))
            self.setMode(ModeKind.VIEW)


    def undo(self):
        widget = QApplication.focusWidget()
        if self.model.isUndoMacro:
            say("Undoing…")
            eid = self.viewAllPanel.view.selectedEid
            with Lib.DisableUI(*self.window.widgets()):
                self.model.undo()
            say("Undone", SAY_TIMEOUT)
        else:
            eid = self.model.undo()
        self._postUndoOrRedoRefresh(eid, widget)


    def redo(self):
        widget = QApplication.focusWidget()
        if self.model.isRedoMacro:
            say("Redoing…")
            eid = self.viewAllPanel.view.selectedEid
            with Lib.DisableUI(*self.window.widgets()):
                self.model.redo()
            say("Redone", SAY_TIMEOUT)
        else:
            eid = self.model.redo()
        self._postUndoOrRedoRefresh(eid, widget)


    def _postUndoOrRedoRefresh(self, eid, widget):
        if eid is not None:
            self.viewAllPanel.view.gotoEid(eid)
        else:
            self.entryPanel.clearForm()
            self.viewAllPanel.view.refresh()
            self.viewFilteredPanel.view.refresh()
        self.setMode(ModeKind.VIEW)
        self.window.refreshBookmarks()
        self.updateNavigationStatus()
        Lib.restoreFocus(widget)


    def indicatorCounts(self):
        if bool(self.model):
            top = self.model.count(CountKind.TOP_LEVEL_ENTRIES)
            total = self.model.count(CountKind.ENTRIES)
            filtered = self.viewFilteredPanel.view.count()
            return top, total, filtered
        return 0, 0, 0


    def applyFilter(self):
        sizes = self.window.panelSplitter.sizes()
        if sizes[1] < 20:
            fifth = sum(sizes) // 5
            self.window.panelSplitter.setSizes([fifth, fifth * 4])
        if self.viewFilteredPanel.filterTextComboBox.isEnabled():
            self.viewFilteredPanel.filterTextComboBox.setFocus()
            editor = self.viewFilteredPanel.filterTextComboBox.lineEdit()
            if editor is not None:
                editor.selectAll()
            self.viewFilteredPanel.setMatch()
        else:
            self.viewFilteredPanel.filterComboBox.setFocus()


    def updateGotoEids(self, eid):
        if eid is not None:
            try:
                self.gotoEids.remove(eid)
            except ValueError:
                pass # OK whether it is there or not
            self.gotoEids.appendleft(eid)
            self.window.updateGotoMenu()


    def setSortAsRules(self, name, prefix=None, reportProgress=None):
        rules = SortAs.RulesForName[name]
        say("Updating Sort As texts for “{}” rules…".format(rules.name))
        self.setMode(ModeKind.CHANGE)
        QApplication.sendPostedEvents(None, 0)
        QApplication.processEvents()
        try:
            eid = self.viewAllPanel.view.selectedEid
            self.model.setSortAsRules(name, prefix, reportProgress)
            self.window.sortAsRuleLabel.setText(LABEL_TEMPLATE.format(
                                                rules.abbrev))
            self.window.sortAsRuleLabel.setToolTip(Lib.rulesTip(rules.tip))
            self.viewAllPanel.view.gotoEid(eid)
        finally:
            say("Updated Sort As texts for “{}” rules".format(rules.name),
                SAY_TIMEOUT)
            self.setMode(ModeKind.VIEW)
            QApplication.sendPostedEvents(None, 0)
            QApplication.processEvents()


    def setPageRangeRules(self, name, prefix=None, reportProgress=None):
        rules = Pages.RulesForName[name]
        say("Updating Pages texts for “{}” rules…".format(rules.name))
        self.setMode(ModeKind.CHANGE)
        QApplication.sendPostedEvents(None, 0)
        QApplication.processEvents()
        try:
            eid = self.viewAllPanel.view.selectedEid
            self.model.setPageRangeRules(name, prefix, reportProgress)
            self.window.pageRangeRulesLabel.setText(LABEL_TEMPLATE.format(
                                                    rules.abbrev))
            self.window.pageRangeRulesLabel.setToolTip(
                Lib.rulesTip(rules.tip, False))
            self.viewAllPanel.view.gotoEid(eid)
        finally:
            say("Updated Pages texts for “{}” rules".format(rules.name),
                SAY_TIMEOUT)
            self.setMode(ModeKind.VIEW)
            QApplication.sendPostedEvents(None, 0)
            QApplication.processEvents()


    def help(self, page=None):
        settings = QSettings()
        keepHelpOnTop = bool(int(settings.value(
            Gopt.Key.KeepHelpOnTop, Gopt.Default.KeepHelpOnTop)))
        if self.helpForm is not None:
            original = flags = self.helpForm.windowFlags()
            if keepHelpOnTop:
                flags |= Qt.WindowStaysOnTopHint
            else:
                flags &= ~Qt.WindowStaysOnTopHint
            if int(original) != int(flags): # Reopen with new flag
                self.helpForm.close()
                self.helpForm = None
        if self.helpForm is None:
            self.helpForm = HelpForm.Form("xix_help.html",
                                          stayOnTop=keepHelpOnTop)
        if page is not None:
            self.helpForm.changePage(page)
        self.helpForm.show()
        self.helpForm.raise_()
        self.helpForm.activateWindow()


    def updateNavigationStatus(self):
        if (self.viewFilteredPanel.view.selectedEid is None or
                not self.viewFilteredPanel.view.lineCount):
            message = "No entries match the filter"
        elif (self.viewAllPanel.view.selectedEid !=
                self.viewFilteredPanel.view.selectedEid):
            message = ("The filtered entry isn't the current entry: "
                       "press F3 to navigate")
        else:
            message = "The filtered entry is the current entry"
        say(message, SAY_TIMEOUT)
