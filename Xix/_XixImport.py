#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os

import Lib
from . import _XixImportXiml as ImportXiml
from . import _XixImportIxml as ImportIxml


class Error(Exception):
    pass


class Mixin:

    def _importIndex(self, inFilename):
        extension = os.path.splitext(inFilename)[1].casefold()
        function = {".ixml": ImportIxml.importIndex,
                    ".ximl": ImportXiml.importIndex}.get(extension)
        if function is not None:
            with Lib.Transaction.Transaction(self) as cursor:
                return function(cursor, inFilename)
        raise Error("Cannot import “{}” format".format(extension))
