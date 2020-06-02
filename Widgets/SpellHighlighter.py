#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import re

from PySide.QtCore import Qt
from PySide.QtGui import QSyntaxHighlighter, QTextCharFormat

import Spell


WORD_LIKE_RX = re.compile(r"\w+")


class Highlighter(QSyntaxHighlighter):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.unknownWords = []
        self.wordsToIgnore = set()
        self.spellFormat = QTextCharFormat()
        self.spellFormat.setFontUnderline(True)
        self.spellFormat.setUnderlineColor(Qt.red)
        self.spellFormat.setUnderlineStyle(QTextCharFormat.WaveUnderline)


    def highlightBlock(self, text):
        self.unknownWords = []
        language = self.state.language.value
        for match in WORD_LIKE_RX.finditer(text):
            word = match.group()
            start = match.start()
            length = match.end() - match.start()
            if (word not in self.wordsToIgnore and
                    not Spell.check(word, language)):
                self.setFormat(start, length, self.spellFormat)
                self.unknownWords.append((start, word))
