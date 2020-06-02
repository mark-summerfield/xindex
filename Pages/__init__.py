#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

# Pages/Common.py
# Pages/Page.py
# Pages/Parser.py
# Pages/PreParser.py
# Pages/PageRange.py
# Pages/Util.py

from .Common import (searchablePages, sortedPages, mergedPages, # noqa
                     hasOverlappingPages, combinedOverlappingPages,
                     toIndividualHtmlPages, renumbered, highestPage,
                     largestPageRange, pagesCount)
from .PageRange import (pageRangeFull, pageRangeCMS16, # noqa
                        pageRangeISO999, RulesForName)
from .Util import Error # noqa


# Testing and debugging:
#   tests/pages.py
#   tests/run_pages.py
