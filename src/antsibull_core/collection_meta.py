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
from collections.abc import Collection

import pydantic as p
from antsibull_fileutils.yaml import load_yaml_file
from packaging.version import Version as PypiVer

from .pydantic import forbid_extras, get_formatted_error_messages
from .schemas.collection_meta import (
    BaseRemovalInformation,
    CollectionMetadata,
    CollectionsMetadata,
    RemovalInformation,
    RemovalUpdate,
    RemovedCollectionMetadata,
    RemovedRemovalInformation,
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

    def _update_state_value(
        self,
        state: str | None,
        accepted_states: list[str | None],
        prefix: str,
        index: int,
        field_name: str,
    ) -> str:
        if state not in accepted_states:
            if state is not None:
                self.errors.append(
                    f"{prefix}[{index}] -> {field_name}: Unexpected update after {state}"
                )
            else:
                self.errors.append(
                    f"{prefix}[{index}] -> {field_name}: Unexpected first update"
                )
        return field_name

    def _update_state(
        self, state: str | None, index: int, update: RemovalUpdate, prefix: str
    ) -> tuple[str | None, PypiVer | None, str]:
        if update.cancelled_version:
            state = self._update_state_value(
                state,
                [None, "deprecated_version", "redeprecated_version"],
                prefix,
                index,
                "cancelled_version",
            )
            return state, update.cancelled_version, "cancelled_version"
        if update.deprecated_version:
            state = self._update_state_value(
                state, [None], prefix, index, "deprecated_version"
            )
            return state, update.deprecated_version, "deprecated_version"
        if update.redeprecated_version:
            state = self._update_state_value(
                state,
                ["readded_version", "cancelled_version"],
                prefix,
                index,
                "redeprecated_version",
            )
            return state, update.redeprecated_version, "redeprecated_version"
        if update.removed_version:
            state = self._update_state_value(
                state, [None], prefix, index, "removed_version"
            )
            return state, update.removed_version, "removed_version"
        if update.readded_version:
            state = self._update_state_value(
                state, ["removed_version"], prefix, index, "readded_version"
            )
            return state, update.readded_version, "readded_version"
        # The following lines should never be reached:
        self.errors.append(f"{prefix}[{index}]: Internal error")  # pragma: no cover
        return state, None, ""  # pragma: no cover

    def _validate_removal_updates(
        self,
        removal: BaseRemovalInformation,
        indirect_updates: list[RemovalUpdate],
        prefix: str,
    ) -> None:
        prefix += " -> updates"
        state = None
        for update in indirect_updates:
            state, _, __ = self._update_state(state, -1, update, prefix)
        last_version = None
        for index, update in enumerate(removal.updates):
            state, version, field_name = self._update_state(
                state, index, update, prefix
            )
            if version is None:
                # The following line should never be reached:
                pass  # pragma: no cover
            elif version.major != self.major_release:
                self.errors.append(
                    f"{prefix}[{index}] -> {field_name}: Version's major version {version.major}"
                    f" must be the current major version {self.major_release}"
                )
            elif last_version is not None and version <= last_version:
                self.errors.append(
                    f"{prefix}[{index}] -> {field_name}: Version {version}"
                    f" must be after the previous update's version {last_version}"
                )
            last_version = version

    def _validate_removal_base(
        self, collection: str, removal: BaseRemovalInformation, prefix: str
    ) -> None:
        if removal.reason == "renamed" and removal.new_name == collection:
            self.errors.append(f"{prefix} new_name: Must not be the collection's name")

    def _validate_removal(
        self, collection: str, removal: RemovalInformation, prefix: str
    ) -> None:
        if (
            removal.major_version != "TBD"
            and removal.major_version <= self.major_release  # pyre-ignore[58]
        ):
            is_ok = removal.major_version == self.major_release and any(
                update.removed_version for update in removal.updates
            )
            if not is_ok:
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

        self._validate_removal_base(collection, removal, prefix)

        indirect_updates = []
        if removal.announce_version is not None:
            indirect_updates.append(
                RemovalUpdate(
                    deprecated_version=removal.announce_version,
                    reason=removal.reason,
                    reason_text=removal.reason_text,
                )
            )
        self._validate_removal_updates(removal, indirect_updates, prefix)

    def _validate_collection(
        self, collection: str, meta: CollectionMetadata, prefix: str
    ) -> None:
        if meta.repository is None:
            self.errors.append(f"{prefix} repository: Required field not provided")

        if meta.removal:
            self._validate_removal(collection, meta.removal, f"{prefix} removal ->")

    def _validate_removal_for_removed(
        self, collection: str, removal: RemovedRemovalInformation, prefix: str
    ) -> None:
        if removal.version.major > self.major_release:
            self.errors.append(
                f"{prefix} version: Major version of removal version {removal.version} must"
                f" not be larger than current major version {self.major_release}"
            )

        if (
            removal.announce_version is not None
            and removal.announce_version.major >= self.major_release
        ):
            self.errors.append(
                f"{prefix} announce_version: Major version of {removal.announce_version}"
                f" must be less than the current major version {self.major_release}"
            )

        self._validate_removal_base(collection, removal, prefix)

    def _validate_removed_collection(
        self, collection: str, meta: RemovedCollectionMetadata, prefix: str
    ) -> None:
        if meta.repository is None:
            self.errors.append(f"{prefix} repository: Required field not provided")

        self._validate_removal_for_removed(
            collection, meta.removal, f"{prefix} removal ->"
        )

    def _validate_order(self, collection: Collection, what: str) -> None:
        # Check order
        sorted_list = sorted(collection)
        raw_list = list(collection)
        for raw_entry, sorted_entry in zip(raw_list, sorted_list):
            if raw_entry != sorted_entry:
                self.errors.append(
                    f"{what} must be sorted; "
                    f"{sorted_entry!r} must come before {raw_entry}"
                )
                break

    def _validate_collections(self, data: CollectionsMetadata) -> None:
        # Check order
        self._validate_order(data.collections, "The collection list")

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

    def _validate_removed_collections(self, data: CollectionsMetadata) -> None:
        # Check order
        self._validate_order(data.removed_collections, "The removed collection list")

        # Validate removed collection data
        for collection, removed_meta in data.removed_collections.items():
            if collection in self.all_collections:
                self.errors.append(
                    f"removed_collections -> {collection}: Collection in ansible.in"
                )
            self._validate_removed_collection(
                collection, removed_meta, f"removed_collections -> {collection} ->"
            )

    def validate(self, data: CollectionsMetadata) -> None:
        self._validate_collections(data)
        self._validate_removed_collections(data)


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

    forbid_extras(CollectionsMetadata)

    try:
        parsed_data = CollectionsMetadata.model_validate(data)
        validator.validate(parsed_data)
    except p.ValidationError as exc:
        validator.errors.extend(get_formatted_error_messages(exc))

    return sorted(validator.errors)
