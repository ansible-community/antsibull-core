# Author: Felix Fontein <felix@fontein.de>
# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Ansible Project, 2020

"""
Classes to encapsulate collection metadata from collection-meta.yaml
"""

from __future__ import annotations

import os
import typing as t

import pydantic as p
from antsibull_fileutils.yaml import load_yaml_file
from packaging.version import Version as PypiVer
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated, Self

if t.TYPE_CHECKING:
    from _typeshed import StrPath


def _convert_pypi_version(v: t.Any) -> t.Any:
    if isinstance(v, str):
        if not v:
            raise ValueError(f"must be a non-trivial string, got {v!r}")
        version = PypiVer(v)
    elif isinstance(v, PypiVer):
        version = v
    else:
        raise ValueError(f"must be a string or PypiVer object, got {v!r}")

    if len(version.release) != 3:
        raise ValueError(
            f"must be a version with three release numbers (e.g. 1.2.3, 2.3.4a1), got {v!r}"
        )
    return version


PydanticPypiVersion = Annotated[PypiVer, BeforeValidator(_convert_pypi_version)]


class BaseRemovalInformation(p.BaseModel):
    """
    Stores metadata on why a collection was/will get removed.
    """

    model_config = p.ConfigDict(arbitrary_types_allowed=True)

    # The reason because of which the collection will be removed.
    reason: t.Literal[
        "deprecated",
        "considered-unmaintained",
        "renamed",
        "guidelines-violation",
        "other",
    ]
    reason_text: t.Optional[str] = None

    # The Ansible version in which the announcement was made. This is needed
    # for changelog generation.
    announce_version: t.Optional[PydanticPypiVersion] = None

    # In case reason=renamed, the new name of the collection.
    new_name: t.Optional[str] = None

    # The link to the discussion of the removal.
    discussion: t.Optional[p.HttpUrl] = None

    # In case reason=renamed, the major Ansible release in which the collection's
    # contents have been replaced by deprecated redirects.
    redirect_replacement_major_version: t.Optional[int] = None

    @p.model_validator(mode="after")  # pyre-ignore[56]
    def _check_reason_text(self) -> Self:
        reasons_with_text = ("other", "guidelines-violation")
        if self.reason in reasons_with_text:
            if self.reason_text is None:
                reasons = ", ".join(f"'{reason}'" for reason in reasons_with_text)
                raise ValueError(f"reason_text must be provided if reason is {reasons}")
        else:
            if self.reason_text is not None:
                reasons = ", ".join(f"'{reason}'" for reason in reasons_with_text)
                raise ValueError(
                    f"reason_text must not be provided if reason is not {reasons}"
                )
        return self

    @p.model_validator(mode="after")  # pyre-ignore[56]
    def _check_renamed_base(self) -> Self:
        if self.reason == "renamed":
            if self.new_name is None:
                raise ValueError("new_name must be provided if reason is 'renamed'")
        else:
            if self.new_name is not None:
                raise ValueError(
                    "new_name must not be provided if reason is not 'renamed'"
                )
            if self.redirect_replacement_major_version is not None:
                raise ValueError(
                    "redirect_replacement_major_version must not be provided"
                    " if reason is not 'renamed'"
                )
        return self


class RemovalInformation(BaseRemovalInformation):
    """
    Stores metadata on when and why a collection will get removed.
    """

    # The Ansible major version from which the collection will be removed.
    major_version: t.Union[int, t.Literal["TBD"]]

    @p.model_validator(mode="after")  # pyre-ignore[56]
    def _check_renamed(self) -> Self:
        if self.reason == "renamed":
            if (
                self.redirect_replacement_major_version is not None
                and self.major_version != "TBD"
                and self.redirect_replacement_major_version
                >= self.major_version  # pyre-ignore[58]
            ):
                raise ValueError(
                    "redirect_replacement_major_version must be smaller than major_version"
                )
        else:
            if self.major_version == "TBD":
                raise ValueError(
                    "major_version must not be TBD if reason is not 'renamed'"
                )
        return self


class RemovedRemovalInformation(BaseRemovalInformation):
    """
    Stores metadata on when and why a collection was removed.
    """

    # The exact version from which the collection has been removed.
    # This is needed for changelog generation.
    version: PydanticPypiVersion

    @p.model_validator(mode="after")  # pyre-ignore[56]
    def _check_reason_is_renamed(self) -> Self:
        if self.reason != "renamed":
            return self
        if (
            self.redirect_replacement_major_version is not None
            and self.redirect_replacement_major_version >= self.version.major
        ):
            raise ValueError(
                "redirect_replacement_major_version must be smaller than"
                " version's major version"
            )
        return self


class BaseCollectionMetadata(p.BaseModel):
    """
    Stores metadata about one collection.
    """

    # If the collection does not use changelogs/changelog.yaml, it can provide
    # a URL where the collection's changelog can be found.
    changelog_url: t.Optional[str] = p.Field(alias="changelog-url", default=None)

    # In case the collection is not located in the root of its repository, the
    # subdirectory in which the collection appears.
    collection_directory: t.Optional[str] = p.Field(
        alias="collection-directory", default=None
    )

    # The collection's repository.
    repository: t.Optional[str] = None

    # A regular expression to match the collection's version from a tag in the repository.
    tag_version_regex: t.Optional[str] = None

    # A list of maintainers. These should be usernames for the repository's
    # hosting environment.
    maintainers: list[str] = []


class CollectionMetadata(BaseCollectionMetadata):
    """
    Stores metadata about one collection.
    """

    model_config = p.ConfigDict(arbitrary_types_allowed=True)

    # Optional information that the collection will be removed from
    # a future Ansible release.
    removal: t.Optional[RemovalInformation] = None


class RemovedCollectionMetadata(BaseCollectionMetadata):
    """
    Stores metadata about a removed collection.
    """

    model_config = p.ConfigDict(arbitrary_types_allowed=True)

    # Information why the collection has been removed
    removal: RemovedRemovalInformation


class CollectionsMetadata(p.BaseModel):
    """
    Stores metadata about a set of collections.
    """

    # Metadata on the collections included in Ansible.
    collections: dict[str, CollectionMetadata]

    # Metadata on the collections removed from this major version of Ansible.
    removed_collections: dict[str, RemovedCollectionMetadata] = {}

    @staticmethod
    def load_from(deps_dir: StrPath | None) -> CollectionsMetadata:
        if deps_dir is None:
            return CollectionsMetadata(collections={})
        collection_meta_path = os.path.join(deps_dir, "collection-meta.yaml")
        if not os.path.exists(collection_meta_path):
            return CollectionsMetadata(collections={})
        data = load_yaml_file(collection_meta_path)
        return CollectionsMetadata.model_validate(data)

    def get_meta(self, collection_name: str) -> CollectionMetadata:
        result = self.collections.get(collection_name)
        if result is None:
            result = CollectionMetadata()
            self.collections[collection_name] = result
        return result
