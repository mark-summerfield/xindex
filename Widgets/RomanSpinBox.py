#!/usr/bin/env python3
# Copyright © 2008-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sys

import roman

from PySide.QtCore import QRegExp, Qt
from PySide.QtGui import QApplication, QRegExpValidator, QSpinBox


class Error(Exception):
    pass


# Regex adapted from Mark Pilgrim's "Dive Into Python" book
class SpinBox(QSpinBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        regex = QRegExp(r"^M?M?M?(?:CM|CD|D?C?C?C?)"
                        r"(?:XC|XL|L?X?X?X?)(?:IX|IV|V?I?I?I?)$")
        regex.setCaseSensitivity(Qt.CaseInsensitive)
        self.validator = QRegExpValidator(regex, self)
        self.setRange(1, 3999)
        self.lineEdit().textEdited.connect(self.fixCase)


    def fixCase(self, text):
        self.lineEdit().setText(text.upper())


    def validate(self, text, pos):
        return self.validator.validate(text, pos)


    def valueFromText(self, text):
        try:
            return roman.fromRoman(text.upper())
        except roman.RomanError:
            return 1


    def textFromValue(self, value):
        return roman.toRoman(value)


if __name__ == "__main__":
    def report(value):
        print("{0:4d} {1}".format(value, roman.toRoman(value)))

    app = QApplication(sys.argv)
    spinbox = SpinBox()
    spinbox.show()
    spinbox.setWindowTitle("Roman")
    spinbox.valueChanged.connect(report)
    app.exec_()
