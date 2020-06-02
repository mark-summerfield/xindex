#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

from PySide.QtCore import QCoreApplication

QCoreApplication.setApplicationVersion("0.8.0")
import Lib
import Output
import Xix
import Xix.Util
import tests.Util
from Const import LanguageKind

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    "../tests/data"))


def reportProgress(message):
    pass


class TestImport(unittest.TestCase):

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
            infile = os.path.join(PATH, "TestIxml.ixml")
            outfile = "/tmp/TestIxml.xix"
            self.files.append(outfile)
            Lib.remove_file(outfile)
            model.importIndex(infile, outfile, *self.args)
# FIXME verify, e.g., save as .ixml and then compare allowing for the
# fact that we don't do a perfect round-trip
        finally:
            if model is not None:
                model.close()


    def test_02_ximl(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(os.path.join(PATH, "TestIndex-Indented.xix"),
                       *self.args)

            # Output an .xix index as .ximl and .html
            config = model.configs()
            ximl1 = config.Filename = "/tmp/TestXiml1.ximl"
            Lib.remove_file(ximl1)
            self.files.append(ximl1)
            Output.outputEntries(model, config, "", reportProgress)
            html1 = config.Filename = "/tmp/TestXiml1.html"
            Lib.remove_file(html1)
            self.files.append(html1)
            Output.outputEntries(model, config, "", reportProgress)

            # Import
            outfile = "/tmp/TestXiml2.xix"
            Lib.remove_file(outfile)
            model.importIndex(ximl1, outfile, *self.args)
            self.files.append(outfile)

            # Output the imported .xix index as .ximl and .html
            ximl2 = config.Filename = "/tmp/TestXiml2.ximl"
            Lib.remove_file(ximl2)
            self.files.append(ximl2)
            Output.outputEntries(model, config, "", reportProgress)
            html2 = config.Filename = "/tmp/TestXiml2.html"
            Lib.remove_file(html2)
            self.files.append(html2)
            Output.outputEntries(model, config, "", reportProgress)

            tests.Util.compare_files(self, ximl1, ximl2)
            tests.Util.compare_files(self, html1, html2)

        finally:
            if model is not None:
                model.close()


if __name__ == "__main__":
    unittest.main()
