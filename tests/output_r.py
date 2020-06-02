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
from Const import LanguageKind, StyleKind

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    "../tests/data"))


def reportProgress(message):
    pass


class TestRunInOutput(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.username = "Tester"
        self.args = (LanguageKind.AMERICAN, "wordByWordCMS16",
                     "pageRangeCMS16")
        self.files = []


    def tearDown(self):
        for filename in self.files:
            Lib.remove_file(filename)


    def test_01_txt_main(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunInMain.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunInMain.txt"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunInMain.txt"
            config = model.configs()
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_MAIN
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_02_txt_1st(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunIn1st.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunIn1st.txt"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunIn1st.txt"
            config = model.configs()
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_SUBENTRY1
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_03_txt_2nd(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunIn2nd.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunIn2nd.txt"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunIn2nd.txt"
            config = model.configs()
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_SUBENTRY2
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_04_txt_3rd(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunIn3rd.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunIn3rd.txt"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunIn3rd.txt"
            config = model.configs()
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_SUBENTRY3
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_05_html_main(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunInMain.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunInMain.html"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunInMain.html"
            config = model.configs()
            config.SectionPreLines = 0
            config.SectionPostLines = 0
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_MAIN
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_06_html_1st(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunIn1st.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunIn1st.html"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunIn1st.html"
            config = model.configs()
            config.SectionPreLines = 0
            config.SectionPostLines = 0
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_SUBENTRY1
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_07_html_2nd(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunIn2nd.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunIn2nd.html"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunIn2nd.html"
            config = model.configs()
            config.SectionPreLines = 0
            config.SectionPostLines = 0
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_SUBENTRY2
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_08_html_3rd(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunIn3rd.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunIn3rd.html"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunIn3rd.html"
            config = model.configs()
            config.SectionPreLines = 0
            config.SectionPostLines = 0
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_SUBENTRY3
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_09_rtf_main(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunInMain.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunInMain.rtf"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunInMain.rtf"
            config = model.configs()
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_MAIN
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_10_rtf_1st(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunIn1st.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunIn1st.rtf"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunIn1st.rtf"
            config = model.configs()
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_SUBENTRY1
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_11_rtf_2nd(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunIn2nd.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunIn2nd.rtf"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunIn2nd.rtf"
            config = model.configs()
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_SUBENTRY2
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_12_rtf_3rd(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunIn3rd.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunIn3rd.rtf"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunIn3rd.rtf"
            config = model.configs()
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_SUBENTRY3
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_13_docx_main(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunInMain.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunInMain.docx"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunInMain.docx"
            config = model.configs()
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_MAIN
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_14_docx_1st(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunIn1st.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunIn1st.docx"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunIn1st.docx"
            config = model.configs()
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_SUBENTRY1
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_15_docx_2nd(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunIn2nd.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunIn2nd.docx"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunIn2nd.docx"
            config = model.configs()
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_SUBENTRY2
            Output.outputEntries(model, config, "", reportProgress)
            tests.Util.compare_files(self, actualfile, expectedfile)
        finally:
            if model is not None:
                model.close()


    def test_16_docx_3rd(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            infile = os.path.join(PATH, "TestIndex-RunIn3rd.xix")
            model.open(infile, *self.args)
            actualfile = "/tmp/TestIndex-RunIn3rd.docx"
            self.files.append(actualfile)
            expectedfile = "tests/expected/TestIndex-RunIn3rd.docx"
            config = model.configs()
            config.Filename = actualfile
            config.Style = StyleKind.RUN_IN_FROM_SUBENTRY3
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
