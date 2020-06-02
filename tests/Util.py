#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import difflib
import re
import zipfile


XML_COMMENT_RX = re.compile(r"<!--.+?-->")
XIML_RX = re.compile(
    r'(?:'
    r'<config key="(?:Created|Updated|UUID)">.*?</config>|'
    r'(?:time|created|updated)="\d\d\d\d-\d\d-\d\d[ T]\d\d:\d\d:\d\d"|'
    r'version="\d+(\.\d+\.+d+)?"|'
    r'<ignore_firsts word="[^"]+"/>'
    r')')
XIX_VERSION = re.compile(r"XindeX \d+\.\d+\.\d+")


def compare_files(self, actualfile, expectedfile):
    # self is a unittest.TestCase
    if actualfile.endswith(".docx"):
        with zipfile.ZipFile(actualfile) as zfile:
            with zfile.open("word/document.xml") as file:
                actual = file.read().decode("UTF-8", "surrogateescape")
        with zipfile.ZipFile(expectedfile) as zfile:
            with zfile.open("word/document.xml") as file:
                expected = file.read().decode("UTF-8", "surrogateescape")
    else:
        encoding = "ascii" if actualfile.endswith(".rtf") else "utf-8-sig"
        with open(actualfile, "rt", encoding=encoding) as file:
            actual = file.readlines()
            _ignore_version(actual)
        encoding = "ascii" if expectedfile.endswith(".rtf") else "utf-8-sig"
        with open(expectedfile, "rt", encoding=encoding) as file:
            expected = file.readlines()
            _ignore_version(expected)
        if actualfile.endswith(".html"):
            actual = XML_COMMENT_RX.sub("", "\n".join(actual)).splitlines()
            expected = XML_COMMENT_RX.sub("",
                                          "\n".join(expected)).splitlines()
        elif actualfile.endswith((".ximl", ".ixml")):
            actual = XIML_RX.sub("", "\n".join(actual)).splitlines()
            expected = XIML_RX.sub("", "\n".join(expected)).splitlines()
    same = actual == expected
    if not same:
        diff = difflib.unified_diff(actual, expected, n=0)
        print(actualfile, "!=", expectedfile)
        print("".join(diff), end="")
    self.assertTrue(same)


def _ignore_version(lines):
    for i in range(len(lines)):
        line = lines[i]
        match = XIX_VERSION.search(line)
        if match is not None:
            lines[i] = XIX_VERSION.sub("XindeX", line)
