# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2020, Ansible Project
"""Functions to help with hashing."""

from __future__ import annotations

import typing as t
from collections.abc import Mapping

from antsibull_fileutils.hashing import verify_a_hash as _verify_a_hash
from antsibull_fileutils.hashing import verify_hash as _verify_hash

from .. import app_context

if t.TYPE_CHECKING:
    from _typeshed import StrOrBytesPath


async def verify_hash(
    filename: StrOrBytesPath,
    hash_digest: str,
    algorithm: str = "sha256",
    algorithm_kwargs: dict[str, t.Any] | None = None,
) -> bool:
    """
    Verify whether a file has a given sha256sum.

    :arg filename: The file to verify the sha256sum of.
    :arg hash_digest: The hash that is expected.
    :kwarg algorithm: The hash algorithm to use.  This must be present in hashlib on this
        system.  The default is 'sha256'
    :kwarg algorithm_kwargs: Parameters to provide to the hash algorithm's constructor.
    :returns: True if the hash matches, otherwise False.
    """
    ctx = app_context.lib_ctx.get()
    return await _verify_hash(
        filename,
        hash_digest,
        algorithm=algorithm,
        algorithm_kwargs=algorithm_kwargs,
        chunksize=ctx.chunksize,
    )


async def verify_a_hash(
    filename: StrOrBytesPath, hash_digests: Mapping[str, str]
) -> bool:
    """
    Verify whether a file has a given hash, given a set of digests with different algorithms.
    Will only test trustworthy hashes and return ``False`` if none matches.

    :arg filename: The file to verify the hash of.
    :arg hash_digest: A mapping of hash types to digests.
    :returns: True if the hash matches, otherwise False.
    """
    ctx = app_context.lib_ctx.get()
    return await _verify_a_hash(filename, hash_digests, chunksize=ctx.chunksize)
