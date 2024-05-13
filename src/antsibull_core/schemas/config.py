# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021, Ansible Project
"""Schemas for logging config."""

import os.path
import typing as t
from collections.abc import Callable, Mapping, MutableMapping, MutableSequence, Sequence

import pydantic as p
import twiggy.formats  # type: ignore[import]
import twiggy.outputs  # type: ignore[import]

#: Valid choices for a logging level field
LEVEL_CHOICES_F = p.Field(
    ..., pattern="^(CRITICAL|ERROR|WARNING|NOTICE|INFO|DEBUG|DISABLED)$"
)

#: Valid choice of the logging version field
VERSION_CHOICES_F = p.Field(..., pattern=r"1\.0")


#
# Configuration file schema
#


class BaseModel(p.BaseModel):
    model_config = p.ConfigDict(frozen=True, extra="forbid", validate_default=True)


class LogFiltersModel(BaseModel):
    filter: t.Union[str, Callable]
    args: Sequence[t.Any] = []
    kwargs: Mapping[str, t.Any] = {}


class LogEmitterModel(BaseModel):
    output_name: str
    level: str = LEVEL_CHOICES_F
    filters: list[LogFiltersModel] = []


class LogOutputModel(BaseModel):
    output: t.Union[str, Callable]
    args: Sequence[t.Any] = []
    format: t.Union[str, Callable] = twiggy.formats.line_format
    kwargs: Mapping[str, t.Any] = {}

    @p.field_validator("args")
    # pylint:disable=no-self-argument
    def expand_home_dir_args(
        cls, args_field: MutableSequence, info: p.ValidationInfo
    ) -> MutableSequence:
        """Expand tilde in the arguments of specific outputs."""
        values = info.data
        if values["output"] in ("twiggy.outputs.FileOutput", twiggy.outputs.FileOutput):
            if args_field:
                args_field[0] = os.path.expanduser(args_field[0])
        return args_field

    @p.field_validator("kwargs")
    # pylint:disable=no-self-argument
    def expand_home_dir_kwargs(
        cls, kwargs_field: MutableMapping, info: p.ValidationInfo
    ) -> MutableMapping:
        """Expand tilde in the keyword arguments of specific outputs."""
        values = info.data
        if values["output"] in ("twiggy.outputs.FileOutput", twiggy.outputs.FileOutput):
            if "name" in kwargs_field:
                kwargs_field["name"] = os.path.expanduser(kwargs_field["name"])
        return kwargs_field


class LoggingModel(BaseModel):
    emitters: t.Optional[dict[str, LogEmitterModel]] = {}
    incremental: bool = False
    outputs: t.Optional[dict[str, LogOutputModel]] = {}
    version: str = VERSION_CHOICES_F


#: Default logging configuration
DEFAULT_LOGGING_CONFIG = LoggingModel.model_validate(
    {
        "version": "1.0",
        "outputs": {
            "logfile": {
                "output": "twiggy.outputs.FileOutput",
                "args": ["~/antsibull.log"],
            },
            "stderr": {
                "output": "twiggy.outputs.StreamOutput",
                "format": "twiggy.formats.shell_format",
            },
        },
        "emitters": {
            "all": {"level": "INFO", "output_name": "logfile", "filters": []},
            "problems": {"level": "WARNING", "output_name": "stderr", "filters": []},
        },
    }
)
