# SPDX-FileCopyrightText: © 2022 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

"""
Wrapper function for print() to use stderr instead of stdout.
"""

import sys

def eprint(*args, **kwargs):
    """
    Wrapper function for print() to use stderr instead of stdout.
    """
    print(*args, file=sys.stderr, **kwargs)
