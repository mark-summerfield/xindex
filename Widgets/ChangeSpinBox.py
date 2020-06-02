#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sys

from PySide.QtCore import Qt
from PySide.QtGui import QApplication, QSpinBox


class SpinBox(QSpinBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignRight)


    def valueFromText(self, value):
        try:
            return int(value)
        except ValueError:
            return 0


    def textFromValue(self, value):
        return str(value) if value else "(no change)"


if __name__ == "__main__":
    def report(value):
        print(type(value), value)

    app = QApplication(sys.argv)
    spinbox = SpinBox()
    spinbox.setRange(-10000, 10000)
    spinbox.show()
    spinbox.setWindowTitle("Change")
    spinbox.valueChanged.connect(report)
    app.exec_()
