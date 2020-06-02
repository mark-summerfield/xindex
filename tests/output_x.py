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
import tests.Util
from Const import IndentKind, LanguageKind, SeeAlsoPositionKind

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    "../tests/data"))


def reportProgress(message):
    pass


class TestOutputXML(unittest.TestCase):

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

            # Import a .ixml file
            infile = os.path.join(PATH, "TestIxml.ixml")
            outfile = "/tmp/TestIxml1.xix"
            Lib.remove_file(outfile)
            self.files.append(outfile)
            model.importIndex(infile, outfile, *self.args)

            config = model.configs()
            config.Indent = IndentKind.FOUR_SPACES
            config.SeeAlsoPosition = SeeAlsoPositionKind.AFTER_PAGES

            # Export imported .ixml as .html (to preserve text styling)
            html1 = config.Filename = "/tmp/TestIxml1.html"
            Lib.remove_file(config.Filename)
            self.files.append(html1)
            Output.outputEntries(model, config, "", reportProgress)

            # Export imported .ixml as .ixml
            infile = config.Filename = "/tmp/TestIxml1.ixml"
            Lib.remove_file(config.Filename)
            self.files.append(infile)
            Output.outputEntries(model, config, "", reportProgress)

            # Import exported .ixml
            outfile = "/tmp/TestIxml2.xix"
            self.files.append(outfile)
            Lib.remove_file(outfile)
            model.importIndex(infile, outfile, *self.args)

            # Re-export imported .ixml as .html (to preserve text styling)
            html2 = config.Filename = "/tmp/TestIxml2.html"
            self.files.append(html2)
            Lib.remove_file(config.Filename)
            Output.outputEntries(model, config, "", reportProgress)

            tests.Util.compare_files(self, html1, html2)
        finally:
            if model is not None:
                model.close()


    def test_02_ximl(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-Indented.xix")
            model.open(infile, *self.args)
            config = model.configs()
            outfile = config.Filename = "/tmp/TestXiml1.ximl"
            Lib.remove_file(outfile)
            self.files.append(outfile)
            Output.outputEntries(model, config, "", reportProgress)
        finally:
            if model is not None:
                model.close()


    def test_03_ximl(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)

            # Import a .ximl file
            infile = os.path.join(PATH, "TestXiml.ximl")
            outfile = "/tmp/TestXiml1.xix"
            Lib.remove_file(outfile)
            self.files.append(outfile)
            model.importIndex(infile, outfile, *self.args)

            config = model.configs()
            config.Indent = IndentKind.FOUR_SPACES
            config.SeeAlsoPosition = SeeAlsoPositionKind.AFTER_PAGES

            # Export imported .ximl as .html (to preserve text styling)
            html1 = config.Filename = "/tmp/TestXiml1.html"
            Lib.remove_file(config.Filename)
            self.files.append(html1)
            Output.outputEntries(model, config, "", reportProgress)

            # Export imported .ximl as .ximl
            infile = config.Filename = "/tmp/TestXiml1.ximl"
            Lib.remove_file(config.Filename)
            self.files.append(infile)
            Output.outputEntries(model, config, "", reportProgress)

            # Import exported .ximl
            outfile = "/tmp/TestXiml2.xix"
            self.files.append(outfile)
            Lib.remove_file(outfile)
            model.importIndex(infile, outfile, *self.args)

            # Re-export imported .ximl as .html (to preserve text styling)
            html2 = config.Filename = "/tmp/TestXiml2.html"
            self.files.append(html2)
            Lib.remove_file(config.Filename)
            Output.outputEntries(model, config, "", reportProgress)

            tests.Util.compare_files(self, html1, html2)
        finally:
            if model is not None:
                model.close()



if __name__ == "__main__":
    unittest.main()
