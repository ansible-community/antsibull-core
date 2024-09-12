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

from .schemas.collection_meta import (
    CollectionMetadata,
    CollectionsMetadata,
    RemovalInformation,
)

if t.TYPE_CHECKING:
    from _typeshed import StrPath


class _Validator:
    """
    Validate a CollectionsMetadata object.

    Validation error messages are added to the ``errors`` attribute.
    """

    errors: list[str]

    def __init__(self, *, all_collections: list[str], major_release: int):
        self.errors = []
        self.all_collections = all_collections
        self.major_release = major_release

    def _validate_removal(
        self, collection: str, removal: RemovalInformation, prefix: str
    ) -> None:
        if (
            removal.major_version != "TBD"
            and removal.major_version <= self.major_release  # pyre-ignore[58]
        ):
            self.errors.append(
                f"{prefix} major_version: Removal major version {removal.major_version} must"
                f" be larger than current major version {self.major_release}"
            )

        if (
            removal.announce_version is not None
            and removal.announce_version.major > self.major_release
        ):
            self.errors.append(
                f"{prefix} announce_version: Major version of {removal.announce_version}"
                f" must not be larger than the current major version {self.major_release}"
            )

        if removal.redirect_replacement_major_version is not None:
            if removal.redirect_replacement_major_version <= self.major_release:
                self.errors.append(
                    f"{prefix} redirect_replacement_major_version: Redirect removal version"
                    f" {removal.redirect_replacement_major_version} must be larger than"
                    f" current major version {self.major_release}"
                )
            if (
                removal.major_version != "TBD"
                and removal.redirect_replacement_major_version  # pyre-ignore[58]
                >= removal.major_version
            ):
                self.errors.append(
                    f"{prefix} redirect_replacement_major_version: Redirect removal major version"
                    f" {removal.redirect_replacement_major_version} must be smaller than"
                    f" the removal major version {removal.major_version}"
                )

        if removal.reason == "renamed" and removal.new_name == collection:
            self.errors.append(f"{prefix} new_name: Must not be the collection's name")

    def _validate_collection(
        self, collection: str, meta: CollectionMetadata, prefix: str
    ) -> None:
        if meta.repository is None:
            self.errors.append(f"{prefix} repository: Required field not provided")

        if meta.removal:
            self._validate_removal(collection, meta.removal, f"{prefix} removal ->")

    def validate(self, data: CollectionsMetadata) -> None:
        # Check order
        sorted_list = sorted(data.collections)
        raw_list = list(data.collections)
        if raw_list != sorted_list:
            for raw_entry, sorted_entry in zip(raw_list, sorted_list):
                if raw_entry != sorted_entry:
                    self.errors.append(
                        "The collection list must be sorted; "
                        f"{sorted_entry!r} must come before {raw_entry}"
                    )
                    break

        # Validate collection data
        remaining_collections = set(self.all_collections)
        for collection, meta in data.collections.items():
            if collection not in remaining_collections:
                self.errors.append(
                    f"collections -> {collection}: Collection not in ansible.in"
                )
            else:
                remaining_collections.remove(collection)
            self._validate_collection(
                collection, meta, f"collections -> {collection} ->"
            )

        # Complain about remaining collections
        for collection in sorted(remaining_collections):
            self.errors.append(f"collections: No metadata present for {collection}")


def lint_collection_meta(
    *, collection_meta_path: StrPath, major_release: int, all_collections: list[str]
) -> list[str]:
    """Lint collection-meta.yaml."""
    if not os.path.exists(collection_meta_path):
        return [f"Cannot find {collection_meta_path}"]

    try:
        data = load_yaml_file(collection_meta_path)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return [f"Error while parsing YAML file: {exc}"]

    validator = _Validator(
        all_collections=all_collections,
        major_release=major_release,
    )

    for cls in (
        # NOTE: The order is important here! The most deeply nested classes must come first,
        #       otherwise extra=forbid might not be used for something deeper in the hierarchy.
        RemovalInformation,
        CollectionMetadata,
        CollectionsMetadata,
    ):
        cls.model_config["extra"] = "forbid"
        cls.model_rebuild(force=True)

    try:
        parsed_data = CollectionsMetadata.model_validate(data)
        validator.validate(parsed_data)
    except p.ValidationError as exc:
        for error in exc.errors():
            location = " -> ".join(str(loc) for loc in error["loc"])
            validator.errors.append(f'{location}: {error["msg"]}')

    return sorted(validator.errors)
