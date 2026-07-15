# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Ansible Project

from __future__ import annotations

import ast

import pytest
from packaging.version import Version

import antsibull_core.ansible_core as ac


@pytest.mark.parametrize(
    "version, is_devel",
    [
        ("2.14.0dev0", True),
        ("2.14.0", False),
    ],
)
def test_get_core_package_name_returns_ansible_core(version, is_devel):
    assert ac._version_is_devel(Version(version)) == is_devel


TEST__EXTRACT_SOURCE_VERSION_DATA: list[tuple[str, str | None]] = [
    (
        "",
        None,
    ),
    (
        "__version__ = 1",
        None,
    ),
    (
        "__version__ = 'foo' + 'bar'",
        None,
    ),
    (
        "__version__ = 'foo'[1]",
        None,
    ),
    (
        "__version__ = 'foo'",
        "foo",
    ),
    (
        "a = __version__ = b = 'foo'",
        "foo",
    ),
    (
        "__version__[1:2] = 'foo'",
        None,
    ),
]


@pytest.mark.parametrize("source, version", TEST__EXTRACT_SOURCE_VERSION_DATA)
def test__extract_source_version(source: str, version: str | None) -> None:
    assert ac._extract_source_version(ast.parse(source)) == version
