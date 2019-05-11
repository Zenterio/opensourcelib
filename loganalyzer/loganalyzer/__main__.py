"""
loganalyzer -- analyzes a log using a set of configurable rules.

loganalyzer analyzes a log using a set of configurable rules, defined in a
configuration file, and outputs a report and a summary.

@copyright:  2016 Zenterio AB. All rights reserved.

@license:    Apache 2.0 License
"""

import sys

from loganalyzer.loganalyzercli import main


def entry_point():
    sys.exit(main())


if __name__ == '__main__':
    entry_point()
