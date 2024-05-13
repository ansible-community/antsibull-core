# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2020, Ansible Project
"""Functionality to work with a venv."""

from __future__ import annotations

import asyncio
import os
import sys
import venv
from collections.abc import Sequence
from typing import TYPE_CHECKING, NoReturn

from antsibull_core import subprocess_util

if TYPE_CHECKING:
    import subprocess
    from logging import Logger as StdLogger

    from _typeshed import StrPath
    from twiggy.logger import Logger as TwiggyLogger  # type: ignore[import]


def get_clean_environment() -> dict[str, str]:
    env = os.environ.copy()
    try:
        del env["PYTHONPATH"]
    except KeyError:
        # We just wanted to make sure there was no PYTHONPATH set...
        # all python libs will come from the venv
        pass
    return env


class VenvRunner:
    """
    Makes running a command in a venv easy.

    Combines venv functionality with ``antsibull_core.subprocess_util``.

    .. seealso::
        * :python:mod:`venv`
    """

    name: str
    top_dir: StrPath
    venv_dir: str

    def __init__(self, name: str, top_dir: StrPath) -> None:
        """
        Create a venv.

        :arg name: Name of the venv.
        :arg top_dir: Directory the venv will be created inside of.
        """
        self.name = name
        self.top_dir = top_dir
        self.venv_dir: str = os.path.join(top_dir, name)
        venv.create(self.venv_dir, clear=True, symlinks=True, with_pip=True)

        # Upgrade pip to the latest version.
        # Note that cryptography stopped building manylinux1 wheels (the only ship manylinux2010) so
        # we need pip19+ in order to work now.  RHEL8 and Ubuntu 18.04 contain a pip that's older
        # than that so we must upgrade to something even if it's not latest.

        self.log_run(["pip", "install", "--upgrade", "pip"])

    def install_package(self, package_name: str) -> subprocess.CompletedProcess:
        """
        Install a python package into the venv.

        :arg package_name: This can be a bare package name or a path to a file.  It's passed
            directly to :command:`pip install`.
        :returns: An :obj:`subprocess.CompletedProcess` for the pip output.
        """
        return self.log_run(["pip", "install", package_name])

    async def async_log_run(
        self,
        args: Sequence[StrPath],
        logger: TwiggyLogger | StdLogger | None = None,
        stdout_loglevel: str | subprocess_util.OutputCallbackType | None = None,
        stderr_loglevel: str | subprocess_util.OutputCallbackType | None = "debug",
        check: bool = True,
        *,
        errors: str = "strict",
        **kwargs,
    ) -> subprocess.CompletedProcess[str]:
        """
        This method asynchronously runs a command in a subprocess and logs
        its output. It calls `antsibull_core.subprocess_util.async_log_run` to
        do the heavy lifting. `args[0]` must be a filename that's installed in
        the venv. If it's not, a `ValueError` will be raised.
        """
        kwargs.setdefault("env", get_clean_environment())
        basename = args[0]
        if os.path.isabs(basename):
            raise ValueError(f"{basename!r} must not be an absolute path!")
        path = os.path.join(self.venv_dir, "bin", basename)
        if not os.path.exists(path):
            raise ValueError(f"{path!r} does not exist!")
        args = [path, *args[1:]]
        return await subprocess_util.async_log_run(
            args,
            logger,
            stdout_loglevel,
            stderr_loglevel,
            check,
            errors=errors,
            **kwargs,
        )

    def log_run(
        self,
        args: Sequence[StrPath],
        logger: TwiggyLogger | StdLogger | None = None,
        stdout_loglevel: str | subprocess_util.OutputCallbackType | None = None,
        stderr_loglevel: str | subprocess_util.OutputCallbackType | None = "debug",
        check: bool = True,
        *,
        errors: str = "strict",
        **kwargs,
    ) -> subprocess.CompletedProcess[str]:
        """
        See :method:`async_log_run`
        """
        return asyncio.run(
            self.async_log_run(
                args,
                logger,
                stdout_loglevel,
                stderr_loglevel,
                check,
                errors=errors,
                **kwargs,
            )
        )


class FakeVenvRunner:
    """
    Simply runs commands.

    .. seealso::
        * :python:mod:`venv`
    """

    async def async_log_run(
        self,
        args: Sequence[StrPath],
        logger: TwiggyLogger | StdLogger | None = None,
        stdout_loglevel: str | None = None,
        stderr_loglevel: str | None = "debug",
        check: bool = True,
        *,
        errors: str = "strict",
        **kwargs,
    ) -> subprocess.CompletedProcess[str]:
        """
        This method asynchronously runs a command in a subprocess and logs its
        output.
        It works the same as `antsibull_core.subprocess_util.async_log_run`,
        but 'python' will be replaced by `sys.executable`.
        """
        if args and args[0] == "python":
            args = [sys.executable, *args[1:]]
        return await subprocess_util.async_log_run(
            args,
            logger,
            stdout_loglevel,
            stderr_loglevel,
            check,
            errors=errors,
            **kwargs,
        )

    def log_run(
        self,
        args: Sequence[StrPath],
        logger: TwiggyLogger | StdLogger | None = None,
        stdout_loglevel: str | None = None,
        stderr_loglevel: str | None = "debug",
        check: bool = True,
        *,
        errors: str = "strict",
        **kwargs,
    ) -> subprocess.CompletedProcess[str]:
        """
        See :method:`async_log_run`
        """
        return asyncio.run(
            self.async_log_run(
                args,
                logger,
                stdout_loglevel,
                stderr_loglevel,
                check,
                errors=errors,
                **kwargs,
            )
        )

    @staticmethod
    def install_package(package_name: str) -> NoReturn:
        """
        This raises a NotImplementedError and only exists for parity with
        `VenvRunner`.

        """
        raise NotImplementedError
