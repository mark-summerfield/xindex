#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import re
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import Lib


class TestElideHtml(unittest.TestCase):

    def test1(self):
        for i, (actual, expected) in enumerate(DATA):
            with self.subTest(i=i):
                actual = re.sub(r"\s+", " ", actual)
                expected = re.sub(r"\s+", " ", expected)
                elided = Lib.elideHtml(actual, 20)
                if elided != expected:
                    print(("Act.", actual))
                    print(("Want", expected))
                    print(("Got ", elided))
                    print(len(Lib.htmlToPlainText(elided)))
                self.assertEqual(elided, expected)



class TestSwapAcronym(unittest.TestCase):

    def test1(self):
        for actual, expected in (
                ("Federal Bureau of Investigation (FBI)",
                 "FBI (Federal Bureau of Investigation)"),
                ("Central Intelligence Agency (CIA)",
                 "CIA (Central Intelligence Agency)"),
                ):
            swapped = Lib.swapAcronym(actual)
            self.assertEqual(swapped, expected)
            swapped = Lib.swapAcronym(swapped)
            self.assertEqual(swapped, actual)


DATA = (
    ("""<p><span style="font-family: 'courier new'; font-size:
     9pt;">unordered_map</span> (C++ standard library collections type)
     </p>""",
     """<p><span style="font-family: 'courier new'; font-size:
     9pt;">unordered_map\u2026</span>type)
     </p>"""),
    ("""<p>dictionary or hash mapping. <i>See</i> <span
     style="font-family: 'courier new'; font-size: 9pt;">dict</span><span
     style="font-family: 'times new roman'; font-size: 10pt;">
     (type)</span>; <span style="font-family: 'courier new'; font-size:
     9pt;">OrderedDict</span> (type; <span style="font-family: 'courier
     new'; font-size: 9pt;">collections</span> module)</p>""",
     """<p>dictionary \u2026 module)</p>"""),
    ("""<p>argument, sequence, and mapping unpacking, 13, 222, 241–242,
     248</p>""",
     """<p>argument, seque\u2026 248</p>"""),
    ("""<p>The <span style="font-family: 'courier new'; font-size:
     9pt;">walk_packages()</span> function family, 126</p>""",
     """<p>The <span style="font-family: 'courier new'; font-size:
     9pt;">wal\u2026</span> family, 126</p>"""),
    ("""<p><span style="font-family: 'courier new'; font-size:
     9pt;">place()</span> (<span style="font-family: 'courier new';
     font-size: 9pt;">tkinter.ttk.Widget</span>), Graphical User
     Interface layout function</p>""",
     """<p><span style="font-family: 'courier new'; font-size:
     9pt;">place()\u2026</span>out function</p>"""),
    ("""<p>Operating system <span style="font-family: 'courier new';
     font-size: 9pt;">platform</span> (<span style="font-family: 'courier
     new'; font-size: 9pt;">sys</span> module), 85–86</p>""",
     """<p>Operating sys\u2026 85–86</p>"""),
    ("""<p>▶ Portable Network Graphics (image format), 38, 124, 125,
     137–139, 239</p>""",
     """<p>▶ Portable\u2026–139, 239</p>"""),
    ("""<p>C-style function pointer, 182, 190</p>""",
     """<p>C-style functio\u2026 190</p>"""),
    ("""<p><span style="font-family: 'courier new'; font-size:
     9pt;">POINTER()</span> (<span style="font-family: 'courier new';
     font-size: 9pt;">ctypes</span> module), 184</p>""",
     """<p><span style="font-family: 'courier new'; font-size:
     9pt;">POINTER()\u2026</span>dule), 184</p>"""),
    ("""<p><span style="font-family: 'ariel'; font-size:
     9pt;">Telephone, The</span>, ▷ <span style="font-family: 'courier new';
     font-size: 9pt;">Inventor</span>, <i>Alexander Graham Bell</i></p>""",
     """<p><span style="font-family: 'ariel'; font-size:
     9pt;">Telephone, The\u2026</span><i> Bell</i></p>"""),
    ("""A very long line of completely plain text with no HTML tags""",
     """A very lo\u2026 HTML tags"""),
    )


if __name__ == "__main__":
    unittest.main()
