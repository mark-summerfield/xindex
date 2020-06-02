#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import re

import Xix.Output
from Const import SeeAlsoPositionKind, XRefToSubentryKind


INDENT_AND_TEXT_RX = re.compile(r"^(?P<indent>\t*)(?P<text>.*$)")


class _Base:

    def __init__(self, line=""):
        self.line = line # HTML


class Start:

    def __init__(self, title="", note=""):
        self.title = title # HTML
        self.note = note # HTML


class Section(_Base):
    pass


class Line(_Base):

    def __init__(self, indent=0, line=""):
        super().__init__(line)
        self.indent = indent


class End(_Base):
    pass


def outputEntries(model, config):
    pendingXrefs = []
    pendingSection = None
    prevIndent = 0
    for item in model.outputEntries(config):
        if isinstance(item, Xix.Output.Start):
            yield Start(item.title, item.note)
        elif isinstance(item, Xix.Output.Section):
            if pendingXrefs:
                pendingSection = Section(item.line)
            else:
                yield Section(item.line)
        elif isinstance(item, Xix.Output.End):
            pass # Done at the end after any pending see also xrefs
        else: # item is an Xix.Entry -- this must go last!
            texts = []
            if item.indent < prevIndent and pendingXrefs:
                pendingXref = pendingXrefs.pop()
                texts += pendingXref
            texts += ["\n", "\t" * item.indent, item.term]
            if item.xrefs:
                xrefs, pendingXref = termWithXRefs(item, config)
                texts += xrefs
                if pendingXref is not None:
                    pendingXrefs.append(pendingXref)
            else:
                texts += simpleTerm(item, config)
            prevIndent = item.indent
            if texts:
                yield from linesForTexts(texts, pendingSection)
                pendingSection = None
    if pendingXrefs:
        while pendingXrefs:
            pendingXref = pendingXrefs.pop()
            texts = pendingXref + ["\n"]
            yield from linesForTexts(texts)
    yield End()


def simpleTerm(item, config):
    texts = []
    if item.pages:
        texts += [config.TermPagesSeparator, item.pages]
    return texts


def termWithXRefs(item, config):
    pendingXref = None
    pages = []
    if item.pages:
        pages = [config.TermPagesSeparator, item.pages]
    sees, alsos = listsOfXRefs(item.xrefs, item.istoplevel, config)
    texts = pages
    if sees:
        texts += sees
    if alsos:
        if (config.SeeAlsoPosition is
                SeeAlsoPositionKind.AFTER_PAGES):
            texts += alsos
        elif (config.SeeAlsoPosition is
                SeeAlsoPositionKind.FIRST_SUBENTRY or
                (config.SeeAlsoPosition is
                    SeeAlsoPositionKind.LAST_SUBENTRY and
                    not item.haschildren)):
            indent = "\t" * (item.indent + 1)
            texts += ["\n", indent] + alsos
        elif (config.SeeAlsoPosition is
                SeeAlsoPositionKind.LAST_SUBENTRY):
            indent = "\t" * (item.indent + 1)
            pendingXref = ["\n", indent] + alsos
    return texts, pendingXref


def xrefText(xref, config):
    if xref.totermparent:
        if config.XRefToSubentry is XRefToSubentryKind.COLON:
            return xref.totermparent + ": " + xref.toterm
        elif config.XRefToSubentry is XRefToSubentryKind.COMMA:
            return xref.totermparent + ", " + xref.toterm
        elif config.XRefToSubentry is XRefToSubentryKind.UNDER:
            return "under " + xref.totermparent
    return xref.toterm


def listsOfXRefs(xrefs, istoplevel, config):
    if istoplevel:
        seePrefix = config.SeePrefix
        seeText = config.See
        seeSeparator = config.SeeSeparator
        seeSuffix = config.SeeSuffix
        seeAlsoPrefix = config.SeeAlsoPrefix
        seeAlsoText = config.SeeAlso
        seeAlsoSeparator = config.SeeAlsoSeparator
        seeAlsoSuffix = config.SeeAlsoSuffix
    else:
        seePrefix = config.SubSeePrefix
        seeText = config.SubSee
        seeSeparator = config.SubSeeSeparator
        seeSuffix = config.SubSeeSuffix
        seeAlsoPrefix = config.SubSeeAlsoPrefix
        seeAlsoText = config.SubSeeAlso
        seeAlsoSeparator = config.SubSeeAlsoSeparator
        seeAlsoSuffix = config.SubSeeAlsoSuffix
    sees = []
    alsos = []
    for xref in xrefs:
        if isinstance(xref, (Xix.Output.See, Xix.Output.SeeGeneric)):
            if not sees:
                sees += [seePrefix, seeText]
            if not sees[-1] == seeText:
                sees += [seeSeparator if isinstance(xref,
                         Xix.Output.See) else config.GenericConjunction]
            sees += [xrefText(xref, config)]
        else:
            if not alsos:
                alsos += [seeAlsoPrefix, seeAlsoText]
            if not alsos[-1] == seeAlsoText:
                alsos += [seeAlsoSeparator if isinstance(
                    xref, Xix.Output.SeeAlso) else
                    config.GenericConjunction]
            alsos += [xrefText(xref, config)]
    if sees:
        sees += [seeSuffix]
    if alsos:
        alsos += [seeAlsoSuffix]
    return sees, alsos


def linesForTexts(texts, section=None):
    prevIndent = 0
    for text in "".join((text or "" for text in texts)).split("\n"):
        if text:
            match = INDENT_AND_TEXT_RX.search(text)
            indent = len(match.group("indent"))
            text = match.group("text")
            if indent < prevIndent and section is not None:
                yield section
                section = None
            prevIndent = indent
            yield Line(indent, text.strip())
    if section:
        yield section
