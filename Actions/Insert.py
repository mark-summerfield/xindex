#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtGui import QApplication, QPlainTextEdit, QTextEdit

import Lib
import Forms


class Actions:

    def __init__(self, window):
        self.window = window
        self.state = self.window.state

        self.insertQuoteAction = Lib.createAction(
            window, ":/quote.svg", "&Single Quote",
            lambda: self.insertChar("'"), tooltip="""
<p><b>Insert→Single Quote</b></p>
<p>Insert a single quote ‘'’.</p>""")
        self.insertDoubleQuoteAction = Lib.createAction(
            window, ":/doublequote.svg", "&Double Quote",
            lambda: self.insertChar('"'), tooltip="""
<p><b>Insert→Double Quote</b></p>
<p>Insert a double quote ‘"’.</p>""")
        self.insertEllipsisAction = Lib.createAction(
            window, ":/ellipsis.svg", "&Ellipsis",
            lambda: self.insertChar("…"), tooltip="""
<p><b>Insert→Ellipsis</b></p>
<p>Insert an ellipsis ‘…’.</p>""")
        self.insertEndashAction = Lib.createAction(
            window, ":/endash.svg", "E&n-dash",
            lambda: self.insertChar("–"), tooltip="""
<p><b>Insert→En-dash</b></p>
<p>Insert an en-dash ‘–’.</p>
<p>Using a plain hyphen ‘-’ is fine for page ranges since {}
automatically converts hyphens to en-dashes.""".format(
                QApplication.applicationName()))
        self.insertEmdashAction = Lib.createAction(
            window, ":/emdash.svg", "E&m-dash",
            lambda: self.insertChar("—"), tooltip="""
<p><b>Insert→Em-dash</b></p>
<p>Insert an em-dash ‘—’.</p>""")
        self.insertCharAction = Lib.createAction(
            window, ":/accessories-character-map.svg", "&Copy Character...",
            self.insertCharacter, tooltip="""
<p><b>Insert→Copy Character</b></p>
<p>Pop up the Copy Character dialog from which any available characters
can be chosen and copied to the clipboard.</p>""")


    def forMenu(self):
        return (self.insertQuoteAction, self.insertDoubleQuoteAction,
                self.insertEllipsisAction, self.insertEndashAction,
                self.insertEmdashAction, None, self.insertCharAction)


    def insertChar(self, char):
        for editor in self.state.editors:
            if editor.hasFocus():
                if isinstance(editor, (QTextEdit, QPlainTextEdit)):
                    editor.insertPlainText(char)
                else:
                    editor.insert(char)
                break


    def insertCharacter(self):
        widget = QApplication.focusWidget()
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.CopyCharacter.Form(self.state, self.window)
            form.exec_()
        Lib.restoreFocus(widget)
