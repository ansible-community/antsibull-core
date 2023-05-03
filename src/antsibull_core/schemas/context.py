# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021, Toshio Kuratomi
"""Schemas for app and lib contexts."""

import typing as t

import pydantic as p

from ..utils.collections import ContextDict
from .config import DEFAULT_LOGGING_CONFIG, LoggingModel
from .validators import convert_bool, convert_none, convert_path


class BaseModel(p.BaseModel):
    """
    Configuration for all Context object classes.

    :cvar Config: Sets the following information

        :cvar allow_mutation: ``False``.  Prevents setattr on the contexts.
        :cvar extra: ``p.Extra.forbid``.  Prevents extra fields on the contexts.
        :cvar validate_all: ``True``.  Validates default values as well as user supplied ones.
    """

    class Config:
        """
        Set default configuration for building the context models.

        :cvar allow_mutation: ``False``.  Prevents setattr on the contexts.
        :cvar extra: ``p.Extra.forbid``.  Prevents extra fields on the contexts.
        :cvar validate_all: ``True``.  Validates default values as well as user supplied ones.
        """

        allow_mutation = False
        extra = p.Extra.forbid
        validate_all = True


class AppContext(BaseModel):
    """
    Structure and defaults of the app_ctx.

    :ivar extra: a mapping of arg/config keys to values.  Anything in here is unchecked by a
        schema.  These are usually leftover command line arguments and config entries. If
        values stored in extras need default values, they need to be set outside of the context
        or the entries can be given an actual entry in the AppContext to take advantage of the
        schema's checking, normalization, and default setting.
    :ivar ansible_base_url: Url to the ansible-core git repo. DEPRECATED: use the field
        ``ansible_core_repo_url`` in library context instead.
    :ivar galaxy_url: URL of the galaxy server to get collection info from. DEPRECATED: use the
        field of the same name in library context instead.
    :ivar logging_cfg: Configuration of the application logging.
    :ivar pypi_url: URL of the pypi server to query for information. DEPRECATED: use the field
        of the same name in library context instead.
    :ivar collection_cache: If set, must be a path pointing to a directory where collection
        tarballs are cached so they do not need to be downloaded from Galaxy twice. DEPRECATED:
        use the field of the same name in library context instead.
    """

    extra: ContextDict = ContextDict()

    # DEPRECATED: ansible_base_url will be removed in antsibull-core 3.0.0.
    # pyre-ignore[8]: https://github.com/samuelcolvin/pydantic/issues/1684
    ansible_base_url: p.HttpUrl = "https://github.com/ansible/ansible/"  # type: ignore[assignment]

    # DEPRECATED: galaxy_url will be removed in antsibull-core 3.0.0.
    # pyre-ignore[8]: https://github.com/samuelcolvin/pydantic/issues/1684
    galaxy_url: p.HttpUrl = "https://galaxy.ansible.com/"  # type: ignore[assignment]

    logging_cfg: LoggingModel = LoggingModel.parse_obj(DEFAULT_LOGGING_CONFIG)

    # DEPRECATED: pypi_url will be removed in antsibull-core 3.0.0.
    # pyre-ignore[8]: https://github.com/samuelcolvin/pydantic/issues/1684
    pypi_url: p.HttpUrl = "https://pypi.org/"  # type: ignore[assignment]

    # DEPRECATED: collection_cache will be removed in antsibull-core 3.0.0.
    collection_cache: t.Optional[str] = None

    # pylint: disable-next=unused-private-member
    __convert_paths = p.validator("collection_cache", pre=True, allow_reuse=True)(
        convert_path
    )


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
    :ivar doc_parsing_backend: The backend to use for parsing the documentation strings from
        plugins.  This is DEPRECATED and will be removed from the library context in
        antsibull-core 3.0.0.
        'auto' selects a backend depending on the ansible-core version.
        'ansible-internal' is the fastest, but does not work with ansible-core 2.13+.
        'ansible-core-2.13' is also very fast, but requires ansible-core 2.13+.
        'ansible-doc' exists in case of problems with the ansible-internal backend.
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

    # DEPRECATED: doc_parsing_backend will be removed in antsibull-core 3.0.0
    doc_parsing_backend: str = "auto"

    max_retries: int = 10
    process_max: t.Optional[int] = None
    thread_max: int = 8
    file_check_content: int = 262144
    # pyre-ignore[8]: https://github.com/samuelcolvin/pydantic/issues/1684
    ansible_core_repo_url: p.HttpUrl = (
        "https://github.com/ansible/ansible/"  # type: ignore[assignment]
    )
    # pyre-ignore[8]: https://github.com/samuelcolvin/pydantic/issues/1684
    galaxy_url: p.HttpUrl = "https://galaxy.ansible.com/"  # type: ignore[assignment]
    # pyre-ignore[8]: https://github.com/samuelcolvin/pydantic/issues/1684
    pypi_url: p.HttpUrl = "https://pypi.org/"  # type: ignore[assignment]
    collection_cache: t.Optional[str] = None
    trust_collection_cache: bool = False
    ansible_core_cache: t.Optional[str] = None
    trust_ansible_core_cache: bool = False

    # pylint: disable-next=unused-private-member
    __convert_nones = p.validator("process_max", pre=True, allow_reuse=True)(
        convert_none
    )
    # pylint: disable-next=unused-private-member
    __convert_paths = p.validator(
        "ansible_core_cache", "collection_cache", pre=True, allow_reuse=True
    )(convert_path)
    # pylint: disable-next=unused-private-member
    __convert_bools = p.validator(
        "trust_ansible_core_cache", "trust_collection_cache", pre=True, allow_reuse=True
    )(convert_bool)
