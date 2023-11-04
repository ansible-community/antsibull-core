# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2020, Ansible Project
"""Functions for working with tarballs."""

from __future__ import annotations

import re
import typing as t

from antsibull_core.subprocess_util import async_log_run

if t.TYPE_CHECKING:
    from _typeshed import StrPath

#: Regex to find toplevel directories in tar output
TOPLEVEL_RE: re.Pattern = re.compile("^[^/]+/$")


class InvalidTarball(Exception):
    """Raised when a requested version does not exist."""


async def unpack_tarball(tarname: StrPath, destdir: StrPath) -> str:
    """
    Unpack a tarball.

    :arg tarname: The tarball to unpack.
    :arg destdir: The destination to unpack into.
    :returns: Toplevel of the unpacked directory structure.  This will be
        a subdirectory of `destdir`.
    """
    tarname_str = str(tarname)
    manifest = await async_log_run(["tar", "-xzvf", tarname_str, f"-C{destdir}"])
    toplevel_dirs = [
        filename
        for filename in manifest.stdout.splitlines()
        if TOPLEVEL_RE.match(filename)
    ]

    if len(toplevel_dirs) != 1:
        raise InvalidTarball(
            f"The tarball {tarname} had more than a single toplevel dir"
        )

    expected_dirname = tarname_str[: -len(".tar.gz")]
    if toplevel_dirs[0] != expected_dirname:
        raise InvalidTarball(f"The directory in {tarname} was not {expected_dirname}")

    return toplevel_dirs[0]


async def pack_tarball(tarname: StrPath, directory: str) -> str:
    raise NotImplementedError("pack_tarball has not yet been implemented")
