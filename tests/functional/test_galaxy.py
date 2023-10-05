# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Ansible Project

import hashlib

import aiohttp
import pytest

from antsibull_core.galaxy import (
    CollectionDownloader,
    GalaxyClient,
    GalaxyContext,
    GalaxyVersion,
)

KNOWN_CG_VERSIONS = [
    "6.4.0",
    "6.3.0",
    "6.2.0",
    "6.1.0",
    "6.0.1",
    "6.0.0",
    "6.0.0-a1",
    "5.8.6",
    "5.8.5",
    "5.8.4",
    "5.8.3",
    "5.8.2",
    "5.8.1",
    "5.8.0",
    "5.7.0",
    "5.6.0",
    "5.5.0",
    "5.4.0",
    "5.3.0",
    "5.2.0",
    "5.1.1",
    "5.1.0",
    "5.0.2",
    "5.0.1",
    "5.0.0",
    "5.0.0-a1",
    "4.8.9",
    "4.8.8",
    "4.8.7",
    "4.8.6",
    "4.8.5",
    "4.8.4",
    "4.8.3",
    "4.8.2",
    "4.8.1",
    "4.8.0",
    "4.7.0",
    "4.6.1",
    "4.6.0",
    "4.5.0",
    "4.4.0",
    "4.3.0",
    "4.2.0",
    "4.1.0",
    "4.0.2",
    "4.0.1",
    "4.0.0",
    "3.8.10",
    "3.8.9",
    "3.8.8",
    "3.8.7",
    "3.8.6",
    "3.8.5",
    "3.8.4",
    "3.8.3",
    "3.8.2",
    "3.8.1",
    "3.8.0",
    "3.7.0",
    "3.6.0",
    "3.5.0",
    "3.4.0",
    "3.3.2",
    "3.3.1",
    "3.3.0",
    "3.2.0",
    "3.1.0",
    "3.0.2",
    "3.0.1",
    "3.0.0",
    "2.5.9",
    "2.5.8",
    "2.5.7",
    "2.5.6",
    "2.5.5",
    "2.5.4",
    "2.5.3",
    "2.5.2",
    "2.5.1",
    "2.5.0",
    "2.4.0",
    "2.3.0",
    "2.2.0",
    "2.1.1",
    "2.1.0",
    "2.0.1",
    "2.0.0",
    "1.3.14",
    "1.3.13",
    "1.3.12",
    "1.3.11",
    "1.3.10",
    "1.3.9",
    "1.3.8",
    "1.3.7",
    "1.3.6",
    "1.3.5",
    "1.3.4",
    "1.3.3",
    "1.3.2",
    "1.3.1",
    "1.3.0",
    "1.2.0",
    "1.1.0",
    "1.0.0",
    "0.3.0-experimental.meta.redirects-3",
    "0.3.0-experimental.meta.redirects-2",
    "0.3.0-experimental.meta.redirects",
    "0.2.1",
    "0.2.0",
    "0.1.4",
    "0.1.1",
]


async def galaxy_client_test(
    aio_session: aiohttp.ClientSession,
    context: GalaxyContext,
    tmp_path_factory,
    skip_versions_test: bool = False,
    skip_download_test: bool = False,
) -> None:
    client = GalaxyClient(aio_session, context=context)

    # Check collection info
    cg_info = await client.get_info("community.general")
    print(cg_info)
    assert cg_info["name"] == "general"
    assert cg_info["deprecated"] is False

    # Check info on specific collection version
    cg_version = await client.get_release_info("community.general", "6.0.0")
    cg_version.pop("files", None)  # this is huge for Galaxy v3 API
    cg_version.pop("metadata", None)  # this is large for Galaxy v3 API
    print(cg_version)
    assert "download_url" in cg_version
    assert cg_version["artifact"]["filename"] == "community-general-6.0.0.tar.gz"
    assert cg_version["artifact"]["size"] == 2285782
    expected = "7c7ec856355078577b520f7432645754d75ad8e74a46e84d1ffee8fad80efc5c"
    assert cg_version["artifact"]["sha256"] == expected
    assert cg_version["namespace"]["name"] == "community"
    assert cg_version["collection"]["name"] == "general"
    assert cg_version["version"] == "6.0.0"

    # Check collection list
    if not skip_versions_test:
        cg_versions = await client.get_versions("community.general")
        print(cg_versions)
        for known_version in KNOWN_CG_VERSIONS:
            assert known_version in cg_versions

    # Download collection
    if not skip_download_test:
        download_path = tmp_path_factory.mktemp("download")
        cache_path = tmp_path_factory.mktemp("cache")
        downloader = CollectionDownloader(
            aio_session,
            str(download_path),
            collection_cache=str(cache_path),
            context=context,
        )
        path = await downloader.download("community.dns", "0.1.0")
        with open(path, "rb") as f:
            data = f.read()
        length = len(data)
        print(length)
        assert length == 133242
        m = hashlib.sha256()
        m.update(data)
        digest = m.hexdigest()
        expected = "2de9d40940536e65b35995a3f58dea7776de3f23f1a7ab865e0b3b8482d746b5"
        assert digest == expected

        # Try again, should hit cache
        path2 = await downloader.download("community.dns", "0.1.0")
        with open(path2, "rb") as f:
            data2 = f.read()
        assert path == path2
        assert data == data2


@pytest.mark.asyncio
async def test_galaxy_v2(tmp_path_factory):
    galaxy_url = "https://old-galaxy.ansible.com"
    async with aiohttp.ClientSession() as aio_session:
        context = await GalaxyContext.create(aio_session, galaxy_url)
        assert context.version == GalaxyVersion.V2
        assert context.base_url == galaxy_url + "/api/v2/"
        await galaxy_client_test(aio_session, context, tmp_path_factory)


@pytest.mark.asyncio
async def test_galaxy_v3(tmp_path_factory):
    galaxy_url = "https://galaxy.ansible.com"
    async with aiohttp.ClientSession() as aio_session:
        context = await GalaxyContext.create(aio_session, galaxy_url)
        assert context.version == GalaxyVersion.V3
        assert context.base_url == galaxy_url + "/api/v3/"
        await galaxy_client_test(aio_session, context, tmp_path_factory)
