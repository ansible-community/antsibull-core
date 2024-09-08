# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2020, Ansible Project

"""Functions for working with the ansible-core package."""

from __future__ import annotations

import ast
import os
import re
import tempfile
import typing as t
from urllib.parse import urljoin

import aiofiles
from antsibull_fileutils.hashing import verify_a_hash
from antsibull_fileutils.io import copy_file
from packaging.version import Version as PypiVer

from . import app_context
from .logging import log
from .subprocess_util import async_log_run
from .utils.http import retry_get

if t.TYPE_CHECKING:
    import aiohttp.client
    from _typeshed import StrPath


mlog = log.fields(mod=__name__)


class UnknownVersion(Exception):
    """Raised when a requested version does not exist."""


class CannotBuild(Exception):
    """Raised when we can't figure out how to build a package."""


class AnsibleCorePyPiClient:
    """Class to retrieve information about ansible-core from Pypi."""

    def __init__(
        self,
        aio_session: "aiohttp.client.ClientSession",
        pypi_server_url: t.Optional[str] = None,
    ) -> None:
        """
        Initialize the AnsibleCorePypiClient class.

        :arg aio_session: :obj:`aiohttp.client.ClientSession` to make requests to pypi from.
        :kwarg pypi_server_url: URL to the pypi server to use. Defaults to
            ``lib_ctx.get().pypi_url``.
        """
        self.aio_session = aio_session
        if pypi_server_url is None:
            pypi_server_url = str(app_context.lib_ctx.get().pypi_url)
        self.pypi_server_url: str = pypi_server_url

    async def _get_json(self, query_url: str) -> dict[str, t.Any]:
        """
        JSON data from a url with retries and return the data as python data structures.
        """
        async with retry_get(self.aio_session, query_url) as response:
            pkg_info = await response.json()
        return pkg_info

    async def get_release_info(
        self, package_name: t.Optional[str] = None
    ) -> dict[str, t.Any]:
        """
        Retrieve information about releases of the ansible-core package from pypi.

        :arg package_name: Either 'ansible-core' or None.
        :returns: The dict which represents the release info keyed by version number.
            To examine the data structure, use::

                curl https://pypi.org/pypi/ansible-core/json| python3 -m json.tool
        """
        # Retrieve the ansible-core package info from pypi
        package_name = package_name or "ansible-core"
        query_url = urljoin(self.pypi_server_url, f"pypi/{package_name}/json")
        resp = await self._get_json(query_url)
        return resp["releases"]

    async def get_versions(self) -> list[PypiVer]:
        """
        Get the versions of the ansible-core package on pypi.

        :returns: A list of :pypkg:obj:`packaging.versioning.Version`s
            for all the versions on pypi, including prereleases.
        """
        flog = mlog.fields(func="AnsibleCorePyPiClient.get_versions")
        flog.debug("Enter")

        release_info = await self.get_release_info()
        versions = [PypiVer(r) for r in release_info]
        versions.sort(reverse=True)
        flog.fields(versions=versions).info("sorted list of ansible-core versions")

        flog.debug("Leave")
        return versions

    async def get_latest_version(self) -> PypiVer:
        """
        Get the latest version of ansible-core uploaded to pypi.

        :return: A :pypkg:obj:`packaging.versioning.Version` object representing the latest version
            of the package on pypi.  This may be a pre-release.
        """
        versions = await self.get_versions()
        return versions[0]

    # TODO(anyone): Make function less complex
    async def retrieve(  # noqa C901
        self, ansible_core_version: str, download_dir: StrPath
    ) -> str:
        """
        Get the release from pypi.

        :arg ansible_core_version: Version of ansible-core to download.
        :arg download_dir: Directory to download the tarball to.
        :returns: The name of the downloaded tarball.
        """
        package_name = "ansible-core"

        # https://github.com/pypa/setuptools/pull/4286
        # Newer setuptools versions perform dist filename normalization
        tar_filenames = (
            f"{package_name.replace('-', '_')}-{ansible_core_version}.tar.gz",
            f"{package_name}-{ansible_core_version}.tar.gz",
        )
        tar_filename = tar_filenames[0]
        tar_path = os.path.join(download_dir, tar_filename)

        lib_ctx = app_context.lib_ctx.get()
        if lib_ctx.ansible_core_cache and lib_ctx.trust_ansible_core_cache:
            for tar_filename in tar_filenames:
                cached_path = os.path.join(
                    t.cast(str, lib_ctx.ansible_core_cache), tar_filename
                )
                if os.path.isfile(cached_path):
                    tar_path = os.path.join(download_dir, tar_filename)
                    await copy_file(
                        cached_path,
                        tar_path,
                        check_content=False,
                        file_check_content=lib_ctx.file_check_content,
                        chunksize=lib_ctx.chunksize,
                    )
                    return tar_path

        release_info = await self.get_release_info(package_name)

        pypi_url = ""
        digests = {}
        for release in release_info[ansible_core_version]:
            if release["filename"] in tar_filenames:
                tar_filename = release["filename"]
                tar_path = os.path.join(download_dir, tar_filename)
                pypi_url = release["url"]
                digests = release["digests"]
                break
        else:  # for-else: http://bit.ly/1ElPkyg
            raise UnknownVersion(
                f"{package_name} {ansible_core_version} does not"
                f" exist on {self.pypi_server_url}"
            )

        if lib_ctx.ansible_core_cache and "sha256" in digests:
            cached_path = os.path.join(lib_ctx.ansible_core_cache, tar_filename)
            if os.path.isfile(cached_path):
                if await verify_a_hash(
                    cached_path, digests, chunksize=lib_ctx.chunksize
                ):
                    await copy_file(
                        cached_path,
                        tar_path,
                        check_content=False,
                        file_check_content=lib_ctx.file_check_content,
                        chunksize=lib_ctx.chunksize,
                    )
                    return tar_path

        async with retry_get(self.aio_session, pypi_url) as response:
            async with aiofiles.open(tar_path, "wb") as f:
                while chunk := await response.content.read(lib_ctx.chunksize):
                    await f.write(chunk)

        if lib_ctx.ansible_core_cache:
            cached_path = os.path.join(lib_ctx.ansible_core_cache, tar_filename)
            await copy_file(
                tar_path,
                cached_path,
                check_content=False,
                file_check_content=lib_ctx.file_check_content,
                chunksize=lib_ctx.chunksize,
            )

        return tar_path


def _get_source_version(ansible_core_source: StrPath) -> PypiVer:
    with open(
        os.path.join(ansible_core_source, "lib", "ansible", "release.py"),
        "r",
        encoding="utf-8",
    ) as f:
        root = ast.parse(f.read())

    # Find the version of the source
    source_version = None
    # Iterate backwards in case __version__ is assigned to multiple times
    for node in reversed(root.body):
        if isinstance(node, ast.Assign):
            for name in node.targets:
                # These attributes are dynamic so pyre cannot check them
                if name.id == "__version__":  # type: ignore[attr-defined] # pyre-ignore[16]
                    source_version = node.value.s  # type: ignore[attr-defined] # pyre-ignore[16]
                    break

        if source_version:
            break

    if not source_version:
        raise ValueError("Version was not found")

    return PypiVer(source_version)


def _version_is_devel(version: PypiVer) -> bool:
    dev_version = re.compile(".*[.]dev[0-9]+$")
    return bool(dev_version.match(version.public))


def source_is_devel(ansible_core_source: StrPath | None) -> bool:
    """
    :arg ansible_core_source: A path to an Ansible-core checkout or expanded sdist or None.
        This will be used instead of downloading an ansible-core package if the version matches
        with ``ansible_core_version``.
    :returns: True if the source looks like it is for the devel branch.
    """
    if ansible_core_source is None:
        return False

    try:
        source_version = _get_source_version(ansible_core_source)
    except Exception:  # pylint:disable=broad-except
        return False

    return _version_is_devel(source_version)


def source_is_correct_version(
    ansible_core_source: StrPath | None, ansible_core_version: PypiVer
) -> bool:
    """
    :arg ansible_core_source: A path to an Ansible-core checkout or expanded sdist or None.
        This will be used instead of downloading an ansible-core package if the version matches
        with ``ansible_core_version``.
    :arg ansible_core_version: Version of ansible-core to retrieve.
    :returns: True if the source is for a compatible version at or newer than the requested version
    """
    if ansible_core_source is None:
        return False

    try:
        source_version = _get_source_version(ansible_core_source)
    except Exception:  # pylint:disable=broad-except
        return False

    # If the source is a compatible version of ansible-core and it is the same or more recent than
    # the requested version then allow this.
    if (
        source_version.major == ansible_core_version.major
        and source_version.minor == ansible_core_version.minor
        and source_version.micro >= ansible_core_version.micro
    ):
        return True

    return False


async def checkout_from_git(
    download_dir: StrPath, repo_url: t.Optional[str] = None
) -> str:
    """
    Checkout the ansible-core git repo.

    :arg download_dir: Directory to checkout into.
    :kwarg: repo_url: The URL to the git repo. Defaults to
        ``lib_ctx.get().ansible_core_repo_url``.
    :return: The directory that ansible-core has been checked out to.
    """
    if repo_url is None:
        repo_url = str(app_context.lib_ctx.get().ansible_core_repo_url)
    ansible_core_dir = os.path.join(download_dir, "ansible-core")
    await async_log_run(["git", "clone", repo_url, ansible_core_dir])

    return ansible_core_dir


async def create_sdist(source_dir: StrPath, dest_dir: StrPath) -> str:
    """
    Create an sdist for the python package at a given path.

    :arg source_dir: the directory that the python package source is in.
    :arg dest_dir: the directory that the sdist will be written to/
    :returns: path to the sdist.
    """

    # Make a subdir of dest_dir for returning the dist in
    dist_dir_prefix = os.path.join(
        os.path.basename(
            source_dir  # pyre-ignore[6]: basename() accepts path-like object
        )
    )
    dist_dir = tempfile.mkdtemp(prefix=dist_dir_prefix, dir=dest_dir)

    try:
        await async_log_run(
            ["python", "-m", "build", "--sdist", "--outdir", dist_dir, source_dir],
            stderr_loglevel="warning",
        )
    except Exception as e:
        raise CannotBuild(  # pylint:disable=raise-missing-from
            f"Building {source_dir} failed: {e}"
        )

    dist_files = [f for f in os.listdir(dist_dir) if f.endswith("tar.gz")]
    if len(dist_files) != 1:
        if not dist_files:
            raise CannotBuild(f"Building {source_dir} did not create a tar.gz")

        raise CannotBuild(
            f"Building {source_dir} created more than one tar.gz files which is not"
            " yet supported."
        )

    return os.path.join(dist_dir, dist_files[0])


async def get_ansible_core(
    aio_session: "aiohttp.client.ClientSession",
    ansible_core_version: str,
    tmpdir: StrPath,
    ansible_core_source: StrPath | None = None,
) -> str:
    """
    Create an ansible-core directory of the requested version.

    :arg aio_session: :obj:`aiohttp.client.ClientSession` to make http requests with.
    :arg ansible_core_version: Version of ansible-core to retrieve.  If it is the special string
        ``@devel``, then we will retrieve ansible-core from its git repository.  If it is the
        special string ``@latest``, then we will retrieve the latest version from pypi.
    :arg tmpdir: Temporary directory use as a scratch area for downloading to and the place that the
        ansible-core directory should be placed in.
    :kwarg ansible_core_source: If given, a path to an ansible-core checkout or expanded sdist.
        This will be used instead of downloading an ansible-core package if the version matches
        with ``ansible_core_version``.
    """
    if ansible_core_version == "@devel":
        # is the source usable?
        if source_is_devel(ansible_core_source):
            # source_is_devel() protects against this.  This assert is to inform the type checker
            assert ansible_core_source is not None
            source_location: StrPath = ansible_core_source

        else:
            source_location = await checkout_from_git(tmpdir)

        # Create an sdist from the source that can be installed
        install_file = await create_sdist(source_location, tmpdir)
    else:
        pypi_client = AnsibleCorePyPiClient(aio_session)
        ansible_core_pypi_version: PypiVer
        if ansible_core_version == "@latest":
            ansible_core_pypi_version = await pypi_client.get_latest_version()
        else:
            ansible_core_pypi_version = PypiVer(ansible_core_version)

        # is the source the asked for version?
        if source_is_correct_version(ansible_core_source, ansible_core_pypi_version):
            assert ansible_core_source is not None
            # Create an sdist from the source that can be installed
            install_file = await create_sdist(ansible_core_source, tmpdir)
        else:
            install_file = await pypi_client.retrieve(
                ansible_core_pypi_version.public, tmpdir
            )

    return install_file
