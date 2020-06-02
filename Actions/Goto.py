#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

import string

from PySide.QtCore import Qt
from PySide.QtGui import QKeySequence, QMenu

import Lib
import Xix
from Const import say, SAY_TIMEOUT


class Actions:

    def __init__(self, window):
        self.window = window
        self.state = self.window.state

        self.gotoFilteredAction = Lib.createAction(
            window, ":/goto-found.svg", "&Filtered", self.gotoFiltered,
            QKeySequence(Qt.Key_F3), tooltip="""\
<p><b>Goto→Filtered</b> ({})</p>
<p>Go to the filtered entry.</p>""".format(QKeySequence(
                                           Qt.Key_F3).toString()))
        self.gotoCircledAction = Lib.createAction(
            window, ":/goto-circled.svg", "&Circled", self.gotoCircled,
            QKeySequence(Qt.SHIFT + Qt.Key_F3),
            tooltip="""\
<p><b>Goto→Circled</b> ({})</p>
<p>Go to the circled entry.</p>""".format(QKeySequence(Qt.SHIFT + Qt.Key_F3)
                                          .toString()))
        self.gotoXRefAction = Lib.createAction(
            window, ":/goto-xref.svg", "Cr&oss-reference", self.gotoXRef,
            QKeySequence(Qt.CTRL + Qt.Key_F3),
            tooltip="""\
<p><b>Goto→Cross-reference</b> ({})</p>
<p>Go to the current cross reference.</p>""".format(
                QKeySequence(Qt.CTRL + Qt.Key_F3).toString()))
        self.gotoFirstAction = Lib.createAction(
            window, ":/go-top.svg", "F&irst", self.gotoFirst,
            QKeySequence(Qt.CTRL + Qt.Key_Home),
            tooltip="""\
<p><b>Goto→First</b> ({})</p>
<p>Go to the first entry.</p>""".format(QKeySequence(Qt.CTRL + Qt.Key_Home)
                                        .toString()))
        self.gotoPrevAction = Lib.createAction(
            window, ":/go-previous.svg", "&Previous", self.gotoPrevious,
            QKeySequence(Qt.CTRL + Qt.Key_Up),
            tooltip="""\
<p><b>Goto→Previous</b> ({})</p>
<p>Go to the previous entry.</p>""".format(QKeySequence(Qt.CTRL + Qt.Key_Up)
                                           .toString()))
        self.gotoNextAction = Lib.createAction(
            window, ":/go-next.svg", "&Next", self.gotoNext,
            QKeySequence(Qt.CTRL + Qt.Key_Down),
            tooltip="""\
<p><b>Goto→Next</b> ({})</p>
<p>Go to the next entry.</p>""".format(QKeySequence(Qt.CTRL + Qt.Key_Down)
                                       .toString()))
        self.gotoLastAction = Lib.createAction(
            window, ":/go-bottom.svg", "La&st", self.gotoLast,
            QKeySequence(Qt.CTRL + Qt.Key_End),
            tooltip="""\
<p><b>Goto→Last</b> ({})</p>
<p>Go to the last entry.</p>""".format(QKeySequence(Qt.CTRL + Qt.Key_End)
                                       .toString()))
        menu = QMenu(window)
        self.gotoLetterActions = []
        for letter in string.ascii_uppercase:
            action = Lib.createAction(
                window, None, "&{}".format(letter),
                lambda letter=letter: self.gotoLetter(letter),
                tooltip="""\
<p><b>Goto→Letter→{0}</b></p>
<p>Go to the first Main entry whose Sort As begins with ‘{0}’""".format(
                    letter))
            action.setShortcut("Ctrl+G,{}".format(letter))
            action.hovered.connect(lambda action=action: window.menuHovered(
                                   action))
            menu.addAction(action)
            self.gotoLetterActions.append(action)
        self.gotoLetterAction = Lib.createAction(
            window, ":/goto-letter.svg", "&Letter",
            tooltip="""\
<p><b>Goto→Letter</b></p>
<p>Go to the first Main entry whose Sort As begins with the given
letter.""")
        self.gotoLetterAction.setMenu(menu)
        self.addBookmarkAction = Lib.createAction(
            window, ":/bookmark-new.svg", "&Add Bookmark",
            self.addBookmark, QKeySequence(Qt.Key_F4),
            tooltip="""\
<p><b>Goto→Add Bookmark</b> ({})</p>
<p>Add a bookmark for the current entry.""".format(
                QKeySequence(Qt.Key_F4).toString()))
        self.removeBookmarkAction = Lib.createAction(
            window, ":/bookmark-remove.svg", "&Remove Bookmark",
            self.removeBookmark, QKeySequence(Qt.SHIFT + Qt.Key_F4),
            tooltip="""\
<p><b>Goto→Remove Bookmark</b></p>
<p>Remove any bookmark for the current entry.""".format(
                QKeySequence(Qt.SHIFT + Qt.Key_F4).toString()))
        self.bookmarksAction = Lib.createAction(
            window, ":/bookmark.svg", "&Bookmarks", tooltip="""\
<p><b>Goto→Bookmarks</b></p>
<p>Goto the bookmarked entry.""")

        self.goBackAction = Lib.createAction(
            window, ":/go-back.svg", "Go Back",
            shortcut=QKeySequence(Qt.ALT + Qt.Key_Left), tooltip="""\
<p><b>Goto→Go Back</b> ({})</p>
<p>Go back to the most recently visited entry.</p>""".format(
                QKeySequence(Qt.ALT + Qt.Key_Left).toString()))
        self.goBackAction.setEnabled(False)


    def forMenu(self):
        return (self.gotoFilteredAction, self.gotoCircledAction,
                self.gotoXRefAction, None, self.gotoFirstAction,
                self.gotoPrevAction, self.gotoNextAction,
                self.gotoLastAction, self.gotoLetterAction, None,
                self.addBookmarkAction, self.removeBookmarkAction,
                self.bookmarksAction, None)


    def forToolbar1(self):
        return (self.goBackAction, self.gotoFilteredAction,
                self.gotoCircledAction, self.gotoXRefAction)


    def forToolbar2(self):
        return (self.gotoFirstAction, self.gotoPrevAction,
                self.gotoNextAction, self.gotoLastAction)


    def forToolbar3(self):
        return (self.addBookmarkAction, self.removeBookmarkAction)


    def gotoFirst(self):
        self.state.maybeSave()
        self.state.viewAllPanel.view.goHome()


    def gotoLast(self):
        self.state.maybeSave()
        self.state.viewAllPanel.view.goEnd()


    def gotoFiltered(self):
        self.gotoEid(self.state.viewFilteredPanel.view.selectedEid)


    def gotoCircled(self):
        self.gotoEid(self.state.viewAllPanel.view.circledEid)


    def gotoXRef(self):
        item = self.state.entryPanel.xrefList.currentItem()
        if item is not None:
            xref = Xix.Util.xref_for_data(item.data(Qt.UserRole))
            if xref.to_eid is not None:
                self.gotoEid(xref.to_eid)


    def gotoEid(self, eid):
        if eid is not None:
            self.state.maybeSave()
            self.state.viewAllPanel.view.gotoEid(eid)
            self.state.updateNavigationStatus()


    def gotoPrefix(self, text):
        while text:
            eid = self.state.model.firstForPrefix(text)
            if eid is not None:
                self.gotoEid(eid)
                return True
            text = text[:-1]
        return False


    def gotoLetter(self, letter):
        while letter <= "Z":
            eid = self.state.model.firstForLetter(letter)
            if eid is not None:
                self.gotoEid(eid)
                break
            letter = chr(ord(letter) + 1)


    def gotoPrevious(self):
        self.state.maybeSave()
        self.state.viewAllPanel.view.goUp()


    def gotoNext(self):
        self.state.maybeSave()
        self.state.viewAllPanel.view.goDown()


    def addBookmark(self):
        self.state.maybeSave()
        eid = self.state.viewAllPanel.view.selectedEid
        if eid is not None:
            self.state.model.addBookmark(eid)
            self.window.refreshBookmarks()
            say("Added bookmark", SAY_TIMEOUT)


    def removeBookmark(self):
        self.state.maybeSave()
        eid = self.state.viewAllPanel.view.selectedEid
        if eid is not None:
            self.state.model.removeBookmark(eid)
            self.window.refreshBookmarks()
            say("Removed bookmark", SAY_TIMEOUT)
