# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2020, Ansible Project

"""
Persist collection infornation used to build Ansible.

Build dependency files list the dependencies of an Ansible release along with the versions that are
compatible with that release.

When we initially build an Ansible major release, we'll use certain versions of collections.  We
don't want to install backwards incompatible collections until the next major Ansible release.
"""

from __future__ import annotations

import typing as t
from collections.abc import Mapping

from packaging.version import Version as PypiVer

if t.TYPE_CHECKING:
    from _typeshed import StrPath
    from semantic_version import Version as SemVer


class DependencyFileData(t.NamedTuple):
    ansible_version: str
    ansible_core_version: str
    deps: dict[str, str]


class InvalidFileFormat(Exception):
    pass


def parse_pieces_file(pieces_file: StrPath) -> list[str]:
    with open(pieces_file, "rb") as f:
        contents = f.read()

    decoded_contents = contents.decode("utf-8")
    # One collection per line, ignoring comments and empty lines
    collections = [
        c
        for line in decoded_contents.split("\n")
        if (c := line.strip()) and not c.startswith("#")
    ]
    return collections


def _parse_name_version_spec_file(filename: StrPath) -> DependencyFileData:
    deps: dict[str, str] = {}
    ansible_core_version: str | None = None
    ansible_version: str | None = None

    for line in parse_pieces_file(filename):
        record = [entry.strip() for entry in line.split(":", 1)]

        if record[0] == "_ansible_version":
            if ansible_version is not None:
                raise InvalidFileFormat(
                    f"{filename!r} specified _ansible_version more than once"
                )
            ansible_version = record[1]
            continue

        if record[0] == "_ansible_core_version":
            if ansible_core_version is not None:
                raise InvalidFileFormat(
                    f"{filename!r} specified _ansible_core_version more than once"
                )
            ansible_core_version = record[1]
            continue

        deps[record[0]] = record[1]

    if ansible_core_version is None:
        raise InvalidFileFormat(
            f"{filename!r} was invalid.  It did not contain"
            " the required ansible_core_version field"
        )
    if ansible_version is None:
        raise InvalidFileFormat(
            f"{filename!r} was invalid.  It did not contain"
            " the required ansible_version field"
        )

    return DependencyFileData(ansible_version, ansible_core_version, deps)


class DepsFile:
    """
    File containing the collections which are part of an Ansible release.

    A DepsFile contains a sequence of lines with a collection name, ": ", and then an exact
    version of the collection.  It tracks the exact collection-versions which were installed
    with a particular ansible version.

    The deps file has two special lines which are not collections.  They are::

        _ansible_version: X1.Y1.Z1
        _ansible_core_version: X2.Y2.Z2

    These are, respectively, the ansible version that was built and the ansible-core version which
    it was built against.  Note that the ansible release will depend on a compatible version of that
    ansible-core version, not an exact dependency on that precise version.
    """

    def __init__(self, deps_file: StrPath) -> None:
        """
        Create a :mod:`DepsFile`.

        :arg deps_file: filename of the `DepsFile`.
        """
        self.filename: StrPath = deps_file

    def parse(self) -> DependencyFileData:
        """Parse the deps from a dependency file."""
        return _parse_name_version_spec_file(self.filename)

    def write(
        self,
        ansible_version: str | PypiVer,
        ansible_core_version: str | PypiVer,
        included_versions: Mapping[str, str] | Mapping[str, SemVer],
        python_requires: str | None = None,
    ) -> None:
        """
        Write a list of all the dependent collections included in this Ansible release.

        :arg ansible_version: The version of Ansible that is being recorded.
        :arg ansible_core_version: The version of Ansible-core that will be depended on.
        :arg included_versions: Dictionary mapping collection names to the version range in this
            version of Ansible.
        :arg python_requires: A python_requires string. Will be stored as ``_python``.

        WARNING: This function will no longer accept version objects in the ansible_core_version
                 and included_versions parameters, and will require a PypiVer object in the
                 ansible_version parameter in antsibull-core 2.0.0.
        """
        records = []
        for dep, version in included_versions.items():
            records.append(f"{dep}: {version}")
        records.sort()

        if not isinstance(ansible_version, PypiVer):
            ansible_version = PypiVer(ansible_version)

        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(f"_ansible_version: {ansible_version}\n")
            f.write(f"_ansible_core_version: {ansible_core_version}\n")
            if python_requires is not None:
                f.write(f"_python: {python_requires}\n")
            f.write("\n".join(records))
            f.write("\n")


class BuildFile:
    def __init__(self, build_file: StrPath) -> None:
        self.filename: StrPath = build_file

    def parse(self) -> DependencyFileData:
        """Parse the build from a dependency file."""
        return _parse_name_version_spec_file(self.filename)

    def write(
        self,
        ansible_version: PypiVer,
        ansible_core_version: str,
        dependencies: Mapping[str, SemVer],
        python_requires: str | None = None,
    ) -> None:
        """
        Write a build dependency file.

        A build dependency file records the collections that went into a given Ansible release along
        with the range of versions that are allowed for that collection.  The range is meant to
        define the set of collection versions that are compatible with what was present in the
        collection as of the first beta release, when we feature freeze the collections.

        :arg ansible_version: The version of Ansible that is being recorded.
        :arg ansible_core_version: The version of Ansible-core that will be depended on.
        :arg dependencies: Dictionary with keys of collection names and values of the latest
            versions of those collections.
        :arg python_requires: A python_requires string. Will be stored as ``_python``.
        """
        records = []
        for dep, version in dependencies.items():
            if version.prerelease and version.patch == 0:
                # Prereleases (ex: 2.0.0-b1, 2.1.0-a1) are a special case because they sort before
                # the major.minor that they are for.
                records.append(f"{dep}: >={version},<{version.major + 1}.0.0")
            else:
                records.append(
                    f"{dep}: >={version.major}.{version.minor}.0,"
                    f"<{version.next_major()}"
                )
        records.sort()

        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(f"_ansible_version: {ansible_version.major}\n")
            f.write(f"_ansible_core_version: {ansible_core_version}\n")
            if python_requires is not None:
                f.write(f"_python: {python_requires}\n")
            f.write("\n".join(records))
            f.write("\n")
