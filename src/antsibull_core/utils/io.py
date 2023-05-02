# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021, Ansible Project
"""I/O helper functions."""

from __future__ import annotations

import os
import os.path
import typing as t

import aiofiles

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
    flog = mlog.fields(func="copy_file")
    flog.debug("Enter")

    lib_ctx = app_context.lib_ctx.get()
    if check_content and lib_ctx.file_check_content > 0:
        # Check whether the destination file exists and has the same content as the source file,
        # in which case we won't overwrite the destination file
        try:
            stat_d = os.stat(dest_path)
            if stat_d.st_size <= lib_ctx.file_check_content:
                stat_s = os.stat(source_path)
                if stat_d.st_size == stat_s.st_size:
                    # Read both files and compare
                    async with aiofiles.open(source_path, "rb") as f_in:
                        content_to_copy = await f_in.read()
                    async with aiofiles.open(dest_path, "rb") as f_in:
                        existing_content = await f_in.read()
                    if content_to_copy == existing_content:
                        flog.debug("Skipping copy, since files are identical")
                        return
                    # Since we already read the contents of the file to copy, simply write it to
                    # the destination instead of reading it again
                    async with aiofiles.open(dest_path, "wb") as f_out:
                        await f_out.write(content_to_copy)
                    return
        except FileNotFoundError:
            # Destination (or source) file does not exist
            pass

    async with aiofiles.open(source_path, "rb") as f_in:
        async with aiofiles.open(dest_path, "wb") as f_out:
            while chunk := await f_in.read(lib_ctx.chunksize):
                await f_out.write(chunk)

    flog.debug("Leave")


async def write_file(filename: StrOrBytesPath, content: str) -> None:
    flog = mlog.fields(func="write_file")
    flog.debug("Enter")

    content_bytes = content.encode("utf-8")

    lib_ctx = app_context.lib_ctx.get()
    if (
        lib_ctx.file_check_content > 0
        and len(content_bytes) <= lib_ctx.file_check_content
    ):
        # Check whether the destination file exists and has the same content as the one we want to
        # write, in which case we won't overwrite the file
        try:
            stat = os.stat(filename)
            if stat.st_size == len(content_bytes):
                # Read file and compare
                async with aiofiles.open(filename, "rb") as f:
                    existing_content = await f.read()
                if existing_content == content_bytes:
                    flog.debug(
                        "Skipping write, since file already contains the exact content"
                    )
                    return
        except FileNotFoundError:
            # Destination file does not exist
            pass

    async with aiofiles.open(filename, "wb") as f:
        await f.write(content_bytes)

    flog.debug("Leave")


async def read_file(filename: StrOrBytesPath, encoding: str = "utf-8") -> str:
    flog = mlog.fields(func="read_file")
    flog.debug("Enter")

    async with aiofiles.open(filename, "r", encoding=encoding) as f:
        content = await f.read()

    flog.debug("Leave")
    return content
