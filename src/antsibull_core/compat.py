# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2020, Ansible Project
"""Compat for older versions of Python.

PARTS OF THIS MODULE ARE DEPRECATED AND WILL BE REMOVED IN ANTSIBULL-CORE 3.0.0:
  - the `metadata` module;
  - the functions `asyncio_run`, `best_get_loop`, and `create_task`.
"""

from __future__ import annotations

import argparse
import sys

BooleanOptionalAction: type[argparse.BooleanOptionalAction]

if sys.version_info < (3, 9, 11) or (
    sys.version_info >= (3, 10, 0) and sys.version_info < (3, 10, 3)
):
    # https://bugs.python.org/issue46080 was fixed in Python 3.11.0 alpha 5
    # (https://docs.python.org/3/whatsnew/changelog.html#python-3-11-0-alpha-5)
    # and backported to Python 3.10.3
    # (https://docs.python.org/3.10/whatsnew/changelog.html#python-3-10-3-final)
    # and Python 3.9.11
    # (https://docs.python.org/3.9/whatsnew/changelog.html#python-3-9-11-final).
    # Versions before these have to use the vendored version so that users can actually
    # use `--help` for affected subcommands.
    from .vendored._argparse_booleanoptionalaction import (  # type: ignore
        BooleanOptionalAction,
    )
else:
    BooleanOptionalAction = argparse.BooleanOptionalAction


__all__ = ("BooleanOptionalAction",)
