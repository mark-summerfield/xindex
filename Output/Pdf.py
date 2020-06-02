#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import re

from PySide.QtCore import QSettings
from PySide.QtGui import QApplication, QPrinter, QTextDocument

from Config import Gopt
from Const import PaperSizeKind


INDENT_RX = re.compile(r"""<p\s+class="hi(?P<level>\d+)">""")


def output(config, document):
    p = ("""<p style="font-family: '{family}'; font-size: {size}pt;">"""
         .format(family=config.StdFont, size=config.StdFontSize))
    pad = lambda match: p + (int(match.group("level")) * 4 * "&nbsp;")
    doc = QTextDocument()
    doc.setHtml(INDENT_RX.sub(pad, document))
    printer = getattr(config, "Printer", None)
    if printer is None:
        printer = QPrinter(QPrinter.HighResolution)
        printer.setCreator("{} {}".format(
            QApplication.applicationName(),
            QApplication.applicationVersion()))
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOrientation(QPrinter.Portrait)
        settings = QSettings()
        size = PaperSizeKind(int(settings.value(Gopt.Key.PaperSize,
                                                Gopt.Default.PaperSize)))
        printer.setPaperSize(QPrinter.A4 if size is PaperSizeKind.A4 else
                             QPrinter.Letter)
        printer.setOutputFileName(config.Filename)
    doc.print_(printer)
