#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import re

from PySide.QtCore import QEvent, Qt
from PySide.QtGui import QLabel


class HtmlLabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextFormat(Qt.RichText)


class Label(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextFormat(Qt.RichText)
        self.enabledText = ""
        self.disabledText = ""


    def setText(self, text):
        self.enabledText = text
        self.disabledText = re.sub(r"color=#[\dA-Fa-f]+", "color=#888",
                                   text.replace("chain.svg",
                                                "chain-disabled.svg"))
        self.refreshText()


    def clear(self):
        self.enabledText = ""
        self.disabledText = ""
        self.refreshText()


    def changeEvent(self, event):
        if event.type() == QEvent.EnabledChange:
            self.refreshText()


    def refreshText(self):
        text = self.enabledText if self.isEnabled() else self.disabledText
        super().setText(text)
