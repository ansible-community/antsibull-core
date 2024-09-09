# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021, Ansible Project
"""I/O helper functions."""

from __future__ import annotations

import typing as t

from antsibull_fileutils.io import copy_file as _copy_file
from antsibull_fileutils.io import read_file as _read_file
from antsibull_fileutils.io import write_file as _write_file

from .. import app_context
from ..logging import log

if t.TYPE_CHECKING:
    from _typeshed import StrOrBytesPath

mlog = log.fields(mod=__name__)


async def copy_file(
    source_path: StrOrBytesPath, dest_path: StrOrBytesPath, check_content: bool = True
) -> None:
    """
    Copy content from one file to another.

    :arg source_path: Source path. Must be a file.
    :arg dest_path: Destination path.
    :kwarg check_content: If ``True`` (default) and ``lib_ctx.file_check_content > 0`` and the
        destination file exists, first check whether source and destination are potentially equal
        before actually copying,
    """
    lib_ctx = app_context.lib_ctx.get()
    await _copy_file(
        source_path,
        dest_path,
        check_content=check_content,
        file_check_content=lib_ctx.file_check_content,
        chunksize=lib_ctx.chunksize,
    )


async def write_file(filename: StrOrBytesPath, content: str) -> None:
    lib_ctx = app_context.lib_ctx.get()
    await _write_file(filename, content, file_check_content=lib_ctx.file_check_content)


async def read_file(filename: StrOrBytesPath, encoding: str = "utf-8") -> str:
    return await _read_file(filename, encoding=encoding)
