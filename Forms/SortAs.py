#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import collections
import functools
import itertools
import re

import roman
from PySide.QtCore import QSettings
from PySide.QtGui import (
    QApplication, QDialog, QDialogButtonBox, QHBoxLayout, QIcon,
    QPushButton, QRadioButton, QVBoxLayout)

import Lib
import Saf
import Widgets
from Config import Gopt
from Const import CandidateKind


Candidate = collections.namedtuple(
    "Candidate", "candidate term_word candidate_word kind saf")


DIGITS_RX = re.compile(r"(?P<number>\d+)")


class Result:

    def __init__(self):
        self.sortas = None
        self.saf = Saf.AUTO


    def __str__(self):
        return "«{}» {}".format(self.sortas, self.saf)


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, term, candidates, result, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        self.term = term
        self.candidates = []
        for candidate in candidates:
            self.candidates.append(humanizedCandidate(
                term, candidate.candidate, candidate.saf))
        self.result = result
        self.setWindowTitle("Sort As — {}".format(
                            QApplication.applicationName()))
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.updateUi()
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        self.termLabel = Widgets.Label.HtmlLabel(
            "<p>Sort “{}” with</p>".format(Lib.elidePatchHtml(self.term,
                                                              self.state)))
        self.radioButtons = []
        seen = set()
        for index, candidate in enumerate(self.candidates, 1):
            candidate_word = str(candidate.candidate_word)
            name = self.nameForKind(candidate.kind, candidate_word)
            extra = ""
            if candidate_word in seen:
                extra = " (treat roman numbers as literal text)"
            else:
                seen.add(candidate_word)
            radioButton = QRadioButton("&{} “{}” as{} “{}”{}".format(
                index, candidate.term_word, name, candidate_word, extra))
            self.radioButtons.append(radioButton)
        self.radioButtons[0].setChecked(True)
        self.customRadioButton = QRadioButton("&Custom:")
        self.tooltips.append((self.customRadioButton, """\
<p><b>Custom</b></p>
<p>If checked, this entry's <b>Automatically Calculate Sort As</b>
setting will be <i>unchecked</i>, and the sort as text entered here will
be used as ther entry's sort as text.</p>"""))
        self.sortAsEdit = Widgets.LineEdit.LineEdit(self.state)
        self.tooltips.append((self.sortAsEdit, """\
<p><b>Custom Sort As editor</b></p>
<p>If <b>Custom</b> is checked, this entry's <b>Automatically Calculate
Sort As</b> setting will be <i>unchecked</i>, and the sort as text
entered here will be used as ther entry's sort as text.</p>"""))
        self.sortAsEdit.setText(self.candidates[0].candidate)
        self.sortAsEdit.selectAll()
        self.buttonBox = QDialogButtonBox()
        self.okButton = QPushButton(QIcon(":/ok.svg"), "&OK")
        self.tooltips.append((self.okButton, """\
<p><b>OK</b></p>
<p>Use the specified or custom sort as text for entry
“{}”.</p>""".format(Lib.elidePatchHtml(self.term, self.state))))
        self.buttonBox.addButton(
            self.okButton, QDialogButtonBox.AcceptRole)
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.tooltips.append((self.helpButton,
                              "Help on the Sort As dialog"))
        self.buttonBox.addButton(
            self.helpButton, QDialogButtonBox.HelpRole)


    def nameForKind(self, kind, candidate_word):
        name = kind.name.lower()
        if name == "unchanged":
            name = ""
        elif (name == "roman" or (
                name == "phrase" and
                re.fullmatch(r"[\d.]+", candidate_word) is not None)):
            name = "number"
        if name:
            name = " " + name
        return name


    def layoutWidgets(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.termLabel)
        for radioButton in self.radioButtons:
            vbox.addWidget(radioButton)
        hbox = QHBoxLayout()
        hbox.addWidget(self.customRadioButton)
        hbox.addWidget(self.sortAsEdit)
        vbox.addLayout(hbox)
        vbox.addWidget(self.buttonBox)
        self.setLayout(vbox)


    def createConnections(self):
        for radioButton in itertools.chain((self.customRadioButton,),
                                           self.radioButtons):
            radioButton.toggled.connect(self.updateUi)
        self.sortAsEdit.textChanged.connect(self.updateUi)
        self.okButton.clicked.connect(self.accept)
        self.helpButton.clicked.connect(self.help)


    def help(self):
        self.state.help("xix_ref_dlg_sortas.html")


    def updateUi(self):
        self.sortAsEdit.setEnabled(self.customRadioButton.isChecked())
        with Lib.BlockSignals(self.sortAsEdit):
            for i, radioButton in enumerate(self.radioButtons):
                if radioButton.isChecked():
                    self.sortAsEdit.setText(self.candidates[i].candidate)
                    self.sortAsEdit.selectAll()
                    break
        self.okButton.setEnabled(
            not self.customRadioButton.isChecked() or
            (self.customRadioButton.isChecked() and
             bool(self.sortAsEdit.toPlainText())))


    def reject(self):
        self.accept()


    def accept(self):
        if self.customRadioButton.isChecked():
            self.result.sortas = self.sortAsEdit.toPlainText()
            self.result.saf = Saf.CUSTOM
        else:
            for index, radioButton in enumerate(self.radioButtons):
                if radioButton.isChecked():
                    self.result.sortas = self.candidates[index].candidate
                    kind = self.candidates[index].kind
                    if kind is CandidateKind.LITERAL:
                        saf = Saf.AUTO_BASIC
                    elif kind is CandidateKind.NUMBER:
                        saf = Saf.AUTO_NUMBER
                    elif kind is CandidateKind.ROMAN:
                        saf = Saf.AUTO_NUMBER_ROMAN
                    elif kind is CandidateKind.PHRASE:
                        saf = Saf.AUTO
                    elif kind is CandidateKind.UNCHANGED:
                        saf = self.candidates[index].saf
                    self.result.saf = saf
                    break
        super().accept()


def makeCandidate(candidate, candidate_words, saf, word, n, kind=None):
    computeKind = kind is None
    lword = word.casefold()
    for cword in candidate_words:
        if computeKind:
            kind = (CandidateKind.LITERAL if cword == lword else
                    CandidateKind.NUMBER)
        if cword.isdigit() and n == int(cword):
            return Candidate(candidate, word, cword, kind, saf)
        match = DIGITS_RX.search(cword)
        if match is not None:
            m = int(match.group("number"))
            if m == n:
                return Candidate(candidate, word, cword, kind, saf)


def humanizedCandidate(term, candidate, saf):
    plain_term = Lib.htmlToPlainText(term)
    term_words = plain_term.split()
    lterm_words = plain_term.casefold().split()
    candidate_words = candidate.split()
    unchanged = []
    make_candidate = functools.partial(makeCandidate, candidate,
                                       candidate_words, saf)
    for lword, word in zip(lterm_words, term_words):
        n = kind = match = None
        if lword.isdigit():
            n = int(lword)
        if n is None:
            match = DIGITS_RX.search(lword)
            if match is not None:
                n = int(match.group("number"))
        if n is None and isRoman(lword):
            n = numericValueOf(lword)
            kind = CandidateKind.ROMAN
        if n is not None:
            numericCandidate = make_candidate(word, n, kind)
            if numericCandidate is not None:
                return numericCandidate
        if lword.isdigit() or isRoman(lword):
            words = frozenset(lterm_words) ^ frozenset(candidate_words)
            if words:
                n = numericValueOf(lword)
                if n is not None:
                    sword = Lib.spellNumber(n)
                    sword_set = frozenset(sword.split())
                    if sword_set == (sword_set & words):
                        return Candidate(candidate, word, sword,
                                         CandidateKind.PHRASE, saf)
        if lword in candidate_words:
            if lword.isdigit() or isRoman(lword):
                return Candidate(candidate, word, lword,
                                 CandidateKind.LITERAL, saf)
            unchanged.append(Candidate(
                candidate, word, lword, CandidateKind.UNCHANGED, saf))
        if "." in lword:
            dotlessWord = lword.replace(".", "")
            if dotlessWord in candidate_words:
                return Candidate(candidate, word, dotlessWord,
                                 CandidateKind.LITERAL, saf)
            for cw in candidate_words:
                if cw.replace(".", "").isdigit():
                    kind = (CandidateKind.NUMBER if cw.startswith("0")
                            else CandidateKind.LITERAL)
                    return Candidate(candidate, word, cw, kind, saf)
    if unchanged:
        return unchanged[0]
    word = candidate.split()[0]
    return Candidate(candidate, word, word, CandidateKind.UNCHANGED, saf)


def numericValueOf(text):
    try:
        return roman.fromRoman(text.upper())
    except roman.RomanError:
        try:
            return int(text)
        except ValueError:
            pass


def isRoman(word):
    try:
        roman.fromRoman(word.upper())
        return True
    except roman.RomanError:
        return False


if __name__ == "__main__":
    import sys
    import SortAs
    import Qrc # noqa
    import HelpForm
    app = QApplication([])
    app.setOrganizationName("Qtrac Ltd.")
    app.setOrganizationDomain("qtrac.eu")
    app.setApplicationName("XindeX-Test")
    app.setApplicationVersion("1.0.0")
    class FakeState:
        def __init__(self):
            self.stdFontFamily = "Times New Roman"
            self.stdFontSize = 13
            self.altFontFamily = "Arial"
            self.altFontSize = 13
            self.monoFontFamily = "Courier New"
            self.monoFontSize = 12
            self.window = None
            self.helpForm = None
        def help(self, page=None):
            if self.helpForm is None:
                self.helpForm = HelpForm.Form("xix_help.html", self.window)
            if page is not None:
                self.helpForm.changePage(page)
            self.helpForm.show()
            self.helpForm.raise_()
            self.helpForm.activateWindow()
    state = FakeState()
    result = Result()
    term = "<b>C</b> <i>language</i>"
    if len(sys.argv) > 1:
        term = " ".join(sys.argv[1:])
    candidates = SortAs.candidatesFor(term, "wordByWordCMS16", frozenset())
    form = Form(state, term, candidates, result)
    form.exec_()
    print(result)
