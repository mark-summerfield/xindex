#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

import os
import pathlib
import re


ROOT = str(pathlib.Path(os.path.dirname(__file__)).parent.resolve())

IGNORE_PNG = {"American.png", "Australian.png", "British.png",
              "Canadian.png", "South_African.png", "splash.png"}
IGNORE_SVG = {"American.svg", "Australian.svg", "British.svg",
              "Canadian.svg", "South_African.svg", "splash.svg"}



def main():
    check_doc_icons()
    check_py_icons()
    check_qrc_icons()


def check_doc_icons():
    existing = set(read_filenames(DOCIMGPATH, ".png", withpath=False))
    used = set()
    missing = set()
    for html in read_filenames(DOCPATH, ".html"):
        process(html, existing, used, missing)
    report("doc", DOCIMGPATH, existing, used, missing)


def check_py_icons():
    existing = set(read_filenames(EXEIMGPATH, ".png", withpath=False))
    used = set()
    missing = set()
    for py in read_filenames(EXEPATH, ".pyw", ".py"):
        process(py, existing, used, missing)
    report("py", EXEIMGPATH, existing, used, missing,
           ignore=IGNORE_PNG | IGNORE_SVG)


def check_qrc_icons():
    existing = set(read_filenames(EXEIMGPATH, ".png", ".svg",
                                  withpath=False))
    used = set()
    missing = set()
    process(os.path.join(EXEPATH, "resource.qrc"), existing, used, missing)
    report("qrc", EXEIMGPATH, existing, used, missing,
           ignore=IGNORE_PNG | IGNORE_SVG | {"xindex.png"})


def process(filename, existing, used, missing):
    with open(filename, "rt", encoding="utf-8") as file:
        text = file.read()
    for match in IMG_RX.finditer(text):
        img = match.group("img")
        if img in existing:
            used.add(img)
        else:
            missing.add(img)


def report(title, path, existing, used, missing, ignore=None):
    if ignore is None:
        ignore = set()
    redundant = existing - used
    redundant -= ignore
    missing -= ignore
    if redundant or missing:
        print("echo {:-^30.30}".format(title))
        for img in sorted(redundant):
            print("rm -f       ", os.path.join(path, img))
        for img in sorted(missing):
            print("echo missing:", os.path.join(path, img))


def read_filenames(path, *suffixes, withpath=True):
    for root, _, files in os.walk(os.path.abspath(path)):
        for name in files:
            if name.endswith(suffixes):
                yield os.path.join(root, name) if withpath else name


DOCPATH = os.path.join(ROOT, "doc")
DOCIMGPATH = os.path.join(DOCPATH, "images")
EXEPATH = ROOT
EXEIMGPATH = os.path.join(EXEPATH, "images")
IMG_RX = re.compile(r"images\/(?P<img>.+?\.(?:png|svg))")


if __name__ == "__main__":
    main()
