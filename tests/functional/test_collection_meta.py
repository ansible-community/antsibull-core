# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Ansible Project

import os
from pathlib import Path

import pytest

from antsibull_core.collection_meta import lint_collection_meta
from antsibull_core.schemas.collection_meta import (
    CollectionMetadata,
    CollectionsMetadata,
)

LINT_COLLECTION_META_DATA = [
    (
        5,
        r"""[ invalid yaml
""",
        [],
        [
            "Error while parsing YAML file: while parsing a flow sequence\n"
            '  in "{filename}", line 1, column 1\n'
            "did not find expected ',' or ']'\n"
            '  in "{filename}", line 2, column 1',
        ],
    ),
    (
        10,
        r"""---
collections: {}
""",
        [],
        [],
    ),
    (
        10,
        r"""---
collections:
  baz.bam:
    repository: https://github.com/ansible-collections/collection_template
  foo.bar:
    repository: https://github.com/ansible-collections/collection_template
""",
        [
            "foo.bar",
            "baz.bam",
        ],
        [],
    ),
    (
        9,
        r"""---
collections:
  bad.bar1:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 7
      reason: deprecated
      announce_version: 10.1.0
  bad.bar2:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: renamed
      new_name: bad.bar2
      announce_version: 9.3.0
      redirect_replacement_major_version: 9
  foo.bar: {}
  baz.bam: {}
  correct.foo1:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: considered-unmaintained
      discussion: https://forum.ansible.com/...
      announce_version: 9.3.0
  correct.foo2:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: deprecated
      discussion: https://forum.ansible.com/...
      announce_version: 9.3.0
  correct.foo3:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 10
      reason: renamed
      new_name: namespace.name
      announce_version: 9.3.0
  correct.foo4:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: TBD
      reason: renamed
      new_name: namespace.name
      announce_version: 9.3.0
  correct.foo5:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: renamed
      new_name: namespace.name
      announce_version: 9.3.0
      redirect_replacement_major_version: 10
  correct.foo6:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: TBD
      reason: renamed
      new_name: namespace.name
      announce_version: 9.3.0
      redirect_replacement_major_version: 12
  correct.foo7:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: guidelines-violation
      reason_text: There was a violation.
      discussion: https://forum.ansible.com/...
      announce_version: 9.3.0
  correct.foo8:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 12
      reason: guidelines-violation
      reason_text: Refused to run CI.
      discussion: https://forum.ansible.com/...
      announce_version: 9.3.0
  correct.foo9:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: other
      reason_text: The collection wasn't cow friendly, so the Steering Committee decided to kick it out.
      discussion: https://forum.ansible.com/...
      announce_version: 9.3.0
removed_collections:
  bad.baz2:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      version: 10.2.1
      reason: renamed
      new_name: bad.bar2
      announce_version: 9.3.0
      redirect_replacement_major_version: 7
  bad.baz1:
    removal:
      version: 9.1.0
      reason: deprecated
      announce_version: 7.1.0
  foo.bar:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      version: 9.0.0
      reason: deprecated
      announce_version: 7.1.0
""",
        [
            "foo.bar",
            "correct.foo1",
            "correct.foo2",
            "correct.foo3",
            "correct.foo4",
            "correct.foo5",
            "correct.foo6",
            "correct.foo7",
            "correct.foo8",
            "correct.foo9",
            "not.there",
        ],
        [
            "The collection list must be sorted; 'baz.bam' must come before foo.bar",
            "The removed collection list must be sorted; 'bad.baz1' must come before bad.baz2",
            "collections -> bad.bar1 -> removal -> announce_version: Major version of 10.1.0 must not be larger than the current major version 9",
            "collections -> bad.bar1 -> removal -> major_version: Removal major version 7 must be larger than current major version 9",
            "collections -> bad.bar1: Collection not in ansible.in",
            "collections -> bad.bar2 -> removal -> new_name: Must not be the collection's name",
            "collections -> bad.bar2: Collection not in ansible.in",
            "collections -> baz.bam -> repository: Required field not provided",
            "collections -> baz.bam: Collection not in ansible.in",
            "collections -> foo.bar -> repository: Required field not provided",
            "collections: No metadata present for not.there",
            "removed_collections -> bad.baz1 -> repository: Required field not provided",
            "removed_collections -> bad.baz2 -> removal -> announce_version: Major version of 9.3.0 must be less than the current major version 9",
            "removed_collections -> bad.baz2 -> removal -> version: Major version of removal version 10.2.1 must not be larger than current major version 9",
            "removed_collections -> foo.bar: Collection in ansible.in",
        ],
    ),
    (
        9,
        r"""---
collections:
  bad.foo0:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: renamed
      announce_version: 9.3.0
  bad.foo1:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: considered-unmaintained
      discussion: https://forum.ansible.com/...
      announce_version: 42
  bad.foo2:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: deprecated
      discussion: https://forum.ansible.com/...
      announce_version: "9.3"
  bad.foo3:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 10
      reason: renamed
      new_name: namespace.name
      announce_version: ''
  bad.foo4:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: TBD
      reason: deprecated
      announce_version: 9.3.0
  bad.foo5:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: renamed
      new_name: namespace.name
      announce_version: 9.3.0
      redirect_replacement_major_version: 11
  bad.foo6:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: TBD
      reason: renamed
      reason_text: There was a violation.
      new_name: namespace.name
      announce_version: 9.3.0
      redirect_replacement_major_version: 12
  bad.foo7:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: guidelines-violation
      discussion: https://forum.ansible.com/...
      announce_version: 9.3.0
  bad.foo8:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 12
      reason: guidelines-violation
      reason_text: Refused to run CI.
      new_name: namespace.name
      discussion: https://forum.ansible.com/...
      announce_version: 9.3.0
  bad.foo9:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: other
      reason_text: The collection wasn't cow friendly, so the Steering Committee decided to kick it out.
      discussion: https://forum.ansible.com/...
      announce_version: 9.3.0
      redirect_replacement_major_version: 12
  bad.foo10:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: considered-unmaintained
      reason_text: Foo!
      reason_other: This shouldn't be there!
      discussion: https://forum.ansible.com/...
  bad.foo11:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: considered-unmaintained
      discussion: https://forum.ansible.com/...
  bad.foo12:
    repository: https://github.com/ansible-collections/collection_template
    extra_stuff: bam
  bad.foo13:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: foo
      reason: considered-unmaintained
      discussion: https://forum.ansible.com/...
  bad.foo14:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      major_version: 11
      reason: foo
removed_collections:
  bad.foo1:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      version: TBD
      reason: deprecated
  bad.foo2:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      reason: deprecated
  bad.foo3:
    repository: https://github.com/ansible-collections/collection_template
    removal:
      version: 9.0.0
      reason: renamed
      new_name: bad.foo3_new
      redirect_replacement_major_version: 12
extra_stuff: baz
""",
        [],
        [
            "collections -> bad.foo0 -> removal: Value error, new_name must be provided if reason is 'renamed'",
            "collections -> bad.foo1 -> removal -> announce_version: Value error, must be a string or PypiVer object, got 42",
            "collections -> bad.foo10 -> removal -> reason_other: Extra inputs are not permitted",
            "collections -> bad.foo12 -> extra_stuff: Extra inputs are not permitted",
            "collections -> bad.foo13 -> removal -> major_version -> int: Input should be a valid integer, unable to parse string as an integer",
            "collections -> bad.foo13 -> removal -> major_version -> literal['TBD']: Input should be 'TBD'",
            "collections -> bad.foo14 -> removal -> reason: Input should be 'deprecated', 'considered-unmaintained', 'renamed', 'guidelines-violation' or 'other'",
            "collections -> bad.foo2 -> removal -> announce_version: Value error, must be a version with three release numbers (e.g. 1.2.3, 2.3.4a1), got '9.3'",
            "collections -> bad.foo3 -> removal -> announce_version: Value error, must be a non-trivial string, got ''",
            "collections -> bad.foo4 -> removal: Value error, major_version must not be TBD if reason is not 'renamed'",
            "collections -> bad.foo5 -> removal: Value error, "
            "redirect_replacement_major_version must be smaller than major_version",
            "collections -> bad.foo6 -> removal: Value error, reason_text must not be provided if reason is not 'other', 'guidelines-violation'",
            "collections -> bad.foo7 -> removal: Value error, reason_text must be provided if reason is 'other', 'guidelines-violation'",
            "collections -> bad.foo8 -> removal: Value error, new_name must not be provided if reason is not 'renamed'",
            "collections -> bad.foo9 -> removal: Value error, redirect_replacement_major_version must not be provided if reason is not 'renamed'",
            "extra_stuff: Extra inputs are not permitted",
            "removed_collections -> bad.foo1 -> removal -> version: Value error, Invalid version: 'TBD'",
            "removed_collections -> bad.foo2 -> removal -> version: Field required",
            "removed_collections -> bad.foo3 -> removal: Value error, redirect_replacement_major_version must be smaller than version's major version",
        ],
    ),
]


@pytest.mark.parametrize(
    "major_release, collection_metadata, all_collections, expected_errors",
    LINT_COLLECTION_META_DATA,
)
def test_lint_collection_meta(
    major_release: int,
    collection_metadata: str,
    all_collections: list[str],
    expected_errors: list[str],
    tmp_path: Path,
):
    filename = tmp_path / "collection-meta.yaml"
    filename.write_text(collection_metadata)
    errors = lint_collection_meta(
        collection_meta_path=filename,
        major_release=major_release,
        all_collections=all_collections,
    )
    assert errors == [
        error.replace("{filename}", str(filename)) for error in expected_errors
    ]


def test_lint_collection_meta_not_existing(tmp_path: Path):
    filename = tmp_path / "collection-meta.yaml"
    errors = lint_collection_meta(
        collection_meta_path=filename, major_release=5, all_collections=["foo.bar"]
    )
    assert errors == [f"Cannot find {filename}"]

    filename.mkdir()
    errors = lint_collection_meta(
        collection_meta_path=filename, major_release=5, all_collections=["foo.bar"]
    )
    assert errors == [
        f"Error while parsing YAML file: [Errno 21] Is a directory: {str(filename)!r}"
    ]


def test_collections_metadata_methods(tmp_path: Path):
    assert CollectionsMetadata.load_from(None).collections == {}

    filename = tmp_path / "collection-meta.yaml"
    filename.unlink(missing_ok=True)

    assert CollectionsMetadata.load_from(tmp_path).collections == {}

    filename.write_text(
        r"""---
collections: {}
"""
    )

    assert CollectionsMetadata.load_from(tmp_path).collections == {}

    filename.write_text(
        r"""---
collections:
  foo.bar:
    repository: https://github.com/ansible-collections/collection_template
"""
    )

    meta = CollectionsMetadata.load_from(tmp_path)
    assert meta.collections == {
        "foo.bar": CollectionMetadata(
            repository="https://github.com/ansible-collections/collection_template"
        ),
    }
    assert meta.get_meta("foo.bar") == CollectionMetadata(
        repository="https://github.com/ansible-collections/collection_template"
    )

    assert "not.there" not in meta.collections
    assert meta.get_meta("not.there") == CollectionMetadata()
    assert "not.there" in meta.collections
