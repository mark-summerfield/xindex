#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Qt
from PySide.QtGui import QKeySequence, QPlainTextEdit, QTextEdit

import Lib
from Const import WIN

# May need to extend undo/redo/copy/cut/paste to other editors & others:
# simply add to State.editors


class Actions:

    def __init__(self, window):
        self.window = window
        self.state = self.window.state

        self.undoAction = Lib.createAction(
            window, ":/editor-undo.svg", "&Undo", self.undo,
            QKeySequence.Undo, """
<p><b>Edit→Undo</b> ({})</p>
<p>Undo the last text editing action if possible.</p>
<p>(Use <b>Index→Undo</b> to undo the last change to the index.)</p>"""
            .format(QKeySequence(QKeySequence.Undo).toString()))
        self.redoAction = Lib.createAction(
            window, ":/editor-redo.svg", "&Redo", self.redo,
            QKeySequence.Redo, """
<p><b>Edit→Redo</b> ({})</p>
<p>Redo the most recently undone text editing action if possible.</p>
<p>(Use <b>Index→Redo</b> to redo the most recently undone change to the
index.)</p>""".format(QKeySequence(QKeySequence.Redo).toString()))
        self.copyAction = Lib.createAction(
            window, ":/edit-copy.svg", "&Copy", self.copy,
            QKeySequence.Copy, """
<p><b>Edit→Copy</b> ({})</p>
<p>Copy the selected text to the clipboard.</p>""".format(
                QKeySequence(QKeySequence.Copy).toString()))
        self.cutAction = Lib.createAction(
            window, ":/edit-cut.svg", "Cu&t", self.cut, QKeySequence.Cut,
            """
<p><b>Edit→Cut</b> ({})</p>
<p>Cut the selected text to the clipboard.</p>""".format(
                QKeySequence(QKeySequence.Cut).toString()))
        self.pasteAction = Lib.createAction(
            window, ":/edit-paste.svg", "&Paste", self.paste,
            QKeySequence.Paste, """
<p><b>Edit→Paste</b> ({})</p>
<p>Paste in the text in the clipboard.</p>""".format(
                QKeySequence(QKeySequence.Paste).toString()))

        self.filterAction = Lib.createAction(
            window, ":/edit-find.svg", "&Filter", self.state.applyFilter,
            QKeySequence.Find, tooltip="""
<p><b>Edit→Filter</b> ({})</p>
<p>Show the Filtered panel and move the focus to it, and show the
matching entries for the current filter.</p>""".format(
                QKeySequence(QKeySequence.Find).toString()))
        self.searchAndReplaceAction = Lib.createAction(
            window, ":/edit-find-replace.svg", "&Search and Replace...",
            self.replace,
            QKeySequence.Replace if WIN else
            QKeySequence(Qt.CTRL + Qt.Key_H),
            tooltip="""
<p><b>Edit→Search and Replace</b> ({})</p>
<p>Show the Search and Replace panel and move the focus to it.</p>"""
            .format(QKeySequence(Qt.CTRL + Qt.Key_H).toString()))
        self.updateActions()


    def forMenu(self):
        return (self.undoAction, self.redoAction, None, self.copyAction,
                self.cutAction, self.pasteAction, None,
                self.filterAction, self.searchAndReplaceAction)


    def forToolbar(self):
        return (self.undoAction, self.redoAction, None, self.copyAction,
                self.cutAction, self.pasteAction, None,
                self.filterAction, self.searchAndReplaceAction)


    def connectEditors(self):
        for editor in self.state.editors:
            editor.textChanged.connect(self.updateActions)
            if hasattr(editor, "wordCompleted"):
                editor.wordCompleted.connect(self.updateActions)


    def updateActions(self):
        for action in (self.undoAction, self.redoAction):
            action.setEnabled(False)
        for editor in self.state.editors:
            if editor.hasFocus():
                if isinstance(editor, (QTextEdit, QPlainTextEdit)):
                    editor = editor.document()
                self.undoAction.setEnabled(editor.isUndoAvailable())
                self.redoAction.setEnabled(editor.isRedoAvailable())
                break


    def undo(self):
        for editor in self.state.editors:
            if editor.hasFocus():
                editor.undo()
                break


    def redo(self):
        for editor in self.state.editors:
            if editor.hasFocus():
                editor.redo()
                break


    def copy(self):
        for editor in self.state.editors:
            if editor.hasFocus():
                editor.copy()
                break


    def cut(self):
        for editor in self.state.editors:
            if editor.hasFocus():
                editor.cut()
                break


    def paste(self):
        for editor in self.state.editors:
            if editor.hasFocus():
                editor.paste()
                break


    def replace(self):
        sizes = self.window.viewSplitter.sizes()
        if sizes[1] < 20:
            top = sum(sizes) - 20
            self.window.viewSplitter.setSizes([top, 20])
        self.state.replacePanel.searchLineEdit.setFocus()
