#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

import collections
import itertools

from PySide.QtCore import Qt
from PySide.QtGui import QAction, QIcon, QMenu

import Lib
import Xix
from Const import (
    MAIN_INDICATOR, MAX_DYNAMIC_ACTIONS, ModeKind, SUB_INDICATOR)


class Mixin:

    def updateGotoActions(self, total, filtered):
        self.updateXRefGotoActions()
        self.updateFilteredGotoActions()
        enable = bool(total) and self.state.mode not in {ModeKind.NO_INDEX,
                                                         ModeKind.CHANGE}
        for action in itertools.chain((
                self.gotoActions.gotoFirstAction,
                self.gotoActions.gotoPrevAction,
                self.gotoActions.gotoNextAction,
                self.gotoActions.gotoLastAction,
                self.gotoActions.gotoLetterAction,
                self.gotoActions.addBookmarkAction,
                self.gotoActions.removeBookmarkAction),
                self.gotoActions.gotoLetterActions):
            action.setEnabled(enable)
        self.updateGotoMenu()


    def updateGotoMenu(self):
        self.gotoActions.goBackAction.setEnabled(False)
        menu = self.gotoMenu
        menu.clear()
        Lib.addActions(self.gotoMenu, self.gotoActions.forMenu())
        if self.state.gotoEids and bool(self.state.model):
            eids = collections.deque(maxlen=MAX_DYNAMIC_ACTIONS)
            for eid in self.state.gotoEids:
                if self.state.model.hasEntry(eid):
                    eids.append(eid)
                    if len(eids) == MAX_DYNAMIC_ACTIONS:
                        break
            accels = collections.deque("123456789DEGHJKKMQTUVWXZY")
            self.state.gotoEids = eids
            currentEid = self.state.viewAllPanel.view.selectedEid
            eids = [eid for eid in eids if eid != currentEid]
            for index, eid in enumerate(eids, 1):
                entry = self.state.model.entry(eid)
                term = Lib.elide(entry.term)
                if accels:
                    term = "&{} {}".format(accels.popleft(), term)
                if index == 1:
                    action = self.gotoActions.goBackAction
                    action.setEnabled(True)
                    action.setText(term)
                    action.triggered.disconnect()
                else:
                    action = QAction(QIcon(":/go-back.svg"), term, menu)
                action.triggered.connect(
                    lambda eid=eid: self.gotoActions.gotoEid(eid))
                menu.addAction(action)


    def refreshBookmarks(self):
        enable = bool(self.state.model) and self.state.model.hasBookmarks()
        self.gotoActions.bookmarksAction.setEnabled(enable)
        self.bookmarksToolButton.setEnabled(enable)
        if enable:
            menu = QMenu(self)
            accels = collections.deque(
                "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            for eid, term, istop in self.state.model.bookmarks():
                term = "{} {}".format(MAIN_INDICATOR if istop else
                                      SUB_INDICATOR, Lib.elide(term))
                if accels:
                    term = "&{} {}".format(accels.popleft(), term)
                action = QAction(QIcon(":/bookmark.svg"), term, menu)
                action.triggered.connect(
                    lambda eid=eid: self.gotoActions.gotoEid(eid))
                menu.addAction(action)
            self.gotoActions.bookmarksAction.setMenu(menu)
            self.bookmarksToolButton.setMenu(menu)
        else:
            self.gotoActions.bookmarksAction.setMenu(None)
            self.bookmarksToolButton.setMenu(None)


    def updateFilteredGotoActions(self):
        filtered = (0 if not bool(self.state.model) else
                    self.state.viewFilteredPanel.view.count())
        enable = bool(filtered) and self.state.mode not in {
            ModeKind.NO_INDEX, ModeKind.CHANGE}
        self.gotoActions.gotoFilteredAction.setEnabled(enable)


    def updateXRefGotoActions(self):
        self.gotoActions.gotoXRefAction.setEnabled(False)
        item = self.state.entryPanel.xrefList.currentItem()
        if item is not None:
            xref = Xix.Util.xref_for_data(item.data(Qt.UserRole))
            self.gotoActions.gotoXRefAction.setEnabled(
                xref.to_eid is not None)
