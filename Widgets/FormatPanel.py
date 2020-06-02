#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Qt
from PySide.QtGui import QSpinBox, QToolBar

import Actions
from Const import MAX_FONT_SIZE, MIN_FONT_SIZE


class FormatState:

    def __init__(self, appState, window):
        self.appState = appState
        self.window = window
        self.editors = []

    @property
    def stdFontFamily(self):
        return self.appState.stdFontFamily


    @property
    def stdFontSize(self):
        return self.appState.stdFontSize


    @property
    def altFontFamily(self):
        return self.appState.altFontFamily


    @property
    def altFontSize(self):
        return self.appState.altFontSize


    @property
    def monoFontFamily(self):
        return self.appState.monoFontFamily


    @property
    def monoFontSize(self):
        return self.appState.monoFontSize


class Panel(QToolBar):

    def __init__(self, state, parent=None, *, editableFontSize=False):
        super().__init__(parent)
        self.appState = state
        self.state = FormatState(self.appState, self)
        self.fontSizeSpinBox = None
        if editableFontSize:
            self.fontSizeSpinBox = QSpinBox()
            self.fontSizeSpinBox.setAlignment(Qt.AlignRight)
            self.fontSizeSpinBox.setFocusPolicy(Qt.NoFocus)
            self.fontSizeSpinBox.setRange(MIN_FONT_SIZE, MAX_FONT_SIZE)
            self.fontSizeSpinBox.setSuffix(" pt")
            self.fontSizeSpinBox.setValue(self.appState.stdFontSize)
            self.fontSizeSpinBox.setToolTip("""<p><b>Font Size</b></p>
<p>Set the font size in points.</p>""")
        self.formatActions = Actions.Format.Actions(
            self, self.fontSizeSpinBox)
        for action in self.formatActions.forToolbar():
            if action is not None:
                self.addAction(action)
            else:
                self.addSeparator()
        if editableFontSize:
            self.addWidget(self.fontSizeSpinBox)
