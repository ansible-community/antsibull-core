# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2020, Ansible Project
"""Functions to help with hashing."""

import hashlib

import aiofiles

from .. import app_context


async def verify_hash(filename: str, hash_digest: str, algorithm: str = 'sha256') -> bool:
    """
    Verify whether a file has a given sha256sum.

    :arg filename: The file to verify the sha256sum of.
    :arg hash_digest: The hash that is expected.
    :kwarg algorithm: The hash algorithm to use.  This must be present in hashlib on this
        system.  The default is 'sha256'
    :returns: True if the hash matches, otherwise False.
    """
    hasher = getattr(hashlib, algorithm)()
    async with aiofiles.open(filename, 'rb') as f:
        ctx = app_context.lib_ctx.get()
        # TODO: PY3.8: while chunk := await f.read(ctx.chunksize):
        chunk = await f.read(ctx.chunksize)
        while chunk:
            hasher.update(chunk)
            chunk = await f.read(ctx.chunksize)
    if hasher.hexdigest() != hash_digest:
        return False

    return True
