# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2020, Ansible Project
"""Functions to help with hashing."""

from __future__ import annotations

import dataclasses
import hashlib
import typing as t
from collections.abc import Mapping

import aiofiles

from .. import app_context


@dataclasses.dataclass(frozen=True)
class _AlgorithmData:
    name: str
    algorithm: str
    kwargs: dict[str, t.Any]


_PREFERRED_HASHES: tuple[_AlgorithmData, ...] = (
    # https://pypi.org/help/#verify-hashes, https://github.com/pypi/warehouse/issues/9628
    _AlgorithmData(name="sha256", algorithm="sha256", kwargs={}),
    _AlgorithmData(name="blake2b_256", algorithm="blake2b", kwargs={"digest_size": 32}),
)


async def verify_hash(
    filename: str,
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
    hasher = getattr(hashlib, algorithm)(**(algorithm_kwargs or {}))
    async with aiofiles.open(filename, "rb") as f:
        ctx = app_context.lib_ctx.get()
        while chunk := await f.read(ctx.chunksize):
            hasher.update(chunk)
    if hasher.hexdigest() != hash_digest:
        return False

    return True


async def verify_a_hash(filename: str, hash_digests: Mapping[str, str]) -> bool:
    """
    Verify whether a file has a given hash, given a set of digests with different algorithms.
    Will only test trustworthy hashes and return ``False`` if none matches.

    :arg filename: The file to verify the hash of.
    :arg hash_digest: A mapping of hash types to digests.
    :returns: True if the hash matches, otherwise False.
    """
    for algorithm_data in _PREFERRED_HASHES:
        if algorithm_data.name in hash_digests:
            return await verify_hash(
                filename,
                hash_digests[algorithm_data.name],
                algorithm=algorithm_data.algorithm,
                algorithm_kwargs=algorithm_data.kwargs,
            )
    return False
