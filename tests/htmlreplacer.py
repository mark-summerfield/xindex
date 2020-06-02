#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import HtmlReplacer


class TestMarkup(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None


    def test_01_roundtrip_literal(self):
        replacer = HtmlReplacer.Replacer(literal="year", replacement="2015")
        for i, line in enumerate(LINES):
            with self.subTest(i=i):
                replacer.setHtml(line)
                text = replacer.html
                self.assertEqual(text, line)


    def test_02_roundtrip_pattern(self):
        replacer = HtmlReplacer.Replacer(pattern=r"\byear\b",
                                         replacement="2016")
        for i, line in enumerate(LINES):
            with self.subTest(i=i):
                replacer.setHtml(line)
                text = replacer.html
                self.assertEqual(text, line)


    def test_03_replace_literal(self):
        replacer = HtmlReplacer.Replacer(literal="year", replacement="2015")
        for i, line in enumerate(LINES):
            with self.subTest(i=i):
                replacer.setHtml(line)
                text = paraMatch = None
                while True:
                    paraMatch = replacer.search()
                    if paraMatch is None:
                        break
                    if not replacer.replace():
                        break # No (more) found
                text = replacer.html
                expected = EXPECTED_LITERAL[i]
                self.assertEqual(text, expected)


    def test_04_replace_pattern(self):
        replacer = HtmlReplacer.Replacer(pattern=r"\byear\b",
                                         replacement="2016")
        for i, line in enumerate(LINES):
            with self.subTest(i=i):
                replacer.setHtml(line)
                paraMatch = None
                while True:
                    paraMatch = replacer.search()
                    if paraMatch is None:
                        break
                    if not replacer.replace():
                        break # No (more) found
                text = replacer.html
                expected = EXPECTED_REGEX[i]
                self.assertEqual(text, expected)


    def test_05_replace_and_skip(self):
        replacer = HtmlReplacer.Replacer(literal="year", replacement="2015")
        line = """<i>$5000 reward this</i> <span style="font-family: \
'arial'; font-size: 9pt;">year</span> and next <b>year</b> and every year"""
        replacer.setHtml(line)
        # Round trip
        self.assertEqual(line, replacer.html)
        # Replace all
        replacer.setHtml(line)
        paraMatch = None
        while True:
            paraMatch = replacer.search()
            if paraMatch is None:
                break
            if not replacer.replace():
                break # No (more) found
        self.assertEqual(line.replace("year", "2015"), replacer.html)
        # replace skip replace
        RSR = """<i>$5000 reward this</i> <span style="font-family: \
'arial'; font-size: 9pt;">2015</span> and next <b>year</b> and every 2015"""
        replacer.setHtml(line)
        paraMatch = replacer.search()
        self.assertIsNotNone(paraMatch)
        replacer.replace()
        paraMatch = replacer.search()
        self.assertIsNotNone(paraMatch)
        replacer.skip()
        paraMatch = replacer.search()
        self.assertIsNotNone(paraMatch)
        replacer.replace()
        paraMatch = replacer.search()
        self.assertIsNone(paraMatch)
        self.assertEqual(replacer.html, RSR)
        # skip replace skip
        SRS = """<i>$5000 reward this</i> <span style="font-family: \
'arial'; font-size: 9pt;">year</span> and next <b>2015</b> and every year"""
        replacer.setHtml(line)
        paraMatch = replacer.search()
        self.assertIsNotNone(paraMatch)
        replacer.skip()
        paraMatch = replacer.search()
        self.assertIsNotNone(paraMatch)
        replacer.replace()
        paraMatch = replacer.search()
        self.assertIsNotNone(paraMatch)
        replacer.skip()
        paraMatch = replacer.search()
        self.assertIsNone(paraMatch)
        self.assertEqual(replacer.html, SRS)


    def test_06_search_all(self):
        replacer = HtmlReplacer.Replacer(literal="year", replacement="2015")
        line = """<i>$5000 reward this</i> <span style="font-family: \
'arial'; font-size: 9pt;">year</span> and next <b>year</b> and every year"""
        replacer.setHtml(line)
        # Round trip
        self.assertEqual(line, replacer.html)
        # Search all
        replacer.setHtml(line)
        paraMatch = None
        count = 0
        while True:
            paraMatch = replacer.search()
            if paraMatch is None:
                break
            count += 1
        self.assertEqual(count, 3)


    def test_07_search_all(self):
        replacer = HtmlReplacer.Replacer(literal="pin", replacement="%")
        line = "A pin in the map of India five pin is the pinnacle pint"
        replacer.setHtml(line)
        # Round trip
        self.assertEqual(line, replacer.html)
        # Search all
        replacer.setHtml(line)
        paraMatch = None
        count = 0
        while True:
            paraMatch = replacer.search()
            if paraMatch is None:
                break
            count += 1
        self.assertEqual(count, 4)


    def test_08_replace_all(self):
        replacer = HtmlReplacer.Replacer(literal="pin", replacement="%")
        line = "A pin in the map of India five pin is the pinnacle pint"
        replacer.setHtml(line)
        # Round trip
        self.assertEqual(line, replacer.html)
        # Search all
        replacer.setHtml(line)
        paraMatch = None
        count = 0
        while True:
            paraMatch = replacer.search()
            if paraMatch is None:
                break
            replacer.replace()
            count += 1
        self.assertEqual(replacer.html,
                         "A % in the map of India five % is the %nacle %t")
        self.assertEqual(count, 4)


    def test_09_ww(self):
        replacer = HtmlReplacer.Replacer(literal="pin", replacement="%",
                                         wholewords=True)
        line = "A pin in the map of India five pin is the pinnacle pint"
        replacer.setHtml(line)
        # Round trip
        self.assertEqual(line, replacer.html)
        # Search all
        replacer.setHtml(line)
        paraMatch = None
        count = 0
        while True:
            paraMatch = replacer.search()
            if paraMatch is None:
                break
            replacer.replace()
            count += 1
        self.assertEqual(
            replacer.html,
            "A % in the map of India five % is the pinnacle pint")
        self.assertEqual(count, 2)


    def test_10_replace_literal_special(self):
        for i, (literal, replacement, original, expected) in enumerate((
                ("&", "and", "This &amp; that", "This and that"),
                ("&-", "", "Pack&amp;-aged", "Packaged"),
                ("and", "&", "This and that", "This &amp; that"),
                ("<", "less than", "0 &lt; 1", "0 less than 1"),
                ("<=", ">=", "0 &lt;= 1", "0 &gt;= 1"),
                )):
            with self.subTest(i=i):
                replacer = HtmlReplacer.Replacer(literal=literal,
                                                 replacement=replacement)
                replacer.setHtml(original)
                text = paraMatch = None
                while True:
                    paraMatch = replacer.search()
                    if paraMatch is None:
                        break
                    if not replacer.replace():
                        break # No (more) found
                text = replacer.html
                self.assertEqual(text, expected)



LINES = (
    "year round",
    "all year",
    "all the <i>year</i> round",
    "$10 a day",
    "$100 a <b>year</b>",
    """<i>$5000 reward this</i> <span style="font-family: 'arial'; \
font-size: 9pt;">year</span> and next <b>year</b> and every year""",
    """<i>And again</i> <span style="font-family: 'arial'; \
font-size: 9pt;">yearly</span> and next <b>year</b> and allyear""",
    "<i>XVII</i><i><sup>me</sup></i><i> siècle</i>",
    "<i>M. Flip ignorait sa mort year</i>",
    "SO<sub>4</sub><sup>-2</sup>",
    "SS. Pietro e Paolo year",
    "ZnSO<sub>4</sub>",
    "zoos",
    """adduces <span style="font-family: 'arial'; font-size: \
9pt;">year methanol’s</span>""",
    """<span style="font-family: 'andale mono'; font-size: \
9pt;">crossbars year</span> rickshaw <b>czechoslovakian</b> alderwoman \
mope""",
    )

EXPECTED_LITERAL = (
    "2015 round",
    "all 2015",
    "all the <i>2015</i> round",
    "$10 a day",
    "$100 a <b>2015</b>",
    """<i>$5000 reward this</i> <span style="font-family: 'arial'; \
font-size: 9pt;">2015</span> and next <b>2015</b> and every 2015""",
    """<i>And again</i> <span style="font-family: 'arial'; \
font-size: 9pt;">2015ly</span> and next <b>2015</b> and all2015""",
    "<i>XVII</i><i><sup>me</sup></i><i> siècle</i>",
    "<i>M. Flip ignorait sa mort 2015</i>",
    "SO<sub>4</sub><sup>-2</sup>",
    "SS. Pietro e Paolo 2015",
    "ZnSO<sub>4</sub>",
    "zoos",
    """adduces <span style="font-family: 'arial'; font-size: \
9pt;">2015 methanol’s</span>""",
    """<span style="font-family: 'andale mono'; font-size: \
9pt;">crossbars 2015</span> rickshaw <b>czechoslovakian</b> alderwoman \
mope""",
    )

EXPECTED_REGEX = (
    "2016 round",
    "all 2016",
    "all the <i>2016</i> round",
    "$10 a day",
    "$100 a <b>2016</b>",
    """<i>$5000 reward this</i> <span style="font-family: 'arial'; \
font-size: 9pt;">2016</span> and next <b>2016</b> and every 2016""",
    """<i>And again</i> <span style="font-family: 'arial'; \
font-size: 9pt;">yearly</span> and next <b>2016</b> and allyear""",
    "<i>XVII</i><i><sup>me</sup></i><i> siècle</i>",
    "<i>M. Flip ignorait sa mort 2016</i>",
    "SO<sub>4</sub><sup>-2</sup>",
    "SS. Pietro e Paolo 2016",
    "ZnSO<sub>4</sub>",
    "zoos",
    """adduces <span style="font-family: 'arial'; font-size: \
9pt;">2016 methanol’s</span>""",
    """<span style="font-family: 'andale mono'; font-size: \
9pt;">crossbars 2016</span> rickshaw <b>czechoslovakian</b> alderwoman \
mope""",
    )


if __name__ == "__main__":
    unittest.main()
