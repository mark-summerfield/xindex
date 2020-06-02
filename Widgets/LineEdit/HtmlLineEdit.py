#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import html
import re

from PySide.QtCore import QSize, Qt
from PySide.QtGui import (
    QBrush, QFont, QSyntaxHighlighter, QTextCharFormat, QTextCursor,
    QTextEdit)

import Lib
from . import LineEdit
from Const import MIN_FONT_SIZE, VISUAL_SPACE, WIN


TAG_RX = re.compile(r"(<[^>]*?>)")
HTML_FRAGMENT = re.compile(r"<!--StartFragment-->(.*)<!--EndFragment-->")


class HtmlLineEdit(LineEdit):

    def __init__(self, state, parent=None, *, maxLines=1,
                 allowNewlines=False, formatActions=None, strip=True):
        super().__init__(state, parent, maxLines=maxLines,
                         allowNewlines=allowNewlines,
                         formatActions=formatActions)
        self.strip = strip
        self.setAcceptRichText(True)
        self.cursorPositionChanged.connect(self.updateActions)
        self.doing = False


    def clear(self):
        super().clear()
        self.document().clear()
        self.setFont(QFont(self.state.stdFontFamily,
                           self.state.stdFontSize))


    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.updateActions()


    def insertFromMimeData(self, data):
        text = data.html()
        match = HTML_FRAGMENT.search(text)
        if match is not None:
            self.insertHtml(match.group(1))
        else:
            self.insertPlainText(data.text())
        data.clear()


    def updateActions(self):
        if self.formatActions is None:
            self.formatActions = self.state.window.formatActions
        if self.formatActions is not None:
            charFormat = self.currentCharFormat()
            bold = charFormat.fontWeight() > QFont.Normal
            italic = charFormat.fontItalic()
            underline = charFormat.fontUnderline()
            superscript = subscript = False
            valign = charFormat.verticalAlignment()
            if valign == QTextCharFormat.AlignSuperScript:
                superscript = True
            elif valign == QTextCharFormat.AlignSubScript:
                subscript = True
            family = charFormat.fontFamily()
            size = round(charFormat.fontPointSize())
            if size < MIN_FONT_SIZE:
                size = self.state.stdFontSize
            self.formatActions.update(bold, italic, underline,
                                      superscript, subscript, family, size)


    def toggleItalic(self):
        self.setFontItalic(not self.fontItalic())


    def toggleUnderline(self):
        self.setFontUnderline(not self.fontUnderline())


    def toggleBold(self):
        self.setFontWeight(
            QFont.Normal if self.fontWeight() > QFont.Normal else
            QFont.Bold)


    def setSuperscript(self):
        charFormat = self.currentCharFormat()
        charFormat.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        self.mergeCurrentCharFormat(charFormat)
        self.document().setModified(True)


    def setSubscript(self):
        charFormat = self.currentCharFormat()
        charFormat.setVerticalAlignment(QTextCharFormat.AlignSubScript)
        self.mergeCurrentCharFormat(charFormat)
        self.document().setModified(True)


    def noSuperSubscript(self):
        charFormat = self.currentCharFormat()
        charFormat.setVerticalAlignment(QTextCharFormat.AlignNormal)
        self.mergeCurrentCharFormat(charFormat)
        self.document().setModified(True)


    def setStdFont(self, size=None):
        charFormat = self.currentCharFormat()
        charFormat.setFontFamily(self.state.stdFontFamily)
        charFormat.setFontPointSize(size or self.state.stdFontSize)
        charFormat.setFontFixedPitch(False)
        self.mergeCurrentCharFormat(charFormat)
        self.document().setModified(True)


    def setAltFont(self, size=None):
        charFormat = self.currentCharFormat()
        charFormat.setFontFamily(self.state.altFontFamily)
        charFormat.setFontPointSize(size or self.state.altFontSize)
        charFormat.setFontFixedPitch(False)
        self.mergeCurrentCharFormat(charFormat)
        self.document().setModified(True)


    def setMonoFont(self, size=None):
        charFormat = self.currentCharFormat()
        charFormat.setFontFamily(self.state.monoFontFamily)
        charFormat.setFontPointSize(size or self.state.monoFontSize)
        charFormat.setFontFixedPitch(True)
        self.mergeCurrentCharFormat(charFormat)
        self.document().setModified(True)


    def setFontSize(self, value):
        if self.formatActions is None:
            self.formatActions = self.state.window.formatActions
        if self.formatActions is not None:
            action = self.formatActions.fontGroup.checkedAction()
            if action is self.formatActions.altFontAction:
                self.setAltFont(value)
            elif action is self.formatActions.monoFontAction:
                self.setMonoFont(value)
            else:
                self.setStdFont(value)


    def replaceWord(self, word):
        if self.doing:
            return
        oldWord, end = self.wordAndPosition()
        start = end - len(oldWord)
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.clearSelection()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(word)
        cursor.endEditBlock()
        self.setFocus()
        self.wordCompleted.emit()


    def keyPressEvent(self, event):
        ctrl = bool(int(event.modifiers()) & int(Qt.ControlModifier))
        shift = bool(int(event.modifiers()) & int(Qt.ShiftModifier))
        key = event.key()
        handled = False
        if ctrl:
            if key == Qt.Key_Y or (shift and key == Qt.Key_Z):
                self.redo() # Ctrl+Y or Shift+Ctrl+Z
                handled = True
            elif key == Qt.Key_Z:
                self.undo() # Ctrl+Z
                handled = True
            if handled:
                event.ignore()
                return
        super().keyPressEvent(event)


    def undo(self):
        self.doing = True
        try:
            super().undo()
        finally:
            self.doing = False


    def redo(self):
        self.doing = True
        try:
            super().redo()
        finally:
            self.doing = False


    def setHtml(self, html, position=None):
        super().setHtml(html)
        self._restorePosition(position)


    def toHtml(self):
        texts = []
        block = self.document().begin()
        while block.isValid():
            iterator = block.begin()
            if self._multiline:
                texts.append("<p>")
            while iterator != block.end():
                fragment = iterator.fragment()
                if fragment.isValid():
                    format = fragment.charFormat()
                    family = format.fontFamily()
                    size = format.fontPointSize()
                    if int(size) == round(size):
                        size = int(size)
                    text = html.escape(fragment.text())
                    if (format.verticalAlignment() ==
                            QTextCharFormat.AlignSubScript):
                        text = "<sub>{}</sub>".format(text)
                    elif (format.verticalAlignment() ==
                            QTextCharFormat.AlignSuperScript):
                        text = "<sup>{}</sup>".format(text)
                    if format.fontUnderline():
                        text = "<u>{}</u>".format(text)
                    if format.fontItalic():
                        text = "<i>{}</i>".format(text)
                    if format.fontWeight() > QFont.Normal:
                        text = "<b>{}</b>".format(text)
                    if family:
                        text = ('<span style="font-size: {}pt; ' +
                                'font-family: \'{}\';">{}</span>').format(
                            Lib.sanePointSize(size), family, text)
                    texts.append(text)
                iterator += 1
            if self._multiline:
                texts.append("</p>")
            block = block.next()
        if texts == ["<p>", "</p>"]:
            return ""
        if self.strip:
            return "".join(texts).strip()
        return "".join(texts)


class HtmlPagesLineEdit(HtmlLineEdit):

    def __init__(self, state, parent=None, *, maxLines=None,
                 formatActions=None):
        super().__init__(state, parent, maxLines=maxLines,
                         formatActions=formatActions)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)


    def setFont(self, font):
        super().setFont(font)
        fm = self.fontMetrics()
        h = int(fm.height() * 1.4)
        self.setMinimumHeight(h * 2)
        if self.maxLines is not None:
            self.setMaximumHeight(h * self.maxLines)


class MultilineHtmlEdit(HtmlLineEdit):

    def __init__(self, state, parent=None, *, maxLines=None,
                 formatActions=None):
        super().__init__(state, parent, maxLines=maxLines,
                         allowNewlines=True, formatActions=formatActions)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._multiline = True


    def setFont(self, font):
        super().setFont(font)
        fm = self.fontMetrics()
        h = int(fm.height() * (1.4 if WIN else 1.2))
        self.setMinimumHeight(h * 2)
        if self.maxLines is not None:
            self.setMaximumHeight(h * self.maxLines)


VISUAL_SPACE_RX = re.compile(r"{}+".format(re.escape(VISUAL_SPACE)))


class SpaceHighlighter(QSyntaxHighlighter):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.spaceFormat = QTextCharFormat()
        self.spaceFormat.setForeground(QBrush(Qt.cyan))


    def highlightBlock(self, text):
        for match in VISUAL_SPACE_RX.finditer(text):
            start = match.start()
            length = match.end() - match.start()
            self.setFormat(start, length, self.spaceFormat)


class SpacesHtmlLineEdit(HtmlLineEdit):

    def __init__(self, state, length, parent=None, formatActions=None):
        super().__init__(state, parent, maxLines=1, allowNewlines=False,
                         formatActions=formatActions, strip=False)
        self.length = length
        self.spaceHighlighter = SpaceHighlighter(self.document())


    def sizeHint(self):
        if self.length is None:
            return super().sizeHint()
        return QSize(self.fontMetrics().width("W" * self.length),
                     self.maximumHeight())


    def minimumSizeHint(self):
        if self.length is None:
            return super().minimumSizeHint()
        return QSize(self.fontMetrics().width(
                     "W" * max(1, self.length // 3)), self.maximumHeight())


    def setHtml(self, text):
        if text is None:
            text = ""
        texts = []
        for chunk in TAG_RX.split(text):
            if not chunk.startswith("<"):
                chunk = chunk.replace(" ", VISUAL_SPACE)
            texts.append(chunk)
        super().setHtml("".join(texts))


    def toHtml(self):
        return super().toHtml().replace(VISUAL_SPACE, " ")


    def setPlainText(self, text):
        super().setPlainText(text.replace(" ", VISUAL_SPACE))


    def toPlainText(self):
        return super().toPlainText().replace(VISUAL_SPACE, " ")


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.insertPlainText(VISUAL_SPACE)
            event.ignore()
            return
        super().keyPressEvent(event)
