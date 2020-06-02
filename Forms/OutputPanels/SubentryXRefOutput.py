#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtGui import (
    QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QVBoxLayout,
    QWidget)

from Config import Gconf
import Widgets
from Const import BLANK_SPACE_HTML, SeeAlsoPositionKind


class Panel(QWidget):

    def __init__(self, state, config, parent):
        super().__init__(parent)
        self.state = state
        self.config = config
        self.form = parent
        self.createWidgets()
        self.layoutWidgets()


    def createWidgets(self):
        self.formatPanel = Widgets.FormatPanel.Panel(self.state, self)
        formatActions = self.formatPanel.formatActions

        self.seePrefixLabel = QLabel("Pref&ix")
        self.seePrefixTextEdit = Widgets.LineEdit.SpacesHtmlLineEdit(
            self.state, 3, formatActions=formatActions)
        self.seePrefixLabel.setBuddy(self.seePrefixTextEdit)
        self.seePrefixTextEdit.setHtml(self.config.get(
                                       Gconf.Key.SubSeePrefix))
        self.form.tooltips.append((self.seePrefixTextEdit, """\
<p><b>See, Prefix</b></p>
<p>The text to separate a subentry's <i>see</i> cross-refs from the term
or pages that precede them.</p>{}""".format(BLANK_SPACE_HTML)))
        self.seeLabel = QLabel("T&ext")
        self.seeTextEdit = Widgets.LineEdit.SpacesHtmlLineEdit(
            self.state, 10, formatActions=formatActions)
        self.seeLabel.setBuddy(self.seeTextEdit)
        self.seeTextEdit.setHtml(self.config.get(Gconf.Key.SubSee))
        self.form.tooltips.append((self.seeTextEdit, """\
<p><b>See, Text</b></p>
<p>The text to indicate a subentry's <i>see</i>
cross-ref(s).</p>{}""".format(BLANK_SPACE_HTML)))
        self.seeSepLabel = QLabel("Sepa&rator")
        self.seeSepTextEdit = Widgets.LineEdit.SpacesHtmlLineEdit(
            self.state, 3, formatActions=formatActions)
        self.seeSepLabel.setBuddy(self.seeSepTextEdit)
        self.seeSepTextEdit.setHtml(self.config.get(
                                    Gconf.Key.SubSeeSeparator))
        self.form.tooltips.append((self.seeSepTextEdit, """\
<p><b>See, Separator</b></p>
<p>The text to separate each of a subentry's <i>see</i> cross-references if
there are more than one.</p>{}""".format(BLANK_SPACE_HTML)))
        self.seeSuffixLabel = QLabel("Su&ffix")
        self.seeSuffixTextEdit = Widgets.LineEdit.SpacesHtmlLineEdit(
            self.state, 3, formatActions=formatActions)
        self.seeSuffixLabel.setBuddy(self.seeSuffixTextEdit)
        self.seeSuffixTextEdit.setHtml(self.config.get(
                                       Gconf.Key.SubSeeSuffix))
        self.form.tooltips.append((self.seeSuffixTextEdit, """\
<p><b>See, Suffix</b></p>
<p>The text to follow a subentry's <i>see</i>
cross-references</p>{}""".format(BLANK_SPACE_HTML)))

        self.seeAlsoPrefixLabel = QLabel("&Prefix")
        self.seeAlsoPrefixTextEdit = Widgets.LineEdit.SpacesHtmlLineEdit(
            self.state, 3, formatActions=formatActions)
        self.seeAlsoPrefixLabel.setBuddy(self.seeAlsoPrefixTextEdit)
        self.seeAlsoPrefixTextEdit.setHtml(self.config.get(
                                           Gconf.Key.SubSeeAlsoPrefix))
        self.form.tooltips.append((self.seeAlsoPrefixTextEdit, """\
<p><b>See Also, Prefix</b></p>
<p>The text to separate a subentry's <i>see also</i> cross-refs from the
term or pages that precede them.</p>{}""".format(BLANK_SPACE_HTML)))
        self.seeAlsoLabel = QLabel("Te&xt")
        self.seeAlsoTextEdit = Widgets.LineEdit.SpacesHtmlLineEdit(
            self.state, 10, formatActions=formatActions)
        self.seeAlsoLabel.setBuddy(self.seeAlsoTextEdit)
        self.seeAlsoTextEdit.setHtml(self.config.get(Gconf.Key.SubSeeAlso))
        self.form.tooltips.append((self.seeAlsoTextEdit, """\
<p><b>See Also, Text</b></p>
<p>The text to indicate a subentry's <i>see also</i>
cross-ref(s).</p>{}""".format(BLANK_SPACE_HTML)))
        self.seeAlsoSepLabel = QLabel("&Separator")
        self.seeAlsoSepTextEdit = Widgets.LineEdit.SpacesHtmlLineEdit(
            self.state, 3, formatActions=formatActions)
        self.seeAlsoSepLabel.setBuddy(self.seeAlsoSepTextEdit)
        self.seeAlsoSepTextEdit.setHtml(self.config.get(
                                        Gconf.Key.SubSeeAlsoSeparator))
        self.form.tooltips.append((self.seeAlsoSepTextEdit, """\
<p><b>See Also, Separator</b></p>
<p>The text to separate each of a subentry's <i>see also</i>
cross-references if there are more than one.</p>{}""".format(
            BLANK_SPACE_HTML)))
        self.seeAlsoSuffixLabel = QLabel("S&uffix")
        self.seeAlsoSuffixTextEdit = Widgets.LineEdit.SpacesHtmlLineEdit(
            self.state, 3, formatActions=formatActions)
        self.seeAlsoSuffixLabel.setBuddy(self.seeAlsoSuffixTextEdit)
        self.seeAlsoSuffixTextEdit.setHtml(self.config.get(
                                           Gconf.Key.SubSeeAlsoSuffix))
        self.form.tooltips.append((self.seeAlsoSuffixTextEdit, """\
<p><b>See Also, Suffix</b></p>
<p>The text to follow a subentry's <i>see also</i>
cross-references</p>{}""".format(BLANK_SPACE_HTML)))
        self.seeAlsoPositionLabel = QLabel("P&osition")
        self.seeAlsoPositionComboBox = QComboBox()
        self.seeAlsoPositionLabel.setBuddy(self.seeAlsoPositionComboBox)
        seeAlsoPos = self.config.get(Gconf.Key.SubSeeAlsoPosition)
        index = -1
        for i, pos in enumerate(SeeAlsoPositionKind):
            self.seeAlsoPositionComboBox.addItem(pos.text, pos.value)
            if pos is seeAlsoPos:
                index = i
        self.seeAlsoPositionComboBox.setCurrentIndex(index)
        self.form.tooltips.append((self.seeAlsoPositionComboBox, """\
<p><b>Position</b></p>
<p>Where <i>see also</i> cross-references should appear in relation to the
subentry they belong to.</p>"""))

        self.formatPanel.state.editors = [
            self.seePrefixTextEdit, self.seeTextEdit,
            self.seeSepTextEdit, self.seeSuffixTextEdit,
            self.seeAlsoPrefixTextEdit, self.seeAlsoTextEdit,
            self.seeAlsoSepTextEdit, self.seeAlsoSuffixTextEdit]


    def layoutWidgets(self):
        layout = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.formatPanel)
        layout.addLayout(hbox)

        seeGroup = QGroupBox("See")
        form = QFormLayout()
        form.addRow(self.seeLabel, self.seeTextEdit)
        hbox = QHBoxLayout()
        hbox.addWidget(self.seePrefixTextEdit)
        hbox.addWidget(self.seeSepLabel)
        hbox.addWidget(self.seeSepTextEdit)
        hbox.addWidget(self.seeSuffixLabel)
        hbox.addWidget(self.seeSuffixTextEdit)
        form.addRow(self.seePrefixLabel, hbox)
        seeGroup.setLayout(form)
        layout.addWidget(seeGroup)

        alsoGroup = QGroupBox("See Also")
        form = QFormLayout()
        form.addRow(self.seeAlsoLabel, self.seeAlsoTextEdit)
        hbox = QHBoxLayout()
        hbox.addWidget(self.seeAlsoPrefixTextEdit)
        hbox.addWidget(self.seeAlsoSepLabel)
        hbox.addWidget(self.seeAlsoSepTextEdit)
        hbox.addWidget(self.seeAlsoSuffixLabel)
        hbox.addWidget(self.seeAlsoSuffixTextEdit)
        form.addRow(self.seeAlsoPrefixLabel, hbox)
        form.addRow(self.seeAlsoPositionLabel, self.seeAlsoPositionComboBox)
        alsoGroup.setLayout(form)
        layout.addWidget(alsoGroup)

        layout.addStretch(2)

        self.setLayout(layout)
