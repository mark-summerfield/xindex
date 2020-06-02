#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

from PySide.QtGui import QActionGroup, QKeySequence

import Lib


class Actions:

    def __init__(self, window, fontSizeSpinBox=None):
        self.window = window
        self.state = window.state
        self.fontSizeSpinBox = fontSizeSpinBox
        if self.fontSizeSpinBox is not None:
            self.fontSizeSpinBox.valueChanged.connect(self.setFontSize)
        self.boldAction = Lib.createAction(
            window, ":/format-text-bold.svg", "&Bold", self.toggleBold,
            QKeySequence.Bold, """<p><b>Format→Bold</b> ({})</p>
<p>Toggle bold on or off.</p>""".format(QKeySequence(
                                        QKeySequence.Bold).toString()))
        self.italicAction = Lib.createAction(
            window, ":/format-text-italic.svg", "&Italic",
            self.toggleItalic, QKeySequence.Italic, """\
<p><b>Format→Italic</b> ({})</p>
<p>Toggle italic on or off.</p>""".format(QKeySequence(
                                          QKeySequence.Italic).toString()))
        self.underlineAction = Lib.createAction(
            window, ":/format-text-underline.svg", "&Underline",
            self.toggleUnderline, QKeySequence.Underline, """\
<p><b>Format→Underline</b> ({})</p>
<p>Toggle underline on or off.</p>""".format(
                QKeySequence(QKeySequence.Underline).toString()))
        self.noSuperSubscriptAction = Lib.createAction(
            window, ":/nosupersubscript.svg",
            "&No Superscript or Subscript", self.noSuperSubscript,
            tooltip="""\
<p><b>Format→No superscript or subscript</b></p>
<p>Clear superscript or subscript and return to normal.</p>""")
        self.superscriptAction = Lib.createAction(
            window, ":/superscript.svg", "Su&perscript",
            self.setSuperscript, tooltip="""<p><b>Format→Superscript</b></p>
<p>Set superscript on.</p>""")
        self.subscriptAction = Lib.createAction(
            window, ":/subscript.svg", "Subs&cript", self.setSubscript,
            tooltip="""<p><b>Format→Subscript</b></p>
<p>Set subscript on.</p>""")
        self.superSubGroup = QActionGroup(self.window)
        self.superSubGroup.setExclusive(True)
        for action in (self.superscriptAction, self.subscriptAction,
                       self.noSuperSubscriptAction):
            self.superSubGroup.addAction(action)
        self.stdFontAction = Lib.createAction(
            window, ":/font-std.svg", "&Standard Font", self.setStdFont,
            tooltip="""<p><b>Format→Standard Font</b></p>
<p>Set the standard font.</p>""")
        self.altFontAction = Lib.createAction(
            window, ":/font-alt.svg", "&Alternate Font", self.setAltFont,
            tooltip="""<p><b>Format→Alternate Font</b></p>
<p>Set the alternate font.</p>""")
        self.monoFontAction = Lib.createAction(
            window, ":/font-mono.svg", "&Monospace Font", self.setMonoFont,
            tooltip="""<p><b>Format→Monospace Font</b></p>
<p>Set the monospace font.</p>""")
        self.fontGroup = QActionGroup(self.window)
        self.fontGroup.setExclusive(True)
        for action in (self.stdFontAction, self.altFontAction,
                       self.monoFontAction):
            self.fontGroup.addAction(action)
        for action in (self.boldAction, self.italicAction,
                       self.underlineAction, self.superscriptAction,
                       self.subscriptAction, self.noSuperSubscriptAction,
                       self.stdFontAction, self.altFontAction,
                       self.monoFontAction):
            action.setCheckable(True)
        self.noSuperSubscriptAction.setChecked(True)
        self.stdFontAction.setChecked(True)


    def forMenu(self):
        return (self.boldAction, self.italicAction,
                self.underlineAction, None, self.noSuperSubscriptAction,
                self.superscriptAction, self.subscriptAction, None,
                self.stdFontAction, self.altFontAction,
                self.monoFontAction)


    def forToolbar(self):
        return (self.boldAction, self.italicAction,
                self.underlineAction, None, self.noSuperSubscriptAction,
                self.superscriptAction, self.subscriptAction, None,
                self.stdFontAction, self.altFontAction,
                self.monoFontAction)


    def updateEnabled(self):
        enable = False
        for editor in self.state.editors:
            if editor.hasFocus():
                enable = hasattr(editor, "toggleBold")
                break
        for action in (self.boldAction, self.italicAction,
                       self.underlineAction,
                       self.noSuperSubscriptAction,
                       self.superscriptAction, self.subscriptAction,
                       self.stdFontAction, self.altFontAction,
                       self.monoFontAction):
            action.setEnabled(enable)
        if self.fontSizeSpinBox is not None:
            self.fontSizeSpinBox.setEnabled(enable)
        return enable


    def update(self, bold, italic, underline, superscript, subscript,
               family, size=None):
        enable = self.updateEnabled()
        if enable:
            self.boldAction.setChecked(bold)
            self.italicAction.setChecked(italic)
            self.underlineAction.setChecked(underline)
            self.superscriptAction.setChecked(superscript)
            self.subscriptAction.setChecked(subscript)
            self.noSuperSubscriptAction.setChecked(
                not superscript and not subscript)
            family = family.casefold()
            if family == self.state.altFontFamily.casefold():
                self.altFontAction.setChecked(True)
            elif family == self.state.monoFontFamily.casefold():
                self.monoFontAction.setChecked(True)
            else:
                self.stdFontAction.setChecked(True)
            if size is not None and self.fontSizeSpinBox is not None:
                self.fontSizeSpinBox.setValue(size)


    def toggleBold(self):
        for editor in self.state.editors:
            if editor.hasFocus():
                if hasattr(editor, "toggleBold"):
                    editor.toggleBold()
                break


    def toggleItalic(self):
        for editor in self.state.editors:
            if editor.hasFocus():
                if hasattr(editor, "toggleItalic"):
                    editor.toggleItalic()
                break


    def toggleUnderline(self):
        for editor in self.state.editors:
            if editor.hasFocus():
                if hasattr(editor, "toggleUnderline"):
                    editor.toggleUnderline()
                break


    def setSuperscript(self):
        for editor in self.state.editors:
            if editor.hasFocus():
                if hasattr(editor, "setSuperscript"):
                    editor.setSuperscript()
                break


    def setSubscript(self):
        for editor in self.state.editors:
            if editor.hasFocus():
                if hasattr(editor, "setSubscript"):
                    editor.setSubscript()
                break


    def noSuperSubscript(self):
        for editor in self.state.editors:
            if editor.hasFocus():
                if hasattr(editor, "noSuperSubscript"):
                    editor.noSuperSubscript()
                break


    def setStdFont(self):
        for editor in self.state.editors:
            if editor.hasFocus():
                if hasattr(editor, "setStdFont"):
                    editor.setStdFont()
                break


    def setAltFont(self):
        for editor in self.state.editors:
            if editor.hasFocus():
                if hasattr(editor, "setAltFont"):
                    editor.setAltFont()
                break


    def setMonoFont(self):
        for editor in self.state.editors:
            if editor.hasFocus():
                if hasattr(editor, "setMonoFont"):
                    editor.setMonoFont()
                break


    def setFontSize(self, size):
        if self.fontSizeSpinBox is None:
            return
        for editor in self.state.editors:
            if editor.hasFocus():
                if hasattr(editor, "setFontSize"):
                    editor.setFontSize(size)
                break
