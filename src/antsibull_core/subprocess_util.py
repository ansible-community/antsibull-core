# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Utilities for dealing with subprocesses
"""

from __future__ import annotations

import asyncio
import subprocess
from asyncio.exceptions import IncompleteReadError, LimitOverrunError
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, cast

from antsibull_core.logging import log

if TYPE_CHECKING:
    from logging import Logger as StdLogger

    from _typeshed import StrOrBytesPath
    from twiggy.logger import Logger as TwiggyLogger  # type: ignore[import]

mlog = log.fields(mod=__name__)

CalledProcessError = subprocess.CalledProcessError


async def _stream_log(
    name: str,
    callback: Callable[[str], Any] | None,
    stream: asyncio.StreamReader,
    errors: str,
) -> str:
    # We do not simply use stream.readline() since it has a line length limit.
    # While we set this limit already to 8 MB (the default is 64 KB), we still
    # want to cover longer lines as well, so we use stream.readuntil('\n')
    # and manually handle the case of longer lines.
    lines = []
    line_parts = []
    sep = b"\n"
    while True:
        try:
            line_parts.append(await stream.readuntil(sep))
        except IncompleteReadError as e:
            line_parts.append(e.partial)
        except LimitOverrunError as e:
            part = await stream.read(e.consumed)
            line_parts.append(part)
            if part:
                continue

        line = b"".join(line_parts)
        line_parts.clear()
        if not line:
            break
        text = line.decode("utf-8", errors=errors)
        if callback:
            callback(f"{name}: {text.strip()}")
        lines.append(text)
    return "".join(lines)


async def async_log_run(
    args: Sequence[StrOrBytesPath],
    logger: TwiggyLogger | StdLogger | None = None,
    stdout_loglevel: str | None = None,
    stderr_loglevel: str | None = "debug",
    check: bool = True,
    *,
    errors: str = "strict",
    **kwargs,
) -> subprocess.CompletedProcess[str]:
    """
    Asynchronously run a command in a subprocess and log its output.
    The command's stdout and stderr are always captured.
    For some usecases, you may still need to call
    asyncio.create_subprocess_exec() directly to have more control.

    :param args: Command to run
    :param logger:
        Logger in which to log the command. Can be a `twiggy.logger.Logger` or
        a stdlib `logger.Logger`.
    :param stdout_loglevel: Which level to use to log stdout. `None` disables logging.
    :param stderr_loglevel: Which level to use to log stderr. `None` disables logging.
    :param check:
        Whether to raise a `subprocess.CalledProcessError` when the
        command returns a non-zero exit code
    :param errors:
        How to handle UTF-8 decoding errors. Default is ``strict``.
    """
    logger = logger or mlog
    stdout_logfunc: Callable[[str], Any] | None = None
    if stdout_loglevel:
        stdout_logfunc = getattr(logger, stdout_loglevel)
    stderr_logfunc: Callable[[str], Any] | None = None
    if stderr_loglevel:
        stderr_logfunc = getattr(logger, stderr_loglevel)

    logger.debug(f"Running subprocess: {args!r}")
    kwargs["stdout"] = asyncio.subprocess.PIPE
    kwargs["stderr"] = asyncio.subprocess.PIPE
    kwargs["limit"] = 2**23  # Increase line length limit to 8 MB (the default is 64k)
    proc = await asyncio.create_subprocess_exec(*args, **kwargs)
    stdout, stderr = await asyncio.gather(
        # proc.stdout and proc.stderr won't be None with PIPE, hence the cast()
        asyncio.create_task(
            _stream_log(
                "stdout",
                stdout_logfunc,
                cast(asyncio.StreamReader, proc.stdout),
                errors,
            )
        ),
        asyncio.create_task(
            _stream_log(
                "stderr",
                stderr_logfunc,
                cast(asyncio.StreamReader, proc.stderr),
                errors,
            )
        ),
    )
    returncode = await proc.wait()

    completed = subprocess.CompletedProcess(
        args=args, returncode=returncode, stdout=stdout, stderr=stderr
    )
    if check:
        completed.check_returncode()
    return completed


def log_run(
    args: Sequence[StrOrBytesPath],
    logger: TwiggyLogger | StdLogger | None = None,
    stdout_loglevel: str | None = None,
    stderr_loglevel: str | None = "debug",
    check: bool = True,
    **kwargs,
) -> subprocess.CompletedProcess[str]:
    """
    Synchronous wrapper for the async_log_run function.
    This function runs a command in a subprocess and captures and logs its
    output.
    """
    return asyncio.run(
        async_log_run(args, logger, stdout_loglevel, stderr_loglevel, check, **kwargs)
    )


__all__ = ("async_log_run", "log_run", "CalledProcessError")
