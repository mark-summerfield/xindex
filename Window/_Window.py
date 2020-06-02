#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import QSettings, Qt
from PySide.QtGui import (
    QApplication, QCursor, QIcon, QKeySequence, QLabel, QMenu,
    QShortcut, QToolButton, QToolTip)

import Actions
import Lib
import Pages
import SortAs
import Widgets
from Config import Gopt
from . import EntryPanel
from . import GroupsPanel
from . import ReplacePanel
from . import SpellPanel
from . import ViewAllPanel
from . import ViewFilteredPanel
from Const import COUNT_LABEL_TEMPLATE, LABEL_TEMPLATE, say


class Mixin:

    def createWidgets(self):
        rules = SortAs.RulesForName[Gopt.Default.SortAsRules]
        self.sortAsRuleLabel = QLabel(LABEL_TEMPLATE.format(rules.abbrev))
        self.tooltips.append((self.sortAsRuleLabel,
                              Lib.rulesTip(rules.tip)))
        self.modeLabel = QLabel()
        self.statusbar.addPermanentWidget(self.modeLabel)
        self.tooltips.append((self.modeLabel, """<p><b>Mode</b></p>
<p>{}'s current mode.</p>""".format(QApplication.applicationName())))
        self.statusbar.addPermanentWidget(self.sortAsRuleLabel)
        rules = Pages.RulesForName[Gopt.Default.PageRangeRules]
        self.pageRangeRulesLabel = QLabel(LABEL_TEMPLATE.format(
                                          rules.abbrev))
        self.tooltips.append((self.pageRangeRulesLabel,
                             Lib.rulesTip(rules.tip, False)))
        self.statusbar.addPermanentWidget(self.pageRangeRulesLabel)
        self.countLabel = QLabel(COUNT_LABEL_TEMPLATE.format(0, 0, 0, 0))
        self.tooltips.append((self.countLabel, """<p><b>Counts</b></p>
<p>Counts of entries in the current index.</p>"""))
        self.statusbar.addPermanentWidget(self.countLabel)
        self.worktimeLabel = QLabel()
        self.tooltips.append((self.worktimeLabel, """<p><b>Work Time</b></p>
<p>How many hours and minutes have been spent on this index.</p>"""))
        self.statusbar.addPermanentWidget(self.worktimeLabel)
        self.languageLabel = QLabel()
        self.tooltips.append((self.languageLabel, """<p><b>Language</b></p>
<p>The language used for spelling and suggestions for this index.</p>"""))
        self.statusbar.addPermanentWidget(self.languageLabel)
        self.state.viewAllPanel = ViewAllPanel.Panel(self.state)
        self.state.replacePanel = ReplacePanel.Panel(self.state)
        self.state.replacePanel.closeButton.clicked.connect(
            self.closeReplace)
        self.state.viewFilteredPanel = ViewFilteredPanel.Panel(self.state)
        # Above must precede EntryPanel
        self.state.entryPanel = EntryPanel.Panel(self.state, self)
        # SpellPanel depends on EntryPanel and entryActions
        self.entryActions = Actions.Entry.Actions(self)
        self.state.spellPanel = SpellPanel.Panel(self.state, self)
        self.state.groupsPanel = GroupsPanel.Panel(self.state, self)
        self.state.entryPanel.populateEditors(self.state.editors)


    def widgets(self):
        return (self.state.viewAllPanel, self.state.replacePanel,
                self.state.viewFilteredPanel, self.state.entryPanel,
                self.state.spellPanel, self.state.groupsPanel,
                self.menuBar(), self.fileToolBar, self.editToolBar,
                self.spellingToolBar, self.formatToolBar,
                self.indexToolBar, self.entryToolBar1, self.entryToolBar2,
                self.modifyToolBar, self.gotoToolBar1, self.gotoToolBar2,
                self.gotoToolBar4, self.gotoToolBar3)


    def closeReplace(self):
        self.state.replacePanel.stop()
        sizes = self.viewSplitter.sizes()
        self.viewSplitter.setSizes([sum(sizes), 0])


    def closeSuggestions(self):
        sizes = self.spellAndGroupsSplitter.sizes()
        if 0 in sizes:
            sizes = self.entrySuggestionSplitter.sizes()
            self.entrySuggestionSplitter.setSizes([sum(sizes), 0])
        else:
            self.spellAndGroupsSplitter.setSizes([0, sum(sizes)])


    def closeGroups(self):
        sizes = self.spellAndGroupsSplitter.sizes()
        if 0 in sizes:
            sizes = self.entrySuggestionSplitter.sizes()
            self.entrySuggestionSplitter.setSizes([sum(sizes), 0])
        else:
            self.spellAndGroupsSplitter.setSizes([sum(sizes), 0])


    def showSuggestions(self):
        sizes = self.entrySuggestionSplitter.sizes()
        quarter = sum(sizes) // 4
        self.entrySuggestionSplitter.setSizes([quarter * 3, quarter])
        half = sum(self.spellAndGroupsSplitter.sizes()) // 2
        self.spellAndGroupsSplitter.setSizes([half, half])


    def layoutWidgets(self):
        self.panelSplitter = Widgets.Splitter.Splitter(Qt.Vertical)
        self.entrySuggestionSplitter = Widgets.Splitter.Splitter(
            Qt.Horizontal)
        self.entrySuggestionSplitter.addWidget(self.state.entryPanel)
        self.spellAndGroupsSplitter = Widgets.Splitter.Splitter(Qt.Vertical)
        self.spellAndGroupsSplitter.addWidget(self.state.spellPanel)
        self.spellAndGroupsSplitter.addWidget(self.state.groupsPanel)
        self.entrySuggestionSplitter.addWidget(self.spellAndGroupsSplitter)
        self.entrySuggestionSplitter.setCollapsible(0, False)
        self.entrySuggestionSplitter.setCollapsible(1, True)
        self.entrySuggestionSplitter.setStretchFactor(0, 3)
        self.entrySuggestionSplitter.setStretchFactor(1, 1)
        self.panelSplitter.addWidget(self.entrySuggestionSplitter)
        self.panelSplitter.addWidget(self.state.viewFilteredPanel)
        self.panelSplitter.setCollapsible(0, False)
        self.panelSplitter.setCollapsible(0, False)

        self.viewSplitter = Widgets.Splitter.Splitter(Qt.Vertical)
        self.viewSplitter.addWidget(self.state.viewAllPanel)
        self.viewSplitter.setCollapsible(0, False)
        self.viewSplitter.addWidget(self.state.replacePanel)

        self.splitter = Widgets.Splitter.Splitter(Qt.Horizontal)
        self.splitter.addWidget(self.panelSplitter)
        self.splitter.addWidget(self.viewSplitter)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.setCentralWidget(self.splitter)


    def createActions(self):
        self.fileActions = Actions.File.Actions(self)
        self.fileMenu = self.menuBar().addMenu("&File")
        Lib.addActions(self.fileMenu, self.fileActions.forMenu())
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.setObjectName("File")
        Lib.addActions(self.fileToolBar, self.fileActions.forToolbar())

        self.editActions = Actions.Edit.Actions(self)
        self.editMenu = self.menuBar().addMenu("&Edit")
        Lib.addActions(self.editMenu, self.editActions.forMenu())
        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.setObjectName("Edit")
        Lib.addActions(self.editToolBar, self.editActions.forToolbar())

        self.insertActions = Actions.Insert.Actions(self)
        self.insertMenu = self.menuBar().addMenu("Inse&rt")
        Lib.addActions(self.insertMenu, self.insertActions.forMenu())

        self.spellingActions = Actions.Spelling.Actions(self)
        self.spellingMenu = self.menuBar().addMenu("Spe&lling")
        Lib.addActions(self.spellingMenu, self.spellingActions.forMenu())
        self.spellingToolBar = self.addToolBar("Spelling")
        self.spellingToolBar.setObjectName("Spelling")
        Lib.addActions(self.spellingToolBar,
                       self.spellingActions.forToolbar())

        self.formatActions = Actions.Format.Actions(self)
        self.formatMenu = self.menuBar().addMenu("F&ormat")
        Lib.addActions(self.formatMenu, self.formatActions.forMenu())
        self.formatToolBar = self.addToolBar("Format")
        self.formatToolBar.setObjectName("Format")
        Lib.addActions(self.formatToolBar, self.formatActions.forToolbar())

        self.addToolBarBreak()

        # Actions created earlier
        self.indexActions = Actions.Index.Actions(self) # Menu added later
        self.indexToolBar = self.addToolBar("Index")
        self.indexToolBar.setObjectName("Index")
        Lib.addActions(self.indexToolBar, self.indexActions.forToolbar())

        self.gotoActions = Actions.Goto.Actions(self)
        self.gotoMenu = self.menuBar().addMenu("&Goto")
        Lib.addActions(self.gotoMenu, self.gotoActions.forMenu())
        # Goto toolbar is last

        # These actions are created in createWidgets() because two are
        # needed by the groups panel
        self.entryMenu = self.menuBar().addMenu("Entr&y")
        Lib.addActions(self.entryMenu, self.entryActions.forMenu())
        self.entryToolBar1 = self.addToolBar("Entry Add and Copy")
        self.entryToolBar1.setObjectName("Entry1")
        Lib.addActions(self.entryToolBar1, self.entryActions.forToolbar1())
        self.entryToolBar2 = self.addToolBar("Entry Cross-references")
        self.entryToolBar2.setObjectName("Entry2")
        Lib.addActions(self.entryToolBar2, self.entryActions.forToolbar2())
        self.entryToolBar3 = self.addToolBar("Entry Groups")
        self.entryToolBar3.setObjectName("Entry3")
        Lib.addActions(self.entryToolBar3, self.entryActions.forToolbar3())

        self.modifyActions = Actions.Modify.Actions(self)
        self.modifyMenu = self.menuBar().addMenu("&Modify")
        Lib.addActions(self.modifyMenu, self.modifyActions.forMenu())
        self.modifyToolBar = self.addToolBar("Modify")
        self.modifyToolBar.setObjectName("Modify")
        Lib.addActions(self.modifyToolBar, self.modifyActions.forToolbar())

        self.indexMenu = self.menuBar().addMenu("Inde&x")
        Lib.addActions(self.indexMenu, self.indexActions.forMenu())

        self.helpActions = Actions.Help.Actions(self)
        self.helpMenu = self.menuBar().addMenu("&Help")
        Lib.addActions(self.helpMenu, self.helpActions.forMenu())

        self.addToolBarBreak()

        self.gotoToolBar1 = self.addToolBar("Goto Filtered etc.")
        self.gotoToolBar1.setObjectName("Goto1")
        Lib.addActions(self.gotoToolBar1, self.gotoActions.forToolbar1())

        self.gotoToolBar2 = self.addToolBar("Goto First, Next, etc.")
        self.gotoToolBar2.setObjectName("Goto2")
        Lib.addActions(self.gotoToolBar2, self.gotoActions.forToolbar2())

        self.gotoToolBar4 = Widgets.AlphaBar.Bar()
        self.gotoToolBar4.setWindowTitle("Goto Letter")
        self.gotoToolBar4.setObjectName("Goto4")
        self.addToolBar(self.gotoToolBar4)

        self.gotoToolBar3 = self.addToolBar("Goto Bookmarks")
        self.gotoToolBar3.setObjectName("Goto3")
        Lib.addActions(self.gotoToolBar3, self.gotoActions.forToolbar3())
        self.bookmarksToolButton = QToolButton()
        self.bookmarksToolButton.setIcon(QIcon(":/bookmark.svg"))
        self.bookmarksToolButton.setPopupMode(QToolButton.InstantPopup)
        self.bookmarksToolButton.setToolTip("""\
<p><b>Goto→Bookmarks</b></p><p>Goto the bookmarked entry.""")
        self.gotoToolBar3.addWidget(self.bookmarksToolButton)

        for toolbar in (self.fileToolBar, self.editToolBar,
                        self.spellingToolBar, self.formatToolBar,
                        self.indexToolBar, self.entryToolBar1,
                        self.entryToolBar2, self.modifyToolBar,
                        self.gotoToolBar1, self.gotoToolBar2,
                        self.gotoToolBar4, self.gotoToolBar3):
            toolbar.setFloatable(False)


    def createConnections(self):
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_T), self,
                  self.state.viewAllPanel.gotoLineEdit.setFocus)
        self.state.viewAllPanel.view.selectedEidChanged.connect(
            self.state.updateUi)
        self.state.viewAllPanel.view.circledEidChanged.connect(
            self.state.updateUi)
        self.state.viewAllPanel.view.refreshed.connect(
            self.modifyActions.updateUi)
        self.state.viewFilteredPanel.view.refreshed.connect(
            self.entryActions.updateUi)
        self.state.viewFilteredPanel.view.refreshed.connect(
            self.modifyActions.updateUi)
        self.state.viewFilteredPanel.view.refreshed.connect(
            self.updateFilteredGotoActions)
        self.state.viewFilteredPanel.view.refreshed.connect(
            self.state.replacePanel.updateUi)
        self.state.model.changed.connect(self.state.updateUi)
        self.state.model.edited.connect(self.state.refreshEntry)
        self.state.model.can_undo.connect(self.indexActions.updateUndo)
        self.state.model.can_redo.connect(self.indexActions.updateRedo)
        self.state.model.group_changed.connect(
            self.state.groupsPanel.updateGroups)
        self.workTimer.timeout.connect(self.updateWorkTime)
        self.editActions.connectEditors()
        self.state.entryPanel.xrefList.itemDoubleClicked.connect(
            self.gotoActions.gotoXRef)
        self.state.entryPanel.xrefList.currentRowChanged.connect(
            self.updateXRefGotoActions)
        self.gotoToolBar4.orientationChanged.connect(
            self.gotoToolBar4.setOrientation)
        self.gotoToolBar4.clicked.connect(self.gotoActions.gotoPrefix)
        for menu in self.menuBar().findChildren(QMenu):
            for action in menu.actions():
                if bool(action.toolTip()):
                    action.hovered.connect(
                        lambda action=action: self.menuHovered(action))


    def menuHovered(self, action):
        settings = QSettings()
        if bool(int(settings.value(Gopt.Key.ShowMenuToolTips,
                                   Gopt.Default.ShowMenuToolTips))):
            tip = action.toolTip()
            if tip:
                QToolTip.showText(QCursor.pos(), tip, self)


    def reportProgress(self, message):
        say(message)
        QApplication.processEvents()


    def updateToolTips(self):
        settings = QSettings()
        showToolTips = bool(int(settings.value(
            Gopt.Key.ShowMainWindowToolTips,
            Gopt.Default.ShowMainWindowToolTips)))
        for widget, tip in self.tooltips:
            widget.setToolTip(tip if showToolTips else "")
        for panel in (self.state.viewAllPanel, self.state.replacePanel,
                      self.state.viewFilteredPanel, self.state.entryPanel,
                      self.state.spellPanel, self.state.groupsPanel):
            panel.updateToolTips(showToolTips)


    def createContextMenus(self):
        for action in (self.indexActions.undoAction,
                       self.indexActions.redoAction,
                       self.gotoActions.gotoFirstAction,
                       self.gotoActions.gotoLastAction,
                       self.entryActions.addSiblingAction,
                       self.entryActions.addChildAction,
                       self.entryActions.addTopAction,
                       self.entryActions.copyAction,
                       self.entryActions.moveAction,
                       self.entryActions.deleteAction,
                       self.entryActions.addXRefAction,
                       self.entryActions.circleAction,
                       self.entryActions.addToNormalGroupAction,
                       self.entryActions.addToLinkedGroupAction):
            self.state.viewAllPanel.view.addAction(action)
        for action in (self.gotoActions.gotoFilteredAction,):
            self.state.viewFilteredPanel.view.addAction(action)
        for action in (self.entryActions.addXRefAction,
                       self.entryActions.changeXRefAction,
                       self.entryActions.deleteXRefAction):
            self.state.entryPanel.xrefList.addAction(action)
        self.state.entryPanel.xrefList.setContextMenuPolicy(
            Qt.ActionsContextMenu)
        for action in (self.entryActions.addToNormalGroupAction,
                       self.entryActions.addToLinkedGroupAction,
                       self.entryActions.removeFromGroupAction,
                       self.entryActions.setGroupAction,
                       self.entryActions.editGroupsAction):
            self.state.groupsPanel.groupsList.addAction(action)
        self.state.groupsPanel.groupsList.setContextMenuPolicy(
            Qt.ActionsContextMenu)
