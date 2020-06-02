#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

# Lib/Lib.py
# Lib/Qt.py
# Lib/Win.py
# Lib/Command.py
# Lib/Transaction.py

from .Lib import (htmlToPlainText, htmlToCanonicalText, elide, # noqa
                  elideHtml, spellNumber, registerRules, initials,
                  incrementedFilename, patchFont, isclose, get_path,
                  replace_extension, clamp, remove_file, uopen,
                  sanePointSize, KEY_VALUE_RX, PATCH_FONT_RX,
                  MonitorFile, swapAcronym, CopyInfo)
from .Qt import (Timer, BlockSignals, DisableUI, addActions, # noqa
                 createAction, createFontBoxesFor, updatable_tooltips,
                 prepareModalDialog, rulesTip, elidePatchHtml,
                 restoreFocus)
from .Win import maybe_register_filetype
from . import Command, Transaction # noqa
from .Porter import stem # noqa
