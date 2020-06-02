#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

import html.parser
import re

import Lib


SPLIT_RX = re.compile(r"(,)")


class Chunk:

    __slots__ = ("text", "bold", "fontfamily", "fontsize", "italic",
                 "subscript", "superscript", "underline")

    def __init__(self, text, bold=0, fontfamily=None, fontsize=None,
                 italic=0, subscript=0, superscript=0, underline=0):
        self.text = text
        self.bold = bold
        self.fontfamily = fontfamily
        self.fontsize = fontsize
        self.italic = italic
        self.subscript = subscript
        self.superscript = superscript
        self.underline = underline


class Parser(html.parser.HTMLParser):
    # Used to convert HTML like this:
    #   <b>719, 34, 11t</b>, ix, 42, <i>iv, 13f, 88</i>, 39, 4
    # to this:
    #   <b>719,</b> <b>34,</b> <b>11t</b>, ix, 42, <i>iv,</i>
    #   <i>13f,</i> <i>88</i>, 39, 4

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chunks = []
        self.fontfamily = [] # Empty means std family
        self.fontsize = [] # Empty means std size
        self.bold = 0
        self.italic = 0
        self.subscript = 0
        self.superscript = 0
        self.underline = 0
        self.ids = []


    def handle_starttag(self, tag, attrs):
        if tag == "b":
            self.bold += 1
        elif tag == "i":
            self.italic += 1
        elif tag == "span":
            for name, value in attrs:
                if name == "style":
                    for match in Lib.KEY_VALUE_RX.finditer(value):
                        key = match.group("key")
                        if key == "font-family":
                            self.ids.append("font")
                        if key == "font-family":
                            value = match.group("value").strip("'\" ")
                            self.fontfamily.append(value)
                        elif key == "font-size":
                            self.fontsize.append(match.group("value"))
        elif tag == "sub":
            self.subscript += 1
        elif tag == "sup":
            self.superscript += 1
        elif tag == "u":
            self.underline += 1


    def handle_endtag(self, tag):
        if tag == "b":
            self.bold -= 1
        elif tag == "i":
            self.italic -= 1
        elif tag == "span":
            id = self.ids.pop()
            if id == "font":
                self.fontfamily.pop()
                self.fontsize.pop()
        elif tag == "sub":
            self.subscript -= 1
        elif tag == "sup":
            self.superscript -= 1
        elif tag == "u":
            self.underline -= 1


    def handle_data(self, data):
        fontfamily = self.fontfamily[-1] if self.fontfamily else None
        fontsize = (Lib.sanePointSize(self.fontsize[-1]) if self.fontsize
                    else None)
        for text in SPLIT_RX.split(data):
            if text == ",":
                self.chunks.append(Chunk(","))
                continue
            if text.startswith(" "):
                self.chunks.append(Chunk(" "))
                text = text[1:]
            self.chunks.append(Chunk(
                text, self.bold > 0, fontfamily, fontsize, self.italic > 0,
                self.subscript > 0, self.superscript > 0,
                self.underline > 0))


    def toHtml(self):
        chunks = []
        for chunk in self.chunks:
            pre = []
            post = []
            if chunk.subscript:
                pre.append("<sub>")
                post.append("</sub>")
            if chunk.superscript:
                pre.append("<sup>")
                post.append("</sup>")
            if chunk.underline:
                pre.append("<u>")
                post.append("</u>")
            if chunk.italic:
                pre.append("<i>")
                post.append("</i>")
            if chunk.bold:
                pre.append("<b>")
                post.append("</b>")
            if chunk.fontfamily is not None:
                pre.append(
                    """<span style="font-size: {}; font-family: '{}';">"""
                    .format(Lib.sanePointSize(chunk.fontsize),
                            chunk.fontfamily))
                post.append("</span>")
            if pre:
                chunks.extend(pre)
            chunks.append(chunk.text)
            if post:
                chunks.extend(post)
        return "".join(chunks)
