#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

# Output/Iter.py
# Output/Markup.py
# Output/_Markup.py
# Output/Docx.py
# Output/Ixml.py
# Output/Pdf.py
# Output/Ximl.py

import html
import os

from . import Markup
from . import Docx
from . import Ixml
from . import Pdf
from . import Ximl


class Error(Exception):
    pass


def outputEntries(model, config, prefix, reportProgress):
    extension = os.path.splitext(config.Filename)[1].casefold()
    markup = model.markup(extension) # Custom markup takes precedence
    if markup is not None:
        markup.escape = escape_function(markup.escapefunction)
        Markup.outputEntries(model, markup, config, prefix, reportProgress)
        return
    outputEntries = {".ximl": Ximl.outputEntries,
                     ".ixml": Ixml.outputEntries,
                     }.get(extension)
    if outputEntries is not None:
        return outputEntries(model, config, prefix, reportProgress)
    markup = Markup.MarkupForExtension.get(extension)
    if markup is not None:
        document = Markup.outputEntries(model, markup, config, prefix,
                                        reportProgress)
        if document:
            if markup.kind is Markup.FileKind.DOCX:
                Docx.output(config, document)
            elif markup.kind in {Markup.FileKind.PDF,
                                 Markup.FileKind.PRINT}:
                Pdf.output(config, document)
        return
    raise Error("Cannot output “{}” format".format(extension))


def escape_function(escapefunction):
    if escapefunction == "ucp":
        return (lambda x: x.replace("<", "\x01").replace(">", "<>>")
                .replace("\x01", "<<>"))
    elif escapefunction == "html":
        return html.escape
    return lambda x: x # identity
