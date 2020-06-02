#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import time

from PySide.QtCore import Qt
from PySide.QtGui import (
    QAction, QApplication, QFont, QFontComboBox, QIcon, QKeySequence,
    QShortcut, QSpinBox)

from .Lib import elideHtml, patchFont, PATCH_FONT_RX, sanePointSize


DEBUGGING = False


class Timer:

    def __init__(self, message, ignoreIfLessThanSecs=None):
        if DEBUGGING:
            self.message = message
            self.ignoreIfLessThan = ignoreIfLessThanSecs
            self.monotime = 0


    def __enter__(self):
        if DEBUGGING:
            self.monotime = time.monotonic()


    def __exit__(self, exc_type, exc_val, exc_tb):
        if DEBUGGING:
            elapsed = time.monotonic() - self.monotime
            if (self.ignoreIfLessThan is None or
                    elapsed > self.ignoreIfLessThan):
                print("{} {:.3f} sec".format(self.message, elapsed))


class BlockSignals:

    def __init__(self, widget):
        self.widget = widget


    def __enter__(self):
        self.widget.blockSignals(True)


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.widget.blockSignals(False)


class DisableUI:

    def __init__(self, *widgets, forModalDialog=False):
        self.widgets = widgets
        self.forModalDialog = forModalDialog


    def __enter__(self):
        for widget in self.widgets:
            widget.setEnabled(False)
        if not self.forModalDialog:
            QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.sendPostedEvents(None, 0)
        QApplication.processEvents()


    def __exit__(self, exc_type, exc_val, exc_tb):
        for widget in self.widgets:
            widget.setEnabled(True)
        if not self.forModalDialog:
            QApplication.restoreOverrideCursor()


def restoreFocus(widget):
    if widget is not None and widget.isVisible() and widget.isEnabled():
        widget.setFocus()


def addActions(menuOrToolbar, actions):
    for action in actions:
        if action is None:
            menuOrToolbar.addSeparator()
        else:
            menuOrToolbar.addAction(action)


def createAction(widget, icon, text, slot=None, shortcut=None,
                 tooltip=None):
    action = QAction(QIcon(icon), text, widget)
    if slot is not None:
        action.triggered.connect(slot)
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tooltip is not None:
        action.setToolTip(tooltip)
    return action


def createFontBoxesFor(parent, name, family, size, *, mono=False,
                       tooltips=None, which="Font"):
    font = QFont(family, size)
    fontComboBox = QFontComboBox(parent)
    if not mono:
        fontFilter = QFontComboBox.ScalableFonts
    else:
        fontFilter = (QFontComboBox.ScalableFonts |
                      QFontComboBox.MonospacedFonts)
    fontComboBox.setFontFilters(fontFilter)
    fontComboBox.setCurrentFont(font)
    fontSizeSpinBox = QSpinBox(parent)
    fontSizeSpinBox.setAlignment(Qt.AlignRight)
    fontSizeSpinBox.setRange(6, 36)
    fontSizeSpinBox.setSuffix(" pt")
    fontSizeSpinBox.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
    fontSizeSpinBox.setValue(font.pointSize())
    if tooltips is not None:
        tooltips.append((fontComboBox, """\
<p><b>{0} Font</b></p><p>The font family to use for the {0} Font.</p>"""
                        .format(which)))
        tooltips.append((fontSizeSpinBox, """\
<p><b>{0} Font Size</b></p><p>The font point size to use for the {0}
Font.</p>""".format(which)))
    setattr(parent, "{}FontComboBox".format(name.lower()), fontComboBox)
    setattr(parent, "{}FontSizeSpinBox".format(name.lower()),
            fontSizeSpinBox)


def updatable_tooltips(Class):
    def tooltips(self): # Make tooltips a lazily created r/o property
        if getattr(self, "_tooltips", None) is None:
            setattr(self, "_tooltips", [])
        return self._tooltips
    setattr(Class, "tooltips", property(tooltips))

    def updateToolTips(self, on):
        for widget, tip in self.tooltips:
            widget.setToolTip(tip if on else "")

    setattr(Class, "updateToolTips", updateToolTips)
    return Class


def prepareModalDialog(self):
    self.setWindowModality(Qt.WindowModal)
    self.setWindowFlags(
        self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
    QShortcut(QKeySequence(QKeySequence.HelpContents), self, self.help)


def rulesTip(tip, sortAs=True):
    title = "Sort As Rules" if sortAs else "Page Range Rules"
    return "<p><b>{}</b></p><p>{}</p>".format(title,
                                              tip.replace("\n\n", "<p>"))


def elidePatchHtml(text, state, maxlen=50):
    # Elide if too long; wrap in the std font; patch with user's display
    # fonts
    text = elideHtml(text, maxlen, allowPara=False)
    text = """\
<span style="font-family: '{}'; font-size: {}pt;">{}</span>""".format(
        state.stdFontFamily, sanePointSize(state.stdFontSize), text)
    patcher = lambda match: patchFont(
        match, state.stdFontFamily, state.stdFontSize, state.altFontFamily,
        state.altFontSize, state.monoFontFamily, state.monoFontSize)
    return PATCH_FONT_RX.sub(patcher, text)
