# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Ansible Project

from __future__ import annotations

import pytest

from antsibull_core.utils.hashing import verify_a_hash, verify_hash

HASH_TESTS = [
    (
        b"",
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "sha256",
        {},
        True,
    ),
    (
        b"",
        "01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b",
        "sha256",
        {},
        False,
    ),
]


@pytest.mark.parametrize(
    "content, hash, algorithm, algorithm_kwargs, expected_match", HASH_TESTS
)
@pytest.mark.asyncio
async def test_verify_hash(
    content: bytes,
    hash: bytes,
    algorithm: str,
    algorithm_kwargs: dict | None,
    expected_match: bool,
    tmp_path,
):
    filename = tmp_path / "file"
    with open(filename, "wb") as f:
        f.write(content)
    result = await verify_hash(
        filename, hash, algorithm=algorithm, algorithm_kwargs=algorithm_kwargs
    )
    assert result is expected_match


HASH_DICT_TESTS = [
    (
        b"foo",
        {
            "sha256": "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae",
        },
        True,
    ),
    (
        b"bar",
        {
            "sha256": "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae",
        },
        False,
    ),
    (
        b"foo",
        {
            "blake2b_256": "b8fe9f7f6255a6fa08f668ab632a8d081ad87983c77cd274e48ce450f0b349fd",
        },
        True,
    ),
    (
        b"bar",
        {
            "blake2b_256": "b8fe9f7f6255a6fa08f668ab632a8d081ad87983c77cd274e48ce450f0b349fd",
        },
        False,
    ),
    (
        b"",
        {},
        False,
    ),
    (
        b"",
        {
            "foo": "bar",
        },
        False,
    ),
]


@pytest.mark.parametrize("content, hash_digests, expected_match", HASH_DICT_TESTS)
@pytest.mark.asyncio
async def test_verify_a_hash(
    content: bytes, hash_digests: dict[str, str], expected_match: bool, tmp_path
):
    filename = tmp_path / "file"
    with open(filename, "wb") as f:
        f.write(content)
    result = await verify_a_hash(filename, hash_digests)
    assert result is expected_match
