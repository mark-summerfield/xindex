#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

from PySide.QtCore import QCoreApplication

QCoreApplication.setApplicationVersion("0.8.0")
import Lib
import Xix
import Xix.Util
import Output
import Output.Markup
import tests.Util
from Const import LanguageKind

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    "../tests/data"))


def reportProgress(message):
    pass


class TestMarkup(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.username = "Tester"
        self.args = (LanguageKind.AMERICAN, "wordByWordCMS16",
                     "pageRangeCMS16")
        self.files = []


    def tearDown(self):
        for filename in self.files:
            Lib.remove_file(filename)


    def test_01_ixml(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-Indented.xix")
            model.open(infile, *self.args)
            markups = list(model.markups())
            self.assertListEqual([".ucp"], markups)
            extension = ".app"
            markup = Output.Markup.user_markup()
            markup.escapefunction = "html"
            markup.DocumentStart = "<itml>"
            markup.DocumentEnd = "</itml>"
            markup.SectionStart = "<sp>"
            markup.MainStart = "<itm>"
            markup.MainEnd = "{nl}"
            markup.Sub1Start = "<sit2>"
            markup.Sub1End = "{nl}"
            markup.Sub2Start = "<sit3>"
            markup.Sub2End = "{nl}"
            markup.Sub3Start = "<sit4>"
            markup.Sub3End = "{nl}"
            markup.Sub4Start = "<sit5>"
            markup.Sub4End = "{nl}"
            markup.Sub5Start = "<sit6>"
            markup.Sub5End = "{nl}"
            markup.Sub6Start = "<sit7>"
            markup.Sub6End = "{nl}"
            markup.Sub7Start = "<sit8>"
            markup.Sub7End = "{nl}"
            markup.Sub8Start = "<sit9>"
            markup.Sub8End = "{nl}"
            markup.Sub9Start = "<sit10>"
            markup.Sub9End = "{nl}"
            markup.RangeSeparator = "&ndash;"
            markup.AltFontStart = "<scp>"
            markup.AltFontEnd = "</scp>"
            markup.BoldStart = "<b>"
            markup.BoldEnd = "</b>"
            markup.ItalicStart = "<it>"
            markup.ItalicEnd = "</it>"
            markup.SubscriptStart = "<u.inf>"
            markup.SuperscriptStart = "<u.sup>"
            markup.UnderlineStart = "<e1>"
            markup.UnderlineEnd = "</e1>"
            model.updateMarkup(extension, markup)
            markups = list(model.markups())
            self.assertListEqual([".app", ".ucp"], markups)

            actualfile = "/tmp/TestIndex.app"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex.app"
            config = model.configs()
            config.Filename = actualfile
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.deleteMarkup(".app")
                model.close()



if __name__ == "__main__":
    unittest.main()
