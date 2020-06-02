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
import Saf
import SortAs
import Xix
import Xix.Util
import tests.Util
from Const import EXPORT_EXTENSIONS, LanguageKind


def reportProgress(message):
    pass


class TestPagesAtOutput(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.username = "Tester"
        self.args = (LanguageKind.AMERICAN, "wordByWordCMS16",
                     "pageRangeCMS16")
        self.files = []


    def tearDown(self):
        for filename in self.files:
            Lib.remove_file(filename)


    def test_01(self):
        data = (("One", "1, 2, <b>3</b>, <i>15\u201320</i>"),
                ("Two", "17@10.5<i>tbl</i>, <i>15@11.6\u201320</i>"))
        basename = "TestPagesAtOutput"
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            added = []
            for term, pages in data:
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, pages=pages)
                added.append(term)
            self.assertEqual(len(data), len(model))
            config = model.configs()
            i = 0
            for extension in EXPORT_EXTENSIONS.keys():
                with self.subTest(i=i):
                    if extension not in {".*", ".ucp", ".pdf"}:
                        i += 1
                        filename = basename + extension
                        actualfile = "/tmp/" + filename
                        expectedfile = os.path.join("tests/expected/",
                                                    filename)
                        config.Filename = actualfile
                        self.files.append(config.Filename)
                        Output.outputEntries(model, config, "",
                                             reportProgress)
                        tests.Util.compare_files(self, actualfile,
                                                 expectedfile)
        finally:
            if model is not None:
                model.close()


if __name__ == "__main__":
    unittest.main()
