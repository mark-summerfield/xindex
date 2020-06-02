#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import itertools
import os
import re
import time
import webbrowser

from PySide.QtCore import QSettings, Qt, QTimer, QUrl
from PySide.QtGui import (
    QApplication, QHBoxLayout, QIcon, QKeySequence, QLabel, QMainWindow,
    QShortcut, QToolButton, QVBoxLayout, QWidget)
from PySide.QtWebKit import QWebPage, QWebView

import Lib
import Qrc # noqa
import Widgets
from Const import UTF8


class Form(QMainWindow):

    def __init__(self, home, parent=None, *, stayOnTop=False, debug=False):
        super().__init__(parent)
        if stayOnTop:
            flags = self.windowFlags()
            flags |= Qt.WindowStaysOnTopHint
            self.setWindowFlags(flags)
        self.home = home
        self.debug = debug
        self.filenamesForWord = {}
        self.titleForFilename = {}
        self.createWidgets()
        self.createLayout()
        self.createConnections()
        self.createShortcuts()
        self.changePage(self.home)
        self.updateUi()
        if self.debug:
            self.mtime = 0
            self.timer = QTimer(self)
            self.timer.start(250)
            self.timer.timeout.connect(self.timeout)
        self.loadSettings()
        with open(Lib.get_path("doc/xix_style.css"), "r",
                  encoding=UTF8) as file:
            self.css = file.read()
        self.browser.setFocus()
        self.setWindowTitle("Help — {}".format(
            QApplication.applicationName()))


    def timeout(self):
        mtime = self.get_mtime()
        if mtime and mtime != self.mtime:
            self.mtime = mtime
            self.browser.reload()


    def get_mtime(self):
        filename = self.browser.url().toLocalFile()
        try:
            return os.path.getmtime(filename) if filename else 0
        except FileNotFoundError:
            time.sleep(0.1)
            return 0


    def createWidgets(self):
        self.backButton = QToolButton()
        self.backButton.setIcon(QIcon(":/go-back.svg"))
        self.backButton.setText("&Back")
        self.backButton.setToolTip("""\
<p><b>Back</b> ({})</p>
<p>Navigate to the previous page.</p>""".format(
            QKeySequence("Alt+Left").toString()))
        self.forwardButton = QToolButton()
        self.forwardButton.setIcon(QIcon(":/go-forward.svg"))
        self.forwardButton.setText("&Forward")
        self.forwardButton.setToolTip("""\
<p><b>Forward</b> ({})</p>
<p>Navigate to the page you've just come back from.</p>""".format(
            QKeySequence("Alt+Right").toString()))
        self.contentsButton = QToolButton()
        self.contentsButton.setIcon(QIcon(":/go-home.svg"))
        self.contentsButton.setText("&Contents")
        self.contentsButton.setToolTip("""\
<p><b>Contents</b> ({})</p>
<p>Navigate to the contents page.</p>""".format(
            QKeySequence("Alt+Home").toString()))
        self.searchLineEdit = Widgets.LegendLineEdit.LineEdit(
            "Search (F3 or Ctrl+F)")
        self.searchLineEdit.setToolTip("""\
<p><b>Search editor</p>
<p>Type in a word to search for in the online help pages and press
<b>Enter</b> or <b>F3</b> to search.</p>""")
        self.zoomInButton = QToolButton()
        self.zoomInButton.setIcon(QIcon(":/zoomin.svg"))
        self.zoomInButton.setText("&Zoom In")
        self.zoomInButton.setToolTip("""\
<p><b>Zoom In</b> ({})</p>
<p>Make the text bigger.</p>""".format(
            QKeySequence("Alt++").toString()))
        self.zoomOutButton = QToolButton()
        self.zoomOutButton.setIcon(QIcon(":/zoomout.svg"))
        self.zoomOutButton.setText("Zoom &Out")
        self.zoomOutButton.setToolTip("""\
<p><b>Zoom Out</b> ({})</p>
<p>Make the text smaller.</p>""".format(
            QKeySequence("Alt+-").toString()))
        width = self.fontMetrics().width(self.zoomOutButton.text() + " ")
        for button in (self.backButton, self.forwardButton,
                       self.contentsButton, self.zoomInButton,
                       self.zoomOutButton):
            button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            button.setMinimumWidth(width)
            button.setFocusPolicy(Qt.NoFocus)
        self.browser = QWebView()
        page = self.browser.page()
        page.setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        if self.debug:
            self.urlLabel = QLabel()


    def createLayout(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self.backButton)
        hbox.addWidget(self.forwardButton)
        hbox.addWidget(self.contentsButton)
        hbox.addWidget(self.searchLineEdit, 1)
        hbox.addWidget(self.zoomInButton)
        hbox.addWidget(self.zoomOutButton)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.browser, 1)
        if self.debug:
            vbox.addWidget(self.urlLabel)
        widget = QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)


    def createConnections(self):
        self.browser.urlChanged.connect(self.updateUi)
        self.browser.linkClicked.connect(self.changePage)
        self.backButton.clicked.connect(self.browser.back)
        self.forwardButton.clicked.connect(self.browser.forward)
        self.contentsButton.clicked.connect(
            lambda: self.changePage(self.home))
        self.searchLineEdit.returnPressed.connect(self.search)
        self.searchLineEdit.textEdited.connect(self.search)
        self.zoomInButton.clicked.connect(lambda: self.zoom(1.1))
        self.zoomOutButton.clicked.connect(lambda: self.zoom(0.9))


    def createShortcuts(self):
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.close)
        QShortcut(QKeySequence("Alt+Left"), self, self.browser.back)
        QShortcut(QKeySequence("Alt+Right"), self, self.browser.forward)
        QShortcut(QKeySequence("Alt+Home"), self, self.contentsButton.click)
        QShortcut(QKeySequence("Ctrl++"), self, self.zoomInButton.click)
        QShortcut(QKeySequence("Ctrl+="), self, self.zoomInButton.click)
        QShortcut(QKeySequence("Ctrl+-"), self, self.zoomOutButton.click)
        QShortcut(QKeySequence("F3"), self, self.search)
        QShortcut(QKeySequence("Ctrl+F"), self, self.search)
        if self.debug:
            QShortcut(QKeySequence(Qt.Key_F5), self, self.browser.reload)


    def changePage(self, page):
        if isinstance(page, QUrl) and not page.scheme():
            page = page.toString()
        if isinstance(page, str):
            url = QUrl.fromLocalFile(Lib.get_path(os.path.join("doc",
                                                               page)))
        else:
            url = page
            if not url.isLocalFile():
                webbrowser.open(url.toString())
                return
        self.browser.setUrl(url)


    def search(self):
        self.searchLineEdit.setFocus()
        text = self.searchLineEdit.text()
        words = self.searchWordsSet(text)
        if not words:
            return
        if not self.filenamesForWord:
            self.populateUrlForWord()
        result = [HTML_TOP.format(self.css)]
        pages1, pages2 = self.acquirePageSets(words)
        if not pages1 and not pages2:
            result.append("""\
<h3><font color=darkgray>No help pages match <i>{}</i></font></h3>"""
                          .format("</i> or <i>".join(text.split())))
        else:
            n = len(pages1) + len(pages2)
            result.append("""\
<h3><font color=navy>{:,} help page{} match{} <i>{}</i>:</font></h3><ul>"""
                          .format(n, "s" if n != 1 else "",
                                  "es" if n == 1 else "",
                                  "</i> or <i>".join(text.split())))
            for page in itertools.chain(sorted(pages1), (None,),
                                        sorted(pages2)):
                line = ("</ul><br><ul>" if page is None else
                        "<li><a href='{}'>{}</a></li>\n".format(page[1],
                                                                page[0]))
                result.append(line)
            result.append("</ul>\n")
        result.append("</body></html>\n")
        self.browser.setHtml("".join(result))


    def searchWordsSet(self, text):
        if len(text) < 2:
            return None
        words = set()
        for word in frozenset(re.split(r"\W+", text.strip().casefold())):
            words.add(word)
            words.add(Lib.stem(word))
        return words


    def acquirePageSets(self, words):
        pages1 = set()
        pages2 = set()
        for word in words:
            filenames = self.filenamesForWord.get(word, set())
            if filenames:
                for filename in filenames:
                    title = self.titleForFilename[filename]
                    if words & self.searchWordsSet(
                            Lib.htmlToPlainText(title)):
                        pages1.add((title, filename))
                    else:
                        pages2.add((title, filename))
        return pages1, pages2


    def populateUrlForWord(self):
        self.filenamesForWord = {}
        path = Lib.get_path("doc")
        for filename in os.listdir(path):
            if filename.endswith(".html"):
                with open(os.path.join(path, filename), "r",
                          encoding=UTF8) as file:
                    text = file.read()
                match = re.search(r"<title>(.*?)</title>", text,
                                  re.IGNORECASE)
                title = filename if match is None else match.group(1)
                self.titleForFilename[filename] = title
                text = Lib.htmlToPlainText(text).casefold()
                for word in re.split(r"\W+", text):
                    if word:
                        self.filenamesForWord.setdefault(
                            word, set()).add(filename)
                        wordstem = Lib.stem(word)
                        if wordstem and wordstem != word:
                            self.filenamesForWord.setdefault(
                                wordstem, set()).add(filename)


    def zoom(self, factor):
        factor *= self.browser.textSizeMultiplier()
        self.browser.setTextSizeMultiplier(factor)
        settings = QSettings()
        settings.setValue(HELP_ZOOM, factor)


    def updateUi(self):
        history = self.browser.history()
        self.backButton.setEnabled(history.canGoBack())
        self.forwardButton.setEnabled(history.canGoForward())
        self.contentsButton.setEnabled(self.browser.url() != self.home)
        if self.debug:
            self.urlLabel.setText(self.browser.url().toString())
            self.mtime = self.get_mtime()


    def showEvent(self, event):
        self.loadSettings()


    def loadSettings(self):
        settings = QSettings()
        zoom = float(settings.value(HELP_ZOOM, 1.0))
        if not Lib.isclose(zoom, 1.0):
            self.browser.setTextSizeMultiplier(zoom)
        self.restoreGeometry(settings.value(HELP_GEOMETRY))


    def hideEvent(self, event):
        self.saveSettings()


    def closeEvent(self, event):
        self.saveSettings()


    def saveSettings(self):
        settings = QSettings()
        settings.setValue(HELP_GEOMETRY, self.saveGeometry())


HELP_GEOMETRY = "Help/Geometry"
HELP_ZOOM = "Help/Zoom"

HTML_TOP = """\
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<link rel="stylesheet" type="text/css" href="xix_style.css">
<style>
{}
</style>
<title>Help Find Matches</title>
</head>
<body>
"""

if __name__ == "__main__":
    import sys
    stayOnTop = len(sys.argv) > 1
    app = QApplication([])
    form = Form("xix_help.html", stayOnTop=stayOnTop, debug=True)
    form.show()
    app.exec_()
