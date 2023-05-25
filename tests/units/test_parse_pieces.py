# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Ansible Project

from pathlib import Path

import pytest

from antsibull_core import dependency_files as df

PIECES = """
community.general
# This is a comment
community.aws
    # Supported by ansible
    ansible.posix
    ansible.windows
# Third parties
purestorage.flasharray
"""

PARSED_PIECES = [
    "community.general",
    "community.aws",
    "ansible.posix",
    "ansible.windows",
    "purestorage.flasharray",
]

DEPS = """
_ansible_version: 2.10.5
# this is a comment
_ansible_base_version: 2.10.4
    # supported by ansible
    ansible.netcommon: 1.4.1
    ansible.posix: 1.1.1
    ansible.windows: 1.3.0
# third parties
dellemc.os10: 1.0.2
"""

PARSED_DEPS_ANSIBLE_VERSION = "2.10.5"
PARSED_DEPS_ANSIBLE_CORE_VERSION = "2.10.4"
PARSED_DEPS_DEPS = {
    "ansible.netcommon": "1.4.1",
    "ansible.posix": "1.1.1",
    "ansible.windows": "1.3.0",
    "dellemc.os10": "1.0.2",
}

DEPS_2 = """
_ansible_version: 2.10.5
# this is a comment
_ansible_core_version: 2.10.4
    # supported by ansible
    ansible.netcommon: 1.4.1
    ansible.posix: 1.1.1
    ansible.windows: 1.3.0
# third parties
dellemc.os10: 1.0.2
"""

PARSED_DEPS_2_ANSIBLE_VERSION = "2.10.5"
PARSED_DEPS_2_ANSIBLE_CORE_VERSION = "2.10.4"
PARSED_DEPS_2_DEPS = {
    "ansible.netcommon": "1.4.1",
    "ansible.posix": "1.1.1",
    "ansible.windows": "1.3.0",
    "dellemc.os10": "1.0.2",
}

BUILD = """
_ansible_version: 2.10
# this is a comment
_ansible_base_version: 2.10.1
    # supported by ansible
    ansible.netcommon: >=1.2.0,<2.0.0
    ansible.posix: >=1.1.0,<2.0.0
    ansible.windows: >=1.0.0,<2.0.0
# third parties
dellemc.os10: >=1.0.0,<1.1.0
"""

PARSED_BUILD_ANSIBLE_VERSION = "2.10"
PARSED_BUILD_ANSIBLE_CORE_VERSION = "2.10.1"
PARSED_BUILD_DEPS = {
    "ansible.netcommon": ">=1.2.0,<2.0.0",
    "ansible.posix": ">=1.1.0,<2.0.0",
    "ansible.windows": ">=1.0.0,<2.0.0",
    "dellemc.os10": ">=1.0.0,<1.1.0",
}

BUILD_2 = """
_ansible_version: 2.10
# this is a comment
_ansible_core_version: 2.10.1
    # supported by ansible
    ansible.netcommon: >=1.2.0,<2.0.0
    ansible.posix: >=1.1.0,<2.0.0
    ansible.windows: >=1.0.0,<2.0.0
# third parties
dellemc.os10: >=1.0.0,<1.1.0
"""

PARSED_BUILD_2_ANSIBLE_VERSION = "2.10"
PARSED_BUILD_2_ANSIBLE_CORE_VERSION = "2.10.1"
PARSED_BUILD_2_DEPS = {
    "ansible.netcommon": ">=1.2.0,<2.0.0",
    "ansible.posix": ">=1.1.0,<2.0.0",
    "ansible.windows": ">=1.0.0,<2.0.0",
    "dellemc.os10": ">=1.0.0,<1.1.0",
}

CONSTRAINTS_FILE_2 = """
dellemc.os10: ==1.0.0
"""

PARSED_CONSTRAINTS_FILE_2 = {"dellemc.os10": "==1.0.0"}


def test_parse_pieces(tmp_path):
    pieces_filename = tmp_path / "pieces.in"
    with open(pieces_filename, "w") as f:
        f.write(PIECES)
    assert df.parse_pieces_file(pieces_filename) == PARSED_PIECES


def test_deps_file_parse(tmp_path):
    deps_filename = tmp_path / "deps.in"
    with open(deps_filename, "w") as f:
        f.write(DEPS)
    parsed_deps = df.DepsFile(deps_filename).parse()
    assert parsed_deps.ansible_version == PARSED_DEPS_ANSIBLE_VERSION
    assert parsed_deps.ansible_core_version == PARSED_DEPS_ANSIBLE_CORE_VERSION
    assert parsed_deps.deps == PARSED_DEPS_DEPS


def test_deps_file_2_parse(tmp_path):
    deps_filename = tmp_path / "deps.in"
    with open(deps_filename, "w") as f:
        f.write(DEPS_2)
    parsed_deps = df.DepsFile(deps_filename).parse()
    assert parsed_deps.ansible_version == PARSED_DEPS_2_ANSIBLE_VERSION
    assert parsed_deps.ansible_core_version == PARSED_DEPS_2_ANSIBLE_CORE_VERSION
    assert parsed_deps.deps == PARSED_DEPS_2_DEPS


def test_build_file_parse(tmp_path):
    build_filename = tmp_path / "build.in"
    with open(build_filename, "w") as f:
        f.write(BUILD)
    parsed_build = df.DepsFile(build_filename).parse()
    assert parsed_build.ansible_version == PARSED_BUILD_ANSIBLE_VERSION
    assert parsed_build.ansible_core_version == PARSED_BUILD_ANSIBLE_CORE_VERSION
    assert parsed_build.deps == PARSED_BUILD_DEPS


def test_build_file_2_parse(tmp_path):
    build_filename = tmp_path / "build.in"
    with open(build_filename, "w") as f:
        f.write(BUILD_2)
    parsed_build = df.DepsFile(build_filename).parse()
    assert parsed_build.ansible_version == PARSED_BUILD_2_ANSIBLE_VERSION
    assert parsed_build.ansible_core_version == PARSED_BUILD_2_ANSIBLE_CORE_VERSION
    assert parsed_build.deps == PARSED_BUILD_2_DEPS


def test_constraints_file(tmp_path: Path):
    build_filename = tmp_path / "build.in"
    build_filename.write_text(BUILD_2)

    constraints_filename = tmp_path / "constraints"
    constraints_filename.write_text(CONSTRAINTS_FILE_2)

    parsed_build = df.BuildFile(build_filename).parse(constraints_filename)

    assert parsed_build.ansible_version == PARSED_BUILD_2_ANSIBLE_VERSION
    assert parsed_build.ansible_core_version == PARSED_BUILD_2_ANSIBLE_CORE_VERSION
    assert parsed_build.deps == (PARSED_BUILD_2_DEPS | PARSED_CONSTRAINTS_FILE_2)


def test_constraints_file_invalid_key(tmp_path: Path):
    build_filename = tmp_path / "build.in"
    build_filename.write_text(BUILD_2)

    constraints_filename = tmp_path / "constraints"
    constraints_filename.write_text(
        CONSTRAINTS_FILE_2 + "_ansible_core_version: 2.15.0\n"
    )

    with pytest.raises(
        df.InvalidFileFormat,
        match=rf"{constraints_filename}: Invalid key: _ansible_core_version",
    ):
        df.BuildFile(build_filename).parse(constraints_filename)


def test_parse_pieces_invalid_repeated(tmp_path: Path):
    pieces_filename = tmp_path / "pieces"
    pieces_filename.write_text("key1: abc\nkey1: xyz\n")

    with pytest.raises(
        df.InvalidFileFormat,
        match=f"{pieces_filename}: Duplicated key: 'key1'",
    ):
        df.parse_pieces_mapping_file(pieces_filename)


def test_parse_pieces_invalid_colon(tmp_path: Path):
    pieces_filename = tmp_path / "pieces"
    pieces_filename.write_text("abc: 123\nxyz\n")

    with pytest.raises(
        df.InvalidFileFormat,
        match=f"{pieces_filename}: Invalid line: 'xyz'. No ':' found.",
    ):
        df.parse_pieces_mapping_file(pieces_filename)
