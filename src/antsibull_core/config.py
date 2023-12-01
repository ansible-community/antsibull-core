# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2020, Ansible Project
"""Functions to handle config files."""

from __future__ import annotations

import os.path
import typing as t
from collections.abc import Iterable, Mapping, Sequence

import perky  # type: ignore[import]
import pydantic as p

from .logging import log
from .schemas.context import AppContext, LibContext

if t.TYPE_CHECKING:
    from _typeshed import StrPath

mlog = log.fields(mod=__name__)

#: System config file location.
SYSTEM_CONFIG_FILE = "/etc/antsibull.cfg"

#: Per-user config file location.
USER_CONFIG_FILE = "~/.antsibull.cfg"


class ConfigError(Exception):
    pass


def find_config_files(conf_files: Iterable[StrPath]) -> list[str]:
    """
    Find all config files that exist.

    :arg conf_files: An iterable of config filenames to search for.
    :returns: A List of filenames which actually existed on the system.
    """
    flog = mlog.fields(func="find_config_file")
    flog.fields(conf_files=conf_files).debug("Enter")

    paths = [
        os.path.abspath(p)  # pyre-ignore[6]: abspath() accepts path-like object
        for p in conf_files
    ]
    flog.fields(paths=paths).info("Paths to check")

    config_files = []
    for conf_path in paths:
        if os.path.exists(conf_path):
            config_files.append(str(conf_path))
    flog.fields(paths=config_files).info("Paths found")

    flog.debug("Leave")
    return config_files


def validate_config(
    config: Mapping,
    filenames: Sequence[StrPath],
    app_context_model: type[AppContext],
) -> None:
    """
    Validate configuration.

    Given the configuration loaded from one or more configuration files and the app context model,
    splits up the config into lib context and app context part and validates both parts with the
    given model. Raises a :obj:`ConfigError` if validation fails.
    """
    lib_fields = set(LibContext.model_fields)
    lib = {}
    app = {}
    for key, value in config.items():
        if key in lib_fields:
            lib[key] = value
        else:
            app[key] = value
    # Note: We parse the object but discard the model because we want to validate the config but let
    # the context handle all setting of defaults
    try:
        LibContext.model_validate(lib)
        app_context_model.model_validate(app)
    except p.ValidationError as exc:
        joined_filenames = ", ".join(f"{fn}" for fn in filenames)
        raise ConfigError(
            f"Error while parsing configuration from {joined_filenames}:\n{exc}"
        ) from exc


def _load_config_file(filename: StrPath) -> Mapping:
    """
    Load configuration from one file and return the raw data.
    """
    try:
        return perky.load(filename)
    except OSError as exc:
        raise ConfigError(
            f"Error while loading configuration from {filename}: {exc}"
        ) from exc
    except perky.PerkyFormatError as exc:
        raise ConfigError(
            f"Error while parsing configuration from {filename}:\n{exc}"
        ) from exc


def load_config(
    conf_files: Iterable[str] | str | None = None,
    app_context_model: type[AppContext] = AppContext,
) -> dict:
    """
    Load configuration.

    Load configuration from all found conf files.  The default configuration is loaded
    followed by a system-wide location, user-location, and then any files specified in
    the ``conf_files`` parameter.  Toplevel keys in later files will overwrite earlier
    those same keys in earlier files.

    :arg conf_files: An iterable of conf_files to load configuration information from.
    :kwarg app_context_model: The model to use for the app context. Must be derived from
        :obj:`AppContext`. If not provided, will use :obj:`AppContext` itself.
    :returns: A dict containing the configuration.
    """
    flog = mlog.fields(func="load_config")
    flog.debug("Enter")

    if isinstance(conf_files, str):
        conf_files = (conf_files,)
    elif conf_files is None:
        conf_files = ()

    implicit_files = find_config_files(
        (SYSTEM_CONFIG_FILE, os.path.expanduser(USER_CONFIG_FILE))
    )
    explicit_files = find_config_files(conf_files)

    flog.fields(implicit_files=implicit_files, explicit_files=explicit_files).debug(
        "found config files"
    )

    flog.debug("loading implicit config files")
    cfg: dict = {}
    for filename in implicit_files:
        cfg.update(_load_config_file(filename))

    flog.debug("validating implicit configuration")
    validate_config(cfg, implicit_files, AppContext)

    flog.debug("loading explicit config files")
    for filename in explicit_files:
        cfg.update(_load_config_file(filename))

    flog.debug("validating combined configuration")
    validate_config(cfg, implicit_files + explicit_files, app_context_model)

    flog.fields(config=cfg).debug("Leave")
    return cfg
