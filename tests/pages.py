#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import Lib
import Pages
import Pages.Parser


def print_pages(pages):
    for page in pages:
        for depth, child in page.iterate():
            print("{}{}".format("→ " * (depth + 1), child))


class TestPages(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None


    def test_parser(self):
        for i, (original, expected) in enumerate(PAGESPAIRS1, 1):
            with self.subTest(i=i):
                original = original.replace("\n", " ")
                expected = expected.replace("\n", " ")
                parser = Pages.Parser.Parser()
                parser.feed(original)
                actual = parser.toHtml(Pages.pageRangeFull)
                if expected != actual:
                    print("\n", "IN : ", original, sep="")
                    print("\n", "EXP: ", expected, sep="")
                    print("\n", "OUT: ", actual, sep="")
                    print()
                    print_pages(parser.pages)
                self.assertEqual(actual, expected)
                actual = Pages.sortedPages(
                    expected, Pages.pageRangeFull)
                self.assertEqual(actual, expected)


    def test_sortedPages_full(self):
        for i, (original, expected) in enumerate(PAGESPAIRS1, 1):
            with self.subTest(i=i):
                original = original.replace("\n", " ")
                expected = expected.replace("\n", " ")
                actual = Pages.sortedPages(
                    original, Pages.pageRangeFull)
                if expected != actual:
                    print("\n", "IN : ", original, sep="")
                    print("\n", "EXP: ", expected, sep="")
                    print("\n", "OUT: ", actual, sep="")
                self.assertEqual(actual, expected)
                actual = Pages.sortedPages(
                    expected, Pages.pageRangeFull)
                self.assertEqual(actual, expected)


    def test_sortedPages_CMS16(self):
        for i, (original, expected) in enumerate(PAGESPAIRS2, 1):
            with self.subTest(i=i):
                original = original.replace("\n", " ")
                expected = expected.replace("\n", " ")
                actual = Pages.sortedPages(
                    original, Pages.pageRangeCMS16)
                if expected != actual:
                    print("\n", "IN : ", original, sep="")
                    print("\n", "EXP: ", expected, sep="")
                    print("\n", "OUT: ", actual, sep="")
                self.assertEqual(actual, expected)
                actual = Pages.sortedPages(
                    expected, Pages.pageRangeCMS16)
                self.assertEqual(actual, expected)


    def test_sortedPages_ISO999(self):
        for i, (original, expected) in enumerate(PAGESPAIRS4, 1):
            with self.subTest(i=i):
                original = original.replace("\n", " ")
                expected = expected.replace("\n", " ")
                actual = Pages.sortedPages(
                    original, Pages.pageRangeISO999)
                if expected != actual:
                    print("\n", "IN : ", original, sep="")
                    print("\n", "EXP: ", expected, sep="")
                    print("\n", "OUT: ", actual, sep="")
                self.assertEqual(actual, expected)
                actual = Pages.sortedPages(
                    expected, Pages.pageRangeISO999)
                self.assertEqual(actual, expected)


    def test_sortedPages_good(self):
        pairs = (("", ""), ("1", "1"), ("2-", "2"), ("-3", "3"),
                 ("<b></b>", ""), ("<i>4</i>", "<i>4</i>"),
                 ("<b>5-</b>", "<b>5</b>"), ("<i>-6</i>", "<i>6</i>"),
                 ("<b>7</b>-", "<b>7</b>"),
                 ("<b></b>", ""), ("--<i>8<i>", "\u2013<i>8</i>"),
                 ("<b>9</b>-", "<b>9</b>"),
                 ("<b>10-</b>", "<b>10</b>"),
                 ("<i>-11</i>", "<i>11</i>"),
                 ("<i>-xid</i>", "<i>xid</i>"),
                 ("text", "text"),
                 ("7, 11, 15X-Ray", "7, 11, 15X–Ray"),
                 )
        for i, (original, expected) in enumerate(pairs):
            with self.subTest(i=i):
                actual = Pages.sortedPages(
                    original, Pages.pageRangeCMS16)
                if expected != actual:
                    print("\n", "IN : ", original, sep="")
                    print("\n", "EXP: ", expected, sep="")
                    print("\n", "OUT: ", actual, sep="")
                self.assertEqual(actual, expected)
                # No round-trip because one-way conversion


    def test_sortedPages_bad(self):
        pairs = (("-<b>1</b>", "<b>1</b>"),
                 ("-<b>2</b>-", "<b>2</b>"),
                 )
        for i, (original, expected) in enumerate(pairs):
            with self.subTest(i=i):
                actual = Pages.sortedPages(original, Pages.pageRangeCMS16)
                if expected != actual:
                    print("\n", "IN : ", original, sep="")
                    print("\n", "EXP: ", expected, sep="")
                    print("\n", "OUT: ", actual, sep="")
                self.assertEqual(actual, expected)


    def test_searchablePages(self):
        for i, (original, expected) in enumerate(PAGESPAIRS3, 1):
            with self.subTest(i=i):
                original = original.replace("\n", " ")
                expected = expected.replace("\n", " ")
                actual = Pages.searchablePages(original)
                if expected != actual:
                    print("\n", "IN : ", original, sep="")
                    print("\n", "EXP: ", expected, sep="")
                    print("\n", "OUT: ", actual, sep="")
                self.assertEqual(actual, expected)
                actual = Pages.searchablePages(
                    ",".join(expected.lower().split()))
                self.assertEqual(actual, expected)


    def test_searchablePages_bad(self):
        pairs = (("-<b>1</b>", "1"),
                 ("-<b>2</b>-", "2"),
                 ("text", "text"),
                 ("", ""),
                 )
        for i, (original, expected) in enumerate(pairs, 1):
            with self.subTest(i=i):
                original = original.replace("\n", " ")
                expected = expected.replace("\n", " ")
                actual = Pages.searchablePages(original)
                if expected != actual:
                    print("\n", "IN : ", original, sep="")
                    print("\n", "EXP: ", expected, sep="")
                    print("\n", "OUT: ", actual, sep="")
                self.assertEqual(actual, expected)
                # No round-trip because one-way conversion


    def test_mergePages(self):
        triples = (("2, 4, 8", "1, 3, 5, 11", "1, 2, 3, 4, 5, 8, 11"),
                   ("100, 110-5", "102, 103-5, 111-12",
                       "100, 102, 103–5, 110–15"),
                   ("", "", ""),
                   ("1, 2, 3, 10, 12, 100", "1, 2, 10, 12, 100, 102",
                       "1, 2, 3, 10, 12, 100, 102"),
                   ("", "501-5", "501–5"),
                   ("91, 98", "", "91, 98"),
                   ("", "", ""),
                   ("277-79", "277-79", "277\u201379"),
                   ("277-79", "277&ndash;79", "277\u201379"),
                   ("277\u201379", "277&ndash;79", "277\u201379"),
                   ("32, 56, 96, 159–64", "9, 30–33, 39, 77, 96, 121, 182",
                    "9, 30–33, 39, 56, 77, 96, 121, 159–64, 182"),
                   )
        for i, (left, right, expected) in enumerate(triples, 1):
            with self.subTest(i=i):
                actual = Pages.mergedPages(
                    left, right, pageRange=Pages.pageRangeCMS16)
                if actual != expected:
                    print("\nACT:", actual)
                    print("EXP:", expected)
                self.assertEqual(actual, expected)
                actual2 = Pages.mergedPages(
                    right, left, pageRange=Pages.pageRangeCMS16)
                if actual != expected:
                    print("ACT:", actual)
                    print("EXP:", expected)
                self.assertEqual(actual, actual2)


    def test_highestPage(self):
        for i, (original, expected, _, _) in enumerate(PAGESDATA, 1):
            with self.subTest(i=i):
                original = original.replace("\n", " ")
                actual = Pages.highestPage(original)
                if expected != actual:
                    print("\n", "IN : ", original, sep="")
                    print("\n", "EXP: ", expected, sep="")
                    print("\n", "OUT: ", actual, sep="")
                self.assertEqual(actual, expected)


    def test_largestPagesRange(self):
        for i, (original, _, expected, _) in enumerate(PAGESDATA, 1):
            with self.subTest(i=i):
                original = original.replace("\n", " ")
                actual = Pages.largestPageRange(original)
                if expected != actual:
                    print("\n", "IN : ", original, sep="")
                    print("\n", "EXP: ", expected, sep="")
                    print("\n", "OUT: ", actual, sep="")
                self.assertEqual(actual, expected)


    def test_pagesCount(self):
        for i, (original, _, _, expected) in enumerate(PAGESDATA, 1):
            with self.subTest(i=i):
                original = original.replace("\n", " ")
                actual = Pages.pagesCount(original)
                if expected != actual:
                    print("\n", "IN:    ", original, sep="")
                    print("\n", "IDEAL: ", Lib.htmlToPlainText(
                        Pages.sortedPages(original, Pages.pageRangeFull)),
                        sep="")
                    print("\n", "EXP:   ", expected, sep="")
                    print("\n", "OUT:   ", actual, sep="")
                self.assertEqual(actual, expected)


PAGESPAIRS1 = (
    ("""492(<i>nn</i> 1, 3), vi, 12(<i>n</i>4), xiv, vii<i>n</i>5, \
xi<i>n</i>6, 52n7, 51<i>n</i>10, 15–16<i>n</i>12, 8<i>n14</i>""",
        """vi, vii<i>n</i>5, xi<i>n</i>6, xiv, 8<i>n14</i>, \
12(<i>n</i> 4), 15–16<i>n</i>12, 51<i>n</i>10, 52n7, \
492(<i>nn</i> 1, 3)"""),
    ("""89, 32, 4, xii, 492, vi, 12, xiv, 49, vi, 89, 18(nn 12, 15)""",
        """vi, xii, xiv, 4, 12, 18(nn 12, 15), 32, 49, 89, 492"""),
    ("""<b>719, 34, 11t</b>, ix, 42, <i>iv, 13f, 88</i>, 39, 4""",
        """<i>iv</i>, ix, 4, <b>11t</b>, <i>13f</i>,
<b>34</b>, 39, 42, <i>88</i>, <b>719</b>"""),
    ("""85, <b>35</b>(nn. 11, 19), 75<sub>2</sub>,\
<i>81<sup>a</sup></i>, 49""",
        """<b>35</b>(nn. 11, 19), 49, 75<sub>2</sub>,
<i>81</i><sup><i>a</i></sup>, 85"""),
    ("101–8, <b>808</b>–33, <i>1103–</i>4, 1206(nn. <b>83</b>, 91)",
        "101–108, <b>808</b>–833, <i>1103</i>–1104, 1206(nn. <b>83</b>, 91)"),
    ("""<i>281f</i>, <i><span style="font-size: 11pt;
font-family: 'times new roman';">240 - 248 </span></i>, 116- 118, xv,
<b>32t</b>, 24""",
        """xv, 24, <b>32t</b>, 116\u2013118, \
<i><span style="font-size: 11pt; font-family: 'times new roman';">240\
</span></i><i>\u2013</i>\
<i><span style="font-size: 11pt; font-family: 'times new roman';">248\
</span></i>, <i>281f</i>"""),
    ("102–9, <b>908</b>–33, 2103–<i>4</i>",
        "102–109, <b>908</b>–933, 2103–<i>2104</i>"),
    ("321–28, 498–532, 1087–89, 1496–500, 11564–615, 12991–3001",
        "321–328, 498–532, 1087–1089, 1496–1500, 11564–11615, 12991–13001"),
    ("""89, 32, 4, xii, 492, vi, 12, <b>xiv-</b>xvii, 49, vi, 89""",
        """vi, xii, <b>xiv</b>\u2013xvii, 4, 12, 32, 49, 89, 492"""),
    ("""<b>719, 34, 11t</b>, ix, 42, <i>iv, 13f, 88</i>, 39, 4""",
        """<i>iv</i>, ix, 4, <b>11t</b>, <i>13f</i>,
<b>34</b>, 39, 42, <i>88</i>, <b>719</b>"""),
    ("""85, <b>35</b>, 75<sub>2</sub>, <i>81<sup>a</sup></i>,
49""",
        """<b>35</b>, 49, 75<sub>2</sub>,
<i>81</i><sup><i>a</i></sup>, 85"""),
    ("""<i>281f</i>, <i><span style="font-size: 11pt;
font-family: 'times new roman';">240 - 248 </span></i>, 116- 118, xv,
<b>32t</b>, 24""",
        """xv, 24, <b>32t</b>, 116\u2013118, \
<i><span style="font-size: 11pt; font-family: 'times new roman';">240\
</span></i><i>\u2013</i>\
<i><span style="font-size: 11pt; font-family: 'times new roman';">248\
</span></i>, <i>281f</i>"""),
    ("""<i>203,</i> 290-293, <i>177-182,</i> <span
style="font-size: 11pt; font-family: 'arial';"><i>105,</i></span>
<i>343 - 350,</i> <i><b>239</b>,</i> 154, <span style="font-size: 11pt;
font-family: 'arial';">100,</span> 110, 63, <b>482</b>""",
        """63, <span style="font-size: 11pt; font-family:
'arial';">100</span>, <i><span style="font-size: 11pt; font-family:
'arial';">105</span></i>, 110, 154, <i>177</i><i>\u2013</i><i>182</i>, \
<i>203</i>, <i><b>239</b></i>, 290\u2013293, \
<i>343</i><i>\u2013</i><i>350</i>, \
<b>482</b>"""),
    ("""420, 51<b>t</b>, <i>91<b>f,</b></i> 47\u2013<i>52,</i> 98,
420, 51<b>t</b>, <i>91<b>f</b>,</i> 47\u2013<i>52</i>, 98,
<b>82-<i>84</i></b>""",
        """47\u2013<i>52</i>, 51<b>t</b>,
<b>82</b><b>\u2013</b><i><b>84</b></i>, <i>91</i><i><b>f</b></i>, 98, \
420"""),
    ("""<b>117</b>, 420, 51<b>t</b>, <i>91<b>f</b></i>,
47-<i>52</i>, <b>62-</b><b><i>64</i></b>, 98, <i>2</i>""",
        """<i>2</i>, 47\u2013<i>52</i>, 51<b>t</b>,
<b>62</b><b>\u2013</b><i><b>64</b></i>, <i>91</i><i><b>f</b></i>, 98, \
<b>117</b>, 420"""),
    ("""7, 12, 78, 81<i>f</i>, 92-96, 203<b>t</b>, 206, 255,
290, 300t, 381, 482, 491, iv, xviii, <b>75c</b>""",
        """iv, xviii, 7, 12, <b>75c</b>, 78, 81<i>f</i>, 92\u201396,
203<b>t</b>, 206, 255, 290, 300t, 381, 482, 491""",),
    ("83, 56-74, 91, Frontispiece@0.1, 21-25 <i>passim</i>, 31",
     "Frontispiece@0.1, 21\u201325 <i>passim</i>, 31, 56\u201374, 83, 91"),
    ("2, 1.13, 1.49, 1.3 <i>illus.</i>, 1.8, 1.98, 1.2",
        "1.2, 1.3 <i>illus.</i>, 1.8, 1.13, 1.49, 1.98, 2"),
    ("2, 1.13, 1.4.12, 1.4.6, 1.4, 1.4.1, 1.8, 1.98, 1.2",
        "1.2, 1.4, 1.4.1, 1.4.6, 1.4.12, 1.8, 1.13, 1.98, 2"),
    ("3-10, <i>71-</i>2, 82-85, 87-<i>8</i>, 96-<b>117</b>, 97-9",
        """3\u201310, <i>71</i>\u201372, 82\u201385, 87\u2013<i>88</i>, \
96\u2013<b>117</b>, 97\u201399""",),
    ("1200-1213, 1300-324, 1400-81, 1500-9",
        "1200\u20131213, 1300\u20131324, 1400\u20131481, 1500\u20131509"),
    ("100-4, 110-15, 120-8, 1100-1113, 1200-7, 1300-34, 1400-1595, \
1500-1581",
        """100\u2013104, 110\u2013115, 120\u2013128, 1100\u20131113, \
1200\u20131207, 1300\u20131334, 1400\u20131595, 1500\u20131581"""),
    ("101-108, 202-15, 304-9, 808-33, 909-11, 1103-4, 1205-16, \
1308-401",
        """101\u2013108, 202\u2013215, 304\u2013309, 808\u2013833, \
909\u2013911, 1103\u20131104, 1205\u20131216, 1308\u20131401"""),
    ("321-28, 418-9, 498-532, 1087-89, 1287-9, 1496-500, 11564-615, \
12991-3001",
        """321\u2013328, 418\u2013419, 498\u2013532, 1087\u20131089, \
1287\u20131289, 1496\u20131500, 11564\u201311615, 12991\u201313001"""),
    ("101-08, 808-33, 909-21, 1103-104, 1202-206",
        "101\u2013108, 808\u2013833, 909\u2013921, 1103\u20131104, \
1202\u20131206"),
    ("101–108, 808–833, 1103–1104", "101–108, 808–833, 1103–1104"),
    ("321–328, 498–532, 1087–1089, 1496–1500, 11564–11615, 12991–13001",
        "321–328, 498–532, 1087–1089, 1496–1500, 11564–11615, 12991–13001"),
    ("89, 106–108n., Frontispiece, 202f, 14-18 passim, 21",
        "Frontispiece, 14\u201318 passim, 21, 89, 106–108n., 202f"),
    # Dissalowed
    # ("vi, xiv, 9-15, <i>illus.</i> 45",
    #  "vi, xiv, 9-15, <i>illus.</i> 45"),
    ("<b>13</b>:10:19-21, <b>20</b>:46:5, <b>21</b>:3:15",
        "<b>13</b>:10:19\u201321, <b>20</b>:46:5, <b>21</b>:3:15"),
    ("mcmlxv, mcmlxx", "mcmlxv, mcmlxx"),
    ("53(vii)A, 53(vii)B, 53(ix)A", "53(vii)A, 53(vii)B, 53(ix)A"),
    # ("18, 45-47, A-2, Plate XIV",
    #     "A-2, Plate XIV, 18, 45\u201347"),
    ("II:5, II:7-9, II:24, II:55", "II:5, II:7\u20139, II:24, II:55"),
    # ("3-10 to 3-15, 4.10-15, A-2, B-7 to B-10",
    #     "A-2, B-7 to B-10, 3-10 to 3-15, 4.10\u201315"),
    ("32-38, 40fig, 45(ph), 45(map), 45t, 75-78",
        "32\u201338, 40fig, 45t, 45(map), 45(ph), 75\u201378"),
    ("56t12, 63a-66b, IV:2.3.1(a), 2:435, Plate IV@45, Plate XI@56.1",
        "IV:2.3.1(a), 2:435, Plate IV@45, 56t12, Plate XI@56.1, \
63a\u201366b"),
    ("85(nn. 15, 18), 56(t12), 112n26, 71(nn 23, 27), 91t.13, 105n14",
        "56(t12), 71(nn 23, 27), 85(nn. 15, 18), 91t.13, 105n14, 112n26"),
    # ("STR-23, UTL-4, REF-10, STR-5, STR-24",
    #     "REF-10, STR-5, STR-23, STR-24, UTL-4"),
    ("STR@1.23-23, UTL@2.4-4, REF@3.10-10, STR@1.5-5, STR@1.24-24",
     "STR@1.5–5, STR@1.23–23, STR@1.24–24, UTL@2.4–4, REF@3.10–10"),
    ("199-5, 9-6, 297-3", "9\u201316, 199\u2013205, 297\u2013303"),
    ("""3, 4.5, xii, 492, 4.5.6, 4.3, xiv, 4.9, vi, 89, 18(nn. 12, 15)""",
     """vi, xii, xiv, 3, 4.3, 4.5, 4.5.6, 4.9, 18(nn. 12, 15), 89, 492"""),
    )

PAGESPAIRS2 = (
    ("""492(<i>nn</i> 1, 3), vi, 12(<i>n</i>4), xiv, vii<i>n</i>5, \
xi<i>n</i>6, 52n7, 51<i>n</i>10, 15–16<i>n</i>12, 8<i>n14</i>""",
        """vi, vii<i>n</i>5, xi<i>n</i>6, xiv, 8<i>n14</i>, \
12(<i>n</i> 4), 15–16<i>n</i>12, 51<i>n</i>10, 52n7, \
492(<i>nn</i> 1, 3)"""),
    ("""89, 32, 4, xii, 492, vi, 12, xiv, 49, vi, 89, 18(nn 12, 15)""",
        """vi, xii, xiv, 4, 12, 18(nn 12, 15), 32, 49, 89, 492"""),
    ("""<b>719, 34, 11t</b>, ix, 42, <i>iv, 13f, 88</i>, 39, 4""",
        """<i>iv</i>, ix, 4, <b>11t</b>, <i>13f</i>,
<b>34</b>, 39, 42, <i>88</i>, <b>719</b>"""),
    ("""85, <b>35</b>(nn. 11, 19), 75<sub>2</sub>,\
<i>81<sup>a</sup></i>, 49""",
        """<b>35</b>(nn. 11, 19), 49, 75<sub>2</sub>,
<i>81</i><sup><i>a</i></sup>, 85"""),
    ("101–08, <b>808</b>–833, <i>1103–</i>104, 1206(nn. <b>83</b>, 91)",
        "101–8, <b>808</b>–33, <i>1103</i>–4, 1206(nn. <b>83</b>, 91)"),
    ("""<i>281f</i>, <i><span style="font-size: 11pt;
font-family: 'times new roman';">240 - 248 </span></i>, 116- 118, xv,
<b>32t</b>, 24""",
        """xv, 24, <b>32t</b>, 116\u201318, \
<i><span style="font-size: 11pt; font-family: 'times new roman';">240\
</span></i><i>\u2013</i>\
<i><span style="font-size: 11pt; font-family: 'times new roman';">48\
</span></i>, <i>281f</i>"""),
    ("102–09, <b>908</b>–933, 2103–<i>104</i>",
        "102–9, <b>908</b>–33, 2103–<i>4</i>"),
    ("321–328, 498–532, 1087–1089, 1496–1500, 11564–1615, 12991–13001",
        "321–28, 498–532, 1087–89, 1496–500, 11564–615, 12991–3001"),
    ("""89, 32, 4, xii, 492, vi, 12, <b>xiv-</b>xvii, 49, vi, 89""",
        """vi, xii, <b>xiv</b>\u2013xvii, 4, 12, 32, 49, 89, 492"""),
    ("""<b>719, 34, 11t</b>, ix, 42, <i>iv, 13f, 88</i>, 39, 4""",
        """<i>iv</i>, ix, 4, <b>11t</b>, <i>13f</i>,
<b>34</b>, 39, 42, <i>88</i>, <b>719</b>"""),
    ("""85, <b>35</b>, 75<sub>2</sub>, <i>81<sup>a</sup></i>,
49""",
        """<b>35</b>, 49, 75<sub>2</sub>,
<i>81</i><sup><i>a</i></sup>, 85"""),
    ("""<i>281f</i>, <i><span style="font-size: 11pt;
font-family: 'times new roman';">240 - 248 </span></i>, 116- 118, xv,
<b>32t</b>, 24""",
        """xv, 24, <b>32t</b>, 116\u201318, \
<i><span style="font-size: 11pt; font-family: 'times new roman';">240\
</span></i><i>\u2013</i>\
<i><span style="font-size: 11pt; font-family: 'times new roman';">48\
</span></i>, <i>281f</i>"""),
    ("""<i>203,</i> 290-293, <i>177-182,</i> <span
style="font-size: 11pt; font-family: 'arial';"><i>105,</i></span>
<i>343 - 350,</i> <i><b>239</b>,</i> 154, <span style="font-size: 11pt;
font-family: 'arial';">100,</span> 110, 63, <b>482</b>""",
        """63, <span style="font-size: 11pt; font-family:
'arial';">100</span>, <i><span style="font-size: 11pt; font-family:
'arial';">105</span></i>, 110, 154, <i>177</i><i>\u2013</i><i>82</i>, \
<i>203</i>, <i><b>239</b></i>, 290\u201393, \
<i>343</i><i>\u2013</i><i>50</i>, <b>482</b>"""),
    ("""420, 51<b>t</b>, <i>91<b>f,</b></i> 47\u2013<i>52,</i> 98,
420, 51<b>t</b>, <i>91<b>f</b>,</i> 47\u2013<i>52</i>, 98,
<b>82-<i>84</i></b>""",
        """47\u2013<i>52</i>, 51<b>t</b>,
<b>82</b><b>\u2013</b><i><b>84</b></i>, <i>91</i><i><b>f</b></i>, 98, \
420"""),
    ("""<b>117</b>, 420, 51<b>t</b>, <i>91<b>f</b></i>,
47-<i>52</i>, <b>62-</b><b><i>64</i></b>, 98, <i>2</i>""",
        """<i>2</i>, 47\u2013<i>52</i>, 51<b>t</b>,
<b>62</b><b>\u2013</b><i><b>64</b></i>, <i>91</i><i><b>f</b></i>, 98, \
<b>117</b>, 420"""),
    ("""7, 12, 78, 81<i>f</i>, 92-96, 203<b>t</b>, 206, 255,
290, 300t, 381, 482, 491, iv, xviii, <b>75c</b>""",
        """iv, xviii, 7, 12, <b>75c</b>, 78, 81<i>f</i>, 92\u201396,
203<b>t</b>, 206, 255, 290, 300t, 381, 482, 491""",),
    ("83, 56-74, 91, Frontispiece@0.1, 21-25 <i>passim</i>, 31",
     "Frontispiece@0.1, 21\u201325 <i>passim</i>, 31, 56\u201374, 83, 91"),
    ("2, 1.13, 1.49, 1.3 <i>illus.</i>, 1.8, 1.98, 1.2",
        "1.2, 1.3 <i>illus.</i>, 1.8, 1.13, 1.49, 1.98, 2"),
    ("2, 1.13, 1.4.12, 1.4.6, 1.4, 1.4.1, 1.8, 1.98, 1.2",
        "1.2, 1.4, 1.4.1, 1.4.6, 1.4.12, 1.8, 1.13, 1.98, 2"),
    ("3-10, <i>71-</i>2, 82-85, 87-<i>8</i>, 96-<b>117</b>, 97-9",
        """3\u201310, <i>71</i>\u201372, 82\u201385, 87\u2013<i>88</i>, \
96\u2013<b>117</b>, 97\u201399""",),
    ("1200-1213, 1300-324, 1400-81, 1500-9",
        "1200\u20131213, 1300\u20131324, 1400\u20131481, 1500\u20131509"),
    ("100-4, 110-15, 120-8, 1100-1113, 1200-7, 1300-34, 1400-1595, \
1500-1581",
        """100\u2013104, 110\u201315, 120\u201328, 1100\u20131113, \
1200\u20131207, 1300\u20131334, 1400\u20131595, 1500\u20131581"""),
    ("101-108, 202-15, 304-9, 808-33, 909-11, 1103-4, 1205-16, \
1308-401",
        """101\u20138, 202\u201315, 304\u20139, 808\u201333, \
909\u201311, 1103\u20134, 1205\u201316, 1308\u2013401"""),
    ("321-28, 418-9, 498-532, 1087-89, 1287-9, 1496-500, 11564-615, \
12991-3001",
        """321\u201328, 418\u201319, 498\u2013532, 1087\u201389, \
1287\u201389, 1496\u2013500, 11564\u2013615, 12991\u20133001"""),
    ("101-08, 808-33, 909-21, 1103-104, 1202-206",
        "101\u20138, 808\u201333, 909\u201321, 1103\u20134, 1202\u20136"),
    ("101–108, 808–833, 1103–1104",
        "101–8, 808–33, 1103–4"),
    ("321–328, 498–532, 1087–1089, 1496–1500, 11564–11615, 12991–13001",
        "321–28, 498–532, 1087–89, 1496–500, 11564–615, 12991–3001"),
    ("89, 106–108n., Frontispiece, 202f, 13-18 passim, 21",
        "Frontispiece, 13\u201318 passim, 21, 89, 106–108n., 202f"),
    # Dissalowed
    # ("vi, xiv, 9-15, <i>illus.</i> 45",
    #  "vi, xiv, 9-15, <i>illus.</i> 45"),
    ("<b>13</b>:10:19-21, <b>20</b>:46:5, <b>21</b>:3:15",
        "<b>13</b>:10:19\u201321, <b>20</b>:46:5, <b>21</b>:3:15"),
    ("mcmlxv, mcmlxx", "mcmlxv, mcmlxx"),
    ("53(vii)A, 53(vii)B, 53(ix)A", "53(vii)A, 53(vii)B, 53(ix)A"),
    # ("18, 45-47, A-2, Plate XIV",
    #     "A-2, Plate XIV, 18, 45\u201347"),
    ("II:5, II:7-9, II:24, II:55", "II:5, II:7\u20139, II:24, II:55"),
    # ("3-10 to 3-15, 4.10-15, A-2, B-7 to B-10",
    #     "A-2, B-7 to B-10, 3-10 to 3-15, 4.10\u201315"),
    ("32-38, 40fig, 45(ph), 45(map), 45t, 75-78",
        "32\u201338, 40fig, 45t, 45(map), 45(ph), 75\u201378"),
    ("56t12, 63a-66b, IV:2.3.1(a), 2:435, Plate IV@45, Plate XI@56.1",
        "IV:2.3.1(a), 2:435, Plate IV@45, 56t12, Plate XI@56.1, \
63a\u201366b"),
    ("56(t12), 71(nn 23, 27), 85(nn. 15, 18), 91t.13, 105n14, 112n26",
        "56(t12), 71(nn 23, 27), 85(nn. 15, 18), 91t.13, 105n14, 112n26"),
    # ("STR-23, UTL-4, REF-10, STR-5, STR-24",
    #     "REF-10, STR-5, STR-23, STR-24, UTL-4"),
    ("STR@1.23-23, UTL@2.4-4, REF@3.10-10, STR@1.5-5, STR@1.24-24",
     "STR@1.5–5, STR@1.23–23, STR@1.24–24, UTL@2.4–4, REF@3.10–10"),
    ("199-5, 9-6, 297-3", "9\u201316, 199\u2013205, 297\u2013303"),
    ("""3, 4.5, xii, 492, 4.5.6, 4.3, xiv, 4.9, vi, 89, 18(nn. 12, 15)""",
     """vi, xii, xiv, 3, 4.3, 4.5, 4.5.6, 4.9, 18(nn. 12, 15), 89, 492"""),
    )

PAGESPAIRS3 = (
    ("""89, 32, 4, xii, 492, vi, 12, xiv, 49, vi, 89, 18(nn 12, 15)""",
        """VI XII XIV 4 12 18 32 49 89 492"""),
    ("""<b>719, 34, 11t</b>, ix, 42, <i>iv, 13f, 88</i>, 39, 4""",
        """IV IX 4 11 13 34 39 42 88 719"""),
    ("""85, <b>35</b>(nn. 11, 19), 75<sub>2</sub>,\
<i>81<sup>a</sup></i>, 49""",
        """35 49 75 81 85"""),
    ("101–08, <b>808</b>–813, <i>1103–</i>104, 1206(nn. <b>83</b>, 91)",
        "101 102 103 104 105 106 107 108 808 809 810 811 812 813 \
1103 1104 1206"),
    ("""<i>281f</i>, <i><span style="font-size: 11pt;
font-family: 'times new roman';">240 - 248 </span></i>, 116- 118, xv,
<b>32t</b>, 24""",
        "XV 24 32 116 117 118 240 241 242 243 244 245 246 247 248 281"),
    ("102–09, <b>908</b>–914, 2103–<i>104</i>",
        "102 103 104 105 106 107 108 109 908 909 910 911 912 913 914 \
2103 2104"),
    ("""ix-xiv, xvii, 42, <i>iv, 13f, 88</i>, 39, 4""",
        """IV IX X XI XII XIII XIV XVII 4 13 39 42 88"""),
    ("IV 186 139, 105,", "IV 105"),
    ("199-5, 9-6, 297-3",
     """9 10 11 12 13 14 15 16 199 200 201 202 203 204 205 \
297 298 299 300 301 302 303"""),
    )

PAGESPAIRS4 = (
    ("""492(<i>nn</i> 1, 3), vi, 12(<i>n</i>4), xiv, vii<i>n</i>5, \
xi<i>n</i>6, 52n7, 51<i>n</i>10, 15–16<i>n</i>12, 8<i>n14</i>""",
        """vi, vii<i>n</i>5, xi<i>n</i>6, xiv, 8<i>n14</i>, \
12(<i>n</i> 4), 15–16<i>n</i>12, 51<i>n</i>10, 52n7, \
492(<i>nn</i> 1, 3)"""),
    ("30-31, 42-43, 132-136, 1841-1845, 10-12, 15-19, 114-118, \
214-215, 310-311",
        "10–12, 15–19, 30–1, 42–3, 114–18, 132–6, 214–15, 310–11, 1841–5"),
    )

PAGESDATA = ( # pages, highest, largest range, number of
    ("""492(<i>nn</i> 1, 3), vi, 12(<i>n</i>4), xiv, vii<i>n</i>5, \
xi<i>n</i>6, 52n7, 51<i>n</i>10, 15–16<i>n</i>12, 8<i>n14</i>""",
     492, 2, 10),
    ("""89, 32, 4, xii, 492, vi, 12, xiv, 49, vi, 89, 18(nn 12, 15)""",
     492, 0, 10),
    ("""<b>719, 34, 11t</b>, ix, 42, <i>iv, 13f, 88</i>, 39, 4""",
     719, 0, 10),
    ("""85, <b>35</b>(nn. 11, 19), 75<sub>2</sub>,\
<i>81<sup>a</sup></i>, 49""",
     85, 0, 5),
    ("101–8, <b>808</b>–33, <i>1103–</i>4, 1206(nn. <b>83</b>, 91)",
     1206, 26, 4),
    ("""<i>281f</i>, <i><span style="font-size: 11pt;
font-family: 'times new roman';">240 - 248 </span></i>, 116- 118, xv,
<b>32t</b>, 24""",
     281, 9, 6),
    ("102–9, <b>908</b>–33, 2103–<i>4</i>",
     2104, 26, 3),
    ("321–28, 498–532, 1087–89, 1496–500, 11564–615, 12991–3001",
     13001, 52, 6),
    ("""89, 32, 4, xii, 492, vi, 12, <b>xiv-</b>xvii, 49, vi, 89""",
     492, 4, 9),
    ("""<b>719, 34, 11t</b>, ix, 42, <i>iv, 13f, 88</i>, 39, 4""",
     719, 0, 10),
    ("""85, <b>35</b>, 75<sub>2</sub>, <i>81<sup>a</sup></i>, 49""",
     85, 0, 5),
    ("""<i>281f</i>, <i><span style="font-size: 11pt;
font-family: 'times new roman';">240 - 248 </span></i>, 116- 118, xv,
<b>32t</b>, 24""",
     281, 9, 6),
    ("""<i>203,</i> 290-293, <i>177-182,</i> <span
style="font-size: 11pt; font-family: 'arial';"><i>105,</i></span>
<i>343 - 350,</i> <i><b>239</b>,</i> 154, <span style="font-size: 11pt;
font-family: 'arial';">100,</span> 110, 63, <b>482</b>""",
     482, 8, 11),
    ("""420, 51<b>t</b>, <i>91<b>f,</b></i> 47\u2013<i>52,</i> 98,
420, 51<b>t</b>, <i>91<b>f</b>,</i> 47\u2013<i>52</i>, 98,
<b>82-<i>84</i></b>""",
     420, 6, 6),
    ("""<b>117</b>, 420, 51<b>t</b>, <i>91<b>f</b></i>,
47-<i>52</i>, <b>62-</b><b><i>64</i></b>, 98, <i>2</i>""",
     420, 6, 8),
    ("""7, 12, 78, 81<i>f</i>, 92-96, 203<b>t</b>, 206, 255,
290, 300t, 381, 482, 491, iv, xviii, <b>75c</b>""",
     491, 5, 16),
    ("83, 56-74, 91, Frontispiece@0.1, 21-25 <i>passim</i>, 31",
     91, 19, 6),
    ("2, 1.13, 1.49, 1.3 <i>illus.</i>, 1.8, 1.98, 1.2",
     2, 0, 7),
    ("2, 1.13, 1.4.12, 1.4.6, 1.4, 1.4.1, 1.8, 1.98, 1.2",
     2, 0, 9),
    ("3-10, <i>71-</i>2, 82-85, 87-<i>8</i>, 96-<b>117</b>, 97-9",
     117, 22, 6),
    ("1200-1213, 1300-324, 1400-81, 1500-9",
     1509, 82, 4),
    ("100-4, 110-15, 120-8, 1100-1113, 1200-7, 1300-34, 1400-1595, \
1500-1581",
     1595, 196, 8),
    ("101-108, 202-15, 304-9, 808-33, 909-11, 1103-4, 1205-16, \
1308-401",
     1401, 94, 8),
    ("321-28, 418-9, 498-532, 1087-89, 1287-9, 1496-500, 11564-615, \
12991-3001",
     13001, 52, 8),
    ("101-08, 808-33, 909-21, 1103-104, 1202-206",
     1206, 26, 5),
    ("101–108, 808–833, 1103–1104", 1104, 26, 3),
    ("321–328, 498–532, 1087–1089, 1496–1500, 11564–11615, 12991–13001",
     13001, 52, 6),
    # ("89, 106–108n., Frontispiece, 202f, 14-18 passim, 21",
    #  202, 5, 6), # FAILURE CASE
    # Dissalowed
    # ("vi, xiv, 9-15, <i>illus.</i> 45",
    #  "vi, xiv, 9-15, <i>illus.</i> 45"),
    # ("<b>13</b>:10:19-21, <b>20</b>:46:5, <b>21</b>:3:15",
    #  21, 4, 3), # FAILURE CASE
    ("mcmlxv, mcmlxx", 1970, 0, 2),
    ("53(vii)A, 53(vii)B, 53(ix)A", 53, 0, 3),
    # ("18, 45-47, A-2, Plate XIV",
    #     "A-2, Plate XIV, 18, 45\u201347"),
    # ("II:5, II:7-9, II:24, II:55", 2, 2, 4), # FAILURE CASE
    # ("3-10 to 3-15, 4.10-15, A-2, B-7 to B-10",
    #     "A-2, B-7 to B-10, 3-10 to 3-15, 4.10\u201315"),
    ("32-38, 40fig, 45(ph), 45(map), 45t, 75-78",
     78, 7, 6),
    ("56t12, 63a-66b, IV:2.3.1(a), 2:435, Plate IV@45, Plate XI@56.1",
     66, 4, 6),
    ("85(nn. 15, 18), 56(t12), 112n26, 71(nn 23, 27), 91t.13, 105n14",
     112, 0, 6),
    # ("STR-23, UTL-4, REF-10, STR-5, STR-24",
    #     "REF-10, STR-5, STR-23, STR-24, UTL-4"),
    # ("STR@1.23-23, UTL@2.4-4, REF@3.10-10, STR@1.5-5, STR@1.24-24",
    #  3, 1, 5), # FAILURE CASE
    ("199-5, 9-6, 297-3", 303, 8, 3),
    ("""3, 4.5, xii, 492, 4.5.6, 4.3, xiv, 4.9, vi, 89, 18(nn. 12, 15)""",
     492, 0, 11),
    )


if __name__ == "__main__":
    unittest.main()
