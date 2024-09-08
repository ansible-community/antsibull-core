# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2020, Ansible Project
"""Functions to work with Galaxy."""

from __future__ import annotations

import dataclasses
import os.path
import typing as t
from enum import Enum
from urllib.parse import urljoin

import aiofiles
import semantic_version as semver
from antsibull_fileutils.hashing import verify_hash
from antsibull_fileutils.io import copy_file

from . import app_context
from .utils.http import retry_get

# The type checker can handle finding aiohttp.client but flake8 cannot :-(
if t.TYPE_CHECKING:
    import aiohttp.client
    from _typeshed import StrPath


class NoSuchCollection(Exception):
    """Collection name does not map to a collection on Galaxy."""


class NoSuchVersion(Exception):
    """Version does not match with any versions of a collection on Galaxy."""


class DownloadFailure(Exception):
    """Failure downloading a collection from Galaxy."""


class DownloadResults(t.NamedTuple):
    """Results of downloading a collection."""

    #: :obj:`semantic_version.Version` of the exact version of the collection that was downloaded.
    version: semver.Version
    #: Location on the filesystem of the downloaded collection.
    download_path: str


class GalaxyVersion(Enum):
    V2 = 2
    V3 = 3


@dataclasses.dataclass
class GalaxyContext:
    server: str
    version: GalaxyVersion
    base_url: str

    @classmethod
    async def create(
        cls,
        aio_session: aiohttp.client.ClientSession,
        galaxy_server: t.Optional[str] = None,
    ) -> GalaxyContext:
        """
        Create a new Galaxy context.

        :arg aio_session: A ``aiohttp.client.ClientSession`` object.
        :kwarg galaxy_server: A Galaxy server URL. Defaults to ``lib_ctx.get().galaxy_url``.
        """
        if galaxy_server is None:
            galaxy_server = str(app_context.lib_ctx.get().galaxy_url)
        api_url = urljoin(galaxy_server, "api/")
        async with retry_get(
            aio_session, api_url, headers={"Accept": "application/json"}
        ) as response:
            galaxy_info = await response.json()
        available_versions: t.Mapping[str, str] = (
            galaxy_info.get("available_versions") or {}
        )
        if "v3" in available_versions:
            version = GalaxyVersion.V3
            base_url = urljoin(galaxy_server, "api/" + available_versions["v3"])
        elif "v2" in available_versions:
            version = GalaxyVersion.V2
            base_url = urljoin(galaxy_server, "api/" + available_versions["v2"])
        else:
            raise RuntimeError(
                f"Information retrieved from {api_url} seems to indicate"
                " neither Galaxy v2 API nor Galaxy v3 API"
            )
        return cls(galaxy_server, version, base_url)


class GalaxyClient:
    """Class for querying the Galaxy REST API."""

    def __init__(
        self,
        aio_session: aiohttp.client.ClientSession,
        *,
        context: GalaxyContext,
    ) -> None:
        """
        Create a GalaxyClient object to query the Galaxy Server.

        :arg aio_session: :obj:`aiohttp.ClientSession` with which to perform all
            requests to galaxy.
        :kwarg context: A ``GalaxyContext`` instance. Must be provided.
        """
        if context is None:
            raise ValueError(
                "The context parameter must be provided to the GalaxyClient constructor"
            )
        self.context = context
        self.aio_session = aio_session
        self.headers: dict[str, str] = {"Accept": "application/json"}
        self.params: dict[str, str] = {}
        if context:
            self._update_from_context(context)

    def _update_from_context(self, context: GalaxyContext) -> None:
        if context.version == GalaxyVersion.V2:
            self.params["format"] = "json"

    async def _get_galaxy_versions(
        self, context: GalaxyContext, versions_url: str, add_params: bool = True
    ) -> list[str]:
        """
        Retrieve the complete list of versions for a collection from a galaxy endpoint.

        This internal function retrieves versions for collections from a Galaxy endpoint.  If the
        information is paged, it continues to retrieve linked pages until all of the information has
        been returned.

        :arg context: the ``GalaxyContext`` to use.
        :arg version_url: url to the page to retrieve.
        :arg add_params: used internally during recursion. Do not specify when calling this.
        :returns: List of the all the versions of the collection.
        """
        if add_params:
            params = self.params.copy()
            if context.version == GalaxyVersion.V2:
                params["page_size"] = "100"
            else:
                params["limit"] = "50"
        else:
            params = None
        async with retry_get(
            self.aio_session,
            versions_url,
            params=params,
            headers=self.headers,
            acceptable_error_codes=[404],
        ) as response:
            if response.status == 404:
                raise NoSuchCollection(f"No collection found at: {versions_url}")
            collection_info = await response.json()

        versions = []
        if context.version == GalaxyVersion.V2:
            results = collection_info["results"]
            next_link = collection_info["next"]
        else:
            if "data" in collection_info:
                # Apparently 'data' isn't always used...
                results = collection_info["data"]
            else:
                results = collection_info["results"]
            next_link = collection_info["links"]["next"]
            add_params = False
        for version_record in results:
            versions.append(version_record["version"])
        if next_link:
            if next_link.startswith("/"):
                next_link = urljoin(context.server, next_link)
            versions.extend(
                await self._get_galaxy_versions(context, next_link, add_params)
            )

        return versions

    async def get_versions(self, collection: str) -> list[str]:
        """
        Retrieve all versions of a collection on Galaxy.

        :arg collection: Name of the collection to get version info for.
        :returns: List of all the versions of this collection on galaxy.
        """
        context = self.context

        collection = collection.replace(".", "/")
        galaxy_url = urljoin(context.base_url, f"collections/{collection}/versions/")
        retval = await self._get_galaxy_versions(context, galaxy_url)
        return retval

    async def get_info(self, collection: str) -> dict[str, t.Any]:
        """
        Retrieve information about the collection on Galaxy.

        :arg collection: Namespace.collection to retrieve information about.
        :returns: Dictionary of information about the collection.

        Please see the Galaxy v2 and v3 REST API documentation for information on the
        structure of the returned data.

        .. seealso::
            An example return value from the
            `Galaxy v2 REST API
            <https://galaxy.ansible.com/api/v2/collections/community/general/>`_
            and the `Galaxy v3 REST API
            <https://beta-galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/community/general/>`_
        """
        context = self.context

        collection = collection.replace(".", "/")
        galaxy_url = urljoin(context.base_url, f"collections/{collection}/")

        async with retry_get(
            self.aio_session,
            galaxy_url,
            params=self.params,
            headers=self.headers,
            acceptable_error_codes=[404],
        ) as response:
            if response.status == 404:
                raise NoSuchCollection(f"No collection found at: {galaxy_url}")
            collection_info = await response.json()

        return collection_info

    async def get_release_info(
        self, collection: str, version: str | semver.Version
    ) -> dict[str, t.Any]:
        """
        Retrive information about a specific version of a collection.

        :arg collection: Namespace.collection string naming the collection.
        :arg version: Version of the collection.
        :returns: Dictionary of information about the release.

        Please see the Galaxy v2 and v3 REST API documentation for information on the
        structure of the returned data.

        .. seealso::
            An example return value from the
            `Galaxy v2 REST API
            <https://galaxy.ansible.com/api/v2/collections/community/general/versions/0.1.1>`_
            and the `Galaxy v3 REST API
            <https://beta-galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/community/general/versions/0.1.1/>`_
        """
        context = self.context

        collection = collection.replace(".", "/")
        galaxy_url = urljoin(
            context.base_url, f"collections/{collection}/versions/{version}/"
        )

        async with retry_get(
            self.aio_session,
            galaxy_url,
            params=self.params,
            headers=self.headers,
            acceptable_error_codes=[404],
        ) as response:
            if response.status == 404:
                raise NoSuchCollection(f"No collection found at: {galaxy_url}")
            collection_info = await response.json()

        return collection_info

    async def get_latest_matching_version(
        self, collection: str, version_spec: str, pre: bool = False
    ) -> semver.Version:
        """
        Get the latest version of a collection that matches a specification.

        :arg collection: Namespace.collection identifying a collection.
        :arg version_spec: String specifying the allowable versions.
        :kwarg pre: If True, allow prereleases (versions which have the form X.Y.Z.SOMETHING).
            This is **not** for excluding 0.Y.Z versions.  non-pre-releases are still
            preferred over pre-releases (for instance, with version_spec='>2.0.0-a1,<3.0.0'
            and pre=True, if the available versions are 2.0.0-a1 and 2.0.0-a2, then 2.0.0-a2
            will be returned.  If the available versions are 2.0.0 and 2.1.0-b2, 2.0.0 will be
            returned since non-pre-releases are preferred.  The default is False
        :returns: :obj:`semantic_version.Version` of the latest collection version that satisfied
            the specification.

        .. seealso:: For the format of the version_spec, see the documentation
            of :obj:`semantic_version.SimpleSpec`

        .. versionchanged:: 0.37.0
            Giving True to the ``pre`` parameter now means that prereleases will be
            *allowed* but stable releases will still be *preferred*.  Previously, the
            latest release, whether stable or prerelease was returned when pre was True.
        """
        versions = await self.get_versions(collection)
        sem_versions = [semver.Version(v) for v in versions]
        sem_versions.sort(reverse=True)

        spec = semver.SimpleSpec(version_spec)
        prereleases = []
        for version in (v for v in sem_versions if v in spec):
            # If this is a pre-release, first check if there's a non-pre-release that
            # will satisfy the version_spec.
            if version.prerelease:
                prereleases.append(version)
                continue
            return version

        # We did not find a stable version that satisies the version_spec.  If we
        # allow prereleases, return the latest of those here.
        if pre and prereleases:
            return prereleases[0]

        # No matching versions were found
        raise NoSuchVersion(
            f"{version_spec} did not match with any version of {collection}."
        )


class CollectionDownloader(GalaxyClient):
    """Manage downloading collections from Galaxy."""

    def __init__(
        self,
        aio_session: aiohttp.client.ClientSession,
        download_dir: StrPath,
        *,
        collection_cache: str | None = None,
        context: GalaxyContext,
        trust_collection_cache: t.Optional[bool] = None,
    ) -> None:
        """
        Create an object to download collections from galaxy.

        :arg aio_session: :obj:`aiohttp.ClientSession` with which to perform all
            requests to galaxy.
        :arg download_dir: Directory to download into.
        :kwarg context: A ``GalaxyContext`` instance. Must be provided.
        :kwarg collection_cache: If given, a path to a directory containing collection tarballs.
            These tarballs will be used instead of downloading new tarballs provided that the
            versions match the criteria (latest compatible version known to galaxy).
            Defaults to ``lib_ctx.get().collection_cache``.
        :kwarg trust_collection_cache: If set to ``True``, will assume that if the collection
            cache contains an artifact, it is the current one available on the Galaxy server.
            This avoids making a request to the Galaxy server to figure out the artifact's
            checksum and comparing it before trusting the cached artifact.
        """
        super().__init__(aio_session, context=context)
        self.download_dir = download_dir
        lib_ctx = app_context.lib_ctx.get()
        if collection_cache is None:
            collection_cache = lib_ctx.collection_cache
        self.collection_cache: t.Final[str | None] = collection_cache
        if trust_collection_cache is None:
            trust_collection_cache = lib_ctx.trust_collection_cache
        self.trust_collection_cache: t.Final[bool] = trust_collection_cache

    async def download(
        self,
        collection: str,
        version: str | semver.Version,
    ) -> str:
        """
        Download a collection.

        Downloads the collection at the specified version.

        :arg collection: Namespace.collection identifying the collection.
        :arg version: Version of the collection to download.
        :returns: The full path to the downloaded collection.
        """
        namespace, name = collection.split(".", 1)
        filename = f"{namespace}-{name}-{version}.tar.gz"
        download_filename = os.path.join(self.download_dir, filename)
        lib_ctx = app_context.lib_ctx.get()

        if self.collection_cache and self.trust_collection_cache:
            cached_copy = os.path.join(self.collection_cache, filename)
            if os.path.isfile(cached_copy):
                await copy_file(
                    cached_copy,
                    download_filename,
                    check_content=False,
                    file_check_content=lib_ctx.file_check_content,
                    chunksize=lib_ctx.chunksize,
                )
                return download_filename

        release_info = await self.get_release_info(f"{namespace}/{name}", version)
        release_url = release_info["download_url"]

        sha256sum = release_info["artifact"]["sha256"]

        if self.collection_cache:
            cached_copy = os.path.join(self.collection_cache, filename)
            if os.path.isfile(cached_copy):
                lib_ctx = app_context.lib_ctx.get()
                if await verify_hash(
                    cached_copy, sha256sum, chunksize=lib_ctx.chunksize
                ):
                    await copy_file(
                        cached_copy,
                        download_filename,
                        check_content=False,
                        file_check_content=lib_ctx.file_check_content,
                        chunksize=lib_ctx.chunksize,
                    )
                    return download_filename

        async with retry_get(
            self.aio_session, release_url, acceptable_error_codes=[404]
        ) as response:
            if response.status == 404:
                raise NoSuchCollection(f"No collection found at: {release_url}")

            async with aiofiles.open(download_filename, "wb") as f:
                lib_ctx = app_context.lib_ctx.get()
                while chunk := await response.content.read(lib_ctx.chunksize):
                    await f.write(chunk)

        # Verify the download
        if not await verify_hash(
            download_filename, sha256sum, chunksize=lib_ctx.chunksize
        ):
            raise DownloadFailure(
                f"{release_url} failed to download correctly."
                f" Expected checksum: {sha256sum}"
            )

        # Copy downloaded collection into cache
        if self.collection_cache:
            cached_copy = os.path.join(self.collection_cache, filename)
            await copy_file(
                download_filename,
                cached_copy,
                check_content=False,
                file_check_content=lib_ctx.file_check_content,
                chunksize=lib_ctx.chunksize,
            )

        return download_filename

    async def download_latest_matching(
        self, collection: str, version_spec: str
    ) -> DownloadResults:
        """
        Download the latest version of a collection that matches a specification.

        :arg collection: Namespace.collection identifying a collection.
        :arg version_spec: String specifying the allowable versions.
        :returns: :obj:`DownloadResults` with version and download path for the collection we
            downloaded.

        .. seealso:: For the format of the version_spec, see the documentation
            of :obj:`semantic_version.SimpleSpec`
        """
        version = await self.get_latest_matching_version(collection, version_spec)
        download_path = await self.download(collection, version)
        return DownloadResults(version=version, download_path=download_path)
