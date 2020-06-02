#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import apsw

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


class TestIndentedOutput(unittest.TestCase):

    def setUp(self):
        # self.maxDiff = None
        self.username = "Tester"
        self.args = (LanguageKind.AMERICAN, "wordByWordCMS16",
                     "pageRangeCMS16")
        self.files = []


    def tearDown(self):
        for filename in self.files:
            Lib.remove_file(filename)


    def test_01_txt_after(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-Indented.xix")
            model.open(infile, *self.args)

            actualfile = "/tmp/TestIndex-Indented_SeeAlsoAfter.txt"
            self.files.append(actualfile)
            expectedfile = ("tests/expected/"
                            "TestIndex-Indented_SeeAlsoAfter.txt")
            config = model.configs()
            config.Filename = actualfile
            config.Indent = IndentKind.FOUR_SPACES
            config.SeeAlsoPosition = SeeAlsoPositionKind.AFTER_PAGES
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_02_txt_first(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-Indented.xix")
            model.open(infile, *self.args)

            actualfile = "/tmp/TestIndex-Indented_SeeAlsoFirst.txt"
            self.files.append(actualfile)
            expectedfile = ("tests/expected/"
                            "TestIndex-Indented_SeeAlsoFirst.txt")
            config = model.configs()
            config.Filename = actualfile
            config.Indent = IndentKind.FOUR_SPACES
            config.SeeAlsoPosition = SeeAlsoPositionKind.FIRST_SUBENTRY
            config.SeeAlsoPrefix = ""
            config.SeeAlsoSuffix = ""
            config.SubSee = "<i>See</i> "
            config.SubSeePrefix = ". "
            config.SubSeeSuffix = ""
            config.SubSeeAlso = "<i>See also</i> "
            config.SubSeeAlsoPrefix = ""
            config.SubSeeAlsoSuffix = ""
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_03_txt_last(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-Indented.xix")
            model.open(infile, *self.args)

            actualfile = "/tmp/TestIndex-Indented_SeeAlsoLast.txt"
            self.files.append(actualfile)
            expectedfile = ("tests/expected/"
                            "TestIndex-Indented_SeeAlsoLast.txt")
            config = model.configs()
            config.Filename = actualfile
            config.Indent = IndentKind.FOUR_SPACES
            config.SeeAlsoPosition = SeeAlsoPositionKind.LAST_SUBENTRY
            config.SeeAlsoPrefix = ""
            config.SeeAlsoSuffix = ""
            config.SubSee = "<i>See</i> "
            config.SubSeePrefix = ". "
            config.SubSeeSuffix = ""
            config.SubSeeAlso = "<i>See also</i> "
            config.SubSeeAlsoPrefix = ""
            config.SubSeeAlsoSuffix = ""
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_04_html_after(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-Indented.xix")
            model.open(infile, *self.args)

            actualfile = "/tmp/TestIndex-Indented_SeeAlsoAfter.html"
            self.files.append(actualfile)
            expectedfile = ("tests/expected/"
                            "TestIndex-Indented_SeeAlsoAfter.html")
            config = model.configs()
            config.Filename = actualfile
            config.SeeAlsoPosition = SeeAlsoPositionKind.AFTER_PAGES
            config.SectionPreLines = 0
            config.SectionPostLines = 0
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_05_html_first(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-Indented.xix")
            model.open(infile, *self.args)

            actualfile = "/tmp/TestIndex-Indented_SeeAlsoFirst.html"
            self.files.append(actualfile)
            expectedfile = ("tests/expected/"
                            "TestIndex-Indented_SeeAlsoFirst.html")
            config = model.configs()
            config.Filename = actualfile
            config.Indent = IndentKind.FOUR_SPACES
            config.SectionPreLines = 0
            config.SectionPostLines = 0
            config.SeeAlsoPosition = SeeAlsoPositionKind.FIRST_SUBENTRY
            config.SeeAlsoPrefix = ""
            config.SeeAlsoSuffix = ""
            config.SubSee = "<i>See</i> "
            config.SubSeePrefix = " ("
            config.SubSeeSuffix = ")"
            config.SubSeeAlso = "<i>see also</i> "
            config.SubSeeAlsoPrefix = " ("
            config.SubSeeAlsoSuffix = ")"
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_06_html_last(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-Indented.xix")
            model.open(infile, *self.args)

            actualfile = "/tmp/TestIndex-Indented_SeeAlsoLast.html"
            self.files.append(actualfile)
            expectedfile = ("tests/expected/"
                            "TestIndex-Indented_SeeAlsoLast.html")
            config = model.configs()
            config.SectionPreLines = 0
            config.SectionPostLines = 0
            config.Filename = actualfile
            config.Indent = IndentKind.FOUR_SPACES
            config.SeeAlsoPosition = SeeAlsoPositionKind.LAST_SUBENTRY
            config.SeeAlsoPrefix = ""
            config.SeeAlsoSuffix = ""
            config.SubSee = "<i>See</i> "
            config.SubSeePrefix = " ("
            config.SubSeeSuffix = ")"
            config.SubSeeAlso = "<i>see also</i> "
            config.SubSeeAlsoPrefix = " ("
            config.SubSeeAlsoSuffix = ")"
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_07_rtf_after(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-Indented.xix")
            model.open(infile, *self.args)

            actualfile = "/tmp/TestIndex-Indented_SeeAlsoAfter.rtf"
            self.files.append(actualfile)
            expectedfile = ("tests/expected/"
                            "TestIndex-Indented_SeeAlsoAfter.rtf")
            config = model.configs()
            config.Filename = actualfile
            config.SeeAlsoPosition = SeeAlsoPositionKind.AFTER_PAGES
            config.SeeAlsoPrefix = ". "
            config.SeeAlsoSuffix = ""
            config.SubSee = "<i>see</i> "
            config.SubSeePrefix = " ("
            config.SubSeeSuffix = ")"
            config.SubSeeAlso = "<i>see also</i> "
            config.SubSeeAlsoPrefix = " ("
            config.SubSeeAlsoSuffix = ")"
            config.SectionSpecialTitle = """<span style="font-size: \
11pt; font-family: 'Arial';">Symbols &amp; Numbers</span>"""
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_08_rtf_first(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-Indented.xix")
            model.open(infile, *self.args)

            actualfile = "/tmp/TestIndex-Indented_SeeAlsoFirst.rtf"
            self.files.append(actualfile)
            expectedfile = ("tests/expected/"
                            "TestIndex-Indented_SeeAlsoFirst.rtf")
            config = model.configs()
            config.Filename = actualfile
            config.Indent = IndentKind.FOUR_SPACES
            config.SeeAlsoPosition = SeeAlsoPositionKind.FIRST_SUBENTRY
            config.SeeAlsoPrefix = ""
            config.SeeAlsoSuffix = ""
            config.SubSee = "<i>see</i> "
            config.SubSeePrefix = " ("
            config.SubSeeSuffix = ")"
            config.SubSeeAlso = "<i>see also</i> "
            config.SubSeeAlsoPrefix = " ("
            config.SubSeeAlsoSuffix = ")"
            config.SectionSpecialTitle = """<span style="font-size: \
11pt; font-family: 'Arial';">Symbols &amp; Numbers</span>"""
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_09_rtf_last(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-Indented.xix")
            model.open(infile, *self.args)

            actualfile = "/tmp/TestIndex-Indented_SeeAlsoLast.rtf"
            self.files.append(actualfile)
            expectedfile = ("tests/expected/"
                            "TestIndex-Indented_SeeAlsoLast.rtf")
            config = model.configs()
            config.Filename = actualfile
            config.Indent = IndentKind.FOUR_SPACES
            config.SeeAlsoPosition = SeeAlsoPositionKind.LAST_SUBENTRY
            config.SeeAlsoPrefix = ""
            config.SeeAlsoSuffix = ""
            config.SubSee = "<i>see</i> "
            config.SubSeePrefix = " ("
            config.SubSeeSuffix = ")"
            config.SubSeeAlso = "<i>see also</i> "
            config.SubSeeAlsoPrefix = " ("
            config.SubSeeAlsoSuffix = ")"
            config.SectionSpecialTitle = """<span style="font-size: \
11pt; font-family: 'Arial';">Symbols &amp; Numbers</span>"""
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_10_docx_after(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-Indented.xix")
            model.open(infile, *self.args)

            actualfile = "/tmp/TestIndex-Indented_SeeAlsoAfter.docx"
            self.files.append(actualfile)
            expectedfile = ("tests/expected/"
                            "TestIndex-Indented_SeeAlsoAfter.docx")
            config = model.configs()
            config.Filename = actualfile
            config.SeeAlsoPosition = SeeAlsoPositionKind.AFTER_PAGES
            config.SeeAlsoPrefix = ". "
            config.SeeAlsoSuffix = ""
            config.SubSee = "<i>see</i> "
            config.SubSeePrefix = " ("
            config.SubSeeSuffix = ")"
            config.SubSeeAlso = "<i>see also</i> "
            config.SubSeeAlsoPrefix = " ("
            config.SubSeeAlsoSuffix = ")"
            config.SectionSpecialTitle = """<span style="font-size: \
11pt; font-family: 'Arial';">Symbols &amp; Numbers</span>"""
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_11_docx_first(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-Indented.xix")
            model.open(infile, *self.args)

            actualfile = "/tmp/TestIndex-Indented_SeeAlsoFirst.docx"
            self.files.append(actualfile)
            expectedfile = ("tests/expected/"
                            "TestIndex-Indented_SeeAlsoFirst.docx")
            config = model.configs()
            config.Filename = actualfile
            config.Indent = IndentKind.FOUR_SPACES
            config.SeeAlsoPosition = SeeAlsoPositionKind.FIRST_SUBENTRY
            config.SeeAlsoPrefix = ""
            config.SeeAlsoSuffix = ""
            config.SubSee = "<i>see</i> "
            config.SubSeePrefix = " ("
            config.SubSeeSuffix = ")"
            config.SubSeeAlso = "<i>see also</i> "
            config.SubSeeAlsoPrefix = " ("
            config.SubSeeAlsoSuffix = ")"
            config.SectionSpecialTitle = """<span style="font-size: \
11pt; font-family: 'Arial';">Symbols &amp; Numbers</span>"""
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_12_docx_last(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-Indented.xix")
            model.open(infile, *self.args)

            actualfile = "/tmp/TestIndex-Indented_SeeAlsoLast.docx"
            self.files.append(actualfile)
            expectedfile = ("tests/expected/"
                            "TestIndex-Indented_SeeAlsoLast.docx")
            config = model.configs()
            config.Filename = actualfile
            config.Indent = IndentKind.FOUR_SPACES
            config.SeeAlsoPosition = SeeAlsoPositionKind.LAST_SUBENTRY
            config.SeeAlsoPrefix = ""
            config.SeeAlsoSuffix = ""
            config.SubSee = "<i>see</i> "
            config.SubSeePrefix = " ("
            config.SubSeeSuffix = ")"
            config.SubSeeAlso = "<i>see also</i> "
            config.SubSeeAlsoPrefix = " ("
            config.SubSeeAlsoSuffix = ")"
            config.SectionSpecialTitle = """<span style="font-size: \
11pt; font-family: 'Arial';">Symbols &amp; Numbers</span>"""
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()

    def test_13_rtf(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "RussianNationalism-Amanda.xix")
            model.open(infile, *self.args)

            actualfile = "/tmp/RussianNationalism-Amanda.rtf"
            self.files.append(actualfile)
            expectedfile = ("tests/expected/RussianNationalism-Amanda.rtf")
            config = model.configs()
            config.Filename = actualfile
            config.Indent = IndentKind.FOUR_SPACES
            config.SeeAlsoPosition = SeeAlsoPositionKind.LAST_SUBENTRY
            config.SeeAlsoPrefix = ""
            config.SeeAlsoSuffix = ""
            config.SubSee = "<i>see</i> "
            config.SubSeePrefix = " ("
            config.SubSeeSuffix = ")"
            config.SubSeeAlso = "<i>see also</i> "
            config.SubSeeAlsoPrefix = " ("
            config.SubSeeAlsoSuffix = ")"
            config.SectionSpecialTitle = """<span style="font-size: \
11pt; font-family: 'Arial';">Symbols &amp; Numbers</span>"""
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def dump(self, db):
        print("dump")
        shell = apsw.Shell(stdout=sys.stdout, db=db)
        shell.process_command(".dump entries xrefs generic_xrefs")


if __name__ == "__main__":
    unittest.main()
