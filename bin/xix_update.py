#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import Xix


def main():
    if len(sys.argv) > 1 and sys.argv[1] in {"-h", "--help"}:
        raise SystemExit("""usage: {}
updates the .xix files in the current directory and subdirectories
simply by opening and closing them.
""".format(os.path.basename(sys.argv[0])))
    for root, _, filenames in os.walk("."):
        for filename in filenames:
            if filename.lower().endswith(".xix"):
                fullname = os.path.join(root, filename)
                with Xix.Xix.Xix(fullname) as xix: # noqa
                    xix.optimize()
                print(fullname)


if __name__ == "__main__":
    main()
