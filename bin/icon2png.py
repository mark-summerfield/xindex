#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import pathlib
import re

ROOT = str(pathlib.Path(os.path.dirname(__file__)).parent.resolve())
SRC = os.path.join(ROOT, "images")
DST = os.path.join(ROOT, "doc/images")
DOCPATH = os.path.join(ROOT, "doc")
IMG_RX = re.compile(r"images\/(?P<img>.+?\.(?:png|svg))")


def read_filenames(path, *suffixes, withpath=True):
    for root, _, files in os.walk(os.path.abspath(path)):
        for name in files:
            if name.endswith(suffixes):
                yield os.path.join(root, name) if withpath else name


images = set()
for html in read_filenames(DOCPATH, ".html"):
    with open(html, "rt", encoding="utf-8") as file:
        text = file.read()
    for match in IMG_RX.finditer(text):
        images.add(match.group("img"))


for name in os.listdir(SRC):
    if name.endswith(".svg"):
        svg = os.path.join(SRC, name)
        png = name.replace(".svg", ".png")
        if png in images:
            png = os.path.join(DST, png)
            command = "convert -scale 24x24 {} {}".format(svg, png)
            print(command)
            os.system(command)
