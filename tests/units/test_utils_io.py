# Author: Sorin Sbarnea <ssbarnea@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024, Ansible Project
"""Tests for antsibull_core.utils.io modules."""

from pathlib import Path

import pytest

from antsibull_core.utils.io import write_file


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("a", "a\n", id="1"),
        pytest.param("b\n", "b\n", id="2"),
        pytest.param("c\n\n", "c\n", id="3"),
        pytest.param("d \n", "d\n", id="4"),
        pytest.param("e  \n", "e\n", id="5"),
        pytest.param("f \t \n", "f\n", id="6"),
    ],
)
@pytest.mark.asyncio
async def test_write_file(tmp_path: Path, text: str, expected: str) -> None:
    """Tests behavior of write_file."""
    file = tmp_path / "output.out"
    await write_file(file, text, sanitize=True)
    effective = file.open("rt", encoding="utf-8").read()
    assert effective == expected
