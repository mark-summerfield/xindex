#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

import Widgets
from Lib import elidePatchHtml


def setUpRadioButton(widget, entry, button, label, buttons, seen, tooltip):
    if entry is None:
        button.setEnabled(False)
        if label is not None:
            label.setEnabled(False)
    else:
        term = ""
        if label is not None:
            term = elidePatchHtml(widget.state.model.termPath(entry.eid),
                                  widget.state)
            term = "“{}”".format(term)
            label.setText(term)
        widget.tooltips.append((button, tooltip.format(" " + term)))
        if entry.eid in seen:
            button.setEnabled(False)
            if label is not None:
                label.setEnabled(False)
        else:
            if all(not radio.isChecked() for radio in buttons):
                button.setChecked(True)
            seen.add(entry.eid)


def createTermsComboBox(state, eids, *, ignore=None, maximum=None):
    if ignore is None:
        ignore = set()
    combobox = Widgets.List.HtmlComboBox(state)
    eids = [eid for eid in eids if eid not in ignore]
    if maximum is not None:
        eids = eids[:maximum]
    for eid in eids:
        term = elidePatchHtml(state.model.termPath(eid), state)
        combobox.addItem(term, eid)
    return combobox
