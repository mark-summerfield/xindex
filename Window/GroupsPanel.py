#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Qt
from PySide.QtGui import (
    QHBoxLayout, QIcon, QLabel, QListWidget, QListWidgetItem,
    QToolButton, QVBoxLayout, QWidget)

import Lib
from Const import ModeKind


@Lib.updatable_tooltips
class Panel(QWidget):

    def __init__(self, state, parent=None):
        super().__init__(parent=parent)
        self.state = state
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.tooltips.append((self, """<p><b>Groups panel</b></p>
<p>This panel shows the groups the current entry belongs to.</p>"""))


    def createWidgets(self):
        self.label = QLabel("Gro&ups")
        self.groupsList = QListWidget()
        self.tooltips.append((self.groupsList, """
<p><b>Groups</b> (Alt+U)</p>
<p>A (possibly empty) list of the current entry's groups.</p>"""))
        self.label.setBuddy(self.groupsList)
        self.closeButton = QToolButton()
        self.closeButton.setIcon(QIcon(":/hide.svg"))
        self.closeButton.setFocusPolicy(Qt.NoFocus)
        self.tooltips.append((self.closeButton, """<p><b>Hide</b></p>
<p>Hide the Groups panel.</p>
<p>Use <b>Spelling→Show Suggestions and Groups</b> to show it
again.</p>"""))
        self.helpButton = QToolButton()
        self.helpButton.setIcon(QIcon(":/help.svg"))
        self.helpButton.setFocusPolicy(Qt.NoFocus)
        self.tooltips.append((self.helpButton,
                              "Help on the Groups panel."))

    def layoutWidgets(self):
        layout = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addStretch()
        hbox.addWidget(self.closeButton)
        hbox.addWidget(self.helpButton)
        layout.addLayout(hbox)
        layout.addWidget(self.groupsList)
        self.setLayout(layout)


    def createConnections(self):
        self.closeButton.clicked.connect(self.state.window.closeGroups)
        self.helpButton.clicked.connect(self.help)
        self.groupsList.itemDoubleClicked.connect(
            self.state.viewFilteredPanel.setGroup)


    def updateUi(self):
        enable = bool(self.state.model) and self.state.mode not in {
            ModeKind.NO_INDEX, ModeKind.CHANGE}
        self.setEnabled(enable)
        if enable:
            (self.state.window.entryActions.addToNormalGroupAction
                .setEnabled(self.state.model.normalGroupCount()))
            (self.state.window.entryActions.addToLinkedGroupAction
                .setEnabled(self.state.model.linkedGroupCount()))
            self.state.window.entryActions.removeFromGroupAction.setEnabled(
                self.groupsList.currentItem() is not None)


    def updateGroups(self):
        self.groupsList.clear()
        eid = self.state.viewAllPanel.view.selectedEid
        if eid is not None:
            for gid, name, linked in self.state.model.groupsForEid(
                    eid, withLinks=True):
                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, gid)
                item.setIcon(QIcon(":/grouplink.svg" if linked else
                                   ":/groups.svg"))
                self.groupsList.addItem(item)
        if self.groupsList.count():
            self.groupsList.setCurrentRow(0)
        self.updateUi()
        self.state.viewFilteredPanel.groupChanged()


    def clear(self):
        self.groupsList.clear()
        self.updateUi()


    def help(self):
        self.state.help("xix_ref_panel_grp.html")


    def __getattr__(self, name):
        return getattr(self.groupsList, name)
