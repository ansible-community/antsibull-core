# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021, Toshio Kuratomi
"""Schemas for app and lib contexts."""

import typing as t
from functools import cached_property

import pydantic as p

from ..utils.collections import ContextDict
from .config import DEFAULT_LOGGING_CONFIG, LoggingModel
from .validators import convert_bool, convert_none, convert_path


class BaseModel(p.BaseModel):
    """
    Configuration for all Context object classes.

    :cvar model_config: Sets the following information

        :arg allow_mutation: ``False``.  Prevents setattr on the contexts.
        :arg extra: ``p.Extra.forbid``.  Prevents extra fields on the contexts.
        :arg validate_all: ``True``.  Validates default values as well as user supplied ones.
    """

    model_config = p.ConfigDict(frozen=True, extra="forbid", validate_default=True)


class AppContext(BaseModel):
    """
    Structure and defaults of the app_ctx.

    :ivar extra: a mapping of arg/config keys to values.  Anything in here is unchecked by a
        schema.  These are usually leftover command line arguments and config entries. If
        values stored in extras need default values, they need to be set outside of the context
        or the entries can be given an actual entry in the AppContext to take advantage of the
        schema's checking, normalization, and default setting.
    :ivar logging_cfg: Configuration of the application logging.
    """

    model_config = p.ConfigDict(frozen=True, extra="allow", validate_default=True)

    @cached_property
    def extra(self) -> ContextDict:
        d = (self.__pydantic_extra__ or {}).get("extra", {})
        return ContextDict.validate_and_convert(d)

    logging_cfg: LoggingModel = LoggingModel.model_validate(DEFAULT_LOGGING_CONFIG)


class LibContext(BaseModel):
    """
    Structure and defaults of the lib_ctx.

    :ivar chunksize: number of bytes to read or write at one time for network or file IO
    :ivar process_max: Maximum number of worker processes for parallel operations.  It may be None
        to mean, use all available CPU cores.
    :ivar thread_max: Maximum number of helper threads for parallel operations
    :ivar file_check_content: Maximum number of bytes of a file to read before writing it to
        compare contents. If contents are as expected, file is not overwritten. Set to 0 to
        disable.
    :ivar max_retries: Maximum number of times to retry an http request (in case of timeouts and
        other transient problems.
    :ivar ansible_core_repo_url: Url to the ansible-core git repo.
    :ivar galaxy_url: URL of the galaxy server to get collection info from
    :ivar logging_cfg: Configuration of the application logging
    :ivar pypi_url: URL of the pypi server to query for information
    :ivar collection_cache: If set, must be a path pointing to a directory where collection
        tarballs are cached so they do not need to be downloaded from Galaxy twice.
    :ivar trust_collection_cache: If set to ``True``, will assume that if the collection
        cache contains an artifact, it is the current one available on the Galaxy server.
        This avoids making a request to the Galaxy server to figure out the artifact's
        checksum and comparing it before trusting the cached artifact.
    :ivar ansible_core_cache: If set, must be a path pointing to a directory where ansible-core
        tarballs are cached so they do not need to be downloaded from PyPI twice.
    :ivar trust_ansible_core_cache: If set to ``True``, will assume that if the ansible-core
        cache contains an artifact, it is the current one available on PyPI. This avoids making a
        request to PyPI to figure out the artifact's checksum and comparing it before trusting
        the cached artifact.
    """

    chunksize: int = 4096

    max_retries: int = 10
    process_max: t.Optional[int] = None
    thread_max: int = 8
    file_check_content: int = 262144
    ansible_core_repo_url: p.HttpUrl = p.HttpUrl("https://github.com/ansible/ansible/")
    galaxy_url: p.HttpUrl = p.HttpUrl("https://galaxy.ansible.com/")
    pypi_url: p.HttpUrl = p.HttpUrl("https://pypi.org/")
    collection_cache: t.Optional[str] = None
    trust_collection_cache: bool = False
    ansible_core_cache: t.Optional[str] = None
    trust_ansible_core_cache: bool = False

    # pylint: disable-next=unused-private-member
    __convert_nones = p.field_validator("process_max", mode="before")(convert_none)
    # pylint: disable-next=unused-private-member
    __convert_paths = p.field_validator(
        "ansible_core_cache", "collection_cache", mode="before"
    )(convert_path)
    # pylint: disable-next=unused-private-member
    __convert_bools = p.field_validator(
        "trust_ansible_core_cache", "trust_collection_cache", mode="before"
    )(convert_bool)
