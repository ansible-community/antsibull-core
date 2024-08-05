# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2020, Ansible Project
"""General functions for working with aiohttp."""

from __future__ import annotations

import asyncio
import math
import random
import typing as t
import warnings
from collections.abc import Iterable, Mapping

import aiohttp

from .. import app_context
from ..logging import log

mlog = log.fields(mod=__name__)


# Since Python 3.11 asyncio.TimeoutError is a deprecated alias of TimeoutError
_AsyncIoTimeoutError = getattr(asyncio, "TimeoutError", TimeoutError)  # pyre-ignore[16]


def _format_call(
    command: str, args: tuple[t.Any, ...], kwargs: Mapping[str, t.Any]
) -> str:
    arguments = [repr(a) for a in args] + [f"{k}={repr(v)}" for k, v in kwargs.items()]
    return f'aio_session.{command}({", ".join(arguments)})'


class RetryGetManager:
    response: aiohttp.ClientResponse | None

    def __init__(
        self,
        aio_session: aiohttp.client.ClientSession,
        args: tuple[t.Any, ...],
        kwargs: Mapping[str, t.Any],
        max_retries: int,
        acceptable_error_codes: Iterable[int],
    ):
        self.aio_session = aio_session
        self.args = args
        self.kwargs = kwargs
        self.max_retries = max_retries
        self.acceptable_error_codes = acceptable_error_codes
        self.call_string = _format_call("get", args, kwargs)
        self.response = None

    async def __aenter__(self) -> aiohttp.ClientResponse:
        flog = mlog.fields(func="RetryGetManager.__aenter__")
        flog.debug("Enter")

        errors = []
        for retry in range(self.max_retries):
            flog.debug("Execute {0}", self.call_string)
            wait_factor: float = 5
            try:
                response = await self.aio_session.get(  # pyre-ignore[16]
                    *self.args, **self.kwargs, timeout=aiohttp.ClientTimeout(total=20)
                )
                status_code = response.status
                flog.debug(f"Status code {status_code}")
                if status_code < 400 or status_code in self.acceptable_error_codes:
                    self.response = response
                    flog.debug("Leave")
                    return response
                status = str(status_code)
                response.close()
            except _AsyncIoTimeoutError:
                flog.trace()
                status = "timeout"
                wait_factor = 0.5
            except Exception as error:  # pylint:disable=broad-except
                flog.trace()
                status = str(error)

            errors.append(status)
            failed = retry + 1 == self.max_retries
            warnings.warn(
                f"{self.call_string} failed with status code {status}"
                f'{", finally failed." if failed else ", retrying..."}'
            )
            if failed:
                break

            await asyncio.sleep(
                math.pow(1.5, retry) * wait_factor + (0.5 + random.uniform(0, 1))
            )

        flog.debug("Raise error")
        raise RuntimeError(
            f"Repeated error when calling {self.call_string}: received status codes "
            f'{", ".join(errors)}'
        )

    async def __aexit__(self, exc_type, exc, tb) -> None:
        flog = mlog.fields(func="RetryGetManager.__aexit__")
        flog.debug("Enter")
        response = self.response
        self.response = None
        if response is not None:
            response.close()
        flog.debug("Leave")


def retry_get(
    aio_session: aiohttp.client.ClientSession,
    *args,
    acceptable_error_codes: Iterable[int] | None = None,
    max_retries: int | None = None,
    **kwargs,
) -> t.AsyncContextManager[aiohttp.ClientResponse]:
    # Handle default value for max_retries
    lib_ctx = app_context.lib_ctx.get()
    if max_retries is None:
        max_retries = lib_ctx.max_retries

    # Make sure max_retries is at least 1
    max_retries = max(max_retries, 1)

    return RetryGetManager(
        aio_session, args, kwargs, max_retries, acceptable_error_codes or ()
    )
