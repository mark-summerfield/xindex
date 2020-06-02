#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Qt
from PySide.QtGui import QAction, QApplication, QIcon, QKeySequence

import Forms
import Lib
import Sql


class Actions:

    def __init__(self, window):
        self.window = window
        self.state = self.window.state

        self.rememberWordAction = Lib.createAction(
            window, ":/spelling-add.svg", "&Remember Word",
            self.state.entryPanel.rememberWord,
            QKeySequence(Qt.CTRL + Qt.Key_R), """
<p><b>Spelling→Remember Word</b> ({})</p>
<p>Remember the unknown word in the current entry's term that's nearest
to the cursor's left, in the index's dictionary.</p>""".format(
                QKeySequence(Qt.CTRL + Qt.Key_R).toString()))
        self.ignoreWordAction = Lib.createAction(
            window, ":/spelling-ignore.svg", "&Ignore Word",
            self.state.entryPanel.ignoreWord,
            tooltip="""
<p><b>Spelling→Ignore Word</b></p>
<p>Ignore the unknown word in the current entry's term that's nearest
to the cursor's left, for this session.</p>""")
        self.forgetWordsAction = Lib.createAction(
            window, ":/spelling-remove.svg", "&Forget Words...",
            self.forgetWords, tooltip="""
<p><b>Spelling→Forget Words</b></p>
<p>Forget one or more words from this session's ignore list or from the
index's dictionary.</p>""")
        self.autoReplaceAction = Lib.createAction(
            window, ":/autoreplace.svg", "&Auto Replace...",
            self.autoReplace, tooltip="""
<p><b>Spelling→Auto Replace</b></p>
<p>Add, edit, and delete the index's auto. replacements' texts and
replacements.</p>""")
        self.completeWithSuggestedAction = Lib.createAction(
            window, ":/complete.svg", "Replace with &Suggested",
            self.state.entryPanel.completeWithSuggested,
            QKeySequence(Qt.CTRL + Qt.Key_M),
            tooltip="""
<p><b>Spelling→Replace with Suggested</b> ({})</p>
<p>Replace the current term's current word with the current
suggestion.</p>""".format(QKeySequence(Qt.CTRL + Qt.Key_M).toString()))
        self.completionActions = []
        for i in range(9):
            action = QAction(
                QIcon(":/complete.svg"),
                "&{} Replace with “”".format(i + 1), self.window)
            action.setShortcut(QKeySequence("Ctrl+{}".format(i + 1)))
            action.triggered.connect(
                lambda i=i: self.state.entryPanel.complete(i))
            action.setVisible(False)
            self.completionActions.append(action)


    def forMenu(self):
        return (self.rememberWordAction, self.ignoreWordAction,
                self.forgetWordsAction, None, self.autoReplaceAction,
                None, self.completeWithSuggestedAction,) + tuple(
                    self.completionActions)


    def forToolbar(self):
        return (self.rememberWordAction, self.ignoreWordAction, None,
                self.completeWithSuggestedAction)


    def updateUi(self):
        enable = bool(self.state.spellPanel.count())
        if enable:
            for action in (self.rememberWordAction, self.ignoreWordAction,
                           self.completeWithSuggestedAction):
                action.setEnabled(enable)
        else:
            enable = bool(self.state.entryPanel.unknownWords)
            for action in (self.rememberWordAction, self.ignoreWordAction):
                action.setEnabled(enable)


    def forgetWords(self):
        widget = QApplication.focusWidget()
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.ForgetWords.Form(self.state, self.window)
            form.exec_()
        Lib.restoreFocus(widget)


    def autoReplace(self):
        info = Forms.PairList.Info(
            "Auto Replace", "Manage Auto Replace",
            "xix_ref_dlg_autorep.html", "Text", "Replacement",
            self.state.model._xix.db, Sql.SORTED_AUTO_REPLACE,
            Sql.EDIT_AUTO_REPLACE, Sql.DELETE_AUTO_REPLACE,
            Sql.AUTO_REPLACE_COUNT)
        widget = QApplication.focusWidget()
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.PairList.Form(self.state, info, self.window)
            form.exec_()
        Lib.restoreFocus(widget)
