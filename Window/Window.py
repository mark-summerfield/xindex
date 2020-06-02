#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

import os
import sys
import time

from PySide.QtCore import QDir, QSettings, Qt, QTimer
from PySide.QtGui import (
    QAction, QApplication, QIcon, QMainWindow, QMenu, QMessageBox,
    QPixmap)

import Lib
import Pages
import Qrc # noqa
import SortAs
import State
from Config import Gconf, Gopt
from Const import (COUNT_LABEL_TEMPLATE, EXTENSION, LABEL_TEMPLATE,
                   LanguageKind, ModeKind, say, SAY_TIMEOUT)
from . import _Goto
from . import _Window


class Window(QMainWindow, _Goto.Mixin, _Window.Mixin):

    def __init__(self, debug, parent=None):
        super().__init__(parent)
        Lib.Qt.DEBUGGING = self.debug = debug
        self.resizeTimer = QTimer(self)
        self.resizeTimer.setSingleShot(True)
        self.resizeTimer.timeout.connect(self.onResize)
        self.tooltips = []
        self.state = State.State(self)
        self.statusbar = self.statusBar()
        self.statusbar.setSizeGripEnabled(False)
        self.workTimer = QTimer(self)
        self.createWidgets()
        self.layoutWidgets()
        self.createActions()
        self.createConnections()
        self.state.createConnections()
        self.loadSettings()
        self.createContextMenus()
        self.workTimer.start(60 * 1000) # 1 minute
        self.state.setMode(ModeKind.NO_INDEX)
        self.initialize()
        self.show()


    def initialize(self):
        self.setWindowTitle("{}".format(QApplication.applicationName()))
        self.state.updateDisplayFonts()
        self.filename = None
        if len(sys.argv) > 1:
            filename = sys.argv[1]
            if (filename.lower().endswith(EXTENSION) and
                    os.path.exists(filename)):
                self.filename = filename
        if self.filename is None:
            settings = QSettings()
            filename = settings.value(Gopt.Key.MainForm_Filename,
                                      Gopt.Default.MainForm_Filename)
            if (filename and filename.lower().endswith(EXTENSION) and
                    os.path.exists(filename)):
                self.filename = filename
        if self.filename is None:
            say("Click File→New or File→Open to create or open an index")
            self.updateWorkTime()
            self.state.updateUi()
        else:
            say("Opening {}".format(os.path.normpath(self.filename)))
            QTimer.singleShot(5, self.openXix)
        self.updateRecentFilesMenu()
        self.updateToolTips()
        Lib.maybe_register_filetype(self.debug)


    def initializePanelSplitter(self):
        size = sum(self.panelSplitter.sizes())
        self.panelSplitter.setSizes([size * 0.1, size * 0.9])


    def loadSettings(self):
        settings = QSettings()
        self.restoreGeometry(settings.value(Gopt.Key.MainForm_Geometry))
        self.restoreState(settings.value(Gopt.Key.MainForm_State))
        self.setIndexViewPosition()
        self.splitter.restoreState(settings.value(
                                   Gopt.Key.MainForm_Splitter))
        panelState = settings.value(Gopt.Key.MainForm_PanelSplitter)
        if panelState is None:
            QTimer.singleShot(50, self.initializePanelSplitter)
        else:
            self.panelSplitter.restoreState(panelState)
        self.entrySuggestionSplitter.restoreState(
            settings.value(Gopt.Key.MainForm_EntrySuggestionsSplitter))
        self.spellAndGroupsSplitter.restoreState(
            settings.value(Gopt.Key.MainForm_SpellAndGroupsSplitter))
        viewState = settings.value(Gopt.Key.MainForm_ViewSplitter)
        if viewState is None:
            sizes = self.viewSplitter.sizes()
            self.viewSplitter.setSizes([sum(sizes), 0])
        else:
            self.viewSplitter.restoreState(viewState)
        self.recent_files = settings.value(
            Gopt.Key.MainForm_RecentFiles) or []
        if isinstance(self.recent_files, str):
            self.recent_files = [self.recent_files]


    def setIndexViewPosition(self):
        settings = QSettings()
        index = int(settings.value(Gopt.Key.MainForm_IndexViewPosition,
                                   Gopt.Default.MainForm_IndexViewPosition))
        self.splitter.insertWidget(index, self.viewSplitter)


    def updateUi(self):
        if self.resizing:
            return
        enable = bool(self.state.model)
        self.fileActions.saveAction.setEnabled(
            enable and self.state.mode is not ModeKind.VIEW)
        for action in (self.fileActions.backupAction,
                       self.fileActions.saveAsAction,
                       self.fileActions.printAction,
                       self.fileActions.outputRtfAction,
                       self.fileActions.outputDocxAction,
                       self.fileActions.outputAsAction):
            action.setEnabled(enable)
        enable = self.state.mode not in {ModeKind.NO_INDEX, ModeKind.CHANGE}
        for widget in (
                self.state.viewAllPanel, self.state.viewFilteredPanel,
                self.editMenu, self.editToolBar, self.formatMenu,
                self.formatToolBar, self.insertMenu, self.gotoMenu,
                self.gotoToolBar1, self.gotoToolBar2, self.gotoToolBar3,
                self.gotoToolBar4, self.entryMenu, self.entryToolBar1,
                self.entryToolBar2, self.modifyMenu, self.modifyToolBar,
                self.indexMenu, self.indexToolBar, self.spellingMenu,
                self.spellingToolBar, self.state.viewFilteredPanel):
            widget.setEnabled(enable)
        enable = bool(self.state.entryPanel.xrefList.count())
        self.entryActions.changeXRefAction.setEnabled(enable)
        self.entryActions.deleteXRefAction.setEnabled(enable)
        self.entryActions.updateUi()
        self.modifyActions.updateUi()
        total, filtered = self.updateIndicatorCounts()
        self.updateGotoActions(total, filtered)


    def updateIndicatorCounts(self):
        top, total, filtered = self.state.indicatorCounts()
        self.countLabel.setText(COUNT_LABEL_TEMPLATE.format(
            total, top, max(0, total - self.state.startCount), filtered))
        return total, filtered


    def updateWorkTime(self):
        if not self.state.model:
            message = "0'"
        else:
            secs = self.state.workTime + int(time.monotonic() -
                                             self.state.startTime)
            hours, secs = divmod(secs, 3600)
            if hours:
                message = "{:,}h{}'".format(hours, secs // 60)
            else:
                message = "{}'".format(secs // 60)
        self.worktimeLabel.setText(LABEL_TEMPLATE.format(message))


    def openXix(self, filename=None):
        if self.isReadOnly(filename if filename is not None else
                           self.filename):
            return
        self.closeXix()
        if filename is not None:
            self.filename = filename
        try:
            self.recent_files.remove(self.filename)
            self.updateRecentFilesMenu()
        except ValueError:
            pass # No problem if it isn't there to be removed
        self.state.indexPath = os.path.dirname(self.filename)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            say("Opening {}…".format(os.path.normpath(self.filename)))
            QApplication.processEvents()
            self.state.entryPanel.clearForm()
            self._openModel("Opened")
            self.state.entryPanel.termEdit.setFocus()
            self.state.updateUi()
            self.updateWorkTime()
            self.updateLanguageIndicator()
            self.state.setMode(ModeKind.VIEW)
            self.refreshBookmarks()
        finally:
            QApplication.restoreOverrideCursor()


    def newXix(self, filename):
        if self.isReadOnly(filename):
            return
        self.closeXix()
        self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            say("Creating {}…".format(os.path.normpath(self.filename)),
                SAY_TIMEOUT)
            QApplication.processEvents()
            self._openModel("Created")
            self.state.updateUi()
            self.updateWorkTime()
            self.state.entryPanel.clearForm()
            self.updateLanguageIndicator()
            self.state.setMode(ModeKind.VIEW)
        finally:
            QApplication.restoreOverrideCursor()


    def isReadOnly(self, filename):
        if (os.access(filename, os.R_OK) and
                not os.access(filename, os.W_OK)):
            QMessageBox.information(
                self, "Can't Open Read-Only Index — {}".format(
                    QApplication.applicationName()),
                """<p>Cannot open index<br>“{}”<br>
since the file and/or its folder is read-only.</p>""".format(
                    os.path.normpath(filename)))
            return True
        return False


    def _openModel(self, word):
        self.state.viewAllPanel.clear()
        self.state.viewFilteredPanel.clear()
        language, sortAsRules, pageRangeRules = self._getLanguageAndRules()
        with Lib.Timer("Opened in", 0.2):
            self.state.model.open(self.filename, language, sortAsRules,
                                  pageRangeRules)
            say("{} “{}”".format(word, os.path.normpath(self.filename)),
                self.state.showMessageTime)
        rules = SortAs.RulesForName[self.state.model.sortAsRules()]
        self.sortAsRuleLabel.setText(LABEL_TEMPLATE.format(rules.abbrev))
        self.sortAsRuleLabel.setToolTip(Lib.rulesTip(rules.tip))
        rules = Pages.RulesForName[self.state.model.pageRangeRules()]
        self.pageRangeRulesLabel.setText(LABEL_TEMPLATE.format(
                                         rules.abbrev))
        self.pageRangeRulesLabel.setToolTip(Lib.rulesTip(rules.tip, False))
        self.updateTitle()
        self.state.viewAllPanel.view.goHome()


    def importIndex(self, filename, inFilename):
        if self.isReadOnly(filename):
            return
        self.closeXix()
        Lib.remove_file(filename) # Don't want to merge!
        self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            say("Importing {}…".format(os.path.normpath(self.filename)),
                SAY_TIMEOUT)
            QApplication.processEvents()
            self._importIndex(filename, inFilename)
            self.state.entryPanel.termEdit.setFocus()
            self.state.updateUi()
            self.updateWorkTime()
            self.updateLanguageIndicator()
            self.state.setMode(ModeKind.VIEW)
        finally:
            QApplication.restoreOverrideCursor()


    # Why is filename ignored in favour of self.filename?
    def _importIndex(self, filename, inFilename):
        language, sortAsRules, pageRangeRules = self._getLanguageAndRules()
        with Lib.Timer("Imported in", 0.2):
            if self.state.model.importIndex(
                inFilename, self.filename, language, sortAsRules,
                    pageRangeRules):
                say("Imported “{}” from “{}”".format(
                    self.filename, inFilename), self.state.showMessageTime)
            else:
                say("Failed to import “{}” from “{}”".format(
                    self.filename, inFilename), self.state.showMessageTime)
        self.updateTitle()


    def _getLanguageAndRules(self):
        settings = QSettings()
        language = LanguageKind(settings.value(Gopt.Key.Language,
                                               Gopt.Default.Language))
        sortAsRules = settings.value(Gopt.Key.SortAsRules,
                                     Gopt.Default.SortAsRules)
        pageRangeRules = settings.value(Gopt.Key.PageRangeRules,
                                        Gopt.Default.PageRangeRules)
        return language, sortAsRules, pageRangeRules


    def updateTitle(self):
        if self.filename is None:
            self.setWindowTitle(QApplication.applicationName())
            say("Click File→New or File→Open to create or open an index")
        else:
            filename = os.path.basename(self.filename)
            dirname = os.path.abspath(os.path.dirname(self.filename))
            dirname = (" [{}]".format(os.path.normcase(dirname))
                       if dirname != os.getcwd() else "")
            self.setWindowTitle("{}{} — {}".format(
                filename, dirname, QApplication.applicationName()))


    def updateLanguageIndicator(self):
        language = self.state.model.config(Gconf.Key.Language).value
        self.languageLabel.setPixmap(
            QPixmap(":/{}.png".format(language.replace(" ", "_"))))


    def closeEvent(self, event=None):
        if self.state.saving:
            QTimer.singleShot(100, self.close)
            return
        if self.state.helpForm is not None:
            self.state.helpForm.close()
            self.state.helpForm.deleteLater()
            del self.state.helpForm
            self.state.helpForm = None
        self.indexActions.keepCheckFormsAlive = set()
        self.state.replacePanel.stop()
        self.state.replacePanel.saveSettings()
        self.state.closeModel()
        self.saveSettings()
        event.accept()


    def closeXix(self):
        if self.state.model.filename not in self.recent_files:
            self.recent_files.append(self.state.model.filename)
            self.recent_files = self.recent_files[-9:]
        self.updateRecentFilesMenu()
        self.state.closeModel()


    def saveSettings(self):
        settings = QSettings()
        settings.setValue(Gopt.Key.MainForm_Geometry, self.saveGeometry())
        settings.setValue(Gopt.Key.MainForm_State, self.saveState())
        settings.setValue(Gopt.Key.MainForm_Splitter,
                          self.splitter.saveState())
        settings.setValue(Gopt.Key.MainForm_PanelSplitter,
                          self.panelSplitter.saveState())
        settings.setValue(Gopt.Key.MainForm_EntrySuggestionsSplitter,
                          self.entrySuggestionSplitter.saveState())
        settings.setValue(Gopt.Key.MainForm_SpellAndGroupsSplitter,
                          self.spellAndGroupsSplitter.saveState())
        settings.setValue(Gopt.Key.MainForm_ViewSplitter,
                          self.viewSplitter.saveState())
        settings.setValue(Gopt.Key.MainForm_Filename, self.filename)
        settings.setValue(Gopt.Key.MainForm_RecentFiles, self.recent_files)


    def updateRecentFilesMenu(self):
        recentAction = self.fileActions.openRecentAction
        if self.recent_files:
            self.recent_files = [filename for filename in self.recent_files
                                 if filename and os.path.exists(filename)]
        if not self.recent_files:
            recentAction.setEnabled(False)
        else:
            recentAction.setEnabled(True)
            menu = QMenu(self)
            for i, filename in enumerate(self.recent_files, 1):
                action = QAction(
                    QIcon(":/document-open.svg"), "&{} {}".format(
                        i, QDir.toNativeSeparators(filename)), menu)
                action.triggered.connect(
                    lambda filename=filename: self.openXix(filename))
                menu.addAction(action)
            recentAction.setMenu(menu)


    def resizeEvent(self, event):
        if not self.resizing:
            self.state.viewAllPanel.view.busy = True
            self.state.viewFilteredPanel.view.busy = True
            self.resizeTimer.start(400)
        super().resizeEvent(event)


    def onResize(self):
        self.resizeTimer.stop()
        self.state.viewAllPanel.view.busy = False
        self.state.viewFilteredPanel.view.busy = False
        self.state.viewAllPanel.view.refresh()
        self.state.viewFilteredPanel.view.refresh()
        self.updateUi()
        if self.debug:
            print("{:,}x{:,}".format(self.frameGeometry().width(),
                                     self.frameGeometry().height()))


    @property
    def resizing(self):
        return self.resizeTimer.isActive()
